# Architecture Design Guide

## 📍 Cách Xem Architecture Design

Có **3 cách** để xem architecture design của hệ thống:

### 1. 🌐 Xem Trực Quan Trên Web (Recommended)

Truy cập trang **About** của ứng dụng để xem architecture design với animations và visualization đẹp mắt:

**Local Development:**
```
http://localhost:5173/about
```

**Production:**
```
https://ai-uit-1-25-26-demoapp-1.onrender.com/about
```

**Nội dung bao gồm:**
- ✨ 3-Tier Architecture với animations
- ✨ Data Flow Timeline với thời gian xử lý
- ✨ System Features Grid
- ✨ Technology Stack Details với màu sắc
- ✨ API Endpoints Documentation
- ✨ Deployment Architecture
- ✨ Full Stack Overview

---

### 2. 📄 Đọc Documentation (Chi tiết nhất)

Mở file [ARCHITECTURE.md](./ARCHITECTURE.md) để xem tài liệu chi tiết về kiến trúc:

**Nội dung bao gồm:**
- System Overview với ASCII diagrams
- Architecture Layers (Frontend, Backend, ML)
- Data Flow chi tiết từng bước
- Technology Stack đầy đủ
- API Endpoints reference
- Deployment Architecture
- Security best practices
- Performance metrics
- Future improvements

**Cách mở:**
```bash
# Trong editor
code ARCHITECTURE.md

# Hoặc trong browser (với Markdown preview)
open ARCHITECTURE.md
```

---

### 3. 🔍 Xem Code Structure

Khám phá source code để hiểu implementation chi tiết:

**Frontend Components:**
```
frontend/src/components/about/
├── ArchitectureDiagram.tsx    # Main architecture visualization
└── SystemOverview.tsx          # 3-tier overview & data flow
```

**Backend Structure:**
```
backend/app/
├── api/routes.py              # All API endpoints
├── core/
│   ├── auth.py                # JWT authentication
│   ├── config.py              # Configuration
│   └── security.py            # Security utilities
├── services/
│   ├── tree_model_service.py      # ML model service
│   ├── tree_preprocess_service.py # Preprocessing
│   └── llm_service.py             # LLM parsing
└── main.py                    # FastAPI app
```

---

## 🎯 Quick Reference

### System Architecture Overview

```
┌─────────────────────────────────────────────┐
│           CLIENT LAYER                      │
│  React + TypeScript + TailwindCSS           │
└────────────────┬────────────────────────────┘
                 │ HTTPS/REST
                 ▼
┌─────────────────────────────────────────────┐
│        APPLICATION LAYER                    │
│  FastAPI + JWT Auth + Pydantic              │
│  ├── API Gateway                            │
│  ├── Business Services                      │
│  └── LLM Service                            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│        ML PROCESSING LAYER                  │
│  ├── Data Preprocessing (41 features)      │
│  ├── LightGBM Regressor                     │
│  ├── XGBoost Regressor                      │
│  └── Ensemble Prediction                    │
└─────────────────────────────────────────────┘
```

### Key Technologies

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, TailwindCSS, Framer Motion |
| **Backend** | FastAPI, Python 3.8+, Pydantic, JWT |
| **ML** | LightGBM, XGBoost, HuggingFace, Scikit-learn |
| **DevOps** | Docker, GitHub Actions, Vercel/Railway |

### Performance Metrics

- **API Response Time**: ~200-300ms
- **Model Inference**: ~50-80ms
- **R² Score**: ~0.82
- **MAPE**: ~12%

### Main API Endpoints

```
POST   /api/v1/auth/login          # Login
POST   /api/v1/predict             # Predict price
POST   /api/v1/parse-and-predict   # Parse text + predict
GET    /api/v1/models              # List models
GET    /api/v1/health              # Health check
```

---

## 📚 Deep Dive Sections

### Frontend Architecture
- Component structure với React
- State management strategy
- API client configuration
- Routing và navigation
- UI components library (shadcn/ui)

### Backend Architecture
- FastAPI application structure
- Request/Response flow
- Service layer pattern
- Authentication & authorization
- Error handling strategy

### ML Pipeline
- Data preprocessing (8 → 41 features)
- Label encoding
- Location statistics
- Model loading & inference
- Ensemble prediction
- Confidence scoring

### Deployment
- Docker containerization
- CI/CD với GitHub Actions
- Frontend hosting (Vercel/Netlify)
- Backend hosting (Railway/Render)
- Environment variables
- Health checks

---

## 🔗 Related Resources

- **Main README**: [README.md](./README.md)
- **Architecture Docs**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Source Code**: [GitHub Repository](https://github.com/UIT-June-2025-Nhom-8/AI.UIT.1.25-26)
- **API Docs**: http://localhost:8000/docs (khi chạy local)

---

## 💡 Tips

1. **Xem Web UI trước** để có overview tổng quan với visualization
2. **Đọc ARCHITECTURE.md** để hiểu chi tiết implementation
3. **Khám phá source code** để học cách implement
4. **Chạy local** để test và experiment

---

## 🤝 Contributing

Nếu bạn muốn đóng góp cải thiện architecture:

1. Tạo branch mới
2. Cập nhật code + documentation
3. Update ARCHITECTURE.md nếu có thay đổi lớn
4. Update component visualization nếu cần
5. Submit pull request

---

**Questions?** Contact team members hoặc tạo issue trên GitHub.

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Team**: Nhóm 8 - CS106.TTNT - UIT
