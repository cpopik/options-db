import time
import datetime

# CURRENTLY USING UTC, MAY NEED TO CHANGE
EST_CONVERSION = 60*60*6

def py_to_mat(dateObject):
    unix_time = dateObject.value/10**9
    datenum = int((unix_time+EST_CONVERSION)/86400 + 719529)
    return datenum

def mat_to_py(mat):
    unix = 86400*(mat - 719529)-EST_CONVERSION
    return datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')

def py_to_unix(dateObject):
    unix_time = dateObject.value/10**9
    return unix_time + EST_CONVERSION

def generate_contract_time(unix_time):
    out = datetime.datetime.fromtimestamp(int(unix_time+EST_CONVERSION)).strftime("%y%m%d")
    return out

def datenum_today():
    out = int(int(time.time()+EST_CONVERSION)/86400 + 719529)
    return out

def first_character(x):
    return x[0]

if __name__ == "__main__":
    print(mat_to_py(736558))
