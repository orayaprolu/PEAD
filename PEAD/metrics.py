import yfinance as yf
import pandas as pd
from typing import Tuple

def date_to_quarter(): 
    return 0

# Only works for companies that have already released latest earnings !
def calculate_ear(ticker: str, benchmark_ticker: str, earnings_date: pd.Timestamp) -> float:

    # Get day before and after earnings
    def get_earnings_interval():
        day_before = earnings_date - pd.Timedelta(days=1)
        day_after = earnings_date + pd.Timedelta(days=1)

        return (day_before, day_after)

    # Get returns from day before earnings to day after earnings
    def get_interval_return(i_ticker: yf.ticker.Ticker, interval: Tuple[pd.Timedelta, pd.Timedelta]):  
        earnings_df = i_ticker.history(start=interval[0], end=interval[1] + pd.Timedelta(days=2)).loc[:, ['Open']]
        earnings_df["return"] = earnings_df.pct_change() + 1
        return earnings_df["return"].prod()
    
    equity_earnings_interval = get_earnings_interval()
    equity_return = get_interval_return(yf.Ticker(ticker), equity_earnings_interval)
    benchmark_return = get_interval_return(yf.Ticker(benchmark_ticker), equity_earnings_interval)

    return equity_return - benchmark_return

# Only works for companies that have already released latest earnings !
def calculate_sue(ticker: str, earnings_date: pd.Timestamp) -> float:
    def get_earnings_info(): 
        earnings_df = yf.Ticker(ticker).get_earnings_dates(limit=1000).loc[earnings_date:]
        earnings_df = earnings_df[:8]

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

def find_earnings_date(ticker: str, year: int, quarter: int) -> pd.Timestamp:

    earnings_seasons = {
        1: (f"{year}-04-01", f"{year}-05-25"),  # Q1 (Reports in Apr-May)
        2: (f"{year}-07-01", f"{year}-08-25"),  # Q2 (Reports in Jul-Aug)
        3: (f"{year}-10-01", f"{year}-11-25"),  # Q3 (Reports in Oct-Nov)
        4: (f"{year+1}-01-01", f"{year+1}-02-25"),  # Q4 (Reports in Jan-Feb of next year)
    }
    # Convert to timezone-aware timestamps
    tz = "America/New_York"  # Ensure consistency with DataFrame index
    start_date = pd.Timestamp(earnings_seasons[quarter][0], tz=tz)
    end_date = pd.Timestamp(earnings_seasons[quarter][1], tz=tz)

    df = yf.Ticker(ticker).get_earnings_dates(limit=1000).dropna()
    ret = df.loc[(df.index >= start_date) & (df.index <= end_date)].index
    return ret.



if __name__ == "__main__":
    ticker = "MSFT"
    ed = find_earnings_date(ticker, 2024, 1)
    print(ed)

    # ear = calculate_ear(ticker, "SPY", ed)
    # sue = calculate_sue(ticker, ed)
    # print(ear, sue)
