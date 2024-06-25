import matplotlib.pyplot as plt
import yfinance as yf  
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
from scipy.interpolate import griddata
import matplotlib.ticker as mticker
import pandas as pd
from analyze_options import *
from analyze_stock import *

def plot_volatility_surface(options_data, ticker):
    try:
        # Extract data
        stock = yf.Ticker(ticker)
        current_price = stock.info.get('currentPrice', stock.info.get('previousClose', None))
        call_strike_prices = list(np.array(options_data['call_strike_prices'])/current_price)
        put_strike_prices = list(np.array(options_data['put_strike_prices'])/current_price)
        call_ivs = options_data['call_ivs']
        put_ivs = options_data['put_ivs']
        call_expirations = options_data['call_expirations']
        put_expirations = options_data['put_expirations']

        # Convert expiration dates to numerical format
        call_exp_nums = mdates.date2num(pd.to_datetime(call_expirations))
        put_exp_nums = mdates.date2num(pd.to_datetime(put_expirations))

        # Combine call and put data
        strikes = np.array(call_strike_prices + put_strike_prices)
        expirations = np.array(list(call_exp_nums) + list(put_exp_nums))
        ivs = np.array(call_ivs + put_ivs)

        # Check for sufficient variation in data
        if len(set(strikes)) < 2 or len(set(expirations)) < 2:
            print("Insufficient variation in strike prices or expiration dates for interpolation.")
            return

        # Check for NaNs or infinite values
        if np.isnan(ivs).any() or np.isinf(ivs).any():
            print("Data contains NaNs or infinite values.")
            return

        # Create a 2D grid of strikes and expirations
        strike_grid, exp_grid = np.meshgrid(
            np.linspace(strikes.min(), strikes.max(), 100),
            np.linspace(expirations.min(), expirations.max(), 100)
        )

        # Interpolate IV data over the grid
        ivs_grid = griddata((strikes, expirations), ivs, (strike_grid, exp_grid), method='cubic')

        # Plot the surface
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(strike_grid, exp_grid, ivs_grid, cmap='viridis', edgecolor='none')

        # Labels and title
        ax.set_title(f'Volatility Surface for {ticker}')
        ax.set_xlabel('Moneyness (Strike Price/Current Price)')
        ax.set_ylabel('Expiration Date')
        ax.set_zlabel('Implied Volatility')

        # Date formatting
        ax.yaxis.set_major_locator(mdates.AutoDateLocator())
        ax.yaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        ax.yaxis.set_tick_params(labelsize=9)
        for label in ax.yaxis.get_majorticklabels():
            label.set_rotation(45)

        # View adjustment
        ax.view_init(30, 210)
        colorbar = fig.colorbar(surf, shrink=0.5, aspect=30, pad=-0.025)
        plt.subplots_adjust(left=0.1, right=1.0, top=1.0, bottom=0.05)

        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")

def plot_iv_skew_otm_only(options_data, target_date, ticker, days_range=21):
    # Fetch the current stock price
    stock = yf.Ticker(ticker)
    current_price = stock.info.get('currentPrice', stock.info.get('previousClose', None))

    historical_volatility = calculate_historical_volatility(ticker)

    # Extract call and put strike prices and IVs
    call_strike_prices = options_data['call_strike_prices']
    put_strike_prices = options_data['put_strike_prices']
    call_ivs = options_data['call_ivs']
    put_ivs = options_data['put_ivs']
    call_expirations = options_data['call_expirations']
    put_expirations = options_data['put_expirations']

    # Convert expiration dates to datetime objects and filter by target date
    call_expirations_dt = [datetime.strptime(date, "%Y-%m-%d") for date in call_expirations]
    put_expirations_dt = [datetime.strptime(date, "%Y-%m-%d") for date in put_expirations]
    target_date_dt = np.datetime64(target_date)

    # Filter call data for OTM options
    filtered_call_data_otm = [(strike, iv, exp) for strike, iv, exp in zip(call_strike_prices, call_ivs, call_expirations_dt)
                              if exp > target_date_dt and exp <= target_date_dt + np.timedelta64(days_range, 'D') and strike > current_price]
    call_strikes_rel_otm, call_ivs_rel_otm = zip(*[(strike/current_price, iv) for strike, iv, _ in filtered_call_data_otm]) if filtered_call_data_otm else ([], [])

    # Filter put data for OTM options
    filtered_put_data_otm = [(strike, iv, exp) for strike, iv, exp in zip(put_strike_prices, put_ivs, put_expirations_dt)
                             if exp > target_date_dt and exp <= target_date_dt + np.timedelta64(days_range, 'D') and strike < current_price]
    put_strikes_rel_otm, put_ivs_rel_otm = zip(*[(strike/current_price, iv) for strike, iv, _ in filtered_put_data_otm]) if filtered_put_data_otm else ([], [])

    # Create plot for combined OTM skew
    fig, ax = plt.subplots(figsize=(15, 6))

    # Plot OTM call and put data
    ax.scatter(call_strikes_rel_otm, call_ivs_rel_otm, color='blue', marker='o', label='OTM Calls')
    ax.scatter(put_strikes_rel_otm, put_ivs_rel_otm, color='green', marker='o', label='OTM Puts')
    ax.axvline(1, color='grey', linestyle='--', label='Current Price')

    # Overlay historical volatility as a horizontal line
    ax.axhline(y=historical_volatility, color='purple', linestyle='--', label=f'Historical Volatility ({historical_volatility:.2%})')

    ax.set_title(f'OTM Options Implied Volatility Skew - {ticker}')
    ax.set_xlabel('Strike Price / Current Price')
    ax.set_ylabel('Implied Volatility')
    ax.legend(frameon=False)
    ax.grid(True)

    plt.tight_layout()
    plt.show()

