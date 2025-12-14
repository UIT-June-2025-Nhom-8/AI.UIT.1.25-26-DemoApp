# Vietnam Housing Price Prediction - Backend API

Backend API cho hệ thống dự đoán giá nhà tại Việt Nam sử dụng Machine Learning.

## Tính năng

- **🔐 Authentication**: Login/Logout với JWT tokens (hardcoded accounts cho demo)
- **📝 Text Parsing**: Parse mô tả bất động sản tiếng Việt thành features sử dụng LLM
- **🤖 Price Prediction**: Dự đoán giá nhà sử dụng nhiều ML models
- **📊 Multi-Model Support**: Hỗ trợ 4 models (LightGBM, Random Forest, XGBoost, Linear Regression)
- **🎯 Ensemble Prediction**: Kết hợp dự đoán từ nhiều models
- **📖 API Documentation**: Tự động tạo docs với Swagger UI

## Công nghệ sử dụng

- **FastAPI**: Modern web framework cho Python
- **Pydantic**: Data validation
- **Scikit-learn, XGBoost, LightGBM**: ML models
- **HuggingFace**: LLM parsing
- **JWT**: Authentication
- **Uvicorn**: ASGI server

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── api/                  # API routes
│   │   ├── routes.py
│   │   └── __init__.py
│   ├── core/                 # Core configuration & auth
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── auth.py
│   │   └── __init__.py
│   ├── services/             # Business logic services
│   │   ├── model_service.py      # ML model loading & prediction
│   │   ├── preprocess_service.py # Data preprocessing
│   │   ├── llm_service.py        # LLM text parsing
│   │   └── __init__.py
│   ├── schemas/              # Request/Response schemas
│   │   ├── request.py
│   │   ├── response.py
│   │   └── __init__.py
│   ├── utils/                # Utilities
│   │   ├── helpers.py
│   │   └── __init__.py
│   └── main.py               # FastAPI application
├── models/
│   └── saved_models/         # Trained ML models (.pkl files)
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .env.example             # Environment variables template
├── render.yaml              # Render.com deployment config
└── README.md                # This file
```

## Cài đặt & Chạy Local

### 1. Prerequisites

- Python 3.9+
- pip hoặc conda

### 2. Clone và Setup

```bash
# Di chuyển vào thư mục backend
cd Final_Project/backend

# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Cấu hình Environment Variables

```bash
# Copy .env.example thành .env
cp .env.example .env

# Chỉnh sửa .env file
nano .env
```

**Quan trọng**: Thêm HuggingFace token vào `.env`:

