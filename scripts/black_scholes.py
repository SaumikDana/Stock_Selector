import setup
from imports import *

def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    """Calculate Black-Scholes price for both call and put options."""
    sigma = max(sigma, 0.0001)
    T = max(T, 1/(365*24*60))
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        return (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    else:  # put
        return (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))

def calculate_greeks(S, K, T, r, sigma, option_type='call'):
    """Calculate Greeks for both call and put options."""
    sigma = max(sigma, 0.0001)
    T = max(T, 1/(365*24*60))
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    greeks = {
        'delta': si.norm.cdf(d1, 0.0, 1.0) if option_type == 'call' else -si.norm.cdf(-d1, 0.0, 1.0),
        'gamma': si.norm.pdf(d1, 0.0, 1.0) / (S * sigma * np.sqrt(T)),
        'theta': -((S * si.norm.pdf(d1, 0.0, 1.0) * sigma) / (2 * np.sqrt(T))) - r * K * np.exp(-r * T) * si.norm.cdf(d2 if option_type == 'call' else -d2, 0.0, 1.0),
        'vega': S * si.norm.pdf(d1, 0.0, 1.0) * np.sqrt(T),
        'rho': K * T * np.exp(-r * T) * si.norm.cdf(d2 if option_type == 'call' else -d2, 0.0, 1.0) * (1 if option_type == 'call' else -1)
    }
    return greeks

def process_options(options, S, T, r, type='call'):
    """Process options data to extract Black-Scholes prices and Greeks."""
    prices, greeks_data = [], {'delta': [], 'gamma': [], 'theta': [], 'vega': [], 'rho': []}
    selected_option = options.iloc[(options['strike'] - S).abs().argsort()[:1]]
    for _, row in selected_option.iterrows():
        K = row['strike']
        sigma = row['impliedVolatility']
        price = black_scholes_price(S, K, T, r, sigma, type)
        prices.append(price)
        greeks = calculate_greeks(S, K, T, r, sigma, type)
        for key in greeks:
            greeks_data[key].append(greeks[key])
    return prices, greeks_data

def analyze_and_plot_greeks(ticker_symbol, risk_free_rate=0.01):
    stock = yf.Ticker(ticker_symbol)
    exp_dates = stock.options
    stock_info = stock.info
    S = stock_info.get('currentPrice', stock_info.get('previousClose', None))
    if S is None:
        raise ValueError("No current price data available.")

    call_bs_prices, put_bs_prices, dates = [], [], []
    call_greeks_data, put_greeks_data = {}, {}

    for date in exp_dates:
        options_data = stock.option_chain(date)
        T = (pd.to_datetime(date) - pd.Timestamp.now()).days / 365
        dates.append(pd.to_datetime(date))

        call_prices, call_greeks = process_options(options_data.calls, S, T, risk_free_rate, 'call')
        put_prices, put_greeks = process_options(options_data.puts, S, T, risk_free_rate, 'put')

        call_bs_prices.extend(call_prices)
        put_bs_prices.extend(put_prices)
        for key in call_greeks:
            call_greeks_data.setdefault(key, []).extend(call_greeks[key])
            put_greeks_data.setdefault(key, []).extend(put_greeks[key])

    # Create a matplotlib figure for plotting
    plt.figure(figsize=(10, 8))

    # Define a helper function for plotting selected Greeks
    def plot_selected_greeks(dates, greeks_data, selected_greeks, title, subplot=None):
        if subplot is not None:
            plt.subplot(subplot)
        else:
            plt.figure(figsize=(10, 4))
        
        for greek in selected_greeks:
            plt.plot(dates, greeks_data[greek], label=greek.capitalize())
        
        plt.title(title)
        plt.legend(loc='best', frameon=False, fontsize='small')
        plt.grid(True)
        plt.xticks(rotation=45, fontsize='small')
        plt.yticks(fontsize='small')

    # Plot Delta and Gamma for call options
    plot_selected_greeks(dates, call_greeks_data, ['delta', 'gamma'], 'Call Option Delta & Gamma', 221)

    # Plot Theta, Vega, and Rho for call options
    plot_selected_greeks(dates, call_greeks_data, ['theta', 'vega', 'rho'], 'Call Option Theta, Vega & Rho', 222)

    # Plot Delta and Gamma for put options
    plot_selected_greeks(dates, put_greeks_data, ['delta', 'gamma'], 'Put Option Delta & Gamma', 223)

    # Plot Theta, Vega, and Rho for put options
    plot_selected_greeks(dates, put_greeks_data, ['theta', 'vega', 'rho'], 'Put Option Theta, Vega & Rho', 224)

    # Adjust layout and show the plots
    plt.tight_layout()
    plt.show()
