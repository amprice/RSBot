import asyncio
# from contextvars import Context
from email import message
from http import client
from inspect import _ParameterKind
# from multiprocessing import context
from tracemalloc import start
from unicodedata import name
import discord
from discord import User, Member, DMChannel, Reaction
from discord.ext import commands, tasks
from datetime import datetime
from mongodb import Mongodb
import pprint
from enum import Enum
import typing
from RSQueue import MemberInfo, RSQueue
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

class PrivateMessage():

    def __init__(self, message : discord.Message, userId : int, queue : RSQueue, memInfo : MemberInfo) -> None:
        self.message : discord.Message = message
        self.userId = userId
        self.queue = queue
        self.memeberInfo = memInfo

    
class RSQueueManager(commands.Cog, name="RS Queue"):
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

    def __init__(self, bot : commands.Bot):
        self.bot : commands.Bot = bot
        self.queueCheck.start()
        for key in RSQueueManager.qs:
            q = RSQueue(queueId=key)
            if q.name != None:
                RSQueueManager.qs[key] = q
        
        self.privateMessages : typing.List[PrivateMessage] = []

    async def handelReaction(self, reaction : Reaction, user : User):
        print ('handleReaction')
        
        #private channel reactions
        for h in self.privateMessages:
            if h.memeberInfo.userId == user.id:
                if (h.message.content == reaction.message.content):
                    #check which emoji clicked
                    guild = self.bot.get_guild(h.queue.guildId)
                    channel = guild.get_channel(h.queue.channelId)
                    if reaction.emoji == '✅':
                        msg = h.message
                        memeber : discord.Member = msg.author
                        # await msg.remove_reaction(emoji='✅', member=memeber)
                        # await msg.remove_reaction(emoji='❎', member=memeber)
                        #await msg.clear_reactions() 
                        await msg.channel.send (f"**You have choosen to remain in the {h.queue.name}**.\n" + 
                                                f"Thankyou for your response {guild.get_member(h.userId).mention}.\n")
                        await msg.delete()
                        # accept stay in queue
                        # 1. update user timout update to now()
                        h.memeberInfo.refreshStaleStatus()

                        # 2. remove message from handler message list
                        self.privateMessages.remove(h)

                    elif reaction.emoji == '❎':
                        msg = h.message
                        memeber : discord.Member = msg.author
                        # await msg.remove_reaction(emoji='✅', member=memeber)
                        # await msg.remove_reaction(emoji='❎', member=memeber)
                        #await msg.clear_reactions()
                        await msg.delete()
                        await msg.channel.send(f"**You have been removed from the {h.queue.name}**\n" +
                                               f"Thankyou for your response {guild.get_member(h.userId).mention}.\n")
                        await channel.send(f"{guild.get_member(h.userId).mention} has timed out and selected to leave {h.queue.name}")
                        # reject leave queue
                        h.queue.delUser(user.name, user.id)
                        await self.sendQueueStatus(h.queue, True)

                        self.privateMessages.remove(h)
                        
    async def sendQueueStatus(self, q, isEditMessage : bool = False):
        q.printMembers() #debug maybe convert to log
        guild = self.bot.get_guild(q.guildId)
        channel = guild.get_channel(q.channelId)
        emb = self.buildQueueEmbed(guild, q)
        if isEditMessage:
            q.lastQueueMessage = await q.lastQueueMessage.edit(embed=emb)
        else:
            q.lastQueueMessage = await channel.send(embed=emb)

    # @commands.command()
    # async def hi(self, ctx : commands.Context, *args, **kwargs):
    #     """string B"""
    #     print(args.__str__())
    #     await ctx.send(ctx.message.channel.__str__)
    #     await ctx.send("Pong")

    @commands.command(aliases=["c"])
    @commands.has_role("Moderator")
    async def connect(self, ctx : commands.Context, *args):
        """ Connects queue to discord channel **(@moderator)**

        Usage: -connect <RS_Level> <Q_Name> <Role> <optional: Queue_Refresh_Rate> 

        Examples: 
            -c 8 "RS8 Queue" RS8 15
            -connect 9 "RS9 Queue" RS9 15

        Arguments: 
        <RS_Level> = integer for RS Queue Level
        <Q_Name> = text based name for the queue
        <Role> = discord role to use for the queue
        <Optional: Queue_Refresh_Rate> = Optional time in minutes to refresh queue when idle (default is 15 min)
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

    @commands.command(aliases=["i", "in", "j"])
    async def joinq(self, ctx :commands.Context, *args):
        '''Joins an RS Queue 

           Usage: -joinq <RS Level>
               where <RS Level> is value in range 5 .. 11

           Example: 
               -joinq 10
               -j 10
               -in 10
               -i 10
        '''
    
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
                    # ping queue role of queue addition
                    role = guild.get_role(q.roleId)
                    await channel.send(f'**{name}** joined {q.name} {role.mention} ({len(q.members)}/4)')
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

    @commands.command(aliases=["o", "out", "l"])
    async def leaveq(self, ctx : commands.Context, *args):
        ''' Leaves an RS Queue

            Usage: -leaveq <RS Level>
                where <RS Level> is value in range 5 to 11

            Example: 
                -o 7
                -leaveq 7 
                -l 7
                -o 7
                -out 7
        '''
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
                await channel.send(f'**{name}** has left {q.name}!')
                
            else:
                #log error
                pass

        else:
            #print help
            pass
    @commands.command(aliases=["s", "start"])
    async def startq(self, ctx : commands.Context, *args):
        ''' Stars an RS Queue before it is full.

        Usage: -start <RS Level>
            where <RS Level> is value of 5 .. 11

        Examples: 
            -startq 7
            -s 5
            -start 10
        '''
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
    @commands.has_role("Moderator")
    async def listq(self, ctx : commands.Context, *args):
        '''Shows RS Queues Configuration **(@Moderator)**

           Shows configuration of RS Queue to Discord Server Channel/Roles
        '''
        emb = self.buildQueueConfigEmbed(RSQueueManager.qs)
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_role("Moderator")
    async def start_botloop(self, ctx : commands.Context, *args):
        """Starts the main bot loop **(@Moderator)**
        
        Loop is responsible for processing bot data and queue refreshes

        Examples:
            -start_bootloop
        """
        await ctx.channel.send("Starting Periodic RS Bot Services")
        self.queueCheck.start()

    @commands.command()
    @commands.has_role("Moderator")
    async def stop_botloop(self, ctx : commands.Context, *args):
        """Stops the main bot loop **(@Moderator)**
        
        Loop is responsible for processing bot data and queue refreshes 

        Examples:
            -stop_bootloop
        """
        await ctx.channel.send("Stopping Periodic RS Bot Services")
        self.queueCheck.cancel()

    @commands.command(aliases=["q"])
    async def queue(self, ctx : commands.Context, *args):
        """Shows the RS Queue status.
        
        Usage: -queue <RS Level>
            where <RS Level> is value 5 to 11

        Examples:
            -q 7
            -queue 10
        """

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

    # Run Loop Activity Methods
    async def QueueRefreshToChannel(self, q : RSQueue):
        # Check to see if we need to print new queue information to channel based on timeout peroid since last queue update
        if (q.isTimeToPrintQueue()): #and q.size != 0):
            guild = self.bot.get_guild(q.guildId)
            channel = guild.get_channel(q.channelId)
            emb = self.buildQueueEmbed(guild, q)
            if q.lastQueueMessage == None:
                q.lastQueueMessage = await channel.send(embed=emb)
            else:
                q.lastQueueMessage = await q.lastQueueMessage.edit(embed=emb)
            return True
        return False

    async def CheckForStaleMembers(self, q : RSQueue):
        staleMembers = q.getStaleMembers()
        if (staleMembers != None):
            # we potentially have stale members test them with DM message with react emojis
            guild = self.bot.get_guild(q.guildId)
            channel = guild.get_channel(q.channelId)
            
            for user in staleMembers:
                # build stale embed message
                emb = self.buildStaleEmbed(guild, q, user)
                m : Member = guild.get_member(user.userId)
                await m.create_dm() #private DM channel with potentially stale member

                msg = await m.send(embed=emb)
                await msg.add_reaction('✅')
                await msg.add_reaction('❎')
                self.privateMessages.append(PrivateMessage(msg, user.userId, q, user)) # refactor out user.userId since its already in user 4th param

                return True;
        else:
            return False

    async def CheckForStaleTimedOutMembers(self, q : RSQueue):
        staleMembers = q.getStaleMembersWhoTimedOut()
        guild = self.bot.get_guild(q.guildId)
        channel = guild.get_channel(q.channelId)
        if (staleMembers != None):
            # we have timedout users so remove them from the queue
            for userId in staleMembers:
                # 0. get stale memeber message
                m = None
                for message in self.privateMessages:
                    if message.userId == userId.userId:
                        # we found the message and user who have timed out
                        # 1. remove react emoji's 
                        msg = message.message
                        memeber = guild.get_member(msg.author.id)
                        await msg.remove_reaction(emoji='✅', member=memeber)
                        await msg.remove_reaction(emoji='❎', member=memeber)
                    
                        # 3. Send Timeout message to user & channel
                        await msg.channel.send(f"You have be removed from the **{q.name}** due to acitivty timeout.\n\n" +
                                            f"Please rejoin {q.name} in {channel.mention} if interested to run.\n")
                        await channel.send(f"{guild.get_member(message.userId).mention} has timed out and been removed from {q.name}")

                        # 5. Remove User from the queue
                        if (q.delUser(userName=userId.name, userId=userId.userId)):
                            # print updates queue status and ensure lastPrint timestamp is refreshed as to not spam the channel
                            await self.sendQueueStatus(q, True)
                            # q.printMembers() #debug maybe convert to log
                            # guild = self.bot.get_guild(q.guildId)
                            # channel = guild.get_channel(q.channelId)
                            # emb = self.buildQueueEmbed(guild, q)
                            # q.lastQueueMessage = await channel.send(embed=emb)
                        # 4. Remove stale react message from list                        
                        self.privateMessages.remove(message) 

                        return True   
        return False

    @tasks.loop(seconds=10.0)
    async def queueCheck(self):
        #self.guild = self.bot.get_guild(1032563230620524615)
        #self.channel = self.guild.get_channel(1015814996497813595)
        # channel = self.bot.get_channel(1015814996497813595)
        # await channel.send("Tick")

        for key in RSQueueManager.qs.keys():
            if RSQueueManager.qs[key] != None:
                q = RSQueueManager.qs[key]

                if (await self.QueueRefreshToChannel(q)):
                    pass
                elif (await self.CheckForStaleMembers(q)):# check for stale queue members 
                    pass
                elif (await self.CheckForStaleTimedOutMembers(q)): # check for stale queue message timeouts (5 min?)
                    pass

    def buildStaleEmbed(self, guild : discord.Guild, queue : RSQueue, user : MemberInfo):
        timeInQueue : int = int((datetime.now() - user.timeInQueue).total_seconds() / 60)
        emb = discord.Embed(title=f"<:redstar:1032938394562613248> {queue.name} Check",
                      description=f"You have been in the queue for {timeInQueue} min.\n\n",
                                  color=discord.Color.magenta())
        emb.add_field(value = queue.buildUserStrings(queue.queueId),
                          name = '\u200b',
                          inline=False)
        emb.add_field(value = f"There are **{queue.size-1} other members** in your queue!\n\n"
                              f"**Do you want to remain in queue?**\n\n" +
                              f"Please click emoji ✅ to stay or ❎ to leave.\n" +
                              f"Note: This Message with timeout in 5 min and you will be automatically removed from the queue.",
                              name = '\u200b',
                              inline=False)
        emb.set_footer(text=f"Run ID: {queue.qRuns}", icon_url=None)

        emb.set_thumbnail(url=guild.icon.url)
        return emb

    def buildQueueEmbed(self, guild : discord.Guild, queue : RSQueue):
        queue.refreshLastQueuePrint()
        emb = discord.Embed(title=f"<:redstar:1032938394562613248> {queue.name} \t\t ({queue.size}/4)",
            description=f"Use command **-i {queue.queueId}** to join queue and **-o {queue.queueId}** to leave queue\n", #+
                #f"e.g. **-i {queue.queueId}** or **-o {queue.queueId}** \n",
            color=discord.Color.dark_blue())
        emb.set_footer(text=f"Run ID: {queue.qRuns}", icon_url=None)

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


async def setup(bot : commands.bot):
    print ("Adding RSQueueManager")
    await bot.add_cog(RSQueueManager(bot))

if __name__ == '__main__':
    pass
