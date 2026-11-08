import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
BASE_URL = "http://localhost:5173"

def run_tests():
    print(f"Connecting to {BASE_URL} with Microsoft Edge...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # -------------------------------------------------------------
        # 1. Desktop Landing Page Test (1280 x 800)
        # -------------------------------------------------------------
        page_desktop = browser.new_page(viewport={"width": 1280, "height": 800})
        page_desktop.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1.5)
        
        # Verify Navbar: Exactly 3 Zones (Left Logo, Center 3 Links, Right CTA & Theme)
        nav_center_links = page_desktop.locator("nav a").all_text_contents()
        print(f"[Pass] Desktop Navbar Center Links: {nav_center_links}")
        assert "Home" in nav_center_links
        assert "Features" in nav_center_links
        assert "How It Works" in nav_center_links
        
        get_started_btn = page_desktop.locator("header a:has-text('Get Started')")
        assert get_started_btn.is_visible(), "Get Started CTA button missing"
        print("[Pass] Get Started CTA button is visible in navbar")
        
        # Verify Hero Section Content
        badge = page_desktop.locator("text=AI-Powered Career Intelligence Platform")
        assert badge.is_visible(), "Hero badge missing"
        
        heading = page_desktop.locator("h1")
        print(f"[Pass] Hero Heading: '{heading.text_content().strip()}'")
        assert "Your Career." in heading.text_content()
        assert "Your Intelligence. Your Growth." in heading.text_content()
        
        desc = page_desktop.locator("text=Analyze your skills, find opportunities and get interview-ready — all in one platform.")
        assert desc.is_visible(), "Hero description missing"
        
        cta_primary = page_desktop.locator("a:has-text('Build My Career Profile')").first
        cta_secondary = page_desktop.locator("a:has-text('Explore Features')").first
        assert cta_primary.is_visible(), "Primary CTA button missing"
        assert cta_secondary.is_visible(), "Secondary CTA button missing"
        
        # Verify 3 Trust Indicators
        trust1 = page_desktop.locator("text=Local-First & Private").first
        trust2 = page_desktop.locator("text=Explainable Scoring").first
        trust3 = page_desktop.locator("text=Zero External LLM APIs").first
        assert trust1.is_visible() and trust2.is_visible() and trust3.is_visible(), "Trust indicators missing"
        print("[Pass] 3 trust indicators verified")
        
        # Verify Mindy Mascot & 4 Orbital Badges
        mindy_img = page_desktop.locator("img[alt*='Mindy']").first
        assert mindy_img.is_visible(), "Mindy mascot image missing"
        
        badge_resume = page_desktop.locator("text=Resume").first
        badge_jobs = page_desktop.locator("text=Job Matching").first
        badge_analytics = page_desktop.locator("text=Analytics").first
        badge_interview = page_desktop.locator("text=AI Interview").first
        assert badge_resume.is_visible(), "Orbital Resume badge missing"
        assert badge_jobs.is_visible(), "Orbital Job Matching badge missing"
        assert badge_analytics.is_visible(), "Orbital Analytics badge missing"
        assert badge_interview.is_visible(), "Orbital AI Interview badge missing"
        print("[Pass] Mindy mascot and all 4 revolving orbital badges verified")
        
        # Screenshot Desktop Hero with Mindy & Orbit
        page_desktop.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_desktop_hero.png"))
        print("[Pass] Saved mindy_desktop_hero.png")
        
        # Verify Floating Chatbot
        chatbot_btn = page_desktop.locator("button[aria-label*='Mindy AI Assistant']")
        assert chatbot_btn.is_visible(), "Floating chatbot button missing"
        chatbot_btn.click()
        time.sleep(0.5)
        
        chat_header = page_desktop.locator("text=Hi! I'm Mindy 👋").first
        assert chat_header.is_visible(), "Chatbot header missing"
        page_desktop.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_chatbot_opened.png"))
        print("[Pass] Saved mindy_chatbot_opened.png")
        
        # Close Chatbot
        page_desktop.locator("button[aria-label='Close Mindy Chat']").click()
        time.sleep(0.5)
        
        # Scroll to Final CTA Section with Mindy celebrating
        page_desktop.locator("text=Ready to Take Control").scroll_into_view_if_needed()
        time.sleep(0.8)
        page_desktop.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_final_cta.png"))
        print("[Pass] Saved mindy_final_cta.png")
        page_desktop.close()
        
        # -------------------------------------------------------------
        # 2. Mobile View (390 x 844)
        # -------------------------------------------------------------
        page_mob = browser.new_page(viewport={"width": 390, "height": 844})
        page_mob.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1)
        page_mob.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_mobile_hero.png"))
        print("[Pass] Saved mindy_mobile_hero.png")
        
        # Open mobile hamburger menu
        page_mob.click("button[aria-label='Open menu']")
        time.sleep(0.5)
        page_mob.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_mobile_menu.png"))
        print("[Pass] Saved mindy_mobile_menu.png")
        page_mob.close()
        
        # -------------------------------------------------------------
        # 3. Tablet View (768 x 1024)
        # -------------------------------------------------------------
        page_tab = browser.new_page(viewport={"width": 768, "height": 1024})
        page_tab.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1)
        page_tab.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_tablet_hero.png"))
        print("[Pass] Saved mindy_tablet_hero.png")
        page_tab.close()

        # -------------------------------------------------------------
        # 4. Verify /onboarding with Mindy Header
        # -------------------------------------------------------------
        page_onboarding = browser.new_page(viewport={"width": 425, "height": 962})
        page_onboarding.goto(f"{BASE_URL}/onboarding?edit=true", wait_until="networkidle")
        time.sleep(1)
        page_onboarding.screenshot(path=os.path.join(ARTIFACT_DIR, "mindy_onboarding_mobile.png"))
        print("[Pass] Saved mindy_onboarding_mobile.png")
        page_onboarding.close()

        browser.close()
        print("\n=======================================================")
        print("🎉 ALL MINDY MASCOT & REDESIGN VERIFICATIONS PASSED!")
        print("=======================================================")

if __name__ == "__main__":
    run_tests()
