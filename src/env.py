import os

token = ""

def getToken():
	fd = open(".env", "r")

	#count = 0
	for line in fd:
		#count += 1
		#print("{0}: {1}".format(count, line.strip()))
		if line.startswith('TOKEN='):
			#print("FOUND")
			token = line.split("TOKEN=", 1)[1]
	fd.close()

	return token

if __name__ == '__main__':
    print(getToken())

