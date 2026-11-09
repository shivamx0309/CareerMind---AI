import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # 1. Mobile Viewport (390 x 844 - iPhone 14/15)
        # -------------------------------------------------------------
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://localhost:5173/#features")
        page.wait_for_load_state("networkidle")

        # Set Light Mode
        page.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)

        # Scroll to #features
        page.locator("#features").scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # 1. Check Main Card on Feature 01
        card_heading = page.locator("#features h3")
        print("Initial main card heading:", card_heading.inner_text())
        assert "Resume Intelligence" in card_heading.inner_text(), "Initial card should be Resume Intelligence"

        # Check Green Available Badge on Card
        card_badge = page.locator("#features span:has-text('Available')")
        assert card_badge.first.is_visible(), "Available badge must be visible on main card!"
        print("PASS: Available badge visible on main card.")

        # Check Counter 01 / 05
        counter_pill = page.locator("#features span:has-text('01 / 05')")
        assert counter_pill.is_visible(), "01 / 05 counter pill must be visible on main card!"
        print("PASS: 01 / 05 counter pill is visible.")

        # Check 5 Horizontal Selectors exist in ONE row
        selectors = page.locator("#features div[ref='selectorsContainerRef'] button, #features .snap-x > button")
        sel_count = selectors.count()
        print(f"Total selectors: {sel_count}")
        assert sel_count == 5, f"Expected 5 selectors, got {sel_count}"

        # Verify all 5 selectors are on one horizontal line (same Y coordinate or scrollable container)
        boxes = [selectors.nth(i).bounding_box() for i in range(sel_count)]
        y_coords = [b["y"] for b in boxes if b]
        assert max(y_coords) - min(y_coords) <= 3, f"Selectors are not on a single line! Y coords: {y_coords}"
        print(f"PASS: All 5 selectors are in ONE horizontal row (Y={y_coords[0]}).")

        # Verify green 'Available' badge on ALL 5 selectors
        sel_badges = page.locator("#features .snap-x button > span:has-text('Available')")
        assert sel_badges.count() == 5, f"Expected 5 Available badges on selectors, got {sel_badges.count()}"
        print("PASS: Green 'Available' badge displayed on ALL FIVE selectors.")

        # Capture Mobile 390px Light Mode Screenshot
        shot_390 = os.path.join(ARTIFACT_DIR, "features_carousel_390_light.png")
        page.screenshot(path=shot_390, full_page=False)
        print("Captured mobile 390px screenshot:", shot_390)

        # 2. Test Arrow Controls: Click Next Arrow (>)
        next_btn = page.locator('button[aria-label="Next feature"]')
        next_btn.click()
        page.wait_for_timeout(600)
        heading_after_next = page.locator("#features h3").inner_text()
        print("Heading after next arrow click:", heading_after_next)
        assert "Job Description Matching" in heading_after_next
        print("PASS: Next arrow advanced to Job Description Matching.")

        # 3. Test Selector Click: Click Selector 05 (AI Interview)
        selectors.nth(4).click()
        page.wait_for_timeout(600)
        heading_after_sel5 = page.locator("#features h3").inner_text()
        print("Heading after clicking selector 05:", heading_after_sel5)
        assert "AI Interview Preparation" in heading_after_sel5
        print("PASS: Clicking selector 05 switched card to AI Interview Preparation.")

        # Capture Clicked State
        shot_sel = os.path.join(ARTIFACT_DIR, "features_carousel_selector_clicked.png")
        page.screenshot(path=shot_sel, full_page=False)
        print("Captured selector click screenshot:", shot_sel)

        # 4. Test Continuous Looping: Click Next Arrow from 05 -> loops to 01
        next_btn.click()
        page.wait_for_timeout(600)
        heading_loop = page.locator("#features h3").inner_text()
        print("Heading after looping from 5:", heading_loop)
        assert "Resume Intelligence" in heading_loop
        print("PASS: Carousel looped continuously from 05 back to 01.")

        # 5. Test Autoplay (advance after 4 seconds)
        print("Testing 4s autoplay...")
        # Move mouse completely away to trigger onMouseLeave and unpause
        page.mouse.move(5, 5)
        page.locator("body").hover(position={"x": 5, "y": 5})
        page.wait_for_timeout(4500)
        heading_autoplay = page.locator("#features h3").inner_text()
        print("Heading after 4s autoplay:", heading_autoplay)
        assert "Job Description Matching" in heading_autoplay
        print("PASS: Autoplay successfully advanced to next feature after 4s.")

        context.close()

        # -------------------------------------------------------------
        # 2. Mobile Dark Mode (390 x 844)
        # -------------------------------------------------------------
        context_dark = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page_dark = context_dark.new_page()
        page_dark.goto("http://localhost:5173/#features")
        page_dark.wait_for_load_state("networkidle")
        page_dark.evaluate("""
            localStorage.setItem('careermind-theme', 'dark');
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.classList.add('dark');
        """)
        page_dark.reload()
        page_dark.wait_for_load_state("networkidle")
        page_dark.wait_for_timeout(800)
        page_dark.locator("#features").scroll_into_view_if_needed()
        page_dark.wait_for_timeout(400)

        shot_dark = os.path.join(ARTIFACT_DIR, "features_carousel_390_dark.png")
        page_dark.screenshot(path=shot_dark, full_page=False)
        print("Captured mobile 390px dark screenshot:", shot_dark)
        context_dark.close()

        # -------------------------------------------------------------
        # 3. Narrow Mobile (320 x 650 - iPhone SE)
        # -------------------------------------------------------------
        context_320 = browser.new_context(
            viewport={"width": 320, "height": 650},
            device_scale_factor=2,
        )
        page_320 = context_320.new_page()
        page_320.goto("http://localhost:5173/#features")
        page_320.wait_for_load_state("networkidle")
        page_320.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page_320.reload()
        page_320.wait_for_load_state("networkidle")
        page_320.wait_for_timeout(800)
        page_320.locator("#features").scroll_into_view_if_needed()
        page_320.wait_for_timeout(400)

        # Check overflow
        sw_320 = page_320.evaluate("document.documentElement.scrollWidth")
        cw_320 = page_320.evaluate("document.documentElement.clientWidth")
        assert sw_320 <= cw_320 + 1, f"Horizontal overflow at 320px: {sw_320} > {cw_320}"
        print(f"PASS: No horizontal overflow at 320px (sw={sw_320}, cw={cw_320}).")

        shot_320 = os.path.join(ARTIFACT_DIR, "features_carousel_320_light.png")
        page_320.screenshot(path=shot_320, full_page=False)
        print("Captured mobile 320px screenshot:", shot_320)
        context_320.close()

        # -------------------------------------------------------------
        # 4. Desktop Viewport (1280 x 800)
        # -------------------------------------------------------------
        context_desk = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
        )
        page_desk = context_desk.new_page()
        page_desk.goto("http://localhost:5173/#features")
        page_desk.wait_for_load_state("networkidle")
        page_desk.wait_for_timeout(800)
        page_desk.locator("#features").scroll_into_view_if_needed()
        page_desk.wait_for_timeout(400)

        shot_desk = os.path.join(ARTIFACT_DIR, "features_carousel_desktop_1280.png")
        page_desk.screenshot(path=shot_desk, full_page=False)
        print("Captured desktop 1280px screenshot:", shot_desk)
        context_desk.close()

        browser.close()
        print("\nALL FEATURE CAROUSEL REQUIREMENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
