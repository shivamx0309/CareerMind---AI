import os
from playwright.sync_api import sync_playwright

def test_nav():
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
        page.goto("http://localhost:5173/dashboard")
        page.wait_for_load_state("networkidle")
        
        # Click Resume
        page.locator(".dashboard-bottom-nav-item", has_text="Resume").click()
        page.wait_for_load_state("networkidle")
        print("URL after Resume click:", page.url)
        assert "/resume" in page.url

        # Check that Resume item is active
        is_resume_active = page.evaluate("""() => {
            const el = Array.from(document.querySelectorAll('.dashboard-bottom-nav-item')).find(x => x.textContent.includes('Resume'));
            return el && el.classList.contains('active');
        }""")
        print("Is Resume item active:", is_resume_active)
        assert is_resume_active, "Resume item should have .active class"

        # Click Jobs
        page.locator(".dashboard-bottom-nav-item", has_text="Jobs").click()
        page.wait_for_load_state("networkidle")
        print("URL after Jobs click:", page.url)
        assert "/jobs" in page.url

        # Click Dashboard
        page.locator(".dashboard-bottom-nav-item", has_text="Dashboard").click()
        page.wait_for_load_state("networkidle")
        print("URL after Dashboard click:", page.url)
        assert "/dashboard" in page.url

        browser.close()
        print("Navigation test passed successfully!")

if __name__ == "__main__":
    test_nav()

