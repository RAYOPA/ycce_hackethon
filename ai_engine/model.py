import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import shap
import joblib
import os

class ManRakshakAIEngine:
    def __init__(self):
        self.model = None
        self.calibrated_model = None
        self.explainer = None
        self.feature_names = None
        
    def generate_temporal_features(self, df):
        """
        Creates personal baselines and temporal features (rolling averages, deviations)
        """
        print("Generating temporal and baseline features...")
        # Ensure data is sorted by personnel and date
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by=['personnel_id', 'date'])
        
        # Calculate 7-day and 14-day rolling baselines for each personnel
        # Using shift(1) to avoid data leakage (baseline shouldn't include current day)
        
        df['sleep_baseline_7d'] = df.groupby('personnel_id')['sleep_hours'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
        df['mood_baseline_7d'] = df.groupby('personnel_id')['mood_score'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
        df['workload_baseline_7d'] = df.groupby('personnel_id')['workload_perception'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
        
        # Calculate deviations from baseline
        df['sleep_deviation'] = df['sleep_hours'] - df['sleep_baseline_7d']
        df['mood_deviation'] = df['mood_score'] - df['mood_baseline_7d']
        df['workload_deviation'] = df['workload_perception'] - df['workload_baseline_7d']
        
        # Temporal aggregations (cumulative fatigue indicators)
        df['consecutive_night_duties_7d'] = df.groupby('personnel_id')['night_duty'].transform(lambda x: x.rolling(7, min_periods=1).sum())
        
        # Fill NaN values that might arise from rolling windows at the beginning of series
        df = df.fillna(0)
        
        return df

    def train(self, data_path):
        print(f"Loading data from {data_path}...")
        df = pd.read_csv(data_path)
        
        df = self.generate_temporal_features(df)
        
        # Features for the model
        self.feature_names = [
            'deployment_duration_months', 'duty_duration_hrs', 'consecutive_duty_days', 
            'night_duty', 'leave_gap_days', 'training_load', 
            'sleep_hours', 'mood_score', 'workload_perception',
            'sleep_deviation', 'mood_deviation', 'workload_deviation',
            'consecutive_night_duties_7d'
        ]
        
        X = df[self.feature_names]
        y = df['risk_flag']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        print("Training XGBoost model...")
        base_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        # Calibrate probabilities for reliable confidence estimates
        self.calibrated_model = CalibratedClassifierCV(base_model, method='sigmoid', cv=3)
        self.calibrated_model.fit(X_train, y_train)
        
        print("Evaluating model...")
        y_pred = self.calibrated_model.predict(X_test)
        y_prob = self.calibrated_model.predict_proba(X_test)[:, 1]
        
        print(classification_report(y_test, y_pred))
        print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")
        
        # Setup SHAP Explainer
        # Since CalibratedClassifierCV wraps the XGBoost model, we extract one of the base estimators for SHAP
        self.model = self.calibrated_model.calibrated_classifiers_[0].estimator
        self.explainer = shap.TreeExplainer(self.model)
        
        # Save model
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.calibrated_model, 'models/calibrated_xgboost.pkl')
        joblib.dump(self.feature_names, 'models/feature_names.pkl')
        joblib.dump(self.model, 'models/base_xgboost_for_shap.pkl')
        print("Models saved in 'models/' directory.")
        
    def load_model(self):
        self.calibrated_model = joblib.load('models/calibrated_xgboost.pkl')
        self.feature_names = joblib.load('models/feature_names.pkl')
        self.model = joblib.load('models/base_xgboost_for_shap.pkl')
        self.explainer = shap.TreeExplainer(self.model)
        
    def predict_risk(self, features_dict):
        """
        Predicts risk, confidence, and returns SHAP explanations
        """
        df = pd.DataFrame([features_dict])
        
        # Ensure correct column order
        X = df[self.feature_names]
        
        # Predict probability
        prob = self.calibrated_model.predict_proba(X)[0][1]
        
        # Calculate confidence
        # Heuristic: Confidence is higher when probability is closer to 0 or 1
        # Confidence is lower when probability is around 0.5
        confidence = abs(prob - 0.5) * 2.0  # Scales to [0, 1]
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(X)[0]
        
        # Map SHAP values to feature names and sort by absolute impact
        shap_dict = {feat: float(val) for feat, val in zip(self.feature_names, shap_values)}
        sorted_shap = sorted(shap_dict.items(), key=lambda item: abs(item[1]), reverse=True)
        
        # Get top 3 positive contributing factors (factors driving risk up)
        top_factors = [{'feature': k, 'impact': v} for k, v in sorted_shap if v > 0][:3]
        
        return {
            'risk_probability': float(prob),
            'risk_category': 'Elevated' if prob >= 0.5 else 'Normal',
            'confidence': float(confidence),
            'top_factors': top_factors
        }

if __name__ == "__main__":
    engine = ManRakshakAIEngine()
    if os.path.exists("synthetic_welfare_data.csv"):
        engine.train("synthetic_welfare_data.csv")
    elif os.path.exists("../synthetic_welfare_data.csv"):
        engine.train("../synthetic_welfare_data.csv")
    else:
        print("Run generate_data.py first to create the dataset.")
