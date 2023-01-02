import sys, os
if __name__ == '__main__':
    import sys
    sys.path.insert(1, 'src')

from botSystem import BUILD_TYPE

from mongodb import Mongodb
from rsbot_logger import rslog
from emoji import Mods, emoji

from datetime import datetime, timedelta

if BUILD_TYPE == BUILD_TYPE.MANUAL_TESTING:
    STALE_QUEUE_PERIOD = 1 # mins
    STALE_REACT_TIMEOUT = 1 # mins
elif (BUILD_TYPE == BUILD_TYPE.UNIT_TESTING or BUILD_TYPE == BUILD_TYPE.RELEASE):
    STALE_QUEUE_PERIOD = 30 # mins
    STALE_REACT_TIMEOUT = 5 # mins
    
class UserInfo():
    def __init__(self, name : str, userId : int, guildId : int, queue : str = "", croid : bool = False) -> None:
        rslog.debug("UserInfo.__init__()")
        self.name : str = name
        self.userId : int = userId
        self.queue = queue.__str__()
        self.guildId : int = guildId
        self.croid : bool = croid
        self.rsModString = ""
        
    def addRun(self):
        rslog.error("UserInfo.addRun()")

    def UpdateUserRecordInDatabase(self):
        rslog.error("UserInfo.UpdateUserRecordInDatabase()")
        return (False)

    def UpdateUserRSModsInDatabase(self, userId : int, rsmods : Mods):
        rslog.error("UserInfo.UpdateUserRSModsInDatabase()")
        return (False)

    def refreshStaleStatus(self):
        rslog.error("UserInfo.refreshStaleStatus()")
        
    def getRuns(self, queue : int) -> int:
        rslog.error("UserInfo.getRuns()")
        return 0

    def getName(self) -> str:
        rslog.error("UserInfo.getName()")
        return ""
    
    def getTimeInQueue(self) -> datetime:
        rslog.debug("UserInfo.getTimeInQueue()")
        return datetime.now()
    
    def isStale(self) -> bool:
        rslog.error("UserInfo.isStale()")
        return False
    
    def isGuest(self) -> bool:
        rslog.debug("UserInfo.isGuest()")
        return False
    
    def isReactStale(self) -> bool:
        rslog.debug("UserInfo.isReactStale()")
        return False
    
    def isCroid(self) -> bool:
        rslog.debug("UserInfo.isCroid()")
        return False
    
    def toggleCroid(self) -> bool:
        rslog.debug("UserInfo.toggleCroid()")
        return False
    
    def now(self):
        rslog.error("UserInfo.now()")
        return None
    
#GuestInfo(name=userName, userId=userId, guildId=self.guildId, queue=self.queueId)    
class GuestInfo(UserInfo):
    def __init__(self, name : str, userId : int, queue : str = "", guildId : int = None) -> None:
        rslog.debug("GuestInfo.__init__()")
        super().__init__(name=name, userId=userId, guildId=guildId, queue=queue, croid=False)
        
    def getName(self) -> str:
        rslog.debug("GuestInfo.getName()")
        name = f"{emoji['guest']} Guest ({self.name})"
        return name
        
    def isStale(self) -> bool:
        rslog.debug("GuestInfo.isStale()")
        # By pass stale check for guest entries
        return False           
    
    def isGuest(self) -> bool:
        rslog.debug("GuestInfo.isGuest()")
        return True
    

    
