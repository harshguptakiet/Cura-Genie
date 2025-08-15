import factory
import json
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime, timedelta
import random

# Import models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import User, GenomicData, PRSScore, MRIScan, Report, Consent
from core.security import get_password_hash

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    hashed_password = factory.LazyAttribute(lambda o: get_password_hash("testpass123"))
    role = factory.Iterator(["patient", "doctor", "researcher"])
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

class GenomicDataFactory(SQLAlchemyModelFactory):
    class Meta:
        model = GenomicData
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory)
    filename = factory.Sequence(lambda n: f"sample_{n}.vcf")
    file_type = factory.Iterator(["vcf", "fastq", "bam", "fasta"])
    status = factory.Iterator(["uploaded", "processing", "completed", "failed"])
    file_size = factory.LazyFunction(lambda: random.randint(1000000, 10000000))  # 1MB to 10MB
    upload_date = factory.LazyFunction(datetime.utcnow)
    metadata_json = factory.LazyFunction(lambda: json.dumps({
        "variants": random.randint(100, 10000),
        "chromosomes": random.randint(1, 23),
        "quality_score": round(random.uniform(0.8, 1.0), 3)
    }))

class PRSScoreFactory(SQLAlchemyModelFactory):
    class Meta:
        model = PRSScore
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory)
    disease = factory.Iterator(["diabetes", "alzheimer", "breast_cancer", "heart_disease"])
    score = factory.LazyFunction(lambda: round(random.uniform(0.0, 1.0), 4))
    percentile = factory.LazyFunction(lambda: random.randint(1, 100))
    risk_level = factory.LazyFunction(lambda: random.choice(["low", "medium", "high"]))
    calculated_at = factory.LazyFunction(datetime.utcnow)
    variants_used = factory.LazyFunction(lambda: random.randint(50, 500))

class MRIScanFactory(SQLAlchemyModelFactory):
    class Meta:
        model = MRIScan
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory)
    filename = factory.Sequence(lambda n: f"mri_scan_{n}.dcm")
    scan_type = factory.Iterator(["brain", "chest", "abdomen", "spine"])
    status = factory.Iterator(["uploaded", "analyzing", "completed", "failed"])
    file_size = factory.LazyFunction(lambda: random.randint(50000000, 500000000))  # 50MB to 500MB
    upload_date = factory.LazyFunction(datetime.utcnow)
    analysis_results = factory.LazyFunction(lambda: json.dumps({
        "abnormalities": random.randint(0, 3),
        "confidence": round(random.uniform(0.7, 1.0), 3),
        "processing_time": round(random.uniform(10, 300), 2)
    }))

class ReportFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Report
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory)
    report_type = factory.Iterator(["genomic", "mri", "comprehensive"])
    title = factory.Sequence(lambda n: f"Report {n}")
    content = factory.LazyFunction(lambda: "This is a sample report content for testing purposes.")
    generated_at = factory.LazyFunction(datetime.utcnow)
    status = factory.Iterator(["draft", "final", "archived"])

class ConsentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Consent
        sqlalchemy_session_persistence = "commit"

    user = factory.SubFactory(UserFactory)
    consent_type = factory.Iterator(["data_processing", "research", "third_party"])
    granted = factory.Iterator([True, False])
    granted_at = factory.LazyFunction(lambda: datetime.utcnow() if random.choice([True, False]) else None)
    expires_at = factory.LazyFunction(lambda: datetime.utcnow() + timedelta(days=365))
    ip_address = factory.LazyFunction(lambda: f"192.168.1.{random.randint(1, 255)}")

# Helper functions for creating specific test scenarios
def create_patient_with_genomic_data():
    """Create a patient user with genomic data"""
    user = UserFactory(role="patient")
    genomic_data = GenomicDataFactory(user=user, status="completed")
    return user, genomic_data

def create_doctor_with_patients(num_patients=3):
    """Create a doctor user with multiple patients"""
    doctor = UserFactory(role="doctor")
    patients = [UserFactory(role="patient") for _ in range(num_patients)]
    return doctor, patients

def create_complete_user_profile():
    """Create a complete user profile with all data types"""
    user = UserFactory()
    genomic_data = GenomicDataFactory(user=user, status="completed")
    prs_scores = [PRSScoreFactory(user=user) for _ in range(3)]
    mri_scan = MRIScanFactory(user=user, status="completed")
    report = ReportFactory(user=user, user=user)
    consent = ConsentFactory(user=user, granted=True)
    
    return {
        "user": user,
        "genomic_data": genomic_data,
        "prs_scores": prs_scores,
        "mri_scan": mri_scan,
        "report": report,
        "consent": consent
    }
