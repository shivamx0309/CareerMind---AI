from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 425, "height": 962})
    page.goto("http://localhost:5173/onboarding?edit=true", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    page.screenshot(path="C:/Users/ASUS/.gemini/antigravity/brain/1b5df970-b463-4980-ad64-e56d270f5cd6/scratch_onboarding_mobile.png")
    print("Screenshot saved to scratch_onboarding_mobile.png")
    browser.close()
