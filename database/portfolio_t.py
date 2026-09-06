import pandas as pd
import random

avgo = pd.read_csv("data/avgo_clean.csv")
dell = pd.read_csv("data/dell_clean.csv")
nvda = pd.read_csv("data/nvda_clean.csv")

for data in [avgo, dell, nvda]:
    data["date"] = pd.to_datetime(data["date"])

prices = pd.concat([avgo, dell, nvda], ignore_index=True)
prices = prices.sort_values("date")


def get_stock_in_portfolio_at_date(trades, isin, date):
    stock_trades = trades[
        (trades["isin"] == isin) &
        (trades["date"] <= date)
    ]

    buy_trades = stock_trades[stock_trades["type"] == "buy"]
    total_buy = buy_trades["amount"].sum()

    sell_trades = stock_trades[stock_trades["type"] == "sell"]
    total_sell = sell_trades["amount"].sum()

    return total_buy - total_sell


def get_portfolio_state_at_date(trades, date):
    states = []

    # 核心修改：只找截至今天真正发生过交易的股票
    past_trades = trades[trades["date"] <= date]
    traded_isins = past_trades["isin"].unique()

    for isin in traded_isins:
        amount = get_stock_in_portfolio_at_date(trades, isin, date)

        # 只记录手里还有持仓的股票
        if amount > 0:
            states.append({
                "isin": isin,
                "amount": amount,
                "date": date
            })

    return pd.DataFrame(states)


# 4. 计算某个日期的持仓权重
def get_portfolio_weights_at_target_date(trades, target_date):
    portfolio = get_portfolio_state_at_date(trades, target_date)

    # 如果今天还没买过任何股票，直接返回空表格
    if portfolio.empty:
        return portfolio

    # 匹配当天的收盘价
    portfolio = portfolio.merge(
        prices[["date", "isin", "close"]],
        on=["date", "isin"],
        how="left"
    )

    # 市值 = 数量 * 价格
    portfolio["value"] = portfolio["amount"] * portfolio["close"]

    # 计算总市值
    total_value = portfolio["value"].sum()

    # 权重 = 股票市值 / 总市值（加个 if 保护，防止总市值为 0 报错）
    if total_value > 0:
        portfolio["weight"] = portfolio["value"] / total_value
    else:
        portfolio["weight"] = 0

    return portfolio


# 5. 生成随机交易数据
def get_random_trades():
    random.seed(2022)

    trading_dates = (
        prices["date"]
        .drop_duplicates()
        .sort_values()
    )

    dates = sorted(
        random.sample(
            list(trading_dates),
            250
        )
    )

    isins = [
        "US11135F1012",
        "US24703L2025",
        "US67066G1040"
    ]

    holdings = dict.fromkeys(isins, 0)
    trades = []

    for date in dates:
        isin = random.choice(isins)
        trade_type = random.choice(["buy", "sell"])

        if trade_type == "sell" and holdings[isin] == 0:
            trade_type = "buy"

        if trade_type == "buy":
            amount = random.randint(1, 100)
            holdings[isin] += amount
        else:
            amount = random.randint(1, min(holdings[isin], 100))
            holdings[isin] -= amount

        trades.append({
            "date": date,
            "isin": isin,
            "amount": amount,
            "type": trade_type
        })

    return pd.DataFrame(trades)


# 6. 计算历史组合收益率
# 计算历史组合收益率（观察窗口设定为 250 天）
def get_historical_portfolio_returns(trades, target_date, observation_period=250):
    weights = get_portfolio_weights_at_target_date(trades, target_date)

    # 如果今天没有任何持仓，跳过
    if weights.empty:
        return pd.DataFrame(columns=["date", "dailyreturns"])

    weights = weights[["isin", "weight"]]

    # 找出 target_date 之前的历史交易日
    past_prices = prices[prices["date"] < target_date]
    unique_dates = past_prices["date"].drop_duplicates().sort_values()

    # 严谨校验：如果过去的数据不够 250 个交易日，不凑合计算，直接返回空
    if len(unique_dates) < observation_period:
        return pd.DataFrame(columns=["date", "dailyreturns"])

    # 截取最近的 250 个交易日
    last_250_dates = unique_dates.iloc[-observation_period:]

    # 提取这 250 天的价格数据并匹配权重
    historical_prices = prices[prices["date"].isin(last_250_dates)].copy()
    historical_prices = historical_prices.merge(weights, on="isin", how="inner")

    # 计算 250 天内组合的加权每日收益率
    historical_prices["dailyreturns"] = (
        historical_prices["dailyreturns"] * historical_prices["weight"]
    )

    return (
        historical_prices
        .groupby("date")["dailyreturns"]
        .sum()
        .reset_index()
    )
