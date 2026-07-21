"""
Same idea as evaluate_skew.py, but for vol_coefficient: runs the bot
across many random seeds for each candidate value, so we judge each one
by its AVERAGE behaviour (and how much it varies), not by a single
lucky or unlucky simulation. skew_coefficient is fixed at 0.01 (the
value evaluate_skew.py already found to be best), so this sweep isolates
the effect of the volatility-based spread on top of that.
"""

import statistics
from market_simulator import simulate_market_with_bot


def evaluate_volatility(vol_values, n_seeds: int = 50, n_ticks: int = 200,
                         skew_coefficient: float = 0.01, vol_window: int = 20):
    results = {}
    for vol_coef in vol_values:
        pnls = []
        abs_inventories = []
        for seed in range(n_seeds):
            book, price_history, bot, pnl_history = simulate_market_with_bot(
                n_ticks=n_ticks, seed=seed, skew_coefficient=skew_coefficient,
                vol_window=vol_window, vol_coefficient=vol_coef
            )
            inventory, cash = bot.get_inventory_and_cash()
            pnl = bot.get_pnl()
            pnls.append(pnl)
            abs_inventories.append(abs(inventory))

        results[vol_coef] = {
            "mean_pnl": statistics.mean(pnls),
            "stdev_pnl": statistics.stdev(pnls),
            "mean_abs_inventory": statistics.mean(abs_inventories),
        }
    return results


def print_results(results):
    print(f"{'vol_coef':<10}{'mean PnL':>12}{'stdev PnL':>12}{'mean |inv|':>12}")
    for vol_coef, r in results.items():
        print(f"{vol_coef:<10}{r['mean_pnl']:>12.2f}{r['stdev_pnl']:>12.2f}{r['mean_abs_inventory']:>12.2f}")


if __name__ == "__main__":
    vol_values = [0, 10, 50, 100, 200, 500, 1000, 2000, 5000]
    results = evaluate_volatility(vol_values, n_seeds=50, n_ticks=200)
    print_results(results)
