import asyncio

import discord
from discord import User, Member, DMChannel, Reaction, app_commands
from discord.ext import commands, tasks


from datetime import datetime

import pprint
import typing


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

	
	@commands.command()
	async def ver(self, ctx : commands.Context, *args):
		await ctx.send(self.softwareId)

	@commands.command()
	async def sync_slash(self, ctx : commands.Context, *args):
			fmt = await ctx.bot.tree.sync(guild = discord.Object(id=939859311847415818))
			await ctx.send(f'Synced {len(fmt)} commands to guild')
			return

	@commands.command()
	async def clear_slash(self, ctx : commands.Context, *args):
			ctx.bot.tree.clear_commands(guild = discord.Object(id=939859311847415818))
			await ctx.send(f'Cleared slash commands from guild')
			return

async def setup(bot : commands.bot):
    print ("Addint BotInfo Cog")
    await bot.add_cog(BotInfo(bot), guilds = [discord.Object(id=939859311847415818)])
