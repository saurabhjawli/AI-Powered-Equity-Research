import pandas as pd

def calculate_dcf_valuation(financials, cashflow, info, growth_rate=0.10):
    """Robust DCF model. Hardcoded WACC=9% and Terminal=2.5% to simplify UI."""
    discount_rate = 0.09
    terminal_growth = 0.025
    
    try:
        cf_data = cashflow() if callable(cashflow) else cashflow
        
        recent_fcf = 0
        if cf_data is not None and not cf_data.empty:
            possible_fcf_names = ['Free Cash Flow', 'FreeCashFlow', 'Total Cash From Operating Activities']
            for name in possible_fcf_names:
                if name in cf_data.index:
                    recent_fcf = cf_data.loc[name].iloc[0]
                    break
        
        if recent_fcf == 0 and financials is not None and not financials.empty and 'Net Income' in financials.index:
            recent_fcf = financials.loc['Net Income'].iloc[0]

        if not recent_fcf or pd.isna(recent_fcf) or recent_fcf <= 0:
            return None # DCF fails for negative cash flows

        projected_fcfs = []
        for i in range(1, 6):
            fcf = recent_fcf * ((1 + growth_rate) ** i)
            projected_fcfs.append(fcf / ((1 + discount_rate) ** i))

        terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 5)

        enterprise_value = sum(projected_fcfs) + discounted_terminal_value
        cash = info.get('totalCash', 0)
        debt = info.get('totalDebt', 0)
        equity_value = enterprise_value + cash - debt
        
        shares = info.get('sharesOutstanding', 1)
        if not shares or shares == 0: return None
        
        intrinsic_value = equity_value / shares
        return intrinsic_value if intrinsic_value > 0 else None

    except Exception:
        return None

def calculate_hybrid_valuation(info, intrinsic_val, avg_pe_5y, avg_pe_10y, expected_pe=None):
    """Combines DCF and Historical Multiples to find a balanced Fair Value."""
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
    eps = info.get('trailingEps', 0)
    
    # Use override if provided, else prefer 10y avg if available, otherwise 5y
    if expected_pe and expected_pe > 0:
        target_pe = expected_pe
    else:
        target_pe = avg_pe_10y if avg_pe_10y else avg_pe_5y
    
    pe_target_price = eps * target_pe if target_pe and eps > 0 else 0
    
    if intrinsic_val and pe_target_price > 0:
        fair_value = (intrinsic_val + pe_target_price) / 2
    elif intrinsic_val:
        fair_value = intrinsic_val
    elif pe_target_price > 0:
        fair_value = pe_target_price
    else:
        fair_value = None
        
    if not fair_value or current_price == 0:
        return None, 0, "N/A", "Insufficient data. The company might have negative earnings or cash flow."

    upside = ((fair_value - current_price) / current_price) * 100
    
    # Reasoning Logic
    is_undervalued = fair_value > current_price
    is_deep_value = fair_value > (current_price * 1.15) # 15% margin of safety
    is_overvalued = fair_value < (current_price * 0.85)

    if is_deep_value:
        rec = "BUY"
        reason = "The stock's fair value is significantly higher than its current market price based on historical and cash flow metrics."
    elif is_overvalued:
        rec = "SELL"
        reason = "The stock is trading at a premium compared to its historical averages and projected cash flows."
    elif is_undervalued:
        rec = "HOLD / ACCUMULATE"
        reason = "The stock is slightly undervalued, offering a moderate upside but lacking a strong margin of safety."
    else:
        rec = "HOLD / FAIRLY VALUED"
        reason = "The current market price closely aligns with the estimated fair value."
        
    return fair_value, upside, rec, reason
