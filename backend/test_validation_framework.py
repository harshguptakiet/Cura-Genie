"""
Comprehensive Test Script for CuraGenie Validation Framework

This script tests:
- Input validation and sanitization
- Security middleware and rate limiting
- File upload validation
- API endpoint security
- Error handling
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our validation and security components
from core.validation import (
    InputSanitizer, FileUploadValidator, ValidationError as ValidationErrorCustom,
    validate_and_sanitize_input, ValidationResponse,
    UserRegistrationRequest, UserLoginRequest
)
from core.security import (
    rate_limiter, request_throttler, ip_blocklist,
    RateLimiter, RequestThrottler, IPBlocklist
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationFrameworkTester:
    """Comprehensive tester for the validation framework"""
    
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
    
    def run_test(self, test_name: str, test_func, *args, **kwargs):
        """Run a test and record results"""
        self.test_results["total"] += 1
        
        try:
            result = test_func(*args, **kwargs)
            self.test_results["passed"] += 1
            self.test_results["details"].append({
                "test": test_name,
                "status": "PASSED",
                "result": result
            })
            logger.info(f"✅ {test_name}: PASSED")
            return True
        except Exception as e:
            self.test_results["failed"] += 1
            self.test_results["details"].append({
                "test": test_name,
                "status": "FAILED",
                "error": str(e)
            })
            logger.error(f"❌ {test_name}: FAILED - {e}")
            return False
    
    def test_input_sanitizer(self):
        """Test input sanitization functionality"""
        logger.info("🧪 Testing Input Sanitizer...")
        
        # Test HTML sanitization
        html_input = "<script>alert('xss')</script>Hello <b>World</b>"
        sanitized = InputSanitizer.sanitize_html(html_input)
        assert "<script>" not in sanitized
        assert "<b>" not in sanitized
        assert "Hello World" in sanitized
        
        # Test filename sanitization
        dangerous_filename = "../../../etc/passwd"
        safe_filename = InputSanitizer.sanitize_filename(dangerous_filename)
        assert ".." not in safe_filename
        assert "etc" not in safe_filename
        assert "passwd" in safe_filename
        
        # Test SQL input sanitization
        sql_input = "'; DROP TABLE users; --"
        sanitized_sql = InputSanitizer.sanitize_sql_input(sql_input)
        assert "DROP TABLE" not in sanitized_sql
        
        # Test email validation
        valid_emails = ["test@example.com", "user.name@domain.co.uk"]
        invalid_emails = ["invalid-email", "@domain.com", "user@"]
        
        for email in valid_emails:
            assert InputSanitizer.validate_email_format(email)
        
        for email in invalid_emails:
            assert not InputSanitizer.validate_email_format(email)
        
        # Test password strength validation
        strong_password = "SecurePass123!"
        weak_password = "weak"
        
        strong_result = InputSanitizer.validate_password_strength(strong_password)
        weak_result = InputSanitizer.validate_password_strength(weak_password)
        
        assert strong_result["valid"]
        assert not weak_result["valid"]
        assert len(weak_result["errors"]) > 0
        
        # Test username validation
        valid_usernames = ["user123", "user_name", "user-name"]
        invalid_usernames = ["u", "user@name", "user name"]
        
        for username in valid_usernames:
            assert InputSanitizer.validate_username_format(username)
        
        for username in invalid_usernames:
            assert not InputSanitizer.validate_username_format(username)
        
        return "Input sanitizer tests completed successfully"
    
    def test_file_upload_validator(self):
        """Test file upload validation functionality"""
        logger.info("🧪 Testing File Upload Validator...")
        
        # Test genomic file validation
        valid_genomic_files = [
            ("test.vcf", "text/plain", 1024),
            ("data.fastq.gz", "application/gzip", 2048),
            ("variants.bam", "application/octet-stream", 512)
        ]
        
        invalid_genomic_files = [
            ("test.exe", "application/octet-stream", 1024),  # Executable
            ("../../../etc/passwd", "text/plain", 1024),     # Path traversal
            ("script.php", "text/plain", 1024)               # PHP file
        ]
        
        for filename, content_type, size in valid_genomic_files:
            try:
                result = FileUploadValidator.validate_genomic_file(
                    None, filename, content_type, size
                )
                assert result["valid"]
            except ValidationErrorCustom:
                assert False, f"Valid file {filename} was rejected"
        
        for filename, content_type, size in invalid_genomic_files:
            try:
                FileUploadValidator.validate_genomic_file(
                    None, filename, content_type, size
                )
                assert False, f"Invalid file {filename} was accepted"
            except ValidationErrorCustom:
                pass  # Expected
        
        # Test MRI file validation
        valid_mri_files = [
            ("scan.dcm", "application/dicom", 1024),
            ("brain.nii.gz", "application/octet-stream", 2048),
            ("image.jpg", "image/jpeg", 512)
        ]
        
        for filename, content_type, size in valid_mri_files:
            try:
                result = FileUploadValidator.validate_mri_file(
                    None, filename, content_type, size
                )
                assert result["valid"]
            except ValidationErrorCustom:
                assert False, f"Valid MRI file {filename} was rejected"
        
        # Test file content validation
        vcf_content = b"##fileformat=VCF\n#CHROM\tPOS\tID\tREF\tALT\n1\t100\t.\tA\tT"
        fastq_content = b"@read1\nACGT\n+\nIIII"
        
        assert FileUploadValidator.validate_file_content(vcf_content, ".vcf")
        assert FileUploadValidator.validate_file_content(fastq_content, ".fastq")
        assert not FileUploadValidator.validate_file_content(b"invalid", ".vcf")
        
        return "File upload validator tests completed successfully"
    
    def test_generic_validation(self):
        """Test generic input validation and sanitization"""
        logger.info("🧪 Testing Generic Validation...")
        
        # Test data validation
        test_data = {
            "name": "John Doe",
            "age": 25,
            "email": "john@example.com",
            "description": "<script>alert('xss')</script>Hello World"
        }
        
        validation_rules = {
            "name": {"type": str, "min_length": 2, "max_length": 50, "required": True},
            "age": {"type": int, "min": 18, "max": 100, "required": True},
            "email": {"type": str, "required": True, "custom_validator": InputSanitizer.validate_email_format},
            "description": {"type": str, "max_length": 1000, "sanitize_html": True, "required": False}
        }
        
        result = validate_and_sanitize_input(test_data, validation_rules)
        
        assert result.valid
        assert "name" in result.sanitized_data
        assert result.sanitized_data["age"] == 25
        assert "<script>" not in result.sanitized_data["description"]
        
        # Test validation failures
        invalid_data = {
            "name": "A",  # Too short
            "age": 15,    # Too young
            "email": "invalid-email"
        }
        
        result = validate_and_sanitize_input(invalid_data, validation_rules)
        assert not result.valid
        assert len(result.errors) > 0
        
        return "Generic validation tests completed successfully"
    
    def test_pydantic_models(self):
        """Test Pydantic validation models"""
        logger.info("🧪 Testing Pydantic Models...")
        
        # Test valid user registration
        valid_user = UserRegistrationRequest(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            role="patient"
        )
        assert valid_user.email == "test@example.com"
        assert valid_user.username == "testuser"
        
        # Test invalid user registration
        try:
            UserRegistrationRequest(
                email="invalid-email",
                username="u",  # Too short
                password="weak",  # Too weak
                role="invalid_role"
            )
            assert False, "Invalid user should have been rejected"
        except Exception:
            pass  # Expected
        
        # Test valid user login
        valid_login = UserLoginRequest(
            email="test@example.com",
            password="SecurePass123!"
        )
        assert valid_login.email == "test@example.com"
        
        return "Pydantic models tests completed successfully"
    
    def test_rate_limiter(self):
        """Test rate limiting functionality"""
        logger.info("🧪 Testing Rate Limiter...")
        
        # Create a mock request object
        class MockRequest:
            def __init__(self, client_host="127.0.0.1", user_agent="test-agent"):
                self.client = type('obj', (object,), {'host': client_host})()
                self.headers = {'user-agent': user_agent}
                self.url = type('obj', (object,), {'path': '/test'})()
                self.query_params = {}
        
        request = MockRequest()
        
        # Test rate limiting
        assert rate_limiter.check_rate_limit(request, "default")
        
        # Test multiple requests (should hit rate limit)
        for i in range(101):  # Exceed 100 requests per minute
            if not rate_limiter.check_rate_limit(request, "default"):
                break
        
        # Should have hit rate limit
        assert i < 100
        
        # Test different rate limit types
        assert rate_limiter.check_rate_limit(request, "auth")
        assert rate_limiter.check_rate_limit(request, "upload")
        
        return "Rate limiter tests completed successfully"
    
    def test_request_throttler(self):
        """Test request throttling functionality"""
        logger.info("🧪 Testing Request Throttler...")
        
        # Test throttling
        user_id = "test_user"
        operation = "file_upload"
        
        # First operation should succeed
        assert request_throttler.check_throttle(operation, user_id)
        
        # Second operation should be throttled
        assert not request_throttler.check_throttle(operation, user_id)
        
        # Wait time should be positive
        wait_time = request_throttler.get_wait_time(operation, user_id)
        assert wait_time > 0
        
        # Test different operations
        assert request_throttler.check_throttle("genomic_analysis", user_id)
        assert request_throttler.check_throttle("mri_analysis", user_id)
        
        return "Request throttler tests completed successfully"
    
    def test_ip_blocklist(self):
        """Test IP blocking functionality"""
        logger.info("🧪 Testing IP Blocklist...")
        
        # Test IP blocking
        test_ip = "192.168.1.100"
        
        # IP should not be blocked initially
        assert not ip_blocklist.is_ip_blocked(test_ip)
        
        # Block the IP
        assert ip_blocklist.block_ip(test_ip, "Test blocking", 60)
        
        # IP should now be blocked
        assert ip_blocklist.is_ip_blocked(test_ip)
        
        # Get block info
        block_info = ip_blocklist.get_block_info(test_ip)
        assert block_info is not None
        assert block_info["reason"] == "Test blocking"
        
        # Unblock the IP
        assert ip_blocklist.unblock_ip(test_ip)
        
        # IP should no longer be blocked
        assert not ip_blocklist.is_ip_blocked(test_ip)
        
        # Test whitelist
        localhost_ip = "127.0.0.1"
        assert not ip_blocklist.is_ip_blocked(localhost_ip)  # Should be whitelisted
        
        return "IP blocklist tests completed successfully"
    
    def test_security_patterns(self):
        """Test security pattern detection"""
        logger.info("🧪 Testing Security Pattern Detection...")
        
        # Test suspicious patterns
        suspicious_patterns = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "javascript:alert('xss')",
            "1' OR '1'='1"
        ]
        
        for pattern in suspicious_patterns:
            # These should trigger security warnings
            sanitized = InputSanitizer.sanitize_sql_input(pattern)
            assert sanitized != pattern  # Should be modified
        
        # Test safe patterns
        safe_patterns = [
            "Hello World",
            "user@example.com",
            "normal_filename.txt",
            "SELECT * FROM users WHERE id = 1"
        ]
        
        for pattern in safe_patterns:
            sanitized = InputSanitizer.sanitize_sql_input(pattern)
            assert sanitized == pattern  # Should be unchanged
        
        return "Security pattern detection tests completed successfully"
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting comprehensive validation framework tests...")
        
        tests = [
            ("Input Sanitizer", self.test_input_sanitizer),
            ("File Upload Validator", self.test_file_upload_validator),
            ("Generic Validation", self.test_generic_validation),
            ("Pydantic Models", self.test_pydantic_models),
            ("Rate Limiter", self.test_rate_limiter),
            ("Request Throttler", self.test_request_throttler),
            ("IP Blocklist", self.test_ip_blocklist),
            ("Security Patterns", self.test_security_patterns)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        self.print_summary()
        
        return self.test_results["failed"] == 0
    
    def print_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {self.test_results['total']}")
        logger.info(f"Passed: {self.test_results['passed']} ✅")
        logger.info(f"Failed: {self.test_results['failed']} ❌")
        logger.info(f"Success Rate: {(self.test_results['passed']/self.test_results['total']*100):.1f}%")
        
        if self.test_results["failed"] > 0:
            logger.info("\n❌ FAILED TESTS:")
            for detail in self.test_results["details"]:
                if detail["status"] == "FAILED":
                    logger.error(f"  - {detail['test']}: {detail['error']}")
        
        logger.info("="*60)

def main():
    """Main test function"""
    try:
        tester = ValidationFrameworkTester()
        success = tester.run_all_tests()
        
        if success:
            logger.info("🎉 All tests passed! Validation framework is working correctly.")
            return 0
        else:
            logger.error("❌ Some tests failed. Please review the errors above.")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

