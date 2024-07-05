import setup
from imports import *
from scripts.analyze_stock import *
    
def stock_tracker(ticker_symbol):
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
    
    plt.plot(times, todays_prices['Close'])
    plt.title(f"Today's Stock Price of {ticker_symbol}", fontsize='small')
    plt.xticks(times[::20], rotation=45)
    plt.yticks(fontsize='small')
    plt.xlabel('Time', fontsize='small')
    plt.ylabel('Price', fontsize='small')
    plt.grid(True)
    plt.tick_params(axis='x', labelsize=6)
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

def plot_stock_historical_data(ticker_symbol, start_date, end_date):
    stock = yf.Ticker(ticker_symbol)
    industry = stock.info.get("industry", None)
    adjusted_start_date = start_date - timedelta(days=180)

    plot_historical_data(ticker_symbol, industry, adjusted_start_date, end_date)

    return

def plot_historical_data(ticker_symbol, industry, start_date, end_date, long=False):
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(start=start_date, end=end_date)

    if 'Close' in hist.columns:
        prices = hist['Close']
    elif hasattr(stock.info, 'regularMarketPreviousClose'):
        prices = [stock.info['regularMarketPreviousClose']] * len(hist)
    else:
        raise ValueError("No suitable price data found for this stock.")

    plt.figure(figsize=(8, 4))

    plt.plot(hist.index, prices, '-o', markersize=2)
    plt.title(f"Stock Price History of {ticker_symbol} ({industry})", fontsize='small')
    plt.grid(True)
    
    plt.xticks(rotation=45)
    plt.tick_params(axis='x', labelsize=6)

    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

    plt.show()

def plot_stock_history(ticker_symbol, start_date, end_date):
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    stock_tracker(ticker_symbol)

    plt.subplot(1, 2, 2)
    plot_stock_historical_data(ticker_symbol, start_date, end_date)
    plt.close()

def plot_metric(ticker_symbol, metric, name):
    plt.figure(figsize=(8, 4))
    plt.plot(metric.index, metric, color='purple')
    plt.title(f'{name.upper()}, {ticker_symbol}')
    plt.xticks(rotation=45)
    plt.tick_params(axis='x', labelsize=6)
    plt.grid(True)  
    plt.show()

def plot_rsi(ticker_symbol, stock, adjusted_start_date, end_date, window=14):
    adjusted_start_date -= timedelta(days=window)
    hist = stock.history(start=adjusted_start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    rsi = calculate_rsi(hist, window=window)
    plot_metric(ticker_symbol, rsi, 'rsi')

def plot_obv(ticker_symbol, stock, adjusted_start_date, end_date):
    hist = stock.history(start=adjusted_start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    obv = calculate_obv(hist)
    plot_metric(ticker_symbol, obv, 'obv')

def plot_macd(ticker_symbol, stock, adjusted_start_date, end_date, window_slow=26, window_fast=12, window_sign=9):
    adjusted_start_date -= timedelta(days=window_slow+window_sign)
    hist = stock.history(start=adjusted_start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    macd, macd_signal, _ = calculate_macd(hist, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
    plt.figure(figsize=(8, 4))
    plt.plot(macd.index, macd, color='blue', label='MACD')
    plt.plot(macd_signal.index, macd_signal, color='red', label='MACD SIGNAL')
    plt.title(f'MACD/MACD SIGNAL, {ticker_symbol}')
    plt.xticks(rotation=45)
    plt.legend(frameon=False, loc='best')
    plt.tick_params(axis='x', labelsize=6)
    plt.grid(True)  
    plt.show()

def plot_indicators(ticker_symbol, start_date, end_date):

    adjusted_start_date = start_date - timedelta(days=180)
    stock = yf.Ticker(ticker_symbol)

    plot_macd(ticker_symbol, stock, adjusted_start_date, end_date)
    plot_rsi(ticker_symbol, stock, adjusted_start_date, end_date)
    plot_obv(ticker_symbol, stock, adjusted_start_date, end_date)

