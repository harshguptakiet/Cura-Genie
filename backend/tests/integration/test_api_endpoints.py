import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import UserFactory, GenomicDataFactory, PRSScoreFactory
from core.security import create_access_token

class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    def test_register_endpoint_success(self, client: TestClient, db_session: Session):
        """Test successful user registration via API"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "role": "patient"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["role"] == "patient"
        assert "id" in data
        assert "created_at" in data
    
    def test_register_endpoint_duplicate_email(self, client: TestClient, db_session: Session):
        """Test registration with duplicate email fails"""
        # Create first user
        user = UserFactory(email="duplicate@example.com")
        db_session.add(user)
        db_session.commit()
        
        # Try to register with same email
        user_data = {
            "email": "duplicate@example.com",
            "username": "differentuser",
            "password": "SecurePass123!",
            "role": "patient"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Email already registered" in data["detail"]
    
    def test_login_endpoint_success(self, client: TestClient, db_session: Session):
        """Test successful user login via API"""
        # Create user with known password
        from core.security import get_password_hash
        password = "SecurePass123!"
        hashed_password = get_password_hash(password)
        user = UserFactory(
            email="login@example.com",
            hashed_password=hashed_password
        )
        db_session.add(user)
        db_session.commit()
        
        # Attempt login
        login_data = {
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "login@example.com"
    
    def test_login_endpoint_invalid_credentials(self, client: TestClient, db_session: Session):
        """Test login with invalid credentials fails"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid credentials" in data["detail"]

class TestGenomicEndpoints:
    """Test genomic data API endpoints"""
    
    def test_upload_genomic_data_success(self, client: TestClient, db_session: Session, sample_vcf_file, auth_headers):
        """Test successful genomic data upload"""
        # Create authenticated user
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload file
        with open(sample_vcf_file, "rb") as f:
            files = {"file": ("sample.vcf", f, "text/plain")}
            data = {"file_type": "vcf"}
            
            response = client.post(
                "/api/genomic/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["filename"] == "sample.vcf"
        assert data["status"] == "uploaded"
        assert data["user_id"] == user.id
    
    def test_upload_genomic_data_unauthorized(self, client: TestClient, sample_vcf_file):
        """Test genomic data upload without authentication fails"""
        with open(sample_vcf_file, "rb") as f:
            files = {"file": ("sample.vcf", f, "text/plain")}
            data = {"file_type": "vcf"}
            
            response = client.post("/api/genomic/upload", files=files, data=data)
        
        assert response.status_code == 401
    
    def test_get_genomic_data_list(self, client: TestClient, db_session: Session, auth_headers):
        """Test getting list of user's genomic data"""
        # Create user with genomic data
        user = UserFactory()
        genomic_data1 = GenomicDataFactory(user=user, filename="file1.vcf")
        genomic_data2 = GenomicDataFactory(user=user, filename="file2.fastq")
        db_session.add_all([user, genomic_data1, genomic_data2])
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/genomic/data", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        filenames = [item["filename"] for item in data]
        assert "file1.vcf" in filenames
        assert "file2.fastq" in filenames
    
    def test_get_genomic_data_detail(self, client: TestClient, db_session: Session, auth_headers):
        """Test getting specific genomic data details"""
        # Create user with genomic data
        user = UserFactory()
        genomic_data = GenomicDataFactory(user=user, filename="detail.vcf")
        db_session.add_all([user, genomic_data])
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/genomic/data/{genomic_data.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == genomic_data.id
        assert data["filename"] == "detail.vcf"
        assert data["user_id"] == user.id

class TestPRSEndpoints:
    """Test PRS calculation API endpoints"""
    
    def test_calculate_prs_success(self, client: TestClient, db_session: Session, auth_headers):
        """Test successful PRS calculation"""
        # Create user with genomic data
        user = UserFactory()
        genomic_data = GenomicDataFactory(user=user, status="completed")
        db_session.add_all([user, genomic_data])
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request PRS calculation
        prs_data = {
            "disease": "diabetes",
            "genomic_data_id": genomic_data.id
        }
        
        response = client.post("/api/prs/calculate", json=prs_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["disease"] == "diabetes"
        assert data["user_id"] == user.id
        assert "score" in data
        assert "percentile" in data
        assert "risk_level" in data
    
    def test_get_prs_scores_list(self, client: TestClient, db_session: Session, auth_headers):
        """Test getting list of user's PRS scores"""
        # Create user with PRS scores
        user = UserFactory()
        prs1 = PRSScoreFactory(user=user, disease="diabetes")
        prs2 = PRSScoreFactory(user=user, disease="alzheimer")
        db_session.add_all([user, prs1, prs2])
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/prs/scores", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        diseases = [item["disease"] for item in data]
        assert "diabetes" in diseases
        assert "alzheimer" in diseases

class TestUserProfileEndpoints:
    """Test user profile API endpoints"""
    
    def test_get_user_profile(self, client: TestClient, db_session: Session, auth_headers):
        """Test getting user profile"""
        # Create user
        user = UserFactory(
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/profile/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == "john@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
    
    def test_update_user_profile(self, client: TestClient, db_session: Session, auth_headers):
        """Test updating user profile"""
        # Create user
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        
        # Create access token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update profile
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+1234567890"
        }
        
        response = client.put("/api/profile/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert data["phone"] == "+1234567890"
    
    def test_get_user_profile_unauthorized(self, client: TestClient):
        """Test getting user profile without authentication fails"""
        response = client.get("/api/profile/me")
        assert response.status_code == 401

class TestHealthCheckEndpoints:
    """Test health check and system endpoints"""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_database_health(self, client: TestClient, db_session: Session):
        """Test database health check endpoint"""
        response = client.get("/api/health/database")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert data["database"]["status"] == "connected"
