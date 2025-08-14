"""
Simplified ML Prediction Service
Works with minimal dependencies (scikit-learn only)
"""

import json
import pickle
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import random
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

@dataclass
class DiseasePrediction:
    """Disease prediction result"""
    disease: str
    risk_score: float
    risk_category: str
    confidence: float
    key_factors: List[str]
    recommendations: List[str]

class SimpleMLPredictionService:
    """Simplified ML prediction service without numpy/pandas dependencies"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self._ensure_models_directory()
        self._load_or_create_models()
    
    def _ensure_models_directory(self):
        """Ensure the models directory exists"""
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        diseases = ['diabetes', 'alzheimer', 'brain_tumor']
        
        for disease in diseases:
            model_path = os.path.join(self.models_dir, f"{disease}_model.pkl")
            scaler_path = os.path.join(self.models_dir, f"{disease}_scaler.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                try:
                    with open(model_path, 'rb') as f:
                        self.models[disease] = pickle.load(f)
                    with open(scaler_path, 'rb') as f:
                        self.scalers[disease] = pickle.load(f)
                    print(f"Loaded existing {disease} model")
                except Exception as e:
                    print(f"Error loading {disease} model: {e}")
                    self._create_disease_model(disease)
            else:
                self._create_disease_model(disease)
    
    def _create_disease_model(self, disease: str):
        """Create a new model for a specific disease"""
        try:
            if disease == 'diabetes':
                model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            scaler = StandardScaler()
            
            # Generate synthetic training data
            X_train, y_train = self._generate_synthetic_data(disease)
            
            # Scale features
            X_train_scaled = scaler.fit_transform(X_train)
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Save model and scaler
            model_path = os.path.join(self.models_dir, f"{disease}_model.pkl")
            scaler_path = os.path.join(self.models_dir, f"{disease}_scaler.pkl")
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            
            self.models[disease] = model
            self.scalers[disease] = scaler
            
            print(f"Created and saved new {disease} model")
            
        except Exception as e:
            print(f"Error creating {disease} model: {e}")
    
    def _generate_synthetic_data(self, disease: str) -> Tuple[List[List[float]], List[int]]:
        """Generate synthetic training data for disease prediction"""
        n_samples = 1000
        n_features = 20
        
        # Generate random features
        X = []
        for _ in range(n_samples):
            sample = [random.uniform(0, 1) for _ in range(n_features)]
            X.append(sample)
        
        # Generate labels based on disease-specific patterns
        y = []
        for sample in X:
            # Simple rule-based labeling for demonstration
            if disease == 'diabetes':
                # Higher values in certain features increase diabetes risk
                risk_score = (sample[0] * 0.3 + sample[5] * 0.4 + sample[10] * 0.3)
                y.append(1 if risk_score > 0.6 else 0)
            elif disease == 'alzheimer':
                # Different feature importance for Alzheimer's
                risk_score = (sample[2] * 0.5 + sample[7] * 0.3 + sample[15] * 0.2)
                y.append(1 if risk_score > 0.7 else 0)
            else:  # brain_tumor
                # Brain tumor risk pattern
                risk_score = (sample[1] * 0.4 + sample[8] * 0.4 + sample[18] * 0.2)
                y.append(1 if risk_score > 0.65 else 0)
        
        return X, y
    
    def predict_diabetes_risk(self, features: List[float]) -> DiseasePrediction:
        """Predict diabetes risk"""
        return self._predict_disease_risk('diabetes', features)
    
    def predict_alzheimer_risk(self, features: List[float]) -> DiseasePrediction:
        """Predict Alzheimer's risk"""
        return self._predict_disease_risk('alzheimer', features)
    
    def predict_brain_tumor_risk(self, features: List[float]) -> DiseasePrediction:
        """Predict brain tumor risk"""
        return self._predict_disease_risk('brain_tumor', features)
    
    def _predict_disease_risk(self, disease: str, features: List[float]) -> DiseasePrediction:
        """Generic disease risk prediction"""
        try:
            if disease not in self.models or disease not in self.scalers:
                raise ValueError(f"Model for {disease} not available")
            
            model = self.models[disease]
            scaler = self.scalers[disease]
            
            # Ensure features list has correct length
            if len(features) < 20:
                # Pad with zeros if too short
                features = features + [0.0] * (20 - len(features))
            elif len(features) > 20:
                # Truncate if too long
                features = features[:20]
            
            # Scale features
            features_scaled = scaler.transform([features])
            
            # Get prediction probability
            prob = model.predict_proba(features_scaled)[0]
            risk_score = prob[1] if len(prob) > 1 else prob[0]
            
            # Determine risk category
            if risk_score < 0.3:
                risk_category = "Low"
            elif risk_score < 0.6:
                risk_category = "Moderate"
            else:
                risk_category = "High"
            
            # Calculate confidence
            confidence = max(prob) if len(prob) > 1 else 0.8
            
            # Generate key factors and recommendations
            key_factors = self._generate_key_factors(disease, features)
            recommendations = self._generate_recommendations(disease, risk_score)
            
            return DiseasePrediction(
                disease=disease.replace('_', ' ').title(),
                risk_score=risk_score,
                risk_category=risk_category,
                confidence=confidence,
                key_factors=key_factors,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Error predicting {disease} risk: {e}")
            # Return default prediction
            return DiseasePrediction(
                disease=disease.replace('_', ' ').title(),
                risk_score=0.5,
                risk_category="Unknown",
                confidence=0.0,
                key_factors=["Unable to analyze"],
                recommendations=["Please consult a healthcare provider"]
            )
    
    def _generate_key_factors(self, disease: str, features: List[float]) -> List[str]:
        """Generate key factors based on feature values"""
        factors = []
        
        if disease == 'diabetes':
            if features[0] > 0.7:
                factors.append("High genetic predisposition")
            if features[5] > 0.6:
                factors.append("Metabolic pathway variations")
            if features[10] > 0.5:
                factors.append("Insulin resistance markers")
        elif disease == 'alzheimer':
            if features[2] > 0.7:
                factors.append("APOE gene variants")
            if features[7] > 0.6:
                factors.append("Amyloid processing genes")
            if features[15] > 0.5:
                factors.append("Tau protein genes")
        else:  # brain_tumor
            if features[1] > 0.7:
                factors.append("Cell cycle regulation genes")
            if features[8] > 0.6:
                factors.append("DNA repair mechanisms")
            if features[18] > 0.5:
                factors.append("Tumor suppressor genes")
        
        if not factors:
            factors.append("Standard genetic background")
        
        return factors
    
    def _generate_recommendations(self, disease: str, risk_score: float) -> List[str]:
        """Generate recommendations based on disease and risk score"""
        recommendations = []
        
        if risk_score < 0.3:
            recommendations.append("Continue regular health monitoring")
            recommendations.append("Maintain healthy lifestyle habits")
        elif risk_score < 0.6:
            recommendations.append("Schedule regular check-ups")
            recommendations.append("Consider genetic counseling")
            recommendations.append("Monitor for early symptoms")
        else:
            recommendations.append("Consult healthcare provider immediately")
            recommendations.append("Consider specialized screening")
            recommendations.append("Discuss family history with doctor")
        
        # Disease-specific recommendations
        if disease == 'diabetes':
            recommendations.append("Monitor blood glucose levels")
            recommendations.append("Maintain healthy diet and exercise")
        elif disease == 'alzheimer':
            recommendations.append("Engage in cognitive activities")
            recommendations.append("Monitor memory and cognitive function")
        else:  # brain_tumor
            recommendations.append("Monitor for neurological symptoms")
            recommendations.append("Consider brain imaging if symptoms arise")
        
        return recommendations

# Test function
def test_ml_service():
    """Test the ML prediction service"""
    service = SimpleMLPredictionService()
    
    # Test features
    test_features = [random.uniform(0, 1) for _ in range(20)]
    
    print("Testing ML Prediction Service:")
    print("=" * 50)
    
    # Test diabetes prediction
    diabetes_pred = service.predict_diabetes_risk(test_features)
    print(f"Diabetes Risk: {diabetes_pred.risk_score:.3f} ({diabetes_pred.risk_category})")
    print(f"Confidence: {diabetes_pred.confidence:.3f}")
    print(f"Key Factors: {', '.join(diabetes_pred.key_factors)}")
    print(f"Recommendations: {', '.join(diabetes_pred.recommendations)}")
    print()
    
    # Test Alzheimer's prediction
    alzheimer_pred = service.predict_alzheimer_risk(test_features)
    print(f"Alzheimer's Risk: {alzheimer_pred.risk_score:.3f} ({alzheimer_pred.risk_category})")
    print(f"Confidence: {alzheimer_pred.confidence:.3f}")
    print(f"Key Factors: {', '.join(alzheimer_pred.key_factors)}")
    print(f"Recommendations: {', '.join(alzheimer_pred.recommendations)}")
    print()
    
    # Test brain tumor prediction
    tumor_pred = service.predict_brain_tumor_risk(test_features)
    print(f"Brain Tumor Risk: {tumor_pred.risk_score:.3f} ({tumor_pred.risk_category})")
    print(f"Confidence: {tumor_pred.confidence:.3f}")
    print(f"Key Factors: {', '.join(tumor_pred.key_factors)}")
    print(f"Recommendations: {', '.join(tumor_pred.recommendations)}")

if __name__ == "__main__":
    test_ml_service()
