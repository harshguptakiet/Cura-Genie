"""
Simplified Report Generator
Works with minimal dependencies (basic Python only)
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random

@dataclass
class SimpleVariant:
    """Simplified variant representation"""
    chrom: str
    pos: int
    ref: str
    alt: str
    significance: Optional[str] = None
    frequency: Optional[float] = None
    impact: Optional[str] = None

@dataclass
class SimpleDiseaseAssessment:
    """Simplified disease assessment"""
    disease: str
    risk_score: float
    risk_category: str
    confidence: float
    key_factors: List[str]
    recommendations: List[str]

class SimpleReportGenerator:
    """Simplified report generator without numpy/pandas dependencies"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_report(self, 
                       variants: List[SimpleVariant],
                       disease_assessments: List[SimpleDiseaseAssessment],
                       processing_time: float) -> Dict[str, Any]:
        """Generate a comprehensive genomic analysis report"""
        
        try:
            report = {
                "report_metadata": self._generate_metadata(processing_time),
                "executive_summary": self._generate_executive_summary(disease_assessments),
                "disease_assessments": self._generate_disease_assessments(disease_assessments),
                "variant_analysis": self._generate_variant_analysis(variants),
                "key_findings": self._extract_key_findings(variants, disease_assessments),
                "recommendations": self._generate_overall_recommendations(disease_assessments),
                "technical_details": self._generate_technical_details(variants, processing_time)
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return self._generate_error_report(str(e))
    
    def _generate_metadata(self, processing_time: float) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            "generated_at": self.timestamp,
            "processing_time_seconds": round(processing_time, 2),
            "report_version": "1.0",
            "analysis_type": "Enhanced Genomic Risk Assessment",
            "supported_diseases": ["Diabetes", "Alzheimer's Disease", "Brain Tumor"]
        }
    
    def _generate_executive_summary(self, disease_assessments: List[SimpleDiseaseAssessment]) -> Dict[str, Any]:
        """Generate executive summary"""
        if not disease_assessments:
            return {
                "overall_risk": "Unknown",
                "primary_concern": "No disease assessments available",
                "summary": "Unable to generate risk assessment summary"
            }
        
        # Calculate overall risk
        risk_scores = [da.risk_score for da in disease_assessments]
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        if avg_risk < 0.3:
            overall_risk = "Low"
        elif avg_risk < 0.6:
            overall_risk = "Moderate"
        else:
            overall_risk = "High"
        
        # Find highest risk disease
        highest_risk = max(disease_assessments, key=lambda x: x.risk_score)
        
        return {
            "overall_risk": overall_risk,
            "primary_concern": highest_risk.disease,
            "highest_risk_score": round(highest_risk.risk_score, 3),
            "summary": f"Overall genomic risk assessment indicates {overall_risk.lower()} risk across all analyzed conditions. Primary concern is {highest_risk.disease} with a risk score of {highest_risk.risk_score:.3f}."
        }
    
    def _generate_disease_assessments(self, disease_assessments: List[SimpleDiseaseAssessment]) -> List[Dict[str, Any]]:
        """Generate detailed disease assessments"""
        assessments = []
        
        for assessment in disease_assessments:
            assessment_dict = {
                "disease": assessment.disease,
                "risk_score": round(assessment.risk_score, 3),
                "risk_category": assessment.risk_category,
                "confidence": round(assessment.confidence, 3),
                "key_factors": assessment.key_factors,
                "recommendations": assessment.recommendations,
                "risk_level_description": self._get_risk_description(assessment.risk_score)
            }
            assessments.append(assessment_dict)
        
        return assessments
    
    def _get_risk_description(self, risk_score: float) -> str:
        """Get human-readable risk description"""
        if risk_score < 0.2:
            return "Very low risk - Continue normal health monitoring"
        elif risk_score < 0.4:
            return "Low risk - Maintain healthy lifestyle habits"
        elif risk_score < 0.6:
            return "Moderate risk - Consider increased monitoring and lifestyle changes"
        elif risk_score < 0.8:
            return "High risk - Consult healthcare provider and consider screening"
        else:
            return "Very high risk - Immediate medical consultation recommended"
    
    def _generate_variant_analysis(self, variants: List[SimpleVariant]) -> Dict[str, Any]:
        """Generate variant analysis summary"""
        if not variants:
            return {
                "total_variants": 0,
                "significant_variants": 0,
                "variant_types": {},
                "impact_distribution": {}
            }
        
        # Count variants by type
        variant_types = {}
        impact_distribution = {}
        significant_count = 0
        
        for variant in variants:
            # Count by type
            var_type = f"{len(variant.ref)}->{len(variant.alt)}"
            variant_types[var_type] = variant_types.get(var_type, 0) + 1
            
            # Count by impact
            impact = variant.impact or "unknown"
            impact_distribution[impact] = impact_distribution.get(impact, 0) + 1
            
            # Count significant variants
            if variant.significance and "pathogenic" in variant.significance.lower():
                significant_count += 1
        
        return {
            "total_variants": len(variants),
            "significant_variants": significant_count,
            "variant_types": variant_types,
            "impact_distribution": impact_distribution,
            "top_variants": self._get_top_variants(variants)
        }
    
    def _get_top_variants(self, variants: List[SimpleVariant]) -> List[Dict[str, Any]]:
        """Get top variants by significance"""
        # Sort variants by significance (simplified scoring)
        scored_variants = []
        
        for variant in variants:
            score = 0
            if variant.significance:
                if "pathogenic" in variant.significance.lower():
                    score += 10
                elif "likely_pathogenic" in variant.significance.lower():
                    score += 8
                elif "uncertain" in variant.significance.lower():
                    score += 5
            
            if variant.frequency and variant.frequency < 0.01:
                score += 3  # Rare variants get higher score
            
            scored_variants.append((score, variant))
        
        # Sort by score and return top 5
        scored_variants.sort(key=lambda x: x[0], reverse=True)
        
        top_variants = []
        for score, variant in scored_variants[:5]:
            top_variants.append({
                "position": f"{variant.chrom}:{variant.pos}",
                "change": f"{variant.ref} -> {variant.alt}",
                "significance": variant.significance or "Unknown",
                "frequency": variant.frequency or "Unknown",
                "impact": variant.impact or "Unknown",
                "relevance_score": score
            })
        
        return top_variants
    
    def _extract_key_findings(self, variants: List[SimpleVariant], 
                             disease_assessments: List[SimpleDiseaseAssessment]) -> List[str]:
        """Extract key findings from the analysis"""
        findings = []
        
        # Disease-related findings
        for assessment in disease_assessments:
            if assessment.risk_score > 0.6:
                findings.append(f"High risk detected for {assessment.disease} (Score: {assessment.risk_score:.3f})")
            elif assessment.risk_score > 0.4:
                findings.append(f"Moderate risk detected for {assessment.disease} (Score: {assessment.risk_score:.3f})")
        
        # Variant-related findings
        if variants:
            pathogenic_count = sum(1 for v in variants if v.significance and "pathogenic" in v.significance.lower())
            if pathogenic_count > 0:
                findings.append(f"Found {pathogenic_count} potentially pathogenic variants")
            
            rare_variants = sum(1 for v in variants if v.frequency and v.frequency < 0.01)
            if rare_variants > 0:
                findings.append(f"Identified {rare_variants} rare variants (frequency < 1%)")
        
        if not findings:
            findings.append("No significant findings detected in this analysis")
        
        return findings
    
    def _generate_overall_recommendations(self, disease_assessments: List[SimpleDiseaseAssessment]) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        if not disease_assessments:
            recommendations.append("Consult with a healthcare provider for comprehensive assessment")
            return recommendations
        
        # Overall recommendations based on highest risk
        highest_risk = max(disease_assessments, key=lambda x: x.risk_score)
        
        if highest_risk.risk_score > 0.7:
            recommendations.append("Schedule immediate consultation with healthcare provider")
            recommendations.append("Consider genetic counseling services")
            recommendations.append("Implement preventive screening measures")
        elif highest_risk.risk_score > 0.5:
            recommendations.append("Schedule regular health monitoring")
            recommendations.append("Consider lifestyle modifications")
            recommendations.append("Discuss family history with healthcare provider")
        else:
            recommendations.append("Continue regular health monitoring")
            recommendations.append("Maintain healthy lifestyle habits")
        
        # Add general recommendations
        recommendations.append("Keep detailed family health history records")
        recommendations.append("Stay informed about new genetic research")
        recommendations.append("Consider participating in genetic research studies")
        
        return recommendations
    
    def _generate_technical_details(self, variants: List[SimpleVariant], 
                                  processing_time: float) -> Dict[str, Any]:
        """Generate technical details"""
        return {
            "analysis_parameters": {
                "variant_count": len(variants),
                "processing_time_seconds": round(processing_time, 2),
                "analysis_date": self.timestamp
            },
            "quality_metrics": {
                "data_completeness": "High" if variants else "Low",
                "processing_efficiency": "Good" if processing_time < 60 else "Acceptable"
            },
            "limitations": [
                "Analysis based on available genetic markers",
                "Risk scores are estimates and not diagnostic",
                "Environmental factors not considered in this analysis",
                "Results should be interpreted by qualified healthcare professionals"
            ]
        }
    
    def _generate_error_report(self, error_message: str) -> Dict[str, Any]:
        """Generate error report when something goes wrong"""
        return {
            "error": True,
            "error_message": error_message,
            "generated_at": self.timestamp,
            "report_status": "Failed to generate complete report"
        }

