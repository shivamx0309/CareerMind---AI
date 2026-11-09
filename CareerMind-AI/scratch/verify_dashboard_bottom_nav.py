import os
import sys
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # First ensure user has completed onboarding profile in localStorage
        init_context = browser.new_context()
        page = init_context.new_page()
        page.goto("http://localhost:5173/onboarding")
        page.evaluate("""() => {
            const profile = {
                id: 1,
                full_name: "Shivam Kumar Singh",
                primary_target_role: "SDE",
                current_career_status: "Fresher",
                target_locations: "On-site",
                target_role_domain: "CSE",
                highest_education: "B.Tech",
                primary_discipline: "CSE",
                job_search_urgency: "Immediate",
                preferred_job_type: "Full-time"
            };
            localStorage.setItem("careermind_profile", JSON.stringify(profile));
            localStorage.setItem("careermind_theme", "dark");
        }""")
        init_context.close()

        # 1. Test at 1024x732 (Exact User's DevTools screenshot)
        print("Testing at 1024x732...")
        ctx_1024 = browser.new_context(viewport={"width": 1024, "height": 732})
        p_1024 = ctx_1024.new_page()
        p_1024.goto("http://localhost:5173/dashboard")
        p_1024.wait_for_load_state("networkidle")
        p_1024.wait_for_timeout(1000)

        # Check visibility
        sidebar_hidden = p_1024.evaluate("() => { const s = document.querySelector('.sidebar'); return !s || window.getComputedStyle(s).display === 'none'; }")
        bottom_nav_visible = p_1024.evaluate("() => { const b = document.querySelector('.dashboard-bottom-nav'); return b && window.getComputedStyle(b).display !== 'none'; }")
        nav_items_count = p_1024.evaluate("() => document.querySelectorAll('.dashboard-bottom-nav-item').length")
        nav_labels = p_1024.evaluate("() => Array.from(document.querySelectorAll('.dashboard-bottom-label')).map(el => el.textContent.trim())")

        print(f"1024px: sidebar_hidden={sidebar_hidden}, bottom_nav_visible={bottom_nav_visible}, items={nav_items_count}, labels={nav_labels}")
        p_1024.screenshot(path=os.path.join(ARTIFACT_DIR, "dashboard_1024_dark.png"), full_page=False)

        # 2. Test in Light Mode at 1024x732
        p_1024.click(".theme-toggle")
        p_1024.wait_for_timeout(500)
        p_1024.screenshot(path=os.path.join(ARTIFACT_DIR, "dashboard_1024_light.png"), full_page=False)
        ctx_1024.close()

        # 3. Test on Mobile at 390x844
        print("Testing at 390x844...")
        ctx_mobile = browser.new_context(viewport={"width": 390, "height": 844})
        p_mobile = ctx_mobile.new_page()
        p_mobile.goto("http://localhost:5173/dashboard")
        p_mobile.wait_for_load_state("networkidle")
        p_mobile.wait_for_timeout(1000)

        mobile_nav_visible = p_mobile.evaluate("() => { const b = document.querySelector('.dashboard-bottom-nav'); return b && window.getComputedStyle(b).display !== 'none'; }")
        print(f"390px: mobile_nav_visible={mobile_nav_visible}")
        p_mobile.screenshot(path=os.path.join(ARTIFACT_DIR, "dashboard_390_dark.png"), full_page=False)

        # Scroll down in .dashboard-content to ensure content doesn't get covered by bottom nav
        p_mobile.evaluate("() => { const c = document.querySelector('.dashboard-content'); if (c) c.scrollTop = c.scrollHeight; }")
        p_mobile.wait_for_timeout(500)
        p_mobile.screenshot(path=os.path.join(ARTIFACT_DIR, "dashboard_390_dark_scrolled.png"), full_page=False)
        ctx_mobile.close()

        # 4. Test on Desktop at 1280x800
        print("Testing at 1280x800 (Desktop)...")
        ctx_desktop = browser.new_context(viewport={"width": 1280, "height": 800})
        p_desktop = ctx_desktop.new_page()
        p_desktop.goto("http://localhost:5173/dashboard")
        p_desktop.wait_for_load_state("networkidle")
        p_desktop.wait_for_timeout(1000)

        desktop_sidebar_visible = p_desktop.evaluate("() => { const s = document.querySelector('.sidebar'); return s && window.getComputedStyle(s).display !== 'none'; }")
        desktop_bottom_nav_hidden = p_desktop.evaluate("() => { const b = document.querySelector('.dashboard-bottom-nav'); return !b || window.getComputedStyle(b).display === 'none'; }")
        print(f"1280px Desktop: desktop_sidebar_visible={desktop_sidebar_visible}, desktop_bottom_nav_hidden={desktop_bottom_nav_hidden}")
        p_desktop.screenshot(path=os.path.join(ARTIFACT_DIR, "dashboard_1280_desktop.png"), full_page=False)
        ctx_desktop.close()

        browser.close()
        print("Verification complete!")

if __name__ == "__main__":
    verify()
