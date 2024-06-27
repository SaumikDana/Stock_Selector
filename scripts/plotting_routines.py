import setup
from imports import *
from scripts.analyze_stock import *
from scripts.scrape_url import get_stock_price

def plot_volatility_surface(options_data, ticker):
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.info.get('currentPrice', stock.info.get('previousClose', None))

        call_strikes = list(np.array(options_data['call_strikes'])/current_price)
        put_strikes = list(np.array(options_data['put_strikes'])/current_price)
        call_ivs = options_data['call_ivs']
        put_ivs = options_data['put_ivs']
        call_expirations = options_data['call_expirations']
        put_expirations = options_data['put_expirations']

        call_exp_nums = mdates.date2num(pd.to_datetime(call_expirations))
        put_exp_nums = mdates.date2num(pd.to_datetime(put_expirations))

        strikes = np.array(call_strikes + put_strikes)
        expirations = np.array(list(call_exp_nums) + list(put_exp_nums))
        ivs = np.array(call_ivs + put_ivs)

        if len(set(strikes)) < 2 or len(set(expirations)) < 2:
            print("Insufficient variation in strike prices or expiration dates for interpolation.")
            return

        if np.isnan(ivs).any() or np.isinf(ivs).any():
            print("Data contains NaNs or infinite values.")
            return

        strike_grid, exp_grid = np.meshgrid(
            np.linspace(strikes.min(), strikes.max(), 100),
            np.linspace(expirations.min(), expirations.max(), 100)
        )

        ivs_grid = griddata((strikes, expirations), ivs, (strike_grid, exp_grid), method='cubic')

        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(strike_grid, exp_grid, ivs_grid, cmap='viridis', edgecolor='none')

        ax.set_title(f'Volatility Surface for {ticker}')
        ax.set_xlabel('Strike/Spot')
        ax.set_ylabel('Expiration')
        ax.set_zlabel('Implied Volatility')

        ax.yaxis.set_major_locator(mdates.AutoDateLocator())
        ax.yaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        ax.yaxis.set_tick_params(labelsize=6)
        for label in ax.yaxis.get_majorticklabels():
            label.set_rotation(45)

        ax.view_init(30, 210)
        # colorbar = fig.colorbar(surf, shrink=0.5, aspect=30, pad=-0.025)
        plt.subplots_adjust(left=0.1, right=1.0, top=1.0, bottom=0.05)

        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")

def plot_iv_skew_otm_only(options_data, target_date, ticker, days_range=21):
    stock = yf.Ticker(ticker)
    current_price = stock.info.get('currentPrice', stock.info.get('previousClose', None))

    historical_volatility = calculate_historical_volatility(ticker)

    call_strikes = options_data['call_strikes']
    put_strikes = options_data['put_strikes']
    call_ivs = options_data['call_ivs']
    put_ivs = options_data['put_ivs']
    call_expirations = options_data['call_expirations']
    put_expirations = options_data['put_expirations']

    call_expirations_dt = [datetime.strptime(date, "%Y-%m-%d") for date in call_expirations]
    put_expirations_dt = [datetime.strptime(date, "%Y-%m-%d") for date in put_expirations]
    target_date_dt = np.datetime64(target_date)

    filtered_call_data_otm = [(strike, iv, exp) for strike, iv, exp in zip(call_strikes, call_ivs, call_expirations_dt)
                              if exp > target_date_dt and exp <= target_date_dt + np.timedelta64(days_range, 'D') and strike > current_price]
    call_strikes_rel_otm, call_ivs_rel_otm = zip(*[(strike/current_price, iv) for strike, iv, _ in filtered_call_data_otm]) if filtered_call_data_otm else ([], [])

    filtered_put_data_otm = [(strike, iv, exp) for strike, iv, exp in zip(put_strikes, put_ivs, put_expirations_dt)
                             if exp > target_date_dt and exp <= target_date_dt + np.timedelta64(days_range, 'D') and strike < current_price]
    put_strikes_rel_otm, put_ivs_rel_otm = zip(*[(strike/current_price, iv) for strike, iv, _ in filtered_put_data_otm]) if filtered_put_data_otm else ([], [])

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.scatter(call_strikes_rel_otm, call_ivs_rel_otm, color='blue', marker='o', label='OTM Calls', s=10)
    ax.scatter(put_strikes_rel_otm, put_ivs_rel_otm, color='green', marker='o', label='OTM Puts', s=10)
    ax.axvline(1, color='grey', linestyle='--', label='Current Price')

    ax.axhline(y=historical_volatility, color='purple', linestyle='--', label=f'Historical Volatility ({historical_volatility:.2%})')

    ax.set_title(f'OTM Options Implied Volatility Skew - {ticker}')
    ax.set_xlabel('Strike Price / Current Price')
    ax.set_ylabel('Implied Volatility')
    ax.legend(frameon=False, loc='best')
    ax.grid(True)

    plt.tight_layout()
    plt.show()

