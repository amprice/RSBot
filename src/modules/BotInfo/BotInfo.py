import asyncio

import discord
from discord import User, Member, DMChannel, Reaction, app_commands
from discord.ext import commands, tasks


from datetime import datetime

import pprint
import typing

GUILD = discord.Object(id=939859311847415818)

class BotInfo(commands.Cog, name="BotInfo"):

	def __init__(self, bot : commands.Bot) -> None:
		super().__init__()
		self.bot = bot
		self.softwareId = ""


	def setSoftwareId(self, sid : str):
		self.softwareId = sid


	
	@app_commands.command(name='test', description='describe test')
	@app_commands.describe(name='name to say hello')
	async def test(self, interaction: discord.Interaction, name: str):
		await interaction.response.send_message(f"hello {name}!")


	@app_commands.command(name='connect', description='Associated and initialises RS Queue with Discord channel')
	@app_commands.describe(level='Connects RS queue to your discord server.')
	@app_commands.choices(level=[
		discord.app_commands.Choice(name='level 5', value=5),
		discord.app_commands.Choice(name='level 6', value=6),
		discord.app_commands.Choice(name='level 7', value=7),
		discord.app_commands.Choice(name='level 8', value=8),
		discord.app_commands.Choice(name='level 9', value=9),
		discord.app_commands.Choice(name='level 10', value=10),
		discord.app_commands.Choice(name='level 11', value=11)])
	@app_commands.describe(queuename='String name of the queue this will be shown in queue messages')
	@app_commands.describe(rolename='The role name from discord server to be used for the queue. Used in queue and user pings')
	@app_commands.describe(refreshrate='Set the peoid in minutes, at which queue message get to channel when queue is idle')
	async def connect(self, interaction: discord.Interaction, level: int, queuename: str, rolename: str, refreshrate: int):
		await interaction.response.send_message(f"You said {level} {queuename} {rolename} {refreshrate}min ")


	@app_commands.command(name='help', description='Provides RS Queue Bot Help')
	@app_commands.describe(subcommand='TBD')
	async def help(self, interaction: discord.Interaction, subcommand: str):
		await interaction.response.send_message(f"You said {subcommand}")

	@commands.command()
	async def ver(self, ctx : commands.Context, *args):
		''' Shows the bot software version identified.

			e.g. Vx.y-build_hash
			
			Bot Supports:
				RS Queue Management
		'''
		await ctx.send(self.softwareId)

	@commands.command(hidden=True)
	async def sync_slash(self, ctx : commands.Context, *args):
			fmt = await ctx.bot.tree.sync(guild = discord.Object(id=939859311847415818))
			await ctx.send(f'Synced {len(fmt)} commands to guild')
			return

	@commands.command(hidden=True)
	async def clear_slash(self, ctx : commands.Context, *args):
			ctx.bot.tree.clear_commands(guild = discord.Object(id=939859311847415818))
			await ctx.send(f'Cleared slash commands from guild')
			return

async def setup(bot : commands.bot):
    print ("Addint BotInfo Cog")
    await bot.add_cog(BotInfo(bot), guilds = [discord.Object(id=939859311847415818)])
