from orderbook import Order, OrderBook, Side

def test_full_fill():
    book = OrderBook()

    # someone sells 10 units at 102.10 (rests, nobody matches it yet)
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))

    # a buy for the exact same 10 units and price arrives -> should fully match
    trades = book.add_limit_order(Order(Side.BUY, 102.10, 10, timestamp=1))

    # exactly 1 trade generated, for the 10 units, at price 102.10
    assert len(trades) == 1
    assert trades[0].quantity == 10
    assert trades[0].price == 102.10

    # neither order should remain in the book (both filled in full)
    assert book.best_bid() is None
    assert book.best_ask() is None

def test_partial_fill():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))
    trades = book.add_limit_order(Order(Side.BUY, 102.10, 30, timestamp=1))
    assert len(trades) == 1
    assert trades[0].quantity == 10
    assert book.best_ask() is None          # ask ran out, gone
    assert book.best_bid().quantity == 20   # 20 left over from the buy, resting

def test_walking_the_book():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 102.20, 20, timestamp=1))
    book.add_resting_order(Order(Side.SELL, 102.30, 50, timestamp=2))
    trades = book.add_limit_order(Order(Side.BUY, 102.30, 60, timestamp=3))
    assert len(trades) == 3
    assert [t.price for t in trades] == [102.10, 102.20, 102.30]
    assert book.best_ask().quantity == 20   # 20 left of the original 50 at 102.30

def test_no_match():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))
    trades = book.add_limit_order(Order(Side.BUY, 101.80, 5, timestamp=1))
    assert len(trades) == 0
    assert book.best_bid().price == 101.80
    assert book.best_ask().price == 102.10