from inspect import getmembers
from sys import prefix
import discord
import os
import RSQueueManager
import discord.utils
import asyncio 
import logging

from botenv import getEnvKey
#from botversion import getVersion

import command
from command_help import HelpCommand
from command_ver import VersionCommand

from discord.ext import commands

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)

#softwareVersion = ""
#client = discord.Client(intents=discord.Intents.all())
help_cmd = commands.DefaultHelpCommand(show_parameter_descriptions=False)
client : commands.Bot = commands.Bot(intents=discord.Intents.all(), command_prefix="-", help_command=help_cmd)

cm = command.Command_Manager()

#rsQueue = RSQueue.Queue('dummy11111')

@client.event
async def on_ready():
	print('We Have logged in as {0.user}'.format(client))

#@client.event
async def on_message(message : discord.Message):
	if message.author == client.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello {1}! Welcome to #{0} channel!'.format(message.channel.name, message.author.mention))
		await message.channel.send(message.author.id)
		user = client.get_user(message.author.id)
		await message.channel.send(user.mention)
		await message.channel.send(message.channel.__str__)
	#elif message.content.startswith('$ver'):
	#	await message.channel.send(softwareVersion)
	elif message.content.startswith(cm.prefix_char):
		# try execute command
		cmd = message.content.split(' ', 1)[0]
		#await message.channel.send('Echo: {0}'.format(cmd))
		err_str = await cm.executeCommand(cmd, message)
		if err_str != None:
			await message.channel.send(err_str)
		#await message.channel.send(cm.executeCommand(cmd, message))

	#if message.content.startswith('$q'):
	#	await rsQueue.printQueue(message.channel)

async def main():
	print("Starting RSBot")
	#softwareVersion = getVersion()

	HelpCommand('help', cm)
	VersionCommand('ver', cm)
	await client.load_extension(name="RSQueueManager")

	#await client.run(getEnvKey('TOKEN'))
	await client.start(getEnvKey('TOKEN'))
	

if __name__ == '__main__':
	asyncio.run(main())