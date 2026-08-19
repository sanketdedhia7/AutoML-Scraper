import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    r.raise_for_status()
    print("Health check passed:", r.json())

def test_dashboard():
    r = requests.get(f"{BASE_URL}/")
    r.raise_for_status()
    assert "text/html" in r.headers["Content-Type"]
    print("Dashboard loaded successfully.")

def test_api():
    r = requests.get(f"{BASE_URL}/api/dashboard-data")
    r.raise_for_status()
    data = r.json()
    assert "articles" in data
    assert "scrapers_html" in data
    print(f"API dashboard-data loaded successfully. Found {len(data['articles'])} articles.")

if __name__ == "__main__":
    try:
        test_health()
        test_dashboard()
        test_api()
        print("All tests passed.")
    except Exception as e:
        print("Test failed:", e)
        sys.exit(1)
