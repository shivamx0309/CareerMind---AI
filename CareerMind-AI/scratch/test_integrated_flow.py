import os
import time
import threading
import http.server
import socketserver
from playwright.sync_api import sync_playwright

PORT = 5195
DIRECTORY = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend\dist"
ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            self.path = "/index.html"
        return super().do_GET()

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), SPAHandler) as httpd:
        print(f"Serving at http://127.0.0.1:{PORT}")
        httpd.serve_forever()

def run():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    print("Launching Playwright verification for Mindy Mascot & Landing Redesign...")
    # Launch browser using chromium inside the python process
    # Note: On Windows if ms-playwright is in localappdata, launch with standard channel if needed
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            
            # 1. Desktop View (1280 x 800)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
            page.wait_for_selector("text=Your Career", timeout=10000)
            time.sleep(1)
            
            # Verify Mindy mascot image loaded
            mascot_img = page.locator("img[alt*='Mindy']").first
            assert mascot_img.is_visible(), "Mindy mascot is not visible in Hero!"
            print("[Pass] Mindy mascot is visible in Hero section")
            
            # Verify 4 orbital badges
            resume_badge = page.locator("text=Resume").first
            job_badge = page.locator("text=Job Matching").first
            analytics_badge = page.locator("text=Analytics").first
            interview_badge = page.locator("text=AI Interview").first
            assert resume_badge.is_visible(), "Resume orbital badge missing"
            assert job_badge.is_visible(), "Job Matching orbital badge missing"
            assert analytics_badge.is_visible(), "Analytics orbital badge missing"
            assert interview_badge.is_visible(), "AI Interview orbital badge missing"
            print("[Pass] All 4 Mindy orbital badges are present")
            
            # Screenshot Desktop Hero with Mindy
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_mindy_desktop_hero.png"))
            print("[Pass] Saved verified_mindy_desktop_hero.png")
            
            # Test Floating Chatbot
            chatbot_btn = page.locator("button[aria-label*='Mindy AI Assistant']")
            assert chatbot_btn.is_visible(), "Floating chatbot button is missing"
            chatbot_btn.click()
            time.sleep(0.5)
            page.wait_for_selector("text=Hi! I'm Mindy 👋", timeout=5000)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_mindy_chatbot_open.png"))
            print("[Pass] Mindy chatbot opened and screenshot saved")
            
            # Close chatbot
            page.locator("button[aria-label='Close Mindy Chat']").click()
            time.sleep(0.5)
            
            # Scroll to Final CTA Section with Mindy
            page.locator("text=Ready to Take Control").scroll_into_view_if_needed()
            time.sleep(0.8)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_mindy_final_cta.png"))
            print("[Pass] Saved verified_mindy_final_cta.png")
            
            page.close()
            
            # 2. Mobile View (390 x 844)
            page_mob = browser.new_page(viewport={"width": 390, "height": 844})
            page_mob.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
            page_mob.wait_for_selector("text=Your Career", timeout=10000)
            time.sleep(1)
            page_mob.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_mindy_mobile_hero.png"))
            print("[Pass] Saved verified_mindy_mobile_hero.png")
            
            # Open mobile menu
            page_mob.click("button[aria-label='Open menu']")
            time.sleep(0.5)
            page_mob.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_mindy_mobile_menu.png"))
            print("[Pass] Saved verified_mindy_mobile_menu.png")
            page_mob.close()

            # 3. Tablet View (768 x 1024)
            page_tab = browser.new_page(viewport={"width": 768, "height": 1024})
            page_tab.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
            page_tab.wait_for_selector("text=Your Career", timeout=10000)
            time.sleep(1)
            page_tab.screenshot(path=os.path.join(ARTIFACT_DIR, "verified_mindy_tablet_hero.png"))
            print("[Pass] Saved verified_mindy_tablet_hero.png")
            page_tab.close()
            
            browser.close()
            print("\n*** ALL PLAYWRIGHT MINDY VERIFICATIONS PASSED SUCCESSFULLY ***")
    except Exception as e:
        print(f"Playwright execution error: {e}")

if __name__ == "__main__":
    run()
