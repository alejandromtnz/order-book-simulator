from orderbook import Order, OrderBook, Side

def test_best_bid_best_ask_empty_book():
    book = OrderBook()
    assert book.best_bid() is None
    assert book.best_ask() is None

def test_bids_sorted_by_price_then_time():
    book = OrderBook()
    book.add_resting_order(Order(Side.BUY, 102.10, 5, timestamp=0))
    book.add_resting_order(Order(Side.BUY, 103.00, 5, timestamp=1))
    book.add_resting_order(Order(Side.BUY, 103.00, 3, timestamp=2))  # empate de precio

    assert book.best_bid().price == 103.00
    assert book.best_bid().timestamp == 1  # el que llegó antes gana el empate

def test_asks_sorted_by_price_then_time():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 105.00, 5, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 104.50, 5, timestamp=1))

    assert book.best_ask().price == 104.50

def test_cancel_existing_order():
    book = OrderBook()
    o1 = Order(Side.BUY, 102.10, 5, timestamp=0)
    book.add_resting_order(o1)

    assert book.cancel_order(o1.id) is True
    assert book.best_bid() is None

def test_cancel_unknown_id_returns_false():
    book = OrderBook()
    book.add_resting_order(Order(Side.BUY, 102.10, 5, timestamp=0))

    assert book.cancel_order(9999) is False
    assert book.best_bid() is not None  # la orden real sigue ahí, intacta