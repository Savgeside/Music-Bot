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

players = {}


@client.command(pass_context=True)
async def join(ctx):
  channel = ctx.message.author.voice.voice_channel
  await client.join_voice_channel(channel)
  
@client.command(pass_context=True)
async def leave(ctx):
  server = ctx.message.server
  voice_client = client.voice_client_in(server)
  await voice_client.disconnect()
  
@client.command(pass_context=True)
async def play(ctx, *, url):
  server = ctx.message.server
  voice_client = client.voice_client_in(server)
  player = await voice_client.create_ytdl_player(url)
  players[server.id] = player
  player.start
    

bot.run(os.environ['TOKEN'])
