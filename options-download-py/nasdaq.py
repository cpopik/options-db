# standard requirements
import requests
import re
import numpy as np
import pandas as pd
import pymysql
import threading
from bs4 import BeautifulSoup

# date conversion
from functions import *
import time

# custom classes
from options import *

# disable false positive warning
pd.options.mode.chained_assignment = None  # default='warn'

# global vars
columns = ['date','ticker','underlying','contract','type','strike','expiry','last','bid','ask','volume','openInterest']
host = 'derivs.xyz'
port = 3306
user = 'admin'
passwd = 'servire87'
db = 'options-prod'

# set up SQL connection
conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)

def getLastPage(ticker):
    '''
    - Determine the last option chain page for a specific ticker
    - Return an int object
    '''

    # Construct the URL
    url = 'http://www.nasdaq.com/symbol/' + ticker + '/option-chain?dateindex=-1&page=1'

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

    try:
        page = int(page_nb)
    except:
        page = 1

    return ticker, page

def downloadOptionsPage(ticker, url):
    '''
    - Download chain for a specific ticker from a specific page
    - Return a pandas.DataFrame() object
    '''
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
    reshaped = arr.reshape((int(len(arr)/16), 16))
    df = pd.DataFrame(reshaped)

    # Remove extraneous tickers
    df = df[df.ix[:,7] == ticker]

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
    output['ticker'] = ticker
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

    # keep only columns we need and replace empty
    output = output[columns]
    output = output.replace(r'\s+( +\.)|#',np.nan,regex=True).replace('',np.nan)

    # add unique key
    output['recordID'] = output['date'].map(str) + output['contract']
    output = output.set_index('recordID')

    # calculate greeks
    yields = getYieldCurve()
    output['bsVol'] = output.apply(lambda row: bsVol(row, yields), axis=1)
    output['bsDelta'] = output.apply(lambda row: bsDelta(row, yields), axis=1)
    output['bsGamma'] = output.apply(lambda row: bsGamma(row, yields), axis=1)
    output['bsTheta'] = output.apply(lambda row: bsTheta(row, yields), axis=1)
    output['bsVega'] = output.apply(lambda row: bsVega(row, yields), axis=1)

    return output

def uploadToSQL(ticker, output):
    # upload to SQL database
    #try:
    output.to_sql('$'+ticker.replace('-','').upper(), conn, flavor='mysql', schema=db, if_exists='append', index=True)
    return 1
    #except:
    #    return 0

if __name__ == '__main__':
    x = getLastPage("NLY")
    print(x)