# Function to plot the P/E ratio time series
def plot_pe_ratio(ticker_symbol, date):
    start_date = date - timedelta(days=365)  # Approximately 1 year back
    end_date = date  # Up to the current date

    hist = get_financial_ratios(ticker_symbol, start_date, end_date)

    if 'P/E' in hist.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist['P/E'], '-o', markersize=2, label='P/E')
        plt.title(f"P/E Ratio History of {ticker_symbol}")
        plt.xlabel('Date')
        plt.ylabel('P/E Ratio')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.show()
    
def stock_tracker(ticker_symbol, subplot_position):
    def get_todays_prices(ticker_symbol):
        try:
            ticker = yf.Ticker(ticker_symbol)
            todays_data = ticker.history(period='1d', interval='1m')
            return todays_data
        except Exception as e:
            print(f"Error fetching historical prices: {e}")
            return None

    todays_prices = get_todays_prices(ticker_symbol)
    times = [ts.strftime('%H:%M') for ts in todays_prices.index]
    
    plt.subplot(1, 2, subplot_position)
    plt.plot(times, todays_prices['Close'])
    plt.title(f"Today's Stock Price of {ticker_symbol}", fontsize='small')
    plt.xticks(times[::20], rotation=45)
    plt.yticks(fontsize='small')
    plt.xlabel('Time', fontsize='small')
    plt.ylabel('Price', fontsize='small')
    plt.grid(True)
    plt.tick_params(axis='x', labelsize=6)
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

def plot_etf_historical_data(ticker_symbol, start_date, end_date):

    # Fetch stock information
    stock = yf.Ticker(ticker_symbol)

    # Get the industry of the stock
    industry = stock.info.get("industry", None)

    # Extract etf ticker symbol corresponding to industry
    etf_ticker_symbol = get_sector_etf_for_stock().get(industry)
    
    # Check if ticker_symbol is not None
    if etf_ticker_symbol is None:
        return

    # Plot historical data
    plot_historical_data(etf_ticker_symbol, industry, start_date, end_date)

    return

def plot_stock_historical_data(ticker_symbol, start_date, end_date):

    # Fetch stock information
    stock = yf.Ticker(ticker_symbol)

    # Get the industry of the stock
    industry = stock.info.get("industry", None)

    # Plot historical data
    plot_historical_data(ticker_symbol, industry, start_date, end_date)

    return

def plot_historical_data(ticker_symbol, industry, start_date, end_date, long=False):

    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(start=start_date, end=end_date)

    # Determine which data to plot: Close or regularMarketPreviousClose
    if 'Close' in hist.columns:
        prices = hist['Close']
    elif hasattr(stock.info, 'regularMarketPreviousClose'):
        prices = [stock.info['regularMarketPreviousClose']] * len(hist)
    else:
        raise ValueError("No suitable price data found for this stock.")

    plt.plot(hist.index, prices, '-o', markersize=2)
    plt.title(f"Stock Price History of {ticker_symbol} ({industry})", fontsize='small')
    plt.yticks(fontsize='small')
    plt.xlabel('Date', fontsize='small')
    plt.ylabel('Price', fontsize='small')
    plt.grid(True)
    
    if not long:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45)
        plt.tick_params(axis='x', labelsize=6)

    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

    plt.show()

def plot_stock_history(ticker_symbol, start_date, end_date):
    plt.figure(figsize=(10, 4))
    
    # Plotting today's prices - Assuming stock_tracker is a defined function
    stock_tracker(ticker_symbol, 1)

    # Plotting stock history
    plt.subplot(1, 2, 2)
    plot_stock_historical_data(ticker_symbol, start_date, end_date)
