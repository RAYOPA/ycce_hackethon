# ManRakshak Mobile Web App (React JS)

The **Mobile Web App** is a responsive, web-based alternative to the Flutter mobile application, designed using React JS. It provides the same personnel-facing functionalities but is accessible directly via a mobile web browser, eliminating the need for an app installation.

## Overview
This app serves **Personnel** users with a mobile-first UI to:
- Perform daily wellness check-ins.
- Submit and view support requests.
- Access the platform easily without downloading an APK/IPA.

## Tech Stack
- **Framework**: React 19 (TypeScript)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **Icons**: Lucide React

## Setup Instructions

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:5173` (or the next available port if the web dashboard is running).

## Note on Environment Variables
Ensure the app points to the correct backend API URL. By default, it communicates with the FastAPI server running locally at `http://localhost:8000`.
