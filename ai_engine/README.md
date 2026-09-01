# ManRakshak AI Engine

The **AI Engine** is a machine learning component responsible for analyzing personnel wellness data, duty logs, and check-ins to predict the risk of severe stress or burnout.

## Overview
The engine uses **XGBoost** combined with **CalibratedClassifierCV** to output reliable risk probabilities. To ensure the predictions are transparent and actionable for Welfare Officers, the engine uses **SHAP (SHapley Additive exPlanations)** to extract the top contributing factors (e.g., "Lack of sleep", "Consecutive night shifts") for each prediction.

## Tech Stack
- **Python Data Stack**: Pandas, Numpy
- **Machine Learning**: Scikit-Learn, XGBoost
- **Explainable AI**: SHAP
- **Model Serialization**: Joblib

## Features
- **Temporal Baseline Generation**: Calculates personal baselines (e.g., 7-day average sleep) and deviations to detect sudden behavioral shifts.
- **Risk Prediction**: Outputs a probability score and risk category (Elevated/Normal).
- **Explainability**: Returns the top factors driving the risk score up.

## Setup & Training

1. **Install Dependencies**
   Ensure you are using the backend's virtual environment or create a new one:
   ```bash
   pip install pandas numpy xgboost scikit-learn shap joblib
   ```

2. **Train the Model**
   Run the model script to train the XGBoost classifier on the synthetic dataset.
   ```bash
   python model.py
   ```
   This will output serialized model files (`.pkl`) into the `models/` directory, which can then be loaded by the FastAPI backend for real-time inference.
