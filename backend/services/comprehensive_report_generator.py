"""
Comprehensive Report Generator for CuraGenie
Generates user-friendly reports with risk scores, key variants, and supporting evidence
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class DiseaseRiskAssessment:
    """Structured disease risk assessment"""
    disease_name: str
    risk_score: float
    risk_level: str
    confidence: float
    key_variants: List[Dict]
    supporting_evidence: List[str]
    recommendations: List[str]
    model_metadata: Dict[str, Any]

@dataclass
class ComprehensiveReport:
    """Complete comprehensive analysis report"""
    report_id: str
    user_id: str
    timestamp: str
    processing_time_seconds: float
    file_analyzed: str
    total_variants: int
    annotated_variants: int
    disease_assessments: List[DiseaseRiskAssessment]
    variant_summary: Dict[str, Any]
    technical_details: Dict[str, Any]
    disclaimer: str

class ComprehensiveReportGenerator:
    """Generates comprehensive genomic analysis reports"""
    
    def __init__(self):
        self.report_templates = self._load_report_templates()
    
    def _load_report_templates(self) -> Dict[str, Any]:
        """Load report templates for different diseases"""
        return {
            "diabetes": {
                "description": "Type 2 Diabetes Risk Assessment",
                "risk_factors": ["genetic predisposition", "lifestyle factors", "family history"],
                "key_genes": ["TCF7L2", "PPARG", "KCNJ11", "CDKAL1"],
                "recommendations": [
                    "Monitor blood glucose levels regularly",
                    "Maintain healthy diet and exercise routine",
                    "Consult with endocrinologist if risk is high",
                    "Consider genetic counseling for family planning"
                ]
            },
            "alzheimer": {
                "description": "Alzheimer's Disease Risk Assessment",
                "risk_factors": ["genetic variants", "age", "family history", "APOE status"],
                "key_genes": ["APOE", "APP", "PSEN1", "PSEN2", "TREM2"],
                "recommendations": [
                    "Regular cognitive assessments",
                    "Maintain brain health through mental stimulation",
                    "Consult with neurologist for baseline evaluation",
                    "Consider participation in clinical trials if eligible"
                ]
            },
            "brain_tumor": {
                "description": "Brain Tumor Risk Assessment",
                "risk_factors": ["genetic mutations", "radiation exposure", "family history"],
                "key_genes": ["TP53", "NF1", "NF2", "VHL", "PTCH1"],
                "recommendations": [
                    "Regular neurological examinations",
                    "Immediate medical attention for new symptoms",
                    "Consider genetic testing for family members",
                    "Consult with neurosurgeon if risk is high"
                ]
            }
        }
    
    def generate_comprehensive_report(
        self,
        user_id: str,
        genomic_data: Dict[str, Any],
        variant_annotations: List[Dict],
        ml_predictions: Dict[str, Any],
        processing_time: float
    ) -> ComprehensiveReport:
        """
        Generate a comprehensive genomic analysis report
        
        Args:
            user_id: User identifier
            genomic_data: Processed genomic data
            variant_annotations: Annotated variants
            ml_predictions: ML model predictions
            processing_time: Total processing time in seconds
            
        Returns:
            Comprehensive report object
        """
        start_time = time.time()
        
        try:
            logger.info(f"Generating comprehensive report for user {user_id}")
            
            # Generate disease-specific assessments
            disease_assessments = []
            
            # Diabetes assessment
            if 'diabetes' in ml_predictions:
                diabetes_assessment = self._generate_disease_assessment(
                    'diabetes',
                    ml_predictions['diabetes'],
                    variant_annotations,
                    genomic_data
                )
                disease_assessments.append(diabetes_assessment)
            
            # Alzheimer's assessment
            if 'alzheimer' in ml_predictions:
                alzheimer_assessment = self._generate_disease_assessment(
                    'alzheimer',
                    ml_predictions['alzheimer'],
                    variant_annotations,
                    genomic_data
                )
                disease_assessments.append(alzheimer_assessment)
            
            # Brain tumor assessment
            if 'brain_tumor' in ml_predictions:
                brain_tumor_assessment = self._generate_disease_assessment(
                    'brain_tumor',
                    ml_predictions['brain_tumor'],
                    variant_annotations,
                    genomic_data
                )
                disease_assessments.append(brain_tumor_assessment)
            
            # Generate variant summary
            variant_summary = self._generate_variant_summary(variant_annotations)
            
            # Generate technical details
            technical_details = self._generate_technical_details(
                genomic_data, processing_time, ml_predictions
            )
            
            # Create comprehensive report
            report = ComprehensiveReport(
                report_id=f"report_{int(time.time())}_{user_id}",
                user_id=user_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time_seconds=processing_time,
                file_analyzed=genomic_data.get('filename', 'Unknown'),
                total_variants=len(variant_annotations),
                annotated_variants=sum(1 for v in variant_annotations if v.get('functional_impact')),
                disease_assessments=disease_assessments,
                variant_summary=variant_summary,
                technical_details=technical_details,
                disclaimer=self._get_disclaimer()
            )
            
            report_generation_time = time.time() - start_time
            logger.info(f"✅ Comprehensive report generated in {report_generation_time:.2f}s")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating comprehensive report: {e}")
            raise
    
    def _generate_disease_assessment(
        self,
        disease_type: str,
        ml_prediction: Dict[str, Any],
        variant_annotations: List[Dict],
        genomic_data: Dict[str, Any]
    ) -> DiseaseRiskAssessment:
        """Generate disease-specific risk assessment"""
        
        template = self.report_templates.get(disease_type, {})
        
        # Extract key variants relevant to this disease
        key_variants = self._extract_disease_relevant_variants(
            disease_type, variant_annotations
        )
        
        # Generate supporting evidence
        supporting_evidence = self._generate_supporting_evidence(
            disease_type, key_variants, ml_prediction
        )
        
        # Generate personalized recommendations
        recommendations = self._generate_personalized_recommendations(
            disease_type, ml_prediction, key_variants
        )
        
        # Create assessment
        assessment = DiseaseRiskAssessment(
            disease_name=template.get('description', f"{disease_type.title()} Risk Assessment"),
            risk_score=ml_prediction.get('risk_score', 0.5),
            risk_level=ml_prediction.get('risk_level', 'Unknown'),
            confidence=ml_prediction.get('confidence', 0.0),
            key_variants=key_variants,
            supporting_evidence=supporting_evidence,
            recommendations=recommendations,
            model_metadata={
                'model_type': ml_prediction.get('model_type', 'Unknown'),
                'features_used': ml_prediction.get('features_used', []),
                'prediction_confidence': ml_prediction.get('confidence', 0.0)
            }
        )
        
        return assessment
    
    def _extract_disease_relevant_variants(
        self,
        disease_type: str,
        variant_annotations: List[Dict]
    ) -> List[Dict]:
        """Extract variants relevant to specific disease"""
        
        # Define disease-specific gene lists
        disease_genes = {
            'diabetes': ['TCF7L2', 'PPARG', 'KCNJ11', 'CDKAL1', 'HHEX', 'IGF2BP2'],
            'alzheimer': ['APOE', 'APP', 'PSEN1', 'PSEN2', 'TREM2', 'CLU', 'CR1'],
            'brain_tumor': ['TP53', 'NF1', 'NF2', 'VHL', 'PTCH1', 'IDH1', 'TERT']
        }
        
        relevant_variants = []
        target_genes = disease_genes.get(disease_type, [])
        
        for variant in variant_annotations:
            # Check if variant is in disease-relevant genes
            # This is a simplified check - in reality you'd use gene annotations
            if self._is_variant_relevant_to_disease(variant, disease_type, target_genes):
                relevant_variants.append({
                    'chrom': variant.get('chrom'),
                    'pos': variant.get('pos'),
                    'ref': variant.get('ref'),
                    'alt': variant.get('alt'),
                    'functional_impact': variant.get('functional_impact'),
                    'clinvar_significance': variant.get('clinvar_significance'),
                    'gnomad_frequency': variant.get('gnomad_af'),
                    'relevance_score': self._calculate_variant_relevance(variant, disease_type)
                })
        
        # Sort by relevance score
        relevant_variants.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top variants
        return relevant_variants[:10]
    
    def _is_variant_relevant_to_disease(
        self,
        variant: Dict[str, Any],
        disease_type: str,
        target_genes: List[str]
    ) -> bool:
        """Check if variant is relevant to specific disease"""
        
        # Simplified relevance check
        # In reality, you'd use proper gene annotations and pathway analysis
        
        # Check functional impact
        if variant.get('functional_impact') in ['HIGH', 'MODERATE']:
            return True
        
        # Check ClinVar significance
        clinvar_sig = variant.get('clinvar_significance', '').lower()
        if any(term in clinvar_sig for term in ['pathogenic', 'likely_pathogenic']):
            return True
        
        # Check population frequency (rarer variants are more likely to be disease-causing)
        gnomad_freq = variant.get('gnomad_af', 1.0)
        if gnomad_freq < 0.01:  # Less than 1% population frequency
            return True
        
        return False
    
    def _calculate_variant_relevance(
        self,
        variant: Dict[str, Any],
        disease_type: str
    ) -> float:
        """Calculate variant relevance score for disease"""
        
        relevance_score = 0.0
        
        # Functional impact scoring
        impact_scores = {'HIGH': 1.0, 'MODERATE': 0.7, 'LOW': 0.3, 'MODIFIER': 0.1}
        impact = variant.get('functional_impact', 'MODIFIER')
        relevance_score += impact_scores.get(impact, 0.0)
        
        # ClinVar significance scoring
        clinvar_scores = {
            'pathogenic': 1.0,
            'likely_pathogenic': 0.8,
            'uncertain_significance': 0.5,
            'likely_benign': 0.2,
            'benign': 0.1
        }
        clinvar_sig = variant.get('clinvar_significance', 'uncertain_significance').lower()
        relevance_score += clinvar_scores.get(clinvar_sig, 0.5)
        
        # Population frequency scoring (rarer = more relevant)
        gnomad_freq = variant.get('gnomad_af', 0.5)
        if gnomad_freq < 0.001:  # Very rare
            relevance_score += 0.3
        elif gnomad_freq < 0.01:  # Rare
            relevance_score += 0.2
        elif gnomad_freq < 0.1:  # Uncommon
            relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _generate_supporting_evidence(
        self,
        disease_type: str,
        key_variants: List[Dict],
        ml_prediction: Dict[str, Any]
    ) -> List[str]:
        """Generate supporting evidence for disease risk assessment"""
        
        evidence = []
        
        # Add ML model evidence
        if ml_prediction.get('confidence', 0) > 0.7:
            evidence.append(f"High-confidence prediction from {ml_prediction.get('model_type', 'ML model')}")
        
        # Add variant-based evidence
        high_impact_variants = [v for v in key_variants if v.get('functional_impact') == 'HIGH']
        if high_impact_variants:
            evidence.append(f"Found {len(high_impact_variants)} high-impact genetic variants")
        
        pathogenic_variants = [v for v in key_variants if 'pathogenic' in str(v.get('clinvar_significance', '')).lower()]
        if pathogenic_variants:
            evidence.append(f"Identified {len(pathogenic_variants)} clinically significant variants")
        
        rare_variants = [v for v in key_variants if v.get('gnomad_frequency', 1.0) < 0.01]
        if rare_variants:
            evidence.append(f"Detected {len(rare_variants)} rare genetic variants")
        
        # Add disease-specific evidence
        if disease_type == 'diabetes':
            if ml_prediction.get('risk_score', 0) > 0.6:
                evidence.append("Elevated risk factors consistent with Type 2 Diabetes")
        elif disease_type == 'alzheimer':
            if ml_prediction.get('risk_score', 0) > 0.6:
                evidence.append("Genetic profile associated with increased Alzheimer's risk")
        elif disease_type == 'brain_tumor':
            if ml_prediction.get('risk_score', 0) > 0.6:
                evidence.append("Genetic markers suggestive of brain tumor predisposition")
        
        return evidence
    
    def _generate_personalized_recommendations(
        self,
        disease_type: str,
        ml_prediction: Dict[str, Any],
        key_variants: List[Dict]
    ) -> List[str]:
        """Generate personalized recommendations based on risk assessment"""
        
        base_recommendations = self.report_templates.get(disease_type, {}).get('recommendations', [])
        personalized_recommendations = base_recommendations.copy()
        
        risk_score = ml_prediction.get('risk_score', 0.5)
        risk_level = ml_prediction.get('risk_level', 'Unknown')
        
        # Add risk-specific recommendations
        if risk_level in ['High Risk', 'Very High Risk']:
            personalized_recommendations.append(
                "Schedule consultation with specialist within 2-4 weeks"
            )
            personalized_recommendations.append(
                "Consider additional genetic testing for family members"
            )
            if disease_type == 'diabetes':
                personalized_recommendations.append(
                    "Begin regular glucose monitoring and lifestyle modifications"
                )
            elif disease_type == 'alzheimer':
                personalized_recommendations.append(
                    "Establish baseline cognitive assessment with neurologist"
                )
            elif disease_type == 'brain_tumor':
                personalized_recommendations.append(
                    "Immediate neurological evaluation recommended"
                )
        
        elif risk_level in ['Moderate Risk']:
            personalized_recommendations.append(
                "Schedule follow-up consultation within 3-6 months"
            )
            personalized_recommendations.append(
                "Monitor for new symptoms or changes in condition"
            )
        
        # Add variant-specific recommendations
        if any(v.get('functional_impact') == 'HIGH' for v in key_variants):
            personalized_recommendations.append(
                "High-impact variants detected - consider genetic counseling"
            )
        
        if any('pathogenic' in str(v.get('clinvar_significance', '')).lower() for v in key_variants):
            personalized_recommendations.append(
                "Pathogenic variants identified - clinical correlation recommended"
            )
        
        return personalized_recommendations
    
    def _generate_variant_summary(self, variant_annotations: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for all variants"""
        
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
        
        # Calculate average population frequencies
        frequencies = [v.get('gnomad_af', 0) for v in variant_annotations if v.get('gnomad_af') is not None]
        avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0
        
        return {
            'total_variants': len(variant_annotations),
            'impact_distribution': impact_counts,
            'clinvar_distribution': clinvar_counts,
            'average_population_frequency': avg_frequency,
            'rare_variants': sum(1 for v in variant_annotations if v.get('gnomad_af', 1.0) < 0.01),
            'pathogenic_variants': sum(1 for v in variant_annotations 
                                    if 'pathogenic' in str(v.get('clinvar_significance', '')).lower())
        }
    
    def _generate_technical_details(
        self,
        genomic_data: Dict[str, Any],
        processing_time: float,
        ml_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate technical details about the analysis"""
        
        return {
            'analysis_pipeline_version': 'CuraGenie_v2.0_Advanced',
            'processing_time_seconds': processing_time,
            'file_format': genomic_data.get('file_type', 'Unknown'),
            'file_size_bytes': genomic_data.get('file_size_bytes', 0),
            'ml_models_used': list(ml_predictions.keys()),
            'variant_annotation_sources': ['ClinVar', 'gnomAD', 'SIFT', 'PolyPhen-2'],
            'quality_metrics': genomic_data.get('quality_assessment', {}),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_disclaimer(self) -> str:
        """Get medical disclaimer for the report"""
        
        return (
            "IMPORTANT: This analysis is for informational and research purposes only. "
            "It is not a medical diagnosis and should not replace consultation with qualified healthcare professionals. "
            "Genetic risk assessments are probabilistic and do not guarantee disease development or absence. "
            "Always consult with your physician for medical advice and interpretation of results."
        )
    
    def export_report_json(self, report: ComprehensiveReport) -> str:
        """Export report to JSON format"""
        return json.dumps(asdict(report), indent=2, default=str)
    
    def export_report_summary(self, report: ComprehensiveReport) -> Dict[str, Any]:
        """Export simplified report summary"""
        
        return {
            'report_id': report.report_id,
            'timestamp': report.timestamp,
            'processing_time': report.processing_time_seconds,
            'total_variants': report.total_variants,
            'disease_risks': [
                {
                    'disease': assessment.disease_name,
                    'risk_level': assessment.risk_level,
                    'risk_score': assessment.risk_score,
                    'confidence': assessment.confidence
                }
                for assessment in report.disease_assessments
            ],
            'key_findings': {
                'high_impact_variants': report.variant_summary.get('pathogenic_variants', 0),
                'rare_variants': report.variant_summary.get('rare_variants', 0),
                'annotation_rate': report.annotated_variants / report.total_variants if report.total_variants > 0 else 0
            }
        }
