from typing import List
import discord
import asyncio
import pprint
import typing

from botversion import getVersion
from command import DiscordCommand, Command_Manager

class VersionCommand(DiscordCommand):
	
	def __init__(self, command_prefix : str, cm : Command_Manager):
		super(VersionCommand, self).__init__(command_prefix, cm)
		self.version_string = getVersion()

	async def executeCommand(self, message : discord.Message):
		#print ('Version Command Execute')
		if message != None:
			await message.channel.send(self.version_string)

	def getHelpStr(self):
		helpStr = 'Print the current Version and Hash of the Bot. e.g. V0.1-DEAD'
		return (helpStr)

async def dummyMain1():

	cm = Command_Manager()
	c2 = VersionCommand('ver', cm)

	print ('Number of Commands Regisered: {}'.format(cm.get_Command_Count()))
	if (err_str := await cm.executeCommand('$ver', None)) != None:
		print (err_str)

	cm.printHelp()

if __name__ == '__main__':
	asyncio.run(dummyMain1())
	