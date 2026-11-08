"""
Verify onboarding page scrolling behavior across desktop and small viewports.
"""

import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

BACKEND_DIR = r"c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend"
FRONTEND_DIR = r"c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend"
PYTHON_EXE = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")

print("Starting backend and frontend...")
backend_proc = subprocess.Popen(
    [PYTHON_EXE, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=BACKEND_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
frontend_proc = subprocess.Popen(
    ["npx.cmd", "vite", "--port", "5173", "--host", "127.0.0.1"],
    cwd=FRONTEND_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

for _ in range(25):
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=1)
        urllib.request.urlopen("http://127.0.0.1:5173/", timeout=1)
        break
    except Exception:
        time.sleep(1)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        # Test Viewport 1: Standard Laptop (1280x720)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        page.goto("http://127.0.0.1:5173/onboarding?edit=true", wait_until="networkidle")
        time.sleep(1)

        scroll_info = page.evaluate("""() => {
            const container = document.querySelector('.onboarding-page-container') || document.documentElement;
            return {
                scrollHeight: container.scrollHeight,
                clientHeight: container.clientHeight,
                canScroll: container.scrollHeight > container.clientHeight,
                initialScrollTop: container.scrollTop
            };
        }""")
        print("[Laptop Viewport 1280x720] Initial scroll info:", scroll_info)
        assert scroll_info["canScroll"], f"Container should be scrollable! {scroll_info}"

        # Scroll down to bottom
        page.evaluate("() => { const c = document.querySelector('.onboarding-page-container'); c.scrollTop = 500; }")
        time.sleep(0.5)

        after_scroll = page.evaluate("() => document.querySelector('.onboarding-page-container').scrollTop")
        print("[Laptop Viewport 1280x720] ScrollTop after scrolling:", after_scroll)
        assert after_scroll > 0, "Page should scroll down successfully!"

        # Verify submit button is reachable
        submit_btn = page.locator("button[type='submit']")
        submit_btn.scroll_into_view_if_needed()
        assert submit_btn.is_visible(), "Submit button must be visible after scrolling into view!"
        print("  ✓ Desktop/Laptop scrolling works perfectly!")

        # Test Viewport 2: Mobile (390x844)
        m_context = browser.new_context(viewport={"width": 390, "height": 844})
        m_page = m_context.new_page()
        m_page.goto("http://127.0.0.1:5173/onboarding?edit=true", wait_until="networkidle")
        time.sleep(1)

        m_scroll_info = m_page.evaluate("""() => {
            const container = document.querySelector('.onboarding-page-container');
            return {
                scrollHeight: container.scrollHeight,
                clientHeight: container.clientHeight,
                canScroll: container.scrollHeight > container.clientHeight
            };
        }""")
        print("[Mobile Viewport 390x844] Scroll info:", m_scroll_info)
        assert m_scroll_info["canScroll"], "Mobile view must be scrollable!"

        m_page.evaluate("() => { const c = document.querySelector('.onboarding-page-container'); c.scrollTop = 600; }")
        time.sleep(0.5)
        m_after_scroll = m_page.evaluate("() => document.querySelector('.onboarding-page-container').scrollTop")
        print("[Mobile Viewport 390x844] ScrollTop after scrolling:", m_after_scroll)
        assert m_after_scroll > 0, "Mobile page must scroll down!"
        print("  ✓ Mobile viewport scrolling works perfectly!")

        browser.close()
        print("\n*** ALL SCROLL VERIFICATIONS PASSED 100%! ***\n")

finally:
    backend_proc.terminate()
    frontend_proc.terminate()

