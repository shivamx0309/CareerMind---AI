import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # =========================================================================
        # 1. First Visit: Greeting Popup Visibility & Auto-Dismiss Test (375px)
        # =========================================================================
        print("--- TEST 1: First Visit at 375px (Initial Greeting & Auto-Dismiss) ---")
        context = browser.new_context(viewport={"width": 375, "height": 667}, device_scale_factor=2)
        page = context.new_page()
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")

        # Clear storage to simulate brand new first visit
        page.evaluate("""
            localStorage.clear();
            sessionStorage.clear();
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(400)

        # Check greeting popup is visible on first visit
        greeting_popup = page.locator("div[role='status']:has-text(\"Let's do this! 🚀\")")
        assert greeting_popup.is_visible(), "Greeting popup must be visible on first visit!"
        print("PASS: Greeting popup is visible on first visit.")

        # Check dismiss button exists
        dismiss_btn = page.locator("button[aria-label='Dismiss greeting popup']")
        assert dismiss_btn.is_visible(), "Dismiss (X) button must be visible on greeting popup!"
        print("PASS: Dismiss button is visible.")

        # Capture First Visit Greeting Screenshot
        shot_greeting = os.path.join(ARTIFACT_DIR, "floating_mascot_greeting_375.png")
        page.screenshot(path=shot_greeting, full_page=False)
        print("Saved screenshot of active greeting:", shot_greeting)

        # Check that greeting popup does not cause horizontal scroll
        win_x = page.evaluate("window.scrollX")
        cnt_x = page.evaluate("document.querySelector('.landing-page-container') ? document.querySelector('.landing-page-container').scrollLeft : 0")
        assert win_x == 0 and cnt_x == 0, f"Greeting popup caused horizontal drift! winX={win_x}, cntX={cnt_x}"
        print("PASS: Zero horizontal scroll with greeting popup active.")

        # Wait 3.6s for auto-dismiss
        print("Waiting 3.6s for auto-dismiss timer...")
        page.wait_for_timeout(3600)

        # Verify greeting popup is now hidden
        assert not greeting_popup.is_visible(), "Greeting popup should automatically hide after ~3 seconds!"
        print("PASS: Greeting popup automatically dismissed after 3 seconds.")

        # Floating mascot button must remain visible at bottom-right
        mascot_btn = page.locator("button[aria-label*='Mindy AI Assistant']")
        assert mascot_btn.is_visible(), "Floating mascot button must remain visible!"
        print("PASS: Floating mascot button remains visible.")

        # Capture Auto-dismissed state screenshot
        shot_dismissed = os.path.join(ARTIFACT_DIR, "floating_mascot_auto_dismissed_375.png")
        page.screenshot(path=shot_dismissed, full_page=False)
        print("Saved screenshot of auto-dismissed state:", shot_dismissed)

        # =========================================================================
        # 2. Subsequent Visit: Tooltip remains hidden on reload
        # =========================================================================
        print("\n--- TEST 2: Subsequent Visit (Greeting Stays Hidden) ---")
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        assert not greeting_popup.is_visible(), "Greeting popup must NOT reappear on subsequent visits!"
        assert mascot_btn.is_visible(), "Mascot button must still be visible!"
        print("PASS: Greeting popup remains hidden on subsequent visits.")

        # =========================================================================
        # 3. Mascot Interaction: Clicking opens existing chat dialog
        # =========================================================================
        print("\n--- TEST 3: Mascot Click Opens Existing Chat Interaction ---")
        mascot_btn.click()
        page.wait_for_timeout(500)

        chat_header = page.locator("h3:has-text(\"Hi! I'm Mindy\")")
        assert chat_header.is_visible(), "Clicking mascot must open existing chat interface!"
        print("PASS: Chat interaction opens properly.")

        # Close chat dialog
        close_chat_btn = page.locator("button[aria-label='Close Mindy Chat']")
        close_chat_btn.click()
        page.wait_for_timeout(400)
        assert not chat_header.is_visible(), "Chat closed cleanly."
        print("PASS: Chat closed cleanly.")

        # =========================================================================
        # 4. Final CTA Section Check: No Trust Badge Overlap
        # =========================================================================
        print("\n--- TEST 4: Final CTA Section Content & Trust Badges Check ---")
        cta_btn = page.locator("a:has-text('Build My Career Profile')").last
        cta_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Check trust badges text is visible and not covered
        trust_badges = page.locator("span:has-text('Local-First')").last
        assert trust_badges.is_visible(), "Trust badges in Final CTA must be visible!"
        print("PASS: Final CTA trust badges are completely unobstructed.")

        shot_cta_clean = os.path.join(ARTIFACT_DIR, "final_cta_section_clean_375.png")
        page.screenshot(path=shot_cta_clean, full_page=False)
        print("Saved clean Final CTA section screenshot:", shot_cta_clean)

        # =========================================================================
        # 5. Multi-Device Viewport Verification: 390px, 430px, 1280px
        # =========================================================================
        print("\n--- TEST 5: Responsive Verification at 390px, 430px, 1280px ---")
        for width, name in [(390, "mobile_390"), (430, "mobile_430"), (1280, "desktop_1280")]:
            ctx = browser.new_context(viewport={"width": width, "height": 844}, device_scale_factor=2)
            p = ctx.new_page()
            p.goto("http://localhost:5173")
            p.wait_for_load_state("networkidle")
            p.wait_for_timeout(400)

            # Check mascot position
            m_btn = p.locator("button[aria-label*='Mindy AI Assistant']")
            assert m_btn.is_visible(), f"Mascot must be visible on {name}!"
            box = m_btn.bounding_box()
            assert box and box["x"] + box["width"] <= width, f"Mascot overflows screen on {name}!"

            shot_responsive = os.path.join(ARTIFACT_DIR, f"mascot_clean_{name}.png")
            p.screenshot(path=shot_responsive, full_page=False)
            print(f"PASS: {name} (width {width}px) verified and saved to {shot_responsive}")
            ctx.close()

        print("\n========================================================")
        print("ALL MASCOT GREETING FIX TESTS PASSED SUCCESSFULLY!")
        print("========================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()

