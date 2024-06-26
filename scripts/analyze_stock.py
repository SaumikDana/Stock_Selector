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

def extend_lists(call_strikes, put_strikes, call_ivs, put_ivs, call_expirations, put_expirations, call_options, put_options, date):
        
    call_strikes.extend(call_options['strike'].tolist())
    put_strikes.extend(put_options['strike'].tolist())
    call_ivs.extend(call_options['impliedVolatility'].tolist())
    put_ivs.extend(put_options['impliedVolatility'].tolist())
    call_expirations.extend([date] * len(call_options))
    put_expirations.extend([date] * len(put_options))

    return

def analyze_stock_options(ticker):
    stock = yf.Ticker(ticker)
    exp_dates = stock.options

    call_strikes, put_strikes, call_expirations, put_expirations, call_ivs, put_ivs = [], [], [], [], [], []  

    for date in exp_dates:
        opt = stock.option_chain(date)
        call_options, put_options = opt.calls, opt.puts
        extend_lists(call_strikes, put_strikes, call_ivs, put_ivs, call_expirations, put_expirations, call_options, put_options, date)

    opt_dict = {
        "call_strikes": call_strikes,
        "put_strikes": put_strikes,
        "call_ivs": call_ivs,
        "put_ivs": put_ivs,
        "call_expirations": call_expirations,
        "put_expirations": put_expirations
    }

    return opt_dict

def options_chain(ticker):
    stock = yf.Ticker(ticker)
    exp_dates = stock.options

    current_date = datetime.now().date()

    options = pd.DataFrame()
    for date in exp_dates:
        opt = stock.option_chain(date)
        call_options, put_options = opt.calls, opt.puts
        opt_df = pd.concat([call_options, put_options])
        opt_df['expirationDate'] = date
        opt_df['expirationDate'] = pd.to_datetime(opt_df['expirationDate']).dt.date
        opt_df['daysToExpiry'] = (opt_df['expirationDate'] - current_date).apply(lambda x: x.days)
        options = pd.concat([options, opt_df], ignore_index=True)

    if 'daysToExpiry' in options.columns:
        options = options[options['daysToExpiry'] <= 30]

    return options
