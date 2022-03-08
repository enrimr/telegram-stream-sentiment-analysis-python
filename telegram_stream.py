from telethon import TelegramClient, events
from datetime import datetime
import pandas as pd
import yaml
import os
from elasticsearch import Elasticsearch
from sentiment_analysis_spanish import sentiment_analysis
import time

print("Init Telegram Streaming app")

print("😁 Loading channels...")
channels = pd.read_csv('telegram_channels.csv')
channels = tuple(channels['Channels'])

print("😁 Loading config...")
if os.path.isfile("config.yml"):
    with open("config.yml", 'r') as ymlfile:
        config_file = yaml.safe_load(ymlfile)
        
        
api_id = config_file['API_ID']
api_hash = config_file['API_HASH']
elastic_url = config_file['ELASTIC_URL']
elastic_user = config_file['ELASTIC_USER']
elastic_password = config_file['ELASTIC_PASSWORD']
elastic_app_id = config_file['ELASTIC_APP_ID']
elastic_api_key = config_file['ELASTIC_API_KEY']

print("😁 Creating ElasticSearch client...")
es = Elasticsearch(
    elastic_url, 
    #http_auth=(elastic_user, elastic_password), #deprecated
    api_key=(elastic_app_id, elastic_api_key),
    verify_certs=False,
    ssl_show_warn=False
)

print("😁 Creating Telegram Client...")
client = TelegramClient('session_name', api_id, api_hash)

print("😁 Loading Sentiment Analysis Spanish...")
sentiment = sentiment_analysis.SentimentAnalysisSpanish()

print("👍 Done!")

print("⏳ Waiting for messages")

#@client.on(events.NewMessage(chats=channels)) #if you want to filter by channels
@client.on(events.NewMessage())
async def my_event_handler(event):
    me = await client.get_me()
    sender = await event.get_sender()
    print('    > Message received from a:')
    print(sender.__class__.__name__)

    message_sentiment = sentiment.sentiment(event.raw_text)
    print('    > Sentiment value:')
    print(message_sentiment)
    sentiment_value = 'tbd'

    if message_sentiment > 0.4:
        sentiment_value = 'positive'
    elif message_sentiment < 0.1:
        sentiment_value = 'negative'
    else:
        sentiment_value = 'neutral'

    is_channel = False
    if sender.__class__.__name__ == 'Channel':
        username = sender.title
        is_channel = True
    else:
        username = sender.first_name

    chat_id = 0
    print(event.message.peer_id)
    if hasattr(event.message.peer_id, 'channel_id'):
        chat_id = event.message.peer_id.channel_id
        print(chat_id)
    elif hasattr(event.message.peer_id, 'chat_id'):
        chat_id = event.message.peer_id.chat_id
        print(chat_id)
    elif hasattr(event.message.peer_id, 'user_id'):
        chat_id = 0

    data = {'message_id': event.message.id,
        'channel_id': chat_id,
         'user_id': sender.id,
         'username': username,
         'timestamp': datetime.now(),
         'message': event.raw_text,
         'is_bot': event.message.via_bot_id,
         'sentiment': sentiment_value,
         'is_channel' : is_channel
         }

    print('DATA:')
    print(data)

    # add document to index
    res = es.index(index='telegram-sentiment', id=data['message_id'], document=data)
    print(res['result'])
    
client.start()
client.run_until_disconnected()

print("Thanks for using Telegram Sentiment! 💃")

