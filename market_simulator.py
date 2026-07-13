"""
Market simulator: generates random order flow to feed into the
OrderBook, so there is something to test the matching engine (and,
later, the market-making bot) against.
"""

import random
import matplotlib.pyplot as plt
from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker

# TODO (self-cross / self-trade prevention): Order has no owner/trader_id
# field right now. Once the market-making bot places its own bid and ask
# into this same book, there's a theoretical risk of the bot crossing
# against its own resting order. Two ways to handle it later:
#   a) simple: the bot always cancels its previous quote before placing
#      a new one, and never lets its own bid >= its own ask by design.
#   b) robust: add an `owner` field to Order, and in add_limit_order,
#      skip any best_counter whose owner matches order's owner (this is
#      what real exchanges call self-trade prevention).
# (a) is enough for this project's scale.

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
                              spread_pct: float = 0.001, quote_qty: int = 10):
    """
    Same as simulate_market, but a MarketMaker bot also quotes into the
    book every tick, right before that tick's random order arrives.
    Returns book, price_history, and the bot itself (so its state can be
    inspected afterwards).
    """
    if seed is not None:
        random.seed(seed)

    book = OrderBook()
    bot = MarketMaker(book, spread_pct=spread_pct, quote_qty=quote_qty)
    true_price = start_price
    price_history = [(0, true_price)]

    for t in range(1, n_ticks + 1):
        true_price += random.gauss(0, 0.05)
        price_history.append((t, true_price))

        bot.update_quotes(t)                                                # bot re-quotes first

        order = random_order(true_price, timestamp=t)
        book.add_limit_order(order)                                         # then a random trader shows up

    return book, price_history, bot


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


if __name__ == "__main__":
    book, price_history = simulate_market(n_ticks=200, seed=42)
    print(f"Executed trades: {len(book.trades)}")
    print(f"Resting orders in bids: {len(book.bids)}  |  in asks: {len(book.asks)}")
    book.print_book()
    plot_simulation(book, price_history)