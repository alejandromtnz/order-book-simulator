"""
Market simulator: generates random order flow to feed into the
OrderBook, so there is something to test the matching engine (and,
later, the market-making bot) against.
"""

import random
import matplotlib.pyplot as plt
from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker

# Self-cross / self-trade prevention - RESOLVED, not just deferred.
# Order still has no owner/trader_id field, but it turns out it doesn't
# need one: in MarketMaker.update_quotes, bid = skewed_mid - offset and
# ask = skewed_mid + offset, where offset = mid * spread_pct / 2 is
# always positive. That means bid < ask is guaranteed by construction,
# no matter what the skew does to skewed_mid - the bot's own bid and ask
# can never cross each other. A real exchange still needs a proper
# owner-based self-trade check (many different strategies/desks share
# the same book), but for this single bot, the formula itself already
# rules out the risk.

def random_order(true_price: float, timestamp: int, price_noise: float = 0.10, max_qty: int = 20) -> Order:
    """
    Creates one random Order around the current true_price:
    - side: buy or sell, 50/50 chance
    - price: true_price plus a bit of extra noise, so not every order
      lands exactly on the true price
    - quantity: random integer between 1 and max_qty
    """
    side = random.choice([Side.BUY, Side.SELL])
    price = round(true_price + random.gauss(0, price_noise), 2)                         # mean 0, stddev price_noise
    quantity = random.randint(1, max_qty)                                               # extranoise
    return Order(side=side, price=price, quantity=quantity, timestamp=timestamp)


def simulate_market(n_ticks: int = 200, start_price: float = 100.0, seed: int | None = None):
    """
    Runs a simple market simulation: for n_ticks steps, moves a "true"
    reference price with a small random walk, and feeds one random
    order per tick into a fresh OrderBook using add_limit_order
    (matching + resting logic already built).

    Returns the OrderBook so it is abble inspect trades/book state after
    the run, plus price_history for plotting.
    """
    if seed is not None:
        random.seed(seed)

    book = OrderBook()
    true_price = start_price
    price_history = [(0, true_price)]

    for t in range(1, n_ticks + 1):
        true_price += random.gauss(0, 0.05)                         # ref price moves with a small random walk
        price_history.append((t, true_price))
        order = random_order(true_price, timestamp=t)
        book.add_limit_order(order)

    return book, price_history


def simulate_market_with_bot(n_ticks: int = 200, start_price: float = 100.0, seed: int | None = None,
                              spread_pct: float = 0.001, quote_qty: int = 10, skew_coefficient: float = 0.0,
                              vol_window: int = 20, vol_coefficient: float = 0.0):
    """
    Same as simulate_market, but a MarketMaker bot also quotes into the
    book every tick, right before that tick's random order arrives.
    Returns book, price_history, the bot itself, and pnl_history (the
    bot's mark-to-market PnL at every tick, using that tick's real price).
    """
    if seed is not None:
        random.seed(seed)

    book = OrderBook()
    bot = MarketMaker(book, spread_pct=spread_pct, quote_qty=quote_qty, skew_coefficient=skew_coefficient,
                       vol_window=vol_window, vol_coefficient=vol_coefficient)
    true_price = start_price
    price_history = [(0, true_price)]
    pnl_history = [(0, 0.0)]                                                # bot starts with 0 PnL

    for t in range(1, n_ticks + 1):
        true_price += random.gauss(0, 0.05)
        price_history.append((t, true_price))

        bot.update_quotes(t)                                                # bot re-quotes first

        order = random_order(true_price, timestamp=t)
        book.add_limit_order(order)                                         # then a random trader shows up

        pnl_history.append((t, bot.get_pnl(current_price=true_price)))      # mark-to-market at this tick's real price

    return book, price_history, bot, pnl_history


