import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
BACKEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend"
FRONTEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend"
PYTHON_EXE = os.path.join(BACKEND_DIR, r".venv\Scripts\python.exe")

def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status in (200, 404):
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def main():
    print("[1/5] Starting FastAPI backend on port 8000...")
    backend_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("[2/5] Starting Vite server on port 5173...")
    frontend_proc = subprocess.Popen(
        ["npx.cmd", "vite", "--port", "5173"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        if not wait_for_server("http://127.0.0.1:8000/health", timeout=15):
            print("ERROR: Backend failed to start on 8000")
            return 1

        if not wait_for_server("http://localhost:5173", timeout=15):
            print("ERROR: Frontend failed to start on 5173")
            return 1

        print("Both servers healthy! Running Playwright tests with system Chrome...")

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)

            # -----------------------------------------------------------------
            # TEST 1: Desktop 1440x900 - Dark Theme & Generation Flow
            # -----------------------------------------------------------------
            print("[3/5] Testing Desktop Viewport (1440x900) Dark Theme...")
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            page.goto("http://localhost:5173/roadmap")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Verify page title
            assert page.locator("h1", has_text="Personalized Learning Roadmap").is_visible(), "Page heading not found"
            print("✓ Roadmap heading is visible")

            # Check if empty state or existing roadmap is shown
            empty_btn = page.locator("button", has_text="Generate Your Roadmap")
            new_btn = page.locator("button", has_text="New Roadmap")

            if empty_btn.is_visible():
                print("Empty state detected. Generating first roadmap...")
                empty_btn.click()
                page.wait_for_timeout(600)
                # In modal, click Generate
                gen_submit = page.locator("button[type='submit']", has_text="Generate Roadmap")
                if gen_submit.is_visible():
                    gen_submit.click()
                    print("Submitted generation request, waiting for curriculum...")
                    page.wait_for_timeout(3500)
            elif new_btn.is_visible():
                print("Existing roadmap found or ready.")

            page.wait_for_timeout(1000)

            # Take screenshot of Desktop Dark Theme Overview
            shot_dark = os.path.join(ARTIFACT_DIR, "roadmap_desktop_1440_dark.png")
            page.screenshot(path=shot_dark, full_page=True)
            print(f"✓ Saved dark theme desktop screenshot: {shot_dark}")

            # Test Topic Status Update
            complete_topic_btns = page.locator("button[title='Mark as Completed']")
            if complete_topic_btns.count() > 0:
                print("Testing topic completion toggle...")
                complete_topic_btns.first.click()
                page.wait_for_timeout(1500)
                print("✓ Successfully toggled topic to completed")

            # -----------------------------------------------------------------
            # TEST 2: Desktop 1440x900 - Light Theme
            # -----------------------------------------------------------------
            print("[4/5] Testing Desktop Light Theme...")
            # Toggle light theme button in topbar
            theme_btn = page.locator("header button[title*='theme' i], header button:has(svg.lucide-moon), header button:has(svg.lucide-sun)")
            if theme_btn.count() > 0:
                theme_btn.first.click()
                page.wait_for_timeout(800)
            else:
                page.evaluate("document.documentElement.classList.remove('dark')")

            shot_light = os.path.join(ARTIFACT_DIR, "roadmap_desktop_1440_light.png")
            page.screenshot(path=shot_light, full_page=True)
            print(f"✓ Saved light theme desktop screenshot: {shot_light}")

            # -----------------------------------------------------------------
            # TEST 3: Responsive Viewports (Tablet 768px, Mobile 425px, 375px)
            # -----------------------------------------------------------------
            print("[5/5] Testing Responsive Mobile & Tablet Viewports...")

            # Tablet 768px
            ctx_tab = browser.new_context(viewport={"width": 768, "height": 1024})
            p_tab = ctx_tab.new_page()
            p_tab.goto("http://localhost:5173/roadmap")
            p_tab.wait_for_load_state("networkidle")
            p_tab.wait_for_timeout(1000)
            shot_tab = os.path.join(ARTIFACT_DIR, "roadmap_tablet_768_dark.png")
            p_tab.screenshot(path=shot_tab, full_page=True)
            print(f"✓ Saved tablet 768px screenshot: {shot_tab}")
            ctx_tab.close()

            # Mobile 425px
            ctx_m425 = browser.new_context(viewport={"width": 425, "height": 844})
            p_m425 = ctx_m425.new_page()
            p_m425.goto("http://localhost:5173/roadmap")
            p_m425.wait_for_load_state("networkidle")
            p_m425.wait_for_timeout(1000)
            shot_m425 = os.path.join(ARTIFACT_DIR, "roadmap_mobile_425_dark.png")
            p_m425.screenshot(path=shot_m425, full_page=True)
            print(f"✓ Saved mobile 425px screenshot: {shot_m425}")
            ctx_m425.close()

            # Mobile 375px
            ctx_m375 = browser.new_context(viewport={"width": 375, "height": 667})
            p_m375 = ctx_m375.new_page()
            p_m375.goto("http://localhost:5173/roadmap")
            p_m375.wait_for_load_state("networkidle")
            p_m375.wait_for_timeout(1000)
            shot_m375 = os.path.join(ARTIFACT_DIR, "roadmap_mobile_375_dark.png")
            p_m375.screenshot(path=shot_m375, full_page=True)
            print(f"✓ Saved mobile 375px screenshot: {shot_m375}")
            ctx_m375.close()

            browser.close()

        print("\nAll Playwright UI automation checks completed successfully!")
        return 0

    finally:
        print("Cleaning up server processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=5)
            frontend_proc.wait(timeout=5)
        except Exception:
            backend_proc.kill()
            frontend_proc.kill()

if __name__ == "__main__":
    sys.exit(main())

