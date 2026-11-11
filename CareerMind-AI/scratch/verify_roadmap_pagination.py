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
            
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        
        page.add_init_script("localStorage.setItem('careermind-theme', 'light');")
        page.goto("http://localhost:4173/roadmap", wait_until="networkidle")
        page.evaluate("document.documentElement.classList.remove('dark'); document.documentElement.setAttribute('data-theme', 'light');")
        page.wait_for_timeout(600)
        
        # Test 1: Weekly Schedule View
        page.locator("button:has-text('Weekly Schedule')").click()
        page.wait_for_timeout(400)
        page.locator("#weekly-timeline-section").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_pagination_timeline_page1.png"))
        
        # Check weekly timeline pagination text
        timeline_pag = page.locator("#weekly-timeline-section nav[aria-label='Pagination for weeks']")
        if timeline_pag.is_visible():
            text = timeline_pag.inner_text()
            print(f"Weekly timeline pagination text: {repr(text)}")
            
            # Click Next
            timeline_pag.locator("button:has-text('Next')").click()
            page.wait_for_timeout(400)
            timeline_pag.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_pagination_timeline_page2.png"))
            print("Successfully paged to Next week chunk!")
        else:
            print("Timeline pagination not visible (maybe totalWeeks <= 3)")
            
        # Test 2: Skill Modules View
        page.locator("button:has-text('Skill Modules')").click()
        page.wait_for_timeout(400)
        page.locator("#skill-modules-section").scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_pagination_skills_page1.png"))
        
        skills_pag = page.locator("#skill-modules-section nav[aria-label='Pagination for modules']")
        if skills_pag.is_visible():
            text = skills_pag.inner_text()
            print(f"Skill modules pagination text: {repr(text)}")
            
            # Click Page 2
            skills_pag.locator("button:has-text('2')").click()
            page.wait_for_timeout(400)
            skills_pag.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "roadmap_pagination_skills_page2.png"))
            print("Successfully paged to Skill Modules Page 2!")
        else:
            print("Skills pagination not visible (maybe totalSkills <= 3)")
            
        browser.close()
        
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Done verifying roadmap pagination.")

if __name__ == "__main__":
    main()
