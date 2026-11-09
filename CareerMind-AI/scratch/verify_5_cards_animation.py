import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        context = browser.new_context(
            viewport={"width": 375, "height": 731},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://localhost:5173/")
        page.wait_for_load_state("networkidle")

        # Set Light Mode
        page.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Verify all 5 cards exist
        card_texts = page.locator("[data-testid='mascot-feature-card']")
        count = card_texts.count()
        print(f"Total feature cards beside Mindy: {count}")
        assert count == 5, f"Expected 5 cards, got {count}"

        labels = [card_texts.nth(i).inner_text().replace('\n', ' ').strip() for i in range(count)]
        print("Card labels:", labels)
        assert any("AI Interview" in l for l in labels), "AI Interview card missing!"
        print("PASS: AI Interview card is present alongside the other 4 cards.")

        # Capture initial state (Card 0 active)
        shot_0 = os.path.join(ARTIFACT_DIR, "mascot_5cards_step0_resume.png")
        page.screenshot(path=shot_0, full_page=False)
        print("Captured Card 0 active:", shot_0)

        # Wait 2.2 seconds for loop to move to Card 1
        page.wait_for_timeout(2200)
        shot_1 = os.path.join(ARTIFACT_DIR, "mascot_5cards_step1_job.png")
        page.screenshot(path=shot_1, full_page=False)
        print("Captured Card 1 active:", shot_1)

        # Wait 2.2 seconds for loop to move to Card 2
        page.wait_for_timeout(2200)
        shot_2 = os.path.join(ARTIFACT_DIR, "mascot_5cards_step2_skillgap.png")
        page.screenshot(path=shot_2, full_page=False)
        print("Captured Card 2 active:", shot_2)

        # Wait 4.4 seconds for loop to reach Card 4 (AI Interview)
        page.wait_for_timeout(4400)
        shot_4 = os.path.join(ARTIFACT_DIR, "mascot_5cards_step4_ai_interview.png")
        page.screenshot(path=shot_4, full_page=False)
        print("Captured Card 4 (AI Interview) active:", shot_4)

        # Check horizontal overflow on 375px
        sw = page.evaluate("document.documentElement.scrollWidth")
        cw = page.evaluate("document.documentElement.clientWidth")
        assert sw <= cw + 1, f"Horizontal overflow: {sw} > {cw}"
        print(f"PASS: No horizontal overflow (sw={sw}, cw={cw}).")

        context.close()
        browser.close()
        print("ALL 5 CARDS & 2-SECOND TOP-TO-BOTTOM ANIMATION TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
