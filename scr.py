import requests
import asyncio
import os
from telegram import Bot

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
USERNAMES = ['MonThreat', 'DarkWebInformer', 'DailyDarkWeb']
POLL_INTERVAL = 60  # seconds

bot = Bot(token=TELEGRAM_TOKEN)
last_seen = {}

def get_user_id(username):
    url = f'https://api.twitter.com/2/users/by/username/{username}'
    headers = {'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}'}
    r = requests.get(url, headers=headers)
    return r.json().get('data', {}).get('id')

def get_latest_tweets(user_id, since_id=None):
    url = f'https://api.twitter.com/2/users/{user_id}/tweets'
    params = {
        'max_results': 5,
        'tweet.fields': 'created_at',
        'exclude': 'retweets,replies',
    }
    if since_id:
        params['since_id'] = since_id

    headers = {'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}'}
    r = requests.get(url, headers=headers, params=params)
    return r.json().get('data', [])

async def send_to_telegram(message):
    await bot.send_message(chat_id=CHAT_ID, text=message, disable_web_page_preview=False)

async def main_loop():
    user_ids = {u: get_user_id(u) for u in USERNAMES}
    print('🔍 Monitoring Twitter accounts for new tweets...')

    while True:
        for username, user_id in user_ids.items():
            tweets = get_latest_tweets(user_id, last_seen.get(username))
            if tweets:
                for tweet in reversed(tweets):
                    tweet_url = f"https://x.com/{username}/status/{tweet['id']}"
                    await send_to_telegram(f"🕵️ New tweet from @{username}:\n{tweet_url}")
                    last_seen[username] = tweet['id']
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    asyncio.run(main_loop())
