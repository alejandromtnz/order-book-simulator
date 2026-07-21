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
  cash, and total PnL (realized + mark-to-market) from its own trades, and
  skews its quotes to correct accumulated inventory.
- **`evaluate_skew.py`**: runs the bot across many random seeds per
  candidate `skew_coefficient`, to judge each one by its average behaviour
  (and variance) instead of a single lucky/unlucky run.

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
    test_inventory_skew.py          # inventory skew direction
  README.md
```

## Running it

```bash
python3 -m pip install pytest matplotlib
python3 -m pytest tests/ -v
python3 market_simulator.py
```

## Findings

**Single-run check (seed=42, 200 ticks):** with no inventory management,
the bot drifted to an inventory of **-279 units** (heavily net short) and
a PnL of -38.71. A large cash balance (+27984.05) hid an equally large
liability - the 279 units it still "owed" at market price - which is why
raw cash is a misleading number on its own; PnL (cash + inventory marked
to the current price) is what actually matters.

| | Inventory | Cash | PnL |
|---|---|---|---|
| No skew | -279.0 | 27984.05 | -38.71 |
| skew=0.001 | -10.0 | 993.68 | -11.72 |
| skew=0.01 | 0.0 | -27.59 | -27.59 |

(Note skew=0.01 looks "worse" than skew=0.001 on this ONE seed - that's
exactly the trap the 50-seed sweep below catches: a single run can't tell
you which coefficient is actually better.)

**Why a single run isn't enough:** picking a `skew_coefficient` from one
seed is unreliable - `evaluate_skew.py` reruns each candidate across 50
random seeds and reports the mean PnL, its standard deviation, and the
mean absolute inventory:

| skew | mean PnL | stdev PnL | mean \|inventory\| |
|---|---|---|---|
| 0.0    | -24.66  | 56.93 | 368.54 |
| 0.0005 | -31.42  | 51.96 | 163.16 |
| 0.001  | -29.76  | 35.27 |  81.08 |
| 0.002  | -27.64  | 31.84 |  38.60 |
| 0.005  | -16.76  | 16.63 |  16.60 |
| **0.01**   | **-15.62**  | **12.50** |   **9.40** |
| 0.02   | -23.58  |  9.39 |   6.14 |
| 0.05   | -79.93  | 14.92 |   4.66 |
| 0.1    | -176.22 | 29.70 |   4.92 |
| 0.2    | -365.39 | 70.53 |   4.60 |

Across 50 seeds, `skew=0.001` is actually mediocre - the earlier
single-seed result favouring it was noise from one lucky run. The real
picture: inventory risk drops steadily as skew increases, but PnL only
improves up to **~0.01**, then gets sharply worse (-15.62 -> -365.39) even
though inventory barely changes further (it's already near its floor,
~4.6-9 units). Beyond that point the bot is overcorrecting - quoting so
aggressively to stay flat that it gives away edge on every trade for no
extra risk reduction. `skew_coefficient=0.01` is the value now used in
`market_simulator.py`'s default run.

## Roadmap

This is the first of several weekend milestones. Coming up:

1. ~~Random order flow generator, to simulate a live market.~~ Done.
2. ~~A market-making bot with percentage-based spread quoting.~~ Done.
3. ~~Inventory and PnL tracking for the bot.~~ Done.
4. ~~Inventory-skewed quoting, to manage the risk found above.~~ Done.
5. ~~PnL chart over the course of a simulation.~~ Done (`pnl_over_time.png`).
6. Optional: volatility-based spread, an Avellaneda-Stoikov-style model,
   robust self-trade prevention, and a C++ port of the matching engine core.

## Why this project

Order books and market making are the daily mechanics behind quantitative
trading firms. This project is a from-scratch, tested implementation of that
mechanism, built to genuinely understand price-time priority, matching
logic, and the risk a market maker takes on - not just to have a line on a
CV.