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


def check_server_running(url):
    try:
        with urllib.request.urlopen(url, timeout=1) as resp:
            return resp.status in (200, 404)
    except Exception:
        return False


def main():
    backend_proc = None
    frontend_proc = None

    if not check_server_running("http://127.0.0.1:8000/health"):
        print("[1/6] Starting FastAPI backend on port 8000...")
        backend_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "main:app", "--port", "8000"],
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    else:
        print("[1/6] FastAPI backend already running on port 8000.")

    if not check_server_running("http://localhost:5173"):
        print("[2/6] Starting Vite server on port 5173...")
        frontend_proc = subprocess.Popen(
            ["npx.cmd", "vite", "--port", "5173"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    else:
        print("[2/6] Vite frontend already running on port 5173.")

    try:
        if not wait_for_server("http://127.0.0.1:8000/health", timeout=15):
            print("ERROR: Backend failed to start on 8000")
            return 1

        if not wait_for_server("http://localhost:5173", timeout=15):
            print("ERROR: Frontend failed to start on 5173")
            return 1

        print("Both servers healthy! Launching Chromium via Playwright...")

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)

            # -----------------------------------------------------------------
            # TEST 1: Desktop 1440x900 - Overview & Setup Modal
            # -----------------------------------------------------------------
            print("[3/6] Testing Desktop 1440x900 Overview & Setup Modal...")
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            page.goto("http://localhost:5173/interview")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Check heading
            assert page.locator("h1", has_text="AI Mock Interview Simulator").is_visible(), "Heading not found"
            print("✓ Found 'AI Mock Interview Simulator' heading")

            # Verify disclaimer
            assert page.locator("text=Assessment Disclaimer:").is_visible(), "Disclaimer not found"
            print("✓ Transparency disclaimer is visible")

            shot_overview = os.path.join(ARTIFACT_DIR, "interview_desktop_1440_overview_dark.png")
            page.screenshot(path=shot_overview, full_page=True)
            print(f"✓ Saved screenshot: {shot_overview}")

            # Open Setup Modal
            start_btn = page.locator("button", has_text="Start New Interview").first
            start_btn.click()
            page.wait_for_timeout(600)

            modal_title = page.locator("#setup-modal-title")
            assert modal_title.is_visible(), "Setup modal failed to open"
            print("✓ Setup modal opened successfully")

            shot_modal = os.path.join(ARTIFACT_DIR, "interview_desktop_setup_modal.png")
            page.screenshot(path=shot_modal, full_page=True)
            print(f"✓ Saved screenshot: {shot_modal}")

            # -----------------------------------------------------------------
            # TEST 2: Start Session & Interactive Workspace
            # -----------------------------------------------------------------
            print("[4/6] Launching mock interview session...")
            launch_btn = page.locator("button[type='submit']", has_text="Launch Interview Session")
            launch_btn.click()
            page.wait_for_timeout(3500)

            # Check question workspace is visible
            assert page.locator("textarea#interview-answer-input").is_visible(), "Workspace textarea not found"
            print("✓ Workspace loaded with active question and textarea")

            shot_workspace = os.path.join(ARTIFACT_DIR, "interview_desktop_1440_workspace_dark.png")
            page.screenshot(path=shot_workspace, full_page=True)
            print(f"✓ Saved screenshot: {shot_workspace}")

            # -----------------------------------------------------------------
            # TEST 3: Submit Answer & Evaluate Deterministic Rubric
            # -----------------------------------------------------------------
            print("[5/6] Submitting answer and testing deterministic rubric evaluation...")
            # Type comprehensive answer into textarea
            answer_input = page.locator("textarea#interview-answer-input")
            answer_text = (
                "Stack memory is used for static allocation and stores primitive variables and function execution call frames in LIFO order. "
                "Stack allocation is extremely fast and managed automatically by the CPU, but limited in size, leading to stack overflow if recursion is unbounded. "
                "Heap memory is used for dynamic allocation where objects and reference types are created at runtime. "
                "It requires manual deallocation or garbage collection, and failure to free heap memory causes memory leaks."
            )
            answer_input.fill(answer_text)
            page.wait_for_timeout(500)

            # Submit Answer
            submit_btn = page.locator("button[type='submit']", has_text="Submit Answer")
            submit_btn.click()
            page.wait_for_timeout(2500)

            # Verify evaluation panel appeared
            assert page.locator("h4", has_text="Deterministic Rubric Performance").is_visible(), "Evaluation panel not visible"
            print("✓ Deterministic Rubric Performance panel rendered successfully")

            shot_eval = os.path.join(ARTIFACT_DIR, "interview_desktop_1440_evaluation_dark.png")
            page.screenshot(path=shot_eval, full_page=True)
            print(f"✓ Saved screenshot: {shot_eval}")

            # -----------------------------------------------------------------
            # TEST 4: Finish Interview & Review Final Report
            # -----------------------------------------------------------------
            print("[6/6] Progressing and finalizing interview to generate performance report...")
            # Complete the remaining questions quickly or click finalize
            while page.locator("button", has_text="Proceed to Next Question").is_visible():
                page.locator("button", has_text="Proceed to Next Question").click()
                page.wait_for_timeout(1000)
                if page.locator("textarea#interview-answer-input").is_visible():
                    page.locator("textarea#interview-answer-input").fill(
                        "Encapsulation, abstraction, inheritance, and polymorphism are the four pillars of object-oriented architecture."
                    )
                    page.locator("button[type='submit']", has_text="Submit Answer").click()
                    page.wait_for_timeout(2000)

            # Click Finish Interview button
            finish_btn = page.locator("button", has_text="Finish Interview & View Final Report")
            if finish_btn.is_visible():
                finish_btn.click()
                page.wait_for_timeout(3500)

            # Verify Report page
            assert page.locator("span", has_text="Official Interview Assessment Report").is_visible(), "Report header not found"
            print("✓ Final Interview Report generated and rendered")

            shot_report = os.path.join(ARTIFACT_DIR, "interview_desktop_1440_report_dark.png")
            page.screenshot(path=shot_report, full_page=True)
            print(f"✓ Saved screenshot: {shot_report}")

            # Test Light Theme
            page.evaluate("document.documentElement.setAttribute('data-theme', 'light'); document.documentElement.classList.remove('dark')")
            page.wait_for_timeout(600)
            shot_report_light = os.path.join(ARTIFACT_DIR, "interview_desktop_1440_report_light.png")
            page.screenshot(path=shot_report_light, full_page=True)
            print(f"✓ Saved light theme screenshot: {shot_report_light}")

            # Switch back to dark theme
            page.evaluate("document.documentElement.setAttribute('data-theme', 'dark'); document.documentElement.classList.add('dark')")

            # -----------------------------------------------------------------
            # Responsive Viewports: Tablet (768px), Mobile (425px, 375px)
            # -----------------------------------------------------------------
            print("Testing Tablet & Mobile Viewports...")
            # Tablet 768px
            page.set_viewport_size({"width": 768, "height": 1024})
            page.wait_for_timeout(500)
            overflow_tablet = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow_tablet, "Horizontal overflow detected on 768px Tablet"
            shot_tablet = os.path.join(ARTIFACT_DIR, "interview_tablet_768_dark.png")
            page.screenshot(path=shot_tablet, full_page=True)
            print(f"✓ Saved tablet screenshot: {shot_tablet}")

            # Mobile 425px
            page.set_viewport_size({"width": 425, "height": 850})
            page.wait_for_timeout(500)
            overflow_425 = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow_425, "Horizontal overflow detected on 425px Mobile"
            shot_425 = os.path.join(ARTIFACT_DIR, "interview_mobile_425_dark.png")
            page.screenshot(path=shot_425, full_page=True)
            print(f"✓ Saved mobile 425px screenshot: {shot_425}")

            # Mobile 375px
            page.set_viewport_size({"width": 375, "height": 812})
            page.wait_for_timeout(500)
            overflow_375 = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow_375, "Horizontal overflow detected on 375px Mobile"
            shot_375 = os.path.join(ARTIFACT_DIR, "interview_mobile_375_dark.png")
            page.screenshot(path=shot_375, full_page=True)
            print(f"✓ Saved mobile 375px screenshot: {shot_375}")

            browser.close()
            print("ALL PLAYWRIGHT AUTOMATION TESTS COMPLETED SUCCESSFULLY!")

    finally:
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()


if __name__ == "__main__":
    sys.exit(main() or 0)

