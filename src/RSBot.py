from inspect import getmembers
from sys import prefix
import discord
from discord import Reaction, User
import os
import RSQueueManager
import discord.utils
import asyncio 
import logging

from botenv import getEnvKey
from botversion import getVersion

import command
from command_help import HelpCommand
from command_ver import VersionCommand

from discord.ext import commands

from RSQueueManager import RSQueueManager
from modules.BotInfo.cog import BotInfo

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)

help_cmd = commands.DefaultHelpCommand(show_parameter_descriptions=False)
client : commands.Bot = commands.Bot(intents=discord.Intents.all(), command_prefix="-", help_command=help_cmd)

cm = command.Command_Manager()

@client.event
async def on_ready():
	print('We Have logged in as {0.user}'.format(client))

@client.event
async def on_reaction_add(reaction : Reaction, user : User):
	print ('on_reaction_add')
	
	if user.id == client.user.id:
		return

	rsManager : RSQueueManager = client.get_cog("RSQueueManager")
	await rsManager.handelReaction(reaction, user)

async def main():
	print("Starting RSBot")

	# HelpCommand('help', cm)

	await client.load_extension(name="RSQueueManager")

	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			await client.load_extension(name=f"modules.{folder}.cog")

	sBotInfo : BotInfo = client.get_cog("BotInfo")
	sBotInfo.setSoftwareId(getVersion())

	await client.start(getEnvKey('TOKEN'))
	
if __name__ == '__main__':
	asyncio.run(main())