def plot_pe_ratio(ticker_symbol, date):
    start_date = date - timedelta(days=365)  
    end_date = date  

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
    plot_historical_data(ticker_symbol, industry, start_date, end_date)

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
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    stock_tracker(ticker_symbol)

    plt.subplot(1, 2, 2)
    plot_stock_historical_data(ticker_symbol, start_date, end_date)
    plt.close()

    plot_rsi(ticker_symbol, start_date, end_date)

def plot_option_data(df, ticker, option_type='Calls', stock_price=None):
    if 'contractSymbol' not in df.columns:
        return
    df = df[df['contractSymbol'].str.contains('C' if option_type == 'Calls' else 'P')]
    df = df[df['openInterest'] > 0]
    df = df.sort_values(by='strike', ascending=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # 1 row, 2 columns

    ax1.scatter(df['strike'], df['impliedVolatility'], 
                color='green' if option_type == 'Calls' else 'red', 
                edgecolors='black', s=10)
    ax1.set_title(f'{option_type} Options, {ticker}')
    ax1.set_xlabel('Strike Price')
    ax1.set_ylabel('Implied Volatility')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True)

    if stock_price is not None:
        ax1.axvline(x=stock_price, color='blue', linestyle='--', linewidth=2, label=f'Spot: {stock_price}')
        ax1.legend()

    ax2.scatter(df['strike'], df['openInterest'], 
                color='green' if option_type == 'Calls' else 'red', 
                edgecolors='black', s=10)
    ax2.set_title(f'{option_type} Options, {ticker}')
    ax2.set_xlabel('Strike Price')
    ax2.set_ylabel('Open Interest')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True)

    if stock_price is not None:
        ax2.axvline(x=stock_price, color='blue', linestyle='--', linewidth=2, label=f'Spot: {stock_price}')
        ax2.legend()

    plt.tight_layout()
    plt.show()

def plot_calls_puts_separately(df, ticker):
    stock_price = get_stock_price(ticker)
    plot_option_data(df, ticker, 'Calls', stock_price=stock_price)
    plot_option_data(df, ticker, 'Puts', stock_price=stock_price)

    return

def plot_rsi(ticker_symbol, start_date, end_date, window=14):

    adjusted_start_date = start_date - timedelta(days=window)

    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(start=adjusted_start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    rsi = ta.momentum.RSIIndicator(hist['Close'], window=window).rsi()

    # Set up the plot
    plt.figure(figsize=(8, 4))
    plt.plot(rsi.index, rsi, label='RSI', color='purple')
    plt.axhline(70, linestyle='--', color='red', alpha=0.5)
    plt.axhline(30, linestyle='--', color='green', alpha=0.5)
    plt.title(f'RSI, {ticker_symbol}')
    plt.xticks(rotation=45)
    plt.tick_params(axis='x', labelsize=8)  # Reduce x-tick label size

    plt.show()
    return
