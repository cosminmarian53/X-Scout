import json
import argparse
import re

# --- SCORING CONFIGURATION ---

# REVISED: Balanced list. High scores for security, moderate for news, low for context.
USEFUL_KEYWORDS = {
    # High-Value Security Intel
    'vulnerability': 15, 'exploit': 15, '0-day': 15, 'rce': 12,
    'security audit': 12, 'post-mortem': 10, 'threat actor': 8, 'malware': 8,
    'phishing campaign': 8, 'responsible disclosure': 7, 'poc': 8,
    # Bug Bounties & Contests
    'bug bounty': 12, 'ctf contest': 10, 'security contest': 10, 'hackerone': 8,
    # Regulation & Adoption (High-level News)
    'regulation': 6, 'adoption': 6, 'partnership': 5, 'integrates': 5,
    'institutional': 4, 'security advisory': 10,
    # Technical & Development
    'github': 6, 'open source': 5, 'devtool': 6, 'sdk': 5, 'technical deep dive': 8,
    'whitepaper': 6, 'research paper': 7, 'hardhat': 5, 'foundry': 5,
    # Contextual Keywords (Low score, acts as a multiplier)
    'ethereum': 2, 'solana': 2, 'bitcoin': 1, 'blockchain': 1, 'web3': 1,
    'smart contract': 3, 'protocol': 3, 'mainnet': 2, 'testnet': 1,
    'governance attack': 9, 'oracle manipulation': 9, 'bridge exploit': 9, "zero-knowledge":5,
    "noir-lang":3,"zk-proofs":3
}

# Penalizes investment, trading, and price talk.
NOISE_KEYWORDS = {
    # Trading & Price Talk (High Penalty)
    'price target': -15, 'long': -10, 'short': -10, 'trading signal': -15,
    'bullish': -10, 'bearish': -10, 'rsi': -10, 'moving average': -10,
    'chart': -8, 'undervalued': -8, '1000x': -10, 'pump': -8, 'dump': -8,
    'dip': -6, 'ath': -6, 'moon': -10,
    # Generic Hype & Spam
    'airdrop': -10, 'giveaway': -10, 'tag friends': -8, 'retweet to win': -8,
    'gleam': -10, 'whitelist': -5, 'presale': -5, 'shill': -6,
    'lfg': -10, 'killing it': -6, 'solid project': -6,
}

# Phrases that will instantly disqualify a tweet.
DISQUALIFYING_PHRASES = [
    "dm now for", "dm for recovery", "for reliable recovery", "contact for recovery",
    "lost funds on", "fast & trusted recovery", "claimed some sepolia eth"
]

SCORE_THRESHOLD = 6 # Raised threshold slightly for higher quality signal

# --- DEDUPLICATION & FILTERING LOGIC ---

def normalize_text_for_deduplication(text):
    """Removes noise (URLs, mentions) to identify functionally duplicate content."""
    text = re.sub(r'https?:\/\/\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\$\w+', '', text)
    return ' '.join(text.split()).lower()

def calculate_score(tweet_text):
    lower_text = tweet_text.lower()
    for phrase in DISQUALIFYING_PHRASES:
        if phrase in lower_text:
            return -100

    score = 0
    for keyword, points in USEFUL_KEYWORDS.items():
        if keyword in lower_text:
            score += points
    for keyword, points in NOISE_KEYWORDS.items():
        if keyword in lower_text:
            score += points

    if lower_text.startswith('@') and len(lower_text.split()) < 8:
        score -= 5
    if lower_text.count('#') > 6:
        score -= 7
    if any(char.isdigit() for char in lower_text):
        score += 1
        
    return score

def main():
    parser = argparse.ArgumentParser(description="Filter tweets for developer/security info.")
    parser.add_argument("input_file", help="Input JSONL file (e.g., twikit_tweets.jsonl)")
    parser.add_argument("--out", default="filtered_tweets.jsonl", help="Output file for useful tweets.")
    parser.add_argument("--min-score", type=int, default=SCORE_THRESHOLD, help="The minimum score for a tweet to be kept.")
    args = parser.parse_args()

    print(f"Filtering tweets from '{args.input_file}' with a minimum score of {args.min_score}...")
    
    useful_tweets = []
    total_tweets = 0
    seen_normalized_tweets = set()

    with open(args.input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            total_tweets += 1
            try:
                tweet = json.loads(line)
                tweet_text = tweet.get('text', '')
                
                normalized_text = normalize_text_for_deduplication(tweet_text)
                if not normalized_text or normalized_text in seen_normalized_tweets:
                    continue

                score = calculate_score(tweet_text)
                
                if score >= args.min_score:
                    tweet['filter_score'] = score
                    useful_tweets.append(tweet)
                    seen_normalized_tweets.add(normalized_text)

            except json.JSONDecodeError:
                print(f"[WARN] Skipping a malformed line: {line.strip()}")

    useful_tweets.sort(key=lambda x: x['filter_score'], reverse=True)

    with open(args.out, 'w', encoding='utf-8') as f_out:
        for tweet in useful_tweets:
            f_out.write(json.dumps(tweet, ensure_ascii=False) + '\n')

    print("\n--- Filtering Complete ---")
    print(f"Processed: {total_tweets} tweets")
    print(f"Found:     {len(useful_tweets)} unique, high-value tweets")
    print(f"Results saved to '{args.out}'")
    print("\n--- Top 5 Developer/Security Tweets ---")
    for i, tweet in enumerate(useful_tweets[:5]):
        print(f"{i+1}. (Score: {tweet['filter_score']}) {tweet['text']}")

if __name__ == "__main__":
    main()