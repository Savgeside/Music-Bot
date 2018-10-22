import discord
import asyncio
import youtube_dl
import os
from discord.ext import commands
from discord.ext.commands import Bot


client=commands.Bot(command_prefix='a.')

from discord import opus
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

    raise RuntimeError('Could not load an opus lib. Tried %s' %
                       (', '.join(opus_libs)))
load_opus_lib()

in_voice=[]


players = {}
songs = {}
playing = {}


async def all_false():
    for i in bot.servers:
        playing[i.id]=False


async def checking_voice(ctx):
    await asyncio.sleep(130)
    if playing[ctx.message.server.id]== False:
        try:
            pos = in_voice.index(ctx.message.server.id)
            del in_voice[pos]
            server = ctx.message.server
            voice_client = bot.voice_client_in(server)
            await voice_client.disconnect()
            await bot.say("{} left because there was no audio playing for a while".format(bot.user.name))
        except:
            pass

@client.event
async def on_ready():
    bot.loop.create_task(all_false())
    print(bot.user.name)    
    
@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    if channel is None:
      client.say(":x: | You need to join a voice channel first bud!")
      return
    await client.join_voice_channel(channel)
    in_voice.append(ctx.message.server.id)
    await client.say(":musical_note: I have joined and I am ready to play some music for you!")


async def player_in(con):  # After function for music
    try:
        if len(songs[con.message.server.id]) == 0:  # If there is no queue make it False
            playing[con.message.server.id] = False
            bot.loop.create_task(checking_voice(con))
    except:
        pass
    try:
        if len(songs[con.message.server.id]) != 0:  # If queue is not empty
            # if audio is not playing and there is a queue
            songs[con.message.server.id][0].start()  # start it
            await client.send_message(con.message.channel, ':musical_note: Now playing {}'.format(songs.title))
            del songs[con.message.server.id][0]  # delete list afterwards
    except:
        pass


@client.command(pass_context=True)
async def play(ctx, *,url):

    opts = {
        'default_search': 'auto',
        'quiet': True,
    }  # youtube_dl options


    if ctx.message.server.id not in in_voice: #auto join voice if not joined
        channel = ctx.message.author.voice.voice_channel
        await client.join_voice_channel(channel)
        in_voice.append(ctx.message.server.id)

    

    if playing[ctx.message.server.id] == True: #IF THERE IS CURRENT AUDIO PLAYING QUEUE IT
        voice = client.voice_client_in(ctx.message.server)
        song = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: bot.loop.create_task(player_in(ctx)))
        songs[ctx.message.server.id]=[] #make a list 
        songs[ctx.message.server.id].append(song) #add song to queue
        await client.say(":musical_note: Audio ``{}`` is queued".format(song.title))

    if playing[ctx.message.server.id] == False:
        voice = bot.voice_client_in(ctx.message.server)
        player = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: bot.loop.create_task(player_in(ctx)))
        players[ctx.message.server.id] = player
        # play_in.append(player)
        if players[ctx.message.server.id].is_live == True:
            await bot.say(":musical_note: **Can not play live audio yet.**")
        elif players[ctx.message.server.id].is_live == False:
            player.start()
            await bot.say(f"Searching :mag_right: ``{url}``")
            await bot.say(f":musical_note: Now playing ``{player.title}``")
            playing[ctx.message.server.id] = True



@client.command(pass_context=True)
async def queue(con):
    players[ctx.message.server.id] = player
    await client.say("There are currently ``{}`` audios in queue".format(player.title))

@client.command(pass_context=True)
async def pause(ctx):
    players[ctx.message.server.id].pause()
    await client.say(":musical_note: I have now paused the audio")
    
@client.command(pass_context=True)
async def resume(ctx):
    players[ctx.message.server.id].resume()
    await client.say(":musical_note: I have now resumed the audio")
          


@client.command(pass_context=True)
async def stop(con):
  if ctx.message.author.server_permissions.manage_channels:
    players[con.message.server.id].stop()
    songs.clear()
  else:
    await client.say(":x: Only users with ``Manage Channels`` can use this command!")

@client.command(pass_context=True)
async def leave(ctx):
    pos=in_voice.index(ctx.message.server.id)
    del in_voice[pos]
    server=ctx.message.server
    voice_client=client.voice_client_in(server)
    await voice_client.disconnect()
    songs.clear()
    await client.say(":musical_note: I have left the voice channel!")
   
