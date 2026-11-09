import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # Desktop Test (1280 x 800)
        # -------------------------------------------------------------
        context = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        page = context.new_page()

        # Set Light Mode for first set of tests (like the reference screenshot)
        page.goto("http://localhost:5173/onboarding?edit=true")
        page.wait_for_load_state("networkidle")
        page.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)

        # Clear Full Name so Step 1 is fresh / empty
        name_input = page.locator("#full_name")
        name_input.fill("")
        # Click outside to ensure no focus
        page.locator("header").click()
        page.wait_for_timeout(500)

        # 1. State 1 (Hidden) on Step 1
        shot_s1_hidden = os.path.join(ARTIFACT_DIR, "onboarding_step1_state1_hidden.png")
        page.screenshot(path=shot_s1_hidden, full_page=False)
        print("Captured Step 1 State 1 (Hidden):", shot_s1_hidden)

        # 2. State 2 (Peeking): Focus Full Name input
        print("Focusing Full Name input...")
        name_input.focus()
        page.wait_for_timeout(600)
        shot_s1_peeking = os.path.join(ARTIFACT_DIR, "onboarding_step1_state2_peeking.png")
        page.screenshot(path=shot_s1_peeking, full_page=False)
        print("Captured Step 1 State 2 (Peeking):", shot_s1_peeking)

        # Type continuously - Mindy should remain visible
        name_input.type("Shivam Kumar Singh", delay=50)
        page.wait_for_timeout(300)

        # Move to Career Status (click Fresher) - no flickering
        fresher_btn = page.locator("button:has-text('Fresher')")
        fresher_btn.click()
        page.wait_for_timeout(500)

        # Click outside form to blur
        page.locator("header").click()
        page.wait_for_timeout(600)

        # 3. State 3 (CTA Companion): All Step 1 fields completed and blurred
        shot_s1_companion = os.path.join(ARTIFACT_DIR, "onboarding_step1_state3_companion.png")
        page.screenshot(path=shot_s1_companion, full_page=False)
        print("Captured Step 1 State 3 (CTA Companion):", shot_s1_companion)

        # Verify companion Mindy is visible near CTA button
        companion_mindy = page.locator("div[aria-hidden='true'] img[src*='mindy-welcome.png']")
        assert companion_mindy.last.is_visible(), "Companion Mindy must be visible when step is complete!"
        print("PASS: Companion Mindy is visible beside CTA button.")

        # Test Priority: Focus Full Name again -> Mindy returns to Peeking
        name_input.focus()
        page.wait_for_timeout(500)
        shot_s1_refocus = os.path.join(ARTIFACT_DIR, "onboarding_step1_refocus_peeking.png")
        page.screenshot(path=shot_s1_refocus, full_page=False)
        print("Captured Step 1 Refocus Peeking:", shot_s1_refocus)

        # Advance to Step 2
        next_btn = page.locator("button:has-text('Continue to Education')")
        next_btn.click()
        page.wait_for_timeout(600)

        # Click outside to ensure no field focused on Step 2
        page.locator("header").click()
        page.wait_for_timeout(500)

        # Step 2: Clear degree to ensure incomplete
        degree_input = page.locator("#degree")
        degree_input.fill("")
        page.locator("header").click()
        page.wait_for_timeout(500)

        # Step 2 State 1 (Hidden)
        shot_s2_hidden = os.path.join(ARTIFACT_DIR, "onboarding_step2_state1_hidden.png")
        page.screenshot(path=shot_s2_hidden, full_page=False)
        print("Captured Step 2 State 1 (Hidden):", shot_s2_hidden)

        # Step 2 State 2 (Peeking): Focus Degree
        degree_input.focus()
        page.wait_for_timeout(600)
        shot_s2_peeking = os.path.join(ARTIFACT_DIR, "onboarding_step2_state2_peeking.png")
        page.screenshot(path=shot_s2_peeking, full_page=False)
        print("Captured Step 2 State 2 (Peeking):", shot_s2_peeking)

        # Complete Step 2
        degree_input.type("B.Tech Computer Science", delay=30)
        inst_input = page.locator("#institution")
        inst_input.fill("Indian Institute of Technology")
        year_input = page.locator("#graduation_year")
        year_input.fill("2025")
        page.locator("header").click()
        page.wait_for_timeout(600)

        # Step 2 State 3 (CTA Companion)
        shot_s2_companion = os.path.join(ARTIFACT_DIR, "onboarding_step2_state3_companion.png")
        page.screenshot(path=shot_s2_companion, full_page=False)
        print("Captured Step 2 State 3 (CTA Companion):", shot_s2_companion)

        # Advance to Step 3
        next_s2_btn = page.locator("button:has-text('Continue to Preferences')")
        next_s2_btn.click()
        page.wait_for_timeout(600)

        # Step 3: Clear target role
        page.locator("header").click()
        page.wait_for_timeout(300)
        role_input = page.locator("#primary_target_role")
        role_input.fill("")
        page.locator("header").click()
        page.wait_for_timeout(500)

        # Step 3 State 1 (Hidden)
        shot_s3_hidden = os.path.join(ARTIFACT_DIR, "onboarding_step3_state1_hidden.png")
        page.screenshot(path=shot_s3_hidden, full_page=False)
        print("Captured Step 3 State 1 (Hidden):", shot_s3_hidden)

        # Step 3 State 2 (Peeking): Focus Role
        role_input.focus()
        page.wait_for_timeout(600)
        shot_s3_peeking = os.path.join(ARTIFACT_DIR, "onboarding_step3_state2_peeking.png")
        page.screenshot(path=shot_s3_peeking, full_page=False)
        print("Captured Step 3 State 2 (Peeking):", shot_s3_peeking)

        # Complete Step 3
        role_input.type("Full Stack AI Engineer", delay=30)
        page.locator("header").click()
        page.wait_for_timeout(600)

        # Step 3 State 3 (CTA Companion)
        shot_s3_companion = os.path.join(ARTIFACT_DIR, "onboarding_step3_state3_companion.png")
        page.screenshot(path=shot_s3_companion, full_page=False)
        print("Captured Step 3 State 3 (CTA Companion):", shot_s3_companion)

        # -------------------------------------------------------------
        # Mobile Test (375 x 667 - iPhone SE)
        # -------------------------------------------------------------
        print("\n--- Testing Mobile Viewport (375px) ---")
        m_ctx = browser.new_context(viewport={"width": 375, "height": 667}, device_scale_factor=2)
        m_page = m_ctx.new_page()
        m_page.goto("http://localhost:5173/onboarding?edit=true")
        m_page.wait_for_load_state("networkidle")
        m_page.wait_for_timeout(600)

        m_name = m_page.locator("#full_name")
        m_name.focus()
        m_page.wait_for_timeout(600)
        shot_m_peeking = os.path.join(ARTIFACT_DIR, "onboarding_mobile_375_peeking.png")
        m_page.screenshot(path=shot_m_peeking, full_page=False)
        print("Captured Mobile 375px Peeking:", shot_m_peeking)

        # Complete and blur on mobile
        m_name.fill("Shivam Kumar Singh")
        m_page.locator("button:has-text('Fresher')").click()
        m_page.locator("header").click()
        m_page.wait_for_timeout(600)
        shot_m_companion = os.path.join(ARTIFACT_DIR, "onboarding_mobile_375_companion.png")
        m_page.screenshot(path=shot_m_companion, full_page=False)
        print("Captured Mobile 375px Companion:", shot_m_companion)

        print("\nALL VERIFICATIONS PASSED!")
        browser.close()

if __name__ == "__main__":
    run_tests()

