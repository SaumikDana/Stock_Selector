# Importing necessary libraries for data manipulation, mathematical operations and plotting
import matplotlib.pyplot as plt
import yfinance as yf  
import pandas as pd
import numpy as np
import scipy.stats as si

# Black-Scholes Call Price Calculation
def black_scholes_call(S, K, T, r, sigma):
    # Prevent division by zero or near-zero values in sigma and T
    sigma = max(sigma, 0.0001)
    T = max(T, 1/(365*24*60))  # Ensuring at least 1 minute to expiration

    # Calculating d1 and d2 using the Black-Scholes formula components
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Try-except block to handle exceptions during call price calculation
    try:
        call_price = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    except Exception as e:
        print(f"Error calculating call price: {e}")
        call_price = np.nan

    return call_price

# Calculate Greeks for Call Option
def call_greeks(S, K, T, r, sigma):
    # Prevent division by zero or near-zero values in sigma and T
    sigma = max(sigma, 0.0001)
    T = max(T, 1/(365*24*60))  # Ensuring at least 1 minute to expiration

    # Try-except block to handle exceptions during Greeks calculation
    try:
        # Calculating d1 and d2 for Greeks
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Calculating each of the Greeks for Call options
        delta = si.norm.cdf(d1, 0.0, 1.0)
        gamma = si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T))
        theta = -((S * si.norm.pdf(d1, 0.0, 1.0) * sigma) / (2 * np.sqrt(T))) - r * K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
        vega = S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T)
        rho = K * T * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0)
    except Exception as e:
        print(f"Error calculating Greeks: {e}")
        return {'delta': np.nan, 'gamma': np.nan, 'theta': np.nan, 'vega': np.nan, 'rho': np.nan}

    return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega, 'rho': rho}

# Black-Scholes Put Price Calculation
def black_scholes_put(S, K, T, r, sigma):
    # Prevent division by zero or near-zero values in sigma and T
    sigma = max(sigma, 0.0001)
    T = max(T, 1/(365*24*60))

    # Calculating d1 and d2 for the put option price
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Calculating the put price using the Black-Scholes formula
    return (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))

# Calculate Greeks for Put Option
def put_greeks(S, K, T, r, sigma):
    # Calculating d1 and d2 for the Greeks
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # Calculating each of the Greeks for Put options
    delta = -si.norm.cdf(-d1, 0.0, 1.0)
    gamma = si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T))
    theta = -((S * si.norm.pdf(d1, 0.0, 1.0) * sigma) / (2 * np.sqrt(T))) + r * K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0)
    vega = S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T)
    rho = -K * T * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0)
    return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega, 'rho': rho}

def plot_selected_greeks(dates, greeks_data, selected_greeks, title, subplot=None):
    if subplot is not None:
        plt.subplot(subplot)
    else:
        plt.figure(figsize=(10, 4))
    
    # Plotting the selected Greeks over time
    for greek in selected_greeks:
        plt.plot(dates, greeks_data[greek], label=greek.capitalize())
    
    # Setting the plot title and labels
    plt.title(title)
    plt.legend(loc='best', frameon=False, fontsize='small')
    plt.grid(True)
    plt.xticks(rotation=45, fontsize='small')
    plt.yticks(fontsize='small')

def analyze_and_plot_greeks(ticker_symbol, risk_free_rate=0.01):
    # Fetch stock data using yfinance for the given ticker symbol
    stock = yf.Ticker(ticker_symbol)

    # Get all available options expiration dates
    exp_dates = stock.options

    # Fetch stock's current price or the previous close if current price is not available
    stock_info = stock.info
    S = stock_info.get('currentPrice', stock_info.get('previousClose', None))
    if S is None:
        raise ValueError("No current price data available.")

    # Initialize lists to store prices and dates, and dictionaries to store Greeks data
    call_bs_prices, put_bs_prices, dates = [], [], []
    call_greeks_data = {'delta': [], 'gamma': [], 'theta': [], 'vega': [], 'rho': []}
    put_greeks_data = {'delta': [], 'gamma': [], 'theta': [], 'vega': [], 'rho': []}

    # Loop through each expiration date to calculate prices and Greeks
    for date in exp_dates:
        # Get the options chain for the given date
        options_data = stock.option_chain(date)
        call_options = options_data.calls
        put_options = options_data.puts

        # Calculate time to expiration in years
        T = (pd.to_datetime(date) - pd.Timestamp.now()).days / 365
        dates.append(pd.to_datetime(date))

        # Find the call option closest to the money and calculate its Black-Scholes price and Greeks
        selected_call_option = call_options.iloc[(call_options['strike'] - S).abs().argsort()[:1]]
        for _, call_row in selected_call_option.iterrows():
            K = call_row['strike']  # Strike price
            sigma = call_row['impliedVolatility']  # Implied volatility
            # Calculate the Black-Scholes price
            price = black_scholes_call(S, K, T, risk_free_rate, sigma)
            call_bs_prices.append(price)
            # Calculate the Greeks for the call option
            call_greeks_result = call_greeks(S, K, T, risk_free_rate, sigma)
            for key in call_greeks_result:
                call_greeks_data[key].append(call_greeks_result[key])

        # Repeat the process for the put option closest to the money
        selected_put_option = put_options.iloc[(put_options['strike'] - S).abs().argsort()[:1]]
        for _, put_row in selected_put_option.iterrows():
            K = put_row['strike']
            sigma = put_row['impliedVolatility']
            # Calculate the Black-Scholes price for the put option
            put_price = black_scholes_put(S, K, T, risk_free_rate, sigma)
            put_bs_prices.append(put_price)
            # Calculate the Greeks for the put option
            put_greeks_result = put_greeks(S, K, T, risk_free_rate, sigma)
            for key in put_greeks_result:
                put_greeks_data[key].append(put_greeks_result[key])

    # Align the call data for non-NaN prices and corresponding dates
    aligned_call_dates, aligned_call_bs_prices = [], []
    for date, price in zip(dates, call_bs_prices):
        if not np.isnan(price):
            aligned_call_dates.append(date)
            aligned_call_bs_prices.append(price)
    # Verify that data for all Greeks have the same length as the dates
    call_data_is_aligned = all(len(values) == len(aligned_call_dates) for values in call_greeks_data.values())

    # Repeat the alignment process for put options
    aligned_put_dates, aligned_put_bs_prices = [], []
    for date, price in zip(dates, put_bs_prices):
        if not np.isnan(price):
            aligned_put_dates.append(date)
            aligned_put_bs_prices.append(price)
    put_data_is_aligned = all(len(values) == len(aligned_put_dates) for values in put_greeks_data.values())

    # Create a matplotlib figure for plotting
    plt.figure(figsize=(10, 8))

    # Plot Delta and Gamma for call options
    plot_selected_greeks(aligned_call_dates, call_greeks_data, ['delta', 'gamma'], 'Call Option Delta & Gamma', 221)

    # Plot Theta, Vega, and Rho for call options
    other_greeks = ['theta', 'vega', 'rho']
    plot_selected_greeks(aligned_call_dates, call_greeks_data, other_greeks, 'Call Option Theta, Vega & Rho', 222)

    # Plot Delta and Gamma for put options
    plot_selected_greeks(aligned_put_dates, put_greeks_data, ['delta', 'gamma'], 'Put Option Delta & Gamma', 223)

    # Plot Theta, Vega, and Rho for put options
    plot_selected_greeks(aligned_put_dates, put_greeks_data, other_greeks, 'Put Option Theta, Vega & Rho', 224)

    # Adjust layout and show the plots
    plt.tight_layout()
    plt.show()