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
        print("Starting FastAPI backend...")
        backend_proc = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "main:app", "--port", "8000"],
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    if not check_server("http://localhost:5173"):
        print("Starting Vite frontend...")
        frontend_proc = subprocess.Popen(
            ["npx.cmd", "vite", "--port", "5173"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    try:
        wait_for_server("http://127.0.0.1:8000/health", timeout=15)
        wait_for_server("http://localhost:5173", timeout=15)

        print("Servers ready! Launching Chrome via Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)

            for theme in ["light", "dark"]:
                # 1. Desktop 1440x900
                context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
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

                # Hero banner screenshot
                banner = page.locator(".welcome-banner")
                if banner.is_visible():
                    box = banner.bounding_box()
                    banner_file = f"dashboard_hero_desktop_1440_{theme}.png"
                    page.screenshot(path=os.path.join(ARTIFACT_DIR, banner_file), clip=box)
                    print(f"Captured {banner_file}")

                # Full page
                page_file = f"dashboard_desktop_1440_{theme}.png"
                page.screenshot(path=os.path.join(ARTIFACT_DIR, page_file), full_page=False)
                print(f"Captured {page_file}")

                context.close()

                # 2. Tablet 768x1024
                context = browser.new_context(viewport={"width": 768, "height": 1024}, device_scale_factor=2)
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

                banner = page.locator(".welcome-banner")
                if banner.is_visible():
                    box = banner.bounding_box()
                    banner_file = f"dashboard_hero_tablet_768_{theme}.png"
                    page.screenshot(path=os.path.join(ARTIFACT_DIR, banner_file), clip=box)
                    print(f"Captured {banner_file}")
                context.close()

                # 3. Mobile 375x812
                context = browser.new_context(viewport={"width": 375, "height": 812}, device_scale_factor=2)
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

                banner = page.locator(".welcome-banner")
                if banner.is_visible():
                    box = banner.bounding_box()
                    banner_file = f"dashboard_hero_mobile_375_{theme}.png"
                    page.screenshot(path=os.path.join(ARTIFACT_DIR, banner_file), clip=box)
                    print(f"Captured {banner_file}")
                context.close()

            browser.close()
    finally:
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()


if __name__ == "__main__":
    main()

