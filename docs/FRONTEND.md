# 🎨 ManRakshak AI — Frontend Documentation

## Overview

The ManRakshak platform has **three frontend applications**:

1. **Web Dashboard** — React 19 + TypeScript + TailwindCSS (for commanders/welfare officers/admins)
2. **Mobile Web App** — React + TypeScript + Vite PWA (lightweight mobile browser interface for personnel)
3. **Flutter Mobile App** — Native Android/iOS app for personnel

---

## 🌐 Web Dashboard (`/web_dashboard`)

### Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| React | 19.x | UI framework |
| TypeScript | 6.x | Type safety |
| Vite | 8.x | Build tool + dev server |
| TailwindCSS | 3.x | Utility-first CSS |
| React Router DOM | 7.x | Client-side routing |
| Recharts | 3.x | Data visualization charts |
| Lucide React | 1.x | Icon library |
| date-fns | 4.x | Date utilities |

### Directory Structure

```
web_dashboard/
├── src/
│   ├── main.tsx              # React app entry point
│   ├── App.tsx               # Root component, routing setup
│   ├── App.css               # Global styles
│   ├── index.css             # Tailwind base imports
│   │
│   ├── components/           # Reusable UI components
│   │   ├── charts/           # Recharts-based chart components
│   │   ├── cards/            # Metric/info card components
│   │   ├── tables/           # Data table components
│   │   └── ui/               # Base UI primitives (buttons, inputs, modals)
│   │
│   ├── features/             # Feature-based module organization
│   │   ├── auth/             # Login, logout, auth guards
│   │   ├── dashboard/        # Main overview dashboard
│   │   ├── wellness/         # Wellness monitoring views
│   │   ├── personnel/        # Personnel management
│   │   ├── interventions/    # Intervention tracking
│   │   ├── reports/          # Report generation & export
│   │   ├── analytics/        # Analytics charts and stats
│   │   ├── notifications/    # Notification center
│   │   └── admin/            # Admin panel (user management)
│   │
│   ├── contexts/             # React context providers
│   │   ├── AuthContext.tsx   # Authentication state + JWT management
│   │   └── ThemeContext.tsx  # Dark/light mode
│   │
│   ├── layouts/              # Page layout wrappers
│   │   ├── DashboardLayout.tsx  # Sidebar + header layout
│   │   └── AuthLayout.tsx       # Login/register layout
│   │
│   ├── data/                 # Static data, constants, mock data
│   └── utils/                # Helper functions
│
├── public/                   # Static assets
├── dist/                     # Production build output
│
├── index.html                # HTML entry point
├── vite.config.ts            # Vite configuration
├── tailwind.config.js        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
├── package.json
├── Dockerfile
└── nginx.conf                # Nginx config for Docker serving
```

### Environment Configuration

Create `web_dashboard/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

For production:
```env
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

### Development Commands

```bash
cd web_dashboard

npm install          # Install dependencies
npm run dev          # Start dev server → http://localhost:5173
npm run build        # Production build → dist/
npm run preview      # Preview production build → http://localhost:4173
npm run lint         # Run oxlint linter
```

### User Roles & Access (Dashboard)

| Role | Accessible Features |
|---|---|
| **Admin** | All features + User management + System settings |
| **Welfare Officer** | Individual wellness data, interventions, reports, AI predictions |
| **Commander** | Anonymized unit dashboard, notifications |

### Key Components

#### AuthContext

```typescript
// Usage in any component:
import { useAuth } from '../contexts/AuthContext';

const { user, login, logout, isAuthenticated } = useAuth();
```

#### API Service Layer

All API calls go through a centralized service that:
- Automatically attaches `Authorization: Bearer <token>` headers
- Handles 401 responses with token refresh
- Normalizes error responses

---

## 📱 Mobile Web App (`/mobile_web_app`)

A lightweight React PWA designed for **police personnel** to access the platform from their mobile browser.

### Tech Stack

