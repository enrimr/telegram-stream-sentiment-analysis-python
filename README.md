# Telegram Streaming Sentiment Analysis

This is a python program to collect messages from your user Telegram account. You can configure to get them from various telegram channels. 

This script is based on the original source code from https://github.com/rohanvartak1996/Telegram-Streaming 

It use Telegram API to stream the messages from Telegram.

## Installing Requirements

pip install -r requirements.txt

## Configure Telegram
Create a application in telegram to obtain the API Id and Hash.

https://core.telegram.org/api/obtaining_api_id

Put API Id and Hash in the config.yml file.

## Configure ElasticSearch
You need to have ElasticSearch installed to connect and store the messages. Any other database can be used in place of it.

In Kibana, you can create both of the index and the API credentials.

For the Index, you need to create the index telegram-sentiment.

Go to DevTools and:

PUT /telegram-sentiment

To create API credentials:

POST /_security/api_key
{
  "name": "telegram-script",
  
  "metadata": {
    "application": "telegram-script",
    "environment": {
       "level": 1,
       "trusted": true,
       "tags": ["dev", "staging"]
    }
  }
}


## Running the code

You need to have a Telegram account to run the code.

When you run the python file, Telegram will ask you to login using your account information. You will recieve a code on your telegram which you need to enter.

The 'me' channel has been added to the list of telegram channels.

All the messages will be saved to your ElasticSearch. 

To run the python file:
```
python telegram-stream.py
```