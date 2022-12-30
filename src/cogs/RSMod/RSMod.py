import asyncio
import discord
from discord import User, Member, DMChannel, Reaction, app_commands, Message
from discord.ext import commands, tasks

from datetime import datetime
from rsbot_logger import rslog
from emoji import emoji, Mods

from discord.ui import Button, View

import pprint
import typing

class RSModView(View):
    def __init__(self, buildEmbCallback, rsModCompleteCallback, rsModCancelledCallback, timeout: float = 0):
        super().__init__(timeout=timeout)
        self.buildEmbCallback = buildEmbCallback
        self.rsModCompleteCallback = rsModCompleteCallback
        self.rsModCancelledCallback = rsModCancelledCallback
        
        mods = Mods()
        for key in mods.status:
            b = Button(style=discord.ButtonStyle.grey, emoji=emoji[key], custom_id=key)
            b.callback = self.buttonCallback
            self.add_item(b)
         
        acceptButton = Button(row=4, style=discord.ButtonStyle.green, emoji='<:tick_mark:1056560138137378837>')
        acceptButton.callback = self.acceptButtonCallback
        
        cancelButton = Button(row=4, style=discord.ButtonStyle.red, emoji='<:cross_mark:1056558747520077934>')
        cancelButton.callback = self.cancelButtonCallback
        
        self.add_item(acceptButton)
        self.add_item(cancelButton)
    
    async def buttonCallback (self, interaction : discord.Interaction):
        emb = self.buildEmbCallback(interaction.user.id, interaction.data["custom_id"])
        await interaction.response.edit_message(embed=emb)
    
    async def acceptButtonCallback (self, interaction : discord.Interaction):
        self.rsModCompleteCallback(interaction.user.id)
        await interaction.response.send_message("RSMods Saved")
        await interaction.message.delete()
    
    async def cancelButtonCallback (self, interaction : discord.Interaction):
        self.rsModCancelledCallback(interaction.user.id)
        await interaction.response.send_message("RSMod Change Cancelled!")
        await interaction.message.delete()
    
class RSMod(commands.Cog, name="RSMod"):
    def __init__(self, bot : commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        #self.bot.add_listener(self.on_reaction_add, "on_reaction_add")
        self.rsmodMessages : typing.List[Message] = []
        self.userMods : typing.Dict[int, Mods] = {}
        
    # async def on_reaction_add(self, reaction : Reaction, user : User):
        
    #     # Ignore bot notifiations for reactions
    #     if user.id == self.bot.user.id:
    #         return

    #     if (len(self.rsmodMessages) == 0):
    #         return
    def rsModCancelled(self, userId : int):
        del self.userMods[userId]
        
    def rsModComplete(self, userId : int):
        rsQueueCog = self.bot.get_cog("RS Queue")
        rsQueueCog.setRSMod(userId, self.userMods[userId])
        del self.userMods[userId]
        
    async def setEmojis(self, msg : Message, rsmods : Mods):
        for key in rsmods.status:
            if rsmods.status[key] == False:
                await msg.add_reaction(emoji[key])
        

    @commands.command()
    async def rsmod(self, ctx : commands.Context, *args):
        '''Begin an Interactive RS Mods selection with bot 

           Usage: -rsmod
        '''
        rsQueueCog = self.bot.get_cog("RS Queue")
        guild = ctx.author.guild
        m : Member = guild.get_member(ctx.author.id)
        #rsmods = Mods()
        rsmods = rsQueueCog.getRSMod(ctx.author.id)
        rsmods.guild = guild
        emb = self.buildRSModMessage(guild, rsmods)

        

        self.userMods[ctx.author.id] = rsmods
        
        await m.create_dm() #private DM channel with potentially stale member
        msg = await m.send(embed=emb, view=RSModView(self.buildEmbCallback, self.rsModComplete, self.rsModCancelled))
        # await self.setEmojis(msg, rsmods)
        #await msg.add_reaction('➕')
        #await msg.add_reaction('➖')
        # await msg.add_reaction('✅')
        # await msg.add_reaction('❎')
        self.rsmodMessages.append(msg)

    def buildEmbCallback(self, userId : int, rsmodKey : str):
        self.userMods[userId].status[rsmodKey] = not self.userMods[userId].status[rsmodKey]
        return self.buildRSModMessage(self.userMods[userId].guild, self.userMods[userId])
        
    def buildRSModMessage(self, guild : discord.Guild, rmsmod : Mods):
        #timeInQueue : int = int((datetime.now() - user.timeInQueue).total_seconds() / 60)
        emb = discord.Embed(title=f"<:redstar:1032938394562613248> Welcome to RSMod Builder",
                      description=f"Here you can select your RS Mods you want to show other when you join Red Star Queues\n\n",
                                  color=discord.Color.magenta())

    
        emb.add_field(value = f"Your RSMods: {rmsmod.modString()}\n\n",
                              name = '\u200b',
                              inline=False)
        
        emb.add_field(value = f"Click the emoji buttons below to add/remove your mods.\n\n" + 
                              f"**Please click buttons ✅ to accept or ❎ to cancel.**\n",
                              name = '\u200b',
                              inline=False)
        #emb.set_footer(text=f"Your emoji's selected are: TBA", icon_url=None)

        emb.set_thumbnail(url=guild.icon.url)
        return emb
    
    
async def setup(bot : commands.bot):
    rslog.debug("Adding Cog: RSMod")
    await bot.add_cog(RSMod(bot), guilds = [discord.Object(id=939859311847415818)])
