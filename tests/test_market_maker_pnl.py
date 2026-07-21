from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker


def test_inventory_and_cash_after_bot_buys():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)

    # seed the book so the bot has a mid to quote around
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))
    bot.update_quotes(timestamp=2)   # bot now has bid=99.5, ask=100.5 resting

    # a random seller crosses the bot's bid at 99.5, selling 3 units to it
    book.add_limit_order(Order(Side.SELL, 99.0, 3, timestamp=3))

    inventory, cash = bot.get_inventory_and_cash()
    assert inventory == 3           # bot bought 3 units
    assert cash == -3 * 99.5        # bot paid 99.5 per unit (the resting bid's own price)


def test_inventory_and_cash_after_bot_sells():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)

    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))
    bot.update_quotes(timestamp=2)   # bid=99.5, ask=100.5

    # a random buyer crosses the bot's ask at 100.5, buying 4 units from it
    book.add_limit_order(Order(Side.BUY, 101.0, 4, timestamp=3))

    inventory, cash = bot.get_inventory_and_cash()
    assert inventory == -4          # bot sold 4 units
    assert cash == 4 * 100.5        # bot collected 100.5 per unit


def test_no_trades_means_zero_inventory_and_cash():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)
    bot.update_quotes(timestamp=0)   # nothing to quote against, no-op

    inventory, cash = bot.get_inventory_and_cash()
    assert inventory == 0
    assert cash == 0