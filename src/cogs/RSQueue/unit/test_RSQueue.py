from datetime import datetime, timedelta
from pprint import pprint
import pytest
from unittest.mock import MagicMock, mock_open, patch, call
import collections

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from cogs.RSQueue.RSQueueData import MemberInfo, RSQueue
from mongodb import Mongodb

from emoji import Mods
class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

Data = collections.namedtuple("Data", 
			['databaseId', 
			 'guildId', 
			 'queueName', 
			 'queueId', 
			 'queueRole', 
			 'queueRoleId', 
			 'channel', 
			 'channelId', 
			 'refreshRate', 
			 'qRuns', 
			 'expectedSearchKey_QueueCfg', 
			 'expectedRecordToRequestForUpsert_QueueCfg', 
			 'expectedRecord_QueueCfg',
			 'expectedSearchKey_AccountRecord',
			 #'expectedRecord_Account',
			 #'runs',
			 'mockDb'])

@pytest.fixture()
def testdata(monkeypatch):
	
	databaseId = 111111111231
	
	guildId = 1234
	
	queueName = "RS7 Queue"
	queueId = "7"
	queueRole = "RS7"
	queueRoleId = "4444"
	channel = "#test-channel"
	channelId = "4444"
	refreshRate : float = "1.0"
	qRuns = 0

	# userId = 3432452
	# userName = 'Jesus'
	# runs = {7:55, 8:1}
	
	expectedSearchKey_AccountRecord = {'_id': databaseId}
	expectedSearchKey_QueueCfg = {'queueId': queueId}

	expectedRecordToRequestForUpsert_QueueCfg =  {
		'guildId': guildId, 
		'queueName': queueName, 
		'queueId': queueId, 
		'roleName': queueRole, 
		'roleId': queueRoleId, 
		'channel': channel, 
		'channelId': channelId, 
		'queueRefreshRate': 
		refreshRate, 'qRuns': qRuns}

	expectedRecord_QueueCfg = {
		'_id' : databaseId,
		'guildId': guildId,
		'queueName': queueName, 
		'queueId': queueId, 
		'roleName': queueRole, 
		'roleId': queueRoleId, 
		'channel': channel, 
		'channelId': channelId, 
		'queueRefreshRate': refreshRate, 
		'qRuns': qRuns}


	# expectedRecord_Account = {
	# 	'_id': databaseId, 
    #     'userId' : userId,
    #     'userName' : userName,
    #     'guildId' : guildId,
    #     'runs' : runs}

	mockDb = MagicMock()
	mockDb.updateOne = MagicMock()
	mockDb.setCollection = MagicMock(return_value=1) # TODO: check return of setCollection
	mockDb.findRecord : MagicMock = MagicMock(return_value=None)
	mock_MemeberInfo = MagicMock(spec=MemberInfo)
	monkeypatch.setattr(Mongodb, 'setCollection', mockDb.setCollection)
	monkeypatch.setattr(Mongodb, 'updateOne', mockDb.updateOne)
	monkeypatch.setattr(Mongodb, 'findRecord', mockDb.findRecord)	
	

	td = Data(databaseId, 
				guildId, 
				queueName, 
				queueId, 
				queueRole, 
				queueRoleId, 
				channel, 
				channelId, 
				refreshRate, 
				qRuns, 
				expectedSearchKey_QueueCfg, 
				expectedRecordToRequestForUpsert_QueueCfg, 
				expectedRecord_QueueCfg, 
				expectedSearchKey_AccountRecord, 
				#expectedRecord_Account, 
				#runs, 
				mockDb)
	
	    

	return td

UserData = collections.namedtuple(
	"UserData", 
		['queueId',
		 'userName1', 
		 'uId1', 
		 'userName2', 
		 'uId2', 
		 'userName3', 
		 'uId3', 
		 'userName4', 
		 'uId4', 
		 'userName5', 
		 'uId5', 
		 'expectedFixDataTime1', 
		 'expectedFixDataTime2', 
		 'mock_MemberInfo_now', 
		 'mock_RSQueue_now',
		 'expectedRecord1_Account',
		 'expectedRecordToRequestForUpsert_Account',
		 'runs'
		 ])

