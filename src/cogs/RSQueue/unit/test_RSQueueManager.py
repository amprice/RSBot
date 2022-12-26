import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch, call

import collections
import asyncio
import pprint
from datetime import datetime

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from cogs.RSQueue.RSQueueData import MemberInfo, RSQueue
from mongodb import Mongodb

from cogs.RSQueue.RSQueue import PrivateMessage, RSQueueManager
import discord
from discord.ext import commands, tasks

class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

# TODO: Establish Setup / Teardown for tests.....and clean up with fixtures
class handelReactionTestDataAndMocks():

	def __init__(self, mp) -> None:
		self.monkeypatch = mp
		self.databaseId = 111122222
		self.guildId = 2222222
		self.queueName = "RS 11 Queue"
		self.queueId = "11"
		self.queueRole = "SomeRole"
		self.queueRoleId = "444444"
		self.channel = "#RS11"
		self.channelId = "555555"
		self.refreshRate = 15.0
		# runs = 0
		self.size = 4

		self.staleMessageSentTime : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0) # Time activity check message sent to user
		self.timeNow : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=15, second=0) # time now setup to expire the message e.g. 5 min later

		self.expected_dummy_string = 'Message from the bot that the user will react too.'
		self.expected_memInfo = MemberInfo(name="Jesus", userId=10000, queue="RS11", guildId=1111)
	
		self.expected_members = [self.expected_memInfo]
		self.expected_userId_stale_members = [self.expected_memInfo]
	
		self.mock_MemberInfo_now = MagicMock(return_value=self.staleMessageSentTime)
		self.monkeypatch.setattr(MemberInfo, 'now', self.mock_MemberInfo_now)

		self.message_mock = AsyncMock(spec=discord.Message)
		self.message_mock.add_reaction = AsyncMock()
		self.message_mock.remove_reaction = AsyncMock()
		self.message_mock.channel = AsyncMock()
		self.message_mock.channel.send = AsyncMock()
		self.message_mock.content = self.expected_dummy_string
		self.member_mock = MagicMock()
		self.member_mock.create_dm = AsyncMock()
		self.member_mock.send = AsyncMock(return_value=self.message_mock)
	
		self.context_mock = MagicMock(spec=commands.Context)
		self.context_mock.author = MagicMock()
		self.context_mock.author.name = 'Somebody'
	
		self.channel_mock = MagicMock()
		self.channel_mock.send = AsyncMock(return_value=self.message_mock)
	
		self.guild_mock = MagicMock()
		self.guild_mock.get_channel = MagicMock(return_value=self.channel_mock)
		self.guild_mock.get_member = MagicMock(return_value=self.member_mock)
	
		self.bot_mock = MagicMock(spec=commands.Bot)
		self.bot_mock.get_guild = MagicMock(return_value=self.guild_mock)
	
		self.rsqueue_mock = MagicMock(spec=RSQueue)
		self.rsqueue_mock.databaseId = self.databaseId
		self.rsqueue_mock.guildId = self.guildId
		self.rsqueue_mock.name = self.queueName
		self.rsqueue_mock.queueId = self.queueId
		self.rsqueue_mock.role = self.queueRole
		self.rsqueue_mock.roleId = self.queueRoleId
		self.rsqueue_mock.channel = self.channel
		self.rsqueue_mock.channelId = self.channelId
		self.rsqueue_mock.refreshRate = self.refreshRate
		self.rsqueue_mock.size = self.size
		self.rsqueue_mock.members = self.expected_members
		self.rsqueue_mock.getQueueMembers = MagicMock(return_value=self.expected_members)
		self.rsqueue_mock.getStaleMembers = MagicMock(return_value=self.expected_members)
		self.rsqueue_mock.getStaleMembersWhoTimedOut = MagicMock(return_value=self.expected_members)

		self.expected_privateMessage = PrivateMessage(message=self.message_mock, userId=10000, queue=self.rsqueue_mock, memInfo=self.expected_memInfo)
		self.expected_privateMessages = [self.expected_privateMessage]

		self.reaction_mock = MagicMock(spec=discord.Reaction)
		self.reaction_mock.message = MagicMock()
		self.reaction_mock.message.channel = MagicMock()
		self.reaction_mock.message.content = self.expected_dummy_string
		self.reaction_mock.emoji = "" # simulate any emoji we are not looking for
		self.user_mock = MagicMock(spec=discord.User)
		self.user_mock.dm_channel = self.reaction_mock.message.channel

	
