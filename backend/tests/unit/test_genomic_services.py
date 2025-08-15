import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from tests.factories import UserFactory, GenomicDataFactory
from services.enhanced_genomic_processor import EnhancedGenomicProcessor
from services.variant_annotation import VariantAnnotator
from services.ml_prediction_service import MLPredictionService

class TestEnhancedGenomicProcessor:
    """Test enhanced genomic data processing"""
    
    def test_vcf_parsing_success(self, sample_vcf_file):
        """Test successful VCF file parsing"""
        processor = EnhancedGenomicProcessor()
        
        # Parse VCF file
        variants = processor.parse_vcf_file(sample_vcf_file)
        
        assert len(variants) == 2
        assert variants[0]["chromosome"] == "chr1"
        assert variants[0]["position"] == 1000
        assert variants[0]["reference"] == "A"
        assert variants[0]["alternative"] == "T"
        assert variants[0]["rsid"] == "rs123"
        assert variants[0]["quality"] == 100
        assert variants[0]["filter"] == "PASS"
    
    def test_vcf_parsing_invalid_file(self):
        """Test VCF parsing with invalid file fails gracefully"""
        processor = EnhancedGenomicProcessor()
        
        # Create invalid VCF content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False) as f:
            f.write("Invalid VCF content\nNo proper headers\n")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                processor.parse_vcf_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_variant_filtering(self):
        """Test variant filtering by quality and frequency"""
        processor = EnhancedGenomicProcessor()
        
        # Sample variants with different qualities
        variants = [
            {"chromosome": "chr1", "position": 1000, "quality": 100, "filter": "PASS"},
            {"chromosome": "chr1", "position": 2000, "quality": 30, "filter": "PASS"},
            {"chromosome": "chr2", "position": 3000, "quality": 80, "filter": "FAIL"},
            {"chromosome": "chr2", "position": 4000, "quality": 95, "filter": "PASS"}
        ]
        
        # Filter by quality > 50 and PASS filter
        filtered_variants = processor.filter_variants(
            variants, 
            min_quality=50, 
            required_filter="PASS"
        )
        
        assert len(filtered_variants) == 2
        assert filtered_variants[0]["position"] == 1000
        assert filtered_variants[1]["position"] == 4000
    
    def test_genomic_data_processing_pipeline(self, db_session: Session, sample_vcf_file):
        """Test complete genomic data processing pipeline"""
        processor = EnhancedGenomicProcessor()
        
        # Create user and genomic data
        user = UserFactory()
        genomic_data = GenomicDataFactory(user=user, filename="test.vcf")
        db_session.add_all([user, genomic_data])
        db_session.commit()
        
        # Process genomic data
        with patch.object(processor, 'parse_vcf_file') as mock_parse:
            mock_parse.return_value = [
                {"chromosome": "chr1", "position": 1000, "quality": 100, "filter": "PASS"}
            ]
            
            result = processor.process_genomic_data(
                genomic_data.id, 
                sample_vcf_file, 
                db_session
            )
        
        assert result is not None
        assert result["status"] == "completed"
        assert "variants_count" in result
        assert "processing_time" in result
    
    def test_genomic_data_validation(self):
        """Test genomic data file validation"""
        processor = EnhancedGenomicProcessor()
        
        # Valid file types
        valid_files = ["sample.vcf", "data.fastq", "sequence.bam"]
        for filename in valid_files:
            assert processor.validate_file_type(filename) is True
        
        # Invalid file types
        invalid_files = ["sample.txt", "data.doc", "sequence.pdf"]
        for filename in invalid_files:
            assert processor.validate_file_type(filename) is False

class TestVariantAnnotator:
    """Test variant annotation functionality"""
    
    def test_variant_annotation_success(self):
        """Test successful variant annotation"""
        annotator = VariantAnnotator()
        
        # Sample variant
        variant = {
            "chromosome": "chr1",
            "position": 1000,
            "reference": "A",
            "alternative": "T",
            "rsid": "rs123"
        }
        
        # Annotate variant
        annotated_variant = annotator.annotate_variant(variant)
        
        assert "clinical_significance" in annotated_variant
        assert "gene" in annotated_variant
        assert "consequence" in annotated_variant
        assert "frequency" in annotated_variant
    
    def test_variant_annotation_with_external_api(self):
        """Test variant annotation using external API"""
        annotator = VariantAnnotator()
        
        # Sample variant
        variant = {
            "chromosome": "chr1",
            "position": 1000,
            "reference": "A",
            "alternative": "T",
            "rsid": "rs123"
        }
        
        # Mock external API response
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "clinical_significance": "likely_pathogenic",
                "gene": "BRCA1",
                "consequence": "missense_variant",
                "frequency": 0.001
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            annotated_variant = annotator.annotate_variant_with_api(variant)
            
            assert annotated_variant["clinical_significance"] == "likely_pathogenic"
            assert annotated_variant["gene"] == "BRCA1"
    
    def test_batch_variant_annotation(self):
        """Test batch annotation of multiple variants"""
        annotator = VariantAnnotator()
        
        # Sample variants
        variants = [
            {"chromosome": "chr1", "position": 1000, "rsid": "rs123"},
            {"chromosome": "chr2", "position": 2000, "rsid": "rs456"},
            {"chromosome": "chr3", "position": 3000, "rsid": "rs789"}
        ]
        
        # Annotate all variants
        annotated_variants = annotator.annotate_variants_batch(variants)
        
        assert len(annotated_variants) == 3
        for variant in annotated_variants:
            assert "clinical_significance" in variant
            assert "gene" in variant

