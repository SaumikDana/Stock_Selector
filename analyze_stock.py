import yfinance as yf  
from analyze_options import *

def print_info_keys(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    try:
        stock_info = stock.info  # Fetch stock information
        print(f"Information for {ticker_symbol}:")
        for key, value in stock_info.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error retrieving info for {ticker_symbol}: {e}")

# Function to fetch historical financial ratios
def get_financial_ratios(ticker_symbol, start_date, end_date):
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(start=start_date, end=end_date)

    # Use trailing EPS to calculate P/E ratio if available
    if 'trailingEps' in stock.info:
        trailing_eps = stock.info['trailingEps']
        hist['P/E'] = hist['Close'] / trailing_eps

    # Other calculations could follow a similar pattern if the data were available
    
    return hist
    
def get_sector_etf_for_stock():
    # Dictionary mapping industries to their corresponding ETFs
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
        "Conglomerates": None,  # No specific ETF
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
        "Thermal Coal": None,  # No specific ETF
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
        "Pollution & Treatment Controls": "XLI",  # Part of a broader category
        "Tobacco": "XLP",
        "Restaurants": "PBJ"
    }

    return industry_etf_dict
