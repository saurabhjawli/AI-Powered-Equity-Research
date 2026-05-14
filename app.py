import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetch import get_stock_info, get_financials, get_cashflow, get_historical_pe_averages, get_stock_history, get_balance_sheet
from utils.valuation import calculate_dcf_valuation, calculate_hybrid_valuation
from utils.metrics import get_all_metrics
from utils.ai_summary import generate_ai_summary, get_peers_via_ai

st.set_page_config(page_title="Equity Research", page_icon="📈", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    div.stButton > button { width: 100%; background-color: #2ea043; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🔍 Search & Settings")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper()
api_key = st.sidebar.text_input("Gemini API Key (Optional)", type="password", help="Required for AI Summaries & Peer Detection")

with st.sidebar.expander("⚙️ Advanced Settings"):
    growth_input = st.slider("Expected Growth Rate (%)", 0, 100, 10) / 100
    expected_pe_input = st.number_input("Target P/E Ratio Override", min_value=0.0, value=0.0, step=1.0, help="Leave at 0.0 to auto-use historical averages.")

analyze_btn = st.sidebar.button("Run Full Analysis")

st.title("📈 AI-Powered Equity Research")

if analyze_btn or ticker:
    try:
        with st.spinner(f"Fetching and analyzing data for {ticker}..."):
            info = get_stock_info(ticker)
            if not info:
                st.error(f"Error: Could not retrieve data for ticker '{ticker}'. Please check the symbol and try again.")
                st.stop()
                
            financials = get_financials(ticker)
            balance_sheet = get_balance_sheet(ticker)
            cashflow_data = get_cashflow(ticker)
            history = get_stock_history(ticker, "4y")
            pe_result = get_historical_pe_averages(ticker)
            avg_5y, avg_10y, pe_history = pe_result if len(pe_result) == 3 else (None, None, {})
            
            metrics = get_all_metrics(financials, balance_sheet, info)
            
            intrinsic_val = calculate_dcf_valuation(financials, cashflow_data, info, growth_rate=growth_input)
            fair_value, upside, rec, reason = calculate_hybrid_valuation(info, intrinsic_val, avg_5y, avg_10y, expected_pe=expected_pe_input)
            
            # --- UI OUTPUT ---
            st.markdown(f"### {info.get('longName', ticker)}")
            currency = info.get('currency', '$')
            
            res_col1, res_col2, res_col3, res_col4 = st.columns(4)
            with res_col1:
                price_str = f"{info.get('currentPrice', 0):,}" if isinstance(info.get('currentPrice'), (int, float)) else "N/A"
                st.metric("Current Market Price", f"{currency} {price_str}")
            with res_col2:
                fv_str = f"{fair_value:,.2f}" if isinstance(fair_value, (int, float)) else "N/A"
                st.metric("Estimated Fair Value", f"{currency} {fv_str}")
            with res_col3:
                up_str = f"{upside:.1f}%" if isinstance(upside, (int, float)) else "N/A"
                st.metric("Expected Upside", up_str, delta=up_str if up_str != "N/A" else None)
            with res_col4:
                st.metric("Recommendation", rec)

            st.divider()

            # TABS for organization
            tab1, tab2, tab3, tab4 = st.tabs(["Overview & Metrics", "Charts", "Peer Comparison", "AI Summary"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("💡 Investment Thesis")
                    st.write(reason)
                    st.write("**Historical P/E Comparison**")
                    current_pe = info.get('trailingPE', 0)
                    st.write(f"- Current P/E: {current_pe:.1f}" if isinstance(current_pe, (int, float)) else "- Current P/E: N/A")
                    st.write(f"- 5-Year Avg P/E: {avg_5y:.1f}" if avg_5y else "- 5-Year Avg P/E: N/A")
                    st.write(f"- 10-Year Avg P/E: {avg_10y:.1f}" if avg_10y else "- 10-Year Avg P/E: N/A")
                
                with col2:
                    st.subheader("⚙️ Key Financial Metrics")
                    for k, v in metrics.items():
                        st.write(f"- **{k}:** {v:.2f}" if isinstance(v, (int, float)) else f"- **{k}:** N/A")

            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📈 4-Year Price Trend")
                    if history is not None and not history.empty:
                        fig1 = go.Figure()
                        fig1.add_trace(go.Scatter(x=history.index, y=history['Close'], mode='lines', line=dict(color='#00d1b2')))
                        fig1.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), template="plotly_dark")
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.warning("Price history not available.")
                        
                    st.subheader("📉 Historical P/E Trend")
                    if pe_history:
                        pe_df = pd.DataFrame(list(pe_history.items()), columns=['Date', 'P/E']).sort_values('Date')
                        fig_pe = go.Figure()
                        fig_pe.add_trace(go.Scatter(x=pe_df['Date'], y=pe_df['P/E'], mode='lines', line=dict(color='#ff9f43')))
                        fig_pe.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), template="plotly_dark")
                        st.plotly_chart(fig_pe, use_container_width=True)
                    else:
                        st.warning("Historical P/E data not available.")
                        
                with c2:
                    st.subheader("📊 Annual Performance (Last 4 Years)")
                    if financials is not None and not financials.empty:
                        plot_df = financials.iloc[:, :4].T.sort_index()
                        fig2 = go.Figure()
                        if 'Total Revenue' in plot_df.columns:
                            fig2.add_trace(go.Bar(x=plot_df.index.strftime('%Y'), y=plot_df['Total Revenue'], name='Revenue', marker_color='#1f77b4'))
                        if 'Net Income' in plot_df.columns:
                            fig2.add_trace(go.Bar(x=plot_df.index.strftime('%Y'), y=plot_df['Net Income'], name='Net Income', marker_color='#2ca02c'))
                        fig2.update_layout(barmode='group', height=400, margin=dict(l=0, r=0, t=30, b=0), template="plotly_dark")
                        st.plotly_chart(fig2, use_container_width=True)

            with tab3:
                st.subheader("🏢 Auto-Detected Peer Comparison")
                peers = get_peers_via_ai(ticker, info.get('longBusinessSummary', ''), api_key)
                
                if not peers:
                    st.info("No peers detected. Enter a Gemini API Key to enable AI peer detection, or use a major US ticker for fallback defaults.")
                else:
                    peer_data = []
                    # Add current stock first
                    peer_data.append({
                        "Ticker": ticker,
                        "Price": info.get('currentPrice', 'N/A'),
                        "P/E Ratio": info.get('trailingPE', 'N/A'),
                        "Market Cap (B)": round(info.get('marketCap', 0)/1e9, 2) if info.get('marketCap') else 'N/A'
                    })
                    
                    with st.spinner("Fetching peer data..."):
                        for p in peers:
                            p_info = get_stock_info(p)
                            if p_info:
                                peer_data.append({
                                    "Ticker": p,
                                    "Price": p_info.get('currentPrice', 'N/A'),
                                    "P/E Ratio": p_info.get('trailingPE', 'N/A'),
                                    "Market Cap (B)": round(p_info.get('marketCap', 0)/1e9, 2) if p_info.get('marketCap') else 'N/A'
                                })
                    
                    st.dataframe(pd.DataFrame(peer_data), use_container_width=True)

            with tab4:
                st.subheader("🤖 AI Executive Summary")
                if not api_key:
                    st.warning("Please enter a Gemini API Key in the sidebar to generate an AI summary.")
                else:
                    with st.spinner("Generating AI analysis..."):
                        summary = generate_ai_summary(ticker, info, metrics, fair_value, rec, api_key)
                        st.markdown(summary)

    except Exception as e:
        import traceback
        st.error(f"An unexpected error occurred while analyzing {ticker}. Check the symbol or try again.")
        with st.expander("View Error Details"):
            st.text(traceback.format_exc())
