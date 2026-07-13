from dataclasses import dataclass, field
from enum import Enum
import itertools
 
 
class Side(Enum):
    BUY = "buy"
    SELL = "sell"
 
 
_id_counter = itertools.count(1)
 
 
@dataclass                                                      
class Order:                                                    # intention, not frozen
    side: Side
    price: float
    quantity: float          
    timestamp: int                                              # arrival time
    id: int = field(default_factory=lambda: next(_id_counter))  # autom id
    
    original_quantity: float = field(init=False)  
    def __post_init__(self):
        self.original_quantity = self.quantity


@dataclass
class Trade:                                                    # frozen
    buy_order_id: int
    sell_order_id: int
    price: float              
    quantity: float
    timestamp: int
    aggressor_side: Side


class OrderBook:
    def __init__(self):
        self.bids: list[Order] = []
        self.asks: list[Order] = []
        self.trades: list[Trade] = []

    def add_resting_order(self, order: "Order"):
        if order.side == Side.BUY:
            self.bids.append(order)
            self.bids.sort(key=lambda o: (-o.price, o.timestamp))
        else:
            self.asks.append(order)
            self.asks.sort(key=lambda o: (o.price, o.timestamp))

        # TODO:
        # lvl 2 - bisect
        # lvl 3 - heapq / pip install sortedcontainers

    def best_bid(self):
        return self.bids[0] if self.bids else None

    def best_ask(self):
        return self.asks[0] if self.asks else None

    def add_limit_order(self, order: "Order") -> list["Trade"]:
        trades = []

        counter_book = self.asks if order.side == Side.BUY else self.bids           # makes unnecessary an if/else for the counter book

        while order.quantity > 0 and len(counter_book) > 0:                         # running while orders to match and order not fully filled
            best_counter = counter_book[0]

            if order.side == Side.BUY and order.price < best_counter.price:         # my buy > other sell !=
                break
            if order.side == Side.SELL and order.price > best_counter.price:        # my sell < other buy !=
                break

            filled_qty = min(order.quantity, best_counter.quantity)                 # minimum of the two quantities to fill the order, otherwise it would be a negative quantity

            if order.side == Side.BUY:                                              # id of the buy order is always the one that is being added to the book, and the id of the sell order is always the one that is being matched against it
                trade = Trade(buy_order_id=order.id, sell_order_id=best_counter.id,
                          price=best_counter.price, quantity=filled_qty,
                          timestamp=order.timestamp, aggressor_side=order.side)
            
            else:
                trade = Trade(buy_order_id=best_counter.id, sell_order_id=order.id,
                          price=best_counter.price, quantity=filled_qty,
                          timestamp=order.timestamp, aggressor_side=order.side)
            
            trades.append(trade)
            self.trades.append(trade)

            order.quantity -= filled_qty                                            # minus the filled quantity from the order being added to the book
            best_counter.quantity -= filled_qty

            if best_counter.quantity == 0:                                          # if the best counter order is fully filled, remove it from the book
                counter_book.pop(0)

        if order.quantity > 0:                                                      # if the order being added to the book is not fully filled, add it to the book
            self.add_resting_order(order)

        return trades
    
    def cancel_order(self, order_id: int) -> bool:                                  # cancel an order by id, return True if found and removed, False otherwise
        for book_side in (self.bids, self.asks):                                    # iterate over both sides of the book
            for i, o in enumerate(book_side):                                       # iterate over the position and number of the order 
                if o.id == order_id:
                    book_side.pop(i)
                    return True
        return False                                                                # do not found the order

    def print_book(self, depth: int = 5):
        print("----- ASKS (worst to best) -----")
        for a in reversed(self.asks[:depth]):
            print(f"  {a.price:>8.2f}  |  qty {a.quantity}")
        print("---------------------------------")
        for b in self.bids[:depth]:
            print(f"  {b.price:>8.2f}  |  qty {b.quantity}")
        print("----- BIDS (best to worst) ------")

