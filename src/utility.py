import sys
import os



def searchFile(name):
	absPathEnvFile = ''
	
	for (root,dirs,files) in os.walk(os.getcwd(), topdown=True):
		#print (root)
		# print (dirs)
		#print (files)
		# print ('--------------------------------')
		if name in files:
			absPathEnvFile = root + "/" + name
			#print('Match')
			break

	print('ABSFILE: {0}'.format(absPathEnvFile))	
	return absPathEnvFile
   

