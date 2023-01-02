from datetime import datetime, timedelta
from pprint import pprint
import pytest
from unittest.mock import MagicMock, mock_open, patch, call
import collections

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from cogs.RSQueue.RSQueueData import MemberInfo, RSQueue, ChangeStatus
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

class UserTestData():
    def __init__(self, monkeypatch) -> None:
        self.monkeypatch = monkeypatch
        
        self.userName1 = "SomeName"
        self.uId1 = 11223344
        self.rsModString1 = ""
        self.rsMods1 = Mods().status
        self.runs = {'7':55, '8':1}
        
        self.userName2 = "Lord Jesus"
        self.uId2 = 11223355
        
        self.userName3 = "SomeName3"
        self.uId3 = 11223366

        self.userName4 = "SomeName4"
        self.uId4 = 11223377

        self.userName5 = "SomeName5"
        self.uId5 = 11223388
		
        self.queueId = 7
        self.databaseId1 = 111111111231
        self.guildId = 1234

        self.expectedFixDataTime1 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=40)
        self.expectedFixDataTime2 : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=45)        
        self.mock_MemberInfo_now = MagicMock(return_value=self.expectedFixDataTime1)
        self.mock_RSQueue_now = MagicMock(return_value=self.expectedFixDataTime1)
        
        self.expectedRecord1_Account = {
		    '_id': self.databaseId1, 
	        'userId' : self.uId1,
	        'userName' : self.userName1,
	        'guildId' : self.guildId,
	        'runs' : self.runs}
        self.expectedRecordToRequestForUpsert_Account = {
            'userId' : self.uId1,
            'userName' : self.userName1,
            'guildId' : self.guildId,
            'runs' : self.runs,
            'rsModString' : self.rsModString1,
            'rsMods' : self.rsMods1}

        self.monkeypatch.setattr(MemberInfo, 'now', self.mock_MemberInfo_now)
        self.monkeypatch.setattr(RSQueue, 'now', self.mock_RSQueue_now)

@pytest.fixture()
def UserData_fix(monkeypatch):

    td : UserTestData = UserTestData(monkeypatch)

    return td

@pytest.mark.asyncio
async def test_constructionWithArguments(testdata):
	
    # Method under test
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
async def test_adduser_basicAdd(testdata, UserData_fix):

    userTestData : UserTestData = UserData_fix
    
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]
	
    q = RSQueue(queueId=testdata.queueId)

    # method under test
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
    # expected : datetime= userTestData.expectedFixDataTime1
    # print (f'\n Type: {type(q.members[0].timeInQueue)} {q.members[0].timeInQueue}')
    # print (f'type: {type(expected)} expected : {expected}')
    # print ((expected - q.members[0].timeInQueue).total_seconds())
    assert len(q.members) == 1
    assert q.members[0].name == userTestData.userName1
    assert q.members[0].userId == userTestData.uId1
    assert q.members[0].timeInQueue == userTestData.expectedFixDataTime1

@pytest.mark.asyncio	
async def test_adduser_basicAddDuplicateUserId(testdata, UserData_fix):

    userTestData : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)

    # method under test
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.FAIL

    assert len(q.members) == 1
    assert q.members[0].name == userTestData.userName1
    assert q.members[0].userId == userTestData.uId1

@pytest.mark.asyncio
async def test_adduser_AddUniqueUsersBeyondQueueSizeOf4(testdata, UserData_fix):

    userTestData : UserTestData = UserData_fix
    td = userTestData

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

    # method under test
    assert q.addUser(userId=td.uId1, userName=td.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId2, userName=td.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId3, userName=td.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId4, userName=td.userName4) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId5, userName=td.userName5) == ChangeStatus.FAIL

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
async def test_AddGuest_EmptyQueue(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)

    # method under test
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.MEMBER_AND_GUEST
    
    assert len(q.members) == 2
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[1].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[1].userId == utd.uId1
    assert q.members[1].isGuest() == True

@pytest.mark.asyncio
async def test_AddGuest_AddMemberThenGuestsBeyondSizeOf4(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)

    # method under test
    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.FAIL
    
    assert len(q.members) == 4
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[1].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[1].userId == utd.uId1
    assert q.members[1].isGuest() == True
    assert q.members[2].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[2].userId == utd.uId1
    assert q.members[2].isGuest() == True
    assert q.members[3].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[3].userId == utd.uId1
    assert q.members[3].isGuest() == True

