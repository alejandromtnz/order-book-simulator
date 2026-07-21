from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker


def test_pnl_with_explicit_price_marks_inventory_to_market():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)

    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))
    bot.update_quotes(timestamp=2)                          # bid=99.5, ask=100.5

    book.add_limit_order(Order(Side.SELL, 99.0, 3, timestamp=3))  # bot buys 3 @ 99.5

    pnl = bot.get_pnl(current_price=100.0)
    # cash = -3*99.5 = -298.5 ; inventory*price = 3*100 = 300 ; pnl = 1.5
    assert round(pnl, 2) == 1.5


def test_pnl_falls_back_to_last_mid_when_no_price_given():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)

    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))
    bot.update_quotes(timestamp=2)                          # last_mid becomes 100

    book.add_limit_order(Order(Side.SELL, 99.0, 3, timestamp=3))

    pnl = bot.get_pnl()   # no price given -> uses self.last_mid (100)
    assert round(pnl, 2) == 1.5


def test_pnl_zero_with_no_trades():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)
    assert bot.get_pnl(current_price=100.0) == 0
