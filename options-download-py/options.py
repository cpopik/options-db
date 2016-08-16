import datetime
import numpy as np
import pandas as pd

from functions import *
from scipy.stats import norm
from scipy.interpolate import interp1d
from math import log, sqrt, exp
from yahoo_finance import Share

# global variables
n = norm.pdf
N = norm.cdf
DAY_COUNT = float(360) # maybe need to switch to 252. keep float in here!!
START_VOL = .25
MAX_ITERATIONS = 25
PRECISION = 1.0e-3

# functions
def getYieldCurve():
    # generate a yield curve interpolation to use in pricing options which persists with the instance
    yieldPoints = [0, Share('^IRX').get_price(), Share('^FVX').get_price(), Share('^TNX').get_price(), Share('^TYX').get_price()]
    yieldPoints = [float(x)/100 for x in yieldPoints]
    yieldDays = [0 ,13*7, 5*360, 10*360, 30*360] # 13 week, 5 year, 10 year, 30 year assuming 360 day count

    nRange = np.linspace(0, 800, 800)
    f2 = interp1d(yieldDays, yieldPoints, kind='linear') # convieniently indexed by days

    return f2(nRange)

def bsVol(row, yields):
    if not(pd.isnull(row['bid'])) and not (pd.isnull(row['ask'])):
        mid = (float(row['bid']) + float(row['ask']))/2
        cp_flag = row['type']
        S = float(row['underlying'])
        K = float(row['strike'])
        T = daysToExpiry(row['expiry'])/DAY_COUNT
        q = divYield(row['ticker'])
        v = START_VOL
        r = yields[int(DAY_COUNT*T)]

        for i in range(0, MAX_ITERATIONS):
            d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
            d2 = d1-v*sqrt(T)
            if cp_flag == 'CALL':
                price = S*exp(-q*T)*N(d1)-K*exp(-r*T)*N(d2)
            else:
                price = K*exp(-r*T)*N(-d2)-S*exp(-q*T)*N(-d1)
            vega = S*sqrt(T)*n(d1)*exp(-q*T)
            diff = mid - price  # our root

            if (abs(diff) < PRECISION):
                return v
            v = v + diff/vega # f(x) / f'(x)
        # value wasn't found, return best guess so far
        return v
    else:
        return None

def bsDelta(row, yields):
    if not(pd.isnull(row['bid'])) and not (pd.isnull(row['ask'])):
        mid = (float(row['bid']) + float(row['ask']))/2
        cp_flag = row['type']
        S = float(row['underlying'])
        K = float(row['strike'])
        T = daysToExpiry(row['expiry'])/DAY_COUNT
        q = divYield(row['ticker'])
        v = row['bsVol']
        r = yields[int(DAY_COUNT*T)]

        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))

        if cp_flag == "CALL":
            return N(d1)*exp(-q*T)
        else:
            return (N(d1)-1)*exp(-q*T)
    else:
        return None

def bsGamma(row, yields):
    if not(pd.isnull(row['bid'])) and not (pd.isnull(row['ask'])):
        mid = (float(row['bid']) + float(row['ask']))/2
        cp_flag = row['type']
        S = float(row['underlying'])
        K = float(row['strike'])
        T = daysToExpiry(row['expiry'])/DAY_COUNT
        q = divYield(row['ticker'])
        v = row['bsVol']
        r = yields[int(DAY_COUNT*T)]

        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))

        return n(d1)*exp(-q*T)/(S*v*sqrt(T))
    else:
        return None

def bsTheta(row, yields):
    if not(pd.isnull(row['bid'])) and not (pd.isnull(row['ask'])):
        mid = (float(row['bid']) + float(row['ask']))/2
        cp_flag = row['type']
        S = float(row['underlying'])
        K = float(row['strike'])
        T = daysToExpiry(row['expiry'])/DAY_COUNT
        q = divYield(row['ticker'])
        v = row['bsVol']
        r = yields[int(DAY_COUNT*T)]

        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)

        if cp_flag == "CALL":
            return -S*n(d1)*v*exp(-q*T)/(2*sqrt(T)) + q*S*N(d1)*exp(-q*T) - r*K*exp(-r*T)*N(d2)
        else:
            return -S*n(d1)*v*exp(-q*T)/(2*sqrt(T)) - q*S*N(-d1)*exp(-q*T) + r*K*exp(-r*T)*N(-d2)
    else:
        return None

def bsVega(row, yields):
    if not(pd.isnull(row['bid'])) and not (pd.isnull(row['ask'])):
        mid = (float(row['bid']) + float(row['ask']))/2
        cp_flag = row['type']
        S = float(row['underlying'])
        K = float(row['strike'])
        T = daysToExpiry(row['expiry'])/DAY_COUNT
        q = divYield(row['ticker'])
        v = row['bsVol']
        r = yields[int(DAY_COUNT*T)]

        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))

        return S*sqrt(T)*n(d1)*exp(-q*T)
    else:
        return None

def bsRho(row, yields):
    if not(pd.isnull(row['bid'])) and not (pd.isnull(row['ask'])):
        mid = (float(row['bid']) + float(row['ask']))/2
        cp_flag = row['type']
        S = float(row['underlying'])
        K = float(row['strike'])
        T = daysToExpiry(row['expiry'])/DAY_COUNT
        q = divYield(row['ticker'])
        v = row['bsVol']
        r = yields[int(DAY_COUNT*T)]

        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)

        if cp_flag == "CALL":
            return K*T*exp(-r*T)*N(d2)
        else:
            return -K*T*exp(-r*T)*N(-d2)
    else:
        return None

def daysToExpiry(expiry):
    if (expiry - datenum_today()) >= 0:
        return (expiry - datenum_today())
    else:
        return 0

def divYield(ticker):
    return float(Share(ticker).get_dividend_yield())/100

# main thread
def main():
    mid = 0.52
    K = 110.0
    T = (datetime.date(2016,8,19) - datetime.date(2016,8,15)).days / DAY_COUNT
    S = 109.48
    q = 0.00
    cp = 'CALL' # call option

    yields = getYieldCurve()
    row = {'bid': 0.52, 'ask': 0.52, 'type': 'CALL', 'strike': K, 'underlying': S, 'expiry': 736565, 'ticker': 'AAPL', 'bsVol': 0.12}

    y = bsVol(row, yields)
    print(y)

if __name__ == '__main__':
    main()