```bash
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Lấy token tại: https://huggingface.co/settings/tokens (Token Type: "Read")

### 4. Chạy Backend

```bash
# Chạy với uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc chạy trực tiếp
python -m app.main
```

Server sẽ chạy tại: http://localhost:8000

### 5. Kiểm tra API

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Authentication

#### POST `/api/v1/auth/login`
Đăng nhập với username/password

**Demo accounts**:
- `admin` / `admin123`
- `demo` / `demo123`
- `user` / `user123`

**Request**:
```json
{
  "username": "demo",
  "password": "demo123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "demo"
}
```

#### POST `/api/v1/auth/logout`
Đăng xuất (requires authentication)

**Headers**: `Authorization: Bearer <token>`

---

### Text Parsing

#### POST `/api/v1/parse`
Parse mô tả bất động sản tiếng Việt thành features

**Request**:
```json
{
  "text": "Nhà 120m2, 3 phòng ngủ, 2 WC, quận 7, sổ hồng, hướng đông nam",
  "verbose": false
}
```

**Response**:
```json
{
  "success": true,
  "features": {
    "Area": 120,
    "Bedrooms": 3,
    "Bathrooms": 2,
    "District": "Quận 7",
    "LegalStatus": "Sổ hồng",
    "Direction": "Đông nam"
  },
  "raw_text": "Nhà 120m2, 3 phòng ngủ, 2 WC, quận 7, sổ hồng, hướng đông nam"
}
```

---

### Price Prediction

#### POST `/api/v1/predict`
Dự đoán giá nhà từ features

**Request**:
```json
{
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
}
```

**Response** (single model):
```json
{
  "prediction": 5200000000,
  "prediction_formatted": "5.2 tỷ",
  "confidence": 85.0,
  "model_used": "lightgbm",
  "features_used": { ... }
}
```

**Response** (ensemble):
```json
{
  "ensemble_prediction": 5150000000,
  "ensemble_prediction_formatted": "5.15 tỷ",
  "ensemble_std": 150000000,
  "confidence": 88.5,
  "individual_predictions": {
    "lightgbm": { ... },
    "random_forest": { ... },
    "xgboost": { ... },
    "linear_regression": { ... }
  },
  "models_used": ["lightgbm", "random_forest", "xgboost", "linear_regression"],
  "features_used": { ... }
}
```

#### POST `/api/v1/parse-and-predict`
Parse text và predict trong một request

**Request**:
```json
{
  "text": "Nhà 120m2, 3PN, 2WC, quận 7, sổ hồng",
  "model_name": "lightgbm",
  "use_ensemble": false
}
```

---

### Model Information

#### GET `/api/v1/models`
Lấy danh sách models có sẵn

**Response**:
```json
{
  "models": ["lightgbm", "random_forest", "xgboost", "linear_regression"],
  "default_model": "lightgbm"
}
```

#### GET `/api/v1/models/{model_name}`
Lấy thông tin về một model cụ thể

---

### Health Check

#### GET `/api/v1/health`
Kiểm tra trạng thái service

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": 4,
  "llm_available": true
}
```

## Deployment

### Deploy với Docker

```bash
# Build image
docker build -t vietnam-house-price-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e HUGGINGFACE_TOKEN=hf_xxx \
  --name house-price-api \
  vietnam-house-price-api
```

### Deploy lên Render.com

1. Push code lên GitHub
2. Tạo account trên [Render.com](https://render.com)
3. Click "New" → "Blueprint"
4. Connect GitHub repository
5. Render sẽ tự động detect `render.yaml`
6. Thêm `HUGGINGFACE_TOKEN` vào Environment Variables
7. Deploy!

**Hoặc deploy manual**:

1. Click "New" → "Web Service"
2. Connect repository
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add `HUGGINGFACE_TOKEN`
4. Deploy

### Deploy lên Railway.app

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set HUGGINGFACE_TOKEN=hf_xxx

# Deploy
railway up
```

### Deploy lên Heroku

```bash
# Install Heroku CLI
# Then:

heroku login
heroku create vietnam-house-price-api
heroku config:set HUGGINGFACE_TOKEN=hf_xxx
git push heroku main
```

## Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Development

### Code formatting

```bash
# Install black
pip install black

# Format code
black app/
```

### Run with auto-reload

```bash
uvicorn app.main:app --reload
```

## Troubleshooting

### Models không load được

**Lỗi**: `Model file not found`

**Giải pháp**:
- Kiểm tra thư mục `models/saved_models/` có các file `.pkl`
- Kiểm tra tên file trong `app/core/config.py` → `MODEL_FILES`

### LLM parsing không hoạt động

**Lỗi**: `LLM parsing service not available`

**Giải pháp**:
- Thêm `HUGGINGFACE_TOKEN` vào file `.env`
- Lấy token tại: https://huggingface.co/settings/tokens
- Token phải bắt đầu bằng `hf_`

### CORS errors từ frontend

**Giải pháp**: Thêm frontend URL vào `ALLOWED_ORIGINS` trong `.env`

```bash
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

## License

CS106.TTNT Final Project - Educational purposes

## Contact

- GitHub: [Your GitHub]
- Email: [Your Email]

---

**Happy Coding!** 🚀
