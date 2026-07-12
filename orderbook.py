from dataclasses import dataclass, field
from enum import Enum
import itertools
 
 
class Side(Enum):
    BUY = "buy"
    SELL = "sell"
 
 
_id_counter = itertools.count(1)
 
 
@dataclass                                                      # intention, not frozen
class Order:
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