import os
import sys
import json
import urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
PDF_PATH = r"CareerMind-AI\sample_data\resumes\sample_resume.pdf"

def upload_and_get_file_id():
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    with open(PDF_PATH, 'rb') as f:
        file_bytes = f.read()

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="sample_resume.pdf"\r\n'
        f'Content-Type: application/pdf\r\n\r\n'
    ).encode('utf-8') + file_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/resumes/upload",
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        return res['file_id']

def setup_page(page, file_id, theme="dark"):
    page.goto("http://localhost:5173/")
    page.evaluate(f"""() => {{
        const profile = {{
            id: 1,
            full_name: "Shivam Kumar Singh",
            primary_target_role: "SDE",
            current_career_status: "Fresher"
        }};
        localStorage.setItem("careermind_profile", JSON.stringify(profile));
        localStorage.setItem("careermind_theme", "{theme}");
        sessionStorage.setItem("careermind_resume_file_id", "{file_id}");
    }}""")
    page.goto("http://localhost:5173/resume")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".resume-section-item", timeout=15000)
    page.wait_for_timeout(1000)

def run_verification():
    file_id = upload_and_get_file_id()
    print(f"Uploaded resume, file_id = {file_id}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # 1. Test Mobile View at 390x844 (iPhone 14)
        # -------------------------------------------------------------
        print("Testing Mobile at 390x844...")
        p_m = browser.new_page(viewport={"width": 390, "height": 844})
        setup_page(p_m, file_id, "dark")

        # Verify mobile pagination elements exist and are visible
        tabs_visible = p_m.evaluate("() => { const el = document.querySelector('.mobile-resume-nav-tabs'); return el && window.getComputedStyle(el).display !== 'none'; }")
        banner_visible = p_m.evaluate("() => { const el = document.querySelector('.mobile-resume-section-banner'); return el && window.getComputedStyle(el).display !== 'none'; }")
        footer_visible = p_m.evaluate("() => { const el = document.querySelector('.mobile-resume-pagination-footer'); return el && window.getComputedStyle(el).display !== 'none'; }")
        print(f"Mobile UI Elements check: tabs={tabs_visible}, banner={banner_visible}, footer={footer_visible}")
        assert tabs_visible and banner_visible and footer_visible, "Mobile pagination controls should be visible on <450px"

        # Capture Section 01 - Profile
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec01_profile.png"))
        print("[Pass] Section 01 captured")

        # Previous should be disabled on Section 01
        prev_disabled = p_m.locator(".mobile-page-btn.prev-btn").is_disabled()
        print(f"Section 01 Previous disabled: {prev_disabled}")
        assert prev_disabled, "Previous button should be disabled on section 01"

        # Advance to Section 02 - Skills
        p_m.locator(".mobile-page-btn.next-btn").click()
        p_m.wait_for_timeout(500)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec02_skills.png"))
        print("[Pass] Section 02 captured")

        # Advance to Section 03 - Experience
        p_m.locator(".mobile-page-btn.next-btn").click()
        p_m.wait_for_timeout(500)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec03_experience.png"))
        print("[Pass] Section 03 captured")

        # Advance to Section 04 - Education
        p_m.locator(".mobile-page-btn.next-btn").click()
        p_m.wait_for_timeout(500)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec04_education.png"))
        print("[Pass] Section 04 captured")

        # Advance to Section 05 - Projects
        p_m.locator(".mobile-page-btn.next-btn").click()
        p_m.wait_for_timeout(500)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec05_projects.png"))
        print("[Pass] Section 05 captured")

        # Advance to Section 06 - Achievements
        p_m.locator(".mobile-page-btn.next-btn").click()
        p_m.wait_for_timeout(500)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec06_achievements.png"))
        print("[Pass] Section 06 captured")

        # Verify Finish button exists on Section 06
        finish_btn_visible = p_m.locator(".mobile-page-btn.finish-btn").is_visible()
        print(f"Section 06 Finish button visible: {finish_btn_visible}")
        assert finish_btn_visible, "Finish button should be visible on section 06"

        # Click Finish -> should return to Section 01 Profile
        p_m.locator(".mobile-page-btn.finish-btn").click()
        p_m.wait_for_timeout(500)
        current_badge = p_m.locator(".section-badge").text_content()
        print(f"After Finish, section badge is: {current_badge}")
        assert "SECTION 01" in current_badge, "Clicking finish should return to Section 01"

        # Direct tab click test: Click Tab 04 (Education)
        p_m.locator(".mobile-resume-tab-btn", has_text="04 Education").click()
        p_m.wait_for_timeout(500)
        current_badge_4 = p_m.locator(".section-badge").text_content()
        print(f"After clicking Tab 04, section badge is: {current_badge_4}")
        assert "SECTION 04" in current_badge_4, "Clicking tab 04 should navigate directly to Section 04"

        # Check light theme on mobile
        p_m.click(".theme-toggle")
        p_m.wait_for_timeout(400)
        p_m.locator(".mobile-resume-tab-btn", has_text="01 Profile").click()
        p_m.wait_for_timeout(500)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_sec01_profile_light.png"))
        print("[Pass] Mobile Light mode Profile captured")
        p_m.close()

        # -------------------------------------------------------------
        # 2. Test Narrow Mobile View at 320px
        # -------------------------------------------------------------
        print("Testing Narrow Mobile at 320x568...")
        p_n = browser.new_page(viewport={"width": 320, "height": 568})
        setup_page(p_n, file_id, "dark")
        p_n.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_320_narrow.png"))
        print("[Pass] Narrow 320px mobile captured")
        p_n.close()

        # -------------------------------------------------------------
        # 3. Test Tablet View at 768x1024 (Regression Check >= 450px)
        # -------------------------------------------------------------
        print("Testing Tablet at 768x1024...")
        p_t = browser.new_page(viewport={"width": 768, "height": 1024})
        setup_page(p_t, file_id, "dark")

        t_tabs_hidden = p_t.evaluate("() => { const el = document.querySelector('.mobile-resume-nav-tabs'); return !el || window.getComputedStyle(el).display === 'none'; }")
        t_all_sections_visible = p_t.evaluate("""() => {
            const items = document.querySelectorAll('.resume-section-item');
            return items.length === 6 && Array.from(items).every(el => window.getComputedStyle(el).display !== 'none');
        }""")
        print(f"Tablet (768px): tabs_hidden={t_tabs_hidden}, all_6_sections_visible={t_all_sections_visible}")
        assert t_tabs_hidden, "Mobile tabs should be hidden on 768px"
        assert t_all_sections_visible, "All 6 sections must be visible continuously on 768px"
        p_t.screenshot(path=os.path.join(ARTIFACT_DIR, "tablet_768_continuous.png"))
        p_t.close()

        # -------------------------------------------------------------
        # 4. Test Desktop View at 1440x900 (Regression Check >= 450px)
        # -------------------------------------------------------------
        print("Testing Desktop at 1440x900...")
        p_d = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page(p_d, file_id, "dark")

        d_tabs_hidden = p_d.evaluate("() => { const el = document.querySelector('.mobile-resume-nav-tabs'); return !el || window.getComputedStyle(el).display === 'none'; }")
        d_all_sections_visible = p_d.evaluate("""() => {
            const items = document.querySelectorAll('.resume-section-item');
            return items.length === 6 && Array.from(items).every(el => window.getComputedStyle(el).display !== 'none');
        }""")
        print(f"Desktop (1440px): tabs_hidden={d_tabs_hidden}, all_6_sections_visible={d_all_sections_visible}")
        assert d_tabs_hidden, "Mobile tabs should be hidden on 1440px desktop"
        assert d_all_sections_visible, "All 6 sections must be visible continuously on 1440px desktop"
        p_d.screenshot(path=os.path.join(ARTIFACT_DIR, "desktop_1440_continuous.png"))
        p_d.close()

        browser.close()
        print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_verification()
