import statistics

from orderbook import OrderBook
from market_maker import MarketMaker


def test_volatility_zero_with_no_history():
    book = OrderBook()
    bot = MarketMaker(book)

    assert bot._recent_volatility() == 0.0


def test_volatility_zero_with_a_single_point():
    book = OrderBook()
    bot = MarketMaker(book)
    bot.mid_history = [100.0]

    assert bot._recent_volatility() == 0.0


def test_volatility_matches_stdev_of_recent_window():
    book = OrderBook()
    bot = MarketMaker(book, vol_window=3)
    bot.mid_history = [100.0, 101.0, 99.0, 102.0, 100.0]   # only the last 3 count: 99, 102, 100

    expected = statistics.stdev([99.0, 102.0, 100.0])

    assert bot._recent_volatility() == expected


def test_volatility_ignores_points_older_than_the_window():
    book = OrderBook()
    bot = MarketMaker(book, vol_window=2)
    bot.mid_history = [1000.0, 2000.0, 100.0, 100.0]   # last 2 are identical -> 0 volatility

    assert bot._recent_volatility() == 0.0