@pytest.fixture()
def userTestData(monkeypatch):
	userName1 = "SomeName"
	uId1 = 11223344
	rsModString1 = ""
	rsMods1 = Mods().status
	userName2 = "Lord"
	uId2 = 11223355
	userName3 = "SomeName"	# although confusing user alias could be same?
	uId3 = 11223366
	userName4 = "SomeName4"
	uId4 = 11223377
	userName4 = "SomeName4"
	uId4 = 11223377
	userName5 = "SomeName5"
	uId5 = 11223388

	databaseId1 = 111111111231
	guildId = 1234
	queueId = 7
	userId = 3432452
	userName = 'Jesus'
	runs = {'7':55, '8':1}

	expectedRecord1_Account = {
		'_id': databaseId1, 
	    'userId' : uId1,
	    'userName' : userName1,
	    'guildId' : guildId,
	    'runs' : runs}


	expectedRecordToRequestForUpsert_Account = {
        'userId' : uId1,
        'userName' : userName1,
        'guildId' : guildId,
        'runs' : runs,
        'rsModString' : rsModString1,
        'rsMods' : rsMods1}

	expectedFixDataTime1 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=40)
	expectedFixDataTime2 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=45)

	mock_MemberInfo_now = MagicMock(return_value=expectedFixDataTime1)
	monkeypatch.setattr(MemberInfo, 'now', mock_MemberInfo_now)
	
	mock_RSQueue_now = MagicMock(return_value=expectedFixDataTime1)
	monkeypatch.setattr(RSQueue, 'now', mock_RSQueue_now)

	data = UserData(
			queueId, 
			userName1, 
			uId1, 
			userName2, 
			uId2, 
			userName3, 
			uId3, 
			userName4, 
			uId4, 
			userName5, 
			uId5, 
			expectedFixDataTime1, 
			expectedFixDataTime2, 
			mock_MemberInfo_now, 
			mock_RSQueue_now, 
			expectedRecord1_Account,
			expectedRecordToRequestForUpsert_Account,
			runs)

	return data

@pytest.mark.asyncio
async def test_constructionWithArguments(testdata):
	
	q = RSQueue(guildId=testdata.guildId, 
				queueName=testdata.queueName, 
				queueId=testdata.queueId,
				queueRole=testdata.queueRole, 
				queueRoleId=testdata.queueRoleId,
				channel=testdata.channel,
				channelId=testdata.channelId,
				refreshRate=testdata.refreshRate)

	testdata.mockDb.setCollection.assert_called_once_with('QueueCfg')
	
	# def findRecord(self, collection :str, searchKey : Dict):
	testdata.mockDb.findRecord.assert_called_once_with("QueueCfg", testdata.expectedSearchKey_QueueCfg)

	testdata.mockDb.updateOne.assert_called_once_with('QueueCfg', testdata.expectedSearchKey_QueueCfg, testdata.expectedRecordToRequestForUpsert_QueueCfg)
	
	assert q.guildId == testdata.guildId
	assert q.name == testdata.queueName
	assert q.queueId == testdata.queueId
	assert q.role == testdata.queueRole
	assert q.roleId == testdata.queueRoleId
	assert q.channel == testdata.channel
	assert q.channelId == testdata.channelId
	assert q.refreshRate == testdata.refreshRate
	assert q.qRuns == testdata.qRuns

	assert q.db != None
	assert q.lastQueuePrint != None
	assert q.size == 0
	assert q.searchKey == testdata.expectedSearchKey_QueueCfg

@pytest.mark.asyncio	
async def test_constructionWithoutArguments(testdata):
	
	testdata.mockDb.findRecord.return_value=testdata.expectedRecord_QueueCfg

	q = RSQueue(testdata.queueId)

	testdata.mockDb.setCollection.assert_called_once_with('QueueCfg')
	
	# def findRecord(self, collection :str, searchKey : Dict):
	testdata.mockDb.findRecord.assert_called_once_with("QueueCfg", testdata.expectedSearchKey_QueueCfg)
	
	testdata.mockDb.updateOne.assert_not_called()
	
	assert q.databaseId == testdata.databaseId
	assert q.guildId == testdata.guildId
	assert q.name == testdata.queueName
	assert q.queueId == testdata.queueId
	assert q.role == testdata.queueRole
	assert q.roleId == testdata.queueRoleId
	assert q.channel == testdata.channel
	assert q.channelId == testdata.channelId
	assert q.refreshRate == testdata.refreshRate
	assert q.qRuns == testdata.qRuns

	assert q.db != None
	assert q.lastQueuePrint != None
	assert q.size == 0
	assert q.searchKey == {'queueId': testdata.queueId}

