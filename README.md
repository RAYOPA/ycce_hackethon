# ManRakshak AI: Organizational Wellness & Stress Management Platform

ManRakshak AI is a comprehensive platform designed to manage and monitor the stress, workload, and overall wellness of personnel in high-stress organizations. It provides actionable insights, AI-driven risk predictions, and intervention management.

## Project Structure

This project is divided into several micro-components:

1. **[backend/](./backend/README.md)**: The core FastAPI server that powers the platform. It handles the PostgreSQL database, authentication, role-based access control (RBAC), and serves the REST APIs.
2. **[web_dashboard/](./web_dashboard/README.md)**: A React-based web dashboard used by Commanders, Welfare Officers, and Administrators to monitor wellness metrics, handle support requests, and assign interventions.
3. **[mobile_app/](./mobile_app/README.md)**: A Flutter-based mobile application intended for use by the Personnel on the field. It allows them to submit daily wellness check-ins, view resources, and request support.
4. **[mobile_web_app/](./mobile_web_app/README.md)**: A React JS web equivalent of the personnel mobile app, providing a lightweight way for personnel to access the platform via their mobile browsers.
5. **[ai_engine/](./ai_engine/README.md)**: The Machine Learning module that trains an XGBoost model on personnel data to predict stress and burnout risk, providing explainable AI (SHAP) factors.
6. **data_generation/**: Scripts and utilities used to generate synthetic welfare data for testing and model training.

## Getting Started

To run the full stack locally using Docker:
```bash
docker-compose up -d
```
This will spin up the database, the backend, and the dashboards simultaneously. 

For component-specific setup (e.g., running the Flutter app on your phone), please see the respective `README.md` file in that component's folder.