@pytest.mark.asyncio
async def test_listQueueConfigCommandWithAllQueuesNone(monkeypatch):
	
	# loop = asyncio.get_event_loop()
	# asyncio.set_event_loop(loop)

	class_mock = MagicMock()
	context_mock = MagicMock(spec=commands.Context)
	bot_mock = MagicMock(spec=commands.Bot)
	emb_mock = MagicMock(spec=discord.Embed)
	emb_mock.add_field = MagicMock()

	monkeypatch.setattr(discord.Embed, 'add_field', emb_mock.add_field)

	db_mock = MagicMock(spec=Mongodb)
	db_mock.findRecord = MagicMock(return_value=None)
 
	monkeypatch.setattr(Mongodb, 'setCollection', db_mock.setCollection)
	monkeypatch.setattr(Mongodb, 'updateOne', db_mock.updateOne)
	monkeypatch.setattr(Mongodb, 'findRecord', db_mock.findRecord)	
 
	qm = RSQueueManager(bot_mock)

	await qm.listq(qm, context_mock, "queue_cfg", "foo", "bar")

	calls = [call(name="RS5", value="Not Configured", inline=False),
			 call(name="RS6", value="Not Configured", inline=False),
			 call(name="RS7", value="Not Configured", inline=False),
			 call(name="RS8", value="Not Configured", inline=False),
			 call(name="RS9", value="Not Configured", inline=False),
			 call(name="RS10", value="Not Configured", inline=False),
			 call(name="RS11", value="Not Configured", inline=False)]
	
	emb_mock.add_field.assert_has_calls(calls=calls, any_order=False)
	
	qm.queueCheck.cancel()
 
@pytest.mark.asyncio
async def test_listQueueConfigCommandWithOneQueueConfigured(monkeypatch):
	
	databaseId = 111122222
	guildId = 2222222
	queueName = "RS 11 Queue"
	queueId = "11"
	queueRole = "SomeRole"
	queueRoleId = "444444"
	channel = "#RS11"
	channelId = "555555"
	refreshRate = 15.0
	# runs = 0

	# class_mock = MagicMock()
	context_mock = MagicMock(spec=commands.Context)
	bot_mock = MagicMock(spec=commands.Bot)
	emb_mock = MagicMock(spec=discord.Embed)
	emb_mock.add_field = MagicMock()
	rsqueue_mock = MagicMock(spec=RSQueue)
	rsqueue_mock.databaseId = databaseId
	rsqueue_mock.guildId = guildId
	rsqueue_mock.name = queueName
	rsqueue_mock.queueId = queueId
	rsqueue_mock.role = queueRole
	rsqueue_mock.roleId = queueRoleId
	rsqueue_mock.channel = channel
	rsqueue_mock.channelId = channelId
	rsqueue_mock.refreshRate = refreshRate


	monkeypatch.setattr(discord.Embed, 'add_field', emb_mock.add_field)

	db_mock = MagicMock(spec=Mongodb)
	db_mock.findRecord = MagicMock(return_value=None)
	monkeypatch.setattr(Mongodb, 'setCollection', db_mock.setCollection)
	monkeypatch.setattr(Mongodb, 'updateOne', db_mock.updateOne)
	monkeypatch.setattr(Mongodb, 'findRecord', db_mock.findRecord)	


	qm = RSQueueManager(bot_mock)

	qm.qs[11] = rsqueue_mock

	# method under test
	await qm.listq(qm, context_mock, "queue_cfg", "foo", "bar")

	calls = [call(name="RS5", value="Not Configured", inline=False),
			 call(name="RS6", value="Not Configured", inline=False),
			 call(name="RS7", value="Not Configured", inline=False),
			 call(name="RS8", value="Not Configured", inline=False),
			 call(name="RS9", value="Not Configured", inline=False),
			 call(name="RS10", value="Not Configured", inline=False),
			 call(name="RS11", 
				value=f"databaseId = {databaseId}\n" +
					f"guildId = {guildId}\n" +
					f"queueName = {queueName}\n" +
					f"queueId = {queueId}\n" +
					f"roleName = &{queueRole}\n" +
					f"roleId = {queueRoleId}\n" + 
					f"channel = #{channel}\n" +
					f"channelId = {channelId}\n" +
					f"refreshRate = {refreshRate} min", 
				inline=False)]

	emb_mock.add_field.assert_has_calls(calls=calls, any_order=False)
	
	qm.queueCheck.cancel()
 