@pytest.mark.asyncio
async def test_realUpdateOne():

	databaseId = 111111111231
	guildId = 1234
	queueName = "RS7 Queue"
	queueId = "7"
	queueRole = "RS7"
	queueRoleId = "4444"
	channel = "#test-channel"
	channelId = "4444"
	refreshRate = "1.0"
	runs = 0

	queueData = {
		# '_Id' : databaseId,
		'guildId': guildId,
		'queueName': queueName, 
		'queueId': queueId, 
		'roleName': queueRole, 
		'roleId': queueRoleId, 
		'channel': channel, 
		'channelId': channelId, 
		'queueRefreshRate': refreshRate, 
		'runs': runs}

	q = RSQueue(guildId=guildId, 
			queueName=queueName, 
			queueId=queueId,
			queueRole=queueRole, 
			queueRoleId=queueRoleId,
			channel=channel,
			channelId=channelId,
			refreshRate=refreshRate)

@pytest.mark.asyncio
async def test_adduser_basicAdd(testdata, userTestData):

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]
	
	q = RSQueue(queueId=testdata.queueId)

	# method under test
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	# expected : datetime= userTestData.expectedFixDataTime1
	# print (f'\n Type: {type(q.members[0].timeInQueue)} {q.members[0].timeInQueue}')
	# print (f'type: {type(expected)} expected : {expected}')
	# print ((expected - q.members[0].timeInQueue).total_seconds())
	assert len(q.members) == 1
	assert q.members[0].name == userTestData.userName1
	assert q.members[0].userId == userTestData.uId1
	assert q.members[0].timeInQueue == userTestData.expectedFixDataTime1

@pytest.mark.asyncio	
async def test_adduser_basicAddDuplicateUserId(testdata, userTestData):

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

	q = RSQueue(queueId=testdata.queueId)

	# method under test
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True

	assert len(q.members) == 1
	assert q.members[0].name == userTestData.userName1
	assert q.members[0].userId == userTestData.uId1

@pytest.mark.asyncio
async def test_adduser_AddUniqueUsersBeyondQueueSizeOf4(testdata, userTestData):

	td = userTestData

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)

	# method under test
	assert q.addUser(userId=td.uId1, userName=td.userName1) == True
	assert q.addUser(userId=td.uId2, userName=td.userName2) == True
	assert q.addUser(userId=td.uId3, userName=td.userName3) == True
	assert q.addUser(userId=td.uId4, userName=td.userName4) == True
	assert q.addUser(userId=td.uId5, userName=td.userName5) == False

	assert len(q.members) == 4
	assert q.members[0].name == td.userName1
	assert q.members[0].userId == td.uId1
	assert q.members[1].name == td.userName2
	assert q.members[1].userId == td.uId2
	assert q.members[2].name == td.userName3
	assert q.members[2].userId == td.uId3
	assert q.members[3].name == td.userName4
	assert q.members[3].userId == td.uId4

@pytest.mark.asyncio
async def test_adduser_DeleteUserUser1(testdata, userTestData):
	
	td = userTestData

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)

	assert q.addUser(userId=td.uId1, userName=td.userName1) == True
	assert q.addUser(userId=td.uId2, userName=td.userName2) == True
	assert q.addUser(userId=td.uId3, userName=td.userName3) == True
	assert q.addUser(userId=td.uId4, userName=td.userName4) == True
	assert q.addUser(userId=td.uId5, userName=td.userName5) == False

	assert q.delUser(userId=td.uId1, userName=td.userName1) == True

	assert len(q.members) == 3
	assert q.members[0].name == td.userName2
	assert q.members[0].userId == td.uId2
	assert q.members[1].name == td.userName3
	assert q.members[1].userId == td.uId3
	assert q.members[2].name == td.userName4
	assert q.members[2].userId == td.uId4

