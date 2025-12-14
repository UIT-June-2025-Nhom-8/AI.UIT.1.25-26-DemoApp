"""
Simple API test script
Run this to test the backend API
"""
import requests
import json


BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_login():
    """Test login endpoint"""
    print("Testing /auth/login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "demo", "password": "demo123"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    print()
    return data.get("access_token")


def test_predict(token=None):
    """Test prediction endpoint"""
    print("Testing /predict...")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(
        f"{BASE_URL}/predict",
        json={
            "features": {
                "Area": 120,
                "Bedrooms": 3,
                "Bathrooms": 2,
                "Floors": 2,
                "Frontage": 5,
                "AccessRoad": 4,
                "District": "Quận 7",
                "LegalStatus": "Sổ hồng",
                "Furniture": "Đầy đủ"
            },
            "model_name": "lightgbm",
            "use_ensemble": False
        },
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_parse(token=None):
    """Test parse endpoint"""
    print("Testing /parse...")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(
        f"{BASE_URL}/parse",
        json={
            "text": "Nhà 120m2, 3 phòng ngủ, 2 WC, quận 7, sổ hồng",
            "verbose": False
        },
        headers=headers
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()


def test_models():
    """Test models endpoint"""
    print("Testing /models...")
    response = requests.get(f"{BASE_URL}/models")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


if __name__ == "__main__":
    print("=" * 80)
    print("Backend API Test Script")
    print("=" * 80)
    print()

    print(f"Testing API at: {BASE_URL}")
    print()

    try:
        # Test health
        test_health()

        # Test models
        test_models()

        # Test login
        token = test_login()

        # Test predict (no auth required, but we can pass token anyway)
        test_predict(token)

        # Test parse (may fail if HUGGINGFACE_TOKEN not set)
        test_parse(token)

        print("=" * 80)
        print("✓ All tests completed!")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Is the server running?")
        print("   Run: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
