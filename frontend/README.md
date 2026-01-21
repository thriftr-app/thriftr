# Thriftr Mobile App

React Native mobile application for Thriftr - a thrift store price estimation app built with Expo.

## Features

- 🔐 User authentication (register, login, logout)
- 📸 Image upload from camera or gallery
- 💰 Price estimation for thrifted items
- 👤 User profile management
- 🎨 Instagram-inspired UI with gradient design

## Prerequisites

- Node.js 18+
- Expo Go app (for physical device testing)
- Backend server running on your network

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure backend URL:**
   
   Edit `services/api.ts` and update the API URL:
   - For iOS Simulator: `http://localhost:8000`
   - For physical device: `http://YOUR_LOCAL_IP:8000`
   
   Find your local IP:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Run the app:**
   - **Physical device:** Install Expo Go, scan the QR code
   - **iOS Simulator:** Press `i`
   - **Android Emulator:** Press `a`
   - **Web:** Press `w`

## Project Structure

```
frontend/
├── App.tsx                    # Main app with navigation setup
├── screens/
│   ├── LoginScreen.tsx        # Login page with email/username support
│   ├── RegisterScreen.tsx     # Registration page
│   └── HomeScreen.tsx         # Main screen with image upload & price estimation
├── services/
│   └── api.ts                 # API client with authentication methods
└── package.json
```

## Tech Stack

- **Framework:** React Native with Expo SDK 54
- **Navigation:** React Navigation (Native Stack)
- **State Management:** React Hooks
- **HTTP Client:** Axios
- **Storage:** AsyncStorage (token persistence)
- **UI:** Expo Linear Gradient, Expo Image Picker, Ionicons

## Available Scripts

- `npm start` - Start Expo development server
- `npm run android` - Run on Android
- `npm run ios` - Run on iOS
- `npm run web` - Run on web browser

## API Integration

The app connects to the FastAPI backend at the configured URL. Ensure the backend is running with:

```bash
cd ../backend
make dev
```

**Important:** For physical device testing, the backend must be accessible on your local network (use `--host 0.0.0.0`).

## Authentication Flow

1. User registers/logs in
2. JWT token is stored in AsyncStorage
3. Token is automatically included in authenticated API requests
4. Token is cleared on logout

## Notes

- Supports login with username OR email
- Image picker works on iOS/Android (requires permissions)
- Price estimation endpoint currently returns 404 (feature in development)
- All validation errors from backend are displayed to users
├── screens/
│   └── LoginScreen.tsx      # Instagram-style login screen
├── services/
│   └── api.ts              # Backend API service
├── package.json
└── app.json                # Expo configuration
```

## Testing Login

Use any account you created in your backend tests, for example:
- Username: `tempuser`
- Password: `eXtR3m3ly$trongP@ssw0rd!`

The app will make a POST request to `http://localhost:8000/api/auth/token`
