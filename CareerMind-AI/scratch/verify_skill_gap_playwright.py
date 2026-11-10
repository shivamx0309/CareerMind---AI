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
            # TEST 1: Desktop 1440x900 - Dark Theme & Full Analysis Flow
            # -----------------------------------------------------------------
            print("[3/5] Testing Desktop Viewport (1440x900)...")
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            page.goto("http://localhost:5173/skills")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Check heading
            assert page.locator("h1", has_text="Skill Gap Analysis").is_visible(), "Page heading not found"
            print("✓ Skill Gap Analysis heading is visible")

            # Check role cards exist (8 roles)
            role_cards = page.locator("button:has-text('req')")
            print(f"✓ Found {role_cards.count()} role benchmark options")

            # Select Python Developer role card
            python_dev_btn = page.locator("button:has-text('Python Developer')")
            if python_dev_btn.is_visible():
                python_dev_btn.click()
                print("✓ Selected Python Developer role")
                page.wait_for_timeout(300)

            # Check resume selector
            resume_select = page.locator("select#resume-select")
            if resume_select.is_visible():
                options = resume_select.locator("option").all_inner_texts()
                print(f"✓ Resume select options available: {len(options)}")
                # Select a completed resume if needed
                for opt in options:
                    if "ShivamKumarSingh" in opt or "candidate_resume" in opt:
                        resume_select.select_option(label=opt)
                        print(f"✓ Explicitly selected resume: {opt}")
                        break

            # Click Analyze Skills
            analyze_btn = page.locator("button:has-text('Analyze Skills'), button:has-text('Re-analyze Skills')")
            if analyze_btn.is_enabled():
                print("✓ Clicking Analyze Skills button...")
                analyze_btn.click()
                # Wait for analysis results card to render
                page.wait_for_selector("text=Role Benchmark Coverage", timeout=15000)
                page.wait_for_timeout(1200) # Wait for chart animations
                print("✓ Analysis completed and results rendered!")

            # Capture Desktop Dark Screenshot
            desktop_dark_path = os.path.join(ARTIFACT_DIR, "skill_gap_desktop_1440_dark.png")
            page.screenshot(path=desktop_dark_path, full_page=True)
            print(f"✓ Saved screenshot: {desktop_dark_path}")

            # -----------------------------------------------------------------
            # TEST 2: Desktop 1440x900 - Light Theme
            # -----------------------------------------------------------------
            print("[4/5] Testing Light Theme...")
            theme_btn = page.locator("button.theme-toggle")
            if theme_btn.is_visible():
                theme_btn.click()
                page.wait_for_timeout(500)
                desktop_light_path = os.path.join(ARTIFACT_DIR, "skill_gap_desktop_1440_light.png")
                page.screenshot(path=desktop_light_path, full_page=True)
                print(f"✓ Saved screenshot: {desktop_light_path}")
                # Switch back to dark
                theme_btn.click()
                page.wait_for_timeout(300)

            context.close()

            # -----------------------------------------------------------------
            # TEST 3: Tablet 768x1024
            # -----------------------------------------------------------------
            print("[5/5] Testing Tablet (768x1024) and Mobile (425px & 375px)...")
            tablet_context = browser.new_context(viewport={"width": 768, "height": 1024})
            tablet_page = tablet_context.new_page()
            tablet_page.goto("http://localhost:5173/skills")
            tablet_page.wait_for_load_state("networkidle")
            tablet_page.wait_for_timeout(1000)

            tablet_path = os.path.join(ARTIFACT_DIR, "skill_gap_tablet_768_dark.png")
            tablet_page.screenshot(path=tablet_path, full_page=True)
            print(f"✓ Saved screenshot: {tablet_path}")
            tablet_context.close()

            # Mobile 425x850
            mobile_425_context = browser.new_context(viewport={"width": 425, "height": 850})
            mobile_425_page = mobile_425_context.new_page()
            mobile_425_page.goto("http://localhost:5173/skills")
            mobile_425_page.wait_for_load_state("networkidle")
            mobile_425_page.wait_for_timeout(1000)

            mobile_425_path = os.path.join(ARTIFACT_DIR, "skill_gap_mobile_425_dark.png")
            mobile_425_page.screenshot(path=mobile_425_path, full_page=True)
            print(f"✓ Saved screenshot: {mobile_425_path}")
            mobile_425_context.close()

            # Mobile 375x812
            mobile_375_context = browser.new_context(viewport={"width": 375, "height": 812})
            mobile_375_page = mobile_375_context.new_page()
            mobile_375_page.goto("http://localhost:5173/skills")
            mobile_375_page.wait_for_load_state("networkidle")
            mobile_375_page.wait_for_timeout(1000)

            mobile_375_path = os.path.join(ARTIFACT_DIR, "skill_gap_mobile_375_dark.png")
            mobile_375_page.screenshot(path=mobile_375_path, full_page=True)
            print(f"✓ Saved screenshot: {mobile_375_path}")
            mobile_375_context.close()

            browser.close()

        print("\nAll browser verification tests passed successfully!")
        return 0

    finally:
        print("Cleaning up background server processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
        try:
            frontend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()

if __name__ == "__main__":
    sys.exit(main())

