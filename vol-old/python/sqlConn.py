'''
FILENAME: sql.py
AUTHOR: Connor T. Popik
DATE: AUG 6, 2015

DESCRIPTION:
Implements MySQL handling of the data into the database.

'''

import pandas as pd
import pymysql			# NEED TO SWITCH --> may be depreciated
import location
import datetime
from dateutil.parser import parse
from optionDownloader import *

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
plt.style.use('ggplot')


class SqlConn():
	"""Class that links to mysql db for upload and download"""

	# CONNECTION INFO FOR DB
	host = 'derivs.xyz'
	port = 3306
	user = 'admin'
	passwd = 'servire87'
	db = 'derivs'

	def __init__(self):
		# using pymysql since MySQLdb wouldn't download
		self.conn = pymysql.connect(host=SqlConn.host, port=SqlConn.port, user=SqlConn.user, passwd=SqlConn.passwd, db=SqlConn.db)

	def uploadDataFromClose(self, getAllData=True):
		for ticker in self.getTickerList():
			d = OptionDownloader(ticker.upper(), allData = getAllData)
			d.calculateGreeks()

			if d.data is not None:
				# to_sql(name, con, flavor='sqlite', schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None)
				d.data.to_sql('$'+ticker.replace('-','').lower(), self.conn, flavor='mysql', schema=SqlConn.db, if_exists='append', index=True, index_label=['Symbol','QuoteTime'])
				print(ticker, ": Done")
			else:
				print(ticker, ": Error")

	def getTickerList(self):
		filePath = location.getParentDirectory() + 'tickerList.csv'
		df = pd.read_csv(filePath)
		tickerList = df['Ticker'].tolist()
		return tickerList

	def returnFrameForDate(self, ticker, date, calls = True, puts = False):  # date can take datetime type
		# read_sql_query(sql, con, index_col=None, coerce_float=True, params=None, parse_dates=None, chunksize=None)

		# create the correct datestring for the query
		if isinstance(date, datetime.date):
			dateString = date.isoformat()
		elif isinstance(date, str):
			dateString = parse(date).date().isoformat()

		sqlQuery = "select * from `derivs`.$"+ticker.lower()+" where QuoteTime between '"+dateString+" 00:00:00' AND '"+dateString+" 23:59:59' "

		# add the calls or puts only
		if calls and not puts:
			sqlQuery += "and $"+ticker.lower()+".Type = 'call'"
		elif puts and not calls:
			sqlQuery += "and $"+ticker.lower()+".Type = 'put'"
		elif puts and calls:
			sqlQuery += ''
		else:
			sqlQuery += "and $"+ticker.lower()+".Type <> 'call' and $"+ticker.lower()+".Type <> 'put'"

		# get the frame
		df = pd.read_sql_query(sqlQuery, self.conn, index_col=['Symbol'], coerce_float=True, params=None, parse_dates=None, chunksize=None)
		return df

def main():
	db = SqlConn()
	db.uploadDataFromClose()

# MAIN RUNTIME
if __name__ == "__main__":
	main()


