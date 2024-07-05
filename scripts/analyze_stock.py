import setup
from imports import *
    
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

def calculate_macd(data, window_slow=26, window_fast=12, window_sign=9):
    macd_indicator = ta.trend.MACD(data['Close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
    macd = macd_indicator.macd()
    macd_signal = macd_indicator.macd_signal()
    macd_hist = macd_indicator.macd_diff()  
    return macd, macd_signal, macd_hist

def calculate_obv(data):
    obv = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()
    return obv

def calculate_rsi(data, window=14):
    rsi = ta.momentum.RSIIndicator(data['Close'], window=window).rsi()
    return rsi

def get_stock_news(stock):
    news = stock.news    
    if news:
        for item in news:
            print(f"Title: {item['title']}")
            print(f"Publisher: {item['publisher']}")
            print(f"Link: {item['link']}")
            # Convert UNIX timestamp to a readable date
            date = datetime.fromtimestamp(item['providerPublishTime'])
            print(f"Date: {date.strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n")
    else:
        print("No news available for this ticker.")