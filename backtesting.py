from VaR_t import run_backtest


df = run_backtest()

exceptions = df["is_exception"].sum()
total_days = len(df)

print(
    f"Backtesting-Tage: {total_days} | "
    f"Anzahl der VaR-Verletzungen: {exceptions} | "
    f"Verletzungsrate: {exceptions / total_days:.2%}"
)
