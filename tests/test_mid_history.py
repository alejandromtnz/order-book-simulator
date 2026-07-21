from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker


def test_mid_history_records_first_real_mid():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot.update_quotes(timestamp=2)   # mid = (99 + 101) / 2 = 100.0

    assert bot.mid_history == [100.0]


def test_mid_history_grows_each_tick():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot.update_quotes(timestamp=2)
    bot.update_quotes(timestamp=3)
    bot.update_quotes(timestamp=4)

    assert len(bot.mid_history) == 3


def test_mid_history_stays_empty_without_a_real_mid():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)   # empty book, no bid or ask yet

    bot.update_quotes(timestamp=0)

    assert bot.mid_history == []