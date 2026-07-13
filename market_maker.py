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
    def __init__(self, book: OrderBook, spread_pct: float = 0.001, quote_qty: int = 10):        # spread percentage = 0,1%
        self.book = book
        self.spread_pct = spread_pct
        self.quote_qty = quote_qty
        self.my_bid: Order | None = None                    # our resting bid right now, if any
        self.my_ask: Order | None = None                    # our resting ask right now, if any
        self.last_mid: float | None = None                  # fallback price if book has no bid/ask yet

    def _cancel_my_orders(self):
        if self.my_bid is not None:
            self.book.cancel_order(self.my_bid.id)          # rip down the old bid
            self.my_bid = None
        if self.my_ask is not None:
            self.book.cancel_order(self.my_ask.id)          # rip down the old ask
            self.my_ask = None

    def _compute_mid(self) -> float | None:
        best_bid = self.book.best_bid()
        best_ask = self.book.best_ask()
        if best_bid is not None and best_ask is not None:
            self.last_mid = (best_bid.price + best_ask.price) / 2   # both sides exist, use real mid
        return self.last_mid

    def update_quotes(self, timestamp: int):
        self._cancel_my_orders()                # always kill the old quote before anything else

        mid = self._compute_mid()
        if mid is None:
            return                              # no reference price yet, skip this tick

        offset = mid * self.spread_pct / 2
        bid_price = round(mid - offset, 2)
        ask_price = round(mid + offset, 2)

        bid_order = Order(Side.BUY, bid_price, self.quote_qty, timestamp)
        self.book.add_limit_order(bid_order)
        if bid_order.quantity > 0:              # still resting, not fully filled instantly
            self.my_bid = bid_order

        ask_order = Order(Side.SELL, ask_price, self.quote_qty, timestamp)
        self.book.add_limit_order(ask_order)
        if ask_order.quantity > 0:              # still resting, not fully filled instantly
            self.my_ask = ask_order
