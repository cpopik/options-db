from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd

class NasdaqOptions(object):
    '''
    Class NasdaqOptions fetches options data from Nasdaq website

    User inputs:
        Ticker: ticker
            - Ticker for the underlying
        Page: page
            - Page of the underlying chain
    '''
    def __init__(self):
        '''
        - Initializes the NasdaqOptions instance
        '''
        pass

    def get_last_page(self, ticker):
        '''
        - Determine the last option chain page for a specific ticker
        - Return an int object
        '''
        # Override the ticker
        self.ticker = ticker

        # Construct the URL
        url = 'http://www.nasdaq.com/symbol/' + self.ticker + '/option-chain?money=all&dateindex=-1&page=1'

        # Query NASDAQ website
        try:
            response = requests.get(url)#, timeout=0.1)
        # DNS lookup failure
        except requests.exceptions.ConnectionError as e:
            print('''Webpage doesn't seem to exist!\n%s''' % e)
            pass
        # Timeout failure
        except requests.exceptions.ConnectTimeout as e:
            print('''Slow connection!\n%s''' % e)
            pass
        # HTTP error
        except requests.exceptions.HTTPError as e:
            print('''HTTP error!\n%s''' % e)
            pass

        # Get webpage content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Determine actual number of pages to loop over
        # Get the number of page the option table lies on
        last_page_raw = soup.find('a', {'id': 'quotes_content_left_lb_LastPage'})
        last_page = re.findall(pattern='(?:page=)(\d+)', string=str(last_page_raw))
        page_nb = ''.join(last_page)
        return int(page_nb)

    def get_options_page(self, ticker, page):
        '''
        - Download chain for a specific ticker from a specific page
        - Return a pandas.DataFrame() object
        '''
        # Override the ticker
        self.ticker = ticker
        # Construct the URL
        url = 'http://www.nasdaq.com/symbol/' + self.ticker + '/option-chain?money=all&dateindex=-1&page='+str(page)

        # Query NASDAQ website
        try:
            response = requests.get(url)#, timeout=0.1)
        # DNS lookup failure
        except requests.exceptions.ConnectionError as e:
            print('''Webpage doesn't seem to exist!\n%s''' % e)
            pass
        # Timeout failure
        except requests.exceptions.ConnectTimeout as e:
            print('''Slow connection!\n%s''' % e)
            pass
        # HTTP error
        except requests.exceptions.HTTPError as e:
            print('''HTTP error!\n%s''' % e)
            pass

        # Get webpage content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract table containing the option data from the webpage
        table = soup.find_all('table')[5] # table #5 in the webpage is the one of interest

        # Extract option data from table as a list
        elems = table.find_all('td') # Python object
        lst = [elem.text for elem in elems] # Option data as a readable list

        # Rearrange data and create a pandas.DataFrame
        arrOld = np.array(lst)

        # Remove month headers
        arr = np.array([x for x in arrOld if not (len(x.split(' ')) == 2)])

        # reshape array
        reshaped = arr.reshape((len(arr)/16, 16))
        df = pd.DataFrame(reshaped)

        # Name the column 'Strike'
        df.rename(columns={df.columns[8]:'Strike'}, inplace=True)
        # Remove extraneous tickers
        df = df[df.ix[:,7] == self.ticker]

        ## Split into 2 dataframes (1 for calls and 1 for puts)
        calls = df.ix[:,0:7]
        puts = df.ix[:,9:16] # Slicing is not incluse of the last column

        # Set 'Strike' column as dataframe index
        calls = calls.set_index(df['Strike'])
        puts = puts.set_index(df['Strike'])

        ## Headers names
        headers = ['Date', 'Last', 'Chg', 'Bid', 'Ask', 'Vol', 'OI']
        calls.columns = headers
        puts.columns = headers

        return calls, puts

if __name__ == '__main__':
    options = NasdaqOptions()

    print(options.get_options_page('AAPL',1))
