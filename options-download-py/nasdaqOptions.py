# standard requirements
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd

# date conversion
from mappingFunctions import *
import time

# custom classes
from options import Options

# disable false positive warning
pd.options.mode.chained_assignment = None  # default='warn'

class NasdaqOptions(object):
    '''
    Class NasdaqOptions fetches options data from Nasdaq website

    User inputs:
        Ticker: ticker
            - Ticker for the underlying
        Page: page
            - Page of the underlying chain
    '''

    # global vars
    columns = ['date','ticker','underlying','contract','type','strike','expiry','last','bid','ask','volume','openInterest']

    def __init__(self):
        '''
        - Initializes the NasdaqOptions instance
        '''
        self.timer = []
        self.optionsCalc = Options()

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
        return ticker, int(page_nb)

    def get_options_page(self, ticker, page):
        '''
        - Download chain for a specific ticker from a specific page
        - Return a pandas.DataFrame() object
        '''
        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##

        # Override the ticker
        self.ticker = ticker
        # Construct the URL
        url = 'http://www.nasdaq.com/symbol/' + self.ticker + '/option-chain?&dateindex=-1&page='+str(page)

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

        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##

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
        reshaped = arr.reshape((int(len(arr)/16), 16))
        df = pd.DataFrame(reshaped)

        # Remove extraneous tickers
        df = df[df.ix[:,7] == self.ticker]

        ## Split into 2 dataframes (1 for calls and 1 for puts)
        calls = df.ix[:,0:8]
        puts = df.ix[:,8:16] # Slicing is not incluse of the last column

        ## Headers names
        calls.columns = ['expiry-pd', 'last', 'chg', 'bid', 'ask', 'volume', 'openInterest','ticker', 'strike']
        puts.columns = ['strike', 'expiry-pd', 'last', 'chg', 'bid', 'ask', 'volume', 'openInterest']

        # Set 'Strike' column as dataframe index
        calls['type'] = 'CALL'
        puts['type'] = 'PUT'

        # Join calls and puts dfs
        output = pd.concat([calls, puts])

        # Change to numeric
        output['strike'] = pd.to_numeric(output['strike'])

        # expiry in matlab format
        output['expiry-pd'] = pd.to_datetime(output['expiry-pd'])
        output['unix_time'] = output['expiry-pd'].map(py_to_unix)
        output['expiry'] = output['expiry-pd'].map(py_to_mat)

        # adding additional columns
        output['ticker'] = self.ticker
        output['date'] = datenum_today()
        output['underlying'] = float(str(soup.find('div', {'id': 'qwidget_lastsale'})).split('$')[1].split('<')[0]) # find the stock price

        # generating contract name
        output['contract_time'] = output['unix_time'].map(generate_contract_time)
        output['contract_type'] = output['type'].map(first_character)
        output['contract_strike'] = output['strike']*1000
        output['contract_strike'] = output['contract_strike'].astype('int')
        output['contract_strike'] = output['contract_strike'].astype('str')
        output['contract_strike'] = output['contract_strike'].apply(lambda x: x.zfill(8))
        output['contract'] = output['ticker'] + output['contract_time'] + output['contract_type'] + output['contract_strike']

        # keep only columns we need
        output = output[NasdaqOptions.columns]

        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##

        # calculating greeks
        output = output.replace(r'\s+( +\.)|#',np.nan,regex=True).replace('',np.nan)
        output['bsVol'] = output.apply(lambda row: self.optionsCalc.bsVol(row), axis=1)

        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##
        output['bsDelta'] = output.apply(lambda row: self.optionsCalc.bsDelta(row), axis=1)
        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##
        output['bsGamma'] = output.apply(lambda row: self.optionsCalc.bsGamma(row), axis=1)
        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##
        output['bsTheta'] = output.apply(lambda row: self.optionsCalc.bsTheta(row), axis=1)
        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##
        output['bsVega'] = output.apply(lambda row: self.optionsCalc.bsVega(row), axis=1)
        ## --------------------------- ##
        self.timer.append(time.time())
        ## --------------------------- ##

        return output

if __name__ == '__main__':
    options = NasdaqOptions()
    x = options.get_options_page('AAPL',1)
    print('\nPage load: ', options.timer[1]-options.timer[0])
    print('Data prep: ', options.timer[2]-options.timer[1])
    print('Vol prep: ', options.timer[3]-options.timer[2])
    print('Delta prep: ', options.timer[4]-options.timer[3])
    print('Gamma prep: ', options.timer[5]-options.timer[4])
    print('Theta prep: ', options.timer[6]-options.timer[5])
    print('Vega prep: ', options.timer[7]-options.timer[6])
    print('Total: ', options.timer[7]-options.timer[0])
    print("\n")
