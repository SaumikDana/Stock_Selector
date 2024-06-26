import setup
from imports import *

def print_info_keys(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    try:
        stock_info = stock.info  
        print(f"Information for {ticker_symbol}:")
        for key, value in stock_info.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error retrieving info for {ticker_symbol}: {e}")

def get_financial_ratios(ticker_symbol, start_date, end_date):
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(start=start_date, end=end_date)

    if 'trailingEps' in stock.info:
        trailing_eps = stock.info['trailingEps']
        hist['P/E'] = hist['Close'] / trailing_eps

    return hist
    
def get_sector_etf_for_stock():
    industry_etf_dict = {
        "Residential Construction": "XHB",
        "Specialty Chemicals": "XLB",
        "Credit Services": "XLF",
        "Financial Data & Stock Exchanges": "IYG",
        "Electrical Equipment & Parts": "XLI",
        "Computer Hardware": "XLK",
        "Farm & Heavy Construction Machinery": "XLI",
        "Insurance Brokers": "IAK",
        "Software - Infrastructure": "IGV",
        "Steel": "SLX",
        "Semiconductors": "SMH",
        "Semiconductor Equipment & Materials": "SMH",
        "Aerospace & Defense": "ITA",
        "REIT - Office": "IYR",
        "Capital Markets": "IAI",
        "Furnishings, Fixtures & Appliances": "XLY",
        "Banks - Regional": "KRE",
        "Industrial Distribution": "FXR",
        "Specialty Industrial Machinery": "XLI",
        "Medical Instruments & Supplies": "IHI",
        "Railroads": "IYT",
        "Medical Devices": "IHI",
        "REIT - Residential": "REZ",
        "Electronic Components": "SOXX",
        "Packaged Foods": "XLP",
        "REIT - Specialty": "XLRE",
        "Insurance - Life": "IAK",
        "Software - Application": "IGV",
        "Asset Management": "XLF",
        "Communication Equipment": "XLK",
        "Internet Content & Information": "XLC",
        "Oil & Gas Drilling": "OIH",
        "Electronics & Computer Distribution": "XLK",
        "Information Technology Services": "XLK",
        "Airlines": "JETS",
        "REIT - Mortgage": "REM",
        "Packaging & Containers": "XLB",
        "Auto Parts": "CARZ",
        "Food Distribution": "XLP",
        "Diagnostics & Research": "IHF",
        "Pharmaceutical Retailers": "XLP",
        "Telecom Services": "XLC",
        "Biotechnology": "IBB",
        "Drug Manufacturers - Specialty & Generic": "XPH",
        "Pollution & Treatment Controls": "XLI",  
        "Tobacco": "XLP",
        "Restaurants": "PBJ"
    }

    return industry_etf_dict

def calculate_historical_volatility(ticker_symbol, period="1y"):
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period=period)

    daily_returns = hist['Close'].pct_change().dropna()

    historical_volatility = np.std(daily_returns)
    
    return historical_volatility

def analyze_stock_options(ticker, price_range_factor=0.25):
    stock = yf.Ticker(ticker)

    current_price = stock.info.get('currentPrice', stock.info.get('previousClose', None))

    lower_bound = current_price * (1 - price_range_factor)
    upper_bound = current_price * (1 + price_range_factor)

    # Initialize variables for aggregating options data
    total_call_volume, total_call_open_interest, total_call_implied_volatility = 0, 0, []
    total_put_volume, total_put_open_interest, total_put_implied_volatility = 0, 0, []
    total_itm_calls, total_itm_puts = 0, 0  
    total_otm_calls, total_otm_puts = 0, 0  
    call_strike_prices, put_strike_prices, call_expirations, put_expirations = [], [], [], []  
    call_ivs, put_ivs = [], []  
    exp_dates_count = 0  

    exp_dates = stock.options

    # Loop through each expiration date to analyze options data
    for date in exp_dates:
        options_data = stock.option_chain(date)

        call_options, put_options = options_data.calls, options_data.puts

        filtered_call_options = call_options[(call_options['strike'] >= lower_bound) & (call_options['strike'] <= upper_bound)]
        filtered_put_options = put_options[(put_options['strike'] >= lower_bound) & (put_options['strike'] <= upper_bound)]

        call_strike_prices.extend(filtered_call_options['strike'].tolist())
        put_strike_prices.extend(filtered_put_options['strike'].tolist())
        call_ivs.extend(filtered_call_options['impliedVolatility'].tolist())
        put_ivs.extend(filtered_put_options['impliedVolatility'].tolist())
        call_expirations.extend([date] * len(filtered_call_options))
        put_expirations.extend([date] * len(filtered_put_options))

        total_call_volume += filtered_call_options['volume'].sum()
        total_call_open_interest += filtered_call_options['openInterest'].sum()
        total_call_implied_volatility.extend(filtered_call_options['impliedVolatility'].tolist())

        total_put_volume += filtered_put_options['volume'].sum()
        total_put_open_interest += filtered_put_options['openInterest'].sum()
        total_put_implied_volatility.extend(filtered_put_options['impliedVolatility'].tolist())

        # Increment the expiration dates counter
        exp_dates_count += 1

    # Return a dictionary with the aggregated and calculated options metrics
    return {
        "call_strike_prices": call_strike_prices,
        "put_strike_prices": put_strike_prices,
        "call_ivs": call_ivs,
        "put_ivs": put_ivs,
        "call_expirations": call_expirations,
        "put_expirations": put_expirations
    }

def options_chain(symbol):
    # Create a ticker object
    tk = yf.Ticker(symbol)
    # Get expiration dates
    exps = tk.options

    # Get the current date
    current_date = datetime.now().date()

    # Get options for each expiration
    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt_df = pd.concat([opt.calls, opt.puts])
        opt_df['expirationDate'] = e
        # Convert expirationDate to datetime.date for calculation
        opt_df['expirationDate'] = pd.to_datetime(opt_df['expirationDate']).dt.date
        # Calculate days to expiry
        opt_df['daysToExpiry'] = (opt_df['expirationDate'] - current_date).apply(lambda x: x.days)
        options = pd.concat([options, opt_df], ignore_index=True)

    # Filter out entries where daysToExpiry is greater than 30
    if 'daysToExpiry' in options.columns:
        options = options[options['daysToExpiry'] <= 30]

    return options
