import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch, call

import collections
import asyncio
import pprint

import sys
sys.path .insert(1, '../') # allow the unit test files to be in "./unit" folder

from RSQueue import RSQueue
from mongodb import Mongodb

from RSQueueManager import RSQueueManager
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