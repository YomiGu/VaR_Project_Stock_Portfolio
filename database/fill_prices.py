from common import avgo, dell, nvda

import numpy as np
import pandas as pd


def clean_data_frame(data_frame):
    """
    Clean raw stock price data.

    Steps:
    1. Remove columns that are not needed.
    2. Rename columns to English names.
    3. Convert date to datetime.
    4. Convert close price to numeric.
    """

    # 1. Remove unnecessary columns
    data_frame = data_frame.drop(
        columns=["Erster", "Hoch", "Tief", "Stuecke", "Volumen"]
    )

    # 2. Rename columns
    data_frame = data_frame.rename(
        columns={
            "Schlusskurs": "close",
            "Datum": "date"
        }
    )

    # 3. Convert date
    data_frame["date"] = pd.to_datetime(data_frame["date"])

    # 4. Convert European decimal comma to decimal point
    data_frame["close"] = (
        data_frame["close"]
        .str.replace(",", ".", regex=False)
    )

    # 5. Convert close price to numeric
    data_frame["close"] = pd.to_numeric(data_frame["close"])

    return data_frame


def add_stock_identifier(data_frame, stock_identifier):
    

    data_frame = data_frame.copy()
    data_frame["isin"] = stock_identifier

    return data_frame


def get_continuous_daily_returns(data_frame, close_column_name="close"):


    data_frame = data_frame.sort_values(
        "date",
        ascending=False
    ).copy()

    data_frame["dailyreturns"] = (
        -np.log(data_frame[close_column_name]).diff()
    )

    return data_frame




avgo = clean_data_frame(avgo)

avgo = get_continuous_daily_returns(avgo)

avgo = add_stock_identifier(
    avgo,
    "US11135F1012"
)


dell = clean_data_frame(dell)

dell = get_continuous_daily_returns(dell)

dell = add_stock_identifier(
    dell ,
    "US24703L2025"
)




nvda = clean_data_frame(nvda)

nvda = get_continuous_daily_returns(nvda)

nvda = add_stock_identifier(
    nvda,
    "US67066G1040"
)

# Store all cleaned stock data frames in one dictionary
stocks = {
    "Broadcom": avgo,
    "Dell": dell,
    "NVIDIA": nvda
}


# Check cleaned data
for stock_name, data_frame in stocks.items():

    print(f"\n{stock_name}:")
    print(data_frame.head())

    print(f"\n{stock_name} data types:")
    print(data_frame.dtypes)

    print(f"\n{stock_name} missing values:")
    print(data_frame.isna().sum())

    print(f"\n{stock_name} first and last date:")
    print(data_frame["date"].iloc[0])
    print(data_frame["date"].iloc[-1])

    print(f"\n{stock_name} duplicate dates:")
    print(data_frame["date"].duplicated().sum())


# Save cleaned data
avgo.to_csv("data/avgo_clean.csv", index=False)
dell.to_csv("data/dell_clean.csv", index=False)
nvda.to_csv("data/nvda_clean.csv", index=False)

print("\nCleaned data saved successfully.")