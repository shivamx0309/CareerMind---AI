import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context(viewport={"width": 375, "height": 667}, device_scale_factor=2)
    page = context.new_page()
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    # Scroll .landing-page-container to bottom
    page.evaluate("document.querySelector('.landing-page-container').scrollTop = 999999;")
    page.wait_for_timeout(800)

    shot = os.path.join(ARTIFACT_DIR, "final_cta_current_mobile.png")
    page.screenshot(path=shot, full_page=False)
    print("Screenshot saved to:", shot)
    browser.close()
