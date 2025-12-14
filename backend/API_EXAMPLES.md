# API Examples

Ví dụ chi tiết về cách sử dụng các API endpoints.

## Base URL

```
Local: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

---

## 1. Authentication

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "demo"
}
```

### Using Token

Sau khi login, sử dụng token trong header:

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 2. Text Parsing

### Parse Vietnamese Real Estate Text

```bash
curl -X POST http://localhost:8000/api/v1/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bán nhà mặt tiền đường Nguyễn Thị Minh Khai, Quận 1, DT: 120m2, 3 phòng ngủ, 2 toilet, 2 tầng, hướng đông nam, sổ hồng chính chủ, nội thất đầy đủ",
    "verbose": false
  }'
```

**Response:**
```json
{
  "success": true,
  "features": {
    "Area": 120,
    "Bedrooms": 3,
    "Bathrooms": 2,
    "Floors": 2,
    "District": "Quận 1",
    "Direction": "Đông nam",
    "LegalStatus": "Sổ hồng",
    "Furniture": "Đầy đủ"
  },
  "raw_text": "Bán nhà mặt tiền..."
}
```

### More Examples

**Simple description:**
```bash
curl -X POST http://localhost:8000/api/v1/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Nhà 100m2, 3PN, 2WC, quận 7"}'
```

**Detailed description:**
```bash
curl -X POST http://localhost:8000/api/v1/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Nhà phố cao cấp 150m2, 4 phòng ngủ, 3 WC, 3 lầu, mặt tiền 6m, đường vào 5m, hướng tây nam, ban công hướng đông, quận Bình Thạnh, sổ đỏ, full nội thất"
  }'
```

---

## 3. Price Prediction

### Single Model Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
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
    "use_ensemble": false
  }'
```

**Response:**
```json
{
  "prediction": 5200000000,
  "prediction_formatted": "5.2 tỷ",
  "confidence": 85.0,
  "model_used": "lightgbm",
  "features_used": { ... }
}
```

### Ensemble Prediction (All Models)

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "Area": 120,
      "Bedrooms": 3,
      "Bathrooms": 2,
      "District": "Quận 7"
    },
    "use_ensemble": true
  }'
```

**Response:**
```json
{
  "ensemble_prediction": 5150000000,
  "ensemble_prediction_formatted": "5.15 tỷ",
  "ensemble_std": 150000000,
  "confidence": 88.5,
  "individual_predictions": {
    "lightgbm": {
      "prediction": 5200000000,
      "confidence": 85.0
    },
    "random_forest": {
      "prediction": 5100000000,
      "confidence": 82.0
    },
    "xgboost": {
      "prediction": 5180000000,
      "confidence": 87.0
    },
    "linear_regression": {
      "prediction": 5120000000,
      "confidence": 80.0
    }
  },
  "models_used": ["lightgbm", "random_forest", "xgboost", "linear_regression"],
  "features_used": { ... }
}
```

### Different Models

**Using Random Forest:**
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {"Area": 100, "Bedrooms": 2, "District": "Quận 1"},
    "model_name": "random_forest"
  }'
```

**Using XGBoost:**
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {"Area": 150, "Bedrooms": 4, "District": "Quận 2"},
    "model_name": "xgboost"
  }'
```

---

## 4. Parse & Predict (Combined)

Parse text và predict trong một request:

```bash
curl -X POST http://localhost:8000/api/v1/parse-and-predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Nhà 120m2, 3 phòng ngủ, 2 WC, quận 7, sổ hồng, nội thất đầy đủ",
    "model_name": "lightgbm",
    "use_ensemble": false
  }'
```

**With ensemble:**
```bash
curl -X POST http://localhost:8000/api/v1/parse-and-predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bán gấp nhà 150m2, 4PN, 3WC, quận Bình Thạnh, sổ đỏ",
    "use_ensemble": true
  }'
```

---

## 5. Model Information

### Get Available Models

```bash
curl http://localhost:8000/api/v1/models
```

**Response:**
```json
{
  "models": ["lightgbm", "random_forest", "xgboost", "linear_regression"],
  "default_model": "lightgbm"
}
```

### Get Model Info

```bash
curl http://localhost:8000/api/v1/models/lightgbm
```

**Response:**
```json
{
  "name": "lightgbm",
  "available": true,
  "metadata": {
    "name": "LightGBM Regressor",
    "params": { ... },
    "feature_names": [...],
    "training_time": 2.45
  }
}
```

---

## 6. Health & Status

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": 4,
  "llm_available": true
}
```

---

## Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "demo", "password": "demo123"}
)
token = response.json()["access_token"]

# Parse text
response = requests.post(
    f"{BASE_URL}/parse",
    json={"text": "Nhà 120m2, 3PN, quận 7"}
)
features = response.json()["features"]

# Predict
response = requests.post(
    f"{BASE_URL}/predict",
    json={
        "features": features,
        "use_ensemble": True
    }
)
prediction = response.json()

print(f"Predicted price: {prediction['ensemble_prediction_formatted']}")
print(f"Confidence: {prediction['confidence']:.1f}%")
```

---

## JavaScript/TypeScript Examples

### Using fetch

```javascript
// Login
const login = async () => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'demo',
      password: 'demo123'
    })
  });
  const data = await response.json();
  return data.access_token;
};

// Parse and predict
const parseAndPredict = async (text) => {
  const response = await fetch('http://localhost:8000/api/v1/parse-and-predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      use_ensemble: true
    })
  });
  const data = await response.json();
  console.log(`Price: ${data.ensemble_prediction_formatted}`);
  console.log(`Confidence: ${data.confidence}%`);
  return data;
};

// Usage
parseAndPredict("Nhà 120m2, 3PN, quận 7, sổ hồng");
```

### Using axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' }
});

// Login and set token
const login = async () => {
  const { data } = await api.post('/auth/login', {
    username: 'demo',
    password: 'demo123'
  });
  api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
  return data;
};

// Predict
const predict = async (features) => {
  const { data } = await api.post('/predict', {
    features: features,
    use_ensemble: false
  });
  return data;
};
```

---

## Error Handling

### Invalid credentials
```json
{
  "detail": "Incorrect username or password"
}
```

### Invalid features
```json
{
  "detail": "Invalid features: Area must be positive"
}
```

### Model not found
```json
{
  "detail": "Model 'invalid_model' not found"
}
```

### LLM service unavailable
```json
{
  "detail": "LLM parsing service not available. Please set HUGGINGFACE_TOKEN."
}
```

---

## Rate Limiting

Current implementation has no rate limiting (for demo).
In production, consider adding rate limiting using:
- `slowapi`
- `fastapi-limiter`
- API Gateway (Nginx, CloudFlare, etc.)

---

## Best Practices

1. **Always use HTTPS in production**
2. **Validate input on frontend** before sending to API
3. **Handle errors gracefully**
4. **Cache results** when appropriate
5. **Use ensemble prediction** for higher accuracy
6. **Store tokens securely** (never in localStorage for sensitive apps)

---

For more information, see [README.md](README.md)
