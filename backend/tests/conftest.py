import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, patch

# Import the app and database components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db.database import get_db, Base
from core.config import settings

# Test database setup - use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_curagenie.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    """Create all tables for testing session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db):
    """Create a new database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls"""
    with patch('core.llm_service.openai') as mock:
        mock.ChatCompletion.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Mocked response"))]
        )
        yield mock

@pytest.fixture
def mock_s3():
    """Mock S3 operations"""
    with patch('boto3.client') as mock:
        mock.return_value.upload_file.return_value = None
        mock.return_value.download_file.return_value = None
        yield mock

@pytest.fixture
def sample_vcf_file():
    """Create a temporary sample VCF file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.vcf', delete=False) as f:
        f.write("""##fileformat=VCFv4.2
##reference=GRCh38
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1
chr1	1000	rs123	A	T	100	PASS	.	GT	0/1
chr2	2000	rs456	G	C	95	PASS	.	GT	1/1
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def sample_fastq_file():
    """Create a temporary sample FASTQ file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fastq', delete=False) as f:
        f.write("""@SEQ_ID_1
GATTTGGGGTTCAAAGCAGTATCGATCAAATAGTAAATCCATTTGTTCAACTCACAGTTT
+
!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing"""
    return {"Authorization": "Bearer test_token_12345"}

@pytest.fixture
def mock_celery():
    """Mock Celery tasks"""
    with patch('core.celery_app.celery') as mock:
        mock.send_task.return_value = Mock(id="mock_task_id")
        yield mock