Same as Web Dashboard (React + TypeScript + Vite + TailwindCSS) but optimized for mobile:
- Touch-friendly UI
- Simplified navigation
- Offline-capable (PWA)

### Directory Structure

```
mobile_web_app/
├── src/
│   ├── components/           # Mobile-optimized components
│   ├── screens/              # Mobile screen views
│   │   ├── Login/
│   │   ├── Dashboard/        # Personnel home screen
│   │   ├── CheckIn/          # Daily wellness check-in form
│   │   ├── Resources/        # Wellness resources
│   │   └── Support/          # Support request form
│   └── services/             # API service layer
│
├── Dockerfile
└── nginx.conf
```

### Development Commands

```bash
cd mobile_web_app

npm install
npm run dev     # → http://localhost:5174
npm run build   # → dist/
```

### Environment Configuration

Create `mobile_web_app/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 📲 Flutter Mobile App (`/mobile_app`)

Native Android (and iOS) application for **police personnel**.

### Tech Stack

| Package | Version | Purpose |
|---|---|---|
| Flutter | 3.x SDK | Mobile framework |
| provider | 6.1.x | State management |
| http | 1.6.x | HTTP API calls |
| flutter_secure_storage | 11.x | Secure JWT storage |
| fl_chart | 0.65.x | Charts and graphs |
| google_fonts | 6.x | Typography |
| intl | 0.20.x | Internationalization |

### Directory Structure

```
mobile_app/
├── lib/
│   ├── main.dart             # App entry point
│   ├── app.dart              # App configuration
│   │
│   ├── screens/              # UI screens
│   │   ├── login_screen.dart
│   │   ├── home_screen.dart
│   │   ├── checkin_screen.dart
│   │   ├── support_screen.dart
│   │   └── profile_screen.dart
│   │
│   ├── services/             # API service layer
│   │   └── api_service.dart  # HTTP client + auth token management
│   │
│   ├── models/               # Dart data models
│   │   ├── user_model.dart
│   │   └── wellness_model.dart
│   │
│   ├── providers/            # Provider state management
│   │   └── auth_provider.dart
│   │
│   └── widgets/              # Reusable UI widgets
│
├── assets/
│   ├── images/               # App images and illustrations
│   └── icons/                # App icons
│
├── android/                  # Android-specific configuration
├── ios/                      # iOS-specific configuration
├── pubspec.yaml              # Flutter dependencies
└── README.md
```

### API Configuration

Find the API base URL constant in `lib/services/api_service.dart`:

```dart
// Development (Android Emulator)
const String kBaseUrl = 'http://10.0.2.2:8000/api/v1';

// Development (Physical Device — use your machine's LAN IP)
const String kBaseUrl = 'http://192.168.1.X:8000/api/v1';

// Production
const String kBaseUrl = 'https://your-domain.com/api/v1';

// Cloudflare Tunnel (for demos)
const String kBaseUrl = 'https://xxxx.trycloudflare.com/api/v1';
```

### Flutter Commands

```bash
cd mobile_app

# Get all packages
flutter pub get

# Check available devices
flutter devices

# Run on Android device/emulator
flutter run

# Run on Chrome (web)
flutter run -d chrome

# Build debug APK
flutter build apk --debug

# Build release APK (requires signing config)
flutter build apk --release

# Install to connected Android device
flutter install

# Check Flutter environment
flutter doctor
```

### Secure Storage

JWT tokens are stored using `flutter_secure_storage`:

```dart
// Token is automatically managed by api_service.dart
// Stored securely in Android Keystore / iOS Keychain
// Cleared on logout
```

---

## 🐳 Docker — Frontend Services

### Web Dashboard Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Nginx Configuration (`nginx.conf`)

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — redirect all to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Build & Run Docker Services

```bash
# Build web dashboard image
docker build -t manrakshak-dashboard ./web_dashboard

# Run web dashboard container
docker run -p 8080:80 manrakshak-dashboard

# Via docker-compose (recommended)
docker-compose up web_dashboard -d
```
