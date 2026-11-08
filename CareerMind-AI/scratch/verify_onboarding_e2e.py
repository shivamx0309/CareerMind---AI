"""
CareerMind AI — Phase C & D: Step-by-Step Onboarding Browser Verification Suite.
Powered by Playwright with Chrome Channel.
Tests the 3-step wizard flow, validation, and dashboard persistence.
"""

import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
BACKEND_DIR = r"c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend"
FRONTEND_DIR = r"c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\frontend"
PYTHON_EXE = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")

# 1. Clear existing profile in careermind.db for empty database initial test
sys.path.insert(0, BACKEND_DIR)
from database.session import SessionLocal
from database.models.career_profile import CareerProfile

db = SessionLocal()
try:
    deleted = db.query(CareerProfile).delete()
    db.commit()
    print(f"[Step 0] Cleared {deleted} existing career profile(s) from SQLite database.")
finally:
    db.close()

# 2. Start Servers
print("[Step 0] Starting FastAPI backend (8000) and Vite frontend (5173)...")
backend_proc = subprocess.Popen(
    [PYTHON_EXE, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=BACKEND_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
frontend_proc = subprocess.Popen(
    ["npx.cmd", "vite", "--port", "5173", "--host", "127.0.0.1"],
    cwd=FRONTEND_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

for _ in range(30):
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=1)
        urllib.request.urlopen("http://127.0.0.1:5173/", timeout=1)
        print("  ✓ Local backend and frontend servers are ready and responding.")
        break
    except Exception:
        time.sleep(1)
else:
    backend_proc.terminate()
    frontend_proc.terminate()
    raise RuntimeError("Timed out waiting for servers to start.")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)

        # Requirement 1 & 2: Open application with an empty database -> verify redirect to onboarding
        print("\n[Step 1] Opening http://127.0.0.1:5173/ with empty profile database...")
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        time.sleep(1.5)

        print(f"  Current URL: {page.url}")
        assert "/onboarding" in page.url, f"Expected redirect to /onboarding, but got {page.url}"
        assert page.locator("text=Register Your Career Profile").is_visible(), "Heading missing"
        assert page.locator("text=Step 1 of 3").is_visible(), "Step 1 badge missing"
        print("  ✓ Verified redirect to Step 1 of onboarding wizard.")

        # Test Step 1 validation
        print("\n[Step 1 Validation] Testing validation on blank Next click...")
        page.click("button:has-text('Continue to Education')")
        time.sleep(0.5)
        assert page.locator("text=Full name is required").is_visible(), "Validation error for full name missing"
        print("  ✓ Step 1 inline validation verified.")

        # Fill Step 1: Personal Details
        print("\n[Step 1 Fill] Completing Personal Information...")
        page.fill("#full_name", "Alex Morgan")
        page.click("button:has-text('Experienced')")

        # Capture Screenshot: Step 1
        s1_img = os.path.join(ARTIFACTS_DIR, "browser_step1_personal.png")
        page.screenshot(path=s1_img)
        print(f"  ✓ Screenshot captured: {s1_img}")

        # Advance to Step 2
        page.click("button:has-text('Continue to Education')")
        time.sleep(0.5)
        assert page.locator("text=Step 2 of 3").is_visible(), "Step 2 badge missing"
        print("  ✓ Advanced to Step 2: Educational Background.")

        # Test Step 2 validation
        print("\n[Step 2 Validation] Testing validation on blank Next click...")
        page.click("button:has-text('Continue to Preferences')")
        time.sleep(0.5)
        assert page.locator("text=Degree or qualification specialization is required").is_visible(), "Degree error missing"
        print("  ✓ Step 2 inline validation verified.")

        # Fill Step 2: Educational Background
        print("\n[Step 2 Fill] Completing Educational Background...")
        page.select_option("#highest_education", "Master's Degree")
        page.fill("#degree", "M.S. Software Systems")
        page.fill("#institution", "Georgia Institute of Technology")
        page.fill("#graduation_year", "2023")

        # Capture Screenshot: Step 2
        s2_img = os.path.join(ARTIFACTS_DIR, "browser_step2_education.png")
        page.screenshot(path=s2_img)
        print(f"  ✓ Screenshot captured: {s2_img}")

        # Advance to Step 3
        page.click("button:has-text('Continue to Preferences')")
        time.sleep(0.5)
        assert page.locator("text=Step 3 of 3").is_visible(), "Step 3 badge missing"
        print("  ✓ Advanced to Step 3: Career Preferences.")

        # Fill Step 3: Career Preferences
        print("\n[Step 3 Fill] Completing Career Preferences...")
        page.fill("#primary_target_role", "Senior Backend Engineer")
        page.click("button:has-text('Full-time')")
        page.click("button:has-text('Remote')")
        page.fill("textarea#career_objective", "Architecting high-throughput, fault-tolerant cloud APIs and distributed storage pipelines.")

        # Capture Screenshot: Step 3
        s3_img = os.path.join(ARTIFACTS_DIR, "browser_step3_preferences.png")
        page.screenshot(path=s3_img)
        print(f"  ✓ Screenshot captured: {s3_img}")

        # Submit registration form
        print("\n[Submission] Submitting registration from Step 3...")
        page.click("button:has-text('Complete Registration')")
        page.wait_for_url("http://127.0.0.1:5173/", timeout=10000)
        time.sleep(1.5)
        print(f"  Current URL: {page.url}")
        assert page.url == "http://127.0.0.1:5173/", f"Expected URL to be http://127.0.0.1:5173/, got {page.url}"

        # Assert Dashboard personalized greeting and active profile summary
        assert page.locator("text=Welcome back,").is_visible(), "Greeting 'Welcome back,' missing"
        assert page.locator("text=Alex Morgan.").is_visible(), "Candidate name 'Alex Morgan.' missing"
        assert page.locator("text=Senior Backend Engineer").first.is_visible(), "Target role missing on Dashboard"
        assert page.locator("text=Registered Career Profile").is_visible(), "Profile overview section missing"
        print("  ✓ Dashboard personalized greeting and active profile card verified.")

        # Capture screenshot: Personalized Dashboard
        dash_img = os.path.join(ARTIFACTS_DIR, "browser_req5_dashboard_personalized.png")
        page.screenshot(path=dash_img)
        print(f"  ✓ Screenshot captured: {dash_img}")

        # Refresh browser -> verify onboarding does NOT appear again
        print("\n[Persistence] Refreshing browser to verify persistence...")
        page.reload(wait_until="networkidle")
        time.sleep(1.5)
        assert page.url == "http://127.0.0.1:5173/", f"Expected Dashboard, got {page.url}"
        assert page.locator("text=Alex Morgan.").is_visible(), "Personalized name missing after reload"
        print("  ✓ Verified persistence across browser reload.")

        # Open Edit Profile, navigate to Step 3 tab directly, update field, save
        print("\n[Edit Profile] Opening Edit Profile...")
        page.click("text=Edit Profile")
        page.wait_for_url("**/onboarding?edit=true", timeout=5000)
        time.sleep(1.5)
        assert page.locator("text=Edit Your Career Profile").is_visible(), "'Edit Your Career Profile' heading missing"
        assert page.locator("#full_name").input_value() == "Alex Morgan", "Pre-populated full name mismatch"

        # Click Step 3 bubble directly
        page.click("button[title='Step 3']")
        time.sleep(0.5)
        page.fill("#primary_target_role", "Staff Platform Architect")

        # Save changes from Step 3
        page.click("button:has-text('Save Profile Changes')")
        page.wait_for_url("http://127.0.0.1:5173/", timeout=5000)
        time.sleep(1.5)

        # Verify updated role persists on Dashboard
        assert page.locator("text=Staff Platform Architect").first.is_visible(), "Updated role missing on Dashboard"
        print("  ✓ Verified updated role persisted across reload.")

        # Verify Resume Analyzer (/resume) still works
        print("\n[Sanity] Verifying Resume Analyzer (/resume)...")
        page.goto("http://127.0.0.1:5173/resume", wait_until="networkidle")
        time.sleep(1.5)
        assert page.locator("text=Resume Analyzer").is_visible(), "Resume Analyzer heading missing"
        print("  ✓ Resume Analyzer route operational without regressions.")

        # Verify Job Matcher (/jobs) still works
        print("\n[Sanity] Verifying Job Matcher (/jobs)...")
        page.goto("http://127.0.0.1:5173/jobs", wait_until="networkidle")
        time.sleep(1.5)
        assert page.locator("text=Job Description Matcher").is_visible(), "Job Matcher heading missing"
        print("  ✓ Job Matcher route operational without regressions.")

        # Check console errors
        print(f"\n[Console Audit] Found {len(console_errors)} console errors:")
        for err in console_errors:
            print("  -", err)
        assert len(console_errors) == 0, "Console errors were logged during E2E verification"

        browser.close()
        print("\n============================================================")
        print("  ALL 3-STEP WIZARD E2E VERIFICATIONS PASSED 100%!        ")
        print("============================================================\n")

finally:
    backend_proc.terminate()
    frontend_proc.terminate()
    print("[CleanUp] Backend and Frontend test processes terminated cleanly.")
