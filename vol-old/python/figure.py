'''
FILENAME: figures.py
AUTHOR: Connor T. Popik
DATE: AUG 6, 2015

DESCRIPTION:
Handling of figure creation with data from mysql db.
'''

import pandas as pd
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
from sqlConn import SqlConn
import mpld3
plt.style.use('ggplot')


class Figure():
	"""Handling of figure creation with data from mysql db."""
	def __init__(self):
		# using pymysql since MySQLdb wouldn't download
		self.db = SqlConn()

	def graphSurfaceForDate(self, ticker, date, surfaceVariable, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False, bubble = False):
		df = self.db.returnFrameForDate(ticker, date, calls, puts)

		# daily breakeven calculation
		if surfaceVariable == 'DailyBreakeven':
			df['DailyBreakeven'] = -df['Theta']*2/df['Gamma']
			df['DailyBreakeven'] = df['DailyBreakeven'].apply(np.sqrt)/df["Underlying_Price"]

		if calls:
			df['Moneyness'] = df['Underlying_Price']/df['Strike']
		else:
			df['Moneyness'] = df['Strike']/df['Underlying_Price']

		df = df[df['Moneyness'] <= maxITM] 				# drop way ITM and OTM 
		df = df[df['Moneyness'] >= maxOTM]
		df = df[df['DaysToExpiry'] < maxTenor] 				# drop illiquid options

		x = df['Strike']
		y = df['DaysToExpiry']
		z = df[surfaceVariable]

		if not bubble:
			# setting labels
			f = plt.figure()
			surface = f.gca(projection='3d')
			if byStrike:
				x = df['Strike']	
				surface.set_xlabel('Strike')				# BY STRIKE
			else:
				x = df['Moneyness']
				surface.set_xlabel('Moneyness')
			surface.set_ylabel('Tenor')
			surface.set_zlabel(surfaceVariable)
			surface.plot_trisurf(x, y, z, cmap=cm.brg, linewidth=0.1)
		else:
			f = plt.figure()
			surface = f.gca()
			surface.set_xlabel('Strike')
			surface.set_ylabel('Tenor')
			surface.scatter(x, y, s = z*1000/max(z.tolist()), alpha = .5)

			surface.axvline(df['Underlying_Price'].tolist()[0],color='r',linewidth=1)

		# setting the title
		if calls:
			optionType = "Calls"
		elif puts:
			optionType = "Puts"
		else:
			optionType = "Calls and Puts"
		plt.title(ticker.upper() + ": " + surfaceVariable +' of ' + optionType, y=1.03)

		# showing the plot
		return f

	def volSurface(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False):
		return self.graphSurfaceForDate(ticker, date, 'IV_flt', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike)
	
	def deltaSurface(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False):
		return self.graphSurfaceForDate(ticker, date, 'Delta', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike)
	
	def gammaSurface(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False):
		return self.graphSurfaceForDate(ticker, date, 'Gamma', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike)
	
	def vegaSurface(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False):
		return self.graphSurfaceForDate(ticker, date, 'Vega', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike)

	def thetaSurface(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False):
		return self.graphSurfaceForDate(ticker, date, 'Theta', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike)

	def dailyBreakeven(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False):
		return self.graphSurfaceForDate(ticker, date, 'DailyBreakeven', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike)

	def openInterestBubble(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False, bubble=True):
		return self.graphSurfaceForDate(ticker, date, 'Open_Int', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike, bubble=bubble)
	
	def volumeBubble(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False, bubble=True):
		return self.graphSurfaceForDate(ticker, date, 'Vol', calls = calls, puts = puts, maxTenor = maxTenor, maxITM = maxITM, maxOTM = maxOTM, byStrike = byStrike, bubble=bubble)

	def volChange(self, ticker, date, calls = True, puts = False, maxTenor = 120, maxITM = 1.25, maxOTM = .75, byStrike = False, bubble=True):
		df_current = self.db.returnFrameForDate(ticker, date, calls, puts)
		df_old = self.db.returnFrameForDate(ticker, '8/8/15', calls, puts)

		df = pd.merge(df_current.reset_index(), df_old.reset_index(), how='inner', on=['Symbol'], suffixes=('_old', '_new'))

		if calls:
			df['Moneyness'] = df['Underlying_Price_new']/df['Strike_new']
		else:
			df['Moneyness'] = df['Strike_new']/df['Underlying_Price_new']

		df = df[df['Moneyness'] <= maxITM] 				# drop way ITM and OTM 
		df = df[df['Moneyness'] >= maxOTM]
		df = df[df['DaysToExpiry_new'] < maxTenor] 				# drop illiquid options

		x = df['Moneyness']
		y = df['DaysToExpiry_new']
		z = df['IV_flt_new']-df['IV_flt_old']

		# setting labels
		f = plt.figure()
		surface = f.gca(projection='3d')
		if byStrike:
			x = df['Strike']	
			surface.set_xlabel('Strike')				# BY STRIKE
		else:
			x = df['Moneyness']
			surface.set_xlabel('Moneyness')
		surface.set_ylabel('Tenor')
		surface.set_zlabel('Vol Change')
		surface.plot_trisurf(x, y, z, cmap=cm.brg, linewidth=0.1)

		# setting the title
		if calls:
			optionType = "Calls"
		elif puts:
			optionType = "Puts"
		else:
			optionType = "Calls and Puts"
		plt.title(ticker.upper() + ": " + 'Vol Change' +' of ' + optionType, y=1.03)

		# showing the plot
		return f



def main():

	fx = Figure()
	#db.uploadDataFromClose()
	f = fx.volSurface('AAPL', '8/14/2015')
	plt.show()	

# MAIN RUNTIME
if __name__ == "__main__":
	main()


