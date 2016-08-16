# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 15:51:19 2016

@author: Mitchel Myers
"""
import nasdaqOptions as Nasdaq
import json as json

if __name__ == '__main__':
    options = Nasdaq.NasdaqOptions()
    open_file = open('ticker_list.txt', 'r+')
    ticker_list = json.loads(open_file.read())
    open_file.close()
    
    for ticker in ticker_list:
        calls, puts = options.get_options_table(ticker)

#    calls.to_csv('calls_test.csv')
#    puts.to_csv('puts_test.csv')

    print(options.get_last_page('AAPL'))