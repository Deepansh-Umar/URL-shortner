import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api():
    print("Testing Smart URL Shortener API...")
    
    # Test 1: Health Check
    print("\n1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Create Short URL
    print("\n2. Creating short URL...")
    test_url = "https://www.example.com/very/long/url/path"
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={"url": test_url}
    )
    print(f"Status: {response.status_code}")
    url_data = response.json()
    print(f"Response: {json.dumps(url_data, indent=2)}")
    
    short_code = url_data.get('short_code')
    
    # Test 3: Get URL Info
    print(f"\n3. Getting URL info for {short_code}...")
    response = requests.get(f"{BASE_URL}/api/info/{short_code}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 4: Test Redirect (should redirect to original URL)
    print(f"\n4. Testing redirect for {short_code}...")
    response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Location: {response.headers.get('Location')}")
    
    # Test 5: Create multiple clicks for analytics
    print(f"\n5. Creating multiple clicks for analytics...")
    for i in range(5):
        requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
        time.sleep(0.1)
    
    # Test 6: Get Analytics
    print(f"\n6. Getting analytics for {short_code}...")
    response = requests.get(f"{BASE_URL}/api/analytics/{short_code}")
    print(f"Status: {response.status_code}")
    analytics_data = response.json()
    print(f"Total clicks: {analytics_data.get('total_clicks')}")
    print(f"Unique visitors: {analytics_data.get('unique_visitors')}")
    
    # Test 7: Create Custom Short Code
    print("\n7. Creating custom short code...")
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={
            "url": "https://github.com",
            "custom_code": "github",
            "expires_in_days": 7
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 8: Test Error Cases
    print("\n8. Testing error cases...")
    
    # Invalid URL
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={"url": "invalid-url"}
    )
    print(f"Invalid URL - Status: {response.status_code}")
    
    # Non-existent short code
    response = requests.get(f"{BASE_URL}/api/info/nonexistent")
    print(f"Non-existent code - Status: {response.status_code}")
    
    # Duplicate custom code
    response = requests.post(
        f"{BASE_URL}/api/shorten",
        json={
            "url": "https://another-site.com",
            "custom_code": "github"
        }
    )
    print(f"Duplicate custom code - Status: {response.status_code}")
    
    print("\n✅ API testing completed!")

if __name__ == "__main__":
    test_api()
