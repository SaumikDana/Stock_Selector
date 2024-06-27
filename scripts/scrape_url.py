import setup
from imports import *

def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    try:
        stock_info = stock.info
        price = stock_info.get('currentPrice')
        return price
    except ValueError as e:
        print(f"Error retrieving info for {ticker}: {e}")
        return None

def process_earnings_table(table, ticker_data_list):
    df = pd.read_html(str(table))[0]
    if 'Symbol' in df.columns:
        for _, row in df.iterrows():
            ticker = row.get('Symbol')
            if pd.notna(ticker):
                price = get_stock_price(ticker)
                ticker_data_list.append(pd.DataFrame({'Symbol': [ticker], 'Stock Price': [price]}))
    return ticker_data_list

def extract_table(url):
    try:
        driver.get(url)
        time.sleep(1)  
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()  
        table = soup.find_all('table')
        if not table:
            return None
        return table
    except:
        return None  
        
def convert_to_dataframe(ticker_data_list, ticker_data_sorted=pd.DataFrame()):
    ticker_data = pd.concat(ticker_data_list, ignore_index=True)
    ticker_data = ticker_data.dropna(subset=['Stock Price'])
    ticker_data_sorted = ticker_data.sort_values(by='Stock Price', ascending=False)

    return ticker_data_sorted
