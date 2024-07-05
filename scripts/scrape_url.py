import setup
from imports import *

def process_earnings_table(table, ticker_data_list):
    df = pd.read_html(str(table))[0]
    if 'Symbol' in df.columns:
        for _, row in df.iterrows():
            ticker = row.get('Symbol')
            ticker_data_list.append(pd.DataFrame({'Symbol': [ticker]}))
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

def convert_to_dataframe(ticker_data_list):
    ticker_data = pd.concat(ticker_data_list, ignore_index=True)
    return ticker_data

def fetch_ma(url):
    # Send the request to the URL
    response = requests.get(url)
    # Check if the request was successful
    response.raise_for_status()
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table by ID or class or tag etc.
    table = soup.find('table')
    
    # Extract the rows from the table
    rows = table.find_all('tr')
    
    # List to hold all ticker symbols
    ticker_symbols_acquirer = []
    ticker_symbols_target = []
    
    # Skip the first row assuming it's the header row
    for row in rows[1:]:
        cols = row.find_all('td')
        # Check if there are enough columns to have a second entry
        if len(cols) > 1:
            if cols[9].text.strip() == "Completed":
                continue
            ticker_symbol_acquirer = cols[3].text.strip()
            ticker_symbol_target = cols[4].text.strip()

            if ticker_symbol_acquirer.count('(') == 1 and ticker_symbol_acquirer.count(')') == 1:
                match = re.search(r'\((.*?)\)', ticker_symbol_acquirer)
                ticker_symbols_acquirer.append(match.group(1))

            if ticker_symbol_target.count('(') == 1 and ticker_symbol_target.count(')') == 1:
                match = re.search(r'\((.*?)\)', ticker_symbol_target)
                ticker_symbols_target.append(match.group(1))
    
    return ticker_symbols_acquirer, ticker_symbols_target

def process_ma_table(ticker_list, ticker_data_list):
    for ticker in ticker_list:
        ticker_data_list.append(pd.DataFrame({'Symbol': [ticker]}))

    return ticker_data_list

