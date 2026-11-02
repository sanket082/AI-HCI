"""Run with python app.py. No local substitute for cloud sentiment."""
from bot import Chatbot

def main():
    bot = Chatbot()
    print('Azure Sentiment Chatbot | English | type help or quit')
    print('Analysis sends text to Azure. Do not enter sensitive or personal information.')
    while True:
        try:
            message = input('You: ')
        except (EOFError, KeyboardInterrupt):
            print('\nBot: Goodbye!')
            break
        print('Bot:', bot.reply(message))
        if message.strip().casefold() in ('quit', 'exit', '/quit'):
            break

if __name__ == '__main__':
    main()
