"""
Simplified Enhanced Genomic Processor
Integrates simplified services without numpy/pandas dependencies
"""

import time
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .variant_annotation_simple import SimpleVariantAnnotator, VariantAnnotation
from .ml_prediction_simple import SimpleMLPredictionService, DiseasePrediction
from .report_generator_simple import SimpleReportGenerator, SimpleVariant, SimpleDiseaseAssessment

@dataclass
class ProcessingResult:
    """Result of genomic processing"""
    success: bool
    processing_time: float
    variants_processed: int
    report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class SimpleEnhancedGenomicProcessor:
    """Simplified enhanced genomic processor without numpy/pandas dependencies"""
    
    def __init__(self):
        self.variant_annotator = SimpleVariantAnnotator()
        self.ml_service = SimpleMLPredictionService()
        self.report_generator = SimpleReportGenerator()
        self.processing_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'average_processing_time': 0.0
        }
    
    async def process_vcf_comprehensive(self, vcf_content: str) -> ProcessingResult:
        """Process VCF content comprehensively"""
        start_time = time.time()
        
        try:
            print("Starting comprehensive VCF analysis...")
            
            # Step 1: Parse VCF content
            print("Step 1: Parsing VCF content...")
            variants = self._parse_vcf_simple(vcf_content)
            print(f"Parsed {len(variants)} variants")
            
            # Step 2: Annotate variants
            print("Step 2: Annotating variants...")
            annotations = await self._annotate_variants_optimized(variants)
            print(f"Annotated {len(annotations)} variants")
            
            # Step 3: Run ML predictions
            print("Step 3: Running ML predictions...")
            disease_predictions = self._run_ml_predictions(annotations)
            print(f"Generated predictions for {len(disease_predictions)} diseases")
            
            # Step 4: Generate comprehensive report
            print("Step 4: Generating comprehensive report...")
            report = self._generate_comprehensive_report(annotations, disease_predictions, start_time)
            print("Report generation completed")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_processing_stats(processing_time, True)
            
            print(f"Analysis completed in {processing_time:.2f} seconds")
            
            return ProcessingResult(
                success=True,
                processing_time=processing_time,
                variants_processed=len(variants),
                report=report
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error during processing: {str(e)}"
            print(error_msg)
            
            # Update statistics
            self._update_processing_stats(processing_time, False)
            
            return ProcessingResult(
                success=False,
                processing_time=processing_time,
                variants_processed=0,
                error_message=error_msg
            )
    
    def _parse_vcf_simple(self, vcf_content: str) -> List[Dict[str, Any]]:
        """Parse VCF content without external libraries"""
        variants = []
        lines = vcf_content.strip().split('\n')
        
        for line in lines:
            # Skip header lines and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            try:
                # Parse VCF line (tab-separated)
                parts = line.split('\t')
                if len(parts) >= 5:
                    chrom = parts[0]
                    pos = int(parts[1])
                    ref = parts[3]
                    alt = parts[4]
                    
                    # Basic quality check
                    if self._is_valid_variant(chrom, pos, ref, alt):
                        variant = {
                            'chrom': chrom,
                            'pos': pos,
                            'ref': ref,
                            'alt': alt,
                            'id': parts[2] if len(parts) > 2 else '.',
                            'qual': parts[5] if len(parts) > 5 else '.',
                            'filter': parts[6] if len(parts) > 6 else '.',
                            'info': parts[7] if len(parts) > 7 else '.'
                        }
                        variants.append(variant)
                        
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping malformed VCF line: {e}")
                continue
        
        return variants
    
    def _is_valid_variant(self, chrom: str, pos: int, ref: str, alt: str) -> bool:
        """Check if variant is valid"""
        # Basic validation
        if not chrom or not ref or not alt:
            return False
        
        if pos <= 0:
            return False
        
        # Check for valid DNA bases
        valid_bases = {'A', 'C', 'G', 'T', 'N', 'a', 'c', 'g', 't', 'n'}
        if not all(base in valid_bases for base in ref + alt):
            return False
        
        return True
    
    async def _annotate_variants_optimized(self, variants: List[Dict[str, Any]]) -> List[VariantAnnotation]:
        """Annotate variants with optimization"""
        if not variants:
            return []
        
        # Convert to format expected by annotator
        variant_list = []
        for var in variants:
            variant_list.append({
                'chrom': var['chrom'],
                'pos': var['pos'],
                'ref': var['ref'],
                'alt': var['alt']
            })
        
        # Annotate in batches
        batch_size = 100  # Process in batches for efficiency
        annotations = []
        
        for i in range(0, len(variant_list), batch_size):
            batch = variant_list[i:i + batch_size]
            batch_annotations = await self.variant_annotator.annotate_variants_batch(batch)
            annotations.extend(batch_annotations)
            
            # Small delay to prevent overwhelming external APIs
            if i + batch_size < len(variant_list):
                await asyncio.sleep(0.1)
        
        return annotations
    
    def _run_ml_predictions(self, annotations: List[VariantAnnotation]) -> List[DiseasePrediction]:
        """Run ML predictions for all diseases"""
        predictions = []
        
        try:
            # Extract features from annotations
            features = self._extract_ml_features(annotations)
            
            # Generate predictions for each disease
            diabetes_pred = self.ml_service.predict_diabetes_risk(features)
            alzheimer_pred = self.ml_service.predict_alzheimer_risk(features)
            brain_tumor_pred = self.ml_service.predict_brain_tumor_risk(features)
            
            predictions = [diabetes_pred, alzheimer_pred, brain_tumor_pred]
            
        except Exception as e:
            print(f"Error running ML predictions: {e}")
            # Return default predictions
            predictions = [
                DiseasePrediction("Diabetes", 0.5, "Unknown", 0.0, ["Error"], ["Consult provider"]),
                DiseasePrediction("Alzheimer's Disease", 0.5, "Unknown", 0.0, ["Error"], ["Consult provider"]),
                DiseasePrediction("Brain Tumor", 0.5, "Unknown", 0.0, ["Error"], ["Consult provider"])
            ]
        
        return predictions
    
    def _extract_ml_features(self, annotations: List[VariantAnnotation]) -> List[float]:
        """Extract ML features from variant annotations"""
        if not annotations:
            return [0.0] * 20  # Default features
        
        features = []
        
        # Feature 1-5: Variant type distribution
        snp_count = sum(1 for a in annotations if len(a.ref) == 1 and len(a.alt) == 1)
        indel_count = sum(1 for a in annotations if len(a.ref) != len(a.alt))
        transition_count = sum(1 for a in annotations if a.functional_impact == "transition")
        transversion_count = sum(1 for a in annotations if a.functional_impact == "transversion")
        deletion_count = sum(1 for a in annotations if a.functional_impact == "deletion")
        
        # Normalize counts
        total_variants = len(annotations)
        features.extend([
            snp_count / max(total_variants, 1),
            indel_count / max(total_variants, 1),
            transition_count / max(total_variants, 1),
            transversion_count / max(total_variants, 1),
            deletion_count / max(total_variants, 1)
        ])
        
        # Feature 6-10: Significance distribution
        pathogenic_count = sum(1 for a in annotations if a.clinvar_significance and "pathogenic" in a.clinvar_significance.lower())
        benign_count = sum(1 for a in annotations if a.clinvar_significance and "benign" in a.clinvar_significance.lower())
        uncertain_count = sum(1 for a in annotations if a.clinvar_significance and "uncertain" in a.clinvar_significance.lower())
        
        features.extend([
            pathogenic_count / max(total_variants, 1),
            benign_count / max(total_variants, 1),
            uncertain_count / max(total_variants, 1)
        ])
        
        # Feature 11-15: Frequency-based features
        rare_variants = sum(1 for a in annotations if a.gnomad_frequency and a.gnomad_frequency < 0.01)
        common_variants = sum(1 for a in annotations if a.gnomad_frequency and a.gnomad_frequency > 0.1)
        
        features.extend([
            rare_variants / max(total_variants, 1),
            common_variants / max(total_variants, 1)
        ])
        
        # Feature 16-20: Chromosome distribution (simplified)
        chr1_count = sum(1 for a in annotations if a.chrom == "chr1")
        chr2_count = sum(1 for a in annotations if a.chrom == "chr2")
        chr3_count = sum(1 for a in annotations if a.chrom == "chr3")
        
        features.extend([
            chr1_count / max(total_variants, 1),
            chr2_count / max(total_variants, 1),
            chr3_count / max(total_variants, 1)
        ])
        
        # Pad to exactly 20 features
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]  # Ensure exactly 20 features
    
    def _generate_comprehensive_report(self, annotations: List[VariantAnnotation], 
                                     disease_predictions: List[DiseasePrediction], 
                                     start_time: float) -> Dict[str, Any]:
        """Generate comprehensive report"""
        processing_time = time.time() - start_time
        
        # Convert annotations to simple format
        simple_variants = []
        for annotation in annotations:
            simple_variant = SimpleVariant(
                chrom=annotation.chrom,
                pos=annotation.pos,
                ref=annotation.ref,
                alt=annotation.alt,
                significance=annotation.clinvar_significance,
                frequency=annotation.gnomad_frequency,
                impact=annotation.functional_impact
            )
            simple_variants.append(simple_variant)
        
        # Convert disease predictions to simple format
        simple_assessments = []
        for prediction in disease_predictions:
            simple_assessment = SimpleDiseaseAssessment(
                disease=prediction.disease,
                risk_score=prediction.risk_score,
                risk_category=prediction.risk_category,
                confidence=prediction.confidence,
                key_factors=prediction.key_factors,
                recommendations=prediction.recommendations
            )
            simple_assessments.append(simple_assessment)
        
        # Generate report
        report = self.report_generator.generate_report(
            simple_variants, 
            simple_assessments, 
            processing_time
        )
        
        return report
    
    def _update_processing_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        self.processing_stats['total_analyses'] += 1
        if success:
            self.processing_stats['successful_analyses'] += 1
        
        # Update average processing time
        current_avg = self.processing_stats['average_processing_time']
        total_analyses = self.processing_stats['total_analyses']
        self.processing_stats['average_processing_time'] = (
            (current_avg * (total_analyses - 1) + processing_time) / total_analyses
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return self.processing_stats.copy()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get system capabilities"""
        return {
            "supported_diseases": ["Diabetes", "Alzheimer's Disease", "Brain Tumor"],
            "variant_annotation": {
                "sources": ["ClinVar", "gnomAD"],
                "functional_impact": ["SIFT", "PolyPhen-2 (simplified)"]
            },
            "ml_models": {
                "diabetes": "Gradient Boosting",
                "alzheimer": "Random Forest",
                "brain_tumor": "Random Forest"
            },
            "performance_target": "Under 60 seconds for standard exome VCF",
            "report_features": [
                "Executive summary",
                "Disease-specific risk assessments",
                "Variant analysis and prioritization",
                "Actionable recommendations",
                "Technical details and limitations"
            ]
        }

# Test function
async def test_processor():
    """Test the simplified enhanced genomic processor"""
    processor = SimpleEnhancedGenomicProcessor()
    
    # Create test VCF content
    test_vcf = """##fileformat=VCFv4.2
##source=TestData
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t1000\t.\tA\tT\t100\tPASS\t.
chr2\t2000\t.\tAT\tA\t100\tPASS\t.
chr3\t3000\t.\tC\tG\t100\tPASS\t.
chr1\t4000\t.\tG\tC\t100\tPASS\t.
chr2\t5000\t.\tT\tA\t100\tPASS\t."""
    
    print("Testing Simplified Enhanced Genomic Processor:")
    print("=" * 60)
    
    # Process VCF
    result = await processor.process_vcf_comprehensive(test_vcf)
    
    if result.success:
        print(f"✅ Processing successful!")
        print(f"⏱️  Processing time: {result.processing_time:.2f} seconds")
        print(f"🧬 Variants processed: {result.variants_processed}")
        print(f"📊 Report generated: {'Yes' if result.report else 'No'}")
        
        if result.report:
            print("\n📋 Report Summary:")
            if 'executive_summary' in result.report:
                summary = result.report['executive_summary']
                print(f"   Overall Risk: {summary.get('overall_risk', 'Unknown')}")
                print(f"   Primary Concern: {summary.get('primary_concern', 'Unknown')}")
    else:
        print(f"❌ Processing failed: {result.error_message}")
    
    # Show capabilities
    print("\n🔧 System Capabilities:")
    capabilities = processor.get_capabilities()
    print(f"   Supported Diseases: {', '.join(capabilities['supported_diseases'])}")
    print(f"   Performance Target: {capabilities['performance_target']}")
    
    # Show statistics
    print("\n📈 Processing Statistics:")
    stats = processor.get_processing_stats()
    print(f"   Total Analyses: {stats['total_analyses']}")
    print(f"   Successful: {stats['successful_analyses']}")
    print(f"   Average Time: {stats['average_processing_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_processor())
