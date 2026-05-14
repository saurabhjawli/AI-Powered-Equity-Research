import pandas as pd

def calculate_roe(financials, balance_sheet):
    """Return on Equity = Net Income / Total Equity"""
    try:
        net_income = financials.loc['Net Income'].iloc[0]
        equity = balance_sheet.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in balance_sheet.index else balance_sheet.loc['Total Equity Gross Minority Interest'].iloc[0]
        return (net_income / equity) * 100
    except:
        return None

def calculate_roce(financials, balance_sheet):
    """Return on Capital Employed = EBIT / Capital Employed"""
    try:
        ebit = financials.loc['EBIT'].iloc[0] if 'EBIT' in financials.index else financials.loc['Operating Income'].iloc[0]
        total_assets = balance_sheet.loc['Total Assets'].iloc[0]
        current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0]
        capital_employed = total_assets - current_liabilities
        return (ebit / capital_employed) * 100
    except:
        return None

def calculate_ebitda_margin(financials):
    """EBITDA Margin = EBITDA / Total Revenue"""
    try:
        ebitda = financials.loc['EBITDA'].iloc[0] if 'EBITDA' in financials.index else (financials.loc['EBIT'].iloc[0] + financials.loc['Reconciled Depreciation'].iloc[0])
        revenue = financials.loc['Total Revenue'].iloc[0]
        return (ebitda / revenue) * 100
    except:
        return None

def calculate_debt_to_equity(balance_sheet):
    """Debt to Equity = Total Debt / Total Equity"""
    try:
        debt = balance_sheet.loc['Total Debt'].iloc[0]
        equity = balance_sheet.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in balance_sheet.index else balance_sheet.loc['Total Equity Gross Minority Interest'].iloc[0]
        return debt / equity
    except:
        return None

def calculate_eps_growth(financials, info):
    """Basic EPS Growth (Current Year vs Previous Year)"""
    try:
        shares = info.get('sharesOutstanding', 1)
        if not shares or shares == 0: return None
        net_income_current = financials.loc['Net Income'].iloc[0]
        net_income_prev = financials.loc['Net Income'].iloc[1]
        
        eps_curr = net_income_current / shares
        eps_prev = net_income_prev / shares
        
        return ((eps_curr - eps_prev) / abs(eps_prev)) * 100
    except:
        return None

def get_all_metrics(financials, balance_sheet, info):
    """Returns a dictionary of all calculated metrics"""
    if financials is None or balance_sheet is None or financials.empty or balance_sheet.empty:
        return {}
        
    return {
        "ROE (%)": calculate_roe(financials, balance_sheet),
        "ROCE (%)": calculate_roce(financials, balance_sheet),
        "EBITDA Margin (%)": calculate_ebitda_margin(financials),
        "Debt to Equity": calculate_debt_to_equity(balance_sheet),
        "EPS Growth YoY (%)": calculate_eps_growth(financials, info)
    }
