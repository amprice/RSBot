import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from mongodb import Mongodb
import pprint
from enum import Enum
import typing

import time
class QueueStatus(Enum):
        QUEUE_AVAILABLE = 1,
        QUEUE_COMPLETE = 2,
        QUEUE_FULL = 3,
        QUEUE_ERROR = 4

# TODO: Tie this into knowing is pytest is running or imported....
class BUILD_TYPE(Enum):
        MANUAL_TESTING = 1,
        UNIT_TESTING = 2,
        RELEASE = 3,

BUILD_TYPE = BUILD_TYPE.RELEASE

if BUILD_TYPE.MANUAL_TESTING:
    STALE_QUEUE_PERIOD = 1 # mins
    STALE_REACT_TIMEOUT = 1 # mins
elif (BUILD_TYPE.UNIT_TESTING or BUILD_TYPE.RELEASE):
    STALE_QUEUE_PERIOD = 30 # mins
    STALE_REACT_TIMEOUT = 5 # mins

class MemberInfo():
    def __init__(self, name : str, userId : int, queue : str, guildId : int = None):
        current_time = self.now()
        # Database Stored Information
        self.name : str = name
        self.userId : int = userId
        self.guildId : int = guildId
        self.runs = {}
        self.runs[queue.__str__()] = 0
        self.databaseId = None

        self.queue = queue.__str__()
        self.timeInQueue : datetime = current_time # for ease of testing
        self.timeSinceLastQueueActivity : datetime = current_time # for ease of testing
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
                        'runs' : self.runs} )
                self.databaseId = upsert_result.upserted_id
            elif self.name == None:
                # No Record found in DB and no config data to write
                pass
        else:
            # We have a record from DB so populate it
            self.databaseId = result['_id']
            self.guildId = result['guildId']
            self.name = result['userName']
            self.userId = result['userId']
            self.runs = result['runs']

            key = queue.__str__()
            if (key not in self.runs):
                # we are joining a queue for the first time but we have a user record
                self.runs[key] = 0


    def getUserInfo(self):
        return {'name': self.name, 'userId': self.userId}

    def addRun(self):
        self.runs[self.queue] = self.runs[self.queue] + 1

    def UpdateUserRecordInDatabase(self):
        upsert_result = None

        # current private data valid if we have database Id Key then update record
        if (self.databaseId != None):
            upsert_result = self.db.updateOne('Account', 
                    {'_id': self.databaseId}, 
                        {'userId' : self.userId,
                        'userName' : self.name,
                        'guildId' : self.guildId,
                        'runs' : self.runs} )

        return (upsert_result != None)

    def refreshStaleStatus(self):
        self.staleMessage = None
        self.isStalechecking = False
        self.timeSinceLastQueueActivity = self.now()
        
    def now(self):
        return datetime.now()

