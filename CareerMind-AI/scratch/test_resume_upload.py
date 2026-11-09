import urllib.request
import urllib.parse
import json

def test_api():
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    with open('CareerMind-AI/sample_data/resumes/sample_resume.pdf', 'rb') as f:
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
        print("Upload:", res)
        file_id = res['file_id']

    req2 = urllib.request.Request(
        f"http://127.0.0.1:8000/api/v1/resumes/{file_id}/parse",
        data=b'',
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req2) as resp2:
        res2 = json.loads(resp2.read().decode())
        cand = res2.get('candidate', {})
        print("Candidate Name:", cand.get('personal_information', {}).get('full_name'))
        print("Skills categories:", list(cand.get('technical_skills', {}).keys()))
        print("Experience count:", len(cand.get('experience', [])))
        print("Education count:", len(cand.get('education', [])))
        print("Projects count:", len(cand.get('projects', [])))

if __name__ == "__main__":
    test_api()
