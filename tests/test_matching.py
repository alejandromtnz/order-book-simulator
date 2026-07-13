from orderbook import Order, OrderBook, Side

def test_full_fill():
    book = OrderBook()

    # Alguien vende 10 unidades a 102.10 (queda resting, nadie la casa todavía)
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))

    # Llega una compra de 10 unidades exactas al mismo precio -> debe casar entera
    trades = book.add_limit_order(Order(Side.BUY, 102.10, 10, timestamp=1))

    # Se ha generado exactamente 1 trade, por las 10 unidades, al precio 102.10
    assert len(trades) == 1
    assert trades[0].quantity == 10
    assert trades[0].price == 102.10

    # Ninguna de las dos órdenes debe quedar en el libro (se llenaron enteras)
    assert book.best_bid() is None
    assert book.best_ask() is None

def test_partial_fill():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))
    trades = book.add_limit_order(Order(Side.BUY, 102.10, 30, timestamp=1))
    assert len(trades) == 1
    assert trades[0].quantity == 10
    assert book.best_ask() is None          # el ask se agotó, desapareció
    assert book.best_bid().quantity == 20   # sobraron 20 de la compra, quedan resting

def test_walking_the_book():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))
    book.add_resting_order(Order(Side.SELL, 102.20, 20, timestamp=1))
    book.add_resting_order(Order(Side.SELL, 102.30, 50, timestamp=2))
    trades = book.add_limit_order(Order(Side.BUY, 102.30, 60, timestamp=3))
    assert len(trades) == 3
    assert [t.price for t in trades] == [102.10, 102.20, 102.30]
    assert book.best_ask().quantity == 20   # quedan 20 de los 50 originales a 102.30

def test_no_match():
    book = OrderBook()
    book.add_resting_order(Order(Side.SELL, 102.10, 10, timestamp=0))
    trades = book.add_limit_order(Order(Side.BUY, 101.80, 5, timestamp=1))
    assert len(trades) == 0
    assert book.best_bid().price == 101.80
    assert book.best_ask().price == 102.10