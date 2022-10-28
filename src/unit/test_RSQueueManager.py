from contextlib import AsyncContextDecorator
import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch, call

import collections
import asyncio
import pprint
from datetime import datetime

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from RSQueue import MemberInfo, RSQueue
from mongodb import Mongodb

from RSQueueManager import PrivateMessage, RSQueueManager
import discord
from discord.ext import commands, tasks

class AnyStringWith(str):
    def __eq__(self, other):
        return self in other

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

	qm = RSQueueManager(bot_mock)

	await qm.l(qm, context_mock, "queue_cfg", "foo", "bar")

	calls = [call(name="RS5", value="Not Configured", inline=False),
			 call(name="RS6", value="Not Configured", inline=False),
			 call(name="RS7", value="Not Configured", inline=False),
			 call(name="RS8", value="Not Configured", inline=False),
			 call(name="RS9", value="Not Configured", inline=False),
			 call(name="RS10", value="Not Configured", inline=False),
			 call(name="RS11", value="Not Configured", inline=False)]
	
	emb_mock.add_field.assert_has_calls(calls=calls, any_order=False)
	
	# assert 1==0

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

	qm = RSQueueManager(bot_mock)

	qm.qs[11] = rsqueue_mock

	# method under test
	await qm.l(qm, context_mock, "queue_cfg", "foo", "bar")

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
	
	# assert 1==0

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
	# for key in qm.qs.keys():
	# 	assert
	# level : int = int(args[0])
	# name : str = args[1]
	# role : str = args[2]
	# refresh : int = int(args[3])

# def dummyTest(*args):
# 	print (*args)
# 	print (args[1])

# if __name__ == '__main__':

# 	print ("abc", "123", "1111")
# 	dummyTest("abc", "123", "1111")

@pytest.mark.asyncio
async def test_s_QueueStartCommand(monkeypatch):

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
	await qm.s(qm, context_mock, "11")

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

	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = rsqueue_mock

	# method under test
	result = qm.buildStaleEmbed(rsqueue_mock)

	assert result != None
	assert result.description == AnyStringWith("Do you want to remain in the queue?")
	assert result.title == AnyStringWith("RS 11 Queue")
	assert result.color == discord.Color.magenta()




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
	stalemembers_mock = MagicMock
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = rsqueue_mock

	# method under test
	result = await qm.CheckForStaleMembers(rsqueue_mock)

	assert result == True
	assert len(qm.privateMessages) == 1

	calls = [call("✔"),
			 call("❌")]
	
	message_mock.add_reaction.assert_has_calls(calls=calls, any_order=False)




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
	rsqueue_mock.members = MagicMock()
	rsqueue_mock.getQueueMembers = MagicMock(return_value=expected_members)
	rsqueue_mock.getStaleMembers = MagicMock(return_value=expected_userId_stale_members)
	rsqueue_mock.getStaleMembersWhoTimedOut = MagicMock(return_value=expected_userId_stale_members)

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

	calls = [call("✔"),
			 call("❌")]
	
	message_mock.remove_reaction.assert_has_calls(calls=calls, any_order=False)
	channel_mock.send.assert_awaited_once_with(AnyStringWith('has timed out and been removed from RS 11 Queue'))  # send via channel object obtained from guild return -> guild channel
	message_mock.channel.send.assert_awaited_once_with(AnyStringWith('You have be removed from the **RS 11 Queue** due to acitivty timeout.\n\nPlease rejoin RS 11 Queue in'))	# send via message object -> in this case as DM



@pytest.mark.asyncio
async def test_handelReaction(monkeypatch):
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

	timeStaleExpiredTime : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=10, second=0)
	timeNow : datetime = datetime(year=2022, month=10, day=25, hour=14, minute=15, second=0)

	expected_dummy_string = 'Message from the bot that the user will react too.'
	expected_memInfo = MemberInfo(name="Jesus", userId=10000, queue="RS11", guildId=1111)
	
	expected_members = [expected_memInfo]
	expected_userId_stale_members = [expected_memInfo]
	
	mock_MemberInfo_now = MagicMock(return_value=timeStaleExpiredTime)
	monkeypatch.setattr(MemberInfo, 'now', mock_MemberInfo_now)

	message_mock = AsyncMock(spec=discord.Message)
	message_mock.add_reaction = AsyncMock()
	message_mock.remove_reaction = AsyncMock()
	message_mock.channel = AsyncMock()
	message_mock.channel.send = AsyncMock()
	message_mock.content = expected_dummy_string
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
	rsqueue_mock.members = expected_members
	rsqueue_mock.getQueueMembers = MagicMock(return_value=expected_members)
	rsqueue_mock.getStaleMembers = MagicMock(return_value=expected_members)
	rsqueue_mock.getStaleMembersWhoTimedOut = MagicMock(return_value=expected_members)

	expected_privateMessage = PrivateMessage(message=message_mock, userId=10000, queue=rsqueue_mock, memInfo=expected_memInfo)
	expected_privateMessages = [expected_privateMessage]

	reaction_mock = MagicMock(spec=discord.Reaction)
	reaction_mock.message = MagicMock()
	reaction_mock.message.channel = MagicMock()
	reaction_mock.message.content = expected_dummy_string
	reaction_mock.emoji = "✔"
	user_mock = MagicMock(spec=discord.User)
	user_mock.dm_channel = reaction_mock.message.channel

	#mock_MemberInfo_now.side_effect = [timeStaleExpiredTime, timeNow]
	mock_MemberInfo_now.side_effect = [timeNow]
	qm.privateMessages = expected_privateMessages
	#rsqueue_mock.privateMessages = expected_privateMessages
	stalemembers_mock = MagicMock
	embed_mock = MagicMock(spec=discord.Embed)
	# monkeypatch.setattr(embed_mock, 'findRecord', mockDb.findRecord)	

	qm.qs[11] = rsqueue_mock


	# method under test
	await qm.handelReaction(reaction_mock, user_mock)

	assert len(qm.privateMessages) == 0
	assert qm.privateMessages == []
	assert qm.qs[11].members[0].staleMessage == None
	assert qm.qs[11].members[0].isStalechecking == False
	assert qm.qs[11].members[0].timeSinceLastQueueActivity == timeNow

# async def handelReaction(self, reaction : Reaction, user : User):
#         print ('handleReaction')
#         if (user.dm_channel == reaction.message.channel):
#             #private channel reactions
#             for h in self.privateMessages:
#                 if (h.message.content == reaction.message.content):
#                     #check which emoji clicked
#                     if reaction.emoji == '✔':
#                         # accept stay in queue
#                         # 1. update user timout update to now()
#                         h.memeberInfo.refreshStaleStatus()

#                         # 2. remove message from handler message list
#                         self.privateMessages.remove(h)

#                     elif reaction.emoji == '❌':
#                         # reject leave queue
#                         h.queue.delUser(user.id)
#                         await self.sendQueueStatus(h.queue)