@pytest.mark.asyncio
async def test_AddGuest_AddMemberThenMemberAndGuestsBeyondSizeOf4(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

    # method under test
    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId2, inviterUserName=utd.userName2) == ChangeStatus.MEMBER_AND_GUEST
    assert q.addGuest(inviterUserId=utd.uId3, inviterUserName=utd.userName3) == ChangeStatus.MEMBER
    
    assert len(q.members) == 4
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False

    assert q.members[1].getName() == utd.userName2
    assert q.members[1].userId == utd.uId2
    assert q.members[1].isGuest() == False
    assert q.members[2].getName().endswith(f"Guest ({utd.userName2})")
    assert q.members[2].userId == utd.uId2
    assert q.members[2].isGuest() == True
    
    assert q.members[3].getName() == utd.userName3
    assert q.members[3].userId == utd.uId3
    assert q.members[3].isGuest() == False


@pytest.mark.asyncio
async def test_AddCroid_User1NotInQueueAndQueueEmptyAndToggleCroidStatus(testdata, UserData_fix):
    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

    # Method Under Test
    assert q.addCroid(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    
    assert len(q.members) == 1
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[0].isCroid() == True
    
    # Method Under Test
    assert q.addCroid(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.CROID
    
    assert len(q.members) == 1
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[0].isCroid() == False
    
@pytest.mark.asyncio
async def test_AddCroid_User1InQueueAndQueueEmptyAndToggleCroidStatus(testdata, UserData_fix):
    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert len(q.members) == 1
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[0].isCroid() == False

    # Method Under Test    
    assert q.addCroid(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.CROID
    
    assert len(q.members) == 1
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[0].isCroid() == True

    # Method Under Test    
    assert q.addCroid(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.CROID
    
    assert len(q.members) == 1
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[0].isCroid() == False
    
@pytest.mark.asyncio
async def test_AddCroid_ToUserNotInQueueAndQueueIsFull(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)

    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.FAIL

    # method under test
    assert q.addCroid(userId=utd.uId5, userName=utd.userName5) == ChangeStatus.FAIL
    assert q.addCroid(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.FAIL
    
    assert len(q.members) == 4
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[0].isCroid() == False
    assert q.members[1].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[1].userId == utd.uId1
    assert q.members[1].isGuest() == True
    assert q.members[2].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[2].userId == utd.uId1
    assert q.members[2].isGuest() == True
    assert q.members[3].getName().endswith(f"Guest ({utd.userName1})")
    assert q.members[3].userId == utd.uId1
    assert q.members[3].isGuest() == True
            
@pytest.mark.asyncio
async def test_DeleteMember_User1(testdata, UserData_fix):
	userTestData : UserTestData = UserData_fix
	td = userTestData

	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

	q = RSQueue(queueId=testdata.queueId)

	assert q.addUser(userId=td.uId1, userName=td.userName1) == ChangeStatus.MEMBER
	assert q.addUser(userId=td.uId2, userName=td.userName2) == ChangeStatus.MEMBER
	assert q.addUser(userId=td.uId3, userName=td.userName3) == ChangeStatus.MEMBER
	assert q.addUser(userId=td.uId4, userName=td.userName4) == ChangeStatus.MEMBER
	assert q.addUser(userId=td.uId5, userName=td.userName5) == ChangeStatus.FAIL

    # Method Under Test
	assert q.delUser(userId=td.uId1, userName=td.userName1) == True

	assert len(q.members) == 3
	assert q.members[0].name == td.userName2
	assert q.members[0].userId == td.uId2
	assert q.members[1].name == td.userName3
	assert q.members[1].userId == td.uId3
	assert q.members[2].name == td.userName4
	assert q.members[2].userId == td.uId4

@pytest.mark.asyncio
async def test_DeleteMember_User1AndUser4(testdata, UserData_fix):
    
    utd : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=utd.uId2, userName=utd.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=utd.uId3, userName=utd.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=utd.uId4, userName=utd.userName4) == ChangeStatus.MEMBER
    assert q.addUser(userId=utd.uId5, userName=utd.userName5) == ChangeStatus.FAIL

    # Method Under Test
    assert q.delUser(userId=utd.uId1, userName=utd.userName1) == True
    assert q.delUser(userId=utd.uId4, userName=utd.userName4) == True

    assert len(q.members) == 2
    assert q.members[0].name == utd.userName2
    assert q.members[0].userId == utd.uId2
    assert q.members[1].name == utd.userName3
    assert q.members[1].userId == utd.uId3

@pytest.mark.asyncio
async def test_DeleteMember_DeleteMemberAndAssociatedGuests(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)
    
    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.GUEST
    assert q.addGuest(inviterUserId=utd.uId1, inviterUserName=utd.userName1) == ChangeStatus.FAIL
    
    assert len(q.members) == 4
    
    # method under test
    assert q.delUser(userId=utd.uId1, userName=utd.userName1) == True
        
    assert len(q.members) == 0

@pytest.mark.asyncio
async def test_DeleteMember_DeleteMemberWith0GuestAndOtherMembersAndGuestRemain(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

   
    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId2, inviterUserName=utd.userName2) == ChangeStatus.MEMBER_AND_GUEST
    assert q.addGuest(inviterUserId=utd.uId3, inviterUserName=utd.userName3) == ChangeStatus.MEMBER
   
    # method under test
    assert q.delUser(userId=utd.uId1, userName=utd.userName1) == True
    
    assert len(q.members) == 3
    assert q.members[0].getName() == utd.userName2
    assert q.members[0].userId == utd.uId2
    assert q.members[0].isGuest() == False
    assert q.members[1].getName().endswith(f"Guest ({utd.userName2})")
    assert q.members[1].userId == utd.uId2
    assert q.members[1].isGuest() == True
    
    assert q.members[2].getName() == utd.userName3
    assert q.members[2].userId == utd.uId3
    assert q.members[2].isGuest() == False

@pytest.mark.asyncio
async def test_DeleteGuest_RemoveMembersGuestOnly(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

   
    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId2, inviterUserName=utd.userName2) == ChangeStatus.MEMBER_AND_GUEST
    assert q.addGuest(inviterUserId=utd.uId3, inviterUserName=utd.userName3) == ChangeStatus.MEMBER
   
    # method under test
    assert q.delGuest(userId=utd.uId2) == True
    
    assert len(q.members) == 3
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False
    assert q.members[1].getName() == utd.userName2
    assert q.members[1].userId == utd.uId2
    assert q.members[1].isGuest() == False
    assert q.members[2].getName() == utd.userName3
    assert q.members[2].userId == utd.uId3
    assert q.members[2].isGuest() == False

@pytest.mark.asyncio
async def test_DeleteGuest_DeleteMember_DeleteGuestAndMemberNotInQueue(testdata, UserData_fix):

    utd : UserTestData = UserData_fix

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

   
    assert q.addUser(userId=utd.uId1, userName=utd.userName1) == ChangeStatus.MEMBER
    assert q.addGuest(inviterUserId=utd.uId2, inviterUserName=utd.userName2) == ChangeStatus.MEMBER_AND_GUEST
    assert q.addGuest(inviterUserId=utd.uId3, inviterUserName=utd.userName3) == ChangeStatus.MEMBER
   
    # method under test
    assert q.delGuest(userId=utd.uId5) == False
    assert q.delUser(userId=787878787878, userName="SomeoneNotInQueue") == False
    
    assert len(q.members) == 4
    assert q.members[0].getName() == utd.userName1
    assert q.members[0].userId == utd.uId1
    assert q.members[0].isGuest() == False

    assert q.members[1].getName() == utd.userName2
    assert q.members[1].userId == utd.uId2
    assert q.members[1].isGuest() == False
    assert q.members[2].getName().endswith(f"Guest ({utd.userName2})")
    assert q.members[2].userId == utd.uId2
    assert q.members[2].isGuest() == True
    
    assert q.members[3].getName() == utd.userName3
    assert q.members[3].userId == utd.uId3
    assert q.members[3].isGuest() == False
                
@pytest.mark.asyncio
async def test_isTimeToPrintQueue_NotTimeToPrint(testdata, UserData_fix):

    userTestData : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)


    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
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
async def test_isTimeToPrintQueue_TimeToPrint(testdata, UserData_fix):

    userTestData : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)


    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
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
async def test_getQueueMembers_OneUserInQueue(testdata, UserData_fix):
    userTestData : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)

    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
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
async def test_getQueueMembers_FourUsersInQueue(testdata, UserData_fix):
	
    td : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)

    assert q.addUser(userId=td.uId1, userName=td.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId2, userName=td.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId3, userName=td.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=td.uId4, userName=td.userName4) == ChangeStatus.MEMBER


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
async def test_buildUserStrings_SingleUser(testdata, UserData_fix):

    userTestData : UserTestData = UserData_fix
    #searchKey = {'userId': self.userId} # TODO : check that correct searching key is passed in request
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None]

    q = RSQueue(queueId=testdata.queueId)


    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
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
async def test_buildUserStrings_FourUsers(testdata, UserData_fix):
    queue_td = testdata
    user_td : UserTestData = UserData_fix
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
    assert q.addUser(userId=user_td.uId1, userName=user_td.userName1) == ChangeStatus.MEMBER

    # Advance time return by equiv call datatime.now()
    new_datetime = user_td.expectedFixDataTime1 + timedelta(seconds=120)
    user_td.mock_MemberInfo_now.return_value = new_datetime
    user_td.mock_RSQueue_now.return_value = new_datetime

    result = q.buildUserStrings(q.queueId)

    assert result == expectedString

