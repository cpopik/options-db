'''
FILENAME: location.py
AUTHOR: Connor T. Popik
DATE: AUG 6, 2015

DESCRIPTION:
Implements a location funciton that returns the parent directory of the location
where the file is located. 

'''

import os

def getParentDirectory():
	pathToPython = os.getcwd()
	pathList = pathToPython.split('/')
	parentDirectory = "/".join(pathList[0:len(pathList)-1]) + '/'

	return parentDirectory
