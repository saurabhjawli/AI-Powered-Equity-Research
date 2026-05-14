import google.generativeai as genai

def get_best_model_name():
    """Dynamically finds the best available Gemini model for the user's API key."""
    fallback_model = 'gemini-1.5-flash'
    try:
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1. Try to find the ideal 1.5 flash model
        for m in models:
            if 'gemini-1.5-flash' in m.name:
                return m.name
                
        # 2. Fallback to any 1.5 model
        for m in models:
            if 'gemini-1.5' in m.name:
                return m.name
                
        # 3. Fallback to any gemini model
        for m in models:
            if 'gemini' in m.name:
                return m.name
                
        return fallback_model
    except:
        return fallback_model

def generate_ai_summary(ticker, info, metrics, fair_value, rec, api_key):
    if not api_key:
        return "Please provide a Gemini API Key in the sidebar to generate an AI summary."
    
    try:
        genai.configure(api_key=api_key)
        model_name = get_best_model_name()
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Act as a professional equity research analyst. Write a concise 3-paragraph executive summary for {ticker} ({info.get('longName', 'Unknown')}).
        
        Use the following data:
        - Current Price: {info.get('currentPrice', 'N/A')}
        - Fair Value Estimate: {fair_value}
        - Our Recommendation: {rec}
        - ROE: {metrics.get('ROE (%)', 'N/A')}
        - EBITDA Margin: {metrics.get('EBITDA Margin (%)', 'N/A')}
        - Sector: {info.get('sector', 'N/A')}
        
        Also, pull in any general knowledge you have about this company's recent performance or market position.
        
        Structure:
        1. Business Overview & Market Position
        2. Financial Health & Valuation Analysis
        3. Final Verdict (Why it's a {rec})
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def get_peers_via_ai(ticker, summary, api_key):
    if not api_key:
        # Fallback manual list for demonstration if no key
        fallbacks = {
            'AAPL': ['MSFT', 'GOOGL', 'META'],
            'MSFT': ['AAPL', 'GOOGL', 'AMZN'],
            'GOOGL': ['MSFT', 'META', 'AMZN'],
            'NVDA': ['AMD', 'INTC', 'TSM'],
            'INFY.NS': ['TCS.NS', 'WIPRO.NS', 'HCLTECH.NS']
        }
        return fallbacks.get(ticker.upper(), [])
        
    try:
        genai.configure(api_key=api_key)
        model_name = get_best_model_name()
        model = genai.GenerativeModel(model_name)
        
        prompt = f"Given the company {ticker} with this business summary: '{summary[:500]}...', list exactly 3 to 4 publicly traded competitor ticker symbols (and nothing else, just the symbols separated by commas). Ensure they are valid Yahoo Finance tickers."
        response = model.generate_content(prompt)
        text = response.text.strip()
        tickers = [t.strip().upper() for t in text.replace('\n', ',').split(',')]
        return [t for t in tickers if t and len(t) < 10][:4]
    except:
        return []
