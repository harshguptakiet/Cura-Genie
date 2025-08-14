"""
Report Generator for CuraGenie
Generates comprehensive genomic analysis reports
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates comprehensive genomic analysis reports"""
    
    def __init__(self):
        self.disease_templates = {
            "diabetes": {
                "description": "Type 2 Diabetes Risk Assessment",
                "recommendations": [
                    "Monitor blood glucose levels regularly",
                    "Maintain healthy diet and exercise routine",
                    "Consult with endocrinologist if risk is high"
                ]
            },
            "alzheimer": {
                "description": "Alzheimer's Disease Risk Assessment", 
                "recommendations": [
                    "Regular cognitive assessments",
                    "Maintain brain health through mental stimulation",
                    "Consult with neurologist for baseline evaluation"
                ]
            },
            "brain_tumor": {
                "description": "Brain Tumor Risk Assessment",
                "recommendations": [
                    "Regular neurological examinations",
                    "Immediate medical attention for new symptoms",
                    "Consider genetic testing for family members"
                ]
            }
        }
    
    def generate_report(
        self,
        user_id: str,
        genomic_data: Dict[str, Any],
        variant_annotations: List[Dict],
        ml_predictions: Dict[str, Any],
        processing_time: float
    ) -> Dict[str, Any]:
        """Generate comprehensive genomic analysis report"""
        
        try:
            logger.info(f"Generating report for user {user_id}")
            
            # Generate disease assessments
            disease_assessments = []
            for disease_type, prediction in ml_predictions.items():
                if disease_type in self.disease_templates:
                    assessment = self._generate_disease_assessment(
                        disease_type, prediction, variant_annotations
                    )
                    disease_assessments.append(assessment)
            
            # Generate variant summary
            variant_summary = self._generate_variant_summary(variant_annotations)
            
            # Create report
            report = {
                'report_id': f"report_{int(time.time())}_{user_id}",
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'processing_time_seconds': processing_time,
                'file_analyzed': genomic_data.get('filename', 'Unknown'),
                'total_variants': len(variant_annotations),
                'annotated_variants': sum(1 for v in variant_annotations if v.get('functional_impact')),
                'disease_assessments': disease_assessments,
                'variant_summary': variant_summary,
                'technical_details': {
                    'pipeline_version': 'CuraGenie_v2.0_Advanced',
                    'ml_models_used': list(ml_predictions.keys()),
                    'annotation_sources': ['ClinVar', 'gnomAD', 'SIFT', 'PolyPhen-2']
                },
                'disclaimer': "This analysis is for informational purposes only. Consult healthcare professionals for medical advice."
            }
            
            logger.info(f"✅ Report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            raise
    
    def _generate_disease_assessment(
        self,
        disease_type: str,
        ml_prediction: Dict[str, Any],
        variant_annotations: List[Dict]
    ) -> Dict[str, Any]:
        """Generate disease-specific risk assessment"""
        
        template = self.disease_templates.get(disease_type, {})
        
        # Extract relevant variants
        key_variants = self._extract_relevant_variants(variant_annotations)
        
        # Generate evidence and recommendations
        supporting_evidence = self._generate_evidence(key_variants, ml_prediction)
        recommendations = self._generate_recommendations(disease_type, ml_prediction, key_variants)
        
        return {
            'disease_name': template.get('description', f"{disease_type.title()} Risk Assessment"),
            'risk_score': ml_prediction.get('risk_score', 0.5),
            'risk_level': ml_prediction.get('risk_level', 'Unknown'),
            'confidence': ml_prediction.get('confidence', 0.0),
            'key_variants': key_variants,
            'supporting_evidence': supporting_evidence,
            'recommendations': recommendations,
            'model_metadata': {
                'model_type': ml_prediction.get('model_type', 'Unknown'),
                'features_used': ml_prediction.get('features_used', [])
            }
        }
    
    def _extract_relevant_variants(self, variant_annotations: List[Dict]) -> List[Dict]:
        """Extract relevant variants"""
        
        relevant_variants = []
        
        for variant in variant_annotations:
            if self._is_variant_relevant(variant):
                relevant_variants.append({
                    'chrom': variant.get('chrom'),
                    'pos': variant.get('pos'),
                    'ref': variant.get('ref'),
                    'alt': variant.get('alt'),
                    'functional_impact': variant.get('functional_impact'),
                    'clinvar_significance': variant.get('clinvar_significance'),
                    'gnomad_frequency': variant.get('gnomad_af'),
                    'relevance_score': self._calculate_relevance(variant)
                })
        
        # Sort by relevance and return top variants
        relevant_variants.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_variants[:10]
    
    def _is_variant_relevant(self, variant: Dict[str, Any]) -> bool:
        """Check if variant is relevant"""
        
        # Check functional impact
        if variant.get('functional_impact') in ['HIGH', 'MODERATE']:
            return True
        
        # Check ClinVar significance
        clinvar_sig = variant.get('clinvar_significance', '').lower()
        if any(term in clinvar_sig for term in ['pathogenic', 'likely_pathogenic']):
            return True
        
        # Check population frequency
        gnomad_freq = variant.get('gnomad_af', 1.0)
        if gnomad_freq < 0.01:  # Rare variants
            return True
        
        return False
    
    def _calculate_relevance(self, variant: Dict[str, Any]) -> float:
        """Calculate variant relevance score"""
        
        score = 0.0
        
        # Functional impact
        impact_scores = {'HIGH': 1.0, 'MODERATE': 0.7, 'LOW': 0.3, 'MODIFIER': 0.1}
        impact = variant.get('functional_impact', 'MODIFIER')
        score += impact_scores.get(impact, 0.0)
        
        # ClinVar significance
        clinvar_scores = {
            'pathogenic': 1.0, 'likely_pathogenic': 0.8,
            'uncertain_significance': 0.5, 'likely_benign': 0.2, 'benign': 0.1
        }
        clinvar_sig = variant.get('clinvar_significance', 'uncertain_significance').lower()
        score += clinvar_scores.get(clinvar_sig, 0.5)
        
        # Population frequency (rarer = more relevant)
        gnomad_freq = variant.get('gnomad_af', 0.5)
        if gnomad_freq < 0.001:
            score += 0.3
        elif gnomad_freq < 0.01:
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_evidence(self, key_variants: List[Dict], ml_prediction: Dict[str, Any]) -> List[str]:
        """Generate supporting evidence"""
        
        evidence = []
        
        # ML model evidence
        if ml_prediction.get('confidence', 0) > 0.7:
            evidence.append(f"High-confidence prediction from {ml_prediction.get('model_type', 'ML model')}")
        
        # Variant evidence
        high_impact = [v for v in key_variants if v.get('functional_impact') == 'HIGH']
        if high_impact:
            evidence.append(f"Found {len(high_impact)} high-impact genetic variants")
        
        pathogenic = [v for v in key_variants if 'pathogenic' in str(v.get('clinvar_significance', '')).lower()]
        if pathogenic:
            evidence.append(f"Identified {len(pathogenic)} clinically significant variants")
        
        rare = [v for v in key_variants if v.get('gnomad_frequency', 1.0) < 0.01]
        if rare:
            evidence.append(f"Detected {len(rare)} rare genetic variants")
        
        return evidence
    
    def _generate_recommendations(
        self,
        disease_type: str,
        ml_prediction: Dict[str, Any],
        key_variants: List[Dict]
    ) -> List[str]:
        """Generate personalized recommendations"""
        
        base_recs = self.disease_templates.get(disease_type, {}).get('recommendations', [])
        recommendations = base_recs.copy()
        
        risk_level = ml_prediction.get('risk_level', 'Unknown')
        
        # Risk-specific recommendations
        if risk_level in ['High Risk', 'Very High Risk']:
            recommendations.append("Schedule consultation with specialist within 2-4 weeks")
            recommendations.append("Consider additional genetic testing for family members")
        
        elif risk_level == 'Moderate Risk':
            recommendations.append("Schedule follow-up consultation within 3-6 months")
            recommendations.append("Monitor for new symptoms or changes")
        
        # Variant-specific recommendations
        if any(v.get('functional_impact') == 'HIGH' for v in key_variants):
            recommendations.append("High-impact variants detected - consider genetic counseling")
        
        return recommendations
    
    def _generate_variant_summary(self, variant_annotations: List[Dict]) -> Dict[str, Any]:
        """Generate variant summary statistics"""
        
        if not variant_annotations:
            return {}
        
        # Count by functional impact
        impact_counts = {}
        for variant in variant_annotations:
            impact = variant.get('functional_impact', 'unknown')
            impact_counts[impact] = impact_counts.get(impact, 0) + 1
        
        # Count by ClinVar significance
        clinvar_counts = {}
        for variant in variant_annotations:
            clinvar_sig = variant.get('clinvar_significance', 'unknown')
            clinvar_counts[clinvar_sig] = clinvar_counts.get(clinvar_sig, 0) + 1
        
        return {
            'total_variants': len(variant_annotations),
            'impact_distribution': impact_counts,
            'clinvar_distribution': clinvar_counts,
            'rare_variants': sum(1 for v in variant_annotations if v.get('gnomad_af', 1.0) < 0.01),
            'pathogenic_variants': sum(1 for v in variant_annotations 
                                    if 'pathogenic' in str(v.get('clinvar_significance', '')).lower())
        }
    
    def export_json(self, report: Dict[str, Any]) -> str:
        """Export report to JSON format"""
        return json.dumps(report, indent=2, default=str)
