import yfinance as yf  
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Scrape the Yahoo Finance Table

# Function to fetch stock price using yfinance
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    try:
        stock_info = stock.info
        price = stock_info.get('currentPrice')
        return price
    except ValueError as e:
        print(f"Error retrieving info for {ticker}: {e}")
        return None

def process_earnings_table(table, ticker_data_list=[]):
    """
    Process a single earnings table to extract ticker symbols, 
    fetch stock prices, and get earnings release dates.
    """

    if table == None:
        return ticker_data_list

    df = pd.read_html(str(table))[0]
    
    if 'Symbol' in df.columns:
        # Assuming the release date column is named 'Release Date'
        for _, row in df.iterrows():
            ticker = row.get('Symbol')
            if pd.notna(ticker):
                price = get_stock_price(ticker)
                ticker_data_list.append(pd.DataFrame({'Symbol': [ticker], 'Stock Price': [price]}))

    return ticker_data_list

def extract_table(url):
    
    # Scrape data from Yahoo Finance
    
    headers = {'user-agent': 'Mozilla/5.0'}
    try:
        # Send the GET request
        response = requests.get(url, headers=headers)
        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables in the webpage
        table = soup.find_all('table')
        
        # Check if there are any tables found
        if not table:
            return None
        
        # Further processing or return the tables
        return table

    except requests.RequestException as e:
        return None

def convert_to_dataframe(ticker_data_list, ticker_data_sorted=pd.DataFrame()):

    # Concatenate all DataFrame objects into one DataFrame
    ticker_data = pd.concat(ticker_data_list, ignore_index=True)

    # Clean and sort the data
    ticker_data = ticker_data.dropna(subset=['Stock Price'])
    ticker_data_sorted = ticker_data.sort_values(by='Stock Price', ascending=False)

    return ticker_data_sorted
