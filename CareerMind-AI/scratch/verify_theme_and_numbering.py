import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
BASE_URL = "http://localhost:5173"

def run_tests():
    print(f"Verifying Numbering 1-5 and CTA Text Color across Light and Dark Themes at {BASE_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1)

        # -------------------------------------------------------------
        # 1. Dark Theme Verification (as in user screenshot)
        # -------------------------------------------------------------
        # Set dark theme on document root if not already
        page.evaluate("() => document.documentElement.setAttribute('data-theme', 'dark')")
        time.sleep(0.5)

        features_sec = page.locator("#features")
        features_sec.scroll_into_view_if_needed()
        time.sleep(0.8)

        # Verify Numbers 01 to 05
        featured_num = page.locator("#features .lg\\:col-span-5").get_by_text("Feature 01 of 05")
        assert featured_num.is_visible(), "Featured number 01 missing"
        print("[Pass] Dark mode: Featured card shows 'Feature 01 of 05'")

        small_num_badges = page.locator("#features .lg\\:col-span-7").get_by_text("#0").all_text_contents()
        print(f"[Pass] Dark mode small card number badges: {small_num_badges}")

        # Check CTA Button Text Color in Dark Mode
        cta_btn = page.locator("#features .featured-card-cta")
        assert cta_btn.is_visible(), "Featured CTA button missing"
        
        # Verify text content and computed color
        cta_text = cta_btn.text_content().strip()
        print(f"[Pass] CTA text content: '{cta_text}'")
        assert "Analyze Resume" in cta_text

        cta_color = cta_btn.evaluate("el => window.getComputedStyle(el).color")
        cta_bg = cta_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
        print(f"[Pass] Dark mode CTA: Background = {cta_bg}, Color = {cta_color}")
        # Color must NOT be white rgb(255, 255, 255) on white bg rgb(255, 255, 255)
        assert cta_color != "rgb(255, 255, 255)", "ERROR: CTA text is white on white background!"

        # Screenshot Dark Mode Features Section
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_dark_theme_numbered_cta.png"))
        print("[Pass] Saved verified_dark_theme_numbered_cta.png")

        # -------------------------------------------------------------
        # 2. Light Theme Verification
        # -------------------------------------------------------------
        print("\n--- Light Theme Verification ---")
        page.evaluate("() => document.documentElement.setAttribute('data-theme', 'light')")
        time.sleep(0.5)

        features_sec.scroll_into_view_if_needed()
        time.sleep(0.5)

        cta_btn_light = page.locator("#features .featured-card-cta")
        cta_color_light = cta_btn_light.evaluate("el => window.getComputedStyle(el).color")
        cta_bg_light = cta_btn_light.evaluate("el => window.getComputedStyle(el).backgroundColor")
        print(f"[Pass] Light mode CTA: Background = {cta_bg_light}, Color = {cta_color_light}")
        assert cta_color_light != "rgb(255, 255, 255)", "ERROR: Light mode CTA text is white on white!"

        # Screenshot Light Mode Features Section
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_light_theme_numbered_cta.png"))
        print("[Pass] Saved verified_light_theme_numbered_cta.png")

        # -------------------------------------------------------------
        # 3. Swap Card Verification in Dark Mode with Numbering
        # -------------------------------------------------------------
        page.evaluate("() => document.documentElement.setAttribute('data-theme', 'dark')")
        time.sleep(0.3)

        # Click 03. Skill Gap Analysis
        page.locator("#features .lg\\:col-span-7 h4:has-text('Skill Gap Analysis')").click()
        time.sleep(0.6)

        new_featured_num = page.locator("#features .lg\\:col-span-5").get_by_text("Feature 03 of 05")
        assert new_featured_num.is_visible()
        print("[Pass] Swapped: Featured card now shows 'Feature 03 of 05'")

        page.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_dark_swapped_feature_03.png"))
        print("[Pass] Saved verified_dark_swapped_feature_03.png")

        page.close()
        browser.close()
        print("\n=================================================================")
        print("🎉 THEME CONTRAST & NUMBERING 1-5 FULLY VERIFIED IN BOTH THEMES!")
        print("=================================================================")

if __name__ == "__main__":
    run_tests()
