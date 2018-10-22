import discord
import youtube_dl
import asyncio
from discord.ext import commands

TOKEN = "NTAzNjk1NzYxNzYzMDc0MDcx.Dq6bAw.056jAYmPcWQIlpJ1CvHlGxarT0Q"

client = commands.Bot(command_prefix="-")

@client.event
async def on_ready():
    print("Bot online.")

players = {}

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    if channel is None:
        await client.say(":exclamation: | **You need to join a voice channel!**")
        return
    await client.join_voice_channel(channel)
    await client.say(f"**I have joined {channel}** <:music:503713910763814912>")

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    if voice_client is None:
        await client.say(":exclamation: | **I am not in a voice channel!**")
        return
    await voice_client.disconnect()
    await client.say(f"**I have left** <:music:503713910763814912>")

@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_dl_player(url)
    players[server.id] = player
    player.start()

client.run(TOKEN)
