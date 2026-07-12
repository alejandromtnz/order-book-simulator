from dataclasses import dataclass, field
from enum import Enum
import itertools
 
 
class Side(Enum):
    BUY = "buy"
    SELL = "sell"
 
 
_id_counter = itertools.count(1)
 
 
@dataclass                                                      # intentionally not frozen
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