class RSQueue:

    # Used when starting up to recover previous queue config if any
    # def __init__(self):
    #     self.db.setCollection('QueueCfg')
    #     self.searchKey = {'Queue': self.role}
    #     result = self.db.findRecord('QueueCfg', self.searchKey)

    #     if result != None:


    def __init__(self, queueId :str, guildId : int = None, queueName : str = None, queueRole: str = None, queueRoleId : str = None, channel : str = None, channelId : int = None, refreshRate : float = None):
        self.guildId = guildId
        self.name = queueName
        self.queueId = queueId
        self.role = queueRole
        self.roleId = queueRoleId
        self.channel = channel
        self.channelId = channelId
        self.refreshRate = refreshRate
        self.qRuns = 0

        self.databaseId = None

        self.lastQueuePrint : datetime = self.now()
        self.size = 0
        self.minSinceLastPrint = 0

        self.members : typing.List[MemberInfo] = []
        self.lastQueueMessage : discord.Message = None

        self.db = Mongodb()

        # self.db.setCollection(self.role)
        self.db.setCollection('QueueCfg')
        self.searchKey = {'queueId': self.queueId}
        result = self.db.findRecord('QueueCfg', self.searchKey)
        
        #initalise the queue
        if result == None:
            if self.queueId != None and self.name != None:
                upsert_result = self.db.updateOne('QueueCfg', 
                    self.searchKey, 
                        {'guildId' : self.guildId,
                        'queueName' : self.name,
                        'queueId': self.queueId, 
                        "roleName": self.role,
                        'roleId' : self.roleId,
                        'channel' : self.channel,
                        'channelId' : self.channelId,
                        'queueRefreshRate' : self.refreshRate,
                        #'queuedUsers' : ['', '', '', ''],
                        #'currentSize' : 0,
                        'qRuns' : self.qRuns} )
                self.databaseId = upsert_result.upserted_id
            elif self.name == None:
                # No Record found in DB and no config data to write
                pass
        else:
            # We have a record from DB so populate it
            self.databaseId = result['_id']
            self.guildId = result['guildId']
            self.name = result['queueName']
            self.queueId = result['queueId']
            self.role = result['roleName']
            self.roleId = result['roleId']
            self.channel = result['channel']
            self.channelId = result['channelId']
            self.refreshRate = result['queueRefreshRate']
            self.qRuns = result['qRuns']

        #self.th.start()
    def UpdateQueueConfigRecordInDatabase(self):
        upsert_result = None

        # current private data valid if we have database Id Key then update record
        if (self.databaseId != None):
            upsert_result = self.db.updateOne('QueueCfg', 
                    {'_id': self.databaseId}, 
                        {'qRuns' : self.qRuns})

        return (upsert_result != None)

    def delUser(self, userName, userId):
        if len(self.members) > 0: # might not need this if - write unit test
            for user in self.members:
                if user.userId == userId:
                    self.members.remove(user)
                    self.size -= 1
                    return True
        return False

    def addUser(self, userName, userId):
        
        if len(self.members) < 4:
            
            # add user to the RS queue
            for user in self.members:
                if user.userId == userId:
                    #user Id found so dont add again for now
                    return False

            # User not found in queue so add to list
            user = MemberInfo(name=userName, userId=userId, guildId=self.guildId, queue=self.queueId)
            self.members.append(user)
            self.size += 1
            return True

        elif len(self.members) == 4:
            # queue full user not added
            return False

    def getStaleMembers(self):
        staleIds : typing.List[MemberInfo] = []

        for user in self.members:
            t = int((self.now() - user.timeSinceLastQueueActivity).total_seconds())
            if (t >= STALE_QUEUE_PERIOD * 60) and user.isStalechecking == False:
                # collect ids for stale check
                staleIds.append(user)
                user.isStalechecking = True
                user.timeSinceLastQueueActivity = self.now() # advance time so we can timeout react message
        
        if (len(staleIds) == 0):
            # Nothing Stale
            return None

        return staleIds
    
    def getStaleMembersWhoTimedOut(self):
        staleIds : typing.List[MemberInfo] = []

        for user in self.members:
            t = int((self.now() - user.timeSinceLastQueueActivity).total_seconds())
            if (t >= STALE_REACT_TIMEOUT * 60) and user.isStalechecking == True:
                # collect ids for who timed out
                staleIds.append(user)
                user.isStalechecking = False
                user.timeSinceLastQueueActivity = self.now() # advance time so we can timeout react message
        
        if (len(staleIds) == 0):
            # None timedout Stale
            return None

        return staleIds

    def getQueueMemberIds(self):
        names = []
        for name in self.members:
            names.append(name.userId)
        return names

    def startqueue(self):
        for member in self.members:
            member.addRun()
            member.UpdateUserRecordInDatabase()
            
            
        self.members = []
        self.size = 0
        self.refreshLastQueuePrint()
        self.qRuns += 1
        self.UpdateQueueConfigRecordInDatabase()

    def checkStartQueue(self):
        if self.size == 4:
            # self.startqueue()
            return True
        else:
            return False
        
        # rec = self.db.findRecord(self.role, {'queue': self.queueId})
        # #print ('----------------------------------')
        # #pprint.pprint(rec)
        # inQ = rec['currentSize']
        # if (inQ < 4):
        #     rec['queuedUsers'][inQ] = name
        #     rec['currentSize'] += 1
        # else:
        #     return QueueStatus.QUEUE_FULL

        # #pprint.pprint(rec)
        # if (None == self.db.updateOne(self.role, self.searchKey, rec)):
        #     return QueueStatus.QUEUE_ERROR
        # else:
        #     if rec['currentSize'] == 4:
        #         return QueueStatus.QUEUE_COMPLETE
        #     else:
        #         return QueueStatus.QUEUE_AVAILABLE

    async def printQueue(self, channel):
        queue_embed = discord.Embed(color=discord.Color.blue(), title=self.name, description='Dummy Queue Print Test')
        await channel.send(embed=queue_embed)

    def calculateDeltaTimeSinceLastQueuePrint(self):
        delta = self.now() - self.lastQueuePrint
        print (delta.total_seconds())

    def isTimeToPrintQueue(self):
        delta = (self.now() - self.lastQueuePrint).total_seconds()

        print (f'{delta} {self.refreshRate * 60} Time Now: {self.now()} Last Print: {self.lastQueuePrint}')
        if (delta >= float(self.refreshRate) * 60):
            self.lastQueuePrint = self.now()
            return True
        
        return False

    def printMembers(self):
        if len(self.members) == 0:
            print ('None')

        for i in range(len(self.members)):
            print (f"{i+1}. {self.members[i].name} {self.members[i].userId}")

        print ('\n')

    def now(self):
        return datetime.now()
    
    def refreshLastQueuePrint(self):
        self.lastQueuePrint = self.now()
    
    def buildUserStrings(self, queue) -> str:
        usersStrings = ''

                # emb.add_field(value=f"1\. `LD` \t {tempTest} \t \[5 runs\] \t 🕒 0m\n" +
        #         "2\. `Player 2` some feature based string goes here 🕒 3m \n"
        #         "3\. `Player 3` some feature based string goes here\n" +
        #         "4\. `Player 4` blah blah blah goes here",
        #     name="\u200b")

        for i in range(len(self.members)):
            time_float = (self.now() - self.members[i].timeInQueue).total_seconds() / 60
            time = int(time_float)

            runs = self.members[i].runs
            key = queue.__str__()
            run_value = runs[queue.__str__()]
            usersStrings += f"{i+1}. `{self.members[i].name}` [{run_value} runs] 🕒 {time} min\n"

        return usersStrings