# Test function
def test_report_generator():
    """Test the report generator"""
    generator = SimpleReportGenerator()
    
    # Create test data
    variants = [
        SimpleVariant("chr1", 1000, "A", "T", "likely_pathogenic", 0.001, "transition"),
        SimpleVariant("chr2", 2000, "AT", "A", "uncertain_significance", 0.05, "deletion"),
        SimpleVariant("chr3", 3000, "C", "G", "benign", 0.2, "transversion")
    ]
    
    disease_assessments = [
        SimpleDiseaseAssessment("Diabetes", 0.7, "High", 0.8, 
                               ["High genetic predisposition"], 
                               ["Consult healthcare provider", "Monitor blood glucose"]),
        SimpleDiseaseAssessment("Alzheimer's Disease", 0.4, "Moderate", 0.7,
                               ["APOE gene variants"], 
                               ["Regular check-ups", "Cognitive monitoring"]),
        SimpleDiseaseAssessment("Brain Tumor", 0.2, "Low", 0.6,
                               ["Standard genetic background"], 
                               ["Continue monitoring", "Healthy lifestyle"])
    ]
    
    # Generate report
    report = generator.generate_report(variants, disease_assessments, 45.2)
    
    # Print report
    print("Generated Report:")
    print("=" * 50)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    test_report_generator()
