import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity\brain\1b5df970-b463-4980-ad64-e56d270f5cd6"

def verify_alignment():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 800})
        page = ctx.new_page()
        page.goto("http://localhost:5173/onboarding")
        page.evaluate("""() => {
            const profile = { id: 1, full_name: "Shivam Kumar Singh", primary_target_role: "SDE" };
            localStorage.setItem("careermind_profile", JSON.stringify(profile));
            localStorage.setItem("careermind_theme", "dark");
        }""")
        page.goto("http://localhost:5173/dashboard")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # 1. Dark full desktop screenshot
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "border_alignment_dark_full.png"))

        # 2. Crop top seam (y: 0 to 120, x: 200 to 350)
        page.screenshot(
            path=os.path.join(ARTIFACT_DIR, "border_alignment_dark_seam.png"),
            clip={"x": 200, "y": 0, "width": 200, "height": 100}
        )

        # 3. Test collapsed sidebar alignment
        page.locator(".collapse-button").click()
        page.wait_for_timeout(400)
        sb_collapsed = page.evaluate("() => document.querySelector('.sidebar-brand').getBoundingClientRect()")
        tb = page.evaluate("() => document.querySelector('.topbar').getBoundingClientRect()")
        print(f"Collapsed -> sidebar-brand height: {sb_collapsed['height']}, topbar height: {tb['height']}")
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "border_alignment_collapsed_dark.png"))

        # 4. Expand again and test Light theme
        page.locator(".collapse-button").click()
        page.wait_for_timeout(400)
        page.locator(".theme-toggle").click()
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "border_alignment_light_full.png"))
        page.screenshot(
            path=os.path.join(ARTIFACT_DIR, "border_alignment_light_seam.png"),
            clip={"x": 200, "y": 0, "width": 200, "height": 100}
        )

        browser.close()
        print("All border alignment tests completed!")

if __name__ == "__main__":
    verify_alignment()

