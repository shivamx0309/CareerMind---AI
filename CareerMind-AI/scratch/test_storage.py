from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5173/")
        page.evaluate("""() => {
            sessionStorage.setItem('test_key', '12345');
        }""")
        page.goto("http://localhost:5173/resume")
        val = page.evaluate("() => sessionStorage.getItem('test_key')")
        print("test_key in page after navigation:", val)
        browser.close()

if __name__ == "__main__":
    test()
