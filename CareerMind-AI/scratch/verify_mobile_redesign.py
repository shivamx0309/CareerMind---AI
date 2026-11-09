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

        # Force Light Theme
        page.evaluate("""
            localStorage.setItem('careermind-theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
            document.documentElement.classList.remove('dark');
        """)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Check horizontal overflow
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        print(f"[Mobile 390px] scrollWidth: {scroll_width}, clientWidth: {client_width}")
        assert scroll_width <= client_width + 1, f"Horizontal overflow detected: {scroll_width} > {client_width}"

        # Capture Hero & Mascot on 390px
        hero_shot = os.path.join(ARTIFACT_DIR, "mobile_390_hero_light.png")
        page.screenshot(path=hero_shot, full_page=False)
        print("Captured 390px hero light screenshot:", hero_shot)

        # Open Hamburger Menu
        menu_button = page.locator('button[aria-label="Open menu"]')
        if menu_button.is_visible():
            menu_button.click()
            page.wait_for_timeout(500)
            drawer_shot = os.path.join(ARTIFACT_DIR, "mobile_390_menu_drawer_light.png")
            page.screenshot(path=drawer_shot, full_page=False)
            print("Captured 390px menu drawer screenshot:", drawer_shot)
            # Close it
            page.locator('button[aria-label="Close menu"]').click()
            page.wait_for_timeout(300)

        # Full page mobile screenshot
        full_shot = os.path.join(ARTIFACT_DIR, "mobile_390_fullpage_light.png")
        page.screenshot(path=full_shot, full_page=True)
        print("Captured full page 390px light screenshot:", full_shot)

        context.close()

        # -------------------------------------------------------------
        # 2. Narrow Screen Mobile (320 x 600 - Smallest Mobile SE)
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
        page_320.wait_for_timeout(1000)

        sw_320 = page_320.evaluate("document.documentElement.scrollWidth")
        cw_320 = page_320.evaluate("document.documentElement.clientWidth")
        print(f"[Mobile 320px] scrollWidth: {sw_320}, clientWidth: {cw_320}")
        assert sw_320 <= cw_320 + 1, f"Horizontal overflow on 320px: {sw_320} > {cw_320}"

        shot_320 = os.path.join(ARTIFACT_DIR, "mobile_320_hero_light.png")
        page_320.screenshot(path=shot_320, full_page=False)
        print("Captured 320px hero screenshot:", shot_320)
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
        page_dark.wait_for_timeout(1000)

        shot_dark = os.path.join(ARTIFACT_DIR, "mobile_390_hero_dark.png")
        page_dark.screenshot(path=shot_dark, full_page=False)
        print("Captured 390px dark hero screenshot:", shot_dark)
        context_dark.close()

        # -------------------------------------------------------------
        # 4. Desktop Layout Verification (1280 x 800)
        # -------------------------------------------------------------
        context_desk = browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
        )
        page_desk = context_desk.new_page()
        page_desk.goto("http://localhost:5173/")
        page_desk.wait_for_load_state("networkidle")
        page_desk.wait_for_timeout(1000)

        shot_desk = os.path.join(ARTIFACT_DIR, "desktop_1280_hero.png")
        page_desk.screenshot(path=shot_desk, full_page=False)
        print("Captured desktop 1280px screenshot:", shot_desk)
        context_desk.close()

        browser.close()
        print("All tests and visual verifications passed successfully!")

if __name__ == "__main__":
    run_tests()