@client.command(name="prefix", pass_context=True)
async def prefix(ctx):
    with open("serverConfig.json", "r") as f:
        prefixes = json.load(f)
    if ctx.message.author.bot:
        await client.say("Bots can't use commands.")
        return
    author = ctx.message.author
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.set_author(icon_url=author.avatar_url, name="Prefix Setup")
    embed.add_field(name="Info", value="Hey! I see you are trying to setup a new prefix..? Well if you don't always like the prefix just change it!")
    embed.add_field(name="Start up", value="Now we will start the setup..! So just say the prefix that we will set. Remember you can change this after. PS **if you want to stop just make the prefix -**", inline=False)
    await client.say(embed=embed)
    prefix = await client.wait_for_message(author=author)
    await client.say(f"We have set your server prefix to ``{prefix.content}``")
    prefixes[ctx.message.server.id] = prefix.content
    with open("serverConfig.json", "w") as f:
        json.dump(prefixes, f)

@client.command(pass_context=True)
async def search(ctx):
    with open("economy.json", "r")as f:
        coins = json.load(f)
    author = ctx.message.author
    rancoins = random.randint(1, 100)
    if not ctx.message.server.id in coins:
       	coins[ctx.message.server.id] = {}
    if not author.id in coins[ctx.message.server.id]:
        coins[ctx.message.server.id][author.id] = 0
    coins[ctx.message.server.id][author.id] += rancoins
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.set_author(icon_url=author.avatar_url, name="Searched")
    embed.add_field(name="Search Done", value=f"Your search has given you: **{rancoins}** Coins")
    await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins,f,indent=4)

@client.command(pass_context=True)
async def addmoney(ctx, user: discord.Member = None, amount: int = None):
    with open("economy.json", "r") as f:
       	coins = json.load(f)
    if ctx.message.author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if ctx.message.author.server_permissions.manage_server:
        if user == ctx.message.author:
            await client.say("I can't give you money. You are cheating my system!")
            return
        if user is None:
            embed = discord.Embed(color=(random.randint(0, 0xffffff)))
            embed.add_field(name=":x: Error", value="You need a user name!\n **Example:** \n ?addmoney @User")
            await client.say(embed=embed)
            return
        if amount is None:
            embed = discord.Embed(color=(random.randint(0, 0xffffff)))
            embed.add_field(name=":x: Error", value="You need a amount!\n **Example:** \n ?addmoney @User 5")
            await client.say(embed=embed)
            return
        if not ctx.message.server.id in coins:
            coins[ctx.message.server.id] = {}
        if not user.id in coins[ctx.message.server.id]:
            coins[ctx.message.server.id][user.id] = 0
        coins[ctx.message.server.id][user.id] += amount
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name="Money Added!", value=f"Added **${amount}** to {user.mention}!", inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        await client.say(embed=embed)
    else:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You're missing permissions!", inline=False)
        embed.add_field(name="Permissions:", value="``Manage Server``")
        embed.set_footer(text="Missing Permissions!", icon_url=author.avatar_url)
        await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)

@client.command(pass_context=True)
async def removemoney(ctx, user: discord.Member = None):
    with open("economy.json", "r") as f:
       	coins = json.load(f)
    author = ctx.message.author
    channel = ctx.message.channel
    amount = coins[ctx.message.server.id][user.id]
    if ctx.message.author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if ctx.message.author.server_permissions.manage_server:
        if user == author:
            await client.say("I can't remove your money. You are making me feel like I haven't done good for you!")
            return
        if user is None:
            embed = discord.Embed(color=(random.randint(0, 0xffffff)))
            embed.add_field(name=":x: Error", value="You need a user name!\n **Example:** \n ?remove @User")
            await client.say(embed=embed)
            return
        if not ctx.message.server.id in coins:
            coins[ctx.message.server.id] = {}
        if not user.id in coins[ctx.message.server.id]:
            coins[ctx.message.server.id][user.id] = 0
        coins[ctx.message.server.id][user.id] -= amount
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name="Mone Removed!", value=f"I have removed **${amount}** from {user.mention}!", inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        await client.say(embed=embed)
    else:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You're missing permissions!", inline=False)
        embed.add_field(name="Permissions:", value="``Manage Server``")
        embed.set_footer(text="Missing Permissions!", icon_url=author.avatar_url)
        await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)

