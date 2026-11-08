import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"
BASE_URL = "http://localhost:5173"

def run_tests():
    print(f"Connecting to {BASE_URL} to test Interactive Feature Swapping...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1)

        # Scroll to Features Section
        features_sec = page.locator("#features")
        features_sec.scroll_into_view_if_needed()
        time.sleep(0.8)

        # -------------------------------------------------------------
        # STEP 1: Initial State Verification
        # -------------------------------------------------------------
        print("\n--- Step 1: Initial State ---")
        large_heading = page.locator("#features .lg\\:col-span-5 h3")
        assert large_heading.text_content().strip() == "Resume Intelligence"
        print(f"[Pass] Initial Featured Card: {large_heading.text_content().strip()}")

        small_titles = page.locator("#features .lg\\:col-span-7 h4").all_text_contents()
        print(f"[Pass] Initial 4 Small Cards: {small_titles}")
        assert small_titles == [
            "Job Description Matching",
            "Skill Gap Analysis",
            "Learning Path",
            "Career Insights",
        ]

        page.screenshot(path=os.path.join(ARTIFACT_DIR, "feature_swap_1_initial.png"))
        print("[Pass] Saved feature_swap_1_initial.png")

        # -------------------------------------------------------------
        # STEP 2: Click 'Skill Gap Analysis' (Index 1)
        # -------------------------------------------------------------
        print("\n--- Step 2: Click 'Skill Gap Analysis' ---")
        page.locator("#features .lg\\:col-span-7 h4:has-text('Skill Gap Analysis')").click()
        time.sleep(0.6)

        # Featured card must now be 'Skill Gap Analysis'
        large_heading = page.locator("#features .lg\\:col-span-5 h3")
        assert large_heading.text_content().strip() == "Skill Gap Analysis"
        print(f"[Pass] New Featured Card: {large_heading.text_content().strip()}")

        # Position 1 in small grid must now be 'Resume Intelligence'
        small_titles = page.locator("#features .lg\\:col-span-7 h4").all_text_contents()
        print(f"[Pass] Updated 4 Small Cards: {small_titles}")
        assert small_titles[0] == "Job Description Matching"
        assert small_titles[1] == "Resume Intelligence"  # Swapped into exact position!
        assert small_titles[2] == "Learning Path"
        assert small_titles[3] == "Career Insights"

        page.screenshot(path=os.path.join(ARTIFACT_DIR, "feature_swap_2_skill_gap.png"))
        print("[Pass] Saved feature_swap_2_skill_gap.png")

        # -------------------------------------------------------------
        # STEP 3: Click 'Career Insights' (Index 3)
        # -------------------------------------------------------------
        print("\n--- Step 3: Click 'Career Insights' ---")
        page.locator("#features .lg\\:col-span-7 h4:has-text('Career Insights')").click()
        time.sleep(0.6)

        large_heading = page.locator("#features .lg\\:col-span-5 h3")
        assert large_heading.text_content().strip() == "Career Insights"
        print(f"[Pass] New Featured Card: {large_heading.text_content().strip()}")

        small_titles = page.locator("#features .lg\\:col-span-7 h4").all_text_contents()
        print(f"[Pass] Updated 4 Small Cards: {small_titles}")
        assert small_titles[0] == "Job Description Matching"
        assert small_titles[1] == "Resume Intelligence"
        assert small_titles[2] == "Learning Path"
        assert small_titles[3] == "Skill Gap Analysis"  # Swapped into exact position 3!

        page.screenshot(path=os.path.join(ARTIFACT_DIR, "feature_swap_3_career_insights.png"))
        print("[Pass] Saved feature_swap_3_career_insights.png")

        # -------------------------------------------------------------
        # STEP 4: Click 'Job Description Matching' (Index 0)
        # -------------------------------------------------------------
        print("\n--- Step 4: Click 'Job Description Matching' ---")
        page.locator("#features .lg\\:col-span-7 h4:has-text('Job Description Matching')").click()
        time.sleep(0.6)

        large_heading = page.locator("#features .lg\\:col-span-5 h3")
        assert large_heading.text_content().strip() == "Job Description Matching"
        print(f"[Pass] New Featured Card: {large_heading.text_content().strip()}")

        small_titles = page.locator("#features .lg\\:col-span-7 h4").all_text_contents()
        print(f"[Pass] Updated 4 Small Cards: {small_titles}")
        assert small_titles[0] == "Career Insights"  # Swapped into exact position 0!
        assert small_titles[1] == "Resume Intelligence"
        assert small_titles[2] == "Learning Path"
        assert small_titles[3] == "Skill Gap Analysis"

        page.screenshot(path=os.path.join(ARTIFACT_DIR, "feature_swap_4_jobs.png"))
        print("[Pass] Saved feature_swap_4_jobs.png")

        # -------------------------------------------------------------
        # STEP 5: Verify Bottom Trust Indicators Bar
        # -------------------------------------------------------------
        print("\n--- Step 5: Trust Indicators Bar ---")
        trust_bar = page.locator("#features").get_by_text("Local-First & Private")
        assert trust_bar.is_visible()
        explain_bar = page.locator("#features").get_by_text("Explainable Scoring Engine")
        assert explain_bar.is_visible()
        llm_bar = page.locator("#features").get_by_text("Zero External LLM APIs")
        assert llm_bar.is_visible()
        print("[Pass] All 3 trust indicators are visible in bottom bar")

        # -------------------------------------------------------------
        # STEP 6: Mobile & Tablet Verification
        # -------------------------------------------------------------
        print("\n--- Step 6: Responsive Views ---")
        # Tablet (768 x 1024)
        page.set_viewport_size({"width": 768, "height": 1024})
        time.sleep(0.5)
        features_sec.scroll_into_view_if_needed()
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "feature_swap_tablet.png"))
        print("[Pass] Saved feature_swap_tablet.png")

        # Mobile (390 x 844)
        page.set_viewport_size({"width": 390, "height": 844})
        time.sleep(0.5)
        features_sec.scroll_into_view_if_needed()
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "feature_swap_mobile.png"))
        print("[Pass] Saved feature_swap_mobile.png")

        page.close()
        browser.close()
        print("\n=======================================================")
        print("🎉 ALL FEATURE SWAP INTERACTION TESTS PASSED 100%!")
        print("=======================================================")

if __name__ == "__main__":
    run_tests()
