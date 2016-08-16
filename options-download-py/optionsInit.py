# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 15:51:19 2016

@author: Mitchel Myers
"""
from nasdaqOptions import *
import json as json
import Queue
import threading

def getLastPage(q, ticker):
    print ticker
    q.put(getLastPage(ticker))

def urlBuilder(ticker, last_page):
    global visit_count
    url_dict[ticker] = []
    for page in range(1, last_page+1):
        visit_count += 1
        url_dict[ticker].append('http://www.nasdaq.com/symbol/' + ticker + '/option-chain?money=all&dateindex=-1&page='+str(page))

def getTickerPage(q, ticker, page):
    downloadOptionsPage(ticker, page)

if __name__ == '__main__':
    """ Read the relevant tickers from the ticker_list text file """
    open_file = open('ticker_list.txt', 'r+')
    ticker_list = json.loads(open_file.read())
    open_file.close()

    tickerQueue = Queue.Queue()
    queueLock = threading.Lock()

    """ Retrieve the last page for each ticker """
    for ticker in ticker_list:
        thread = threading.Thread(target = getLastPage, args = (tickerQueue, ticker))
        thread.setName(ticker)
        thread.daemon = True
        thread.start()

    thread_handled_count = 0
    ticker_page_dict = {}

    """ Build a dictionary mapping a ticker to its last page """
    while thread_handled_count < len(ticker_list):
        current_ticker, current_last_page = tickerQueue.get()
        ticker_page_dict[current_ticker] = current_last_page
        thread_handled_count += 1

    visit_count_expected = 0
    visit_count = 0
    url_dict = {}
    threads = []

    """ Iterate over the tickers and use the previously made dictionary to build the URLs for a ticker """
    for ticker in ticker_list:
        visit_count_expected += ticker_page_dict[ticker]
        thread = threading.Thread(target = urlBuilder, args = (ticker, ticker_page_dict[ticker]))
        threads.append(thread)
        thread.daemon = True
        thread.start()

    """ Wait for URLs to be built """
    for thread in threads:
        thread.join()

    """ Iterate over the tickers """
    for ticker in ticker_list:
        page_threads = []

        """ Iterate over the URLs for the pages of a given ticker """
        for page in url_dict[ticker]:
            """ Retrieve web page info for a given ticker, assumes that
                the downloadOptionsPage() method will dump to SQL """
            thread = threading.Thread(target = getTickerPage, args = (ticker, page))
            page_threads.append(thread)
            thread.daemon = True
            thread.start()

        """ Throttle the process by waiting until a given tickers' threads are done """
        for page_thread in page_threads:
            page_thread.join()

#    print url_dict
#    print len(url_dict['AAPL'])
#    print len(url_dict['NLY'])

#    print(getLastPage('AAPL'))