@client.command(pass_context=True)
@commands.cooldown(1, 120, commands.BucketType.user)
async def work(ctx):
    with open("economy.json", "r") as f:
       	coins = json.load(f)
    author = ctx.message.author
    coinsc = random.randint(100, 700)
    if ctx.message.author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if not ctx.message.server.id in coins:
       	coins[ctx.message.server.id] = {}
    if not author.id in coins[ctx.message.server.id]:
        coins[ctx.message.server.id][author.id] = 0
    coins[ctx.message.server.id][author.id] += coinsc
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.add_field(name=":moneybag: | Work Reward", value=f"{author.mention}, I have put $**{coinsc}** in your account!", inline=False)
    await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)
@work.error
async def cooldown_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        remainder = divmod(error.retry_after, 120)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name="Slowdown :stuck_out_tongue_winking_eye: ", value=f"Cooldown: **{remainder}** \n Each Command: **1**", inline=False)
        await client.say(embed=embed)

@client.command(pass_context=True)
@commands.cooldown(1, 864000, commands.BucketType.user)
async def daily(ctx):
    with open("economy.json", "r") as f:
       	coins = json.load(f)
    author = ctx.message.author
    coinsc = random.randint(100, 700)
    if ctx.message.author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if not ctx.message.server.id in coins:
       	coins[ctx.message.server.id] = {}
    if not author.id in coins[ctx.message.server.id]:
        coins[ctx.message.server.id][author.id] = 0
    coins[ctx.message.server.id][author.id] += coinsc
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.add_field(name=":moneybag: | Daily Reward", value=f"{author.mention}, I have put $**{coinsc}** in your account!", inline=False)
    await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)
@daily.error
async def cooldown_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        remainder = divmod(error.retry_after, 864000)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name="Slowdown :stuck_out_tongue_winking_eye: ", value=f"Cooldown: **{remainder}** \n Each Command: **1**", inline=False)
        await client.say(embed=embed)

@client.command(pass_context=True)
async def slots(ctx, *, amount: int = None):
    with open("economy.json", "r") as f:
        coins = json.load(f)
    choices = random.randint(0, 1)
    author = ctx.message.author
    amountt = coins[ctx.message.server.id][author.id]
    if author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if amount is None:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You need a slotting number! **Example:** \n ?slots 5")
        await client.say(embed=embed)
        return
    if coins[ctx.message.server.id][author.id] <= 1:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You need at least 2 coins in your account for this command!")
        await client.say(embed=embed)
        return
    if amount > coins[ctx.message.server.id][author.id]:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You don't have any coins avliable in your balance!")
        await client.say(embed=embed)
        return
    if amount <= 0:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You can't use any number less than 0")
        await client.say(embed=embed)
        return
    if choices == 0:
        coins[ctx.message.server.id][author.id] += amount * 2
        won = amount * 2
        slots = [
            ":tada: :tools: :timer:",
            ":timer: :tada: :timer:",
            ":tools: :timer: :tada:"
        ]
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots)), inline=False)
        msg =  await client.say(embed=embed)
        await asyncio.sleep(.50)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots)), inline=False)
        await client.edit_message(msg, embed=embed)
        await asyncio.sleep(.50)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots)), inline=False)
        await client.edit_message(msg, embed=embed)
        await asyncio.sleep(.50)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots)), inline=False)
        embed.add_field(name="Win Or Lose?", value=f"**You Won: {won}**")
        await client.edit_message(msg, embed=embed)
    else:
        coins[ctx.message.server.id][author.id] -= amount
        slots1 = [
            ":tada: :tools: :timer:",
            ":timer: :tada: :timer:",
            ":tools: :timer: :tada:"
        ]
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots1)), inline=False)
        msg =  await client.say(embed=embed)
        await asyncio.sleep(.50)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots1)), inline=False)
        await client.edit_message(msg, embed=embed)
        await asyncio.sleep(.50)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots1)), inline=False)
        await client.edit_message(msg, embed=embed)
        await asyncio.sleep(.50)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":slot_machine: Slots! :slot_machine:", value=(random.choice(slots1)), inline=False)
        embed.add_field(name="Win Or Lose?", value=f"**You Lost: {amount}**")
        await client.edit_message(msg, embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)

