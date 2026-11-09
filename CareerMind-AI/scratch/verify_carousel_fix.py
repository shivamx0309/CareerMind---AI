import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # Test 1: Mobile Dark Mode (matching user's screenshots) - 375x667
        # -------------------------------------------------------------
        context = browser.new_context(
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://localhost:5173/#features")
        page.wait_for_load_state("networkidle")

        # Set Dark Mode (user was in dark mode in screenshots)
        page.evaluate("""
            localStorage.setItem('careermind-theme', 'dark');
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.classList.add('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)

        # Scroll to features
        page.locator("#features").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        next_btn = page.locator('button[aria-label="Next feature"]')
        prev_btn = page.locator('button[aria-label="Previous feature"]')
        navbar_brand = page.locator('header a:has-text("CareerMind"), nav a:has-text("CareerMind")').first

        # Check initial state
        initial_card = page.locator("#features h3").inner_text()
        print(f"Step 0 (Initial): {initial_card}")
        assert "Resume Intelligence" in initial_card

        initial_win_x = page.evaluate("window.scrollX")
        initial_cnt_x = page.evaluate("document.querySelector('.landing-page-container') ? document.querySelector('.landing-page-container').scrollLeft : 0")
        assert initial_win_x == 0, f"Initial window.scrollX must be 0, got {initial_win_x}"
        assert initial_cnt_x == 0, f"Initial container.scrollLeft must be 0, got {initial_cnt_x}"

        initial_box = page.locator("#features .relative.z-10.w-\\[92\\%\\], #features .rounded-3xl.p-5").first.bounding_box()
        initial_card_x = initial_box["x"]
        print(f"Initial card X position: {initial_card_x}")

        # Cycle through Next arrow: 0 -> 1 -> 2 -> 3 (Card 04) -> 4 (Card 05)
        for step in range(1, 5):
            print(f"\n--- Clicking Next Arrow -> advancing to step {step} ---")
            next_btn.click()
            page.wait_for_timeout(600)

            title = page.locator("#features h3").inner_text()
            win_x = page.evaluate("window.scrollX")
            cnt_x = page.evaluate("document.querySelector('.landing-page-container') ? document.querySelector('.landing-page-container').scrollLeft : 0")
            card_box = page.locator("#features .relative.z-10.w-\\[92\\%\\], #features .rounded-3xl.p-5").first.bounding_box()
            curr_x = card_box["x"]

            print(f"Active Feature: {title}")
            print(f"window.scrollX: {win_x} (expected 0)")
            print(f"container.scrollLeft: {cnt_x} (expected 0)")
            print(f"Card X: {curr_x} (diff from initial: {round(abs(curr_x - initial_card_x), 2)}px)")

            assert win_x == 0, f"FAIL: window.scrollX shifted to {win_x}!"
            assert cnt_x == 0, f"FAIL: landing-page-container.scrollLeft shifted to {cnt_x}!"
            assert abs(curr_x - initial_card_x) < 5, f"FAIL: Card position drifted by {abs(curr_x - initial_card_x)}px!"

            # Verify Left Arrow is completely visible and within viewport bounds
            prev_box = prev_btn.bounding_box()
            assert prev_box and prev_box["x"] >= 0, f"FAIL: Left arrow shifted off-screen! x={prev_box['x'] if prev_box else None}"

            # Capture screenshots of Card 04 and Card 05
            if step == 3:
                shot_card4 = os.path.join(ARTIFACT_DIR, "features_card04_centered.png")
                page.screenshot(path=shot_card4, full_page=False)
                print(f"SAVED Card 04 screenshot: {shot_card4}")
            elif step == 4:
                shot_card5 = os.path.join(ARTIFACT_DIR, "features_card05_centered.png")
                page.screenshot(path=shot_card5, full_page=False)
                print(f"SAVED Card 05 screenshot: {shot_card5}")

        # -------------------------------------------------------------
        # Test 2: Click Next from 4 -> loops back to 0
        # -------------------------------------------------------------
        print("\n--- Testing Loop from 05 -> 01 ---")
        next_btn.click()
        page.wait_for_timeout(600)
        title_loop = page.locator("#features h3").inner_text()
        print(f"After looping: {title_loop}")
        assert "Resume Intelligence" in title_loop
        assert page.evaluate("window.scrollX") == 0
        assert page.evaluate("document.querySelector('.landing-page-container') ? document.querySelector('.landing-page-container').scrollLeft : 0") == 0
        print("PASS: Carousel looped back to 01 seamlessly.")

        # -------------------------------------------------------------
        # Test 3: Backward navigation via Prev Arrow
        # -------------------------------------------------------------
        print("\n--- Testing Backward Navigation via Prev Arrow ---")
        prev_btn.click()
        page.wait_for_timeout(600)
        title_prev = page.locator("#features h3").inner_text()
        print(f"After Prev click: {title_prev}")
        assert "AI Interview Preparation" in title_prev
        assert page.evaluate("window.scrollX") == 0
        assert page.evaluate("document.querySelector('.landing-page-container') ? document.querySelector('.landing-page-container').scrollLeft : 0") == 0
        print("PASS: Prev arrow navigated to 05 with 0px viewport shift.")

        # -------------------------------------------------------------
        # Test 4: Direct Selector Clicks
        # -------------------------------------------------------------
        print("\n--- Testing Direct Selector Clicks ---")
        selectors = page.locator("#features .snap-x > button")
        for i in [2, 3, 4, 1, 0]:
            selectors.nth(i).click()
            page.wait_for_timeout(500)
            win_x = page.evaluate("window.scrollX")
            cnt_x = page.evaluate("document.querySelector('.landing-page-container') ? document.querySelector('.landing-page-container').scrollLeft : 0")
            print(f"Clicked Selector {i+1}: winX={win_x}, cntX={cnt_x}")
            assert win_x == 0 and cnt_x == 0, f"FAIL on selector {i+1} click!"

        print("\n============================================")
        print("ALL TESTS PASSED! ZERO VIEWPORT DRIFT CONFIRMED!")
        print("============================================")
        browser.close()

if __name__ == "__main__":
    run_tests()

