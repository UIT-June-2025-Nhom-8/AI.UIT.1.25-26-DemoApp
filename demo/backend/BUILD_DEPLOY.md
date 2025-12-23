# 🚀 Build & Deployment Guide

This guide covers building and deploying the Vietnam Housing Price Prediction API.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Build & Test](#docker-build--test)
- [Deployment Platforms](#deployment-platforms)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker installed (version 20.10+)
- Docker Compose (version 2.0+)
- Git
- HuggingFace token (optional, for LLM features)

---

## Local Development

### Option 1: Using Virtual Environment (Traditional)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and add your HUGGINGFACE_TOKEN if needed

# Run the server
./run.sh
# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access the API:
- **API Root**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## Docker Build & Test

### Build Image

```bash
# Build the image
docker build -t vietnam-house-api:latest .

# Build with specific tag
docker build -t vietnam-house-api:v1.0.0 .

# Build with no cache (clean build)
docker build --no-cache -t vietnam-house-api:latest .
```

### Run Container

```bash
# Run with default settings
docker run -p 8000:8000 vietnam-house-api:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e DEBUG=True \
  -e LOG_LEVEL=DEBUG \
  -e HUGGINGFACE_TOKEN=your_token_here \
  vietnam-house-api:latest

# Run with .env file
docker run -p 8000:8000 --env-file .env vietnam-house-api:latest

# Run in background
docker run -d -p 8000:8000 --name vietnam-house-api vietnam-house-api:latest
```

### Inspect & Debug

```bash
# Check container logs
docker logs vietnam-house-api
docker logs -f vietnam-house-api  # Follow logs

# Check container health
docker inspect --format='{{.State.Health.Status}}' vietnam-house-api

# Execute commands in running container
docker exec -it vietnam-house-api /bin/bash

# Check running processes
docker exec vietnam-house-api ps aux
```

### Test Image

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test root endpoint
curl http://localhost:8000/

# Test with httpie (if installed)
http GET http://localhost:8000/api/v1/health
```

---

## Deployment Platforms

### 1. Railway.app

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variables
railway variables set HUGGINGFACE_TOKEN=your_token
railway variables set DEBUG=False
railway variables set LOG_LEVEL=INFO
```

**Railway Configuration:**
- Build Command: `docker build`
- Start Command: Automatic (uses Dockerfile CMD)
- Port: Automatic (Railway sets PORT env var)

### 2. Render.com

The project includes `render.yaml` configuration file.

**Steps:**
1. Push code to GitHub
2. Create new Web Service on Render
3. Select "Deploy from Git"
4. Render will auto-detect `render.yaml`
5. Set `HUGGINGFACE_TOKEN` in Render dashboard
6. Deploy!

**Or manual setup:**
- **Build Command**: `docker build -t vietnam-house-api .`
- **Start Command**: Uses Dockerfile CMD
- **Health Check Path**: `/api/v1/health`

### 3. Google Cloud Run

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/vietnam-house-api

# Deploy
gcloud run deploy vietnam-house-api \
  --image gcr.io/YOUR_PROJECT_ID/vietnam-house-api \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "DEBUG=False,LOG_LEVEL=INFO"

# Set secrets
gcloud run services update vietnam-house-api \
  --update-secrets HUGGINGFACE_TOKEN=huggingface-token:latest
```

### 4. AWS ECS/Fargate

```bash
# Login to ECR
aws ecr get-login-password --region ap-southeast-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.ap-southeast-1.amazonaws.com

# Build and tag
docker build -t vietnam-house-api .
docker tag vietnam-house-api:latest YOUR_ACCOUNT.dkr.ecr.ap-southeast-1.amazonaws.com/vietnam-house-api:latest

# Push to ECR
docker push YOUR_ACCOUNT.dkr.ecr.ap-southeast-1.amazonaws.com/vietnam-house-api:latest

# Deploy using ECS CLI or AWS Console
```

### 5. DigitalOcean App Platform

1. Connect your GitHub repo
2. Select Dockerfile deployment
3. Configure:
   - **HTTP Port**: 8000
   - **Health Check**: `/api/v1/health`
   - **Environment Variables**: Set in dashboard
4. Deploy!

---

## Environment Variables

Required/recommended environment variables for deployment:

```bash
# Required
SECRET_KEY=your-secret-key-min-32-chars  # Generate: openssl rand -hex 32

# Optional but recommended
DEBUG=False                               # Set to False in production
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR
ALLOWED_ORIGINS=https://yourdomain.com   # Set to your frontend domain
DEFAULT_MODEL=lightgbm                   # xgboost, lightgbm, or random_forest
HUGGINGFACE_TOKEN=hf_xxxxx              # For LLM features (optional)

# Platform-specific (usually auto-set)
PORT=8000                                # Auto-set by Railway/Render
```

---

## Troubleshooting

### Issue: Container exits immediately

```bash
# Check logs
docker logs vietnam-house-api

# Check if models are loaded
docker exec vietnam-house-api ls -la /app/models/
```

### Issue: Models not found

```bash
# Verify models are copied during build
docker run --rm vietnam-house-api ls -la /app/models/

# Rebuild with no cache
docker build --no-cache -t vietnam-house-api:latest .
```

### Issue: Permission denied errors

The Dockerfile now uses non-root user (`appuser`). If you have permission issues:

```bash
# Ensure files have correct ownership in container
docker exec vietnam-house-api ls -la /app/
```

### Issue: Health check failing

```bash
# Test health endpoint manually
docker exec vietnam-house-api curl http://localhost:8000/api/v1/health

# Check if uvicorn is running
docker exec vietnam-house-api ps aux | grep uvicorn
```

### Issue: Port already in use

```bash
# Find what's using port 8000
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Use different port
docker run -p 8080:8000 vietnam-house-api:latest
```

### Issue: Large image size

Current optimizations already applied:
- Multi-stage build
- Slim base image
- Minimal dependencies
- Cleaned apt cache

To reduce further:

```bash
# Check image size
docker images vietnam-house-api

# Use dive to analyze layers
dive vietnam-house-api:latest

# Consider .dockerignore (already configured)
```

---

## Performance Tuning

### Uvicorn Workers

For production with multiple CPU cores:

```bash
# Run with multiple workers
docker run -p 8000:8000 \
  -e UVICORN_WORKERS=4 \
  vietnam-house-api:latest

# Or modify CMD in Dockerfile:
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
```

### Resource Limits

Set in docker-compose.yml or platform dashboard:
- **CPU**: 1-2 cores recommended
- **Memory**: 512MB-2GB depending on models
- **Storage**: 1GB minimum

---

## CI/CD Pipeline Example

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker image
        run: |
          docker build -t your-registry/vietnam-house-api:${{ github.sha }} .
          docker push your-registry/vietnam-house-api:${{ github.sha }}

      - name: Deploy to platform
        run: |
          # Platform-specific deployment commands
```

---

## Security Checklist

- [ ] Change default `SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Use HTTPS for API endpoints
- [ ] Store `HUGGINGFACE_TOKEN` in secrets/vault
- [ ] Enable rate limiting (add to FastAPI)
- [ ] Regular security updates: `docker pull python:3.9-slim`
- [ ] Monitor logs and set up alerts

---

## Support

For issues or questions:
- Check logs: `docker logs vietnam-house-api`
- Review health status: `curl http://localhost:8000/api/v1/health`
- Check API docs: http://localhost:8000/docs

---

**Last Updated**: 2025-12-23
**Dockerfile Version**: 1.0
