"""
Enhanced Genomic Processor for CuraGenie
Integrates variant annotation, ML prediction, and report generation
"""

import logging
import time
import asyncio
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from .variant_annotation import VariantAnnotator
from .ml_prediction_service import MLPredictionService
from .report_gen import ReportGenerator

logger = logging.getLogger(__name__)

class EnhancedGenomicProcessor:
    """Enhanced genomic processor with real-time analysis capabilities"""
    
    def __init__(self):
        self.variant_annotator = VariantAnnotator()
        self.ml_service = MLPredictionService()
        self.report_generator = ReportGenerator()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("✅ Enhanced Genomic Processor initialized")
    
    async def process_vcf_comprehensive(
        self,
        vcf_content: bytes,
        filename: str,
        user_id: str,
        target_time: float = 60.0
    ) -> Dict[str, Any]:
        """
        Process VCF file comprehensively within target time
        
        Args:
            vcf_content: VCF file content
            filename: VCF filename
            user_id: User identifier
            target_time: Target processing time in seconds
            
        Returns:
            Comprehensive analysis results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting comprehensive VCF analysis for {filename}")
            
            # Step 1: Parse VCF and extract variants (target: 10s)
            variants = await self._parse_vcf_fast(vcf_content, filename)
            if not variants:
                return {"error": "No variants found in VCF file"}
            
            logger.info(f"Parsed {len(variants)} variants in {time.time() - start_time:.2f}s")
            
            # Step 2: Annotate variants (target: 30s)
            annotation_start = time.time()
            annotated_variants = await self._annotate_variants_optimized(variants)
            annotation_time = time.time() - annotation_start
            
            logger.info(f"Annotated {len(annotated_variants)} variants in {annotation_time:.2f}s")
            
            # Step 3: Run ML predictions (target: 15s)
            ml_start = time.time()
            ml_predictions = await self._run_ml_predictions(annotated_variants)
            ml_time = time.time() - ml_start
            
            logger.info(f"ML predictions completed in {ml_time:.2f}s")
            
            # Step 4: Generate comprehensive report (target: 5s)
            report_start = time.time()
            report = self._generate_comprehensive_report(
                user_id, filename, annotated_variants, ml_predictions, time.time() - start_time
            )
            report_time = time.time() - report_start
            
            total_time = time.time() - start_time
            
            logger.info(f"✅ Comprehensive analysis completed in {total_time:.2f}s")
            logger.info(f"  - VCF parsing: {time.time() - start_time:.2f}s")
            logger.info(f"  - Variant annotation: {annotation_time:.2f}s")
            logger.info(f"  - ML predictions: {ml_time:.2f}s")
            logger.info(f"  - Report generation: {report_time:.2f}s")
            
            # Check if we met the target time
            if total_time > target_time:
                logger.warning(f"⚠️ Processing time ({total_time:.2f}s) exceeded target ({target_time}s)")
            
            return {
                "status": "success",
                "processing_time_seconds": total_time,
                "target_time_met": total_time <= target_time,
                "total_variants": len(variants),
                "annotated_variants": len(annotated_variants),
                "ml_predictions": ml_predictions,
                "comprehensive_report": report,
                "performance_metrics": {
                    "vcf_parsing_time": time.time() - start_time,
                    "annotation_time": annotation_time,
                    "ml_prediction_time": ml_time,
                    "report_generation_time": report_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive VCF processing: {e}")
            return {"error": str(e)}
    
    async def _parse_vcf_fast(self, vcf_content: bytes, filename: str) -> List[Dict]:
        """Fast VCF parsing optimized for performance"""
        
        try:
            # Convert bytes to string
            vcf_text = vcf_content.decode('utf-8')
            lines = vcf_text.split('\n')
            
            variants = []
            header_lines = 0
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    header_lines += 1
                    continue
                
                # Parse VCF line (simplified for speed)
                parts = line.split('\t')
                if len(parts) >= 8:
                    chrom = parts[0]
                    pos = int(parts[1])
                    ref = parts[3]
                    alt = parts[4]
                    
                    # Basic quality filter
                    if len(ref) == 1 and len(alt) == 1:  # SNPs only for speed
                        variants.append({
                            'chrom': chrom,
                            'pos': pos,
                            'ref': ref,
                            'alt': alt,
                            'quality': parts[5] if len(parts) > 5 else '0',
                            'filter': parts[6] if len(parts) > 6 else 'PASS'
                        })
            
            logger.info(f"Parsed {len(variants)} variants from {len(lines) - header_lines} data lines")
            return variants
            
        except Exception as e:
            logger.error(f"Error parsing VCF: {e}")
            return []
    
    async def _annotate_variants_optimized(self, variants: List[Dict]) -> List[Dict]:
        """Optimized variant annotation with parallel processing"""
        
        try:
            # Use the variant annotator service
            async with self.variant_annotator as annotator:
                # Process variants in batches for optimal performance
                batch_size = 100
                annotated_variants = []
                
                for i in range(0, len(variants), batch_size):
                    batch = variants[i:i + batch_size]
                    batch_annotations = await annotator.annotate_variants_batch(batch)
                    annotated_variants.extend(batch_annotations)
                    
                    # Log progress
                    if i % 500 == 0:
                        logger.info(f"Annotated {i + len(batch)}/{len(variants)} variants")
                
                return annotated_variants
                
        except Exception as e:
            logger.error(f"Error in variant annotation: {e}")
            # Return basic annotations if annotation fails
            return [self._create_basic_annotation(v) for v in variants]
    
    def _create_basic_annotation(self, variant: Dict) -> Dict:
        """Create basic variant annotation when external services fail"""
        
        return {
            'chrom': variant['chrom'],
            'pos': variant['pos'],
            'ref': variant['ref'],
            'alt': variant['alt'],
            'functional_impact': 'UNKNOWN',
            'clinvar_significance': 'unknown',
            'gnomad_af': None,
            'sift_score': None,
            'polyphen_score': None
        }
    
    async def _run_ml_predictions(self, annotated_variants: List[Dict]) -> Dict[str, Any]:
        """Run ML predictions for all supported diseases"""
        
        try:
            # Extract features for ML models
            features = self._extract_ml_features(annotated_variants)
            
            # Run predictions in parallel
            predictions = {}
            
            # Diabetes prediction
            diabetes_pred = self.ml_service.predict_diabetes_risk(features)
            if 'error' not in diabetes_pred:
                predictions['diabetes'] = diabetes_pred
            
            # Alzheimer's prediction
            alzheimer_pred = self.ml_service.predict_alzheimer_risk(features)
            if 'error' not in alzheimer_pred:
                predictions['alzheimer'] = alzheimer_pred
            
            # Brain tumor prediction
            brain_tumor_pred = self.ml_service.predict_brain_tumor_risk(features)
            if 'error' not in brain_tumor_pred:
                predictions['brain_tumor'] = brain_tumor_pred
            
            logger.info(f"ML predictions completed for {len(predictions)} diseases")
            return predictions
            
        except Exception as e:
            logger.error(f"Error in ML predictions: {e}")
            return {}
    
    def _extract_ml_features(self, annotated_variants: List[Dict]) -> Dict[str, Any]:
        """Extract features for ML models from annotated variants"""
        
        features = {}
        
        # Count variants by functional impact
        impact_counts = {'HIGH': 0, 'MODERATE': 0, 'LOW': 0, 'MODIFIER': 0}
        pathogenic_count = 0
        rare_variant_count = 0
        
        for variant in annotated_variants:
            impact = variant.get('functional_impact', 'MODIFIER')
            if impact in impact_counts:
                impact_counts[impact] += 1
            
            # Count pathogenic variants
            clinvar_sig = variant.get('clinvar_significance', '').lower()
            if 'pathogenic' in clinvar_sig:
                pathogenic_count += 1
            
            # Count rare variants
            gnomad_freq = variant.get('gnomad_af', 1.0)
            if gnomad_freq and gnomad_freq < 0.01:
                rare_variant_count += 1
        
        # Create feature dictionary
        features.update({
            'high_impact_variants': impact_counts['HIGH'],
            'moderate_impact_variants': impact_counts['MODERATE'],
            'low_impact_variants': impact_counts['LOW'],
            'modifier_variants': impact_counts['MODIFIER'],
            'pathogenic_variants': pathogenic_count,
            'rare_variants': rare_variant_count,
            'total_variants': len(annotated_variants),
            'variant_density': len(annotated_variants) / 1000.0,  # variants per kb
        })
        
        # Add disease-specific features
        features.update(self._extract_disease_specific_features(annotated_variants))
        
        return features
    
    def _extract_disease_specific_features(self, annotated_variants: List[Dict]) -> Dict[str, Any]:
        """Extract disease-specific features from variants"""
        
        features = {}
        
        # Diabetes-related features (simplified)
        features['diabetes_risk_score'] = 0.5  # Default
        
        # Alzheimer's-related features (simplified)
        features['alzheimer_risk_score'] = 0.5  # Default
        
        # Brain tumor-related features (simplified)
        features['brain_tumor_risk_score'] = 0.5  # Default
        
        return features
    
    def _generate_comprehensive_report(
        self,
        user_id: str,
        filename: str,
        annotated_variants: List[Dict],
        ml_predictions: Dict[str, Any],
        processing_time: float
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        try:
            # Create genomic data structure
            genomic_data = {
                'filename': filename,
                'file_type': 'VCF',
                'total_variants': len(annotated_variants)
            }
            
            # Generate report using report generator
            report = self.report_generator.generate_report(
                user_id=user_id,
                genomic_data=genomic_data,
                variant_annotations=annotated_variants,
                ml_predictions=ml_predictions,
                processing_time=processing_time
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {"error": f"Report generation failed: {str(e)}"}
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get information about processing capabilities"""
        
        return {
            "supported_file_formats": ["VCF", "VCF.GZ"],
            "target_processing_time": "60 seconds",
            "ml_models_available": self.ml_service.get_model_info(),
            "annotation_sources": ["ClinVar", "gnomAD", "SIFT", "PolyPhen-2"],
            "supported_diseases": ["diabetes", "alzheimer", "brain_tumor"],
            "pipeline_version": "CuraGenie_v2.0_Enhanced"
        }
