import os
import discord
import responses


async def send_message(message, user_message, is_private):
  try:
    response = responses.handle_response(user_message)
    await message.author.send(response) if is_private else await message.channel.send(response)
  except Exception as e:
    print(e)


def run_discord_bot():
  TOKEN = os.environ['DISCORD_TOKEN']
  client = discord.Client(intents=discord.Intents.all())

  @client.event
  async def on_ready():
    print('{} is now running!'.format(client.user))

  @client.event
  async def on_message(message):
    if message.author == client.user:
      return

    user_message = str(message.content)

    if user_message[0] == '?':
      user_message = user_message[1:]
      await send_message(message, user_message, is_private=True)
    else:
      await send_message(message, user_message, is_private=False)

  client.run(TOKEN)
