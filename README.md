# AI-Powered Cybersecurity Intelligence Feed

This project is an end-to-end data pipeline that automates the process of gathering, filtering, and summarizing high-value cybersecurity and Web3 intelligence from X (formerly Twitter). It uses a sophisticated, human-like scraping mechanism, a rule-based content filter, and Google's Gemini 1.5 Flash model to produce a concise, actionable intelligence briefing.

The final output is a clean, self-contained HTML file that displays the AI-generated summary alongside the curated list of relevant tweets.

> **Disclaimer:** This script is intended for educational purposes to demonstrate a full data pipeline, including advanced scraping techniques and AI integration. Scraping data from X is against their Terms of Service and may result in your account being suspended or banned. Use this script at your own risk. The author is not responsible for any consequences of its use.

## Core Features

-   **Human-Like Automated Scraping**: Implements advanced techniques to mimic human behavior, reducing the likelihood of being flagged as a bot. This includes:
    -   Dynamic session management with variable activity levels based on the time of day.
    -   Randomized delays, "distractions," and breaks between actions.
    -   Rotation of browser `User-Agent` strings.
    -   Exponential backoff for handling rate limits gracefully.
-   **Intelligent Content Filtering**: A custom Python script scores and filters tweets using a sophisticated set of weighted keywords, noise penalties, and disqualifying phrases to isolate high-value intelligence from market speculation and spam.
-   **Advanced AI Summarization**: Leverages Google's Gemini 1.5 Flash model to analyze the filtered tweets and generate a high-level intelligence briefing. The AI is prompted to act as a senior analyst with dual expertise in traditional cybersecurity and Web3 security.
-   **Secure Credential Management**: Uses Playwright for a one-time, user-interactive login to securely generate an `.env` file with the necessary authentication tokens, which are never hard-coded.
-   **Simple Command-Line Interface**: A `Makefile` provides an easy-to-use interface for managing the entire workflow, from initial setup to running the full pipeline and cleaning up generated files.
-   **Clean Web Viewer**: A self-contained `viewer.html` file presents the final report in a clean, readable format, dynamically loading and rendering the AI summary and filtered tweets.

## How It Works

The project runs in a simple, multi-step pipeline orchestrated by the `Makefile`:

1.  **Setup (`make setup`)**: This one-time command launches a browser window using Playwright. You log in to your X account, and the script automatically extracts the `auth_token` and `ct0` cookies, saving them to a local `.env` file for all future runs.
2.  **Scrape (`make scrape`)**: The `main.py` script initiates the scraping process. It creates sessions with human-like characteristics, searches for a randomized list of keywords, and saves the raw output to `twikit_tweets.jsonl`. At the start of each run, the previous raw tweet file is deleted to ensure a fresh dataset.
3.  **Filter (`make filter`)**: The `filter_tweets.py` script processes the raw tweets. It assigns a score to each tweet based on the keyword scoring engine and removes any that don't meet the quality threshold. The high-value tweets are saved to `filtered_tweets.jsonl`.
4.  **Summarize (`make summarize`)**: The `summarizer.py` script takes the filtered tweets, sends them to the Google Generative AI API with a specialized prompt, and saves the resulting markdown-formatted summary to `summary.txt`.
5.  **Run (`make run`)**: This default command executes the full `scrape` -> `filter` -> `summarize` pipeline in the correct order.

## Requirements

-   Python (version 3.13 or newer)
-   `uv`: An extremely fast Python package installer.
-   An X (Twitter) Account.
-   A Google AI API Key (for the summarization feature).

## Setup and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/cosminmarian53/X-Scout
cd X-Scout

### 2. Install Dependencies

This project uses `uv` for fast and efficient package management. The dependencies are listed in `pyproject.toml`.

```bash
# This will create a virtual environment and install all required packages
uv sync
```

### 3. Create your Google AI API Key

-   Go to the [Google AI Studio](https://aistudio.google.com/app/apikey).
-   Create a new API key and copy it.
-   Create a new file named `.env` in the project root and add your API key like this:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Generate X Authentication Cookies

Run the `setup` command. This will open a browser window where you need to log in to your X account.

```bash
make setup
```

After you log in, the script will automatically create/update your `.env` file with the necessary `TWITTER_AUTH_TOKEN` and `TWITTER_CT0`.

### 5. Run the Pipeline

Execute the main command to run the full data pipeline.

```bash
make run
```

After the process completes, you will have two key output files:
-   `filtered_tweets.jsonl`: The curated list of high-value tweets.
-   `summary.txt`: The AI-generated intelligence briefing.

You can open `viewer.html` in your browser to see a formatted presentation of these results.

## Project Structure

```
.
├── Makefile              # Automates all project tasks (run, setup, clean).
├── README.md             # This file.
├── get_cookies.py        # Script for securely generating auth tokens.
├── main.py               # Main scraping script with human-like behavior.
├── filter_tweets.py      # Scores and filters raw tweets.
├── summarizer.py         # Generates the AI summary from filtered tweets.
├── session_manager.py    # Class to simulate human-like session patterns.
├── viewer.html           # Local webpage to display the final results.
├── pyproject.toml        # Project metadata and dependencies for uv.
├── .gitignore            # Ensures sensitive files and caches are not committed.
├── .env                  # (Generated) Stores your secret API keys and tokens.
├── twikit_tweets.jsonl   # (Generated) Raw scraped tweets.
├── filtered_tweets.jsonl # (Generated) Filtered, high-value tweets.
└── summary.txt           # (Generated) The final AI-generated summary.
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.


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
git clone https://github.com/cosminmarian53/X-Scout
cd X-Scout
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
