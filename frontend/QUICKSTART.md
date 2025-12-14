# Quick Start Guide

## Setup & Run (3 steps)

### 1. Install dependencies
```bash
cd frontend
npm install
```

### 2. Configure environment
```bash
cp .env.example .env
```

The default `.env` already points to `http://localhost:8000/api/v1` which is correct if your backend is running locally.

### 3. Start dev server
```bash
npm run dev
```

Open http://localhost:3000

## Login

Use demo credentials:
- **Username:** `demo`
- **Password:** `demo123`

## Usage Flow

1. **Login** → Enter demo/demo123
2. **Input text** → Paste house description or click example
   - Example: "Nhà 120m2, 3PN, 2WC, quận 7, sổ hồng"
3. **Parse** → Click "Phân tích với AI"
4. **Edit** → Review and edit auto-filled features
5. **Predict** → Click "Dự đoán giá"
6. **Results** → View prediction, map, and search options

## Features

✨ **Smart Text Parsing** - AI extracts house features from Vietnamese text
📊 **Ensemble Predictions** - Combines 4 ML models
🗺️ **Interactive Map** - See location on map
🔍 **Smart Search** - Find similar properties on Google

## Troubleshooting

**Backend not running?**
```bash
cd ../backend
python -m uvicorn app.main:app --reload
```

**Port conflict?**
Edit `vite.config.ts` and change port from 3000 to another.

**API not connecting?**
1. Check backend is at http://localhost:8000
2. Check `.env` file has correct `VITE_API_URL`
3. Look at browser console for errors

## Development Tips

- Hot reload enabled - changes appear instantly
- API proxy configured - `/api` routes to backend
- TypeScript errors shown in terminal
- React DevTools recommended for debugging
