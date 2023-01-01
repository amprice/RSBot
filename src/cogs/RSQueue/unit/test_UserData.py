import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch, call

import collections
import asyncio
import pprint
import typing
from datetime import datetime
from emoji import emoji, Mods

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from cogs.RSQueue.RSQueueData import RSQueue
from mongodb import Mongodb

from cogs.RSQueue.RSQueue import RSQueueManager
import discord
from discord.ext import commands, tasks

from cogs.RSQueue.RSQueueData import MemberInfo, UserInfo, GuestInfo

class TestObjects():
    def __init__(self) -> None:
        self.databaseId : int = 122323
        self.userId : int = 3432452
        self.userName : str = "Jesus"
        self.queueId : str = "7"
        self.guildId : int = 99999999
        self.runs = {'7':3, '8': 3, '9': 3}
        self.rsModString = "<:laser:1032938402141720576><:mass:1032938405786570813><:barrier:1057824314184957963><:tw:1032938387021254657><:veng:1032938377680535552><:solo1:1032939571777904681>"
        self.rsMods = Mods()
        self.rsMods.status['nosanc'] = True
        self.expectedSearchKey = {'userId': self.userId}
        self.expectedRecord_Account = {'_id': self.databaseId,
                                       'userId' : self.userId,
                                       'userName' : self.userName,
                                       'guildId' : self.guildId,
                                       'rsModString' : self.rsModString,
                                       'rsMods' : self.rsMods.status,
                                       'runs' : self.runs}
        self.expectedRecordUpsert_Account ={'_id': self.databaseId, 
                                            'userId' : self.userId,
                                            'userName' : self.userName,
                                            'guildId' : self.guildId,
                                            'runs' : self.runs}
        
        self.expectedFixDataTime1 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=40)
        self.expectedFixDataTime2 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=45)
                
        self.mock_MemberInfo_now = MagicMock(return_value=self.expectedFixDataTime1)
		
        self.mock_upsert = MagicMock()
        self.mock_upsert.upserted_id = self.databaseId 
        self.mock_Mongodb = MagicMock(spec=Mongodb)
        self.mock_Mongodb.setCollection = MagicMock(return_value=None)
        self.mock_Mongodb.findRecord = MagicMock(return_value=None)
        self.mock_Mongodb.updateOne = MagicMock(return_value=self.mock_upsert)
 
@pytest.fixture()
def fix_UserData(monkeypatch):

    testObjects = TestObjects()
    
    monkeypatch.setattr(MemberInfo, 'now', testObjects.mock_MemberInfo_now)		
    monkeypatch.setattr(Mongodb, 'setCollection', testObjects.mock_Mongodb.setCollection)
    monkeypatch.setattr(Mongodb, 'updateOne', testObjects.mock_Mongodb.updateOne)
    monkeypatch.setattr(Mongodb, 'findRecord', testObjects.mock_Mongodb.findRecord)

    return testObjects

def test_UserInfo_Construction(fix_UserData):
	td : TestObjects = fix_UserData
 
	# Method Under Test
	userInfo = UserInfo(name=td.userName, userId=td.userId, queue=td.queueId, guildId=td.guildId)

	# Test the no database calls made
	td.mock_Mongodb.setCollection.assert_not_called()	
	td.mock_Mongodb.updateOne.assert_not_called()
	td.mock_Mongodb.findRecord.assert_not_called()

	assert userInfo.name == td.userName
	assert userInfo.userId == td.userId
	assert userInfo.queue == td.queueId
	assert userInfo.guildId == td.guildId
	assert userInfo.croid == False
	assert userInfo.rsModString == ""
 
def test_GuestInfo_Construction(fix_UserData):
	td : TestObjects = fix_UserData
 
	# Method Under Test
	userInfo = GuestInfo(name=td.userName, userId=td.userId, queue=td.queueId, guildId=td.guildId)

	# Test the no database calls made
	td.mock_Mongodb.setCollection.assert_not_called()	
	td.mock_Mongodb.updateOne.assert_not_called()
	td.mock_Mongodb.findRecord.assert_not_called()

	assert userInfo.name == td.userName
	assert userInfo.userId == td.userId
	assert userInfo.queue == td.queueId
	assert userInfo.guildId == td.guildId
	assert userInfo.croid == False
	assert userInfo.rsModString == ""
 
def test_MemberInfo_ConstructionWithOutDBRecordRestore(fix_UserData):
    td : TestObjects = fix_UserData

    td.mock_Mongodb.findRecord.return_value = None
	
    # Method Under Test
    d = MemberInfo(name=td.userName, userId=td.userId, queue=td.queueId , guildId=td.guildId)

    #td.mock_Mongodb.assert_called_once()
    
	# Test database calls made
    td.mock_Mongodb.findRecord.assert_called_once()
    
    assert d.name == td.userName
    assert d.userId == td.userId
    assert d.guildId == td.guildId
    assert d.runs == {td.queueId: 0} # taken from initaliser
    assert d.databaseId == td.databaseId
    assert d.queue == td.queueId
    assert d.rsModString == ""
    assert d.rsMods.status == Mods().status
    assert d.timeInQueue == td.expectedFixDataTime1
    assert d.searchKey == td.expectedSearchKey


def test_MemberInfo_ConstructionWithDBRecordRestore(fix_UserData):
    td : TestObjects = fix_UserData

    td.mock_Mongodb.findRecord.return_value = td.expectedRecord_Account
	
    # Method Under Test
    d = MemberInfo(name=td.userName, userId=td.userId, queue=td.queueId , guildId=td.guildId)

    #td.mock_Mongodb.assert_called_once()
    
	# Test database calls made
    td.mock_Mongodb.findRecord.assert_called_once()
    
    assert d.name == td.userName
    assert d.userId == td.userId
    assert d.guildId == td.guildId
    assert d.runs == td.runs
    assert d.databaseId == td.databaseId
    assert d.queue == td.queueId
    assert d.rsModString == td.rsModString
    assert d.rsMods.status == td.rsMods.status
    assert d.timeInQueue == td.expectedFixDataTime1
    assert d.searchKey == td.expectedSearchKey
    
def test_MemberInfoAndGuestInfoPolymorphicCalls(fix_UserData):
    td : TestObjects = fix_UserData
    
    timeJoinedQueue : datetime      = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
    timeNow_30min_later : datetime  = datetime(year=2022, month=10, day=25, hour=14, minute=40, second=0)
    timeNow_5min_later : datetime   = datetime(year=2022, month=10, day=25, hour=14, minute=45, second=0)
    
    td.mock_MemberInfo_now.side_effect = [timeJoinedQueue, timeNow_30min_later, timeNow_30min_later,
                                          timeNow_5min_later, timeNow_5min_later]
  
    # setup Member Info to not restore from mock_Mongodb
    td.mock_Mongodb.findRecord.return_value = None
    
    userData : typing.List[UserInfo] = [
        MemberInfo(td.userName, td.userName),
        GuestInfo(td.userName, td.userId)
    ]
    
    assert userData[0].getName() == td.userName
    assert userData[1].getName() == f"{emoji['guest']} Guest ({td.userName})"
    
    assert userData[0].isGuest() == False
    assert userData[1].isGuest() == True
    
    assert userData[0].isStale() == True
    assert userData[1].isStale() == False
    
    assert userData[0].isReactStale() == True
    assert userData[1].isReactStale() == False