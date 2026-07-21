"""
Runs the bot across many random seeds for each candidate skew_coefficient,
so we judge each value by its AVERAGE behaviour (and how much it varies),
not by a single lucky or unlucky simulation.
"""

import statistics
from market_simulator import simulate_market_with_bot


def evaluate_skew(skew_values, n_seeds: int = 50, n_ticks: int = 200):
    results = {}
    for skew in skew_values:
        pnls = []
        abs_inventories = []
        for seed in range(n_seeds):
            book, price_history, bot, pnl_history = simulate_market_with_bot(
                n_ticks=n_ticks, seed=seed, skew_coefficient=skew
            )
            inventory, cash = bot.get_inventory_and_cash()
            pnl = bot.get_pnl()
            pnls.append(pnl)
            abs_inventories.append(abs(inventory))

        results[skew] = {
            "mean_pnl": statistics.mean(pnls),
            "stdev_pnl": statistics.stdev(pnls),
            "mean_abs_inventory": statistics.mean(abs_inventories),
        }
    return results


def print_results(results):
    print(f"{'skew':<10}{'mean PnL':>12}{'stdev PnL':>12}{'mean |inv|':>12}")
    for skew, r in results.items():
        print(f"{skew:<10}{r['mean_pnl']:>12.2f}{r['stdev_pnl']:>12.2f}{r['mean_abs_inventory']:>12.2f}")


if __name__ == "__main__":
    skew_values = [0.0, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
    results = evaluate_skew(skew_values, n_seeds=50, n_ticks=200)
    print_results(results)