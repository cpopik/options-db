import datetime
from mappingFunctions import *
from scipy.stats import norm
from math import log, sqrt, exp

# class variables
n = norm.pdf
N = norm.cdf

class Options(object):
    '''
    Class keeps track of the yield curve and calculates options
    '''
    # class variables
    n = norm.pdf
    N = norm.cdf

    def __init__(self):
        pass

    def bsVol(self, mid, call_put, S, K, T, r, q):
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5

        sigma = .5
        for i in range(0, MAX_ITERATIONS):
            price = self.bsPrice(call_put, S, K, T, r, sigma, q)
            vega = self.bsVega(call_put, S, K, T, r, sigma, q)
            price = price
            diff = mid - price  # our root

            print(i, sigma, diff)

            if (abs(diff) < PRECISION):
                return sigma
            sigma = sigma + diff/vega # f(x) / f'(x)

        # value wasn't found, return best guess so far
        return sigma

    def bsPrice(self, cp_flag,S,K,T,r,v,q):
        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)
        if cp_flag == 'CALL':
            price = S*exp(-q*T)*N(d1)-K*exp(-r*T)*N(d2)
        else:
            price = K*exp(-r*T)*N(-d2)-S*exp(-q*T)*N(-d1)
        return price

    def bsDelta(self, cp_flag,S,K,T,r,v,q):
        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        if cp_flag == "CALL":
            return N(d1)*exp(-q*T)
        else:
            return (N(d1)-1)*exp(-q*T)

    def bsGamma(self, cp_flag,S,K,T,r,v,q):
        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        return n(d1)*exp(-q*T)/(S*v*sqrt(T))

    def bsTheta(self, cp_flag,S,K,T,r,v,q):
        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)
        if cp_flag == "CALL":
            return -S*n(d1)*v*exp(-q*T)/(2*sqrt(T)) + q*S*N(d1)*exp(-q*T) - r*K*exp(-r*T)*N(d2)
        else:
            return -S*n(d1)*v*exp(-q*T)/(2*sqrt(T)) - q*S*N(-d1)*exp(-q*T) + r*K*exp(-r*T)*N(-d2)

    def bsVega(self, cp_flag,S,K,T,r,v,q):
        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        return S * sqrt(T)*n(d1)*exp(-q*T)

    def bsRho(self, cp_flag,S,K,T,r,v,q):
        d1 = (log(S/K)+(r+v*v/2.0)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)
        if cp_flag == "CALL":
            return K*T*exp(-r*T)*N(d2)
        else:
            return -K*T*exp(-r*T)*N(-d2)

    def daysToExpiry(self, expiry):
        if (expiry - datenum_today()) >= 0:
            return (expiry - datenum_today())
        else:
            return 0


if __name__ == '__main__':
    mid = 2
    K = 585.0
    T = (datetime.date(2014,10,18) - datetime.date(2014,9,8)).days / 365.  # probably need to switch to 252
    S = 586.08
    r = 0.02
    q = 0.01
    cp = 'CALL' # call option

    x = Options()

    implied_vol = x.bsVol(mid, cp, S, K, T, r, q)

    print(implied_vol)
    print(x.bsDelta(cp, S, K, T, r, implied_vol, q))
    print(x.bsGamma(cp, S, K, T, r, implied_vol, q))
    print(x.bsTheta(cp, S, K, T, r, implied_vol, q))
    print(x.bsVega(cp, S, K, T, r, implied_vol, q))
    print(x.bsRho(cp, S, K, T, r, implied_vol, q))
