import asyncio
import json
import argparse
import os
import random
import atexit
import time
from twikit import Client
from dotenv import load_dotenv
from session_manager import HumanSession

# ---------- CONFIG ----------
# Load credentials from the .env file
load_dotenv()
AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
CT0 = os.getenv('TWITTER_CT0')

# This will be the name of the temporary cookie file we create
TEMP_COOKIE_FILE = "temp_cookies.json"

# List of user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

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
    tweet_text = tweet.full_text if hasattr(tweet, 'full_text') and tweet.full_text else tweet.text
    
    return {
        'id': tweet.id,
        'text': tweet_text,
        'created_at': tweet.created_at,
        'user_id': tweet.user.id,
        'user_name': tweet.user.name,
        'user_screen_name': tweet.user.screen_name,
        'retweet_count': tweet.retweet_count,
        'favorite_count': tweet.favorite_count,
        'lang': tweet.lang,
        'keyword_searched': getattr(tweet, 'keyword_searched', None)
    }

def generate_search_variations(keyword):
    """Generate human-like variations of search keywords."""
    variations = [keyword]
    
    qualifiers = ["latest", "new", "recent", "top", "best"]
    if random.random() < 0.15:
        variations.append(f"{random.choice(qualifiers)} {keyword}")
    
    industry_terms = ["news", "update", "guide", "tutorial", "article"]
    if random.random() < 0.1:
        variations.append(f"{keyword} {random.choice(industry_terms)}")
        
    if random.random() < 0.02 and len(keyword) > 5:
        typo_pos = random.randint(1, len(keyword)-1)
        typo_keyword = keyword[:typo_pos] + keyword[typo_pos+1:]
        variations.append(typo_keyword)
    
    return random.choice(variations)

# ---------- CORE TWIKIT FUNCTIONS ----------
async def search_by_keyword(client: Client, keyword: str, out_file: str):
    """Human-like search behavior with micro-pauses and variations."""
    print(f"\n[INFO] Searching for latest tweets with keyword: '{keyword}'")
    await asyncio.sleep(random.uniform(0.5, 3.5))

    try:
        # Using the keyword directly as complex filters can cause 404 errors
        actual_query = keyword
        
        sort_options = ['Latest', 'Top']
        sort_choice = random.choices(sort_options, weights=[0.8, 0.2])[0]
        
        tweets = await client.search_tweet(actual_query, sort_choice)
        
        await asyncio.sleep(random.uniform(1.5, 5))
        
        result_phrases = [
            f"Found {len(tweets)} tweets for '{keyword}'.",
            f"Search returned {len(tweets)} results for '{keyword}'.",
            f"Got {len(tweets)} matching tweets for '{keyword}'."
        ]
        print(random.choice(result_phrases))
        
        for tweet in tweets:
            if random.random() < 0.05:
                continue
                
            tweet.keyword_searched = keyword
            append_to_jsonl(out_file, format_tweet_data(tweet))
            
            if random.random() < 0.2:
                await asyncio.sleep(random.uniform(0.1, 0.3))
        
        if tweets:
            print(f"[SUCCESS] Saved tweets to {out_file}")
    except Exception as e:
        print(f"[ERROR] An error occurred for keyword '{keyword}': {e}")
        raise

async def search_with_backoff(client, keyword, out_file, max_retries=3):
    """Search with exponential backoff for rate limits."""
    retry = 0
    base_wait = 60
    
    while retry <= max_retries:
        try:
            await search_by_keyword(client, keyword, out_file)
            return
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                retry += 1
                if retry > max_retries:
                    print(f"[ERROR] Max retries exceeded for '{keyword}'")
                    return
                
                wait_time = base_wait * (2 ** (retry - 1)) * (0.5 + random.random())
                print(f"[WARN] Rate limited. Waiting {wait_time:.1f}s before retry {retry}/{max_retries}")
                await asyncio.sleep(wait_time)
            else:
                print(f"[ERROR] Non-rate-limit error for '{keyword}': {e}")
                return

# ---------- MAIN EXECUTION ----------
async def main():
    parser = argparse.ArgumentParser(description="Automated Twitter scraper for security/dev info.")
    parser.add_argument("--out", default=DEFAULT_OUT_FILE, help="Output JSONL file.")
    args = parser.parse_args()

    # Clear previous raw tweets before starting a new run
    if os.path.exists(args.out):
        print(f"[INFO] Clearing previous raw tweets from {args.out}...")
        os.remove(args.out)

    if not create_temp_cookie_file():
        print("[ERROR] .env file not found or is missing tokens. Run 'make setup' first.")
        return

    client = Client('en-US', user_agent=random.choice(USER_AGENTS))
    try:
        print(f"[INFO] Loading session from temporary cookie file...")
        client.load_cookies(TEMP_COOKIE_FILE)
        print("[INFO] Login successful.")
    except Exception as e:
        print(f"[ERROR] Failed to log in with cookies. Error: {e}")
        return

    try:
        while True:
            session = HumanSession()
            
            session_keywords_count = random.randint(5, min(12, len(KEYWORDS)))
            session_keywords = random.sample(KEYWORDS, session_keywords_count)
            
            print(f"[INFO] Starting session with {len(session_keywords)} keywords.")
            
            for keyword in session_keywords:
                if not session.should_continue():
                    print("[INFO] Session time limit reached, ending session.")
                    break
                
                search_term = generate_search_variations(keyword)
                
                await search_with_backoff(client, search_term, args.out)
                
                if session.should_take_break():
                    break_duration = session.get_break_duration()
                    print(f"[INFO] Taking a short break for {break_duration:.1f} seconds...")
                    await asyncio.sleep(break_duration)
                else:
                    delay = session.get_next_delay()
                    print(f"[INFO] Waiting {delay:.1f} seconds before next search...")
                    await asyncio.sleep(delay)
            
            if random.random() < 0.3:
                print("[INFO] Ending scraping for now.")
                break
            
            session_break = random.uniform(1800, 3600)
            print(f"[INFO] Session completed. Taking a long break ({session_break/60:.1f} minutes).")
            await asyncio.sleep(session_break)
    except KeyboardInterrupt:
        print("\n[INFO] Script interrupted by user. Shutting down gracefully...")
    except Exception as e:
        print(f"\n[FATAL] An unexpected error occurred: {e}")
    finally:
        print("\n[INFO] All scraping sessions complete.")

if __name__ == "__main__":
    asyncio.run(main())