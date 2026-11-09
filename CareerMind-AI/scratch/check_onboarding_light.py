import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
    page = context.new_page()
    page.goto("http://localhost:5173/onboarding?edit=true")
    page.wait_for_load_state("networkidle")

    # Set light theme
    page.evaluate("""
        localStorage.setItem('careermind-theme', 'light');
        document.documentElement.setAttribute('data-theme', 'light');
        document.documentElement.classList.remove('dark');
    """)
    page.reload()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(600)

    shot = os.path.join(ARTIFACT_DIR, "onboarding_restored_clean_light.png")
    page.screenshot(path=shot, full_page=False)
    print("Screenshot saved to:", shot)
    browser.close()

