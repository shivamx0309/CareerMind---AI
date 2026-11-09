import sys
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={'width': 375, 'height': 667})
        page = context.new_page()
        page.goto('http://localhost:5173')
        page.wait_for_timeout(1000)
        page.locator('#features').scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        next_btn = page.locator('button[aria-label="Next feature"]')
        for i in range(5):
            h3 = page.locator('#features h3').inner_text()
            scroll_x = page.evaluate('window.scrollX')
            cnt_scroll = page.evaluate('document.querySelector(".landing-page-container") ? document.querySelector(".landing-page-container").scrollLeft : 0')
            body_scroll = page.evaluate('document.body.scrollLeft')
            doc_scroll = page.evaluate('document.documentElement.scrollLeft')
            card_box = page.locator('#features h3').bounding_box()
            print(f'Step {i}: {h3} | winX={scroll_x} | cntX={cnt_scroll} | bodyX={body_scroll} | docX={doc_scroll} | card_x={round(card_box["x"], 1) if card_box else None}', flush=True)
            next_btn.click()
            page.wait_for_timeout(600)
        browser.close()

if __name__ == '__main__':
    test()
