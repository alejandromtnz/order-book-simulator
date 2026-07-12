from dataclasses import dataclass, field
from enum import Enum
import itertools
 
 
class Side(Enum):
    BUY = "buy"
    SELL = "sell"
 
 
_id_counter = itertools.count(1)
 
 
@dataclass
class Order:
    side: Side
    price: float
    quantity: float          
    timestamp: int           
    id: int = field(default_factory=lambda: next(_id_counter))
 
