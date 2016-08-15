import pandas as pd
import numpy as np
import time
import datetime

# CURRENTLY USING UTC, MAY NEED TO CHANGE

def py_to_mat(dateObject):
    unix_time = dateObject.value/10**9
    datenum = int(unix_time/86400 + 719529)
    return datenum

def py_to_unix(dateObject):
    unix_time = dateObject.value/10**9
    return unix_time

def generate_contract_time(unix_time):
    out = datetime.datetime.fromtimestamp(int(unix_time)).strftime("%y%m%d")
    return out

def datenum_today():
    out = int(int(time.time())/86400 + 719529)
    return out

def first_character(x):
    return x[0]

def format_strike(x):
    x = x*1000
    xLen = len(str(x))
    return (8-xLen)*"0" + str(x)

if __name__ == "__main__":
    print(format_strike(10))
