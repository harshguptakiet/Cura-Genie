import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from genomic_utils import GenomicProcessor
from db.models import GenomicData, PrsScore
from db.auth_models import User, PatientProfile, MedicalReport

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Real-time medical report generation service"""
    
    def __init__(self):
        self.genomic_processor = GenomicProcessor()
    
    def generate_comprehensive_report(self, user_id: int, genomic_data_id: int, db: Session) -> Dict[str, Any]:
        """Generate a comprehensive medical report for a user's genomic data"""
        
        try:
            # Get user and profile
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"status": "error", "message": "User not found"}
                
            profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
            
            # Get genomic data
            genomic_data = db.query(GenomicData).filter(GenomicData.id == genomic_data_id).first()
            if not genomic_data:
                return {"status": "error", "message": "Genomic data not found"}
            
            # Get PRS scores
            prs_scores = db.query(PrsScore).filter(PrsScore.genomic_data_id == genomic_data_id).all()
            
            # Process the genomic file for detailed analysis
            file_analysis = None
            if genomic_data.file_url:
                try:
                    with open(genomic_data.file_url, 'rb') as f:
                        file_content = f.read()
                    file_analysis = self.genomic_processor.process_genomic_file(
                        file_content, genomic_data.filename
                    )
                except Exception as e:
                    logger.warning(f"Could not reprocess genomic file: {e}")
            
            # Generate comprehensive report
            report_data = {
                "report_id": f"RPT_{genomic_data_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "patient_info": self._get_patient_info(user, profile),
                "genomic_summary": self._get_genomic_summary(genomic_data, file_analysis),
                "risk_assessment": self._get_risk_assessment(prs_scores),
                "recommendations": self._generate_recommendations(prs_scores, profile),
                "detailed_analysis": file_analysis,
                "quality_assessment": self._get_quality_assessment(file_analysis),
                "next_steps": self._get_next_steps(prs_scores)
            }
            
            # Save report to database
            medical_report = MedicalReport(
                user_id=user_id,
                genomic_data_id=genomic_data_id,
                report_title=f"Comprehensive Genomic Analysis - {genomic_data.filename}",
                report_type="comprehensive_genomic",
                report_data=json.dumps(report_data),
                summary=self._generate_summary(report_data),
                recommendations=self._format_recommendations(report_data["recommendations"]),
                status="completed"
            )
            
            db.add(medical_report)
            db.commit()
            db.refresh(medical_report)
            
            report_data["report_db_id"] = medical_report.id
            
            return {
                "status": "success",
                "report": report_data
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate report: {str(e)}"
            }
    
    def _get_patient_info(self, user: User, profile: PatientProfile) -> Dict[str, Any]:
        """Extract patient information for the report"""
        info = {
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "account_created": user.created_at.isoformat() if user.created_at else None
        }
        
        if profile:
            info.update({
                "name": f"{profile.first_name} {profile.last_name}".strip(),
                "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                "age": self._calculate_age(profile.date_of_birth) if profile.date_of_birth else None,
                "gender": profile.gender,
                "blood_type": profile.blood_type,
                "allergies": profile.allergies,
                "current_medications": profile.current_medications,
                "medical_history": profile.medical_history
            })
        
        return info
    
    def _get_genomic_summary(self, genomic_data: GenomicData, file_analysis: Dict) -> Dict[str, Any]:
        """Generate genomic data summary"""
        summary = {
            "filename": genomic_data.filename,
            "uploaded_at": genomic_data.uploaded_at.isoformat() if genomic_data.uploaded_at else None,
            "file_size": None,
            "file_type": None,
            "processing_status": genomic_data.status
        }
        
        # Parse metadata
        try:
            metadata = json.loads(genomic_data.metadata_json) if genomic_data.metadata_json else {}
            summary["file_size"] = metadata.get("file_size_bytes")
            summary["upload_method"] = metadata.get("upload_method")
        except:
            pass
        
        # Add file analysis results
        if file_analysis and "status" not in file_analysis:
            summary.update({
                "file_type": file_analysis.get("file_type"),
                "total_variants": file_analysis.get("total_variants"),
                "total_sequences": file_analysis.get("total_sequences"),
                "analysis_quality": file_analysis.get("quality_assessment", {}).get("overall_quality")
            })
        
        return summary
    
    def _get_risk_assessment(self, prs_scores: List[PrsScore]) -> Dict[str, Any]:
        """Generate risk assessment from PRS scores"""
        assessment = {
            "total_conditions_analyzed": len(prs_scores),
            "high_risk_conditions": [],
            "moderate_risk_conditions": [],
            "low_risk_conditions": [],
            "risk_summary": {}
        }
        
        for score in prs_scores:
            risk_info = {
                "disease_type": score.disease_type,
                "score": score.score,
                "calculated_at": score.calculated_at.isoformat() if score.calculated_at else None,
                "risk_level": self._interpret_risk_score(score.score)
            }
            
            if score.score >= 0.7:
                assessment["high_risk_conditions"].append(risk_info)
            elif score.score >= 0.4:
                assessment["moderate_risk_conditions"].append(risk_info)
            else:
                assessment["low_risk_conditions"].append(risk_info)
            
            assessment["risk_summary"][score.disease_type] = risk_info
        
        return assessment
    
    def _generate_recommendations(self, prs_scores: List[PrsScore], profile: PatientProfile) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on risk scores"""
        recommendations = []
        
        # General recommendations
        recommendations.append({
            "category": "General Health",
            "priority": "medium",
            "recommendation": "Maintain regular health checkups and screenings",
            "rationale": "Proactive health monitoring is essential for early detection and prevention"
        })
        
        for score in prs_scores:
            disease_type = score.disease_type
            risk_level = self._interpret_risk_score(score.score)
            
            if disease_type in ["cardiovascular_disease", "heart_disease"]:
                if score.score >= 0.6:
                    recommendations.append({
                        "category": "Cardiovascular Health",
                        "priority": "high",
                        "recommendation": "Consult with a cardiologist for comprehensive evaluation",
                        "rationale": f"Your PRS score of {score.score:.2f} indicates elevated cardiovascular risk"
                    })
                    recommendations.append({
                        "category": "Lifestyle",
                        "priority": "high",
                        "recommendation": "Adopt a heart-healthy diet and regular exercise routine",
                        "rationale": "Lifestyle modifications can significantly reduce cardiovascular risk"
                    })
                
            elif disease_type in ["diabetes_type2", "diabetes"]:
                if score.score >= 0.5:
                    recommendations.append({
                        "category": "Metabolic Health",
                        "priority": "high",
                        "recommendation": "Regular blood glucose monitoring and diabetes screening",
                        "rationale": f"Elevated diabetes risk (PRS: {score.score:.2f}) warrants closer monitoring"
                    })
                    recommendations.append({
                        "category": "Diet",
                        "priority": "medium",
                        "recommendation": "Consider consultation with a nutritionist for diabetes prevention diet",
                        "rationale": "Dietary modifications can help prevent or delay type 2 diabetes onset"
                    })
                
            elif disease_type in ["alzheimer_disease", "alzheimer"]:
                if score.score >= 0.4:
                    recommendations.append({
                        "category": "Cognitive Health",
                        "priority": "medium",
                        "recommendation": "Regular cognitive assessments and brain-healthy lifestyle practices",
                        "rationale": f"Elevated Alzheimer's risk (PRS: {score.score:.2f}) suggests need for cognitive monitoring"
                    })
                    recommendations.append({
                        "category": "Lifestyle",
                        "priority": "medium",
                        "recommendation": "Engage in regular mental stimulation and physical exercise",
                        "rationale": "These activities may help maintain cognitive health and reduce dementia risk"
                    })
        
        # Medication interaction warnings
        if profile and profile.current_medications:
            recommendations.append({
                "category": "Medication Safety",
                "priority": "high",
                "recommendation": "Discuss genomic results with your healthcare provider",
                "rationale": "Your current medications may interact with genetic predispositions"
            })
        
        return recommendations
    
    def _get_quality_assessment(self, file_analysis: Dict) -> Dict[str, Any]:
        """Extract quality assessment from file analysis"""
        if not file_analysis or "status" in file_analysis:
            return {"status": "no_analysis_available"}
        
        quality_assessment = file_analysis.get("quality_assessment", {})
        
        return {
            "overall_quality": quality_assessment.get("overall_quality", "Unknown"),
            "pass_filters": quality_assessment.get("pass_filters", False),
            "issues": quality_assessment.get("issues", []),
            "recommendations": quality_assessment.get("recommendations", [])
        }
    
    def _get_next_steps(self, prs_scores: List[PrsScore]) -> List[Dict[str, Any]]:
        """Generate next steps based on analysis results"""
        next_steps = []
        
        # Determine highest risk areas
        high_risk_scores = [score for score in prs_scores if score.score >= 0.6]
        
        if high_risk_scores:
            next_steps.append({
                "step": "Schedule specialist consultations",
                "timeframe": "Within 1-2 months",
                "description": "Based on your high-risk genetic predispositions, consult with relevant specialists",
                "priority": "high"
            })
        
        next_steps.extend([
            {
                "step": "Share results with primary care physician",
                "timeframe": "Within 2 weeks",
                "description": "Discuss your genomic analysis results with your doctor",
                "priority": "high"
            },
            {
                "step": "Consider additional genetic counseling",
                "timeframe": "Within 1 month",
                "description": "A genetic counselor can help interpret results and plan preventive measures",
                "priority": "medium"
            },
            {
                "step": "Update family medical history",
                "timeframe": "Ongoing",
                "description": "Share relevant findings with family members who might benefit",
                "priority": "low"
            },
            {
                "step": "Regular monitoring and updates",
                "timeframe": "Every 6-12 months",
                "description": "Stay updated with new genomic research relevant to your profile",
                "priority": "medium"
            }
        ])
        
        return next_steps
    
    def _interpret_risk_score(self, score: float) -> str:
        """Interpret PRS score into risk level"""
        if score >= 0.8:
            return "Very High"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Moderate"
        elif score >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def _calculate_age(self, date_of_birth: datetime) -> int:
        """Calculate age from date of birth"""
        today = datetime.now()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    def _generate_summary(self, report_data: Dict) -> str:
        """Generate text summary of the report"""
        patient_name = report_data["patient_info"].get("name", "Patient")
        total_conditions = report_data["risk_assessment"]["total_conditions_analyzed"]
        high_risk_count = len(report_data["risk_assessment"]["high_risk_conditions"])
        
        summary = f"Comprehensive genomic analysis for {patient_name}. "
        summary += f"Analyzed {total_conditions} health conditions. "
        
        if high_risk_count > 0:
            summary += f"Found {high_risk_count} high-risk condition(s) requiring attention. "
        
        summary += f"Generated {len(report_data['recommendations'])} personalized recommendations. "
        summary += "See detailed report for complete analysis and next steps."
        
        return summary
    
    def _format_recommendations(self, recommendations: List[Dict]) -> str:
        """Format recommendations as text"""
        if not recommendations:
            return "No specific recommendations generated."
        
        formatted = []
        for rec in recommendations:
            formatted.append(f"• [{rec['category']}] {rec['recommendation']} ({rec['priority']} priority)")
        
        return "\n".join(formatted)
