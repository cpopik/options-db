'''
FILENAME: greeks.py
AUTHOR: Connor T. Popik
DATE: AUG 6, 2015

DESCRIPTION:
Implements the class Greeks which returns pricing for puts and class along with
the greeks associated with the class (delta, gamma, theta, vega) for a given vol
and option

'''
import scipy.stats
import math

class Greeks():
	"""Prices options and greeks"""

	tradingDays = 252

	# NORMAL AND CUMULATIVE DISTRIBUTIONS
	@classmethod
	def N(Greeks, x):
		return scipy.stats.norm(0, 1).cdf(x)
	@classmethod
	def NPrime(Greeks, x):
		return scipy.stats.norm(0, 1).pdf(x)

	def __init__(self, s = 1, c = 1, p = 1, k = 1, r = 1, mu = 1, vol = 1, t = 1):
		self.s = s 								# spot price
		self.c = c 								# call price
		self.p = p 								# put price
		self.k = k								# strike price
		self.r = r								# risk free rate
		self.mu = mu							# drift
		self.vol = vol							# volatility
		self.t = t/Greeks.tradingDays		# time in years

		if self.vol != 0:
			self.d1 = 1/(self.vol*math.sqrt(self.t))*(math.log(self.s/self.k) + (self.r + self.vol**2/2)*self.t) 	# d1 parameter for normal distribution
			self.d2 = 1/(self.vol*math.sqrt(self.t))*(math.log(self.s/self.k) + (self.r - self.vol**2/2)*self.t)	# d2 parameter for normal distribution

	def refresh(self):
		#variables
		if self.vol != 0:
			self.d1 = 1/(self.vol*math.sqrt(self.t))*(math.log(self.s/self.k) + (self.r + self.vol**2/2)*self.t) 	# d1 parameter for normal distribution
			self.d2 = 1/(self.vol*math.sqrt(self.t))*(math.log(self.s/self.k) + (self.r - self.vol**2/2)*self.t)	# d2 parameter for normal distribution


	# PRICING
	def price_call(self):
		if self.vol != 0:
			self.refresh()
			return Greeks.N(self.d1)*self.s - Greeks.N(self.d2)*self.k*math.exp(-self.r*self.t)
		else:
			return None
	def price_put(self):
		if self.vol != 0:
			self.refresh()
			return self.k*math.exp(-self.r*self.t) - self.s + self.price_call()
		else:
			return None

	# Greeks
	def delta_call(self):
		if self.vol != 0:
			self.refresh()
			return Greeks.N(self.d1)
		else:
			return None
	def delta_put(self):
		if self.vol != 0:
			self.refresh()
			return Greeks.N(self.d1)-1
		else:
			return None
	def gamma(self):
		if self.vol != 0:
			self.refresh()
			return Greeks.NPrime(self.d1)/(self.s*self.vol*math.sqrt(self.t))
		else:
			return None
	def vega(self):
		if self.vol != 0:
			self.refresh()
			return Greeks.NPrime(self.d1)*(self.s*math.sqrt(self.t))/100
		else:
			return None
	def theta(self):
		if self.vol != 0:
			self.refresh()
			return (-Greeks.NPrime(self.d1)*self.s*self.vol/(2*math.sqrt(self.t)) - self.r*self.k*math.exp(-self.r*self.t)*Greeks.N(self.d2))/252
		else:
			return None

def test():

	call = Greeks(115.52, 1, 1.15, 120, .005, 0, .81, 5)
	print(call.delta_call())

if __name__ == "__main__":
	test()