@pytest.mark.asyncio
async def test_connectCommand(monkeypatch):
	
	# loop = asyncio.get_event_loop()
	# asyncio.set_event_loop(loop)
	
    # ctx.message.guild.id,

	id_mock = MagicMock(return_value="12345")
	class_mock = MagicMock()
	message_mock = MagicMock()
	message_mock.guild = MagicMock(return_value=id_mock)
	context_mock = MagicMock(spec=commands.Context)
	context_mock.message = MagicMock(return_value=message_mock)
	#RSQueue_mock = MagicMock(spec=RSQueue)
	bot_mock = MagicMock(spec=commands.Bot)
	emb_mock = MagicMock(spec=discord.Embed)
	guildRole_mock = MagicMock()
	discordUtils_mock = MagicMock(spec=discord.utils, return_value=guildRole_mock)
	
	db_mock = MagicMock(spec=Mongodb)

	monkeypatch.setattr(Mongodb, 'setCollection', db_mock.setCollection)
	monkeypatch.setattr(Mongodb, 'updateOne', db_mock.updateOne)
	monkeypatch.setattr(Mongodb, 'findRecord', db_mock.findRecord)	

	qm = RSQueueManager(bot_mock)

	# method under test
	await qm.connect(class_mock, context_mock, "8", "RS8 Queue", "RS8", 1.0)

	
	pprint.pprint (qm.qs)
	print(f"{qm.qs[8].databaseId}")
 
	qm.queueCheck.cancel()

@pytest.mark.asyncio
async def test_startQ_QueueStartCommand(monkeypatch):

	databaseId = 111122222
	guildId = 2222222
	queueName = "RS 11 Queue"
	queueId = "11"
	queueRole = "SomeRole"
	queueRoleId = "444444"
	channel = "#RS11"
	channelId = "555555"
	refreshRate = 15.0
	# runs = 0
	size = 4

	expected_members = ['Andrew', 'Paul', 'Peter', 'David']
	context_mock = MagicMock(spec=commands.Context)
	context_mock.author = MagicMock()
	context_mock.author.name = 'Somebody'
	channel_mock = MagicMock()
	channel_mock.send = AsyncMock()
	guild_mock = MagicMock()
	guild_mock.get_channel = MagicMock(return_value=channel_mock)
	bot_mock = MagicMock(spec=commands.Bot)
	bot_mock.get_guild = MagicMock(return_value=guild_mock)
	qm = RSQueueManager(bot_mock)

	rsqueue_mock = MagicMock(spec=RSQueue)
	rsqueue_mock.databaseId = databaseId
	rsqueue_mock.guildId = guildId
	rsqueue_mock.name = queueName
	rsqueue_mock.queueId = queueId
	rsqueue_mock.role = queueRole
	rsqueue_mock.roleId = queueRoleId
	rsqueue_mock.channel = channel
	rsqueue_mock.channelId = channelId
	rsqueue_mock.refreshRate = refreshRate
	rsqueue_mock.size = size
	rsqueue_mock.members = MagicMock()
	rsqueue_mock.getQueueMembers = MagicMock(return_value=expected_members)

	qm.qs[11] = rsqueue_mock

	# method under test
	await qm.startq(qm, context_mock, "11")
 
	qm.queueCheck.cancel()

