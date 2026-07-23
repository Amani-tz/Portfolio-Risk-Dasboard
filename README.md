# Portfolio-Risk-Dasboard
An end-to-end quantitative portfolio risk engine that integrates Excel, Python, and Power BI to calculate 1-week Monte Carlo Value at Risk (VaR) and Expected Shortfall (ES), dynamically adjusted by real-time NLP sentiment analysis of financial news.
A quantitative risk management tool that calculates your portfolio's 1-week Value at Risk (VaR) and Expected Shortfall (ES) using 10,000 Monte Carlo simulations, dynamically adjusted by real-time financial news sentiment.

You input your holdings in Excel, Python runs the data pipeline and financial math, and Power BI displays the interactive dashboard.

How It Works
Reads Your Portfolio: Grabs your stock, ETF, and bond share counts directly from an Excel sheet.

Pulls Market Data & News: Downloads 5 years of daily price history from Yahoo Finance and scrapes current news headlines for each ticker.

Analyzes Sentiment: Uses Natural Language Processing (NLTK VADER) to score current news headlines from -1.0 (negative) to +1.0 (positive). Negative news automatically increases the simulated volatility of your portfolio.

Simulates 10,000 Futures: Runs a Monte Carlo simulation to project 10,000 potential 5-day performance paths based on historical returns and current market sentiment.

Exports to Power BI: Outputs the final risk metrics and distribution curves into clean CSV files for instant visualization.

Tech Stack
Language: Python 3

Libraries: pandas, numpy, yfinance, nltk, openpyxl

Visualization & Input: Microsoft Power BI, Microsoft Excel