def plot_simulation(book: OrderBook, price_history, save_path: str = "market_simulation.png"):
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(11, 6), dpi=160)

    xs = [p[0] for p in price_history]
    ys = [p[1] for p in price_history]
    ax.plot(xs, ys, color="#2b2d42", linewidth=1.6, label="True reference price", zorder=2)

    buy_t = [t.timestamp for t in book.trades if t.aggressor_side == Side.BUY]
    buy_p = [t.price for t in book.trades if t.aggressor_side == Side.BUY]
    sell_t = [t.timestamp for t in book.trades if t.aggressor_side == Side.SELL]
    sell_p = [t.price for t in book.trades if t.aggressor_side == Side.SELL]

    ax.scatter(buy_t, buy_p, s=18, color="#ef476f", alpha=0.75,
               label="Buy-aggressor trades", zorder=3, edgecolors="white", linewidths=0.4)
    ax.scatter(sell_t, sell_p, s=18, color="#118ab2", alpha=0.75,
               label="Sell-aggressor trades", zorder=3, edgecolors="white", linewidths=0.4)

    ax.set_title("Order Book Simulator — Market Simulation", fontsize=14, fontweight="bold",
                 color="#2b2d42", pad=14)
    ax.set_xlabel("Tick (arrival order)", fontsize=10.5, color="#555555")
    ax.set_ylabel("Price", fontsize=10.5, color="#555555")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors="#777777", labelsize=9)
    ax.grid(True, alpha=0.35, linewidth=0.6)

    legend = ax.legend(frameon=False, fontsize=9.5, loc="upper left")
    for text in legend.get_texts():
        text.set_color("#444444")

    fig.tight_layout()
    fig.savefig(save_path, facecolor="white")
    plt.close(fig)
    print(f"Chart saved to {save_path}")


def plot_pnl(pnl_history, save_path: str = "pnl_over_time.png"):
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(11, 5), dpi=160)

    xs = [p[0] for p in pnl_history]
    ys = [p[1] for p in pnl_history]
    ax.plot(xs, ys, color="#2b2d42", linewidth=1.6, zorder=2)
    ax.axhline(0, color="#cccccc", linewidth=1, zorder=1)          # zero line, for reference

    ax.fill_between(xs, ys, 0, where=[y >= 0 for y in ys], color="#06a77d", alpha=0.15, zorder=1)
    ax.fill_between(xs, ys, 0, where=[y < 0 for y in ys], color="#ef476f", alpha=0.15, zorder=1)

    ax.set_title("Order Book Simulator — Bot PnL Over Time", fontsize=14, fontweight="bold",
                 color="#2b2d42", pad=14)
    ax.set_xlabel("Tick (arrival order)", fontsize=10.5, color="#555555")
    ax.set_ylabel("PnL", fontsize=10.5, color="#555555")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors="#777777", labelsize=9)
    ax.grid(True, alpha=0.35, linewidth=0.6)

    fig.tight_layout()
    fig.savefig(save_path, facecolor="white")
    plt.close(fig)
    print(f"Chart saved to {save_path}")


if __name__ == "__main__":
    # skew_coefficient=0.01 chosen from evaluate_skew.py's 50-seed sweep
    # (see README Findings) - the best mean PnL / lowest variance point
    # before higher values start overcorrecting and giving up edge.
    # vol_coefficient=200 chosen from evaluate_volatility.py's 50-seed sweep -
    # keeps ~85% of normal trading activity while still trimming risk in
    # jumpy periods; much higher values "win" on PnL only because the bot
    # quotes so wide it stops trading altogether, which isn't a real win.
    book, price_history, bot, pnl_history = simulate_market_with_bot(
        n_ticks=200, seed=42, skew_coefficient=0.01, vol_coefficient=200
    )

    print(f"Executed trades: {len(book.trades)}")
    print(f"Resting orders in bids: {len(book.bids)}  |  in asks: {len(book.asks)}")
    book.print_book()

    inventory, cash = bot.get_inventory_and_cash()
    pnl = bot.get_pnl()
    print(f"Bot inventory: {inventory}")
    print(f"Bot cash: {cash:.2f}")
    print(f"Bot PnL: {pnl:.2f}")

    plot_simulation(book, price_history, save_path="market_simulation_with_volatility.png")
    plot_pnl(pnl_history, save_path="pnl_over_time.png")