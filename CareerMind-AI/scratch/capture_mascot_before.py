import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
FRONTEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend"


def check_server(url):
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:
            return resp.status in (200, 404)
    except Exception:
        return False


def wait_for_server(url, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        if check_server(url):
            return True
        time.sleep(0.5)
    return False


def main():
    frontend_proc = None
    if not check_server("http://localhost:5173"):
        print("Starting Vite frontend on port 5173...")
        frontend_proc = subprocess.Popen(
            ["npx.cmd", "vite", "--port", "5173"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    try:
        if not wait_for_server("http://localhost:5173", timeout=15):
            print("ERROR: Frontend failed to start on 5173")
            return 1

        print("Frontend ready! Launching Chrome via Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)

            for theme in ["dark", "light"]:
                for width, height in [(375, 812), (425, 900)]:
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        device_scale_factor=2,
                    )
                    page = context.new_page()
                    page.goto("http://localhost:5173/")
                    page.wait_for_load_state("networkidle")

                    page.evaluate(f"""
                        localStorage.setItem('careermind-theme', '{theme}');
                        document.documentElement.setAttribute('data-theme', '{theme}');
                        if ('{theme}' === 'dark') {{
                            document.documentElement.classList.add('dark');
                        }} else {{
                            document.documentElement.classList.remove('dark');
                        }}
                    """)
                    page.reload()
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(600)

                    filename = f"mascot_before_mobile_{width}_{theme}.png"
                    filepath = os.path.join(ARTIFACT_DIR, filename)
                    page.screenshot(path=filepath, full_page=False)
                    print(f"Captured {filename}")

                    context.close()

            browser.close()
    finally:
        if frontend_proc:
            frontend_proc.terminate()


if __name__ == "__main__":
    main()
