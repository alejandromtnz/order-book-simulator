"""
market maker bot, level 2 (percentage spread)
always cancels its own old bid/ask before placing new ones each tick,
so it never leaves a stale quote sitting in the book
"""

# TODO level 1: fixed absolute spread - done (rejected, too naive)
# TODO level 2: percentage-based spread - done (this file)
# TODO level 3: volatility-based spread - not done yet
# TODO level 4: avellaneda-stoikov model (spread + inventory skew together) - not done yet

from orderbook import Order, OrderBook, Side


class MarketMaker:
    def __init__(self, book: OrderBook, spread_pct: float = 0.001, quote_qty: int = 10,
                 skew_coefficient: float = 0.0):
        self.book = book
        self.spread_pct = spread_pct
        self.quote_qty = quote_qty
        self.skew_coefficient = skew_coefficient   # how hard we push quotes to correct inventory
        self.my_bid: Order | None = None      # our resting bid right now, if any
        self.my_ask: Order | None = None      # our resting ask right now, if any
        self.last_mid: float | None = None    # fallback price if book has no bid/ask yet
        self.my_order_ids: set[int] = set()   # every order id we have ever submitted
        self.mid_history: list[float] = []    # every real mid we have ever observed, in order

    def _cancel_my_orders(self):
        if self.my_bid is not None:
            self.book.cancel_order(self.my_bid.id)    # rip down the old bid
            self.my_bid = None
        if self.my_ask is not None:
            self.book.cancel_order(self.my_ask.id)    # rip down the old ask
            self.my_ask = None

    def _compute_mid(self) -> float | None:
        best_bid = self.book.best_bid()
        best_ask = self.book.best_ask()
        if best_bid is not None and best_ask is not None:
            self.last_mid = (best_bid.price + best_ask.price) / 2   # both sides exist, use real mid
            self.mid_history.append(self.last_mid)                  # remember it for volatility later
        return self.last_mid

    def update_quotes(self, timestamp: int):
        self._cancel_my_orders()          # always kill the old quote before anything else

        mid = self._compute_mid()
        if mid is None:
            return                        # no reference price yet, skip this tick

        inventory, _ = self.get_inventory_and_cash()
        skewed_mid = mid - self.skew_coefficient * inventory   # short -> push up, long -> push down

        offset = mid * self.spread_pct / 2                     # spread width still based on raw mid
        bid_price = round(skewed_mid - offset, 2)
        ask_price = round(skewed_mid + offset, 2)

        bid_order = Order(Side.BUY, bid_price, self.quote_qty, timestamp)
        self.my_order_ids.add(bid_order.id)      # remember this id no matter what happens to it
        self.book.add_limit_order(bid_order)
        if bid_order.quantity > 0:        # still resting, not fully filled instantly
            self.my_bid = bid_order

        ask_order = Order(Side.SELL, ask_price, self.quote_qty, timestamp)
        self.my_order_ids.add(ask_order.id)      # remember this id no matter what happens to it
        self.book.add_limit_order(ask_order)
        if ask_order.quantity > 0:        # still resting, not fully filled instantly
            self.my_ask = ask_order

    def get_inventory_and_cash(self) -> tuple[float, float]:
        """
        Scans every trade the book has ever recorded, and adds up the
        ones where we were the buyer or the seller (matched by id
        against my_order_ids). Returns (inventory, cash):
        - inventory: net units we currently hold (bought - sold)
        - cash: net money moved so far (negative if we have spent more
          buying than we have collected selling)
        """
        inventory = 0.0
        cash = 0.0
        for trade in self.book.trades:
            if trade.buy_order_id in self.my_order_ids:
                inventory += trade.quantity
                cash -= trade.price * trade.quantity
            if trade.sell_order_id in self.my_order_ids:
                inventory -= trade.quantity
                cash += trade.price * trade.quantity
        return inventory, cash

    def get_pnl(self, current_price: float | None = None) -> float:
        """
        Total PnL: the cash already collected/spent, plus the
        mark-to-market value of whatever inventory we are still
        holding, valued at current_price. If current_price isn't
        given, falls back to our own last known mid.
        """
        inventory, cash = self.get_inventory_and_cash()
        if current_price is None:
            current_price = self.last_mid
        if current_price is None:
            return cash          # no reference price at all, nothing to mark inventory against
        return cash + inventory * current_price