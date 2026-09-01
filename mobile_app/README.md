# ManRakshak Mobile App (Flutter)

The **Mobile App** is a cross-platform (Android/iOS) frontend application built with Flutter. It is designed for the **Personnel** (end-users on the field) to interact with the ManRakshak wellness platform.

## Overview
This app provides a streamlined, accessible interface for personnel to:
- **Daily Wellness Check-in**: Submit scores for sleep, mood, energy, workload, and stress.
- **Support Requests**: Reach out to Welfare Officers or request professional help anonymously or directly.
- **Resource Center**: Access mental health resources, breathing exercises, and policy information.
- **Notifications**: Receive alerts regarding assigned interventions or follow-ups.

## Tech Stack
- **Framework**: Flutter (Dart)
- **State Management**: Provider
- **Networking**: `http` package (REST to FastAPI backend)
- **Charts**: FL Chart

## Network Configuration for Physical Devices
If you are running the app on a physical mobile device, the app cannot connect to `localhost` or `127.0.0.1`.
You must update the API Base URL to your computer's local network IP address:
1. Open `lib/core/constants.dart`.
2. Change `apiBaseUrl` to your local IP (e.g., `http://192.168.1.5:8000/api/v1`).
3. Ensure the backend FastAPI server is running with `--host 0.0.0.0`.

## Running the App

1. **Install Dependencies**
   ```bash
   flutter pub get
   ```

2. **Run on Device / Emulator**
   Connect your device via USB or start an emulator, then run:
   ```bash
   flutter run
   ```