@pytest.mark.asyncio
async def test_buildStaleEmbed(monkeypatch):
	databaseId = 111122222
	guildId = 2222222
	queueName = "RS 11 Queue"
	queueId = "11"
	queueRole = "SomeRole"
	queueRoleId = "444444"
	channel = "#RS11"
	channelId = "555555"
	refreshRate = 15.0
	# runs = 0
	size = 4
	expected_memInfo = MemberInfo(name="Jesus", userId=10000, queue="RS11", guildId=1111)
	expected_members = ['Andrew', 'Paul', 'Peter', 'David']
	context_mock = MagicMock(spec=commands.Context)
	context_mock.author = MagicMock()
	context_mock.author.name = 'Somebody'
	channel_mock = MagicMock()
	channel_mock.send = AsyncMock()
	guild_mock = MagicMock()
	guild_mock.get_channel = MagicMock(return_value=channel_mock)
	bot_mock = MagicMock(spec=commands.Bot)
	bot_mock.get_guild = MagicMock(return_value=guild_mock)
	qm = RSQueueManager(bot_mock)
	
	rsqueue_mock = MagicMock(spec=RSQueue)
	rsqueue_mock.databaseId = databaseId
	rsqueue_mock.guildId = guildId
	rsqueue_mock.name = queueName
	rsqueue_mock.queueId = queueId
	rsqueue_mock.role = queueRole
	rsqueue_mock.roleId = queueRoleId
	rsqueue_mock.channel = channel
	rsqueue_mock.channelId = channelId
	rsqueue_mock.refreshRate = refreshRate
	rsqueue_mock.size = size
	rsqueue_mock.qRuns = 33
	rsqueue_mock.members = MagicMock()
	rsqueue_mock.getQueueMembers = MagicMock(return_value=expected_members)

	guild_mock = MagicMock(spec=discord.Guild)
 
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = rsqueue_mock

	# method under test
	result = qm.buildStaleEmbed(guild=guild_mock, queue=rsqueue_mock, user=expected_memInfo)

	assert result != None
	assert result.description == AnyStringWith("You have been in the queue for")
	assert result.title == AnyStringWith("Check")
	assert result.color == discord.Color.magenta()

	qm.queueCheck.cancel()

@pytest.mark.asyncio
async def test_CheckForStaleMembers_OneStaleMember(monkeypatch):
	databaseId = 111122222
	guildId = 2222222
	queueName = "RS 11 Queue"
	queueId = "11"
	queueRole = "SomeRole"
	queueRoleId = "444444"
	channel = "#RS11"
	channelId = "555555"
	refreshRate = 15.0
	# runs = 0
	size = 4

	expected_memInfo = MemberInfo(name="Jesus", userId="10000", queue="RS11", guildId=1111)
	expected_members = ['Andrew', 'Paul', 'Peter', 'David']
	expected_userId_stale_members = [expected_memInfo]

	message_mock = AsyncMock(sped=discord.Message)
	message_mock.add_reaction = AsyncMock()
	member_mock = MagicMock()
	member_mock.create_dm = AsyncMock()
	member_mock.send = AsyncMock(return_value=message_mock)
	context_mock = MagicMock(spec=commands.Context)
	context_mock.author = MagicMock()
	context_mock.author.name = 'Somebody'
	channel_mock = MagicMock()
	channel_mock.send = AsyncMock(return_value=message_mock)
	guild_mock = MagicMock()
	guild_mock.get_channel = MagicMock(return_value=channel_mock)
	guild_mock.get_member = MagicMock(return_value=member_mock)
	bot_mock = MagicMock(spec=commands.Bot)
	bot_mock.get_guild = MagicMock(return_value=guild_mock)
	qm = RSQueueManager(bot_mock)
	
	rsqueue_mock = MagicMock(spec=RSQueue)
	rsqueue_mock.databaseId = databaseId
	rsqueue_mock.guildId = guildId
	rsqueue_mock.name = queueName
	rsqueue_mock.queueId = queueId
	rsqueue_mock.role = queueRole
	rsqueue_mock.roleId = queueRoleId
	rsqueue_mock.channel = channel
	rsqueue_mock.channelId = channelId
	rsqueue_mock.refreshRate = refreshRate
	rsqueue_mock.size = size
	rsqueue_mock.members = MagicMock()
	rsqueue_mock.getQueueMembers = MagicMock(return_value=expected_members)
	rsqueue_mock.getStaleMembers = MagicMock(return_value=expected_userId_stale_members)
	rsqueue_mock.qRuns = 33
	stalemembers_mock = MagicMock()
	embed_mock = MagicMock(spec=discord.Embed)

	qm.qs[11] = rsqueue_mock

	# method under test
	result = await qm.CheckForStaleMembers(rsqueue_mock)

	assert result == True
	assert len(qm.privateMessages) == 1

	calls = [call("✅"),
			 call("❎")]
	
	message_mock.add_reaction.assert_has_calls(calls=calls, any_order=True)


	qm.queueCheck.cancel()

