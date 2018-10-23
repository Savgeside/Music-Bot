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
    for i in client.servers:
        playing[i.id]=False


async def checking_voice(ctx):
    await asyncio.sleep(130)
    if playing[ctx.message.server.id]== False:
        try:
            pos = in_voice.index(ctx.message.server.id)
            del in_voice[pos]
            server = ctx.message.server
            voice_client = client.voice_client_in(server)
            await voice_client.disconnect()
            await client.say("{} left because there was no audio playing for a while".format(client.user.name))
        except:
            pass

@client.event
async def on_ready():
    client.loop.create_task(all_false())
    print(client.user.name)    
    
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
        return
    if playing[ctx.message.server.id] == False:
        voice = client.voice_client_in(ctx.message.server)
        player = await voice.create_ytdl_player(url, ytdl_options=opts, after=lambda: client.loop.create_task(player_in(ctx)))
        players[ctx.message.server.id] = player
        # play_in.append(player)
        if players[ctx.message.server.id].is_live == True:
            await client.say(":musical_note: **Can not play live audio yet.**")
        elif players[ctx.message.server.id].is_live == False:
            player.start()
            await client.say(f"Searching :mag_right: ``{url}``")
            await client.say(f":musical_note: Now playing ``{player.title}``")
            await client.say(f":clock: Testing Time: ``{player.time}``")
            playing[ctx.message.server.id] = True



@client.command(pass_context=True)
async def queue(con):
    await client.say(f"There is ")

@client.command(pass_context=True)
async def pause(ctx):
    players[ctx.message.server.id].pause()
    await client.say(":musical_note: I have now paused the audio")
    
@client.command(pass_context=True)
async def resume(ctx):
    players[ctx.message.server.id].resume()
    await client.say(":musical_note: I have now resumed the audio")
          


@client.command(pass_context=True)
async def stop(ctx, con):
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
   


client.run(os.environ['TOKEN'])
