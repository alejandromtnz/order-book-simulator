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
- **`market_simulator.py`**: generates random order flow around a reference
  price that moves with a small random walk, to simulate a live market.
- **`MarketMaker`** (`market_maker.py`): a level-2 market-making bot that
  quotes a percentage-based spread around the mid-price, always cancelling
  its previous quote before placing a new one. Tracks its own inventory,
  cash, and total PnL (realized + mark-to-market) from its own trades.

## Project structure

```
order-book-simulator/
  orderbook.py            # Order, Trade, OrderBook
  market_simulator.py      # random order flow + true-price random walk
  market_maker.py           # the bot
  tests/
    test_orderbook.py        # storage / best_bid / best_ask
    test_matching.py          # the 4 matching cases
    test_cancel.py            # cancellation
    test_market_maker.py       # bot quoting behaviour
    test_market_maker_pnl.py    # inventory / cash tracking
    test_market_maker_totalpnl.py  # PnL calculation
  README.md
```

## Running it

```bash
python3 -m pip install pytest matplotlib
python3 -m pytest tests/ -v
python3 market_simulator.py
```

## Findings

Running the bot for 200 ticks with no inventory management
(`market_simulation_no_skew.png`) shows the real risk of a naive
percentage-spread strategy: the bot drifted to an inventory of **-279
units** (heavily net short), and ended with a slightly negative PnL
(-38.71), despite collecting a large amount of cash from selling. Without
any mechanism to correct for accumulated position, the bot has no way to
push itself back toward neutral - this is the concrete motivation for
adding inventory skew next.

*(to fill in once inventory skew is implemented: same seed, comparison
chart `market_simulation_with_skew.png`, and the resulting inventory/PnL
numbers)*

## Roadmap

This is the first of several weekend milestones. Coming up:

1. ~~Random order flow generator, to simulate a live market.~~ Done.
2. ~~A market-making bot with percentage-based spread quoting.~~ Done.
3. ~~Inventory and PnL tracking for the bot.~~ Done.
4. Inventory-skewed quoting, to manage the risk found above.
5. PnL chart over the course of a simulation.
6. Optional: volatility-based spread, an Avellaneda-Stoikov-style model,
   robust self-trade prevention, and a C++ port of the matching engine core.

## Why this project

Order books and market making are the daily mechanics behind quantitative
trading firms. This project is a from-scratch, tested implementation of that
mechanism, built to genuinely understand price-time priority, matching
logic, and the risk a market maker takes on - not just to have a line on a
CV.