@pytest.mark.asyncio
async def test_CheckForStaleMembers_OneStaleMemberTimedOut(monkeypatch):
	databaseId = 111122222
	guildId = 2222222
	queueName = "RS 11 Queue"
	queueId = "11"
	queueRole = "SomeRole"
	queueRoleId = "444444"
	channel = "#RS11"
	channelId = "555555"
	refreshRate = 15.0
	# runs = 0
	size = 4

	expected_memInfo = MemberInfo(name="Jesus", userId=10000, queue="RS11", guildId=1111)
	
	expected_members = ['Andrew', 'Paul', 'Peter', 'David']
	expected_userId_stale_members = [expected_memInfo]
	
	
	message_mock = AsyncMock(spec=discord.Message)
	message_mock.add_reaction = AsyncMock()
	message_mock.remove_reaction = AsyncMock()
	message_mock.channel = AsyncMock()
	message_mock.channel.send = AsyncMock()

	member_mock = MagicMock()
	member_mock.create_dm = AsyncMock()
	member_mock.send = AsyncMock(return_value=message_mock)
	
	context_mock = MagicMock(spec=commands.Context)
	context_mock.author = MagicMock()
	context_mock.author.name = 'Somebody'
	
	channel_mock = MagicMock()
	channel_mock.send = AsyncMock(return_value=message_mock)
	
	guild_mock = MagicMock()
	guild_mock.get_channel = MagicMock(return_value=channel_mock)
	guild_mock.get_member = MagicMock(return_value=member_mock)
	
	bot_mock = MagicMock(spec=commands.Bot)
	bot_mock.get_guild = MagicMock(return_value=guild_mock)
	qm = RSQueueManager(bot_mock)
	
	rsqueue_mock = MagicMock(spec=RSQueue)
	rsqueue_mock.databaseId = databaseId
	rsqueue_mock.guildId = guildId
	rsqueue_mock.name = queueName
	rsqueue_mock.queueId = queueId
	rsqueue_mock.role = queueRole
	rsqueue_mock.roleId = queueRoleId
	rsqueue_mock.channel = channel
	rsqueue_mock.channelId = channelId
	rsqueue_mock.refreshRate = refreshRate
	rsqueue_mock.size = size
	rsqueue_mock.qRuns = 33
	rsqueue_mock.members = MagicMock()
	rsqueue_mock.getQueueMembers = MagicMock(return_value=expected_members)
	rsqueue_mock.getStaleMembers = MagicMock(return_value=expected_userId_stale_members)
	rsqueue_mock.getStaleMembersWhoTimedOut = MagicMock(return_value=expected_userId_stale_members)
	rsqueue_mock.lastQueueMessage = MagicMock(spec=discord.Message)
	rsqueue_mock.view = MagicMock(spec=discord.ui.View)
	expected_privateMessage = PrivateMessage(message=message_mock, userId=10000, queue=rsqueue_mock, memInfo=expected_memInfo)
	expected_privateMessages = [expected_privateMessage]

	qm.privateMessages = expected_privateMessages
	#rsqueue_mock.privateMessages = expected_privateMessages
	stalemembers_mock = MagicMock
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = rsqueue_mock

	# method under test
	result = await qm.CheckForStaleTimedOutMembers(rsqueue_mock)

	assert result == True
	assert len(qm.privateMessages) == 0

	removeReactionCalls = [call(emoji='✅', member=member_mock),
			 		 	   call(emoji='❎', member=member_mock)]
	
	message_mock.remove_reaction.assert_has_calls(calls=removeReactionCalls, any_order=True)
	channel_mock.send.assert_awaited_once_with(AnyStringWith('has timed out and been removed from RS 11 Queue'))  # send via channel object obtained from guild return -> guild channel
	message_mock.channel.send.assert_awaited_once_with(AnyStringWith('You have be removed from the **RS 11 Queue** due to acitivty timeout.\n\nPlease rejoin RS 11 Queue in'))	# send via message object -> in this case as DM
	# TODO: Check the following actions
	#	1.delete users from RSQueue
    #	2.update queue status to channel

	qm.queueCheck.cancel()
 
