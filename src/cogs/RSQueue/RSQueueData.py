import sys, os
if __name__ == '__main__':
    import sys
    sys.path.insert(1, 'src') # allow the unit test files to be in "./unit" folder

from botSystem import BUILD_TYPE

#import asyncio
import discord
#from discord.ext import commands, tasks
from discord.ui import Button, View
from datetime import datetime, timedelta
from enum import Enum



import typing
import pprint
#import time

from mongodb import Mongodb
from rsbot_logger import rslog
from emoji import Mods, emoji
from cogs.RSQueue.UserInfo import UserInfo, GuestInfo, MemberInfo

#from enum import Enum
# class QueueStatus(Enum):
#         QUEUE_AVAILABLE = 1,
#         QUEUE_COMPLETE = 2,
#         QUEUE_FULL = 3,
#         QUEUE_ERROR = 4
  

class QueueView(View):
    
    callback = None
    
    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji="<:tick_mark:1056560138137378837>")
    async def join_callback(self, interaction : discord.Interaction, button : discord.ui.Button):
        isEditMessage : bool = False
        username = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        await interaction.response.edit_message(content="")
        await self.callback.JoinQueue(self.queue, username, interaction.user.id, isEditMessage)
        
        
    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red, emoji="<:cross_mark:1056558747520077934>")
    async def leave_callback(self, interaction : discord.Interaction, button : discord.ui.Button):
        username = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        await interaction.response.edit_message(content="")
        await self.callback.LeaveQueue(self.queue, username, interaction.user.id)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.grey, emoji="🚀")
    async def start_callback(self, interaction : discord.Interaction, button : discord.ui.Button):
        username = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        await interaction.response.edit_message(content="")
        await self.callback.startQueue(self.queue, username)

    @discord.ui.button(label="+1 Guest", row=1, style=discord.ButtonStyle.green, emoji=emoji['guest1'])
    async def addguest_callback(self, interaction : discord.Interaction, button : discord.ui.Button):
        username = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        await interaction.response.edit_message(content="")
        await self.callback.JoinQueue(queueIndex=self.queue, userName=username, userId=interaction.user.id, editMessage=False, croid=False, isGuest=True)
    
    @discord.ui.button(label="-1 Guest", row=1, style=discord.ButtonStyle.red, emoji=emoji['guest1'])
    async def delguest_callback(self, interaction : discord.Interaction, button : discord.ui.Button):
        username = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        await interaction.response.edit_message(content="")
        await self.callback.LeaveQueue(queueIndex=self.queue, userName=username, userId=interaction.user.id, isGuest=True)
        
    @discord.ui.button(label="", row=1, style=discord.ButtonStyle.green, emoji="<:croid:1032938396353560576>")
    async def addcroid_callback(self, interaction : discord.Interaction, button : discord.ui.Button):
        isCroid : bool = True
        isEditMessage : bool = True
        username = interaction.user.nick if interaction.user.nick != None else interaction.user.name
        await interaction.response.edit_message(content="")
        await self.callback.JoinQueue(self.queue, username, interaction.user.id, isEditMessage, isCroid)
        
    def __init__(self, queue : int, timeout: float = 180):
        super().__init__(timeout=timeout)
        
        self.queue = queue
 
        
        #self.add_item(self.joinButton)
        
   
class ChangeStatus(Enum):
        FAIL = 0,
        MEMBER = 1,
        GUEST = 2,
        MEMBER_AND_GUEST = 3,
        CROID = 4
    