@pytest.mark.asyncio
async def test_adduser_DeleteUserUser1AndUser4(testdata, userTestData):
	userName1 = "SomeName"
	uId1 = 11223344
	userName2 = "Lord"
	uId2 = 11223355
	userName3 = "SomeName"	# although confusing user alias could be same?
	uId3 = 11223366
	userName4 = "SomeName4"
	uId4 = 11223377
	userName4 = "SomeName4"
	uId4 = 11223377
	userName5 = "SomeName5"
	uId5 = 11223388

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)

	assert q.addUser(userId=uId1, userName=userName1) == True
	assert q.addUser(userId=uId2, userName=userName2) == True
	assert q.addUser(userId=uId3, userName=userName3) == True
	assert q.addUser(userId=uId4, userName=userName4) == True
	assert q.addUser(userId=uId5, userName=userName5) == False

	assert q.delUser(userId=uId1, userName=userName1) == True
	assert q.delUser(userId=uId4, userName=userName4) == True

	assert len(q.members) == 2
	assert q.members[0].name == userName2
	assert q.members[0].userId == uId2
	assert q.members[1].name == userName3
	assert q.members[1].userId == uId3

@pytest.mark.asyncio
async def test_isTimeToPrintQueue_NotTimeToPrint(testdata, userTestData):

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

	q = RSQueue(queueId=testdata.queueId)

	
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert len(q.members) == 1
	assert q.members[0].name == userTestData.userName1
	assert q.members[0].userId == userTestData.uId1
	assert q.members[0].timeInQueue == userTestData.expectedFixDataTime1

	# Advance time return by equiv call datatime.now()
	userTestData.mock_MemberInfo_now.return_value = userTestData.expectedFixDataTime2
	userTestData.mock_RSQueue_now.return_value = userTestData.expectedFixDataTime2

	# m = MagicMock()
	# m.return_value(userTestData.expectedFixDataTime2)

	# method under test
	assert q.lastQueuePrint == userTestData.expectedFixDataTime1
	assert q.isTimeToPrintQueue() == False
	assert q.lastQueuePrint == userTestData.expectedFixDataTime1

@pytest.mark.asyncio
async def test_isTimeToPrintQueue_TimeToPrint(testdata, userTestData):

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

	q = RSQueue(queueId=testdata.queueId)

	
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert len(q.members) == 1
	assert q.members[0].name == userTestData.userName1
	assert q.members[0].userId == userTestData.uId1
	assert q.members[0].timeInQueue == userTestData.expectedFixDataTime1

	# Advance time return by equiv call datatime.now()
	new_datetime = userTestData.expectedFixDataTime1 + timedelta(seconds=60)
	userTestData.mock_MemberInfo_now.return_value = new_datetime
	userTestData.mock_RSQueue_now.return_value = new_datetime

	# method under test
	assert q.lastQueuePrint == userTestData.expectedFixDataTime1
	assert q.isTimeToPrintQueue() == True
	assert q.lastQueuePrint == new_datetime

@pytest.mark.asyncio
async def test_getQueueMembers_OneUserInQueue(testdata, userTestData):

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]
	
	q = RSQueue(queueId=testdata.queueId)
	
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert len(q.members) == 1
	assert q.members[0].name == userTestData.userName1
	assert q.members[0].userId == userTestData.uId1
	assert q.members[0].timeInQueue == userTestData.expectedFixDataTime1

	# method under test
	result = q.getQueueMemberIds()

	pprint(result)
	assert len(result) == 1
	assert result[0] == userTestData.uId1

@pytest.mark.asyncio
async def test_getQueueMembers_FourUsersInQueue(testdata, userTestData):
	
	td = userTestData
	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]
	
	q = RSQueue(queueId=testdata.queueId)
	
	assert q.addUser(userId=td.uId1, userName=td.userName1) == True
	assert q.addUser(userId=td.uId2, userName=td.userName2) == True
	assert q.addUser(userId=td.uId3, userName=td.userName3) == True
	assert q.addUser(userId=td.uId4, userName=td.userName4) == True


	assert len(q.members) == 4

	# method under test
	result = q.getQueueMemberIds()

	assert len(result) == 4
	assert result[0] == td.uId1
	assert result[1] == td.uId2
	assert result[2] == td.uId3
	assert result[3] == td.uId4

    #def buildUserStrings(self) -> str:

