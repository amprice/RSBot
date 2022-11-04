from typing import List
import discord
import asyncio
import pprint
import typing
from command import DiscordCommand, Command_Manager

class HelpCommand(DiscordCommand):
	
	def __init__(self, command_prefix : str, cm : Command_Manager):
		super(HelpCommand, self).__init__(command_prefix, cm)

	async def executeCommand(self, message : discord.Message):
		#print ('Help Command Execute')
		self.command_manager.getHelp()
		if message != None:
			embed = discord.Embed(color=discord.Color.blue(), title='Command')
			#embed.add_field(name='aaaaaa', value='bbbbbb', inline=True)
			for c in self.command_manager.helpData:
				#pprint(c)
				embed.add_field(name=c[0], value=c[1], inline=False)
			await message.channel.send(embed=embed)
			#await message.channel.send(self.command_manager.getHelp())
		#return self.command_manager.getHelp()

	def getHelpStr(self):
		helpStr = 'Shows all the supported bot commands.'
		return (helpStr)


async def dummyMain():

	cm = Command_Manager()
	c1 = HelpCommand('help', cm)

	print ('Number of Commands Regisered: {}'.format(cm.get_Command_Count()))
	if (err_str := await cm.executeCommand('$help', None)) != None:
		print (err_str)

	cm.printHelp()

if __name__ == '__main__':
	asyncio.run(dummyMain())
	
	# functPtr : 'function' = somefuntion
	# print (type(functPtr))
	# functPtr()
