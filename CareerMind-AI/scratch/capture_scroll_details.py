import os
import subprocess
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
BACKEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend"
FRONTEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend"
PYTHON_EXE = os.path.join(BACKEND_DIR, r".venv\Scripts\python.exe")

backend = subprocess.Popen([PYTHON_EXE, "-m", "uvicorn", "main:app", "--port", "8000"], cwd=BACKEND_DIR)
frontend = subprocess.Popen(["npx.cmd", "vite", "--port", "5173"], cwd=FRONTEND_DIR)

time.sleep(3)

try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        page = b.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://localhost:5173/skills")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Scroll to Results & Panels
        matched_panel = page.locator("h3:has-text('Matched Skills')")
        if matched_panel.is_visible():
            matched_panel.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "skill_gap_desktop_matched_and_related.png"))

        # Scroll to Chart & History
        chart_panel = page.locator("h3:has-text('Category-wise Competency Breakdown')")
        if chart_panel.is_visible():
            chart_panel.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "skill_gap_desktop_chart_and_history.png"))

        b.close()
        print("Detailed screenshots captured successfully!")
finally:
    backend.terminate()
    frontend.terminate()

