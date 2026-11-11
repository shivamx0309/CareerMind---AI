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
    
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    frontend_proc = subprocess.Popen(
        ["npm.cmd", "run", "preview", "--", "--port", "4173"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = p.chromium.launch(channel="msedge", headless=True)
            
        # Test mobile view matching user screenshot (425 x 750)
        context = browser.new_context(viewport={"width": 425, "height": 750})
        page = context.new_page()
        
        # Switch to light theme properly via localStorage and DOM
        page.add_init_script("localStorage.setItem('careermind-theme', 'light');")
        page.goto("http://localhost:4173/roadmap", wait_until="networkidle")
        page.evaluate("document.documentElement.classList.remove('dark'); document.documentElement.setAttribute('data-theme', 'light');")
        page.wait_for_timeout(600)
        
        # Click "Generate Roadmap" or "New Roadmap" button to open modal
        generate_btn = page.locator("button:has-text('Generate Roadmap'), button:has-text('New Roadmap'), button:has-text('Create Roadmap')").first
        if generate_btn.is_visible():
            generate_btn.click()
            page.wait_for_timeout(600)
        else:
            print("Generate button not immediately found, checking page...")
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_empty_page_light.png"))
            
        # Check if modal is visible
        modal_title = page.locator("text='Generate Learning Roadmap'")
        if modal_title.is_visible():
            print("Modal successfully opened!")
            
            # Check 10h/wk active button color
            active_preset = page.locator("button:has-text('10h / wk')").first
            preset_color = active_preset.evaluate("el => window.getComputedStyle(el).color")
            preset_bg = active_preset.evaluate("el => window.getComputedStyle(el).backgroundColor")
            print(f"[Light Theme Modal] Active 10h/wk color: {preset_color}, bg: {preset_bg}")
            
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_modal_light_425.png"))
            
            # Switch to dark theme
            page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
            page.wait_for_timeout(400)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_modal_dark_425.png"))
        else:
            print("Modal title not found.")
            
        # Also capture desktop light mode roadmap page
        desktop_context = browser.new_context(viewport={"width": 1280, "height": 900})
        desktop_page = desktop_context.new_page()
        desktop_page.add_init_script("localStorage.setItem('careermind-theme', 'light');")
        desktop_page.goto("http://localhost:4173/roadmap", wait_until="networkidle")
        desktop_page.evaluate("document.documentElement.classList.remove('dark'); document.documentElement.setAttribute('data-theme', 'light');")
        desktop_page.wait_for_timeout(600)
        desktop_page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_page_light_desktop.png"))

        browser.close()
        
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Done verifying roadmap modal.")

if __name__ == "__main__":
    main()
