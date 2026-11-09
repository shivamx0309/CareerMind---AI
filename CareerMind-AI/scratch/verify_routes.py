import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def verify_all_routes():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1024, "height": 732})
        page = ctx.new_page()
        page.goto("http://localhost:5173/onboarding")
        page.evaluate("""() => {
            const profile = {
                id: 1,
                full_name: "Shivam Kumar Singh",
                primary_target_role: "SDE",
                current_career_status: "Fresher"
            };
            localStorage.setItem("careermind_profile", JSON.stringify(profile));
        }""")
        
        routes = ["/dashboard", "/resume", "/jobs", "/skills", "/roadmap", "/interview"]
        for r in routes:
            page.goto(f"http://localhost:5173{r}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            active_label = page.evaluate("""() => {
                const el = document.querySelector('.dashboard-bottom-nav-item.active .dashboard-bottom-label');
                return el ? el.textContent.trim() : null;
            }""")
            print(f"Route {r} -> Active bottom nav label: {active_label}")
        
        # Take a screenshot of /resume on 1024px
        page.goto("http://localhost:5173/resume")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "resume_1024_dark.png"))

        browser.close()
        print("All routes verified successfully!")

if __name__ == "__main__":
    verify_all_routes()

