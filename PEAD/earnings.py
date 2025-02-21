import yfinance as yf
import pandas as pd
from typing import Tuple

# Py docs stuff for functions?
def calculate_sue(ticker: yf.ticker.Ticker):
    def get_earnings_info(): 
        earnings_df = ticker.get_earnings_dates(limit=13)
        earnings_df = earnings_df.dropna().iloc[1:]
        print(earnings_df)

        latest_actual_earnings = earnings_df.iat[0,1]
        latest_earning_estimate = earnings_df.iat[0,0]
        std_dev = earnings_df["Reported EPS"].std()

        return (latest_actual_earnings, latest_earning_estimate, std_dev)

    # std_of_earnings refers to std of last 8 quarter of reported ep
    earnings_info = get_earnings_info()
    actual_earnings = earnings_info[0]
    estimated_earnings = earnings_info[1]
    std_of_earnings = earnings_info[2]

    return (actual_earnings - estimated_earnings) / std_of_earnings

def get_earnings_interval(ticker: yf.ticker.Ticker):
    latest_earnings_date = ticker.get_earnings_dates().dropna().index[0]
    day_before = latest_earnings_date - pd.Timedelta(days=1)
    day_after = latest_earnings_date + pd.Timedelta(days=1)

    return (day_before, day_after)


def get_interval_return(ticker: yf.ticker.Ticker, interval: Tuple[pd.Timedelta, pd.Timedelta]):
    
    earnings_df = ticker.history(start=interval[0], end=interval[1] + pd.Timedelta(days=2)).loc[:, ['Open']]
    earnings_df["return"] = earnings_df.pct_change() + 1
    return earnings_df["return"].prod()

# Only comparing to spy for now, not woryying about French and Fama
def calculate_ear(ticker: yf.ticker.Ticker):
    equity_earnings_interval = get_earnings_interval(ticker)
    equity_return = get_interval_return(ticker, equity_earnings_interval)
    benchmark_return = get_interval_return(yf.Ticker("SPY"), equity_earnings_interval)

    print(equity_return, benchmark_return)
    return equity_return - benchmark_return







if __name__ == "__main__":
    # sue = calculate_sue('MSFT')
    # print(sue)
    # multiplier(-1, 5)
    ticker = yf.Ticker("BMBL")
    e = calculate_ear(ticker)
    print(e)
    # print(ticker.history(period="10y"))
