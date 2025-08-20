import os
import json
import argparse
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_TWEETS_FILE = 'filtered_tweets.jsonl'
DEFAULT_SUMMARY_FILE = 'summary.txt'

# --- MAIN LOGIC ---
def get_ai_summary(content: str):
    """Uses the Google Generative AI API to summarize the provided text."""
    if not API_KEY:
        print("[WARN] GOOGLE_API_KEY not found in .env file. Skipping summary.")
        return "AI Summary disabled: GOOGLE_API_KEY is not set."

    print("[INFO] Contacting Google's Generative AI for a full summary...")
    try:
        genai.configure(api_key=API_KEY)
        
        # UPDATED: Increased max_output_tokens to allow for longer summaries
        generation_config = {"temperature": 0.5, "max_output_tokens": 4096} 
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        prompt = (
            f"As of {current_date}, you are a senior cybersecurity analyst specialized in both traditional security and web3/blockchain, reporting to user '{os.getenv('USER', 'cosminmarian53')}'.\n\n"
            "Your primary directive is to produce a high-level intelligence briefing from the provided tweets. Before summarizing, you must first act as a critical filter. "
            "Aggressively discard any tweets that appear to be marketing, spam, price speculation, or otherwise irrelevant to actionable security intelligence. Your summary must only be based on the remaining, high-value information.\n\n"
            "Focus on: actionable intelligence, emerging threats, new vulnerabilities, and significant developer news across both traditional and web3 domains. "
            "Explicitly include details about smart contract vulnerabilities, blockchain exploits, and web3 security tool developments.\n\n"
            "Format the output using markdown bullet points (`*` or `-`) and use headers (`## Category`) to organize the information. Be direct, factual, and concise."
            f"\n\nHere are all the raw tweets to analyze and filter:\n\n{content}"
        )
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"[ERROR] Failed to get Google AI summary: {e}")
        return f"Could not generate AI summary due to an error: {e}"

def main():
    parser = argparse.ArgumentParser(description="Summarize all tweets from a file using Google's Generative AI.")
    parser.add_argument("--in", default=DEFAULT_TWEETS_FILE, dest="input_file", help="Input JSONL file of filtered tweets.")
    parser.add_argument("--out", default=DEFAULT_SUMMARY_FILE, help="Output text file for the summary.")
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            tweets = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"[WARN] No tweets file found at '{args.input_file}'. Skipping summary.")
        with open(args.out, 'w', encoding='utf-8') as f_out:
            f_out.write("No tweets were found to summarize.")
        return

    if not tweets:
        print("[INFO] No tweets to summarize.")
        with open(args.out, 'w', encoding='utf-8') as f_out:
            f_out.write("No useful tweets were found to create a summary.")
        return
    
    print(f"[INFO] Summarizing all {len(tweets)} tweets from '{args.input_file}'.")
    full_text_content = "\n\n---\n\n".join([tweet['text'] for tweet in tweets])
    
    summary = get_ai_summary(full_text_content)
    
    with open(args.out, 'w', encoding='utf-8') as f_out:
        f_out.write(summary)
        
    print(f"[SUCCESS] Full Google AI summary saved to '{args.out}'.")

if __name__ == "__main__":
    main()