@client.command(pass_context=True)
async def givemoney(ctx, user: discord.Member = None, amount: int = None):
    with open("economy.json", "r") as f:
       	coins = json.load(f)
    author = ctx.message.author
    if ctx.message.author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if user == ctx.message.author:
        await client.say("I can't give you money. You are cheating my system!")
        return
    if user is None:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You need a user name!\n **Example:** \n ?givemoney @User")
        await client.say(embed=embed)
        return
    if amount is None:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You need a amount!\n **Example:** \n ?givemoney @User 5")
        await client.say(embed=embed)
        return
    if amount > coins[ctx.message.server.id][author.id]:
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name=":x: Error", value="You have no money in your balance!")
        await client.say(embed=embed)
        return
    if not ctx.message.server.id in coins:
        coins[ctx.message.server.id] = {}
    if not user.id in coins[ctx.message.server.id]:
        coins[ctx.message.server.id][user.id] = 0
    coins[ctx.message.server.id][user.id] += amount
    coins[ctx.message.server.id][author.id] -= amount
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.add_field(name="Money Added!", value=f"Added **${amount}** to {user.mention}!", inline=False)
    embed.set_thumbnail(url=user.avatar_url)
    await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)

@client.command(pass_context=True)
@commands.cooldown(1, 864000, commands.BucketType.user)
async def crate(ctx):
    with open("economy.json", "r") as f:
        coins = json.load(f)
    author = ctx.message.author
    crate = random.randint(100, 900)
    cratenames = [
        "King Crate",
        "Savage Crate",
        "Med Crate"
    ]
    if not ctx.message.server.id in coins:
        coins[ctx.message.server.id] = {}
    if not author.id in coins[ctx.message.server.id]:
        coins[ctx.message.server.id][author.id] = 0
    coins[ctx.message.server.id][author.id] += crate
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.add_field(name=":inbox_tray: | Crate Opened!", value=f"You have opened the ***{(random.choice(cratenames))}***", inline=False)
    embed.add_field(name=":moneybag: | Coin Amount:", value=f"**${crate}**", inline=False)
    await client.say(embed=embed)
    with open("economy.json", "w") as f:
        json.dump(coins, f, indent=4)
@crate.error
async def cooldown_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        remainder = divmod(error.retry_after, 864000)
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name="Slowdown :stuck_out_tongue_winking_eye: ", value=f"Cooldown: **{remainder}** \n Each Command: **1**", inline=False)
        await client.say(embed=embed)

@client.command(pass_context=True)
async def crates(ctx):
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.add_field(name="Crates Avaliable", value="King Crate \n Savage Crate \n Med Crate")
    embed.add_field(name="How to get them", value="**Type ?crate for a random crate out of those 3**")
    await client.say(embed=embed)





@client.command(pass_context=True)
async def bal(ctx, user: discord.Member = None):
    with open("economy.json", "r") as f:
        coins = json.load(f)
    author = ctx.message.author
    if ctx.message.author.bot:
        await client.say("Bot's will not use my commands. Those other bots will store my data full of junk!")
        return
    if user is None:
        if not author.id in coins[ctx.message.server.id]:
            coins[ctx.message.server.id][author.id] = 0
        coinss = coins[ctx.message.server.id][author.id]
        embed = discord.Embed(color=(random.randint(0, 0xffffff)))
        embed.add_field(name="Account Owner:", value=f"{author.mention}", inline=False)
        embed.add_field(name="Account Balance:", value=f"**${coinss}**", inline=False)
        embed.set_thumbnail(url=author.avatar_url)
        embed.set_footer(icon_url=author.avatar_url, text=f"Requested by: {author.name}")
        await client.say(embed=embed)
        return
    if not user.id in coins[ctx.message.server.id]:
        coins[ctx.message.server.id][user.id] = 0
    coinss = coins[ctx.message.server.id][user.id]
    embed = discord.Embed(color=(random.randint(0, 0xffffff)))
    embed.add_field(name="Account Owner:", value=f"{user.mention}", inline=False)
    embed.add_field(name="Account Balance:", value=f"**${coinss}**", inline=False)
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_footer(icon_url=user.avatar_url, text=f"Requested by: {author.name}")
    await client.say(embed=embed)

client.run(os.environ['TOKEN'])
