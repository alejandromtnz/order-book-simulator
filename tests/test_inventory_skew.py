from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker


def test_zero_inventory_means_no_skew():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5, skew_coefficient=0.01)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot.update_quotes(timestamp=2)   # inventory is 0, so skew should do nothing

    assert bot.my_bid.price == 99.5    # same as the unskewed version
    assert bot.my_ask.price == 100.5


def test_short_inventory_pushes_quotes_up():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5, skew_coefficient=0.01)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot.update_quotes(timestamp=2)                              # bid=99.5, ask=100.5
    book.add_limit_order(Order(Side.BUY, 101.0, 20, timestamp=3))  # someone buys 20 from the bot's ask

    bot.update_quotes(timestamp=4)   # bot is now short 20 units -> quotes should shift UP

    assert bot.my_bid.price > 99.5
    assert bot.my_ask.price > 100.5


def test_long_inventory_pushes_quotes_down():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5, skew_coefficient=0.01)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot.update_quotes(timestamp=2)                               # bid=99.5, ask=100.5
    book.add_limit_order(Order(Side.SELL, 99.0, 20, timestamp=3))  # someone sells 20 to the bot's bid

    bot.update_quotes(timestamp=4)   # bot is now long 20 units -> quotes should shift DOWN

    assert bot.my_bid.price < 99.5
    assert bot.my_ask.price < 100.5