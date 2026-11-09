import os
import sys
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # 1. Mobile Light Mode (390 x 844 - iPhone 14/15)
        # -------------------------------------------------------------
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://localhost:5173/")
        page.wait_for_load_state("networkidle")

        # Set Light Theme
        page.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)

        # Check: Top hamburger menu MUST NOT exist
        hamburger = page.locator('button[aria-label="Open menu"]')
        assert not hamburger.is_visible(), "Hamburger button should be removed from mobile!"
        print("PASS: Hamburger button is removed from top navbar.")

        # Check: Bottom Navigation Bar exists and is visible
        bottom_nav = page.locator('nav[aria-label="Mobile Bottom Navigation"]')
        assert bottom_nav.is_visible(), "Bottom navbar must be visible on mobile!"
        print("PASS: Mobile bottom navigation bar is visible.")

        # Check: Exactly 4 items
        items = bottom_nav.locator("a, button, div.grid > *")
        nav_anchors = bottom_nav.locator("a")
        count = nav_anchors.count()
        assert count == 4, f"Expected exactly 4 items, found {count}"
        print(f"PASS: Exactly {count} navigation items present.")

        labels = [nav_anchors.nth(i).inner_text().strip() for i in range(count)]
        print(f"Nav item labels: {labels}")
        assert "Home" in labels[0]
        assert "Features" in labels[1]
        assert "How It Works" in labels[2]
        assert "Get Started" in labels[3]
        print("PASS: Items matched: Home, Features, How It Works, Get Started.")

        # Check: All four items are on a single horizontal line
        boxes = [nav_anchors.nth(i).bounding_box() for i in range(count)]
        y_coords = [b["y"] for b in boxes if b]
        assert max(y_coords) - min(y_coords) <= 2, f"Items are not on a single line! Y coords: {y_coords}"
        print(f"PASS: All 4 items are on one horizontal line (Y={y_coords[0]}).")

        # Check horizontal overflow
        sw = page.evaluate("document.documentElement.scrollWidth")
        cw = page.evaluate("document.documentElement.clientWidth")
        print(f"[Mobile 390px] scrollWidth: {sw}, clientWidth: {cw}")
        assert sw <= cw + 1, f"Horizontal overflow: {sw} > {cw}"

        # Capture Mobile 390px Light Screenshot
        shot_390_light = os.path.join(ARTIFACT_DIR, "mobile_bottom_nav_390_light.png")
        page.screenshot(path=shot_390_light, full_page=False)
        print("Captured mobile 390px light screenshot:", shot_390_light)

        # Test Navigation click: Features
        nav_anchors.nth(1).click()
        page.wait_for_timeout(800)
        shot_features = os.path.join(ARTIFACT_DIR, "mobile_scrolled_to_features.png")
        page.screenshot(path=shot_features, full_page=False)
        print("Captured scrolled to features screenshot:", shot_features)

        # Test Navigation click: Home
        nav_anchors.nth(0).click()
        page.wait_for_timeout(800)
        scroll_y = page.evaluate("window.scrollY")
        assert scroll_y < 100, f"Expected scroll position near 0, got {scroll_y}"
        print(f"PASS: Home button smoothly scrolled to top (scrollY={scroll_y}).")

        context.close()

        # -------------------------------------------------------------
        # 2. Narrow Mobile Viewport (320 x 650 - iPhone SE)
        # -------------------------------------------------------------
        context_320 = browser.new_context(
            viewport={"width": 320, "height": 650},
            device_scale_factor=2,
        )
        page_320 = context_320.new_page()
        page_320.goto("http://localhost:5173/")
        page_320.wait_for_load_state("networkidle")
        page_320.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page_320.reload()
        page_320.wait_for_load_state("networkidle")
        page_320.wait_for_timeout(800)

        sw_320 = page_320.evaluate("document.documentElement.scrollWidth")
        cw_320 = page_320.evaluate("document.documentElement.clientWidth")
        print(f"[Mobile 320px] scrollWidth: {sw_320}, clientWidth: {cw_320}")
        assert sw_320 <= cw_320 + 1, f"Horizontal overflow at 320px: {sw_320} > {cw_320}"

        b_nav_320 = page_320.locator('nav[aria-label="Mobile Bottom Navigation"]')
        anchors_320 = b_nav_320.locator("a")
        boxes_320 = [anchors_320.nth(i).bounding_box() for i in range(4)]
        y_320 = [b["y"] for b in boxes_320 if b]
        assert max(y_320) - min(y_320) <= 2, "Items wrapped on 320px!"
        print(f"PASS: All 4 items on single horizontal line at 320px (Y={y_320[0]}).")

        shot_320 = os.path.join(ARTIFACT_DIR, "mobile_bottom_nav_320_light.png")
        page_320.screenshot(path=shot_320, full_page=False)
        print("Captured 320px bottom nav screenshot:", shot_320)
        context_320.close()

        # -------------------------------------------------------------
        # 3. Mobile Dark Mode (390 x 844)
        # -------------------------------------------------------------
        context_dark = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page_dark = context_dark.new_page()
        page_dark.goto("http://localhost:5173/")
        page_dark.wait_for_load_state("networkidle")
        page_dark.evaluate("""
            localStorage.setItem('careermind-theme', 'dark');
            document.documentElement.setAttribute('data-theme', 'dark');
            document.documentElement.classList.add('dark');
        """)
        page_dark.reload()
        page_dark.wait_for_load_state("networkidle")
        page_dark.wait_for_timeout(800)

        shot_dark = os.path.join(ARTIFACT_DIR, "mobile_bottom_nav_390_dark.png")
        page_dark.screenshot(path=shot_dark, full_page=False)
        print("Captured 390px dark bottom nav screenshot:", shot_dark)
        context_dark.close()

        # -------------------------------------------------------------
        # 4. Desktop Viewport (1280 x 800 - Regression Check)
        # -------------------------------------------------------------
        context_desk = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
        )
        page_desk = context_desk.new_page()
        page_desk.goto("http://localhost:5173/")
        page_desk.wait_for_load_state("networkidle")
        page_desk.wait_for_timeout(800)

        # Check: Mobile bottom nav MUST NOT be visible on desktop
        b_nav_desk = page_desk.locator('nav[aria-label="Mobile Bottom Navigation"]')
        assert not b_nav_desk.is_visible(), "Mobile bottom nav must be hidden on desktop!"
        print("PASS: Mobile bottom nav is hidden on desktop.")

        # Check: Desktop top nav has all four items in one horizontal row
        top_nav = page_desk.locator("header nav")
        assert top_nav.is_visible(), "Desktop top nav must be visible!"
        desk_links = [top_nav.locator("a").nth(i).inner_text().strip() for i in range(top_nav.locator("a").count())]
        print("Desktop top nav items:", desk_links)
        assert "Home" in desk_links[0]
        assert "Features" in desk_links[1]
        assert "How It Works" in desk_links[2]

        get_started_btn = page_desk.locator('header a:has-text("Get Started")')
        assert get_started_btn.is_visible(), "Get Started button must be visible in desktop top nav!"
        print("PASS: Get Started button visible on desktop navbar.")

        shot_desk = os.path.join(ARTIFACT_DIR, "desktop_1280_regression.png")
        page_desk.screenshot(path=shot_desk, full_page=False)
        print("Captured desktop regression screenshot:", shot_desk)
        context_desk.close()

        # -------------------------------------------------------------
        # 5. Get Started Click Navigation Check
        # -------------------------------------------------------------
        context_cta = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
        )
        page_cta = context_cta.new_page()
        page_cta.goto("http://localhost:5173/")
        page_cta.wait_for_load_state("networkidle")
        b_nav_cta = page_cta.locator('nav[aria-label="Mobile Bottom Navigation"]')
        b_nav_cta.locator("a:has-text('Get Started')").click()
        page_cta.wait_for_load_state("networkidle")
        page_cta.wait_for_timeout(500)
        assert "/onboarding" in page_cta.url, f"Expected /onboarding in url, got {page_cta.url}"
        print(f"PASS: Get Started navigated successfully to {page_cta.url}.")
        context_cta.close()

        browser.close()
        print("\nALL MOBILE BOTTOM NAVBAR REQUIREMENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()

