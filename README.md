# AI-Powered Cybersecurity Intelligence Feed

This project automates the process of gathering, filtering, and summarizing high-value cybersecurity intelligence from Twitter/X. It uses a custom scraping script, a rule-based filter, and Google's Generative AI (Gemini) to produce a concise, actionable briefing that covers both traditional and Web3/blockchain security.

The final output is a clean, local web page displaying the AI-generated summary alongside the curated list of tweets.

## Features

- **Automated Twitter Scraping**: Fetches the latest tweets from a curated list of cybersecurity-focused accounts using `twikit`.
- **Intelligent Content Filtering**: A custom Python script scores and filters tweets based on keywords, removing low-value content like ads, job postings, and hype.
- **Advanced AI Summarization**: Uses Google's Gemini 1.5 Flash model to analyze the filtered tweets and generate a high-level intelligence briefing.
- **Dual-Domain Expertise**: The AI is specifically prompted to act as a senior analyst with expertise in both traditional cybersecurity (vulnerabilities, exploits, threat actors) and Web3 security (smart contracts, blockchain exploits, FHE).
- **Critical AI Filtering**: As a final safeguard, the AI is instructed to critically evaluate the provided tweets and discard any remaining marketing or irrelevant content before creating its summary.
- **Simple Command-Line Interface**: A `Makefile` provides easy-to-use commands (`make view`, `make setup`, `make clean`) to manage the entire workflow.
- **Clean Web Viewer**: A self-contained `viewer.html` file presents the final report in a clean, readable format, correctly parsing the AI's markdown for display.

## How It Works

The project runs in a simple, three-step pipeline orchestrated by the `Makefile`:

1.  **Scrape (`make scrape`)**: The `twikit_scraper.py` script logs into Twitter using your credentials and scrapes the latest tweets from the accounts listed within the script. The raw output is saved to `twikit_tweets.jsonl`.
2.  **Filter (`make filter`)**: The `filter_tweets.py` script processes the raw tweets. It assigns a score to each tweet based on a weighted list of keywords and filters out those that don't meet a minimum threshold. The high-value tweets are saved to `filtered_tweets.jsonl`.
3.  **Summarize (`make summarize`)**: The `summarizer.py` script takes all the filtered tweets, sends them to the Google Generative AI API with a specialized prompt, and saves the resulting markdown-formatted summary to `summary.txt`.
4.  **View (`make view`)**: This command runs the full `scrape -> filter -> summarize` pipeline and then opens `viewer.html` in your browser, which dynamically loads and displays the content from `summary.txt` and `filtered_tweets.jsonl`.

## Requirements

- **Python** (version 3.8 or newer)
- **`uv`**: An extremely fast Python package installer.
- A **Twitter/X Account** (for scraping).
- A **Google AI API Key** (for summarization).

## Setup Instructions

Follow these steps to get the project running.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-name>
```

### 2. Install System Dependencies

You need Python and `uv`. If you have Python, you can install `uv` with `pip`:

```bash
pip install uv
```
Alternatively, see the official [uv installation guide](https://github.com/astral-sh/uv#installation).

### 3. Run the Automated Setup

The `setup` command installs Python libraries and generates your Twitter authentication cookies.

```bash
make setup
```

A browser window will open, asking you to log in to Twitter/X. After you log in, the script will automatically save your authentication cookies to a `temp_cookies.json` file and then create the `.env` file for you.

### 4. Add Your Google API Key

The setup process creates a `.env` file for you. You now need to edit it to add your Google API key.

1.  Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Open the `.env` file in your editor. It will look like this:

    ```dotenv
    TWITTER_AUTH_TOKEN="your_auth_token_from_setup"
    TWITTER_CT0="your_ct0_token_from_setup"
    
    # Add your Google API Key below
    GOOGLE_API_KEY=""
    ```

3.  Paste your Google API key into the `GOOGLE_API_KEY` field.

    ```dotenv
    # Add your Google API Key below
    GOOGLE_API_KEY="your_google_api_key_here"
    ```

You are now ready to run the project!

## Usage

All commands are run from the terminal using `make`.

- **Run the pipeline without opening the browser**:
  ```bash
  make run
  ```
  The results will be available in `summary.txt` and `filtered_tweets.jsonl`.

- **Clean up all generated files**:
  ```bash
  make clean
  ```
  This removes all `.jsonl` files, `summary.txt`, the `.env` file, and the Python virtual environment.

- **See all available commands**:
  ```bash
  make help
  ```

## File Structure

```
.
├── Makefile              # The command center for the project
├── README.md             # This file
├── filter_tweets.py      # Script to filter raw tweets
├── get_cookies.py        # Script to handle initial Twitter auth setup
├── summarizer.py         # Script to generate the AI summary
├── twikit_scraper.py     # Script to scrape tweets
└── viewer.html           # The local webpage for displaying results
```