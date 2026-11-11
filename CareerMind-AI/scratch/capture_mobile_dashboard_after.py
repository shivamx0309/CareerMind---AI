import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
FRONTEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend"
BACKEND_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend"
PYTHON_EXE = os.path.join(BACKEND_DIR, r".venv\Scripts\python.exe")


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
    backend_proc = None
    frontend_proc = None

    if not check_server("http://127.0.0.1:8000/health"):
        backend_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "main:app", "--port", "8000"],
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    if not check_server("http://localhost:5173"):
        frontend_proc = subprocess.Popen(
            ["npx.cmd", "vite", "--port", "5173"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    try:
        wait_for_server("http://127.0.0.1:8000/health", timeout=15)
        wait_for_server("http://localhost:5173", timeout=15)

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)

            for width in [425, 375]:
                for theme in ["light", "dark"]:
                    context = browser.new_context(viewport={"width": width, "height": 900}, device_scale_factor=2)
                    page = context.new_page()
                    page.goto("http://localhost:5173/dashboard")
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
                    page.wait_for_timeout(800)

                    # Shot 1: Career Overview in full view
                    overview_el = page.locator("h2:has-text('Career Overview')").first
                    if overview_el.is_visible():
                        overview_el.scroll_into_view_if_needed()
                        page.wait_for_timeout(400)

                    filename_overview = f"mobile_dashboard_after_{width}_{theme}.png"
                    page.screenshot(path=os.path.join(ARTIFACT_DIR, filename_overview), full_page=False)
                    print(f"Captured {filename_overview}")

                    # Shot 2: Quick Actions & Your Next Steps horizontal timeline
                    page.evaluate("""() => {
                        const nextSteps = document.querySelector('.mobile-timeline-card');
                        if (nextSteps) {
                            nextSteps.scrollIntoView({ block: 'center' });
                        } else {
                            window.scrollTo(0, document.body.scrollHeight);
                        }
                    }""")
                    page.wait_for_timeout(500)

                    filename_actions = f"mobile_dashboard_after_{width}_{theme}_actions.png"
                    page.screenshot(path=os.path.join(ARTIFACT_DIR, filename_actions), full_page=False)
                    print(f"Captured {filename_actions}")

                    scroll_w = page.evaluate("document.documentElement.scrollWidth")
                    client_w = page.evaluate("document.documentElement.clientWidth")
                    print(f"Width {width} ({theme}): scrollWidth={scroll_w}, clientWidth={client_w}")

                    context.close()

            # Verify Desktop 1440 remains untouched
            context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
            page = context.new_page()
            page.goto("http://localhost:5173/dashboard")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "dashboard_desktop_verification.png"), full_page=False)
            print("Captured dashboard_desktop_verification.png")
            context.close()

            browser.close()
    finally:
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()


if __name__ == "__main__":
    main()
