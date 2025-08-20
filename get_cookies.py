import asyncio
from playwright.async_api import async_playwright

USER_DATA_DIR = "./cookie_gen_user_data"
ENV_FILE = ".env"

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False
        )
        page = await context.new_page()

        print("[INFO] Opening browser to log in...")
        await page.goto("https://x.com/home")

        if "login" in page.url:
            print("\n" + "="*50)
            print(">>> LOGIN REQUIRED <<<")
            print("Please log in to your Twitter/X account in the browser window.")
            print("The script will automatically detect the cookies once you are logged in.")
            print("="*50 + "\n")
            await page.wait_for_url("https://x.com/home", timeout=300000)

        print("[INFO] Login successful. Extracting cookies...")
        
        cookies = await context.cookies()
        auth_token = None
        ct0 = None

        for cookie in cookies:
            if cookie['name'] == 'auth_token':
                auth_token = cookie['value']
            if cookie['name'] == 'ct0':
                ct0 = cookie['value']

        await context.close()

        if auth_token and ct0:
            with open(ENV_FILE, "w") as f:
                f.write(f"TWITTER_AUTH_TOKEN={auth_token}\n")
                f.write(f"TWITTER_CT0={ct0}\n")
            print(f"[SUCCESS] Cookies saved to {ENV_FILE}. You can now run the main scraper script.")
        else:
            print("[ERROR] Could not find auth_token or ct0. Please try running the script again.")

if __name__ == "__main__":
    asyncio.run(main())