import yfinance as yf  
import numpy as np

def calculate_historical_volatility(ticker_symbol, period="1y"):
    # Fetch historical stock data
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period=period)

    # Calculate daily returns
    daily_returns = hist['Close'].pct_change().dropna()

    # Calculate standard deviation of daily returns (historical volatility)
    historical_volatility = np.std(daily_returns)
    
    return historical_volatility

def analyze_stock_options(ticker, price_range_factor=0.25):
    # Fetch the stock data using the provided ticker symbol
    stock = yf.Ticker(ticker)

    # Get current stock price
    current_price = stock.info.get('currentPrice', stock.info.get('previousClose', None))

    # Calculate bounds for strike price filtering based on current price
    lower_bound = current_price * (1 - price_range_factor)
    upper_bound = current_price * (1 + price_range_factor)

    # Initialize variables for aggregating options data
    total_call_volume, total_call_open_interest, total_call_implied_volatility = 0, 0, []
    total_put_volume, total_put_open_interest, total_put_implied_volatility = 0, 0, []
    total_itm_calls, total_itm_puts = 0, 0  # Counters for in-the-money options
    total_otm_calls, total_otm_puts = 0, 0  # Counters for out-of-the-money options
    call_strike_prices, put_strike_prices, call_expirations, put_expirations = [], [], [], []  # Lists to store data
    call_ivs, put_ivs = [], []  # Lists to store implied volatilities
    exp_dates_count = 0  # Counter for the number of expiration dates

    # Get the list of options expiration dates for the stock
    exp_dates = stock.options

    # Loop through each expiration date to analyze options data
    for date in exp_dates:
        # Retrieve call and put options data for the current expiration date
        options_data = stock.option_chain(date)

        call_options, put_options = options_data.calls, options_data.puts

        # Filter options with strike prices within the defined range
        filtered_call_options = call_options[(call_options['strike'] >= lower_bound) & (call_options['strike'] <= upper_bound)]
        filtered_put_options = put_options[(put_options['strike'] >= lower_bound) & (put_options['strike'] <= upper_bound)]

        # Append strike prices, implied volatilities, and expiration dates to the respective lists
        call_strike_prices.extend(filtered_call_options['strike'].tolist())
        put_strike_prices.extend(filtered_put_options['strike'].tolist())
        call_ivs.extend(filtered_call_options['impliedVolatility'].tolist())
        put_ivs.extend(filtered_put_options['impliedVolatility'].tolist())
        call_expirations.extend([date] * len(filtered_call_options))
        put_expirations.extend([date] * len(filtered_put_options))

        # Aggregate call and put options data
        total_call_volume += filtered_call_options['volume'].sum()
        total_call_open_interest += filtered_call_options['openInterest'].sum()
        total_call_implied_volatility.extend(filtered_call_options['impliedVolatility'].tolist())

        total_put_volume += filtered_put_options['volume'].sum()
        total_put_open_interest += filtered_put_options['openInterest'].sum()
        total_put_implied_volatility.extend(filtered_put_options['impliedVolatility'].tolist())

        # Count in-the-money and out-of-the-money options based on the current price
        total_itm_calls += len(filtered_call_options[filtered_call_options['strike'] < current_price])
        total_otm_calls += len(filtered_call_options[filtered_call_options['strike'] > current_price])

        total_itm_puts += len(filtered_put_options[filtered_put_options['strike'] > current_price])
        total_otm_puts += len(filtered_put_options[filtered_put_options['strike'] < current_price])

        # Increment the expiration dates counter
        exp_dates_count += 1

    # Average the implied volatilities if there are any entries in the list
    avg_call_implied_volatility = sum(total_call_implied_volatility) / len(total_call_implied_volatility) if total_call_implied_volatility else 0
    avg_put_implied_volatility = sum(total_put_implied_volatility) / len(total_put_implied_volatility) if total_put_implied_volatility else 0

    # Calculate total engagement for calls and puts
    total_call_engagement = total_call_volume + total_call_open_interest
    total_put_engagement = total_put_volume + total_put_open_interest

    # Return a dictionary with the aggregated and calculated options metrics
    return {
        "total_call_engagement": total_call_engagement,
        "total_put_engagement": total_put_engagement,
        "avg_call_implied_volatility": avg_call_implied_volatility,
        "avg_put_implied_volatility": avg_put_implied_volatility,
        "total_call_volume": total_call_volume,
        "total_call_open_interest": total_call_open_interest,
        "total_put_volume": total_put_volume,
        "total_put_open_interest": total_put_open_interest,
        "total_itm_calls": total_itm_calls,
        "total_itm_puts": total_itm_puts,
        "total_otm_calls": total_otm_calls,
        "total_otm_puts": total_otm_puts,
        "call_strike_prices": call_strike_prices,
        "put_strike_prices": put_strike_prices,
        "call_ivs": call_ivs,
        "put_ivs": put_ivs,
        "call_expirations": call_expirations,
        "put_expirations": put_expirations
    }

def print_options_data(ticker, options_metrics):
    
    print("===========================================")

    print(f"Options data for {ticker}:")

    print(f"Average IV for Calls: {options_metrics['avg_call_implied_volatility']}")
    print(f"Average IV for Puts: {options_metrics['avg_put_implied_volatility']}")

    print(f"Total Call Volume: {options_metrics['total_call_volume']}")
    print(f"Total Call open interest: {options_metrics['total_call_open_interest']}")
    print(f"Total Call engagement: {options_metrics['total_call_engagement']}")

    print(f"Total Put Volume: {options_metrics['total_put_volume']}")
    print(f"Total Put open interest: {options_metrics['total_put_open_interest']}")
    print(f"Total Put engagement: {options_metrics['total_put_engagement']}")

    print(f"Number of ITM Call Options: {options_metrics['total_itm_calls']}")
    print(f"Number of ITM Put Options: {options_metrics['total_itm_puts']}")

    print(f"Number of OTM Call Options: {options_metrics['total_otm_calls']}")
    print(f"Number of OTM Put Options: {options_metrics['total_otm_puts']}")

    print("===========================================")

    return