class RSQueue:

    # Used when starting up to recover previous queue config if any
    # def __init__(self):
    #     self.db.setCollection('QueueCfg')
    #     self.searchKey = {'Queue': self.role}
    #     result = self.db.findRecord('QueueCfg', self.searchKey)

    #     if result != None:
    callback = None

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

        #self.members : typing.List[MemberInfo] = []
        self.members : typing.List[UserInfo] = []
        self.lastQueueMessage : discord.Message = None
        self.view : QueueView = QueueView(queueId, 0)
        QueueView.callback = self.callback
        
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

    def delGuest(self, userId):
        for user in self.members:
            if user.isGuest() and user.userId == userId:
                self.members.remove(user)
                self.size -= 1
                return True
        return False
                
    def delUser(self, userName, userId):
        isSuccess : bool = False
        usersToRemove = []
        
        if len(self.members) > 0: # might not need this if - write unit test
            for user in self.members:
                if user.userId == userId:
                     usersToRemove.append(user)
                     isSuccess = True
            
            if (len(usersToRemove) > 0):
                for user in usersToRemove:
                    self.members.remove(user)
            
            self.size = len(self.members)
        return isSuccess

    def addUser(self, userName, userId, isCroid : bool = False) -> ChangeStatus:
        if len(self.members) < 4:
            
            for user in self.members:
                if user.userId == userId:
                    # Already in the Queue
                    return ChangeStatus.FAIL

            user = MemberInfo(name=userName, userId=userId, guildId=self.guildId, queue=self.queueId, croid=isCroid)
            self.members.append(user)
            self.size += 1 # Todo do we need a seperate size?
            return ChangeStatus.MEMBER
        return ChangeStatus.FAIL
    
    def addGuest(self, inviterUserName, inviterUserId) -> ChangeStatus:
        guestInviterIndex : int = None
        if len(self.members) < 4:
            for i in range(len(self.members)):
                if self.members[i].userId == inviterUserId:
                    #we found the guest inviter
                        guestInviterIndex = i
                        break
                    
            if (guestInviterIndex == None):
                # if room add user + guest
                if len(self.members) < 3:
                    self.addUser(inviterUserName, inviterUserId)
                    user = GuestInfo(name=inviterUserName, userId=inviterUserId, guildId=self.guildId, queue=self.queueId)
                    self.members.insert(len(self.members)+1, user)    
                    self.size += 1 # Todo do we need a seperate size?
                    return ChangeStatus.MEMBER_AND_GUEST
                else:
                    # just add the user
                    self.addUser(inviterUserName, inviterUserId)
                    return ChangeStatus.MEMBER
            else:
                # Just add the Guest
                user = GuestInfo(name=inviterUserName, userId=inviterUserId, guildId=self.guildId, queue=self.queueId)
                self.members.insert(guestInviterIndex+1, user)
                self.size += 1 # Todo do we need a seperate size?
                return ChangeStatus.GUEST
            
        return ChangeStatus.FAIL
    
    def addCroid(self, userName, userId) -> ChangeStatus:
        if len(self.members) < 4:
            for i in range(len(self.members)):
                if self.members[i].userId == userId:
                    self.members[i].toggleCroid()
                    return ChangeStatus.CROID

            # User not in queue so add them with croid status
            return self.addUser(userName=userName, userId=userId, isCroid=True)
        return ChangeStatus.FAIL

    def getStaleMembers(self):
        staleIds : typing.List[MemberInfo] = []

        for user in self.members:
            
            if user.isStale():
                # collect ids for stale check
                staleIds.append(user)
        
        if (len(staleIds) == 0):
            # Nothing Stale
            return None

        return staleIds
    
    def getStaleMembersWhoTimedOut(self):
        staleIds : typing.List[MemberInfo] = []

        for user in self.members:
            
            if user.isReactStale():
                # collect ids for who timed out
                staleIds.append(user)
        
        if (len(staleIds) == 0):
            # None timedout Stale
            return None

        return staleIds

    def getQueueMemberIds(self):
        userIds = []
        for user in self.members:
            if user.isGuest() == False:
                userIds.append(user.userId)
        return userIds

    def getQueuedGuests(self) -> str:
        guests = 0
        guestStr = ""
        
        for user in self.members:
            if user.isGuest():
                guests += 1
                
        if guests == 0:
            guestStr = ""
        else:
            guestStr = f"{guests}x Guests"
        return guestStr
    
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

    async def printQueue(self, channel):
        queue_embed = discord.Embed(color=discord.Color.blue(), title=self.name, description='Dummy Queue Print Test')
        await channel.send(embed=queue_embed)

    def calculateDeltaTimeSinceLastQueuePrint(self):
        delta = self.now() - self.lastQueuePrint
        print (delta.total_seconds())

    def isTimeToPrintQueue(self):
        delta = (self.now() - self.lastQueuePrint).total_seconds()

        # TODO turn into a debug message in logger #print (f'{delta} {self.refreshRate * 60} Time Now: {self.now()} Last Print: {self.lastQueuePrint}')
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
            time_float = (self.now() - self.members[i].getTimeInQueue()).total_seconds() / 60
            time = int(time_float)

            # runs = self.members[i].runs
            # key = queue.__str__()
            # run_value = runs[queue.__str__()]
            run_value = self.members[i].getRuns(queue)
            
            usersStrings += f"{i+1}. `{self.members[i].getName()}` {self.members[i].rsModString} [{run_value} runs] 🕒 {time} min"
            if (self.members[i].isCroid()):
                usersStrings += " <:croid:1032938396353560576>\n"
            else:
                usersStrings += "\n"
                
        return usersStrings

if __name__ == '__main__':
    pass
