from typing import List
import discord
import asyncio
import pprint
import typing

class Command_Manager: pass

class DiscordCommand():
	def __init__(self, command_prefix : str, cm : Command_Manager, roleReq : str = None):
		self.command_prefix = command_prefix
		self.command_manager : Command_Manager = cm
		
		if (roleReq == None):
			self.permission = "@everyone"
		else:	
			self.permission = roleReq

		cm.register(self)

	def getPrefix(self):
		return (self.command_manager.prefix_char + self.command_prefix)

	def getHelpStr(self):	# probably turn this into a abstract method?
		helpStr = 'Default Help'
		return (helpStr)

	def getPermission(self):
		return (self.permission)

	async def executeCommand(self, message : discord.Message):
		print ('Base Command')
		pass

class Command_Manager():

	def __init__(self, prefix_char : str = '$'):
		#self.commands : List[DiscordCommand] = []
		self.prefix_char = prefix_char
		self.commands : typing.Dict[str, DiscordCommand] = {}
		self.helpData = []

	def register(self, c : DiscordCommand):
		#self.commands.append(c)
		self.commands[c.getPrefix()] = c
		self.addHelpInfo(c)
		#print (type(self.commands))

	def get_Command_Count(self):
		return len(self.commands.keys())

	def addHelpInfo(self, c: DiscordCommand):
		self.helpData.append((c.getPrefix() + " Permission: " + c.getPermission(), c.getHelpStr()))

	def getHelp(self):
		return self.helpData

	def printHelp(self):
		pprint.pprint(self.helpData)
		for elem in self.helpData:
			print("{0}\t\t{1}".format(elem[0], elem[1]))

	async def executeCommand(self, command_str : str, message : discord.Message = None):
		if (command_str in self.commands.keys()):
			#print ('Found Command ' + command_str)
			await self.commands[command_str].executeCommand(message)
			return None
		else:
			return 'Command {0} not found! Try $help for more help information'.format(command_str)

# def somefuntion():
# 	print ('In someFunction')
# async def dummyMain():

# 	cm = Command_Manager()
# 	c1 = command_help.HelpCommand('help', cm)
# 	c2 = command_ver.VersionCommand('ver', cm)

# 	print ('Number of Commands Regisered: {}'.format(cm.get_Command_Count()))
# 	if (err_str := await cm.executeCommand('$help', None)) != None:
# 		print (err_str)

# 	if (err_str := await cm.executeCommand('$ver', None)) != None:
# 		print (err_str)

# 	#await cm.executeCommand('$ver', None)

# 	cm.printHelp()

if __name__ == '__main__':
	# asyncio.run(dummyMain())
	pass	
	# functPtr : 'function' = somefuntion
	# print (type(functPtr))
	# functPtr()
