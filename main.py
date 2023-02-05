from dotenv import load_dotenv
import bot


if __name__ == '__main__':
  # load dotenv
  load_dotenv()

  # run the bot
  bot.run_discord_bot()
