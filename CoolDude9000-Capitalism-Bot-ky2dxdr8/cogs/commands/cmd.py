import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from data.profanity import swearwords
from other.mongo import get_bank_data, cluster, get_user_data, get_log_data
from cogs.moderator.admin import Admin
import random, asyncio, smtplib, re, datetime, asyncio, os, sys

class Cmd(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.data = bot.data
    self.servers = {}
    self.intervals = bot.intervals
    self.cmdintervals = {"strikes":{}}

  @discord.ext.commands.cooldown(1, 15, commands.BucketType.user)
  @commands.command()
  async def userphone(self, ctx):
    if len(self.servers)==0:
      self.servers[str(ctx.guild.id)]=ctx.channel.id
      await ctx.send("Waiting for a server to call...")
      return
    else:
      for server in self.servers.keys():
        guild_id = int(server)
        if guild_id == ctx.guild.id:
          await ctx.send("Call cancelled.")
          self.servers.pop(str(server))
          return
        channel_id = self.servers[str(server)]
        self.servers.pop(str(server))
        break
      guild = self.bot.get_guild(guild_id)
      channel = None
      for chan in guild.text_channels:
        if chan.id == channel_id:
          channel = chan
      if channel == None:
        await ctx.send("Their text channel was deleted during the wait process.")
      await channel.send("Connected! say -h to hangup.")
      await ctx.send("Connected! say -h to hangup.")
    def check(m):
      urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', m.content.lower())
      invites = re.findall("discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})", m.content.lower())
      if urls or invites:
        return False
      if m.author.id == 823699570147065876:
        return False
      return m.channel == ctx.channel or m.channel == channel
    while True:
      try:
        msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        try:
          self.intervals[str(msg.channel.id)]
        except:
          self.intervals[str(msg.channel.id)]={}
        try:
          self.intervals[str(msg.channel.id)][str(msg.author.id)]
        except:
          self.intervals[str(msg.channel.id)][str(msg.author.id)]=[]
        self.intervals[str(msg.channel.id)][str(msg.author.id)].append(msg.created_at)
        author_messages = self.intervals[str(msg.channel.id)][str(msg.author.id)]  
        if len(author_messages) == 1:
          pass
        else:
          if (author_messages[-1]-author_messages[-2]).seconds == 0:
            if (author_messages[-1]-author_messages[-2]).microseconds < 300000:
              await msg.channel.send("Heyo stop spamming!")
              await ctx.send("Disconnected due to spam.")
              await channel.send("Disconnected due to spam.")
              break
        if msg.content.lower() == "-hangup" or msg.content.lower() == "-h":
          await ctx.send("Disconnected by hanging up.")
          await channel.send("Disconnected by hanging up.")
          break
        if msg.channel == ctx.channel:
          await channel.send(f"**{msg.author}:** {msg.content}", allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
        else:
          await ctx.send(f"**{msg.author}:** {msg.content}", allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
      except asyncio.TimeoutError:
        await ctx.send("Disconnected.")
        await channel.send("Disconnected.")
        break

  @commands.Cog.listener()
  async def on_command_completion(self, ctx):
    list_ = ["bruh","nice","meme","bruhmeme"]
    string_ = random.choice(list_)+random.choice(list_)+random.choice(list_)
    self.data[string_] = 1
    result = await self.detc_user(ctx.author)
    if result:
      await ctx.author.send(
        "Hi there, I see you're new to CapitalismTheTrueGaymer.\n**Support server link:** https://discord.gg/capitalism\nAdd me to your server: <https://discord.com/api/oauth2/authorize?client_id=823699570147065876&permissions=268823670&redirect_uri=https%3A%2F%2Fdiscord.com%2Foauth2%2Fauthorize%3Fclient_id%3DCapitalismBot&scope=bot%20applications.commands>\nIf experienced any bugs, or anything that needs improvements please post in support server.\nHave fun with my features!"
      )
      #button
    user = ctx.author
    users = await get_bank_data()
    try:
      users[str(user.id)]["exp"]+=1
    except:
      pass
    db = cluster["CapBot"]
    collection = db["main"]
    collection.replace_one({"_id":0},users)
    users = await get_user_data()
    try:
      commands = users[str(user.id)]["commands"]
      if commands >= 50:
        users[str(user.id)]["commands"]+=1
        collection = db["users"]
        collection.replace_one({"_id":1}, users)
        return
      else:
        users[str(user.id)]["commands"]+=1
        collection = db["users"]
        collection.replace_one({"_id":1}, users)
        tips = [
          'Did you know that you could remove your data?\nUse `CAPhelp data` for more information!~',
          'Have you checked out our currency system yet?\nUse `CAPhelp currency` for more information!~',
          'Do you want to get rich in our currency?\nUse `CAPvote` to get 2-3 coin bags without running any commands!~ Then use `CAPuse` to use the coin bags, it will give you coins.',
          'Support us by voting!\nUse `CAPvote` to support us and get rewards too!',
          'Have trouble using the bot? Commands not functioning?\nJoin our support server! `CAPsupport`',
          'Want this bot in your own server?\nUse `CAPinvite` to get the authorization link!',
          'Check out our website!\nUse `CAPweb` for the URL.',
          'Did you know about CapitalismTheAFKGod?\nIt is a bot in our support server! Join support server to experience it',
          'Dont have slash commands in your server?\nTry inviting the bot again with application.commands scope!'
          ]
        if random.randint(0,3) == 1:
          await ctx.send(f"Tip:\n{random.choice(tips)}")
    except:
      return

  async def detc_user(self, user):
    users = await get_user_data()
    if str(user.id) in users:
      return False
    else:
      users[str(user.id)]={"commands":0}
    db = cluster["CapBot"]
    collection = db["users"]
    collection.replace_one({"_id":1},users)
    return True

  @commands.command(aliases=["restart", "nuke_bot"])
  async def reboot(self, ctx):
    if ctx.author.id == 763854419484999722:
      await ctx.send("rebooting the bot...")
      os.execv(sys.executable, ['python'] + sys.argv)
    else:
      await ctx.send("You cannot reboot the bot.")

  @discord.ext.commands.cooldown(1, 60, commands.BucketType.user)
  @commands.command()
  async def email(self, ctx):
      EMAIL_ADDRESS = 'capitalismdiscordbot@gmail.com'
      EMAIL_PASSWORD = 'capitalism>communism'
      await ctx.send("who will be the email receiver?")
      def check(author):
        def inner_check(message):
          if message.author != author:
            return False
          try:
            return True
          except ValueError:
            return False
        return inner_check
      try:
        msg = await self.bot.wait_for('message', timeout=30, check = check(ctx.author))
        RECEIVER = msg.content
        subject = 'Support Capitalism, Deny Communism.'
        await ctx.send("what will be the body? (if it's too short google will mark it as spam)")
        try:
          msg = await self.bot.wait_for('message', timeout=30, check = check(ctx.author))
          body = f'{msg.content} \n\n\nsent by {ctx.author} from discord'
          message = f'Subject: {subject}\n\n{body}'
          server = smtplib.SMTP('smtp.gmail.com', 587)
          server.ehlo()
          server.starttls()
          server.ehlo()
          try:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
          except Exception as e:
            print(e)
            await ctx.send("Cannot log into Bot Email due to Google being annoying (or gmail having issues)")
          try:
            server.sendmail(EMAIL_ADDRESS, RECEIVER, message)
            server.quit()
            await ctx.send("Email success. Note: if this is an invalid email, it can still say this message")
          except Exception as e:
            print(e)
            await ctx.send("failed to email, are you sure that's the right information?")
        except asyncio.TimeoutError:
          await ctx.send('imagine not replying in time mate')
      except asyncio.TimeoutError:
        await ctx.send("imagine not replying in time mate")

  @commands.Cog.listener()
  async def on_command(self, ctx):
    if ctx.author.id == 763854419484999722:
      ctx.command.reset_cooldown(ctx)
    try:
      self.cmdintervals[str(ctx.author.id)]
    except:
      self.cmdintervals[str(ctx.author.id)]=[]
    self.cmdintervals[str(ctx.author.id)].append(ctx.message.created_at)
    author_messages = self.cmdintervals[str(ctx.author.id)]  
    if len(author_messages) < 6:
      pass
    else:
      if (author_messages[-1]-author_messages[-5]).seconds < 3:
        try:
          self.cmdintervals["strikes"][str(ctx.author.id)]+=1
          if self.cmdintervals["strikes"][str(ctx.author.id)] > 10:
            db = cluster["CapBot"]
            collection = db["bot_banned"]
            cursor = collection.find({})
            for x in cursor:
              users = x
            member = ctx.author.id
            if member in users["spam_banned"]:
              return
            users["spam_banned"].append(member)
            collection.replace_one({"_id":1},users)
            channel = await self.bot.fetch_channel(853288563352404058)
            await channel.send(f"The bot spam_banned {ctx.author} for spamming commands, id {member}")
            try:
              await ctx.author.send("You are now bot banned from our bot for spamming too many commands.")
            except:
              await ctx.message.reply("You are now bot banned from our bot for spamming too many commands.")
        except:
          self.cmdintervals["strikes"][str(ctx.author.id)]=1
        em = discord.Embed(title="Stop spamming commands!", description="If you continue spam commands you will be bot banned.")
        try:
          await ctx.author.send(embed=em)
        except:
          await ctx.message.reply(embed=em)


  @commands.Cog.listener()
  async def on_message(self, message):
    try:
      guild_id = message.guild.id
    except:
      return
    if message.author.id == 823699570147065876:
      return
    if "<@!823699570147065876>" in message.content or "<@823699570147065876>" in message.content:
      prefix = await get_log_data()
      try:
        prefix = prefix[str(message.guild.id)]["prefix"]
        prefix = str(prefix).lstrip('[').rstrip(']')
        await message.reply(f"Hi! My prefix is {prefix}!", mention_author=False)
      except:
        await message.reply("Hi! My prefix is 'CAP' or 'c/'!", mention_author=False)

  @commands.command()
  async def say(self, ctx, *,message):
    print(self)
    if ctx.author.id == 763854419484999722:
      pass
    else:
      await ctx.send('this command is disabled')
      return
    for i in range(5):
      await ctx.send(message)

  @discord.ext.commands.cooldown(1, 1, commands.BucketType.user)
  @commands.command()
  async def msg(self, ctx, *, message):
    if "`" in message:
      await ctx.send('sorry bud, you can\'t send ` in your message')
    else:
      urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.lower())
      invites = re.findall("discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})", message.lower())
      if not urls and not invites:
        var1 = message.lower()
        words = var1.split()
        repeat = int(len(words))
        repeat_times = 0
        for i in words:
          if not i in swearwords:
              if repeat_times == repeat or repeat_times == repeat-1:
                author = ctx.message.author
                await ctx.send(content=f'`{message}`\n\n- {author}',allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
                try:
                  await ctx.message.delete()
                except:
                  pass
                break
              else:
                repeat_times+=1
          else:
            try:
              await ctx.message.delete()
            except:
              pass
            await ctx.send("You cannot send blacklisted words. Sorry but we've blacklisted 835 words that are either swears or close to swears. You can still manually speak most of them.")
            break
      else:
        try:
          await ctx.message.delete()
        except:
          pass
        await ctx.send("You cannot send links")
  
  @discord.ext.commands.cooldown(1, 15, commands.BucketType.user)
  @commands.command()
  async def info(self, ctx):
    try:
      await ctx.message.delete()
    except:
      pass
    await ctx.send("This bot is currently in BETA\n **Abuse use of this bot can get you banned. Post proof in support server #reports with image as proof to report someone!**")
  
  @discord.ext.commands.cooldown(1, 15, commands.BucketType.user)
  @commands.command()
  async def suggestion(self, ctx):
    try:
      await ctx.message.delete()
    except:
      pass
    await ctx.send("https://discord.gg/capitalism\nPost your suggestions in #suggestions channel!")
  
  @discord.ext.commands.cooldown(1, 5, commands.BucketType.user)
  @commands.command()
  async def amIright(self, ctx):
    response = ["yes","no","hmm idk"]
    await ctx.send(random.choice(response))
  
  @discord.ext.commands.cooldown(1, 3, commands.BucketType.user)
  @commands.command()
  async def choose(self, ctx, *, arg=None):
    if not arg==None:
      if "`" in arg:
        await ctx.send("I'm not choosing with options that has ` in them.")
      listrandom = arg.split()
      if len(listrandom) == 1:
        await ctx.send("that's only 1 choice bruh you need at least 2")
      else:
        for i in listrandom:
          urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', i.lower())
          invites = re.findall("discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})", i.lower())
          if urls or invites:
            await ctx.send("You cannot choose between links.")
            return
        await ctx.send("`"+random.choice(listrandom)+"`",allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
    else:
      await ctx.send("You need give at least 2 choices nerd. Format is CAPchoose (1)  (2) ... (n)")
    
  @discord.ext.commands.cooldown(1, 2, commands.BucketType.user)
  @commands.command(name="8ball")
  async def _8ball(self, ctx):
      await ctx.reply("What question do you want to ask? :8ball:", mention_author=False)
      def check(author):
        def inner_check(message):
          if message.author != author:
              return False
          try:
              return True
          except ValueError:
              return False
        return inner_check
      try:
        msg = await self.bot.wait_for('message', timeout=30, check = check(ctx.author))
        if msg:
          await ctx.send("Ok, lemme think for a sec...")
          await asyncio.sleep(2)
          response = ["Yes.","Nah","I wouldn't care less.","maybe?idk","Certainly","Think about the results.","Hell nah"]
          await ctx.send(random.choice(response))
      except asyncio.TimeoutError:
        await ctx.reply("Imagine not answering", mention_author=False)
  
  @discord.ext.commands.cooldown(1, 15, commands.BucketType.user)
  @commands.command(aliases=["link"])
  async def invite(self, ctx):
    await ctx.send("<https://discord.com/api/oauth2/authorize?client_id=823699570147065876&permissions=268823670&redirect_uri=https%3A%2F%2Fdiscord.com%2Foauth2%2Fauthorize%3Fclient_id%3DCapitalismBot&scope=bot%20applications.commands>")
  
  @discord.ext.commands.cooldown(1, 15, commands.BucketType.user)
  @commands.command()
  async def support(self, ctx):
    try:
      await ctx.message.delete()
    except:
      pass
    await ctx.send("https://discord.gg/capitalism")
  
  @commands.command()
  async def web(self, ctx):
    await ctx.send("https://discord.capitalismbot.repl.co")
  
  @discord.ext.commands.cooldown(1, 1, commands.BucketType.user)
  @commands.command(aliases=["howpog"])
  async def pograte(self, ctx,arg=None):
    number = random.randint(1,100)
    if arg ==None:
      embedPog = discord.Embed(
      title="POG RATE MACHINE",
      description="You are {}% pog <:littlepog:825452143657353226>".format(number),
      color=discord.Color.random()
      )
      await ctx.send(embed=embedPog)
    else:
      embedPog = discord.Embed(
      title="POG RATE MACHINE",
      description="{} is {}% pog <:littlepog:825452143657353226>".format(arg, number),
      color=discord.Color.random()
      )
      await ctx.send(embed=embedPog)

  @discord.ext.commands.cooldown(1, 5, commands.BucketType.user)
  @commands.command()
  async def guess(self, ctx):
    number = random.randint(1,100000)
    await ctx.reply("Guess a number between 1 and 100,000", mention_author=False)
    def check(author):
      def inner_check(message):
        if message.author != author:
            return False
        try:
            int(message.content)
            return True
        except ValueError:
            return False
      return inner_check
    try:
      msg = await self.bot.wait_for('message', timeout=30, check = check(ctx.author))
      attempt = int(msg.content)
      if msg:
        if not attempt<=0:
          if not attempt>=100001:
            if attempt == number:
              await msg.reply("Nice job! You got it correct. Screenshot this and post it in support server.", mention_author=False)
            else:
              await msg.reply(f"You're so bad smh you didn't get it right. The correct number was {number}", mention_author=False)
          else:
            await msg.reply("Dude that wasn't even in range 1-100,000", mention_author=False)
        else:
          await msg.reply("Dude that wasn't even in range 1-100,000", mention_author=False)
    except asyncio.TimeoutError:
      await ctx.reply("Imagine not answering", mention_author=False)

  @discord.ext.commands.cooldown(1,5,commands.BucketType.guild)
  @commands.command()
  @has_permissions(manage_guild=True)
  async def enable(self, ctx, cmd):
      logs = await get_log_data()
      cmd = cmd.lower()
      if self.bot.get_command(cmd)==None:
        await ctx.send("Command not found.")
        return
      else:
        cmd = self.bot.get_command(cmd)
        cmd = cmd.name
      try:
        logs[str(ctx.guild.id)]["disabled"]
        index = logs[str(ctx.guild.id)]["disabled"].index(cmd)
        logs[str(ctx.guild.id)]["disabled"].pop(index)
      except:
        await ctx.send("Hey dude you never disabled the command.")
      await ctx.send(f"{cmd} enabled!")
      db = cluster["CapBot"]
      collection = db["logs"]
      collection.replace_one({"_id":1}, logs)

  @discord.ext.commands.cooldown(1,5,commands.BucketType.guild)
  @commands.command()
  @has_permissions(manage_guild=True)
  async def disable(self, ctx, cmd):
      if cmd.lower() == "disable" or cmd.lower() == "enable":
        await ctx.send("Disable and enable command cannot be disabled.")
        return
      logs = await get_log_data()
      cmd = cmd.lower()
      if self.bot.get_command(cmd)==None:
        await ctx.send("Command not found.")
        return
      else:
        cmd = self.bot.get_command(cmd)
        cmd = cmd.name
      try:
        logs[str(ctx.guild.id)]
        try:
          logs[str(ctx.guild.id)]["disabled"].append(cmd)
        except:
          logs[str(ctx.guild.id)]["disabled"]=[]
          logs[str(ctx.guild.id)]["disabled"].append(cmd)
      except:
        logs[str(ctx.guild.id)]={}
        logs[str(ctx.guild.id)]["disabled"]=[]
        logs[str(ctx.guild.id)]["disabled"].append(cmd)
      await ctx.send(f"{cmd} Command disabled.")
      db = cluster["CapBot"]
      collection = db["logs"]
      collection.replace_one({"_id":1}, logs)
    

  @discord.ext.commands.cooldown(1,5,commands.BucketType.user)
  @commands.command()
  async def gcreate(self, ctx):
    await ctx. send("Starting a giveaway. Answer within 30 seconds for the following questions.")
    questions = ["Which channel should the giveaway be posted in?", "How long should it last? Use (s|m|h|d)", "What is the prize of the giveaway?"]
    answers=[]
    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel
    for i in questions:
      await ctx.send(i)
      try:
        msg=await self.bot.wait_for('message', timeout=30.0, check=check)
      except asyncio.TimeoutError:
        await ctx.send("imagine not answering in time")
        return
      else:
        answers.append(msg.content)
    try:
      c_id=int(answers[0][2:-1])
    except:
      await ctx.send("That's not a valid channel id lmao")
      return
    channel=self.bot.get_channel(c_id)
    time_=self.convert(answers[1])
    if time_ == -1:
      await ctx.send("use (s|m|h|d) for time dumbass")
      return
    elif time_ ==-2:
      await ctx.send("Time has to be an integer ya idiot")
      return
    prize = answers[2]
    await ctx.send(f"Alright, the giveaway will be in {channel.mention} and will last {answers[1]} seconds!")
    em=discord.Embed(
      title="Capitalist's Giveaway!",
      description=f"**Prize:** {prize} (React with tada to enter)",
      color=discord.Color.random()
    )
    em.add_field(
      name="host by:",
      value =ctx.author.mention,
      inline=False
    )
    end = datetime.datetime.utcnow()+datetime.timedelta(seconds=time_)
    em.add_field(
      name="Ends at:",
      value=f"{end} UTC",
  )
    em.set_footer(
      text=f"Ends in {answers[1]} from when it started."
    )
    my_msg=await channel.send(embed=em)
    await my_msg.add_reaction("<a:tadagif:827221672193032192>")
    await asyncio.sleep(time_)
    new_msg = await channel.fetch_message(my_msg.id)
    try:
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        winner=random.choice(users)
        await channel.send(f"Congrats to {winner.mention} winning {prize}!")
    except:
        await channel.send(f"I could not determine a winner for the '*prize:* {prize}'' giveaway")
  
  def convert(self, time):
    pos = ["s","m","h","d"]
    time_dict = {"s":1,"m":60,"h":3600,"d":3600*24}
    unit=time[-1]
    if unit not in pos:
      return -1
    try:
      val = int(time[:-1])
    except:
      return -2
    return val*time_dict[unit]
  
  @commands.command(aliases=["gend"])
  async def reroll(self, ctx, channel:discord.TextChannel, id_:int):
    try:
      new_msg = await channel.fetch_message(id_)
    except:
      await channel.send("The message id was incorrect.")
    users=await new_msg.reactions[0].users().flatten()
    users.pop(users.index(self.bot.user))
    winner = random.choice(users)
    await channel.send(f"The new winner is {winner.mention}!")
  
  @discord.ext.commands.cooldown(1, 5, commands.BucketType.user)
  @commands.command()
  async def reminder(self, ctx):
    await ctx.send("Settings a reminder!\nWhat message would you like the bot to dm you?")
    def check(m):
      return m.channel == ctx.channel and m.author == ctx.author
    try:
      msg = await self.bot.wait_for('message', timeout=60.0, check=check)
      dm_msg = msg.content
      await ctx.send(f"Please state when you want to receive a DM reminder. (Use UTC)\nThe UTC time is currently {datetime.datetime.utcnow()}")
      try:
        msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        try:
          time_ = datetime.datetime.fromisoformat(msg.content)
          await ctx.send(f"Alright, I'll remind you at {time_}")
          await discord.utils.sleep_until(datetime.datetime.fromisoformat(msg.content))
          await ctx.author.send(f"You set a reminder: {dm_msg}")
        except:
          await ctx.send("Invalid time provided.")
          raise Exception("bad time")
      except asyncio.TimeoutError:
        await ctx.send("You did not reply in time.")
    except asyncio.TimeoutError:
      await ctx.send("You did not reply in time.")

  @commands.command()
  async def gstart(self, ctx, sec:str,*,prize:str):
    em=discord.Embed(
      title="Capitalist's Giveaway!",
      description=f"**Prize:** {prize} (React with tada to join)",
      color =discord.Color.random()
    )
    em.add_field(
      name="host by:",
      value =ctx.author.mention,
      inline=False
    )
    sec = self.convert(sec)
    end = datetime.datetime.utcnow()+datetime.timedelta(seconds=sec)
    em.add_field(
      name="Ends at:",
      value=f"{end} UTC",
    )
    em.set_footer(
      text=f"Ends {sec} seconds from start"
    )
    my_msg=await ctx.send(embed=em)
    await my_msg.add_reaction("<a:tadagif:827221672193032192>")
    await asyncio.sleep(sec)
    new_msg = await ctx.channel.fetch_message(my_msg.id)
    try:
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        winner = random.choice(users)
        await ctx.send(f"Congrats to {winner.mention} winning {prize}!")
    except:
        await ctx.send(f"I could not determine a winner for the '*prize:* {prize}' giveaway.")

  @commands.command(aliases=["tictactoe"])
  async def ttt(self, ctx, member:discord.Member):
    if member.id == 835902029833699339:
      await ctx.send("You cannot play with me because I'm too good at the game")
      return
    turns = 0
    options = ["a1", "a2","a3","b1","b2","b3","c1","c2","c3"]
    a1 = "⬛"
    a2 = "⬛"
    a3 = "⬛"
    b1 = "⬛"
    b2 = "⬛"
    b3 = "⬛"
    c1 = "⬛"
    c2 = "⬛"
    c3 = "⬛"
    def check(m):
      if m.author.id == member.id:
        if m.channel == ctx.channel:
          return True
    def check2(m):
      if m.author.id == ctx.author.id:
        if m.channel == ctx.channel:
          return True
    game_end = False
    mem=True
    autho=False
    while not game_end:
      if game_end:
        break
      if a1 == a2 and a1 == a3:
        if not a1 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif a1 == b2 and a1 == c3:
        if not a1 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif a1 == b1 and a1 == c1:
        if not a1 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif b1 == b2 and b1 == b3:
        if not b1 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif c1 == c2 and c1 == c3:
        if not c1 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif a2 == b2 and a2 == c2:
        if not a2 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif a3 == b3 and a3 == c3:
        if not a3 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      elif a3 == b2 and a3 == c1:
        if not a3 == "⬛":
          await ctx.send(f"{ctx.author.mention} won.")
          break
      embed = discord.Embed(
        title = "Tic Tac Toe Game",
        description = "`a1-a3`, `b1-b3`, `c1-c3` to place. letter = rows, numbers = columns\ntype `end` to end the game"
      )
      embed.add_field(
        name = "board",
        value = f"{a1}{a2}{a3}\n{b1}{b2}{b3}\n{c1}{c2}{c3}"
      )
      turns+=1
      while mem:
        await ctx.send(content=f"{member.mention} hey {ctx.author} wants to play tictactoe", embed=embed)
        try:
          option = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
          await ctx.send("imagine not replying on time")
          game_end=True
          autho=False
          mem=False
          break
        option = option.content
        if option.lower() == "end":
          await ctx.send("game ends.")
          mem=False
          autho=False
          game_end=True
          break
        if not option in options:
          await ctx.send("that's not a valid option bruh")
          continue
        else:
          emoji = "❎"
          if option == "a1":
            if not a1 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            a1 = emoji
          elif option == "a2":
            if not a2 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            a2 = emoji
          elif option == "a3":
            if not a3 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            a3 = emoji
          elif option == "b1":
            if not b1 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            b1 = emoji
          elif option == "b2":
            if not b2 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            b2 = emoji
          elif option == "b3":
            if not b3 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            b3 = emoji
          elif option == "c1":
            if not c1 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            c1 = emoji
          elif option == "c2":
            if not c2 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            c2 = emoji
          elif option == "c3":
            if not c3 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            c3 = emoji
          mem=False
          autho=True
          break
      embed = discord.Embed(
        title = "Tic Tac Toe Game",
        description = "`a1-a3`, `b1-b3`, `c1-c3` to place. letter = rows, numbers = columns\ntype `end` to end the game"
      )
      embed.add_field(
        name = "board",
        value = f"{a1}{a2}{a3}\n{b1}{b2}{b3}\n{c1}{c2}{c3}"
      )
      if a1 == a2 and a1 == a3:
        if not a1 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif a1 == b2 and a1 == c3:
        if not a1 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif a1 == b1 and a1 == c1:
        if not a1 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif b1 == b2 and b1 == b3:
        if not b1 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif c1 == c2 and c1 == c3:
        if not c1 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif a2 == b2 and a2 == c2:
        if not a2 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif a3 == b3 and a3 == c3:
        if not a3 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      elif a3 == b2 and a3 == c1:
        if not a3 == "⬛":
          await ctx.send(f"{member.mention} won.")
          break
      turns+=1
      if turns == 10:
        await ctx.send(content = "Draw! you both suck", embed=embed)
        break
      while autho:
        await ctx.send(content=f"{ctx.author.mention} hey {member} wants to play tictactoe", embed=embed)
        try:
          option = await self.bot.wait_for('message', timeout=60.0, check=check2)
        except asyncio.TimeoutError:
          await ctx.send("imagine not replying on time")
          game_end=True
          mem=False
          autho=False
          break
        option = option.content
        if option.lower() == "end":
          await ctx.send("game ends.")
          mem=False
          autho=False
          game_end=True
          break
        if not option in options:
          await ctx.send("that's not a valid option bruh")
          continue
        else:
          emoji = "🔴"
          if option == "a1":
            if not a1 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            a1 = emoji
          elif option == "a2":
            if not a2 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            a2 = emoji
          elif option == "a3":
            if not a3 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            a3 = emoji
          elif option == "b1":
            if not b1 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            b1 = emoji
          elif option == "b2":
            if not b2 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            b2 = emoji
          elif option == "b3":
            if not b3 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            b3 = emoji
          elif option == "c1":
            if not c1 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            c1 = emoji
          elif option == "c2":
            if not c2 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            c2 = emoji
          elif option == "c3":
            if not c3 == "⬛":
              await ctx.send("that block is already taken!")
              continue
            c3 = emoji
          mem=True
          autho=False
          break
  
  # @commands.command(aliases=["lb"])
  # async def leaderboard(self,ctx, x=10):
  #   users = await get_bank_data()
  #   leader_board = {}
  #   total = []
  #   for user in users.keys():
  #     if user == "_id":
  #       continue
  #     name= int(user)
  #     total_amount = users[str(user)]["wallet"]
  #     leader_board[str(total_amount)]=name
  #     total.append(total_amount)
  #   total = sorted(total,reverse=True)
  #   em=discord.Embed(
  #     title = f"Top {x} Richest People",
  #     description="placeholder",
  #     color=discord.Color.random()
  #   )
  #   index = 1
  #   for amt in total:
  #     id_ = leader_board[str(amt)]
  #     member=await self.bot.fetch_user(int(id_))
  #     name=member.name
  #     em.add_field(
  #       name=f"{index}. {name}",
  #       value=f"{amt}",
  #       inline=False
  #     )
  #     if index == x:
  #       break
  #     else:
  #       index+=1
  #   await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Cmd(bot))