import asyncio
import functools
import youtube_dl
import discord
from discord.ext import commands


youtube_dl.utils.bug_reports_message = lambda: ''


class YTDLSource(discord.PCMVolumeTransformer):
  ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
  }

  ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
  }

  YTDL = youtube_dl.YoutubeDL(ytdl_format_options)

  def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
    super().__init__(source, volume)

    self.requester = ctx.author
    self.channel = ctx.channel
    self.data = data

    self.uploader = data.get('uploader')
    self.uploader_url = data.get('uploader_url')
    date = data.get('upload_date')
    self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
    self.title = data.get('title')
    self.thumbnail = data.get('thumbnail')
    self.description = data.get('description')
    self.duration = self.parse_duration(int(data.get('duration')))
    self.tags = data.get('tags')
    self.url = data.get('webpage_url')
    self.views = data.get('view_count')
    self.likes = data.get('like_count')
    self.dislikes = data.get('dislike_count')
    self.stream_url = data.get('url')

  def __str__(self):
    return '**{0.title}** by **{0.uploader}**'.format(self)

  @classmethod
  async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
    loop = loop or asyncio.get_event_loop()

    partial = functools.partial(cls.YTDL.extract_info, search, download=False, process=False)
    data = await loop.run_in_executor(None, partial)

    if data is None:
      raise Exception('Couldn not find anything that matches `{}`'.format(search))

    if 'entries' not in data:
      to_process = data
    else:
      to_process = None
      for entry in data['entries']:
        if entry and entry.get('is_live') is False:
          to_process = entry
          break

      if to_process is None:
        raise Exception('Could not find anything that matches `{}`'.format(search))

    webpage_url = to_process['webpage_url']
    partial = functools.partial(cls.YTDL.extract_info, webpage_url, download=False)
    processed_info = await loop.run_in_executor(None, partial)

    if processed_info is None:
      raise Exception('Could not fetch `{}`'.format(webpage_url))

    if 'entries' not in processed_info:
      info = processed_info
    else:
      info = None
      for entry in processed_info['entries']:
        if entry:
          info = entry
          break

      if info is None:
        raise Exception('Could not retrieve any matches for `{}`'.format(webpage_url))

    return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.ffmpeg_options), data=info)

  @staticmethod
  def parse_duration(duration: int):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    duration = []
    if days > 0:
      duration.append('{} days'.format(days))
    if hours > 0:
      duration.append('{} hours'.format(hours))
    if minutes > 0:
      duration.append('{} minutes'.format(minutes))
    if seconds > 0:
      duration.append('{} seconds'.format(seconds))

    return ', '.join(duration)

