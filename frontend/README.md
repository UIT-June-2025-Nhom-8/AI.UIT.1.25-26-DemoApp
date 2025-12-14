# House Price Predictor - Frontend

Modern React 19 frontend for house price prediction using AI.

## Features

- ✨ **React 19** with TypeScript
- 🎨 **Shadcn UI** components with Tailwind CSS
- 🔐 **Authentication** with JWT
- 🤖 **LLM Text Parsing** - Parse Vietnamese house descriptions automatically
- 📝 **Editable Form** - Review and edit parsed features
- 📊 **Ensemble Predictions** - Multiple ML models for better accuracy
- 🗺️ **Interactive Maps** - Leaflet integration for location visualization
- 🔍 **Location Search** - Google & Google Maps integration
- ⚡ **Fast & Modern** - Vite build tool
- 🎭 **Smooth Animations** - Framer Motion
- 📱 **Responsive Design** - Mobile-friendly UI

## Tech Stack

- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite
- **UI Library:** Shadcn UI
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Routing:** React Router v7
- **Data Fetching:** TanStack Query (React Query)
- **HTTP Client:** Axios
- **Maps:** React Leaflet
- **Animations:** Framer Motion
- **Form Validation:** React Hook Form + Zod

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running (see `../backend/README.md`)

## Installation

1. **Install dependencies:**

```bash
npm install
```

2. **Configure environment:**

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Development

```bash
# Start dev server (with proxy to backend)
npm run dev

# Access at http://localhost:3000
```

The dev server includes a proxy to the backend API (`/api` → `http://localhost:8000`).

## Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Shadcn UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── label.tsx
│   │   │   ├── skeleton.tsx
│   │   │   ├── alert.tsx
│   │   │   └── badge.tsx
│   │   ├── auth/            # Authentication components
│   │   │   └── LoginForm.tsx
│   │   ├── predict/         # Prediction workflow components
│   │   │   ├── TextInputStep.tsx        # Step 1: Input house description
│   │   │   ├── FeatureFormStep.tsx      # Step 2: Edit parsed features
│   │   │   ├── PredictionResult.tsx     # Step 3: Show results
│   │   │   └── LocationMap.tsx          # Map & location search
│   │   ├── layout/          # Layout components
│   │   │   ├── Header.tsx
│   │   │   └── Layout.tsx
│   │   └── skeletons/       # Loading skeletons
│   │       └── FormSkeleton.tsx
│   ├── lib/
│   │   ├── api.ts           # API client & endpoints
│   │   └── utils.ts         # Utility functions
│   ├── hooks/               # Custom hooks (future)
│   ├── store/
│   │   └── authStore.ts     # Zustand auth store
│   ├── types/
│   │   └── index.ts         # TypeScript types
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   └── PredictPage.tsx
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── components.json          # Shadcn config
```

## User Flow

### 1. Login Page
- Simple authentication with demo credentials
- Beautiful gradient background
- Form validation
- JWT token management

**Demo credentials:**
- Username: `demo`
- Password: `demo123`

### 2. Prediction Workflow

The app uses a 3-step wizard:

#### Step 1: Text Input
- User pastes Vietnamese house advertisement
- Click "Phân tích với AI" to parse with LLM
- Example texts provided for quick testing

#### Step 2: Feature Form
- Review auto-filled features from AI parsing
- Edit any field as needed
- Choose single model or ensemble prediction
- Required: Area (other fields optional)

#### Step 3: Results
- **Left panel:** Prediction results
  - Main price in large text
  - Confidence score
  - Individual model predictions (if ensemble)
  - Features used
  - Reset button
- **Right panel:** Location & Search
  - Interactive Leaflet map
  - Geocoded location
  - Google Search integration
  - Google Maps link

## API Integration

The frontend connects to these backend endpoints:

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Parsing
- `POST /api/v1/parse` - Parse Vietnamese text to features

### Prediction
- `POST /api/v1/predict` - Predict house price
  - Single model or ensemble
- `POST /api/v1/parse-and-predict` - Parse + predict in one call

### Models
- `GET /api/v1/models` - List available models
- `GET /api/v1/models/{name}` - Get model info
- `GET /api/v1/health` - Health check

## Features in Detail

### LLM Text Parsing
- Automatically extracts features from Vietnamese house descriptions
- Handles various formats and abbreviations
- Example: "Nhà 120m2, 3PN, 2WC, quận 7, sổ hồng"
- Fills form fields automatically

### Ensemble Predictions
- Combines predictions from 4 models:
  - LightGBM
  - Random Forest
  - XGBoost
  - Linear Regression (Ridge)
- Shows individual predictions and confidence
- Calculates ensemble average and standard deviation

### Interactive Maps
- Uses Leaflet with OpenStreetMap tiles
- Geocodes addresses using Nominatim API
- Shows marker at house location
- Zoom controls and draggable

### Location Search
- Google Search for similar properties
- Google Maps integration
- Opens in new tab for research

## Customization

### Theme Colors
Edit `src/index.css` CSS variables:
```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

### API URL
Edit `.env`:
```env
VITE_API_URL=https://your-api.com/api/v1
```

### Adding New Features
1. Add types to `src/types/index.ts`
2. Create component in appropriate folder
3. Add API endpoint to `src/lib/api.ts`
4. Use in pages

## Performance

- Code splitting with React Router
- Lazy loading for heavy components
- React Query caching
- Vite's fast HMR
- Optimized production build

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern mobile browsers

## Troubleshooting

### Port already in use
Change port in `vite.config.ts`:
```ts
server: {
  port: 3001,
}
```

### API connection failed
1. Check backend is running at `http://localhost:8000`
2. Verify `.env` has correct `VITE_API_URL`
3. Check browser console for CORS errors

### Map not loading
1. Check internet connection (needs tiles from OpenStreetMap)
2. Verify Leaflet CSS is loaded in `index.html`
3. Check browser console for errors

### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Deployment

### Vercel/Netlify
1. Build command: `npm run build`
2. Output directory: `dist`
3. Set environment variable: `VITE_API_URL=https://your-backend.com/api/v1`

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
EXPOSE 80
```

## License

MIT

## Support

For issues or questions, please check:
- Backend README for API documentation
- [Shadcn UI Docs](https://ui.shadcn.com)
- [React Leaflet Docs](https://react-leaflet.js.org)
