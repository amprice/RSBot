import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch, call

import collections
import asyncio
import pprint
from datetime import datetime

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from cogs.RSQueue.RSQueueData import RSQueue
from mongodb import Mongodb

from cogs.RSQueue.RSQueue import RSQueueManager
import discord
from discord.ext import commands, tasks

from cogs.RSQueue.RSQueueData import MemberInfo

@pytest.fixture()
def fix_UserData(monkeypatch):
	queueId : str = '7'

	databaseId = 122323
	userId = 3432452
	userName = 'Jesus'
	runs = {queueId: 0}
	
	guildId = 99999999
	
	
	expectedSearchKey = {'userId': userId}

	expectedRecord_Account = {
		'_id': databaseId, 
        'userId' : userId,
        'userName' : userName,
        'guildId' : guildId,
        'runs' : runs}

	expectedRecordUpsert_Account = {
		'_id': databaseId, 
        'userId' : userId,
        'userName' : userName,
        'guildId' : guildId,
        'runs' : runs}

	expectedFixDataTime1 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=40)
	expectedFixDataTime2 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=45)

	mock_MemberInfo_now = MagicMock(return_value=expectedFixDataTime1)
	monkeypatch.setattr(MemberInfo, 'now', mock_MemberInfo_now)
	mock_upsert = MagicMock()
	mock_upsert.upserted_id = databaseId 
	mock_Mongodb = MagicMock(spec=Mongodb)
	mock_Mongodb.setCollection = MagicMock(return_value=None)
	mock_Mongodb.findRecord = MagicMock(return_value=None)
	mock_Mongodb.updateOne = MagicMock(return_value=mock_upsert)
	monkeypatch.setattr(Mongodb, 'setCollection', mock_Mongodb.setCollection)
	monkeypatch.setattr(Mongodb, 'updateOne', mock_Mongodb.updateOne)
	monkeypatch.setattr(Mongodb, 'findRecord', mock_Mongodb.findRecord)

	objects = {'databaseId': databaseId, 'userId': userId, 'userName': userName, 'guildId': guildId, 'runs': runs, 'queueId': queueId, 'expectedSearchKey': expectedSearchKey, 'expectedRecord_Account': expectedRecord_Account, 'expectedFixDataTime1': expectedFixDataTime1, 'mock_Mongodb': mock_Mongodb}

	return objects

def test_UserData_ConstructionWithOutDBRecordRestore(fix_UserData):
	# TODO: refector MemberInfo -> UserData
	ud = fix_UserData

	d = MemberInfo(name=ud['userName'], userId=ud['userId'], queue=ud['queueId'] , guildId=ud['guildId'])

	assert d.name == ud['userName']
	assert d.userId == ud['userId']
	assert d.guildId == ud['guildId']
	assert d.runs == ud['runs']
	assert d.databaseId == ud['databaseId']
	assert d.queue == ud['queueId'] 
	assert d.timeInQueue == ud['expectedFixDataTime1']
	assert d.searchKey == ud['expectedSearchKey']
