import subprocess
import time
from playwright.sync_api import sync_playwright

def test_frontend():
    # Start the server in the background
    server_process = subprocess.Popen(["python3", "gui.py"])
    time.sleep(3) # Wait for server to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://127.0.0.1:5000")

            # Check title
            print(f"Page title: {page.title()}")
            assert "AI Monero Miner GUI V4" in page.title()

            # Verify specific Monero elements
            assert page.is_visible("text=RandomX")
            assert page.is_visible("text=CPU Temp")
            assert page.is_visible("text=Monero Address")

            # Take a screenshot
            page.screenshot(path="frontend_monero.png")
            print("Screenshot saved to frontend_monero.png")

            browser.close()
    finally:
        server_process.terminate()

if __name__ == "__main__":
    test_frontend()
