from playwright.sync_api import sync_playwright

def check():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page.goto("http://localhost:5173/onboarding")
        page.evaluate("""() => {
            const profile = { id: 1, full_name: "Shivam Kumar Singh", primary_target_role: "SDE" };
            localStorage.setItem("careermind_profile", JSON.stringify(profile));
        }""")
        page.goto("http://localhost:5173/dashboard")
        page.wait_for_load_state("networkidle")

        sb = page.evaluate("() => document.querySelector('.sidebar-brand').getBoundingClientRect()")
        tb = page.evaluate("() => document.querySelector('.topbar').getBoundingClientRect()")
        print(f"sidebar-brand: top={sb['top']}, height={sb['height']}, bottom={sb['bottom']}")
        print(f"topbar: top={tb['top']}, height={tb['height']}, bottom={tb['bottom']}")
        browser.close()

if __name__ == "__main__":
    check()