@pytest.mark.asyncio
async def test_buildUserStrings_SingleUser(testdata, userTestData):

	#searchKey = {'userId': self.userId} # TODO : check that correct searching key is passed in request
	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

	q = RSQueue(queueId=testdata.queueId)

	
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert len(q.members) == 1
	assert q.members[0].name == userTestData.userName1
	assert q.members[0].userId == userTestData.uId1
	assert q.members[0].timeInQueue == userTestData.expectedFixDataTime1

	# Advance time return by equiv call datatime.now()
	new_datetime = userTestData.expectedFixDataTime1 + timedelta(seconds=120)
	userTestData.mock_MemberInfo_now.return_value = new_datetime
	userTestData.mock_RSQueue_now.return_value = new_datetime

	# method under test
	result = q.buildUserStrings(q.queueId)

	assert result == f"1. `{q.members[0].name}`  [{q.members[0].runs[q.queueId]} runs] 🕒 2 min\n"
	# assert q.lastQueuePrint == userTestData.expectedFixDataTime1
	# assert q.isTimeToPrintQueue() == True
	# assert q.lastQueuePrint == new_datetime

@pytest.mark.asyncio	
async def test_buildUserStrings_FourUsers(testdata, userTestData):
	queue_td = testdata
	user_td = userTestData
	#TODO : Extend this test for 4 users in the queue
	# for i in range(len(self.members)):
	# time_float = (self.now() - self.members[i].timeInQueue).total_seconds() / 60
	# time = int(time_float)
	# usersStrings += f"{i+1}. `{self.members[i].name}` [{self.members[i].runs} runs] 🕒 {time} min\n"
	time = 2
	i = 0
	expectedString = f'{i+1}. `{user_td.userName1}`  [{user_td.runs[user_td.queueId.__str__()]} runs] 🕒 {time} min\n'
	#assert result == f"1. `{q.members[0].name}` [{q.members[0].runs} runs] 🕒 2 min\n"

	#searchKey = {'userId': self.userId} # TODO : check that correct searching key is passed in request
	queue_td.mockDb.findRecord.side_effect = [queue_td.expectedRecord_QueueCfg, user_td.expectedRecord1_Account, None, None, None]

	q = RSQueue(queueId=queue_td.queueId)
	assert q.addUser(userId=user_td.uId1, userName=user_td.userName1) == True

	# Advance time return by equiv call datatime.now()
	new_datetime = userTestData.expectedFixDataTime1 + timedelta(seconds=120)
	userTestData.mock_MemberInfo_now.return_value = new_datetime
	userTestData.mock_RSQueue_now.return_value = new_datetime

	result = q.buildUserStrings(q.queueId)

	assert result == expectedString

@pytest.mark.asyncio
async def test_startQueue_OneUsers(testdata, userTestData):
	#queue_td = testdata
	user_td = userTestData

	expectedSearchKey_UpdateQueueConfig = {'_id': testdata.databaseId}
 
	time = 2
	i = 0
	expectedString = f'{i+1}. `{user_td.userName1}`  [{user_td.runs[user_td.queueId.__str__()]} runs] 🕒 {time} min\n'
	#assert result == f"1. `{q.members[0].name}` [{q.members[0].runs} runs] 🕒 2 min\n"

	#searchKey = {'userId': self.userId} # TODO : check that correct searching key is passed in request
	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, user_td.expectedRecord1_Account, None, None, None]

	q = RSQueue(queueId=testdata.queueId)
	assert q.addUser(userId=user_td.uId1, userName=user_td.userName1) == True

	# Advance time return by equiv call datatime.now()
	new_datetime = userTestData.expectedFixDataTime1 + timedelta(seconds=120)
	userTestData.mock_MemberInfo_now.return_value = new_datetime
	userTestData.mock_RSQueue_now.return_value = new_datetime

	result = q.buildUserStrings(q.queueId)
	assert result == expectedString

	q.startqueue()

	updateOneCalls = [call("Account", testdata.expectedSearchKey_AccountRecord, user_td.expectedRecordToRequestForUpsert_Account),
			 call("QueueCfg", expectedSearchKey_UpdateQueueConfig, {'qRuns' : 1})]
	
	#message_mock.remove_reaction.assert_has_calls(calls=calls, any_order=False)
	
 	#testdata.mockDb.updateOne.assert_called_once_with("Account", testdata.expectedSearchKey_AccountRecord, user_td.expectedRecordToRequestForUpsert_Account)
	testdata.mockDb.updateOne.assert_has_calls(calls=updateOneCalls, any_order=True)

	assert len(q.members) == 0
	assert q.size == 0

