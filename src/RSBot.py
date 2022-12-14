from botSystem import BUILD_TYPE
from inspect import getmembers
from sys import prefix

import os
from urllib import response
import discord.utils
import asyncio 
import logging
from typing import *
from botenv import getEnvKey
from botversion import getVersion
from pathlib import Path, PurePath

import discord
from discord import Reaction, User, types, app_commands, errors
from discord.ext import commands

from rsbot_logger import rslog, FORMAT

#from discord.ext.commands.bot import PrefixType

from discord.ext.commands._types import *

from cogs.RSQueue.RSQueue import RSQueueManager
from cogs.BotInfo import BotInfo

logger = logging.getLogger('discord')

if BUILD_TYPE == BUILD_TYPE.RELEASE:
	logger.setLevel(logging.WARN)
	fileHandler = logging.FileHandler("{0}/{1}".format('.', 'discord.log'))
	logger.addHandler(fileHandler)
else:
    logger.setLevel(logging.INFO)
    streamHandler = logging.StreamHandler()
    fileHandler = logging.FileHandler("{0}/{1}".format('.', 'discord.log'))
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

help_cmd = commands.DefaultHelpCommand(show_parameter_descriptions=False, no_category='General')
client : commands.Bot = commands.Bot(intents=discord.Intents.all(), 
									 command_prefix="-", 
									 help_command=help_cmd,
									 guilds = [discord.Object(id=939859311847415818)])

# cm = command.Command_Manager()

# @client.command()
# async def sync(ctx : commands.Context, *args):
# 		fmt = await ctx.bot.tree.sync()
# 		await ctx.send(f'Synced {len(fmt)} commands to current guild')
# 		return
@client.event
async def on_command_error(ctx, exception):

	if isinstance(exception, commands.CommandNotFound):  # fails silently
		pass

	# elif isinstance(exception, send_help):
    #     _help = await send_cmd_help(ctx)
    #     exception ctx.send(embed=_help)

	elif isinstance(exception, commands.MissingRole):
		await ctx.send(f'You do not have **permission** to run this command.\n' +
					   f'Please contact the server admin for more information.\n')


@client.event
async def on_ready():

	rslog.info('We Have logged in as {0.user}'.format(client))


@client.event
async def on_reaction_add(reaction : Reaction, user : User):
	rslog.debug(f'Add Reaction by {user.name} {user.id}')
	
	if user.id == client.user.id:
		return

	rsManager : RSQueueManager = client.get_cog("RS Queue")

	await rsManager.handelReaction(reaction, user)

async def main():
	TYPE_CHECKING = False
	rslog.info("Starting RSBot")

	# HelpCommand('help', cm)

	
	# await client.load_extension(name="RSQueueManager")

	path = PurePath("./src/cogs")
	rslog.debug(f"Using Path to find cogs: {path}") 

	for module in os.listdir(path):
		path_to_cog = path.joinpath(f"{module}/{module}.py")
		rslog.debug(f'Cog Filename: {path_to_cog}')
		if os.path.exists(path_to_cog):
			rslog.info(f'Loading Cog: cogs.{module}.{module}')
			await client.load_extension(name=f"cogs.{module}.{module}")

	sBotInfo : BotInfo = client.get_cog("BotInfo")
	sBotInfo.setSoftwareId(getVersion())


	if (BUILD_TYPE == BUILD_TYPE.RELEASE):
		# Live Released Bot
		await client.start(getEnvKey('TOKEN'))
	else:
		# Test Bot
		await client.start(getEnvKey('TEST_BOT_TOKEN'))
	
if __name__ == '__main__':
	asyncio.run(main())