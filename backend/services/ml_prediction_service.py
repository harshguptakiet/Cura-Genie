"""
ML Prediction Service for CuraGenie
Provides real-time disease risk prediction using pre-trained models
"""

import logging
import pickle
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import json

logger = logging.getLogger(__name__)

class MLPredictionService:
    """Service for running ML predictions on genomic and clinical data"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = {}
        self.model_metadata = {}
        self.models_dir = "models"
        
        # Load all available models
        self._load_models()
    
    def _load_models(self):
        """Load all available ML models"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(self.models_dir, exist_ok=True)
            
            # Load diabetes model
            self._load_diabetes_model()
            
            # Load Alzheimer's model
            self._load_alzheimer_model()
            
            # Load brain tumor model
            self._load_brain_tumor_model()
            
            logger.info(f"✅ ML models loaded: {list(self.models.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Error loading ML models: {e}")
    
    def _load_diabetes_model(self):
        """Load diabetes prediction model"""
        try:
            model_path = os.path.join(self.models_dir, "diabetes_model.pkl")
            scaler_path = os.path.join(self.models_dir, "diabetes_scaler.pkl")
            features_path = os.path.join(self.models_dir, "diabetes_features.json")
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models['diabetes'] = pickle.load(f)
                logger.info("✅ Diabetes model loaded from file")
            else:
                # Create and train a new diabetes model
                self._create_diabetes_model()
            
            # Load scaler and features
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers['diabetes'] = pickle.load(f)
            else:
                self.scalers['diabetes'] = StandardScaler()
            
            if os.path.exists(features_path):
                with open(features_path, 'r') as f:
                    self.feature_names['diabetes'] = json.load(f)
            else:
                self.feature_names['diabetes'] = [
                    'pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
                    'insulin', 'bmi', 'diabetes_pedigree', 'age'
                ]
                
        except Exception as e:
            logger.error(f"❌ Error loading diabetes model: {e}")
    
    def _load_alzheimer_model(self):
        """Load Alzheimer's prediction model"""
        try:
            model_path = os.path.join(self.models_dir, "alzheimer_model.pkl")
            scaler_path = os.path.join(self.models_dir, "alzheimer_scaler.pkl")
            features_path = os.path.join(self.models_dir, "alzheimer_features.json")
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models['alzheimer'] = pickle.load(f)
                logger.info("✅ Alzheimer's model loaded from file")
            else:
                # Create and train a new Alzheimer's model
                self._create_alzheimer_model()
            
            # Load scaler and features
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers['alzheimer'] = pickle.load(f)
            else:
                self.scalers['alzheimer'] = StandardScaler()
            
            if os.path.exists(features_path):
                with open(features_path, 'r') as f:
                    self.feature_names['alzheimer'] = json.load(f)
            else:
                self.feature_names['alzheimer'] = [
                    'age', 'education', 'ses', 'mmse', 'cdr', 'etiv', 'nwbv', 'asf'
                ]
                
        except Exception as e:
            logger.error(f"❌ Error loading Alzheimer's model: {e}")
    
    def _load_brain_tumor_model(self):
        """Load brain tumor prediction model"""
        try:
            model_path = os.path.join(self.models_dir, "brain_tumor_model.pkl")
            scaler_path = os.path.join(self.models_dir, "brain_tumor_scaler.pkl")
            features_path = os.path.join(self.models_dir, "brain_tumor_features.json")
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models['brain_tumor'] = pickle.load(f)
                logger.info("✅ Brain tumor model loaded from file")
            else:
                # Create and train a new brain tumor model
                self._create_brain_tumor_model()
            
            # Load scaler and features
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scalers['brain_tumor'] = pickle.load(f)
            else:
                self.scalers['brain_tumor'] = StandardScaler()
            
            if os.path.exists(features_path):
                with open(features_path, 'r') as f:
                    self.feature_names['brain_tumor'] = json.load(f)
            else:
                self.feature_names['brain_tumor'] = [
                    'age', 'gender', 'tumor_size', 'location', 'enhancement',
                    'edema', 'mass_effect', 'histology'
                ]
                
        except Exception as e:
            logger.error(f"❌ Error loading brain tumor model: {e}")
    
    def _create_diabetes_model(self):
        """Create and train a diabetes prediction model"""
        try:
            # Generate synthetic training data for diabetes
            np.random.seed(42)
            n_samples = 1000
            
            # Generate realistic diabetes features
            pregnancies = np.random.randint(0, 18, n_samples)
            glucose = np.random.normal(120, 30, n_samples)
            blood_pressure = np.random.normal(70, 15, n_samples)
            skin_thickness = np.random.normal(20, 10, n_samples)
            insulin = np.random.normal(80, 40, n_samples)
            bmi = np.random.normal(32, 7, n_samples)
            diabetes_pedigree = np.random.normal(0.5, 0.3, n_samples)
            age = np.random.normal(50, 15, n_samples)
            
            # Create target variable (diabetes risk)
            # Higher glucose, BMI, age increase risk
            risk_score = (
                glucose * 0.3 + 
                bmi * 0.2 + 
                age * 0.1 + 
                insulin * 0.15 + 
                blood_pressure * 0.1
            )
            diabetes_target = (risk_score > np.median(risk_score)).astype(int)
            
            # Create feature matrix
            X = np.column_stack([
                pregnancies, glucose, blood_pressure, skin_thickness,
                insulin, bmi, diabetes_pedigree, age
            ])
            
            # Train model
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            
            # Fit scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model.fit(X_scaled, diabetes_target)
            
            # Save model and scaler
            self.models['diabetes'] = model
            self.scalers['diabetes'] = scaler
            
            # Save to disk
            with open(os.path.join(self.models_dir, "diabetes_model.pkl"), 'wb') as f:
                pickle.dump(model, f)
            
            with open(os.path.join(self.models_dir, "diabetes_scaler.pkl"), 'wb') as f:
                pickle.dump(scaler, f)
            
            # Save feature names
            features = [
                'pregnancies', 'glucose', 'blood_pressure', 'skin_thickness',
                'insulin', 'bmi', 'diabetes_pedigree', 'age'
            ]
            with open(os.path.join(self.models_dir, "diabetes_features.json"), 'w') as f:
                json.dump(features, f)
            
            self.feature_names['diabetes'] = features
            
            logger.info("✅ Diabetes model created and trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating diabetes model: {e}")
    
    def _create_alzheimer_model(self):
        """Create and train an Alzheimer's prediction model"""
        try:
            # Generate synthetic training data for Alzheimer's
            np.random.seed(42)
            n_samples = 800
            
            # Generate realistic Alzheimer's features
            age = np.random.normal(75, 10, n_samples)
            education = np.random.normal(12, 4, n_samples)
            ses = np.random.normal(2.5, 1, n_samples)  # Socioeconomic status
            mmse = np.random.normal(25, 5, n_samples)  # Mini-Mental State Exam
            cdr = np.random.normal(0.5, 0.5, n_samples)  # Clinical Dementia Rating
            etiv = np.random.normal(1400, 100, n_samples)  # Estimated Total Intracranial Volume
            nwbv = np.random.normal(0.7, 0.1, n_samples)  # Normalized Whole Brain Volume
            asf = np.random.normal(1.2, 0.2, n_samples)  # Atlas Scaling Factor
            
            # Create target variable (Alzheimer's risk)
            # Lower MMSE, higher CDR, lower NWBV increase risk
            risk_score = (
                (30 - mmse) * 0.4 +  # Lower MMSE = higher risk
                cdr * 0.3 +           # Higher CDR = higher risk
                (1.0 - nwbv) * 0.2 + # Lower NWBV = higher risk
                age * 0.1             # Higher age = higher risk
            )
            alzheimer_target = (risk_score > np.median(risk_score)).astype(int)
            
            # Create feature matrix
            X = np.column_stack([age, education, ses, mmse, cdr, etiv, nwbv, asf])
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Fit scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model.fit(X_scaled, alzheimer_target)
            
            # Save model and scaler
            self.models['alzheimer'] = model
            self.scalers['alzheimer'] = scaler
            
            # Save to disk
            with open(os.path.join(self.models_dir, "alzheimer_model.pkl"), 'wb') as f:
                pickle.dump(model, f)
            
            with open(os.path.join(self.models_dir, "alzheimer_scaler.pkl"), 'wb') as f:
                pickle.dump(scaler, f)
            
            # Save feature names
            features = ['age', 'education', 'ses', 'mmse', 'cdr', 'etiv', 'nwbv', 'asf']
            with open(os.path.join(self.models_dir, "alzheimer_features.json"), 'w') as f:
                json.dump(features, f)
            
            self.feature_names['alzheimer'] = features
            
            logger.info("✅ Alzheimer's model created and trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating Alzheimer's model: {e}")
    
    def _create_brain_tumor_model(self):
        """Create and train a brain tumor prediction model"""
        try:
            # Generate synthetic training data for brain tumors
            np.random.seed(42)
            n_samples = 600
            
            # Generate realistic brain tumor features
            age = np.random.normal(55, 20, n_samples)
            gender = np.random.randint(0, 2, n_samples)  # 0=female, 1=male
            tumor_size = np.random.normal(30, 15, n_samples)  # mm
            location = np.random.randint(0, 4, n_samples)  # 0=frontal, 1=temporal, 2=parietal, 3=occipital
            enhancement = np.random.randint(0, 3, n_samples)  # 0=none, 1=ring, 2=heterogeneous
            edema = np.random.randint(0, 2, n_samples)  # 0=no, 1=yes
            mass_effect = np.random.randint(0, 2, n_samples)  # 0=no, 1=yes
            histology = np.random.randint(0, 4, n_samples)  # 0=glioma, 1=meningioma, 2=metastatic, 3=other
            
            # Create target variable (tumor malignancy risk)
            # Larger size, presence of edema/mass effect, certain locations increase risk
            risk_score = (
                tumor_size * 0.3 +           # Larger = higher risk
                edema * 0.25 +               # Edema = higher risk
                mass_effect * 0.25 +         # Mass effect = higher risk
                (location == 1) * 0.1 +      # Temporal lobe = higher risk
                (histology == 0) * 0.1       # Glioma = higher risk
            )
            malignancy_target = (risk_score > np.median(risk_score)).astype(int)
            
            # Create feature matrix
            X = np.column_stack([age, gender, tumor_size, location, enhancement, edema, mass_effect, histology])
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                random_state=42
            )
            
            # Fit scaler
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model.fit(X_scaled, malignancy_target)
            
            # Save model and scaler
            self.models['brain_tumor'] = model
            self.scalers['brain_tumor'] = scaler
            
            # Save to disk
            with open(os.path.join(self.models_dir, "brain_tumor_model.pkl"), 'wb') as f:
                pickle.dump(model, f)
            
            with open(os.path.join(self.models_dir, "brain_tumor_scaler.pkl"), 'wb') as f:
                pickle.dump(scaler, f)
            
            # Save feature names
            features = ['age', 'gender', 'tumor_size', 'location', 'enhancement', 'edema', 'mass_effect', 'histology']
            with open(os.path.join(self.models_dir, "brain_tumor_features.json"), 'w') as f:
                json.dump(features, f)
            
            self.feature_names['brain_tumor'] = features
            
            logger.info("✅ Brain tumor model created and trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating brain tumor model: {e}")
    
    def predict_diabetes_risk(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict diabetes risk from clinical data"""
        try:
            if 'diabetes' not in self.models:
                return {"error": "Diabetes model not available"}
            
            # Extract features
            features = []
            for feature_name in self.feature_names['diabetes']:
                value = clinical_data.get(feature_name, 0)
                features.append(float(value))
            
            # Scale features
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scalers['diabetes'].transform(X)
            
            # Make prediction
            model = self.models['diabetes']
            prediction = model.predict(X_scaled)[0]
            prediction_proba = model.predict_proba(X_scaled)[0]
            
            # Calculate risk score and interpretation
            risk_score = prediction_proba[1] if len(prediction_proba) > 1 else 0.5
            risk_level = self._interpret_risk_score(risk_score)
            
            return {
                "prediction": int(prediction),
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "confidence": float(max(prediction_proba)),
                "features_used": self.feature_names['diabetes'],
                "model_type": "GradientBoostingClassifier"
            }
            
        except Exception as e:
            logger.error(f"Error in diabetes prediction: {e}")
            return {"error": str(e)}
    
    def predict_alzheimer_risk(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict Alzheimer's risk from clinical data"""
        try:
            if 'alzheimer' not in self.models:
                return {"error": "Alzheimer's model not available"}
            
            # Extract features
            features = []
            for feature_name in self.feature_names['alzheimer']:
                value = clinical_data.get(feature_name, 0)
                features.append(float(value))
            
            # Scale features
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scalers['alzheimer'].transform(X)
            
            # Make prediction
            model = self.models['alzheimer']
            prediction = model.predict(X_scaled)[0]
            prediction_proba = model.predict_proba(X_scaled)[0]
            
            # Calculate risk score and interpretation
            risk_score = prediction_proba[1] if len(prediction_proba) > 1 else 0.5
            risk_level = self._interpret_risk_score(risk_score)
            
            return {
                "prediction": int(prediction),
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "confidence": float(max(prediction_proba)),
                "features_used": self.feature_names['alzheimer'],
                "model_type": "RandomForestClassifier"
            }
            
        except Exception as e:
            logger.error(f"Error in Alzheimer's prediction: {e}")
            return {"error": str(e)}
    
    def predict_brain_tumor_risk(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict brain tumor malignancy risk from clinical data"""
        try:
            if 'brain_tumor' not in self.models:
                return {"error": "Brain tumor model not available"}
            
            # Extract features
            features = []
            for feature_name in self.feature_names['brain_tumor']:
                value = clinical_data.get(feature_name, 0)
                features.append(float(value))
            
            # Scale features
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scalers['brain_tumor'].transform(X)
            
            # Make prediction
            model = self.models['brain_tumor']
            prediction = model.predict(X_scaled)[0]
            prediction_proba = model.predict_proba(X_scaled)[0]
            
            # Calculate risk score and interpretation
            risk_score = prediction_proba[1] if len(prediction_proba) > 1 else 0.5
            risk_level = self._interpret_risk_score(risk_score)
            
            return {
                "prediction": int(prediction),
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "confidence": float(max(prediction_proba)),
                "features_used": self.feature_names['brain_tumor'],
                "model_type": "RandomForestClassifier"
            }
            
        except Exception as e:
            logger.error(f"Error in brain tumor prediction: {e}")
            return {"error": str(e)}
    
    def _interpret_risk_score(self, risk_score: float) -> str:
        """Interpret risk score into human-readable categories"""
        if risk_score >= 0.8:
            return "Very High Risk"
        elif risk_score >= 0.6:
            return "High Risk"
        elif risk_score >= 0.4:
            return "Moderate Risk"
        elif risk_score >= 0.2:
            return "Low Risk"
        else:
            return "Very Low Risk"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "available_models": list(self.models.keys()),
            "model_types": {name: type(model).__name__ for name, model in self.models.items()},
            "feature_counts": {name: len(features) for name, features in self.feature_names.items()},
            "models_directory": self.models_dir
        }
