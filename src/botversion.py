import os.path
from queue import Empty

SW_ID = "V0.1"

def getGitHash():
    if os.path.isfile('.githash'):
        # print("Found GitHash")
        fd = open(".githash", "r")
        gitHash = fd.readline()
        # print ("GitHash: {0}".format(gitHash))
        fd.close()
        return gitHash
    else:
        # print("File .githash Not Found!")
        return ""

def getVersion():
    hash = getGitHash();
    if hash is not Empty:
        version = "{0}-{1}".format(SW_ID, getGitHash())
    else:
        version = SW_ID

    return version

if __name__ == '__main__':
    print(getVersion())
