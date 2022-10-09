import discord
import os
from env import getToken
from botversion import getVersion

softwareVersion = ""
client = discord.Client(intents=discord.Intents.all())
#client = discord.Client()

@client.event
async def on_ready():
	print('We Have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	#print('Got event with message {0}'.format(message.content))
	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')

	if message.content.startswith('$ver'):
		await message.channel.send(softwareVersion)

#client.run(os.getenv('TOKEN'))
print("Starting RSBot")
softwareVersion = getVersion()
client.run(getToken())

