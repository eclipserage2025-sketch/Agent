import subprocess
import time
from playwright.sync_api import sync_playwright

def test_frontend():
    # Start the server in the background
    server_process = subprocess.Popen(["python3", "gui.py"])
    time.sleep(5) # Wait for server to start and load assets

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://127.0.0.1:5000")

            # Check for Pro Miner React text
            print(f"Page content check...")
            assert page.is_visible("text=Pro Miner")
            assert page.is_visible("text=Hashrate")
            assert page.is_visible("text=AI Learning Log")

            # Take a screenshot
            page.screenshot(path="frontend_pro_miner_react.png")
            print("Screenshot saved to frontend_pro_miner_react.png")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    test_frontend()