@pytest.mark.asyncio
async def test_startQueue_OneUsers(testdata, UserData_fix):
	#queue_td = testdata
	user_td : UserTestData = UserData_fix

	expectedSearchKey_UpdateQueueConfig = {'_id': testdata.databaseId}
 
	time = 2
	i = 0
	expectedString = f'{i+1}. `{user_td.userName1}`  [{user_td.runs[user_td.queueId.__str__()]} runs] 🕒 {time} min\n'
	#assert result == f"1. `{q.members[0].name}` [{q.members[0].runs} runs] 🕒 2 min\n"

	#searchKey = {'userId': self.userId} # TODO : check that correct searching key is passed in request
	testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, user_td.expectedRecord1_Account, None, None, None]

	q = RSQueue(queueId=testdata.queueId)
	assert q.addUser(userId=user_td.uId1, userName=user_td.userName1) == ChangeStatus.MEMBER

	# Advance time return by equiv call datatime.now()
	new_datetime = user_td.expectedFixDataTime1 + timedelta(seconds=120)
	user_td.mock_MemberInfo_now.return_value = new_datetime
	user_td.mock_RSQueue_now.return_value = new_datetime

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
async def test_getStaleMembers_NoStaleUsers(testdata, UserData_fix):
    userTestData : UserTestData = UserData_fix
    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == ChangeStatus.MEMBER
    assert len(q.members) == 4

    # method under test
    stale_members = q.getStaleMembers()

    assert(stale_members == None)

