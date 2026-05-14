# AI-Powered Equity Research Platform

An advanced, interactive Streamlit dashboard designed to provide institutional-grade equity research, valuation, and AI-driven insights for public stocks.

## 🚀 Features

- **Hybrid Valuation Engine**: Combines Intrinsic Value (Discounted Cash Flow) and Relative Value (Historical P/E Multiples) to generate a robust Fair Value estimate.
- **Financial Metrics Engine**: Automatically calculates ROE, ROCE, EBITDA Margins, Debt-to-Equity, and EPS Growth.
- **AI Executive Summary**: Integrates with the Gemini API to read the company's business summary, valuation metrics, and generate a professional research summary.
- **Auto-Detected Peer Comparison**: Uses AI to automatically identify competitors and compares their key valuation metrics in a clean table.
- **Interactive Visualizations**: 1-Year price trends and historical revenue/profit bar charts using Plotly.

## 🛠️ Installation

1. **Clone or Download** the repository.
2. **Install Dependencies**: Ensure you have Python 3.8+ installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
3. *(Optional)* **Get a Gemini API Key**: To use the AI Summary and Auto-Peer Detection features, you will need a free API key from [Google AI Studio](https://aistudio.google.com/).

## 🖥️ Usage

Start the Streamlit application by running the following command in your terminal:

```bash
streamlit run app.py
```

### Dashboard Guide

1. **Search**: Enter any valid Yahoo Finance ticker symbol in the sidebar (e.g., `AAPL` for Apple, `INFY.NS` for Infosys).
2. **AI Features**: Paste your Gemini API key into the secure sidebar input to unlock the "AI Summary" and "Peer Comparison" tabs.
3. **Advanced Settings**: Adjust the "Expected Growth Rate" slider to see how it dynamically affects the DCF Intrinsic Value and the final recommendation.
4. **Analysis Tabs**:
   - **Overview & Metrics**: See the investment thesis and core financial ratios.
   - **Charts**: View historical price action and fundamental growth.
   - **Peer Comparison**: Compare the stock against its 4 closest competitors.
   - **AI Summary**: Read a generated 3-paragraph executive brief.

## 📁 Project Structure

- `app.py`: The main Streamlit dashboard application.
- `utils/data_fetch.py`: Handles all interactions with the `yfinance` API (prices, financials).
- `utils/valuation.py`: Contains the math for the DCF model and Hybrid recommendation logic.
- `utils/metrics.py`: Parses balance sheets and income statements to calculate core ratios.
- `utils/ai_summary.py`: Manages the prompt engineering and API calls to Google's Gemini models.
