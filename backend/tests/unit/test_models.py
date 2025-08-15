import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tests.factories import (
    UserFactory, GenomicDataFactory, PRSScoreFactory, 
    MRIScanFactory, ReportFactory, ConsentFactory
)
from db.models import User, GenomicData, PRSScore, MRIScan, Report, Consent, UserRole

class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, db_session: Session):
        """Test basic user creation"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email.endswith("@example.com")
        assert user.role in [role.value for role in UserRole]
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_unique_constraints(self, db_session: Session):
        """Test that email and username are unique"""
        user1 = UserFactory(email="test@example.com", username="testuser")
        db_session.add(user1)
        db_session.commit()
        
        # Try to create another user with same email
        user2 = UserFactory(email="test@example.com", username="different")
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create another user with same username
        user3 = UserFactory(email="different@example.com", username="testuser")
        db_session.add(user3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_password_hashing(self, db_session: Session):
        """Test that passwords are properly hashed"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Password should be hashed, not plain text
        assert user.hashed_password != "testpass123"
        assert len(user.hashed_password) >= 32
    
    def test_user_role_validation(self, db_session: Session):
        """Test user role validation"""
        valid_roles = ["patient", "doctor", "admin", "researcher"]
        
        for role in valid_roles:
            user = UserFactory(role=role)
            db_session.add(user)
            db_session.commit()
            
            assert user.role == role
            db_session.delete(user)
            db_session.commit()

class TestGenomicDataModel:
    """Test GenomicData model functionality"""
    
    def test_genomic_data_creation(self, db_session: Session):
        """Test basic genomic data creation"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        genomic_data = GenomicDataFactory(user=user)
        db_session.add(genomic_data)
        db_session.commit()
        
        assert genomic_data.id is not None
        assert genomic_data.user_id == user.id
        assert genomic_data.filename.endswith(('.vcf', '.fastq', '.bam', '.fasta'))
        assert genomic_data.file_size > 0
    
    def test_genomic_data_user_relationship(self, db_session: Session):
        """Test relationship between genomic data and user"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create multiple genomic data entries for the same user
        genomic_data1 = GenomicDataFactory(user=user)
        genomic_data2 = GenomicDataFactory(user=user)
        db_session.add_all([genomic_data1, genomic_data2])
        db_session.commit()
        
        # Check that user has access to genomic data
        assert len(user.genomic_data) == 2
        assert genomic_data1 in user.genomic_data
        assert genomic_data2 in user.genomic_data
    
    def test_genomic_data_cascade_delete(self, db_session: Session):
        """Test that genomic data is deleted when user is deleted"""
        user = UserFactory()
        genomic_data = GenomicDataFactory(user=user)
        db_session.add_all([user, genomic_data])
        db_session.commit()
        
        user_id = user.id
        genomic_data_id = genomic_data.id
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Check that genomic data is also deleted
        deleted_genomic_data = db_session.query(GenomicData).filter_by(id=genomic_data_id).first()
        assert deleted_genomic_data is None

class TestPRSScoreModel:
    """Test PRSScore model functionality"""
    
    def test_prs_score_creation(self, db_session: Session):
        """Test basic PRS score creation"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        prs_score = PRSScoreFactory(user=user)
        db_session.add(prs_score)
        db_session.commit()
        
        assert prs_score.id is not None
        assert prs_score.user_id == user.id
        assert 0.0 <= prs_score.score <= 1.0
        assert 1 <= prs_score.percentile <= 100
        assert prs_score.risk_level in ["low", "medium", "high"]
    
    def test_prs_score_user_relationship(self, db_session: Session):
        """Test relationship between PRS scores and user"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create multiple PRS scores for different diseases
        diseases = ["diabetes", "alzheimer", "breast_cancer"]
        prs_scores = []
        
        for disease in diseases:
            prs_score = PRSScoreFactory(user=user, disease=disease)
            prs_scores.append(prs_score)
        
        db_session.add_all(prs_scores)
        db_session.commit()
        
        # Check that user has access to all PRS scores
        assert len(user.prs_scores) == 3
        for prs_score in prs_scores:
            assert prs_score in user.prs_scores

class TestMRIScanModel:
    """Test MRIScan model functionality"""
    
    def test_mri_scan_creation(self, db_session: Session):
        """Test basic MRI scan creation"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        mri_scan = MRIScanFactory(user=user)
        db_session.add(mri_scan)
        db_session.commit()
        
        assert mri_scan.id is not None
        assert mri_scan.user_id == user.id
        assert mri_scan.filename.endswith('.dcm')
        assert mri_scan.file_size > 0
        assert mri_scan.scan_type in ["brain", "chest", "abdomen", "spine"]
    
    def test_mri_scan_analysis_results(self, db_session: Session):
        """Test MRI scan analysis results JSON field"""
        user = UserFactory()
        mri_scan = MRIScanFactory(user=user)
        db_session.add_all([user, mri_scan])
        db_session.commit()
        
        # Check that analysis results can be parsed as JSON
        import json
        analysis_results = json.loads(mri_scan.analysis_results)
        
        assert "abnormalities" in analysis_results
        assert "confidence" in analysis_results
        assert "processing_time" in analysis_results
        
        assert isinstance(analysis_results["abnormalities"], int)
        assert isinstance(analysis_results["confidence"], float)
        assert isinstance(analysis_results["processing_time"], float)

class TestReportModel:
    """Test Report model functionality"""
    
    def test_report_creation(self, db_session: Session):
        """Test basic report creation"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        report = ReportFactory(user=user)
        db_session.add(report)
        db_session.commit()
        
        assert report.id is not None
        assert report.user_id == user.id
        assert report.title.startswith("Report")
        assert report.content is not None
        assert report.generated_at is not None
        assert report.status in ["draft", "final", "archived"]

class TestConsentModel:
    """Test Consent model functionality"""
    
    def test_consent_creation(self, db_session: Session):
        """Test basic consent creation"""
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        consent = ConsentFactory(user=user)
        db_session.add(consent)
        db_session.commit()
        
        assert consent.id is not None
        assert consent.user_id == user.id
        assert consent.consent_type in ["data_processing", "research", "third_party"]
        assert isinstance(consent.granted, bool)
        assert consent.expires_at > datetime.utcnow()
    
    def test_consent_expiration_logic(self, db_session: Session):
        """Test consent expiration logic"""
        user = UserFactory()
        consent = ConsentFactory(user=user, granted=True)
        db_session.add_all([user, consent])
        db_session.commit()
        
        # Test that expiration date is in the future
        assert consent.expires_at > datetime.utcnow()
        
        # Test that expiration date is reasonable (within 2 years)
        max_expiration = datetime.utcnow() + timedelta(days=730)
        assert consent.expires_at < max_expiration
