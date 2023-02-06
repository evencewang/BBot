import os
import discord
from discord.ext import commands
from ytdl import *


def run_bot():
  TOKEN = os.environ['DISCORD_TOKEN']
  intents = discord.Intents.all()
  intents.message_content = True
  intents.voice_states = True
  bot = commands.Bot(command_prefix='!', intents=intents)

  @bot.event
  async def on_ready():
    print('{} is now running!'.format(bot.user))

  @bot.command(name='join', help='Bot joins the voice channel')
  async def join(ctx: commands.Context):
    '''Bot joins a voice channel'''
    if not ctx.message.author.voice:
      await ctx.send('{} is not connected to a voice channel, bot is unable to join.'\
        .format(ctx.message.author.name))
      return

    channel = ctx.message.author.voice.channel
    await channel.connect()

  @bot.command(name='leave', help='Bot leaves the voice channel')
  async def leave(ctx: commands.Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
      await stop(ctx)
      await voice_client.disconnect()
      return
    await ctx.send('Bot is not connected to a voice channel.')

  @bot.command(name='play', help='Bot plays the audio from the given url')
  async def play(ctx: commands.Context, *args):
    search = ' '.join(args)

    voice_channel = ctx.message.guild.voice_client
    if not (voice_channel and voice_channel.is_connected()):
      await ctx.invoke(join)
      voice_channel = ctx.message.guild.voice_client
    elif voice_channel.is_playing():
      voice_channel.stop()

    async with ctx.typing():
      try:
        source = await YTDLSource.create_source(ctx, search, loop=bot.loop)
      except YTDLError as e:
        await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
      else:
        voice_channel.play(source)
      await ctx.send('**Now playing:** {}'.format(source))

  @bot.command(name='pause', help='Bot pauses the audio')
  async def pause(ctx: commands.Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_playing():
      voice_client.pause()
      return
    await ctx.send('Bot is not playing anything.')

  @bot.command(name='resume', help='Bot resumes the audio')
  async def resume(ctx: commands.Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_paused():
      voice_client.resume()
      return
    await ctx.send('Bot is not paused, use **play** command to play something.')

  @bot.command(name='stop', help='Bot stops the audio')
  async def stop(ctx: commands.Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_playing():
      voice_client.stop()
      await ctx.send('Stopped playing audio.')
      voice_client.cleanup()
      return
    await ctx.send('Bot is not playing anything.')

  bot.run(TOKEN)
