import os
from typing import Dict, Any

try:
    import joblib
    import shap
    import pandas as pd
except ImportError:
    joblib = None
    shap = None
    pandas = None

class AIService:
    def __init__(self):
        self.calibrated_model = None
        self.feature_names = None
        self.model = None
        self.explainer = None
        self._load_models()
        
    def _load_models(self):
        # We assume the models are placed in a 'models' directory at the backend root or ai_engine root
        # Let's use an absolute path or relative to backend/
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        models_dir = os.path.join(base_path, 'ai_engine', 'models')
        
        if not joblib:
            return
            
        try:
            self.calibrated_model = joblib.load(os.path.join(models_dir, 'calibrated_xgboost.pkl'))
            self.feature_names = joblib.load(os.path.join(models_dir, 'feature_names.pkl'))
            self.model = joblib.load(os.path.join(models_dir, 'base_xgboost_for_shap.pkl'))
            if shap:
                self.explainer = shap.TreeExplainer(self.model)
        except Exception as e:
            print(f"Warning: Could not load AI models from {models_dir}: {e}")
            
    def predict_risk(self, features_dict: Dict[str, Any]) -> Dict[str, Any]:
        if not self.calibrated_model:
            return {
                'risk_probability': 0.0,
                'risk_category': 'Unknown (Model not loaded)',
                'confidence': 0.0,
                'top_factors': []
            }
            
        df = pd.DataFrame([features_dict])
        
        # Ensure correct column order
        # Fill missing features with 0 for safety
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0
                
        X = df[self.feature_names]
        
        prob = self.calibrated_model.predict_proba(X)[0][1]
        confidence = abs(prob - 0.5) * 2.0
        
        shap_values = self.explainer.shap_values(X)[0]
        
        shap_dict = {feat: float(val) for feat, val in zip(self.feature_names, shap_values)}
        sorted_shap = sorted(shap_dict.items(), key=lambda item: abs(item[1]), reverse=True)
        
        top_factors = [{'feature': k, 'impact': v} for k, v in sorted_shap if v > 0][:3]
        
        return {
            'risk_probability': float(prob),
            'risk_category': 'Elevated' if prob >= 0.5 else 'Normal',
            'confidence': float(confidence),
            'top_factors': top_factors
        }

ai_service = AIService()
