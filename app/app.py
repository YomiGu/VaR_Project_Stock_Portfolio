import sys
import pandas as pd
import streamlit as st

# Projektordner zum Python-Pfad hinzufügen,
# damit die Funktionen aus VaR_t.py importiert werden können
sys.path.insert(0, "/Users/liwen/Documents/VaR_Project")

from VaR_t import run_backtest

st.set_page_config(page_title="Portfolio-VaR-Dashboard", layout="wide")
st.title("Portfolio VaR & Backtesting Dashboard")


@st.cache_data
def load_backtest_data():
    df = run_backtest()
    df = df.rename(columns={
        "var": "99% 1-Day VaR",
        "realized_pnl": "Realized P&L"
    })
    return df.set_index("date")


df_bt = load_backtest_data()

col1, col2 = st.columns(2)
# Letzten berechneten VaR-Wert aus dem Backtesting nehmen
latest_var = df_bt["99% 1-Day VaR"].iloc[-1]
# Aktuellen 1-Tages-VaR anzeigen
col1.metric("Latest 1-Day VaR", f"{latest_var:.2%}")

# Anzahl der Tage zählen, an denen der tatsächliche Verlust 
# schlechter als der vorhergesagte VaR war
exceptions = (df_bt["Realized P&L"] < df_bt["99% 1-Day VaR"]).sum()
col2.metric("Backtest Exceptions", f"{exceptions} times")

# Zeitreihe von VaR und Realisierter Gewinn/Verlust anzeigen
st.subheader("VaR vs Realized P&L (Backtesting)")
st.line_chart(df_bt[["99% 1-Day VaR", "Realized P&L"]])
