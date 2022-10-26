import os
import discord
import sys

sys.path .insert(1, '../')
from botenv import getEnvKey

softwareVersion = ""
testClient = discord.Client(intents=discord.Intents.all())

@testClient.event
async def on_ready():
	print('We Have logged in as {0.user}'.format(testClient))

@testClient.event
async def on_message(message):
	if message.author == testClient.user:
		return

	#print('Got event with message {0}'.format(message.content))
	if message.content.startswith('$echo'):
		await message.channel.send('TestBot Ready to Role')

os.chdir(os.getcwd() + '\..')
print(os.getcwd())
print("Starting TestBot")
testClient.run(getEnvKey("TEST_BOT_TOKEN"))
