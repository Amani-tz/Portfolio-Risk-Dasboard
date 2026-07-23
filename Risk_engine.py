import pandas as pd
import yfinance as yf
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Read holdings and clean up any empty rows
portfolio_df = pd.read_excel('Portfolio_Risk_Tracker.xlsx', sheet_name='Holdings')
portfolio_df = portfolio_df.dropna(subset=['Ticker', 'Quantity']) # Removes blank rows

# yfinance automatically sorts tickers alphabetically. 
# Sort our Excel data alphabetically too so the quantities line up with the prices
portfolio_df = portfolio_df.sort_values(by='Ticker')

tickers = portfolio_df['Ticker'].tolist()
quantities = portfolio_df['Quantity'].values

# Download historical data
historical_data = yf.download(tickers, period="5y")['Close']

# Clean the downloaded data
historical_data = historical_data.ffill().dropna()

if isinstance(historical_data, pd.Series):
    historical_data = historical_data.to_frame()

# Calculate latest portfolio market value
latest_prices = historical_data.iloc[-1].values 

print("\n--- Diagnostic Check ---")
print(f"Tickers (Alphabetical): {tickers}")
print(f"Quantities: {quantities}")
print(f"Latest Prices: {latest_prices}")

position_values = quantities * latest_prices
total_portfolio_value = np.sum(position_values)
weights = position_values / total_portfolio_value

print(f"\nTotal Portfolio Value: ${total_portfolio_value:,.2f}")

# Calculate Daily Percentage Returns
daily_returns = historical_data.pct_change().dropna()
print("\n--- Daily Returns (Last 5 Days) ---")
print(daily_returns.tail())

# ALTERNATIVE DATA (NEWS SENTIMENT) 
# We run this BEFORE the Monte Carlo so we can use the score in our math
nltk.download('vader_lexicon', quiet=True)

print("\nFetching Live News Sentiment...")
sia = SentimentIntensityAnalyzer()
total_sentiment = 0

for ticker in tickers:
    stock = yf.Ticker(ticker)
    news = stock.news
    
    ticker_sentiment = 0
    valid_articles = 0 # Track how many articles actually have text
    
    if news:
        # Loop through the recent articles for this stock
        for article in news:
            # Safely try to get the title
            title = article.get('title', '')
            
            # Only calculate sentiment if a title was actually found
            if title:
                score = sia.polarity_scores(title)['compound']
                ticker_sentiment += score
                valid_articles += 1
            
        # Average the sentiment across the VALID articles for this ticker
        if valid_articles > 0:
            ticker_sentiment = ticker_sentiment / valid_articles
        
    print(f"  {ticker} Sentiment Score: {ticker_sentiment:+.2f}")
    total_sentiment += ticker_sentiment

# Calculate the average sentiment for the entire portfolio
portfolio_sentiment = total_sentiment / len(tickers) if len(tickers) > 0 else 0
print(f"\nOverall Portfolio Sentiment: {portfolio_sentiment:+.2f} (Scale: -1.0 to +1.0)")

# Monte Carlo Simulation for 1-Week VaR
print("\nRunning Monte Carlo Simulation (10,000 iterations)...")

portfolio_daily_returns = daily_returns.dot(weights)

# Find the historical average return (mu) and the volatility/standard deviation (sigma)
historical_mu = portfolio_daily_returns.mean()
historical_sigma = portfolio_daily_returns.std()

# Adjust parameters based on sentiment. 
# A negative sentiment score will lower mu and increase sigma.
sentiment_adjustment = portfolio_sentiment / 10 

mu = historical_mu + sentiment_adjustment
sigma = historical_sigma * (1 - sentiment_adjustment)

print(f"Historical Daily Volatility: {historical_sigma:.4f}")
print(f"News-Adjusted Volatility:    {sigma:.4f}")

# Set up the simulation parameters
simulations = 10000  # Number of simulations to run
days = 5  # 1-week horizon (5 trading days)

# Generate random future returns
simulated_returns = np.random.normal(mu, sigma, (simulations, days))
cumulative_returns = np.prod(1 + simulated_returns, axis=1) - 1
simulated_portfolio_values = total_portfolio_value * (1 + cumulative_returns)


# Calculate VaR and Expected Shortfall (ES) at 99% confidence ---
confidence_level = 0.01
sorted_values = np.sort(simulated_portfolio_values)

# Find the threshold for the bottom 1%
var_index = int(simulations * confidence_level)
var_value = sorted_values[var_index]
var_dollar_loss = total_portfolio_value - var_value

# Expected Shortfall
expected_shortfall_value = np.mean(sorted_values[:var_index])
es_dollar_loss = total_portfolio_value - expected_shortfall_value

print("\n--- 1-Week Risk Metrics (99% Confidence) ---")
print(f"Value at Risk (VaR): ${var_dollar_loss:,.2f}")
print(f"Expected Shortfall (ES): ${es_dollar_loss:,.2f}")
# --- PHASE 5: EXPORT FOR POWER BI ---
print("\nExporting data for Power BI...")

# Export the High-Level Risk Metrics
summary_data = {
    'Metric': ['Total Portfolio Value', '1-Week VaR (99%)', 'Expected Shortfall', 'Average Sentiment'],
    'Value': [total_portfolio_value, var_dollar_loss, es_dollar_loss, portfolio_sentiment]
}
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('Risk_Summary.csv', index=False)

# Export the 10,000 Monte Carlo Outcomes (for a Histogram)
sim_df = pd.DataFrame(simulated_portfolio_values, columns=['Simulated_Portfolio_Value'])
sim_df.to_csv('Monte_Carlo_Simulations.csv', index=False)

print("Export Complete! Check your project folder for the two new CSV files.")