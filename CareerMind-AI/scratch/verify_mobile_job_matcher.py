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

def setup_and_match(page, file_id, theme="dark"):
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
    page.goto("http://localhost:5173/jobs")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)

    # Click sample JD: Python Backend Developer
    sample_btn = page.locator("button", has_text="Python Backend Developer")
    if sample_btn.is_visible():
        sample_btn.click()
        page.wait_for_timeout(300)

    # Click Run Match Engine
    submit_btn = page.locator("button[type='submit']")
    submit_btn.click()

    # Wait for results to load
    page.wait_for_selector(".job-match-tab-panel", timeout=20000)
    page.wait_for_timeout(1000)

def verify():
    file_id = upload_and_get_file_id()
    print(f"Uploaded resume, file_id = {file_id}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # 1. Test Mobile View at 390x844 (iPhone 14)
        # -------------------------------------------------------------
        print("Testing Mobile at 390x844...")
        p_m = browser.new_page(viewport={"width": 390, "height": 844})
        
        # Track network calls to ensure tab clicks don't call /jobs/match
        match_call_count = [0]
        def handle_request(req):
            if "/jobs/match" in req.url:
                match_call_count[0] += 1
                print(f"--> [Network] /jobs/match called! Total = {match_call_count[0]}")
        p_m.on("request", handle_request)

        setup_and_match(p_m, file_id, "dark")
        initial_api_calls = match_call_count[0]
        print(f"Initial API calls after matching: {initial_api_calls}")

        # Check mobile tabs are visible
        tabs_visible = p_m.evaluate("() => { const el = document.querySelector('.mobile-job-tabs-container'); return el && window.getComputedStyle(el).display !== 'none'; }")
        print(f"Mobile tabs container visible: {tabs_visible}")
        assert tabs_visible, "Mobile tabs container should be visible on <450px"

        # Check NO progress bars on mobile
        progress_elements = p_m.evaluate("""() => {
            const bars = document.querySelectorAll('.section-progress-track, .section-progress-fill, progress, [role="progressbar"]');
            return bars.length;
        }""")
        print(f"New progress bar elements found: {progress_elements}")
        assert progress_elements == 0, "Strict visual requirement: Absolutely NO progress bars allowed!"

        # Check all 5 tab buttons exist
        tab_labels = p_m.evaluate("() => Array.from(document.querySelectorAll('.mobile-job-tab-label')).map(el => el.textContent.trim())")
        print(f"5 Mobile Tabs found: {tab_labels}")
        expected_tabs = ['Overview', 'Skills', 'Experience', 'Education', 'Roadmap']
        assert tab_labels == expected_tabs, f"Expected {expected_tabs}, found {tab_labels}"

        # Check Form is collapsed by default
        form_visible = p_m.locator("#job-description-form-section").is_visible()
        print(f"Job Description Form visible after match: {form_visible} (expected False/collapsed)")
        assert not form_visible, "Form should be collapsed by default after match"

        # Test Show / Hide toggle
        toggle_btn = p_m.locator("button", has_text="Show Job Description")
        assert toggle_btn.is_visible(), "Show Job Description button should be visible"
        toggle_btn.click()
        p_m.wait_for_timeout(300)
        assert p_m.locator("#job-description-form-section").is_visible(), "Form should expand on click"
        hide_btn = p_m.locator("button", has_text="Hide Job Description")
        assert hide_btn.is_visible(), "Button should change to Hide Job Description"
        hide_btn.click()
        p_m.wait_for_timeout(300)
        assert not p_m.locator("#job-description-form-section").is_visible(), "Form should collapse on click"

        # -------------------------------------------------------------
        # Capture and verify each tab
        # -------------------------------------------------------------
        # Tab 1: Overview
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tab1_overview.png"))
        print("[Pass] Tab 1: Overview captured")

        # Tab 2: Skills
        p_m.locator(".mobile-job-tab-btn", has_text="Skills").click()
        p_m.wait_for_timeout(400)
        assert match_call_count[0] == initial_api_calls, "Tab switch must NOT trigger API request"
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tab2_skills.png"))
        print("[Pass] Tab 2: Skills captured")

        # Tab 3: Experience
        p_m.locator(".mobile-job-tab-btn", has_text="Experience").click()
        p_m.wait_for_timeout(400)
        assert match_call_count[0] == initial_api_calls, "Tab switch must NOT trigger API request"
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tab3_experience.png"))
        print("[Pass] Tab 3: Experience captured")

        # Tab 4: Education
        p_m.locator(".mobile-job-tab-btn", has_text="Education").click()
        p_m.wait_for_timeout(400)
        assert match_call_count[0] == initial_api_calls, "Tab switch must NOT trigger API request"
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tab4_education.png"))
        print("[Pass] Tab 4: Education captured")

        # Tab 5: Roadmap
        p_m.locator(".mobile-job-tab-btn", has_text="Roadmap").click()
        p_m.wait_for_timeout(400)
        assert match_call_count[0] == initial_api_calls, "Tab switch must NOT trigger API request"
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tab5_roadmap.png"))
        print("[Pass] Tab 5: Roadmap captured")

        # Light theme test
        p_m.click(".theme-toggle")
        p_m.wait_for_timeout(300)
        p_m.locator(".mobile-job-tab-btn", has_text="Overview").click()
        p_m.wait_for_timeout(400)
        p_m.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tab1_overview_light.png"))
        print("[Pass] Mobile Light theme captured")
        p_m.close()

        # -------------------------------------------------------------
        # 2. Test other mobile widths: 320px, 375px, 425px
        # -------------------------------------------------------------
        for w in [320, 375, 425]:
            print(f"Testing Mobile at {w}px width...")
            p_w = browser.new_page(viewport={"width": w, "height": 750})
            setup_and_match(p_w, file_id, "dark")
            p_w.screenshot(path=os.path.join(ARTIFACT_DIR, f"job_matcher_{w}px.png"))
            print(f"[Pass] {w}px mobile captured")
            p_w.close()

        # -------------------------------------------------------------
        # 3. Test Tablet View at 768px (Regression Check >= 450px)
        # -------------------------------------------------------------
        print("Testing Tablet at 768x1024...")
        p_t = browser.new_page(viewport={"width": 768, "height": 1024})
        setup_and_match(p_t, file_id, "dark")
        t_tabs_hidden = p_t.evaluate("() => { const el = document.querySelector('.mobile-job-tabs-container'); return !el || window.getComputedStyle(el).display === 'none'; }")
        t_all_panels_visible = p_t.evaluate("""() => {
            const panels = document.querySelectorAll('.job-match-tab-panel');
            return panels.length === 5 && Array.from(panels).every(el => window.getComputedStyle(el).display !== 'none');
        }""")
        print(f"Tablet (768px): tabs_hidden={t_tabs_hidden}, all_panels_visible={t_all_panels_visible}")
        assert t_tabs_hidden, "Mobile tabs should be hidden on 768px"
        assert t_all_panels_visible, "All 5 panels should be visible continuously on 768px"
        p_t.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_tablet_768_continuous.png"))
        p_t.close()

        # -------------------------------------------------------------
        # 4. Test Desktop View at 1440x900 (Regression Check >= 450px)
        # -------------------------------------------------------------
        print("Testing Desktop at 1440x900...")
        p_d = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_and_match(p_d, file_id, "dark")
        d_tabs_hidden = p_d.evaluate("() => { const el = document.querySelector('.mobile-job-tabs-container'); return !el || window.getComputedStyle(el).display === 'none'; }")
        d_all_panels_visible = p_d.evaluate("""() => {
            const panels = document.querySelectorAll('.job-match-tab-panel');
            return panels.length === 5 && Array.from(panels).every(el => window.getComputedStyle(el).display !== 'none');
        }""")
        print(f"Desktop (1440px): tabs_hidden={d_tabs_hidden}, all_panels_visible={d_all_panels_visible}")
        assert d_tabs_hidden, "Mobile tabs should be hidden on 1440px"
        assert d_all_panels_visible, "All 5 panels should be visible continuously on 1440px"
        p_d.screenshot(path=os.path.join(ARTIFACT_DIR, "job_matcher_desktop_1440_continuous.png"))
        p_d.close()

        browser.close()
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    verify()
