import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_light_mode_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://localhost:5173/#features")
        page.wait_for_load_state("networkidle")

        page.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)

        page.locator("#features").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        next_btn = page.locator('button[aria-label="Next feature"]')

        # Advance to Card 4
        next_btn.click()
        page.wait_for_timeout(400)
        next_btn.click()
        page.wait_for_timeout(400)
        next_btn.click()
        page.wait_for_timeout(400)

        shot_card4_light = os.path.join(ARTIFACT_DIR, "features_card04_light_centered.png")
        page.screenshot(path=shot_card4_light, full_page=False)
        print("Captured Light Mode Card 04:", shot_card4_light)

        # Advance to Card 5
        next_btn.click()
        page.wait_for_timeout(400)
        shot_card5_light = os.path.join(ARTIFACT_DIR, "features_card05_light_centered.png")
        page.screenshot(path=shot_card5_light, full_page=False)
        print("Captured Light Mode Card 05:", shot_card5_light)

        browser.close()

if __name__ == "__main__":
    run_light_mode_tests()

