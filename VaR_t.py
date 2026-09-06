import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from database.portfolio_t import (
    prices,
    get_random_trades,
    get_portfolio_weights_at_target_date,
    get_historical_portfolio_returns
)


def run_backtest():
    trades = get_random_trades()
    all_dates = prices["date"].drop_duplicates().sort_values().reset_index(drop=True)

    bt_data = []

    # Start ab dem 251. Tag (Index 250).
    # Die ersten 250 Tage dienen nur als erstes Beobachtungsfenster.
    for i in range(250, len(all_dates)):
        target_date = all_dates.iloc[i]

        # Historische Renditen der letzten 250 Tage holen und VaR berechnen
        hist_returns = get_historical_portfolio_returns(
            trades,
            target_date,
            observation_period=250
        )

        if hist_returns.empty:
            continue

        var_pred = hist_returns["dailyreturns"].quantile(0.01)

        # Tatsächliche Rendite des Portfolios am Zieltag berechnen
        weights = get_portfolio_weights_at_target_date(
            trades,
            target_date
        )[["isin", "weight"]]

        today_prices = prices[
            prices["date"] == target_date
        ].merge(weights, on="isin", how="inner")

        realized_pnl = (
            today_prices["dailyreturns"] * today_prices["weight"]
        ).sum()

        bt_data.append({
            "date": target_date,
            "var": var_pred,
            "realized_pnl": realized_pnl,
            "is_exception": 1 if realized_pnl < var_pred else 0
        })

    return pd.DataFrame(bt_data)


if __name__ == "__main__":
    df = run_backtest()

    # VaR, tatsächliche Rendite und VaR-Verletzungen in einem Plot darstellen
    plt.figure(figsize=(10, 5))

    plt.plot(
        df["date"],
        df["realized_pnl"],
        label="Realisierte Portfolio-Rendite",
        color="gray",
        alpha=0.5
    )

    plt.plot(
        df["date"],
        df["var"],
        label="99%-1-Tages-VaR",
        color="red",
        linestyle="--"
    )

    exceptions = df[df["is_exception"] == 1]

    plt.scatter(
        exceptions["date"],
        exceptions["realized_pnl"],
        color="red",
        label="VaR-Verletzung",
        zorder=5
    )

    plt.title("VaR und realisierte Portfolio-Rendite im Backtesting")
    plt.xlabel("Datum")
    plt.ylabel("Rendite")
    plt.legend()
    plt.tight_layout()
    plt.show()

    print(
        f"Backtesting-Tage / VaR-Beobachtungen: {len(df)} | "
        f"Anzahl der VaR-Verletzungen: {df['is_exception'].sum()}"
    )
