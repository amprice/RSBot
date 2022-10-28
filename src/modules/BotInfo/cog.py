import asyncio

import discord
from discord import User, Member, DMChannel, Reaction
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
	
	@commands.command()
	async def ver(self, ctx : commands.Context, *args):
		await ctx.send(self.softwareId)

async def setup(bot : commands.bot):
    print ("Addint BotInfo Cog")
    await bot.add_cog(BotInfo(bot))
