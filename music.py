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
  await client.join_voice_channel(channel)
  await client.say(f":music_note: **I have joined {channel}** :thumbsup:")
  
@client.command(pass_context=True)
async def leave(ctx):
  server = ctx.message.server
  voice_client = client.voice_client_in(server)
  await voice_client.disconnect()
  await client.say(f":music_note: **I have left {voice_client}**")
  
@client.command(pass_context=True)
async def play(ctx, *, url):
  server = ctx.message.server
  voice_client = client.voice_client_in(server)
  player = await voice.create_ytdl_player(url, ytdl_options=opts)
  players[server.id] = player
  player.start()
  await client.say(f"**Searching** :mag_right: - ``{url}``")
  await client.say(f":music_note: **Now playing** - ``{player.title}``")

   


client.run(os.environ['TOKEN'])
