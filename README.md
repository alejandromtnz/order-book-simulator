# Order Book Simulator

A limit order book matching engine built from scratch in Python, as a hands-on
way to understand the mechanics behind quantitative trading and market making
(the kind of system used by prop trading firms like Optiver, IMC, or Da Vinci
Trading).

This is a work in progress, built incrementally, weekend by weekend, with a
strong focus on correctness (tested with pytest at every step) before adding
any complexity.

## What's implemented so far

- **`Order`**: represents a single limit order (side, price, quantity,
  arrival timestamp). Tracks both the remaining quantity and the original
  quantity requested, so fill history isn't lost as an order gets executed.
- **`Trade`**: an immutable record of a completed execution between a buy and
  a sell order (frozen dataclass - a trade can never change once it happened).
- **`OrderBook`**: the matching engine itself.
  - `add_resting_order`: parks an order in the book (bids/asks), keeping both
    sides sorted by price-time priority.
  - `best_bid` / `best_ask`: O(1) access to the top of the book.
  - `add_limit_order`: the core matching loop. Handles full fills, partial
    fills, walking the book across multiple price levels, and orders that
    don't cross (rest in the book) - all through a single, tested loop.
  - `cancel_order`: removes a resting order by id before it executes.
  - `print_book`: a quick visual dump of the current book depth, useful for
    debugging.

## Project structure

```
order-book-simulator/
  orderbook.py          # Order, Trade, OrderBook
  tests/
    test_orderbook.py    # storage / best_bid / best_ask
    test_matching.py      # the 4 matching cases
    test_cancel.py        # cancellation
  README.md
```

## Running it

```bash
python3 -m pip install pytest
python3 -m pytest tests/ -v
```

## Roadmap

This is the first of several weekend milestones. Coming up:

1. Random order flow generator, to simulate a live market.
2. A market-making bot: symmetric quoting around the mid-price, then
   inventory-skewed quoting to manage risk.
3. PnL tracking (realized + mark-to-market) and visualization.
4. Optional: port the matching engine core to C++ for performance.

## Why this project

Order books and market making are the daily mechanics behind quantitative
trading firms. This project is a from-scratch, tested implementation of that
mechanism, built to genuinely understand price-time priority, matching
logic, and the risk a market maker takes on - not just to have a line on a
CV.