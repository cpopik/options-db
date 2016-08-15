from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd
import json as json

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
        pass

    def get_last_page(self, ticker):
        # Override the ticker
        self.ticker = ticker

        # Construct the URL
        '''url = http://www.nasdaq.com/symbol/aapl/option-chain?money=all&dateindex=-1'''
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
        # Create an empty pandas.Dataframe object. New data will be appended to
        old_df = pd.DataFrame()
        self.ticker = ticker

        # Variables
        loop = 1        # Loop over webpages starts at 1
        page_nb = 4     # Get the top of the options table
        flag = 1        # Set a flag that will be used to call get_pager()
        old_rows_nb = 0 # Number of rows so far in the table

        # Loop over webpages
        while loop < int(page_nb):
            # Construct the URL
            '''url = http://www.nasdaq.com/symbol/aapl/option-chain?money=all&dateindex=-1'''
            url = 'http://www.nasdaq.com/symbol/' + self.ticker + '/option-chain?money=all&dateindex=-1&page='+str(loop)

            print(url)

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
            if flag == 1:   # It is run only once
                # Get the number of page the option table lies on
                last_page_raw = soup.find('a', {'id': 'quotes_content_left_lb_LastPage'})
                last_page = re.findall(pattern='(?:page=)(\d+)', string=str(last_page_raw))
                page_nb = ''.join(last_page)
                flag = 0

            # Extract table containing the option data from the webpage
            table = soup.find_all('table')[5] # table #4 in the webpage is the one of interest

            # Extract option data from table as a list
            elems = table.find_all('td') # Python object
            lst = [elem.text for elem in elems] # Option data as a readable list

            # Rearrange data and create a pandas.DataFrame
            arrOld = np.array(lst)

            # Remove month headers
            arr = np.array([x for x in arrOld if not (len(x.split(' ')) == 2)])

            # reshape array
            reshaped = arr.reshape((len(arr)/16, 16))
            new_df = pd.DataFrame(reshaped)
            frames = [old_df, new_df]
            old_df = pd.concat(frames)
            rows_nb = old_df.shape[0]

            # Increment loop counter
            if rows_nb > old_rows_nb:
                loop+=1
                old_rows_nb = rows_nb
            elif rows_nb == old_rows_nb:
                print('Problem while catching data.\n## You must try again. ##')
                pass
            else:   # Case where rows have been deleted
                    # which shall never occur
                print('Failure!\n## You must try again. ##')
                pass

        # Name the column 'Strike'
        old_df.rename(columns={old_df.columns[8]:'Strike'}, inplace=True)
        # Remove extraneous tickers
        old_df = old_df[old_df.ix[:,7] == self.ticker]

        ## Split into 2 dataframes (1 for calls and 1 for puts)
        calls = old_df.ix[:,0:7]
        puts = old_df.ix[:,9:16] # Slicing is not incluse of the last column

        # Set 'Strike' column as dataframe index
        calls = calls.set_index(old_df['Strike'])
        puts = puts.set_index(old_df['Strike'])

        ## Headers names
        headers = ['Date', 'Last', 'Chg', 'Bid', 'Ask', 'Vol', 'OI']
        calls.columns = headers
        puts.columns = headers

        return calls, puts

if __name__ == '__main__':
    options = NasdaqOptions()
    open_file = open('ticker_list.txt', 'r+')
    ticker_list = json.loads(open_file.read())
    open_file.close()
    
    for ticker in ticker_list:
        calls, puts = options.get_options_table(ticker)

#    calls.to_csv('calls_test.csv')
#    puts.to_csv('puts_test.csv')

    print(options.get_last_page('AAPL'))
