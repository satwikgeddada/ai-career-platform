import requests
import json
import os

BASE_URL = 'http://127.0.0.1:5000/api'
print("--- Starting API Tests ---")

def test_career():
    print("\n[CAREER GUIDE]")
    # Valid
    res = requests.post(f"{BASE_URL}/career-plan", json={
        "name": "Test User", "targetRole": "AI Engineer", "currentSkills": "Python", "experienceLevel": "Fresher"
    })
    print("Valid Input Status:", res.status_code, res.json() if res.status_code != 200 else "")
    
    # Empty
    res = requests.post(f"{BASE_URL}/career-plan", json={})
    print("Empty Input Status:", res.status_code, res.json())

def test_resume():
    print("\n[RESUME ANALYZER]")
    # Empty
    res = requests.post(f"{BASE_URL}/analyze-resume")
    print("No File Status:", res.status_code, res.json())
    
    # Valid PDF (mock)
    with open("dummy.pdf", "wb") as f: f.write(b"%PDF-1.4 mock pdf content")
    with open("dummy.pdf", "rb") as f:
        res = requests.post(f"{BASE_URL}/analyze-resume", files={"resumeFile": f}, data={"jobDescription": "AI Engineer"})
    print("Mock PDF Status:", res.status_code, res.json() if res.status_code != 200 else "")
    
    # Invalid extension
    with open("dummy.txt", "w") as f: f.write("test")
    with open("dummy.txt", "rb") as f:
        res = requests.post(f"{BASE_URL}/analyze-resume", files={"resumeFile": f}, data={"jobDescription": "AI Engineer"})
    print("Invalid File Status:", res.status_code, res.json())

def test_interview():
    print("\n[MOCK INTERVIEW]")
    # Valid
    res = requests.post(f"{BASE_URL}/generate-interview", json={
        "role": "AI Engineer", "type": "Technical", "difficulty": "Beginner", "num_questions": 5
    })
    print("Valid Input Status:", res.status_code)
    if res.status_code == 200:
        print("Questions:", len(res.json().get('questions', [])))
        
    # Empty
    res = requests.post(f"{BASE_URL}/generate-interview", json={})
    print("Empty Input Status:", res.status_code, res.json())
    
    # History
    res = requests.get(f"{BASE_URL}/interview-history")
    print("History Status:", res.status_code)

if __name__ == '__main__':
    try:
        test_career()
        test_resume()
        test_interview()
    except Exception as e:
        print("Test script failed:", e)
    
    # Cleanup
    if os.path.exists("dummy.pdf"): os.remove("dummy.pdf")
    if os.path.exists("dummy.txt"): os.remove("dummy.txt")
