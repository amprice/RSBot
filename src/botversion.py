import os.path
from utility import searchFile

githashFilename = '.githash'

SW_ID = "V0.1"

def getGitHash():
    #print("in getGitHash()")
    absFile = searchFile(githashFilename)
    if os.path.isfile(absFile):
        #print("Found GitHash")
        fd = open(absFile, "r")
        gitHash = fd.readline()
        fd.close()
        return gitHash
    else:
        #print("File .githash Not Found!")
        return ""

def getVersion():
    hash = getGitHash();
    if hash != '':
        version = "{0}-{1}".format(SW_ID, hash)
    else:
        version = SW_ID

    return version

if __name__ == '__main__':
    print(getVersion())
