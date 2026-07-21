from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker


def test_zero_vol_coefficient_keeps_old_spread():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5, vol_coefficient=0.0)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot.update_quotes(timestamp=2)   # mid = 100, offset = 100 * 0.01 / 2 = 0.5

    assert bot.my_bid.price == 99.5
    assert bot.my_ask.price == 100.5


def test_high_volatility_widens_the_spread():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5, vol_coefficient=1.0, vol_window=5)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))
    bot.mid_history = [90.0, 110.0, 90.0, 110.0]   # fake a very jumpy recent history

    bot.update_quotes(timestamp=2)   # mid = 100, but volatility should widen the spread past 0.5

    unskewed_offset = bot.my_ask.price - 100.0
    assert unskewed_offset > 0.5   # bigger than the calm-market offset from the test above


def test_calm_market_gives_the_same_spread_as_no_volatility():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5, vol_coefficient=1.0, vol_window=5)
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))
    bot.mid_history = [100.0, 100.0, 100.0]   # dead calm, stdev == 0

    bot.update_quotes(timestamp=2)

    assert bot.my_bid.price == 99.5
    assert bot.my_ask.price == 100.5