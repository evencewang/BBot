import random


def handle_response(message) -> str:
  p_message = message.lower()
  if p_message == 'hello':
    return 'Hey there!'

  elif p_message == 'roll':
    return str(random.randint(1, 6))

  elif p_message == '!help':
    return '`This is a default help message. You can modify this in the responses.py file.`'
