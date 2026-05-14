import yfinance as yf
import pandas as pd 
import numpy as np

def get_stock_info(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if not info or ('regularMarketPrice' not in info and 'currentPrice' not in info):
            return None # Invalid ticker or no data
        return info
    except:
        return None

def get_financials(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.financials
    except:
        return None

def get_balance_sheet(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.balance_sheet
    except:
        return None

def get_cashflow(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.get_cashflow()
    except:
        return None

def get_stock_history(ticker_symbol, period="1y"):
    """Fetch historical price data"""
    try:
        stock = yf.Ticker(ticker_symbol)
        return stock.history(period=period)
    except:
        return None

def get_historical_pe_averages(ticker_symbol):
    """
    Calculates 5-year and 10-year average P/E ratios based on available data.
    Attempts to fetch 10 years of price data.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        financials = stock.financials
        
        if financials is None or financials.empty or 'Net Income' not in financials.index:
            return None, None
            
        history = stock.history(period="10y", interval="1mo")
        shares = stock.info.get('sharesOutstanding')
        if not shares or shares == 0:
            return None, None
            
        pe_list = []
        pe_history = {}
        # Ensure we are going chronological (oldest to newest) or newest to oldest. 
        # financials columns are usually datetime, newest first.
        for date in financials.columns:
            year = date.year
            net_income = financials.loc['Net Income', date]
            
            # Skip if Net Income is negative or NaN
            if pd.isna(net_income) or net_income <= 0:
                continue
                
            eps = net_income / shares
            
            # Collect monthly PE for the chart
            year_data = history[history.index.year == year]
            for month_date, row in year_data.iterrows():
                if eps > 0:
                    pe_history[month_date.strftime('%Y-%m')] = row['Close'] / eps

            # Collect year-end PE for the averages
            price_date = f"{year}-12-31"
            if price_date in history.index:
                price = history.loc[price_date]['Close']
            else:
                if not year_data.empty:
                    price = year_data['Close'].iloc[-1]
                else:
                    continue
            
            if eps > 0:
                pe_val = price / eps
                pe_list.append(pe_val)

        if not pe_list:
            return None, None, {}
            
        # pe_list is from newest to oldest
        avg_5y = sum(pe_list[:5]) / len(pe_list[:5]) if len(pe_list) > 0 else None
        avg_10y = sum(pe_list) / len(pe_list) if len(pe_list) > 5 else avg_5y
        
        return avg_5y, avg_10y, pe_history
    except Exception:
        return None, None, {}
