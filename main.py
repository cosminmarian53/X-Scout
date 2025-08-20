import asyncio
import json
import argparse
import os
import random
import atexit
from twikit import Client
from dotenv import load_dotenv

# ---------- CONFIG ----------
# Load credentials from the .env file
load_dotenv()
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
CT0 = os.getenv('TWITTER_CT0')

# This will be the name of the temporary cookie file we create
TEMP_COOKIE_FILE = "temp_cookies.json"

# List of keywords to search for
KEYWORDS = [
    # Core Platforms & Concepts (for context)
    "ethereum", "solana", "bitcoin", "blockchain", "web3", "adoption", "regulation",
    # Core Security Topics
    "cybersecurity", "infosec", "web3 security", "smart contract audit",
    "defi exploit", "crypto hack", "bug bounty", "ctf contest", "pentesting",
    # Platform-Specific Security
    "ethereum security", "solana security", "cosmos security","zero-knowledge","noir-lang","zk-proofs","zksync"
    # Technical Concepts & Tools
    "solidity", "rustlang", "zero-knowledge proof", "threat intelligence",
    "malware analysis", "vulnerability research", "security advisory",
    "open source security", "devsecops","multiversx","egld","eth","rust","cantina.xyz","code4rena",
    "sherlock.xyz","gmx","cyfrin","cyfrin updraft","codehawks","trail of bits","openzeppelin","pashov",
    "blockchain","crypto", "privacy","defi","sherlockdefi","security news",
    "AI agents in blockchain","AI in cybersecurity","AI in web3","decentralized exchange","smart contract programming","smart contract programmer"
]

DEFAULT_OUT_FILE = "twikit_tweets.jsonl"
MIN_SEARCH_DELAY = 12
MAX_SEARCH_DELAY = 36

# ---------- UTILITIES ----------
def create_temp_cookie_file():
    if not AUTH_TOKEN or not CT0:
        return False
    cookie_data = {"auth_token": AUTH_TOKEN, "ct0": CT0}
    with open(TEMP_COOKIE_FILE, "w") as f:
        json.dump(cookie_data, f)
    return True

def cleanup_temp_cookie_file():
    if os.path.exists(TEMP_COOKIE_FILE):
        os.remove(TEMP_COOKIE_FILE)
        print("\n[INFO] Cleaned up temporary cookie file.")

atexit.register(cleanup_temp_cookie_file)

def append_to_jsonl(path: str, obj: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def format_tweet_data(tweet) -> dict:
    """
    Formats the tweet data, prioritizing the 'full_text' attribute
    to prevent truncated content.
    """
    # FIX: Prioritize 'full_text' if it exists, otherwise fall back to 'text'.
    tweet_text = tweet.full_text if hasattr(tweet, 'full_text') and tweet.full_text else tweet.text
    
    return {
        'id': tweet.id,
        'text': tweet_text, # Use the potentially longer text
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
            append_to_jsonl(out_file, format_tweet_data(tweet))
        if tweets:
            print(f"[SUCCESS] Saved {len(tweets)} tweets to {out_file}")
    except Exception as e:
        print(f"[ERROR] An error occurred for keyword '{keyword}': {e}")

# ---------- MAIN EXECUTION ----------
async def main():
    parser = argparse.ArgumentParser(description="Automated Twitter scraper for security/dev info.")
    parser.add_argument("--out", default=DEFAULT_OUT_FILE, help="Output JSONL file.")
    args = parser.parse_args()

    if not create_temp_cookie_file():
        print("[ERROR] .env file not found or is missing tokens. Run 'make setup' first.")
        return

    client = Client('en-US')
    try:
        print(f"[INFO] Loading session from temporary cookie file...")
        client.load_cookies(TEMP_COOKIE_FILE)
        print("[INFO] Login successful.")
    except Exception as e:
        print(f"[ERROR] Failed to log in with cookies. Error: {e}")
        return

    print(f"[INFO] Starting keyword search for {len(KEYWORDS)} blended keywords.")
    for keyword in KEYWORDS:
        await search_by_keyword(client, keyword, args.out)
        delay = random.uniform(MIN_SEARCH_DELAY, MAX_SEARCH_DELAY)
        print(f"[INFO] Waiting for {delay:.1f} seconds...")
        await asyncio.sleep(delay)
    print("\n[INFO] All keywords have been searched.")

if __name__ == "__main__":
    asyncio.run(main())