@pytest.mark.asyncio
async def test_getStaleMembers_NoStaleUsers(testdata, userTestData):
	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == True
	assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == True
	assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == True
	assert len(q.members) == 4

	# method under test
	stale_members = q.getStaleMembers()

	assert(stale_members == None)

@pytest.mark.asyncio
async def test_getStaleMembers_OneStaleUser(testdata, userTestData):

	timeJoinedQueue : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
	timeNow : datetime = 		 datetime(year=2022, month=10, day=25, hour=14, minute=40, second=0)

	mock = MagicMock()
	mock.STALE_QUEUE_PERIOD = 15
	userTestData.mock_MemberInfo_now.side_effect = [timeNow, timeNow, timeJoinedQueue, timeNow, timeNow]
	userTestData.mock_RSQueue_now.side_effect = [timeNow, timeNow, timeNow, timeNow, timeNow, timeNow]

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == True
	assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == True
	assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == True
	assert len(q.members) == 4

	#q.members[2].isStalechecking = False
	#q.members[2].timeSinceLastQueueActivity = timeJoinedQueue
	# method under test
	stale_members = q.getStaleMembers()

	assert q.members[0].isStalechecking == False
	assert q.members[1].isStalechecking == False
	assert q.members[2].isStalechecking == True
	assert q.members[3].isStalechecking == False

	assert q.members[2].timeSinceLastQueueActivity == timeNow
	assert(len(stale_members) == 1)
	assert userTestData.uId3 == q.members[2].userId 

@pytest.mark.asyncio
async def test_getStaleMembers_TwoStaleUser(testdata, userTestData):

	timeJoinedQueue : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
	timeNow : datetime = 		 datetime(year=2022, month=10, day=25, hour=14, minute=40, second=0)

	mock = MagicMock()
	mock.STALE_QUEUE_PERIOD = 15
	userTestData.mock_MemberInfo_now.side_effect = [timeNow, timeJoinedQueue, timeJoinedQueue, timeNow, timeNow]
	userTestData.mock_RSQueue_now.side_effect = [timeNow, timeNow, timeNow, timeNow, timeNow, timeNow, timeNow]

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == True
	assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == True
	assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == True
	assert len(q.members) == 4

	#q.members[2].isStalechecking = False
	#q.members[2].timeSinceLastQueueActivity = timeJoinedQueue
	# method under test
	stale_members = q.getStaleMembers()

	assert q.members[0].isStalechecking == False
	assert q.members[1].isStalechecking == True
	assert q.members[2].isStalechecking == True
	assert q.members[3].isStalechecking == False

	assert(len(stale_members) == 2)
	assert q.members[1].timeSinceLastQueueActivity == timeNow
	assert q.members[2].timeSinceLastQueueActivity == timeNow
	assert userTestData.uId2 == q.members[1].userId 
	assert userTestData.uId3 == q.members[2].userId 

@pytest.mark.asyncio
async def test_getStaleMembersWithTimout_OneStaleUser(testdata, userTestData):

	timeJoinedQueue : datetime = 	    datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
	timeNow : datetime = 		 	    datetime(year=2022, month=10, day=25, hour=14, minute=25, second=0)
	timeExpireTimeoutWidow : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=30, second=0)
	mock = MagicMock()
	mock.STALE_QUEUE_PERIOD = 15
	userTestData.mock_MemberInfo_now.side_effect = [timeNow, timeNow, timeNow, timeNow, timeNow]
	userTestData.mock_RSQueue_now.side_effect = [timeNow, timeNow, timeNow, timeExpireTimeoutWidow, timeNow, timeNow]

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)
	assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == True
	assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == True
	assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == True
	assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == True
	assert len(q.members) == 4

	q.members[0].isStalechecking = False
	q.members[1].isStalechecking = False
	q.members[2].isStalechecking = True
	q.members[3].isStalechecking = False

	# method under test
	stale_members = q.getStaleMembersWhoTimedOut()

	assert q.members[0].isStalechecking == False
	assert q.members[1].isStalechecking == False
	assert q.members[2].isStalechecking == False
	assert q.members[3].isStalechecking == False

	assert(len(stale_members) == 1)
	assert q.members[2].timeSinceLastQueueActivity == timeNow
	assert userTestData.uId3 == q.members[2].userId 