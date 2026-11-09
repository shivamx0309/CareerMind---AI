import os
from playwright.sync_api import sync_playwright

def inspect():
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
        page.goto("http://localhost:5173/resume")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        items = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.dashboard-bottom-nav-item')).map(el => ({
                href: el.getAttribute('href'),
                className: el.className,
                text: el.textContent.trim()
            }));
        }""")
        print("Items on /resume:", items)
        browser.close()

if __name__ == "__main__":
    inspect()

