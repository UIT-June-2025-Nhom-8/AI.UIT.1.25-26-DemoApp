# Architecture Design - Vietnam Housing Price Prediction System

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Architecture Layers](#architecture-layers)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [API Endpoints](#api-endpoints)
- [Deployment Architecture](#deployment-architecture)
- [Security](#security)
- [Performance](#performance)

---

## 🏗️ System Overview

Hệ thống dự báo giá nhà được xây dựng theo kiến trúc **3-tier architecture** với sự tách biệt rõ ràng giữa Frontend, Backend API, và ML Processing Layer.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  React + TypeScript Frontend                            │   │
│  │  - UI Components (shadcn/ui)                            │   │
│  │  - State Management (React Hooks)                       │   │
│  │  - Routing (React Router)                               │   │
│  │  - API Client (Axios)                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend                                         │   │
│  │  - API Gateway                                           │   │
│  │  - JWT Authentication                                    │   │
│  │  - Request Validation (Pydantic)                         │   │
│  │  - CORS Middleware                                       │   │
│  │  - Error Handling                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Business Logic Services                                 │   │
│  │  - Tree Model Service                                    │   │
│  │  - Tree Preprocess Service                               │   │
│  │  - LLM Service (HuggingFace)                             │   │
│  │  - Auth Service                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ML PROCESSING LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Data Preprocessing Pipeline                             │   │
│  │  - Label Encoding (41 features)                          │   │
│  │  - Location Statistics                                   │   │
│  │  - Feature Engineering                                   │   │
│  │  - Data Validation                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ML Models                                               │   │
│  │  - LightGBM Regressor (Primary)                          │   │
│  │  - XGBoost Regressor                                     │   │
│  │  - Ensemble Prediction                                   │   │
│  │  - Confidence Scoring                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Architecture Layers

### 1. Frontend Layer (Client)

**Technology Stack:**
- **React 18** - Modern UI library with concurrent features
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **shadcn/ui** - High-quality UI components

**Responsibilities:**
- User interface rendering
- User input handling
- API communication
- Client-side validation
- State management
- Responsive design
- Animation và UX

**Key Components:**
```
frontend/src/
├── components/
│   ├── ui/              # shadcn/ui components
│   ├── auth/            # Authentication components
│   ├── layout/          # Layout components (Header, Footer)
│   ├── predict/         # Prediction form components
│   └── about/           # About page components
├── pages/
│   ├── LoginPage.tsx
│   ├── PredictPage.tsx
│   └── AboutPage.tsx
├── lib/
│   └── api.ts          # API client configuration
└── App.tsx             # Main app component
```

---

### 2. API Gateway Layer (Backend)

**Technology Stack:**
- **FastAPI** - Modern, high-performance web framework
- **Pydantic** - Data validation using Python type hints
- **JWT** - JSON Web Tokens for authentication
- **Uvicorn** - ASGI web server
- **Python 3.8+**

**Responsibilities:**
- Request routing
- Authentication & Authorization
- Input validation
- Error handling
- CORS management
- API documentation (Swagger/OpenAPI)
- Logging

**API Structure:**
```
backend/app/
├── api/
│   ├── __init__.py
│   └── routes.py        # All API endpoints
├── core/
│   ├── auth.py          # JWT authentication
│   ├── config.py        # Configuration settings
│   └── security.py      # Security utilities
├── schemas/
│   ├── request.py       # Request models
│   └── response.py      # Response models
├── services/            # Business logic
├── utils/               # Helper functions
└── main.py             # FastAPI application
```

---

### 3. Business Logic Layer (Services)

**Services:**

#### a. Tree Model Service
```python
# app/services/tree_model_service.py
class TreeModelService:
    - load_models()           # Load LightGBM, XGBoost
    - predict()               # Single model prediction
    - predict_all_models()    # Ensemble prediction
    - get_model_info()        # Model metadata
    - get_available_models()  # List loaded models
```

#### b. Tree Preprocess Service
```python
# app/services/tree_preprocess_service.py
class TreePreprocessService:
    - preprocess()            # Main preprocessing pipeline
    - label_encode()          # Encode categorical features
    - extract_location_stats() # Calculate location statistics
    - validate_features()     # Validate input features
```

#### c. LLM Service
```python
# app/services/llm_service.py
class LLMService:
    - initialize()            # Initialize HuggingFace model
    - parse()                 # Parse natural language to features
    - is_available()          # Check if LLM is ready
```

#### d. Auth Service
```python
# app/core/auth.py
- create_access_token()       # Generate JWT token
- authenticate_user()         # Validate credentials
- get_current_user()          # Decode JWT and get user info
```

---

### 4. ML Processing Layer

#### Data Preprocessing Pipeline

**Steps:**
1. **Input Validation** - Kiểm tra các trường bắt buộc
2. **Label Encoding** - Mã hóa các biến categorical
3. **Location Statistics** - Tính toán thống kê theo vị trí
4. **Feature Engineering** - Tạo 41 features từ raw input
5. **Data Transformation** - Chuẩn hóa dữ liệu cho model

**Input Features (8):**
```python
{
    "Area": float,          # Diện tích (m²)
    "Bedrooms": int,        # Số phòng ngủ
    "Bathrooms": int,       # Số phòng tắm
    "Floors": int,          # Số tầng
    "Frontage": float,      # Mặt tiền (m)
    "AccessRoad": float,    # Đường vào (m)
    "LegalStatus": str,     # Tình trạng pháp lý
    "Furniture": str,       # Nội thất
}
```

**Processed Features (41):**
- 8 raw features
- 33 engineered features từ label encoding và location stats

#### ML Models

**LightGBM Regressor (Primary Model):**
- Gradient boosting framework
- Fast training và inference
- Handle categorical features tốt
- Low memory consumption
- R² score: ~0.82

**XGBoost Regressor (Secondary Model):**
- Regularized boosting
- Handle missing values
- Parallel processing
- R² score: ~0.80

**Ensemble Prediction:**
```python
ensemble_prediction = mean([lightgbm_pred, xgboost_pred])
ensemble_std = std([lightgbm_pred, xgboost_pred])
confidence = calculate_confidence(ensemble_std)
```

---

## 🔄 Data Flow

### Prediction Flow (Form Input)

```
1. User Input (Frontend)
   ↓
2. Validation (Frontend)
   ↓
3. API Request: POST /api/v1/predict
   {
     "features": {...},
     "model_name": "lightgbm",
     "use_ensemble": false
   }
   ↓
4. JWT Authentication (Backend)
   ↓
5. Request Validation (Pydantic)
   ↓
6. Preprocessing Service
   - Label encoding
   - Location stats
   - Feature engineering (8 → 41 features)
   ↓
7. Model Service
   - Load model
   - Make prediction
   - Calculate confidence
   ↓
8. API Response
   {
     "prediction": 5200000000,
     "prediction_formatted": "5.2 tỷ",
     "confidence": 0.87,
     "model_used": "lightgbm"
   }
   ↓
9. Display Result (Frontend)
```

### Text Parsing Flow (Natural Language Input)

```
1. User Input Text (Frontend)
   "Nhà 3 tầng, 4 phòng ngủ, diện tích 120m2..."
   ↓
2. API Request: POST /api/v1/parse-and-predict
   ↓
3. LLM Service (HuggingFace)
   - Parse text to extract features
   - Structure data
   ↓
4. [Same as steps 6-9 above]
```

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI library |
| TypeScript | 5.x | Type safety |
| Vite | 5.x | Build tool |
| TailwindCSS | 3.x | Styling |
| Framer Motion | 11.x | Animations |
| React Router | 6.x | Routing |
| Axios | 1.x | HTTP client |
| shadcn/ui | Latest | UI components |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Programming language |
| FastAPI | 0.104+ | Web framework |
| Pydantic | 2.x | Data validation |
| Uvicorn | 0.24+ | ASGI server |
| PyJWT | 2.x | JWT authentication |
| Python-multipart | 0.0.6+ | Form data handling |

### Machine Learning
| Technology | Version | Purpose |
|------------|---------|---------|
| LightGBM | 4.x | Gradient boosting |
| XGBoost | 2.x | Gradient boosting |
| Scikit-learn | 1.3+ | ML utilities |
| Pandas | 2.x | Data manipulation |
| NumPy | 1.24+ | Numerical computing |
| HuggingFace | Latest | LLM for text parsing |

### DevOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| GitHub Actions | CI/CD |
| Vercel/Netlify | Frontend hosting |
| Railway/Render | Backend hosting |

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

### Prediction
```
POST   /api/v1/predict              # Form-based prediction
POST   /api/v1/parse                # Parse text to features
POST   /api/v1/parse-and-predict    # Parse + predict in one call
```

### Models
```
GET    /api/v1/models               # List available models
GET    /api/v1/models/{name}        # Get model info
GET    /api/v1/models/metadata      # Get model metadata
```

### Health
```
GET    /                            # Root endpoint
GET    /api/v1/health              # Health check
GET    /health                     # Root health check
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🚀 Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────────────────┐
│  USERS                                                  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│   Frontend   │          │   Backend    │
│   (Vercel)   │          │  (Railway)   │
├──────────────┤          ├──────────────┤
│ - Static     │          │ - Docker     │
│ - CDN        │◄────────►│ - API        │
│ - Auto SSL   │  HTTPS   │ - ML Models  │
│ - GitHub     │          │ - Auto Scale │
└──────────────┘          └──────────────┘
```

### Frontend Deployment (Vercel/Netlify)
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**:
  - `VITE_API_BASE_URL`: Backend API URL

### Backend Deployment (Railway/Render)
- **Dockerfile**:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- **Environment Variables**:
  - `HUGGINGFACE_TOKEN`: For LLM service
  - `SECRET_KEY`: JWT secret
  - `ALLOWED_ORIGINS`: CORS origins

---

## 🔒 Security

### Authentication
- **JWT (JSON Web Tokens)** cho session management
- Token expiry: 24 hours
- Secure password storage (hardcoded for demo, should use bcrypt in production)

### CORS Configuration
```python
ALLOWED_ORIGINS = [
    "http://localhost:5173",      # Local development
    "https://your-app.vercel.app" # Production frontend
]
```

### Input Validation
- Pydantic models cho tất cả requests
- Type checking
- Range validation
- Required field validation

### API Rate Limiting (Recommended for Production)
```python
# Add rate limiting middleware
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/predict")
@limiter.limit("10/minute")
async def predict(...):
    ...
```

---

## ⚡ Performance

### Optimization Strategies

**Frontend:**
- Code splitting với React lazy loading
- Image optimization
- CSS purging với TailwindCSS
- Bundle size optimization với Vite
- Caching strategies

**Backend:**
- Model caching (load once at startup)
- Connection pooling
- Async/await cho I/O operations
- Response compression
- Request batching

**ML Models:**
- Pre-trained models (no training at runtime)
- Efficient inference với LightGBM
- Model quantization (future improvement)
- Batch prediction support

### Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time | <500ms | ~200-300ms |
| Model Inference | <100ms | ~50-80ms |
| Frontend Load Time | <2s | ~1.5s |
| R² Score | >0.80 | ~0.82 |
| MAPE | <15% | ~12% |

---

## 📊 Monitoring & Logging

### Backend Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Recommended Monitoring Tools
- **Sentry** - Error tracking
- **LogRocket** - Frontend monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization

---

## 🔮 Future Improvements

1. **Database Integration**
   - PostgreSQL for user management
   - Redis for caching
   - Model versioning

2. **Advanced Features**
   - A/B testing for models
   - Real-time predictions
   - Batch prediction API
   - Model retraining pipeline

3. **Security Enhancements**
   - Rate limiting
   - API key authentication
   - Input sanitization
   - HTTPS enforcement

4. **Performance**
   - Model quantization
   - GPU acceleration
   - Distributed inference
   - CDN for static assets

---

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [LightGBM Documentation](https://lightgbm.readthedocs.io/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Team**: Nhóm 8 - CS106.TTNT