class MemberInfo(UserInfo):
    def __init__(self, name : str, userId : int, queue : str = "", guildId : int = None, croid : bool = False):
        rslog.debug("MemberInfo.__init__()")
        super().__init__(name=name, userId=userId, guildId=guildId, queue=queue, croid=croid)
        # current_time = self.now()
        # Database Stored Information
        #self.name : str = name
        #self.userId : int = userId
        
        self.runs = {}
        self.runs[queue.__str__()] = 0
        #self.croid : bool = croid
        
        self.rsMods : Mods = Mods()
        
        self.databaseId = None
        
        # Items for stale checking
        current_time = self.now()
        self.timeSinceLastQueueActivity = 0
        self.timeInQueue : datetime = current_time # for ease of testing
        self.timeSinceLastQueueActivity : datetime = current_time # for ease of testing
        
        # self.timeInQueue : datetime = current_time # for ease of testing
        # self.timeSinceLastQueueActivity : datetime = current_time # for ease of testing
        self.isStalechecking = False
        self.staleMessage = None #TODO: can this be removed

        self.db = Mongodb()
        self.db.setCollection('Account')
        self.searchKey = {'userId': self.userId}
        result = self.db.findRecord('Account', self.searchKey)

        #initalise the queue
        if result == None:
            if self.userId != None and self.name != None:
                upsert_result = self.db.updateOne('Account', 
                    self.searchKey, 
                        {'userId' : self.userId,
                        'userName' : self.name,
                        'guildId' : self.guildId,
                        'runs' : self.runs,
                        'rsModString' : self.rsModString,
                        'rsMods' : self.rsMods.status} )
                self.databaseId = upsert_result.upserted_id
            elif self.name == None:
                # No Record found in DB and no config data to write
                pass
        else:
            # We have a record from DB so populate it
            self.databaseId = result['_id']
            self.guildId = result['guildId']
            #self.name = result['userName']
            self.userId = result['userId']
            self.runs = result['runs']
            if ('rsModString' in result.keys()):
                self.rsModString = result['rsModString']
                self.rsMods.status = result['rsMods']
                self.rsMods.sortDictByKey()

            key = queue.__str__()
            if (key not in self.runs):
                # we are joining a queue for the first time but we have a user record
                self.runs[key] = 0


    # def getUserInfo(self):
    #     return {'name': self.name, 'userId': self.userId}

    def addRun(self):
        rslog.debug("MemberInfo.addRun()")
        self.runs[self.queue] = self.runs[self.queue] + 1

    def UpdateUserRecordInDatabase(self):
        rslog.debug("MemberInfo.UpdateUserRecordInDatabase()")
        upsert_result = None

        # current private data valid if we have database Id Key then update record
        if (self.databaseId != None):
            upsert_result = self.db.updateOne('Account', 
                    {'_id': self.databaseId}, 
                        {'userId' : self.userId,
                        'userName' : self.name,
                        'guildId' : self.guildId,
                        'runs' : self.runs,
                        'rsModString' : self.rsModString,
                        'rsMods' : self.rsMods.status} )

        return (upsert_result != None)

    def UpdateUserRSModsInDatabase(self, userId : int, rsmods : Mods):
        rslog.debug("MemberInfo.UpdateUserRSModsInDatabase()")
        upsert_result = None

        # current private data valid if we have database Id Key then update record
        if (self.databaseId != None):
            upsert_result = self.db.updateOne('Account', 
                    {'_id': self.databaseId}, 
                        {'userId' : self.userId,
                        'rsModString' : rsmods.modString(),
                        'rsMods' : rsmods.status,
                        'guildId' : rsmods.guild.id} )

        return (upsert_result != None)


    def refreshStaleStatus(self):
        rslog.debug("MemberInfo.refreshStaleStatus()")
        self.staleMessage = None
        self.isStalechecking = False
        self.timeSinceLastQueueActivity = self.now()
        
    # def now(self):
    #     return datetime.now()

    def getRuns(self, queue : int) -> int:
        rslog.debug("MemberInfo.getRuns()")
        return self.runs[queue.__str__()]
    
    def getName(self) -> str:
        rslog.debug("MemberInfo.getName()")
        return self.name
    
    def isStale(self) -> bool:
        rslog.debug("MemberInfo.isStale()")
        # timenow = self.now()
        # delta = timenow - self.timeSinceLastQueueActivity
        # t = delta.total_seconds()
        t = int((self.now() - self.timeSinceLastQueueActivity).total_seconds())
        if (t >= STALE_QUEUE_PERIOD * 60) and self.isStalechecking == False:
            # collect ids for stale check
            self.isStalechecking = True
            self.timeSinceLastQueueActivity = self.now() # advance time so we can timeout react message
            return True
        return False 
    
    def isReactStale(self) -> bool:
        rslog.debug("MemberInfo.isReactStale()")
        t = int((self.now() - self.timeSinceLastQueueActivity).total_seconds())
        if (t >= STALE_REACT_TIMEOUT * 60) and self.isStalechecking == True:
            # collect ids for who timed out
            self.isStalechecking = False
            self.timeSinceLastQueueActivity = self.now() # advance time so we can timeout react message
            return True
        return False
    
    def isCroid(self) -> bool:
        rslog.debug("MemberInfo.isCroid()")
        return self.croid
    
    def toggleCroid(self) -> bool:
        rslog.debug("MemberInfo.toggleCroid()")
        self.croid = not self.croid
        return self.croid
    
    def getTimeInQueue(self) -> datetime:
        rslog.debug("MemberInfo.getTimeInQueue()")
        return self.timeInQueue
    
    def now(self):
        rslog.debug("MemberInfo.now()")
        return datetime.now()
        
if __name__ == '__main__':
	pass