if __name__ == '__main__':
    pass
    # # Basic Queue Test
    # q1 = RSQueue('112233', 'Red Star Level 7', 'RS7', 3223443, '#RS7', 3242332, 1.0)

    # rec = q1.addUser('Andrew')
    # pprint.pprint(rec)
    
    # print (q1.isTimeToPrintQueue())

    # time.sleep(60)

    # print (q1.isTimeToPrintQueue())
    # print (q1.isTimeToPrintQueue())
    
    # q1.calculateDeltaTimeSinceLastQueuePrint()
    # #q2 = Queue('Red Star Level 8', 'RS8')
    # #q3 = Queue('Red Star Level 9', 'RS9')

    # q = RSQueue(7)

    # q.addUser('Andrew', 1111)
    # q.addUser('Andrew', 1111)
    # q.addUser('Andrew1', 2222)
    # q.addUser('Andrew', 1111)
    # q.addUser('Andrew', 1111)

    # q.printMembers()

    # q.delUser(userName='Andrew', userId=2222)

    # q.printMembers()

    # q.addUser('Bob', 3333)
    # q.addUser('Jim', 4444)
    # q.addUser('John', 5555)
    # r = q.addUser('David', 6666)
    # if (r == False):
    #     print ('Failed to Add Member')

    # q.printMembers()

    # q.delUser(userName='Andrew', userId=1111)
    # q.printMembers()

    # dt : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=40)
    # print (f'{type(dt)} {dt}')
    # print ((dt - q.members[0].timeInQueue).total_seconds())