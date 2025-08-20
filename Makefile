# Use uv for running all python commands
PYTHON = uv run

# Define the names of our scripts and generated files
SCRAPER_SCRIPT = main.py
FILTER_SCRIPT = filter_tweets.py
COOKIE_SCRIPT = get_cookies.py

RAW_OUTPUT = twikit_tweets.jsonl
FILTERED_OUTPUT = filtered_tweets.jsonl

# By declaring these as .PHONY, we tell Make that these are commands,
# not files to be built.
.PHONY: all run setup scrape filter clean help

# The default command, executed when you just type `make`
all: run

# The main command to run the full scrape and filter pipeline
run: scrape filter summarize
	@echo "\n✅ Full pipeline complete. Filtered results are in $(FILTERED_OUTPUT)"

# Command to perform the one-time cookie setup
setup:
	@echo "--- Running one-time cookie setup ---"
	@echo "A browser will open. Please log in to generate your .env file."
	$(PYTHON) $(COOKIE_SCRIPT)
	@echo "\n✅ Setup complete. You can now run 'make run'."

# Command to run only the scraper
scrape: $(SCRAPER_SCRIPT) .env
	@echo "--- Running the tweet scraper ---"
	$(PYTHON) $(SCRAPER_SCRIPT) --out $(RAW_OUTPUT)

# Command to run only the filter on existing raw data
filter: $(FILTER_SCRIPT) $(RAW_OUTPUT)
	@echo "--- Filtering raw tweets ---"
	$(PYTHON) $(FILTER_SCRIPT) $(RAW_OUTPUT) --out $(FILTERED_OUTPUT)

# Command to clean up all generated files
clean:
	@echo "--- Cleaning up generated files and caches ---"
	@rm -f $(RAW_OUTPUT) $(FILTERED_OUTPUT) temp_cookies.json .env
	@rm -rf __pycache__ cookie_gen_user_data .uv-venv
	@echo "Cleanup complete."
summarize:
	uv run summarizer.py
# A help command to explain the available targets
help:
	@echo "Available commands:"
	@echo "  make setup    - (Run once) Opens a browser to log in and create the .env file."
	@echo "  make          - Runs the default 'run' command."
	@echo "  make run      - Runs the full pipeline: scrapes tweets and then filters them."
	@echo "  make scrape   - Runs only the tweet scraper."
	@echo "  make filter   - Runs only the filter on the last scraped data."
	@echo "  make clean    - Deletes all generated files (.jsonl, .env, caches, .uv-venv)."
	@echo "  make help     - Shows this help message."
