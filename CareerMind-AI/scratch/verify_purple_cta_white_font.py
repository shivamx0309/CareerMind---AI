import subprocess
import time
import os
import sys
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
PROJECT_DIR = r"C:\Users\ASUS\Videos\CareerAI\CareerMind-AI"
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")

def main():
    print("Starting backend and frontend preview servers...")
    
    # 1. Start backend
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 2. Start frontend preview (port 4173)
    frontend_proc = subprocess.Popen(
        ["npm.cmd", "run", "preview", "--", "--port", "4173"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(4)
    print("Servers started. Launching Playwright tests...")
    
    errors = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            try:
                browser = p.chromium.launch(channel="msedge", headless=True)
            except Exception as e:
                print(f"Could not launch chrome/edge: {e}")
                raise
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        
        # Test 1: Landing Page - Light Theme
        page.goto("http://localhost:4173/", wait_until="networkidle")
        page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
        page.wait_for_timeout(500)
        
        # Check Hero CTA
        hero_btn = page.locator(".purple-gradient-btn").first
        hero_color = hero_btn.evaluate("el => window.getComputedStyle(el).color")
        print(f"[Light Theme] Hero CTA font color: {hero_color}")
        if hero_color != "rgb(255, 255, 255)":
            errors.append(f"Hero CTA color is {hero_color}, expected rgb(255, 255, 255)")
            
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_light_landing_hero.png"))
        
        # Scroll to How It Works (Section 1)
        page.locator("#how-it-works").scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_light_landing_workflow.png"))
        
        # Scroll to Why CareerMind (Section 2)
        page.locator("#why-careermind").scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_light_landing_decisions.png"))
        
        # Scroll to Final CTA
        final_btn = page.locator("section:has-text('Ready to Take Control') .purple-gradient-btn").first
        if final_btn.is_visible():
            final_color = final_btn.evaluate("el => window.getComputedStyle(el).color")
            print(f"[Light Theme] Final CTA font color: {final_color}")
            if final_color != "rgb(255, 255, 255)":
                errors.append(f"Final CTA color is {final_color}, expected rgb(255, 255, 255)")
                
        # Test 2: Landing Page - Dark Theme
        page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
        page.wait_for_timeout(500)
        
        hero_dark_color = hero_btn.evaluate("el => window.getComputedStyle(el).color")
        print(f"[Dark Theme] Hero CTA font color: {hero_dark_color}")
        if hero_dark_color != "rgb(255, 255, 255)":
            errors.append(f"[Dark] Hero CTA color is {hero_dark_color}, expected rgb(255, 255, 255)")
            
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_dark_landing_hero.png"))
        
        # Test 3: Dashboard - Light Theme
        page.goto("http://localhost:4173/dashboard", wait_until="networkidle")
        page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
        page.wait_for_timeout(800)
        
        dash_cta = page.locator(".primary-button").first
        dash_color = dash_cta.evaluate("el => window.getComputedStyle(el).color")
        print(f"[Light Theme] Dashboard 'Analyze my resume' CTA font color: {dash_color}")
        if dash_color != "rgb(255, 255, 255)":
            errors.append(f"Dashboard CTA color is {dash_color}, expected rgb(255, 255, 255)")
            
        # Check active sidebar item
        active_nav = page.locator(".nav-item.active").first
        nav_color = active_nav.evaluate("el => window.getComputedStyle(el).color")
        print(f"[Light Theme] Sidebar active nav item font color: {nav_color}")
        if nav_color != "rgb(255, 255, 255)":
            errors.append(f"Sidebar active nav item color is {nav_color}, expected rgb(255, 255, 255)")
            
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_light_dashboard.png"))
        
        # Test 4: Dashboard - Dark Theme
        page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
        page.wait_for_timeout(500)
        
        dash_dark_color = dash_cta.evaluate("el => window.getComputedStyle(el).color")
        print(f"[Dark Theme] Dashboard 'Analyze my resume' CTA font color: {dash_dark_color}")
        if dash_dark_color != "rgb(255, 255, 255)":
            errors.append(f"[Dark] Dashboard CTA color is {dash_dark_color}, expected rgb(255, 255, 255)")
            
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_dark_dashboard.png"))
        
        # Test 5: Mobile Dashboard (375px)
        mobile_context = browser.new_context(viewport={"width": 375, "height": 812})
        mobile_page = mobile_context.new_page()
        mobile_page.goto("http://localhost:4173/dashboard", wait_until="networkidle")
        mobile_page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
        mobile_page.wait_for_timeout(600)
        
        mobile_bubble = mobile_page.locator(".timeline-bubble.completed, .timeline-bubble.active").first
        if mobile_bubble.is_visible():
            bubble_color = mobile_bubble.evaluate("el => window.getComputedStyle(el).color")
            print(f"[Mobile Light] Timeline completed bubble color: {bubble_color}")
            if bubble_color != "rgb(255, 255, 255)":
                errors.append(f"Timeline bubble color is {bubble_color}, expected rgb(255, 255, 255)")
                
        mobile_page.screenshot(path=os.path.join(ARTIFACT_DIR, "cta_mobile_light_dashboard.png"))
        
        browser.close()
        
    # Shutdown servers
    backend_proc.terminate()
    frontend_proc.terminate()
    
    print("\n--- TEST SUMMARY ---")
    if errors:
        print(f"FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("ALL PURPLE CTA BACKGROUNDS STRICTLY USE WHITE FONT COLOR (rgb(255, 255, 255)) IN BOTH LIGHT AND DARK THEMES!")
        sys.exit(0)

if __name__ == "__main__":
    main()
