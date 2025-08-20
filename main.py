import asyncio
import json
import argparse
import os
from twikit import Client

# ---------- CONFIG ----------
# IMPORTANT: Fill in your Twitter/X account credentials below.
# For better security, you can set these as environment variables.
# The script will create 'cookies.json' to save your login session.
USERNAME = os.environ.get('TWITTER_USERNAME', 'cosmin_lavric')
EMAIL = os.environ.get('TWITTER_EMAIL', 'cosminlavric53@gmail.com') # Needed if USERNAME is not an email
PASSWORD = os.environ.get('TWITTER_PASSWORD', 'Nemesix14$')
COOKIES_FILE = 'cookies.json'


# List of keywords to search for when in 'search' mode
KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "defi", "nft", "web3", "blockchain",
    "crypto", "cryptocurrency", "altcoin", "token", "airdrops", "airdrop",
    "rugpull", "ico", "presale", "staking", "yield farming",
    "smart contract", "layer2", "l2", "rollup", "solana", "sol", "cardano", "ada",
    "polkadot", "dot", "ripple", "xrp", "avalanche", "avax", "tron", "trx",
    "binance", "bnb", "coinbase", "rekt", "memecoin", "memes", "opensea",
    "rarible", "metamask", "wallet", "onchain", "on-chain", "zk", "zkrollup",
    "zk-proof", "zero knowledge", "privacy coin", "monero", "xmr", "lido",
    "liquid staking"
]

DEFAULT_OUT_FILE = "twikit_tweets.jsonl"
# IMPROVEMENT: Use a randomized delay range to appear more human-like
MIN_SEARCH_DELAY = 11  # seconds
MAX_SEARCH_DELAY = 27  # seconds

# ---------- UTILITIES ----------
def append_to_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def format_tweet_data(tweet) -> dict:
    return {
        'id': tweet.id,
        'text': tweet.text,
        'created_at': tweet.created_at,
        'user_id': tweet.user.id,
        'user_name': tweet.user.name,
        'user_screen_name': tweet.user.screen_name,
        'retweet_count': tweet.retweet_count,
        'favorite_count': tweet.favorite_count,
        'lang': tweet.lang,
        'keyword_searched': getattr(tweet, 'keyword_searched', None)
    }

# ---------- CORE TWIKIT FUNCTIONS ----------
async def search_by_keyword(client: Client, keyword: str, out_file: str):
    print(f"\n[INFO] Searching for latest tweets with keyword: '{keyword}'")
    try:
        tweets = await client.search_tweet(keyword, 'Latest')
        print(f"[INFO] Found {len(tweets)} tweets for '{keyword}'.")

        for tweet in tweets:
            tweet.keyword_searched = keyword
            formatted_tweet = format_tweet_data(tweet)
            append_to_jsonl(out_file, formatted_tweet)
        
        if tweets:
            print(f"[SUCCESS] Saved {len(tweets)} tweets to {out_file}")

    except Exception as e:
        print(f"[ERROR] An error occurred during keyword search for '{keyword}': {e}")

async def fetch_user_tweets(client: Client, user_id: str, out_file: str):
    print(f"[INFO] Fetching tweets for user ID: {user_id}")
    try:
        tweets = await client.get_user_tweets(user_id, 'Tweets')
        print(f"[INFO] Found {len(tweets)} tweets for user.")

        for tweet in tweets:
            formatted_tweet = format_tweet_data(tweet)
            append_to_jsonl(out_file, formatted_tweet)
            
        print(f"\n[SUCCESS] Saved {len(tweets)} tweets to {out_file}")
        
    except Exception as e:
        print(f"[ERROR] An error occurred while fetching user tweets: {e}")

# ---------- MAIN EXECUTION ----------
async def main():
    parser = argparse.ArgumentParser(description="Scrape Twitter using the twikit library.")
    parser.add_argument('mode', choices=['search', 'user'], help="The mode of operation: 'search' to use the keyword list, 'user' to fetch from a user.")
    parser.add_argument("--id", dest='user_id', help="The user ID to retrieve tweets from (required for 'user' mode).")
    parser.add_argument("--out", default=DEFAULT_OUT_FILE, help="Output JSONL file.")
    args = parser.parse_args()

    if args.mode == 'user' and not args.user_id:
        parser.error("--id is required when mode is 'user'.")

    if USERNAME == 'example_user' or PASSWORD == 'password0000':
        print("[ERROR] Please fill in your USERNAME and PASSWORD in the script or set environment variables.")
        return

    client = Client('en-US')
    try:
        if os.path.exists(COOKIES_FILE):
            print(f"[INFO] Loading session from {COOKIES_FILE}...")
            client.load_cookies(COOKIES_FILE)
            print("[INFO] Session loaded successfully.")
        else:
            print("[INFO] No cookie file found. Logging in with credentials...")
            await client.login(
                auth_info_1=USERNAME,
                auth_info_2=EMAIL,
                password=PASSWORD,
                cookies_file=COOKIES_FILE
            )
            print(f"[INFO] Login successful. Session saved to {COOKIES_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to log in or load session. Error: {e}")
        return

    if args.mode == 'search':
        print(f"[INFO] Starting keyword search mode. Will search for {len(KEYWORDS)} keywords.")
        for keyword in KEYWORDS:
            await search_by_keyword(client, keyword, args.out)
            # IMPROVEMENT: Wait for a random duration to make activity less bot-like
            delay = random.uniform(MIN_SEARCH_DELAY, MAX_SEARCH_DELAY)
            print(f"[INFO] Waiting for {delay:.1f} seconds before next search...")
            await asyncio.sleep(delay)
        print("\n[INFO] All keywords have been searched.")
            
    elif args.mode == 'user':
        await fetch_user_tweets(client, args.user_id, args.out)

if __name__ == "__main__":
    asyncio.run(main())