@pytest.mark.asyncio
async def test_getStaleMembers_OneStaleUser(testdata, UserData_fix):
    userTestData : UserTestData = UserData_fix

    timeJoinedQueue : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
    timeNow : datetime = 		 datetime(year=2022, month=10, day=25, hour=14, minute=40, second=0)

    mock = MagicMock()
    mock.STALE_QUEUE_PERIOD = 15
    userTestData.mock_MemberInfo_now.side_effect = [timeNow, timeNow, timeJoinedQueue, timeNow, # used for constucting memberInfo's
                                                    timeNow, timeNow, timeNow, timeNow, timeNow] # used getting time now (poitive stale check needs +1)

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == ChangeStatus.MEMBER
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
async def test_getStaleMembers_TwoStaleUser(testdata, UserData_fix):
    userTestData : UserTestData = UserData_fix
    timeJoinedQueue : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
    timeNow : datetime = 		 datetime(year=2022, month=10, day=25, hour=14, minute=40, second=0)


    userTestData.mock_MemberInfo_now.side_effect = [timeNow, timeJoinedQueue, timeJoinedQueue, timeNow, 
                                                    timeNow, timeNow, timeNow, timeNow, timeNow, timeNow]

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == ChangeStatus.MEMBER
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
async def test_getStaleMembersWithTimout_OneStaleUser(testdata, UserData_fix):
    userTestData : UserTestData = UserData_fix
    
    timeNow : datetime = 		 	    datetime(year=2022, month=10, day=25, hour=14, minute=25, second=0)
    timeExpireTimeoutWidow : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=30, second=0)

    userTestData.mock_MemberInfo_now.side_effect = [timeNow, timeNow, timeNow, timeNow,
                                                    timeNow, timeNow, timeExpireTimeoutWidow, timeNow, timeNow]

    testdata.mockDb.findRecord.side_effect = [testdata.expectedRecord_QueueCfg, None, None, None, None]

    q = RSQueue(queueId=testdata.queueId)
    assert q.addUser(userId=userTestData.uId1, userName=userTestData.userName1) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId2, userName=userTestData.userName2) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId3, userName=userTestData.userName3) == ChangeStatus.MEMBER
    assert q.addUser(userId=userTestData.uId4, userName=userTestData.userName4) == ChangeStatus.MEMBER
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
