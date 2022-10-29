import os
import sys
from utility import searchFile

#sys.path .insert(1, './src/')

envFileName = ".environment" 

def getEnvKey(key):
	token = ""

	fd = open(searchFile(envFileName), "r")
	
	while (line := fd.readline()):
		if line.startswith("{0}=".format(key)):
			token = line.split("{0}=".format(key), 1)[1].strip()
			break

	fd.close()
	return token

if __name__ == '__main__':
	print(getEnvKey('TOKEN'))
	print(getEnvKey('TEST_BOT_TOKEN'))

