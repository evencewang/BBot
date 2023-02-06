'''Object that represents a song'''
import discord
from ytdl import YTDLSource


class Song():
  def __init__(self, source: YTDLSource):
    self.source = source
    self.requester = source.requester

  def create_embed_msg(self):
    embed = discord.Embed(
      title='Now playing',
      description='```css\n{0.source.title}\n```'.format(self),
      color=discord.Color.blurple()
    )\
    .add_field(name='Duration', value=self.source.duration)\
    .add_field(name='Requested by', value=self.requester.mention)\
    .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))\
    .add_field(name='Upload date', value=self.source.upload_date)\
    .add_field(name='Views', value=self.source.views)\
    .add_field(name='URL', value='[Click to visit]({0.source.url})'.format(self))\
    .set_thumbnail(url=self.source.thumbnail)

    return embed