class TestMLPredictionService:
    """Test machine learning prediction service"""
    
    def test_prs_calculation_success(self):
        """Test successful PRS calculation"""
        ml_service = MLPredictionService()
        
        # Sample variants with effect sizes
        variants = [
            {"rsid": "rs7903146", "genotype": "0/1", "effect_size": 0.5},
            {"rsid": "rs1801282", "genotype": "1/1", "effect_size": -0.3},
            {"rsid": "rs4402960", "genotype": "0/0", "effect_size": 0.2}
        ]
        
        # Calculate PRS for diabetes
        prs_score = ml_service.calculate_prs(variants, "diabetes")
        
        assert isinstance(prs_score, float)
        assert 0.0 <= prs_score <= 1.0
    
    def test_disease_risk_prediction(self):
        """Test disease risk prediction"""
        ml_service = MLPredictionService()
        
        # Sample user data
        user_data = {
            "age": 45,
            "gender": "female",
            "bmi": 25.5,
            "family_history": ["diabetes", "heart_disease"]
        }
        
        # Predict disease risks
        risks = ml_service.predict_disease_risks(user_data)
        
        assert "diabetes" in risks
        assert "heart_disease" in risks
        assert "alzheimer" in risks
        
        for disease, risk in risks.items():
            assert isinstance(risk, float)
            assert 0.0 <= risk <= 1.0
    
    def test_model_loading_and_caching(self):
        """Test ML model loading and caching"""
        ml_service = MLPredictionService()
        
        # First call should load model
        with patch('joblib.load') as mock_load:
            mock_model = Mock()
            mock_load.return_value = mock_model
            
            model1 = ml_service._get_model("diabetes")
            assert model1 == mock_model
        
        # Second call should use cached model
        with patch('joblib.load') as mock_load:
            model2 = ml_service._get_model("diabetes")
            assert model2 == mock_model
            mock_load.assert_not_called()
    
    def test_feature_engineering(self):
        """Test feature engineering for ML models"""
        ml_service = MLPredictionService()
        
        # Sample raw data
        raw_data = {
            "variants": [
                {"rsid": "rs123", "genotype": "0/1", "quality": 100},
                {"rsid": "rs456", "genotype": "1/1", "quality": 95}
            ],
            "demographics": {
                "age": 45,
                "gender": "female",
                "bmi": 25.5
            }
        }
        
        # Engineer features
        features = ml_service.engineer_features(raw_data)
        
        assert "variant_count" in features
        assert "avg_quality" in features
        assert "age_normalized" in features
        assert "bmi_category" in features
        
        assert features["variant_count"] == 2
        assert features["avg_quality"] == 97.5
        assert features["bmi_category"] == "normal"

class TestGenomicDataQuality:
    """Test genomic data quality assessment"""
    
    def test_quality_metrics_calculation(self):
        """Test calculation of genomic data quality metrics"""
        processor = EnhancedGenomicProcessor()
        
        # Sample variants with different qualities
        variants = [
            {"quality": 100, "filter": "PASS"},
            {"quality": 95, "filter": "PASS"},
            {"quality": 80, "filter": "PASS"},
            {"quality": 30, "filter": "FAIL"},
            {"quality": 90, "filter": "PASS"}
        ]
        
        # Calculate quality metrics
        metrics = processor.calculate_quality_metrics(variants)
        
        assert "total_variants" in metrics
        assert "passing_variants" in metrics
        assert "average_quality" in metrics
        assert "quality_distribution" in metrics
        
        assert metrics["total_variants"] == 5
        assert metrics["passing_variants"] == 4
        assert metrics["average_quality"] == 79.0
    
    def test_coverage_analysis(self):
        """Test genomic coverage analysis"""
        processor = EnhancedGenomicProcessor()
        
        # Sample coverage data
        coverage_data = {
            "chr1": [100, 95, 90, 85, 80],
            "chr2": [95, 90, 85, 80, 75],
            "chr3": [90, 85, 80, 75, 70]
        }
        
        # Analyze coverage
        coverage_metrics = processor.analyze_coverage(coverage_data)
        
        assert "total_coverage" in coverage_metrics
        assert "average_coverage" in coverage_metrics
        assert "coverage_gaps" in coverage_metrics
        assert "chromosome_coverage" in coverage_metrics
        
        assert coverage_metrics["total_coverage"] > 0
        assert coverage_metrics["average_coverage"] > 0
