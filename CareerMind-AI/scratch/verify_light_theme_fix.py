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

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 950})

        # Mock rich candidate matching user screenshot
        def handle_parse(route):
            mock_data = {
                "success": True,
                "file_id": "76385936000000000000000000876bb4",
                "candidate": {
                    "personal_information": {
                        "full_name": "Shivam Kumar Singh",
                        "email": "edu.shivam0903@gmail.com",
                        "phone": "+918887602317",
                        "linkedin": "https://linkedin.com/in/shivam",
                        "github": "https://github.com/shivam",
                        "location": None
                    },
                    "professional_summary": "Computer Science Engineering student skilled in SQL, Python, Excel, Power BI, and Data Analytics.",
                    "technical_skills": {
                        "programming_languages": ["Python", "SQL", "Java"],
                        "frontend": [],
                        "backend": [],
                        "databases": ["PostgreSQL", "MySQL", "Supabase"],
                        "data_analytics": ["Pandas", "NumPy", "Data Analytics", "Data Cleaning", "Power BI", "Excel", "Data Visualization"],
                        "machine_learning": ["Scikit-learn", "Regression", "Classification", "Logistic Regression"],
                        "deep_learning": [],
                        "cloud_devops": [],
                        "tools": ["Git", "GitHub", "VS Code", "Jupyter Notebook"],
                        "other": ["Data Preprocessing", "KPI Dashboards", "Reporting", "Joins", "CTEs", "Window Functions", "Subqueries", "Aggregations"]
                    },
                    "education": [],
                    "experience": [],
                    "projects": [],
                    "certifications": [],
                    "achievements": []
                }
            }
            route.fulfill(status=200, content_type="application/json", body=json.dumps(mock_data))

        page.route("**/api/v1/resumes/*/parse", handle_parse)

        # Set up profile and light theme
        page.goto("http://localhost:5173/")
        page.evaluate("""() => {
            const profile = {
                id: 1,
                full_name: "Shivam Kumar Singh",
                primary_target_role: "SDE",
                current_career_status: "Fresher"
            };
            localStorage.setItem("careermind_profile", JSON.stringify(profile));
            localStorage.setItem("careermind-theme", "light");
            sessionStorage.setItem("careermind_resume_file_id", "76385936000000000000000000876bb4");
        }""")

        # Navigate to Resume Analyzer in Light Mode
        print("Navigating to /resume in Light Mode with user dataset...")
        page.goto("http://localhost:5173/resume")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector(".glass-card", timeout=15000)
        page.wait_for_timeout(1000)

        # Screenshot Profile Card & Header
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "light_theme_resume_header.png"))
        print("[Pass] Saved light_theme_resume_header.png")

        # Scroll to Skills section and capture full skills grid
        page.evaluate("() => { const el = document.querySelector('h3'); const skills = Array.from(document.querySelectorAll('h3')).find(h => h.textContent.includes('Technical Skills')); if (skills) skills.scrollIntoView({ behavior: 'instant', block: 'start' }); }")
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "light_theme_skills_overview.png"))
        print("[Pass] Saved light_theme_skills_overview.png")

        # Switch to Dark Mode to verify regression
        print("Switching to Dark Mode to verify regression...")
        page.locator(".theme-toggle").click()
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "dark_theme_skills_overview.png"))
        print("[Pass] Saved dark_theme_skills_overview.png")

        browser.close()
        print("All visual verification tests completed successfully!")

if __name__ == "__main__":
    verify()
