import json
import urllib.request
from playwright.sync_api import sync_playwright

PDF_PATH = r"CareerMind-AI\sample_data\resumes\sample_resume.pdf"

def diag():
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
        file_id = res['file_id']
    print("file_id:", file_id)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        ctx.add_init_script(f"""() => {{
            localStorage.setItem("careermind_profile", JSON.stringify({{ id: 1, full_name: "Shivam" }}));
            sessionStorage.setItem("careermind_resume_file_id", "{file_id}");
        }}""")
        page = ctx.new_page()
        page.on("console", lambda msg: print("CONSOLE:", msg.text))
        page.on("pageerror", lambda err: print("PAGEERROR:", err))
        page.goto("http://localhost:5173/resume")
        page.wait_for_timeout(3000)
        print("Page URL:", page.url)
        content_html = page.content()
        print("Has resume-section-item:", "resume-section-item" in content_html)
        print("Status text on page:", page.evaluate("() => document.body.innerText.slice(0, 500)"))
        browser.close()

if __name__ == "__main__":
    diag()

