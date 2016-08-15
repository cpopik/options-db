'''
FILENAME: optionDownload.py
AUTHOR: Connor T. Popik
DATE: AUG 6, 2015

DESCRIPTION:
Implements the class OptionDownloader which downloads option data for a given
security into a pandas dataframe using the pandas option class.

'''
import pandas as pd
from pandas.io.data import Options
from greeks import Greeks
import datetime
import workdays

class OptionDownloader:
	"""Downloads option data from pandas option class"""
	mu = 0
	rate = .005
	ab_bl = 20

	def __init__(self, tickerString, source = 'yahoo', allData = True):
		self.tickerString = tickerString							# securitiy ticker
		self.source = source										# datasource
		self.pd_option = Options(self.tickerString, self.source)	# pandas option class instance
		self.data = None											# pandas dataframe for caching
		self.allData = allData										# depreciated

	def loadData(self):
		# USE FOR THE ACTUAL DATASET
		# 6 MONTHS OUT IS THE WHEN LIQUIDITY FALLS OFF 

		try:
			dates = self.pd_option.expiry_dates																		# get the expiry dates
		except:
			dates = [datetime.date(2017, 8, 14)]	# add a dummy date	

		if len(dates) > 0:
			# CALLS 
			self.data = self.pd_option.get_call_data(expiry=dates[0]) 		# created init frame
			for x in range(1,len(dates)):
				try:
					df = self.pd_option.get_call_data(expiry=dates[x])		# get forward expiry
					if len(df.index) > 0:
						self.data = self.data.append(df) 																# append data to self.data																								
				except:
					pass
			# PUTS  	
			for x in range(0,len(dates)):
				try:
					df = self.pd_option.get_put_data(expiry=dates[x])		# get forward expiry
					if len(df.index) > 0:
						self.data = self.data.append(df) 																# append data to self.data																								
				except:
					pass
			# NOTICE THE RANGE SWITCH TO FULLY ACCOUNT FOR ALL EXPIRYS ABOVE
			# TODO: FIGURE OUT WHY TRY/EXCEPT IS NEEDED

			# replace the indexing
			self.data.reset_index(inplace=True) 							# fix old indexing used in pandas option class
			self.data.set_index(['Symbol', 'Quote_Time'],inplace=True)		# create custom indexing of symbol and quote time
			
			# reformat the IV column
			self.data['IV_flt'] = self.data.apply (lambda row: self.volToFloat(row),axis=1)

			# drop un-needed columns to save space
			self.data.drop(['IV', 'PctChg', 'IsNonstandard', 'Underlying'], axis=1, inplace=True)

	def volToFloat(self,row):
		v = row['IV'].replace(',','')
		v = float(v[0:len(v)-1])/100
		return v

	def timeDeltaInDays(self, string):
		year = int(string[0:4])
		month = int(string[5:7])
		day = int(string[8:11])
		d1 = datetime.date(year, month, day)

		if datetime.datetime.now().hour > 16:
			r = workdays.networkdays(datetime.date.today(),d1)-1
		else:
			r = workdays.networkdays(datetime.date.today(),d1)

		# FIX THIS DEAL WITH EXPIRY AND DELTA
		if r == 0:
			r = 1

		return r

	def getNumObservations(self):
		if self.data is None:
			self.loadData()
		return len(self.data.index)

	def getNumColumns(self):
		if self.data is None:
			self.loadData()
		return len(self.data.columns)

	def calculateGreeks(self):
		# sometimes load data can't make connection
		if self.data is None:
			try:
				self.loadData()
			except:
				try:
					self.loadData()
				except:
					pass

		if self.data is not None:
			self.data['Delta'] = self.data.apply (lambda row: self.getDeltaColumn(row),axis=1)
			self.data['Gamma'] = self.data.apply (lambda row: self.getGammaColumn(row),axis=1)
			self.data['Theta'] = self.data.apply (lambda row: self.getThetaColumn(row),axis=1)
			self.data['Vega'] = self.data.apply (lambda row: self.getVegaColumn(row),axis=1)
			self.data['DaysToExpiry'] = self.data.apply(lambda row: self.timeDeltaInDays(str(row["Expiry"])),axis=1)

	def getDeltaColumn(self, row):
		#self, s = "null", c = 'null', p = "null", k = "null", r = 'null', mu = 'null', vol = "null", t = 'null')
		g = Greeks(row['Underlying_Price'], 0, 0, row['Strike'], OptionDownloader.rate, OptionDownloader.mu, row['IV_flt'], self.timeDeltaInDays(str(row['Expiry'])))
		if row['Type'] == 'call':
			return g.delta_call()
		else:
			return g.delta_put()

	def getGammaColumn(self, row):
		g = Greeks(row['Underlying_Price'], 0, 0, row['Strike'], OptionDownloader.rate, OptionDownloader.mu, row['IV_flt'], self.timeDeltaInDays(str(row['Expiry'])))	
		return g.gamma()

	def getVegaColumn(self, row):
		g = Greeks(row['Underlying_Price'], 0, 0, row['Strike'], OptionDownloader.rate, OptionDownloader.mu, row['IV_flt'], self.timeDeltaInDays(str(row['Expiry'])))
		return g.vega()

	def getThetaColumn(self, row):
		g = Greeks(row['Underlying_Price'], 0, 0, row['Strike'], OptionDownloader.rate, OptionDownloader.mu, row['IV_flt'], self.timeDeltaInDays(str(row['Expiry'])))	
		return g.theta()

def main():

	d = OptionDownloader("AKAM", allData = True)
	d.calculateGreeks()
	print(d.data['Delta'].tolist())

if __name__ == "__main__":
	main()

