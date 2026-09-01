# ManRakshak Web Dashboard

The **Web Dashboard** is a React-based frontend application built for Commanders, Welfare Officers, and Administrators.

## Overview
This dashboard acts as the central command center for organizational wellness. Depending on the user's role (RBAC), they can:
- View organization-wide and unit-specific wellness analytics.
- Identify personnel flagged by the AI engine as "At Risk" of burnout or high stress.
- Manage and resolve support requests submitted by personnel.
- Create, assign, and track interventions (e.g., granting leave, assigning counseling).

## Tech Stack
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router DOM
- **Icons**: Lucide React
- **Charts**: Recharts

## Setup Instructions

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`.

3. **Build for Production**
   ```bash
   npm run build
   ```

## Note on Environment Variables
Ensure the dashboard is pointing to the correct backend API URL. In a local development environment, it connects to the FastAPI server running on `http://localhost:8000`.
