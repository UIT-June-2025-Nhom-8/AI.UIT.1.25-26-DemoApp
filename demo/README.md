# House Price Predictor - Demo Application

Hệ thống dự đoán giá nhà sử dụng Machine Learning với giao diện web hiện đại.

## 🌐 Demo Online

- **Frontend UI**: https://ai-uit-1-25-26-demoapp-1.onrender.com
- **Backend API**: https://ai-uit-1-25-26-demoapp.onrender.com

> **Lưu ý**: Backend có thể cần 1-2 phút để khởi động lần đầu (cold start). Nên truy cập Backend trước để wake up API, sau đó UI sẽ tự động ping.

## 📁 Cấu Trúc Dự Án

```
demo/
├── backend/          # FastAPI Backend
│   ├── app/
│   │   ├── api/           # API routes & endpoints
│   │   ├── core/          # Authentication & config
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── models/            # Trained ML models
│   ├── libs/              # ML preprocessing & utilities
│   └── requirements.txt
├── frontend/         # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── lib/           # API client
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── ARCHITECTURE.md   # 📐 Architecture Design Document
```

## 🏗️ Architecture Design

Xem tài liệu chi tiết về kiến trúc hệ thống tại: **[ARCHITECTURE.md](./ARCHITECTURE.md)**

Hoặc xem trực quan trên trang **About** của ứng dụng:
- Local: http://localhost:5173/about
- Production: https://ai-uit-1-25-26-demoapp-1.onrender.com/about

## 🚀 Hướng Dẫn Chạy Local

### Backend (FastAPI)

1. **Di chuyển vào thư mục backend**:
```bash
cd backend
```

2. **Tạo môi trường ảo Python** (khuyến nghị):
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows
```

3. **Cài đặt dependencies**:
```bash
pip install -r requirements.txt
```

4. **Chạy server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

### Frontend (React + Vite)

1. **Di chuyển vào thư mục frontend**:
```bash
cd frontend
```

2. **Cài đặt dependencies**:
```bash
npm install
```

3. **Chạy development server**:
```bash
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:5173**

---

## 🛠️ Build Production

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
npm run start
```

Frontend production sẽ chạy tại: **http://localhost:3000**

---

## 📦 Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Web framework
- **scikit-learn** - Machine Learning
- **XGBoost** - Gradient Boosting
- **LightGBM** - Light Gradient Boosting
- **Pandas & NumPy** - Data processing

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **React Router** - Routing
- **Axios** - HTTP client
- **Zustand** - State management

---

## 🎯 Features

- ✅ Dự đoán giá nhà dựa trên nhiều thuộc tính
- ✅ Giao diện hiện đại với animations mượt mà
- ✅ Authentication system
- ✅ Tích hợp Google Maps
- ✅ Responsive design
- ✅ Dark theme cho trang About
- ✅ Real-time prediction

---

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký tài khoản
- `POST /auth/login` - Đăng nhập
- `POST /auth/logout` - Đăng xuất

### Prediction
- `POST /predict` - Dự đoán giá nhà
- `POST /parse` - Parse thông tin từ text

### Health
- `GET /health` - Kiểm tra trạng thái server

---

## 🔧 Environment Variables

### Backend
Tạo file `.env` trong thư mục `backend/`:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

### Frontend
Tạo file `.env` trong thư mục `frontend/`:
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
```

---

## 👥 Team

- Lã Xuân Hồng - 25410056
- Lê Quang Hoài Đức - 25410034
- Nguyễn Minh Trọng - 25410150
- Trần Thanh Long - 25410088
- Nguyễn Minh Nhật - 25410104

---

## 📄 License

Đồ Án Cuối Kỳ - CS106.TTNT
Trường Đại Học Công Nghệ Thông Tin - UIT

© 2025 - Vietnam Housing Price Prediction System
