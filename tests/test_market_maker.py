from orderbook import Order, OrderBook, Side
from market_maker import MarketMaker


def test_quotes_inside_the_existing_spread():
    book = OrderBook()
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)  # 1% spread around mid
    bot.update_quotes(timestamp=2)

    assert bot.my_bid is not None
    assert bot.my_ask is not None
    assert bot.my_bid.price == 99.5
    assert bot.my_ask.price == 100.5
    # our orders should NOT have matched the outer 99/101 orders
    assert len(book.bids) == 2
    assert len(book.asks) == 2


def test_requoting_cancels_previous_orders():
    book = OrderBook()
    book.add_resting_order(Order(Side.BUY, 99.0, 100, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 101.0, 100, timestamp=1))

    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)
    bot.update_quotes(timestamp=2)
    first_bid_id = bot.my_bid.id
    first_ask_id = bot.my_ask.id

    bot.update_quotes(timestamp=3)

    # the old quote ids should no longer be findable in the book
    assert book.cancel_order(first_bid_id) is False
    assert book.cancel_order(first_ask_id) is False
    # exactly one bot bid and one bot ask should exist now (still 2+2 total)
    assert len(book.bids) == 2
    assert len(book.asks) == 2


def test_no_quote_when_book_is_empty_and_no_last_mid():
    book = OrderBook()
    bot = MarketMaker(book, spread_pct=0.01, quote_qty=5)

    bot.update_quotes(timestamp=0)

    assert bot.my_bid is None
    assert bot.my_ask is None
