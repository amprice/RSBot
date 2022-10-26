import asyncio
from contextvars import Context
from email import message
from inspect import _ParameterKind
from multiprocessing import context
from tracemalloc import start
from unicodedata import name
import discord
from discord import User, Member, DMChannel
from discord.ext import commands, tasks

from mongodb import Mongodb
import pprint
from enum import Enum
import typing
from RSQueue import RSQueue
from typing import Dict

emoji : Dict[str, str] = {
    "nosanc": "<:nosanc:1032935233298903100>",
    "omega_shield": "<:omega_shield:1032943691981139998>",
    "passive_shield" : "<:passive_shield:1032938383170875423>",
    "dart" : "<:dart1:1032938403941060648>",
    "barrage" : "<:barrage:1032938379475685376>",
    "laser" : "<:laser:1032938402141720576>",
    "dual_laser": "<:dual_laser:1032943690135650314>",
    "mass" : "<:mass:1032938405786570813>",
    "batt" : "<:batt:1032938399830650911>",
    "suppress" : "<:suppress:1032938392603873350>",
    "unity" : "<:unity:1032938390812897330>",
    "rse" : "<:rse:1032938388896104478>",
    "tw" : "<:tw:1032938387021254657>",
    "bond" : "<:bond:1032938381266649098>",
    "veng" : "<:veng:1032938377680535552>",
    "remote" : "<:remote:1032938375629520926>",
    "tele" : "<:tele:1032938373658185768>",
    "no_tele" :"<:notele:1033163905540821063>",
    "solo1": "💪",
    "solo2" : "🦾",
    "croid" : "<:croid:1032938396353560576>",
    "time": "🕒",
     "obstain" : "✊",
     "upvote" : "👍",
     "downvote" : "👎"
}
class RSQueueManager(commands.Cog):
    """string A"""

    qs : typing.Dict[int, RSQueue] = {
        5: None,
        6: None,
        7: None,
        8: None,
        9 : None,
        10 : None,
        11 : None
    }
    # async def invoke_after(self, ctx : commands.context):
    #     self.queueCheck.start()

    def __init__(self, bot : commands.Bot):
        self.bot : commands.Bot = bot
        self.queueCheck.start()
        for key in RSQueueManager.qs:
            q = RSQueue(queueId=key)
            if q.name != None:
                RSQueueManager.qs[key] = q

        # self.cog_after_invoke(self.invoke_after)

    @commands.command()
    async def hi(self, ctx : commands.Context, *args, **kwargs):
        """string B"""
        print(args.__str__())
        await ctx.send(ctx.message.channel.__str__)
        await ctx.send("Pong")

    @commands.command()
    async def connect(self, ctx : commands.Context, *args):
        """ connects queue to discord channel

        Usage: -connect <Level> <name> <role> <optional: queue refresh rate> 

        Example: -c 8 "RS8 Queue" RS8 15

        Arguments: 
        <Level> = integer for RS Queue Level
        <name> = text based name for the queue
        <role> = discord role to use for the queue
        <optional: Queue Refresh rate> = Optional time in minutes to refresh queue when idle
        """
        
        # store 
        #   channel id : Channel Id to be used for automated messaging in task loop
        #   queueName : Text Name for the Queue
        #   role : use role for the queue
        #   

        # check arg len
        print (len(args))
        
        numberArgs = len(args)
        level = 0

        channel : str = ctx.channel.name
        
        if numberArgs == 4:
            level : int = int(args[0])
            name : str = args[1]
            role : str = args[2]
            refresh : int = int(args[3])

        elif numberArgs == 3:
            level : int = int(args[0])
            name : str = args[1]
            role : str = args[2]
            refresh : int = 1
        else:
            await ctx.send("Invalid -connect arguments see -help connect")
            return None

        guild_role = self.getDiscordRole(ctx, role)
        # pprint.pprint(RSQueueManager.qs)
        # await ctx.send(f"{type(level)}")
        if (level in RSQueueManager.qs.keys()):
            if (RSQueueManager.qs.get(level) != None):
                await ctx.send("Queue Already Exists see -help disconnect")
                return None
            else:
                if guild_role == None:
                    await ctx.send(f"Role **\@{role}** does not exist please create if first!")
                    return None
                else:
                    # queueId :str, 
                    # guildId : int = None,
                    # queueName : str = None,
                    # queueRole: str = None,
                    # queueRoleId : int = None,
                    # channel : str = None, 
                    # channelId : int = None, 
                    # refreshRate : float = None
                    created_queue = RSQueue(
                                queueId=level,
                                guildId=ctx.message.guild.id,
                                queueName=name,
                                queueRole=role,
                                queueRoleId=guild_role.id,
                                channel=ctx.channel.name,
                                channelId=ctx.channel.id,
                                refreshRate=refresh)

                    RSQueueManager.qs[level] = created_queue
        else:
            await ctx.send("Invalid RS Level. Use value in the range 5 .. 11")
            return None

        # await ctx.send(ctx.channel.id.__str__()) # 1015814996497813595
        await ctx.send(f"Creating an RS Queue with name \"{name}\" on #{channel}\n" +
            f"\tRS Level = {level}\n" +
            f"\tPing Role = {role}\n" +
            f"\tRole Id = {guild_role.id}\n" +
            f"\tChannel Id = {ctx.channel.id}\n" +
            f"\tQueue Refresh Rate = {refresh} min\n")

        return None

    def getDiscordRole(self, ctx : commands.Context, roleName : str):
        guild = ctx.message.guild
        role = discord.utils.get(guild.roles, name=roleName)
        return role

    def buildQueueConfigEmbed(self, queues : typing.Dict[int, RSQueue]):

        emb = discord.Embed(title="<:redstar:1032938394562613248> Queue Config",
            description="\u200b",
            color=discord.Color.red())

        for key in queues:
                if queues[key] == None:
                    emb.add_field(name=f"RS{key}",
                        value="Not Configured", inline=False)
                else:
                    q : RSQueue = queues[key]

                    emb.add_field(name=f"RS{key}",
                        value=f"databaseId = {q.databaseId}\n" +
                            f"guildId = {q.guildId}\n" +
                            f"queueName = {q.name}\n" +
                            f"queueId = {q.queueId}\n" +
                            f"roleName = &{q.role}\n" +
                            f"roleId = {q.roleId}\n" + 
                            f"channel = #{q.channel}\n" +
                            f"channelId = {q.channelId}\n" +
                            f"refreshRate = {q.refreshRate} min", inline=False)

        return emb

    @commands.command()
    async def i(self, ctx :commands.Context, *args):
        if (len(args) == 1 and self.can_convert_to_int(args[0])):
            queueIndex = int(args[0])

            name = ctx.author.name
            userId = ctx.author.id
            # join queue
            if (RSQueueManager.qs[queueIndex].addUser(userName=name, userId=userId)):
                # added user to queue

                # print updates queue status and ensure lastPrint timestamp is refreshed as to not spam the channel
                q = RSQueueManager.qs[queueIndex]
                q.printMembers() #debug maybe convert to log
                guild = self.bot.get_guild(q.guildId)
                channel = guild.get_channel(q.channelId)
                emb = self.buildQueueEmbed(guild, q)
                q.lastQueueMessage = await channel.send(embed=emb)

                #check to see if queue complete 4/4
                if (q.checkStartQueue()):
                    # Trigger Start Messages
                    botname : str = self.bot.user.__str__()
                    botname = botname.split('#', 1)[0]
                    await self.SendStartQueueMessages(q, botname)
                    # Tell QSQueue we done with current queue
            else:
                #log error
                pass

        else:
            #print help
            pass

    async def SendStartQueueMessages(self, q : RSQueue, startedBy : str):
        guild = self.bot.get_guild(q.guildId)
        channel = guild.get_channel(q.channelId)

        userIds = q.getQueueMemberIds()
        mentionStr = ""

        for userId in userIds:
            mentionStr += f"{guild.get_member(userId).mention} "
            m : Member = guild.get_member(userId)
            await m.create_dm()
            await m.send(f"**Your {q.name} is Ready**\n" +
                            f"You can organize where to run at here {channel.mention}")

        #ping members message queue is ready
        await channel.send(f"**{q.name} Ready**\n\n"+
                            f"Started by **{startedBy}** with **({q.size}/4)**\n" +
                            f"{mentionStr}\n\n" +
                            f"Where to meet OOH or Watchers or somewhere else?")

        #start/clear queue in RSQueue - members
        q.startqueue()

    @commands.command()
    async def o(self, ctx : commands.Context, *args):
        if (len(args) == 1 and self.can_convert_to_int(args[0])):
            queueIndex = int(args[0])

            name = ctx.author.name
            userId = ctx.author.id
            # join queue
            if (RSQueueManager.qs[queueIndex].delUser(userName=name, userId=userId)):
                # added user to queue

                # print updates queue status and ensure lastPrint timestamp is refreshed as to not spam the channel
                q = RSQueueManager.qs[queueIndex]
                q.printMembers() #debug maybe convert to log
                guild = self.bot.get_guild(q.guildId)
                channel = guild.get_channel(q.channelId)
                emb = self.buildQueueEmbed(guild, q)
                q.lastQueueMessage = await channel.send(embed=emb)

                
            else:
                #log error
                pass

        else:
            #print help
            pass
    @commands.command()
    async def s(self, ctx : commands.Context, *args):
        if (len(args) == 1 and self.can_convert_to_int(args[0])):
            queueIndex = int(args[0])
            # having a valid queue number
            if queueIndex in range(5,12):
                q = RSQueueManager.qs[queueIndex]
                #q.printMembers() #debug maybe convert to log
                guild = self.bot.get_guild(q.guildId)
                channel = guild.get_channel(q.channelId)
                if q.size == 0:
                    # nothing to start
                    await channel.send(f"{q.name} ({q.size}/4) is empty and can not be started!")
                    return

                userIds = q.getQueueMemberIds()
                mentionStr = ""

                for userId in userIds:
                    mentionStr += f"{guild.get_member(userId).mention} "
                    m : Member = guild.get_member(userId)
                    await m.create_dm()
                    await m.send(f"**Your {q.name} is Ready**\n" +
                                 f"You can organize where to run at here {channel.mention}")

                #ping members message queue is ready
                await channel.send(f"**{q.name} Ready**\n\n"+
                                    f"Started by **{ctx.author.name}** with **({q.size}/4)**\n" +
                                    f"{mentionStr}\n\n" +
                                    f"Where to meet OOH or Watchers or somewhere else?")

                #start/clear queue in RSQueue - members
                q.startqueue()
        else:
            # show command help
            await ctx.message.channel.send('Invalid arguments: use \'-s <queue_level>\'')

    @commands.command()
    async def l(self, ctx : commands.Context, *args):
        if args[0] == "queue_cfg":
            emb = self.buildQueueConfigEmbed(RSQueueManager.qs)
            await ctx.send(embed=emb)
        else:
            emb = self.buildQueueConfigEmbed(RSQueueManager.qs)
            await ctx.send(embed=emb)

    @commands.command()
    async def start_botloop(self, ctx : commands.Context, *args):
        """Starts the main bot loop for processing bot data and queue refreshes"""
        await ctx.channel.send("Starting Periodic RS Bot Services")
        self.queueCheck.start()

    @commands.command()
    async def stop_botloop(self, ctx : commands.Context, *args):
        """Stops the main bot loop for processing bot data and queue refreshes"""
        await ctx.channel.send("Stopping Periodic RS Bot Services")
        self.queueCheck.cancel()

    @commands.command()
    async def q(self, ctx : commands.Context, *args):
        """Shows the queue status of RSX Queue"""
        """e.g '-q x' where x is the RS level """

        if (len(args) == 1 and self.can_convert_to_int(args[0])):
            queueIndex = int(args[0])

            if (queueIndex in range(4,12)):
            # print updates queue status and ensure lastPrint timestamp is refreshed as to not spam the channel
                q = RSQueueManager.qs[queueIndex]
                
                if q == None:
                    await ctx.message.channel.send("Queue Not Configured")
                else:
                    guild = self.bot.get_guild(q.guildId)
                    channel = guild.get_channel(q.channelId)
                    emb = self.buildQueueEmbed(guild, q)
                    q.lastQueueMessage = await channel.send(embed=emb)
        else:
            await ctx.channel.send("Printing Dummy Queue with RSMods")
            qEmbed = self.printQueueEmbed(ctx)
            await ctx.channel.send(embed=qEmbed[0])


    @tasks.loop(seconds=10.0)
    async def queueCheck(self):
        #self.guild = self.bot.get_guild(1032563230620524615)
        #self.channel = self.guild.get_channel(1015814996497813595)
        # channel = self.bot.get_channel(1015814996497813595)
        # await channel.send("Tick")

        for key in RSQueueManager.qs.keys():
            if RSQueueManager.qs[key] != None:
                q = RSQueueManager.qs[key]
                if (q.isTimeToPrintQueue()): #and q.size != 0):
                    guild = self.bot.get_guild(q.guildId)
                    channel = guild.get_channel(q.channelId)
                    emb = self.buildQueueEmbed(guild, q)
                    if q.lastQueueMessage == None:
                        q.lastQueueMessage = await channel.send(embed=emb)
                    else:
                        q.lastQueueMessage = await q.lastQueueMessage.edit(embed=emb)


    def buildQueueEmbed(self, guild : discord.Guild, queue : RSQueue):
        queue.refreshLastQueuePrint()
        emb = discord.Embed(title=f"<:redstar:1032938394562613248> {queue.name} \t\t ({queue.size}/4)",
            description=f"Use command **-i {queue.queueId}** to join queue and **-o {queue.queueId}** to leave queue\n", #+
                #f"e.g. **-i {queue.queueId}** or **-o {queue.queueId}** \n",
            color=discord.Color.dark_blue())
        emb.set_footer(text="Run ID: TBD", icon_url=None)

        emb.set_thumbnail(url=guild.icon.url)

        if (queue.size == 0):
            emb.add_field(name="\u200b",
                value="**\<QUEUE EMPTY\>**")
        else:
            emb.add_field(value = queue.buildUserStrings(queue.queueId),
                          name = '\u200b')

        # tempTest = f"{emoji['nosanc']} {emoji['barrage']} {emoji['omega_shield']}"

        # emb.add_field(value=f"1\. `LD` \t {tempTest} \t \[5 runs\] \t 🕒 0m\n" +
        #         "2\. `Player 2` some feature based string goes here 🕒 3m \n"
        #         "3\. `Player 3` some feature based string goes here\n" +
        #         "4\. `Player 4` blah blah blah goes here",
        #     name="\u200b")
        return emb

    @queueCheck.before_loop
    async def before_my_task(self):
        await asyncio.sleep(5)
        for key in RSQueueManager.qs.keys():
            if RSQueueManager.qs[key] != None:
                q = RSQueueManager.qs[key]
                guild = self.bot.get_guild(q.guildId)
                channel = guild.get_channel(q.channelId)
                emb = self.buildQueueEmbed(guild, q)
                q.lastQueueMessage = await channel.send(embed=emb)
                await asyncio.sleep(1)
        await self.bot.wait_until_ready()  # wait until the bot logs in


    def printQueueEmbed(self, ctx : commands.Context, queueData = None):
        file = discord.File("resources/red_star.png", filename="red_star.png")
        file_thumbnail = discord.File("resources/Default_Queue_Thumbnail.png", filename="Default_Queue_Thumbnail.png")
        #queue_embed = discord.Embed(color=discord.Color.blue(), title=self.name, description='Dummy Queue Print Test')
        emb = discord.Embed(title="<:redstar:1032938394562613248> RS7 Queue \t\t (4/4)",
            description="Use command **-i x** to join queue and **-o x** to leave queue\n" +
                "e.g. **-i 7** or **-o 7** for RS7\n",
            color=discord.Color.dark_blue())
        # emb.set_author(name="<:redstar:1032938394562613248> RS7 Queue \t\t (4/4)",
        #     icon_url="attachment://red_star.png")
        emb.set_footer(text="Run ID: 39574389230", icon_url=None)

        #emb.set_thumbnail(url="attachment://red_star.png")
        
        # print (ctx.guild.icon.url)
        #emb.set_thumbnail(url=ctx.guild.icon.url)

        guild = self.bot.get_guild(RSQueueManager.qs[7].guildId)
        emb.set_thumbnail(url=guild.icon.url)

        # emb.set_thumbnail(url="attachment://Default_Queue_Thumbnail.png")
        tempTest = f"{emoji['nosanc']} {emoji['barrage']} {emoji['omega_shield']}"

        emb.add_field(value=f"1. `LD` \t {tempTest} \t \[5 runs\] \t 🕒 0m\n" +
                "2. `Player 2` some feature based string goes here 🕒 3m \n"
                "3. `Player 3` some feature based string goes here\n" +
                "4. `Player 4` blah blah blah goes here",
            name="\u200b")
        
        # emb.set_thumbnail(url=None)
        #emb.add_field(name="Members",
        #    value=,
        #         inline=False)
        #emb.add_field(name='\u200b', value="Player 2 some feature based string goes here", inline=False)
        #emb.add_field(name="Player 3 some feature based string goes here", value='\u200b', inline=False)
        #emb.add_field(name="Player 4 some feature based string goes here", value=None, inline=False)
        return (emb, file_thumbnail)


    def emojitesting(self):
        emojiStr = ""
        for key in emoji.keys():
            emojiStr += f"{emoji[key]}"
        emojiStr += "\n"
        return emojiStr

    def create_emoji(self):
        e = discord.emoji.Emoji()
        self.bot.get_guild(id).create_custom_emoji()

    def can_convert_to_int(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

# Configure Queue
# -connect RS7 "RS7 Queue"
# -connect RS8 "RS8 Queue"

# Start/Stop All Queues
# -start
# -stop

# Join Queue
# -i x

# Leave Queue
# -o x

# Start Queue
# -rs7 start

# Refresh Queue

async def setup(bot : commands.bot):
    print ("Adding ext")
    await bot.add_cog(RSQueueManager(bot))

    #RSQueueManager.queueCheck.start()
    # Hard code adding one queue for testing and dev
    #RSQueueManager.q.append(RSQueue())



if __name__ == '__main__':
    #test_bot = commands.Bot(intents=discord.Intents.all(), command_prefix="-")
    #test_cog = RSQueueManager(test_bot)
    # test_message = discord.Message(state=discord.ConnectionState.
    # test_context = commands.Context(message=None, bot=test_bot, view="dummy")
    # test_cog.connect(None)
    #RSQueueManager.qs.append(RSQueue('RS7 Queue', 'RS7', "TestChID"))
    pass