@pytest.fixture()
def handelReactionFixure(monkeypatch):
	td = handelReactionTestDataAndMocks(monkeypatch)
	return td

@pytest.mark.asyncio
async def test_handelReactionWithReactionForSomethingElseNotMatchingStaleUser(handelReactionFixure):
	
	td = handelReactionFixure


	td.mock_MemberInfo_now.side_effect = [td.timeNow] # when have two periods to test for
													  #    a) idle timeout of 15
													  #    b) idele message timeout of 5min
 
	qm = RSQueueManager(td.bot_mock)
	qm.privateMessages = td.expected_privateMessages
	
	# Mock setup for this test: matching user and MemberInfo 
	td.user_mock.id = 00000 # user id of something user i.e not the stale user
	td.rsqueue_mock.members = []
	td.rsqueue_mock.members.append(td.expected_memInfo)	# info regarding stale user in queue
	td.expected_memInfo.timeSinceLastQueueActivity = td.timeNow
    
	#rsqueue_mock.privateMessages = expected_privateMessages
	stalemembers_mock = MagicMock
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = td.rsqueue_mock


	# method under test
	await qm.handelReaction(td.reaction_mock, td.user_mock)

	assert len(qm.privateMessages) == 1
	assert qm.qs[11].members[0] == td.expected_memInfo #this should be the stale message
	assert qm.qs[11].members[0].timeSinceLastQueueActivity == td.timeNow

	qm.queueCheck.cancel()
 
@pytest.mark.asyncio
async def test_handelReactionWithMatchingStaleUserId(handelReactionFixure):
	
	td = handelReactionFixure

	td.mock_MemberInfo_now.side_effect = [td.timeNow] # when have two periods to test for
													  #    a) idle timeout of 15
													  #    b) idele message timeout of 5min
 
	qm = RSQueueManager(td.bot_mock)
	qm.privateMessages = td.expected_privateMessages
	
	# Mock setup for this test: matching user and MemberInfo 
	td.user_mock.id = td.expected_memInfo.userId # user id of the stale user
	td.rsqueue_mock.members = []
	td.rsqueue_mock.members.append(td.expected_memInfo)	# info regarding stale user in queue
	td.expected_memInfo.timeSinceLastQueueActivity = td.timeNow
    
	#rsqueue_mock.privateMessages = expected_privateMessages
	stalemembers_mock = MagicMock
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = td.rsqueue_mock


	# method under test
	await qm.handelReaction(td.reaction_mock, td.user_mock)

	assert len(qm.privateMessages) == 1
	assert qm.qs[11].members[0] == td.expected_memInfo #this should be the stale message
	assert qm.qs[11].members[0].timeSinceLastQueueActivity == td.timeNow

	qm.queueCheck.cancel()
 
@pytest.mark.asyncio
async def test_handelReactionWithMatchingStaleUserIdAndTickEmojiClicked(handelReactionFixure):
	
	td = handelReactionFixure

	td.mock_MemberInfo_now.side_effect = [td.timeNow] # when have two periods to test for
													  #    a) idle timeout of 15
													  #    b) idele message timeout of 5min
 
	qm = RSQueueManager(td.bot_mock)
	qm.privateMessages = td.expected_privateMessages
	
	# Mock setup for this test: matching user and MemberInfo 
	td.user_mock.id = td.expected_memInfo.userId # user id of the stale user
	td.rsqueue_mock.members = []
	td.rsqueue_mock.members.append(td.expected_memInfo)	# info regarding stale user in queue
	td.expected_memInfo.timeSinceLastQueueActivity = td.timeNow
	td.reaction_mock.emoji = "✅" # reaction to stay in queue
	#rsqueue_mock.privateMessages = expected_privateMessages
	stalemembers_mock = MagicMock
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = td.rsqueue_mock

	# method under test
	await qm.handelReaction(td.reaction_mock, td.user_mock)
 
 	#	MagicMock.assert_called_once()
	td.message_mock.channel.send.assert_called_once()

	assert len(qm.privateMessages) == 0
	assert qm.qs[11].members[0] == td.expected_memInfo
	assert qm.qs[11].members[0].isStalechecking == False
	assert qm.qs[11].members[0].timeSinceLastQueueActivity == td.timeNow
	
	qm.queueCheck.cancel()