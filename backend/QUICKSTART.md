# Quick Start Guide

Hướng dẫn nhanh để chạy backend trong 5 phút!

## Bước 1: Cài đặt dependencies

```bash
cd Final_Project/backend
pip install -r requirements.txt
```

## Bước 2: Cấu hình token (Optional cho LLM parsing)

```bash
# Copy .env.example thành .env
cp .env.example .env

# Sửa file .env và thêm token
nano .env
```

Lấy HuggingFace token tại: https://huggingface.co/settings/tokens

```
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **Lưu ý**: Nếu không có token, vẫn chạy được nhưng không sử dụng được tính năng parse text.

## Bước 3: Chạy server

### Cách 1: Sử dụng script (MacOS/Linux)
```bash
./run.sh
```

### Cách 2: Chạy trực tiếp
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Cách 3: Chạy với Python
```bash
python -m app.main
```

## Bước 4: Kiểm tra

Mở browser và truy cập:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## Bước 5: Test API

```bash
# Chạy test script
python test_api.py
```

Hoặc test với curl:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# Predict
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "Area": 120,
      "Bedrooms": 3,
      "Bathrooms": 2,
      "District": "Quận 7"
    }
  }'
```

## Demo Accounts

- `admin` / `admin123`
- `demo` / `demo123`
- `user` / `user123`

## Các endpoint chính

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/auth/login` | POST | Login |
| `/api/v1/parse` | POST | Parse text |
| `/api/v1/predict` | POST | Predict price |
| `/api/v1/models` | GET | Get models |

## Troubleshooting

**Lỗi: Models không load được**
- Kiểm tra thư mục `models/saved_models/` có file `.pkl`

**Lỗi: LLM parsing không hoạt động**
- Thêm `HUGGINGFACE_TOKEN` vào `.env`

**Lỗi: Port 8000 đã được sử dụng**
- Đổi port: `uvicorn app.main:app --port 8001`

---

Xem chi tiết tại [README.md](README.md)
