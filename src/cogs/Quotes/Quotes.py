from aiohttp import request
import asyncio
import threading
from threading import Thread
import discord
from discord import Embed
from typing import Any, Dict, List

from pprint import pprint
import json

from discord.ext import commands

class Quotes(commands.Cog, name="Quotes"):

	URL='https://labs.bible.org/api/?passage=random&type=json'
 
	def __init__(self, bot : commands.Bot) -> None:
		super().__init__()
		self.bot = bot
		self.bibleQuote = {}


# [{'bookname': '2 Samuel',
#   'chapter': '2',
#   'text': 'So David sent messengers to the people of Jabesh Gilead and told '
#           'them, “May you be blessed by the Lord because you have shown this '
#           'kindness to your lord Saul by burying him.',
#   'verse': '5'}]


	# ?passage=random&type=json
	# content_type='text/html'
	async def getBibleVerse(self):
		async with request(method="GET", url=Quotes.URL, headers={},  ) as response:
			if response.status == 200:
				data = await response.text()
				d = json.loads(data)
    
				self.bibleQuote = d
				pprint(d)
				return d

			return None

	@commands.command()
	async def quote(self, ctx : commands.Context, *args):
		emb = discord.Embed(title=f"✝ Quote of the Day ✝", 
                      description="\u200b", 
                      color=discord.Color.brand_green())
		quote = await self.getBibleVerse()
		quote = quote[0]
		emb = emb.add_field(name = f"{quote['bookname']} {quote['chapter']} : {quote['verse']}",
                         	value = f"{quote['text']}")
  
		await ctx.channel.send(embed=emb)


async def setup(bot : commands.bot):
    print ("Loading Cog: Qutotes")
    await bot.add_cog(Quotes(bot), guilds = [discord.Object(id=939859311847415818)])
    
    
# async def main():
# 	t = asyncio.create_task(getBibleVerse())
# 	await t	
# if __name__ == '__main__':
# 	#e = threading.Event()
# 	asyncio.run(main())
