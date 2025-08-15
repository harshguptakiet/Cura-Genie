#!/usr/bin/env python3
"""
Test script for CuraGenie Error Handling System
Verifies that all components are working correctly
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_error_classes():
    """Test error class creation and properties"""
    print("🧪 Testing Error Classes...")
    
    try:
        from core.errors import (
            CuraGenieError, ValidationError, AuthenticationError,
            ProcessingError, DatabaseError, ExternalServiceError,
            ErrorCode
        )
        
        # Test base error class
        base_error = CuraGenieError(
            message="Test error",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=500
        )
        assert base_error.message == "Test error"
        assert base_error.error_code == ErrorCode.INTERNAL_SERVER_ERROR
        assert base_error.status_code == 500
        print("✅ Base error class working")
        
        # Test specific error classes
        val_error = ValidationError("Invalid input")
        assert val_error.error_code == ErrorCode.VALIDATION_ERROR
        assert val_error.status_code == 400
        print("✅ ValidationError working")
        
        auth_error = AuthenticationError("Auth failed")
        assert auth_error.error_code == ErrorCode.AUTHENTICATION_FAILED
        assert auth_error.status_code == 401
        print("✅ AuthenticationError working")
        
        proc_error = ProcessingError("Processing failed")
        assert proc_error.error_code == ErrorCode.FILE_PROCESSING_FAILED
        assert proc_error.status_code == 422
        print("✅ ProcessingError working")
        
        db_error = DatabaseError("DB failed")
        assert db_error.error_code == ErrorCode.DATABASE_QUERY_ERROR
        assert db_error.status_code == 500
        print("✅ DatabaseError working")
        
        ext_error = ExternalServiceError("External service failed")
        assert ext_error.error_code == ErrorCode.EXTERNAL_API_ERROR
        assert ext_error.status_code == 502
        print("✅ ExternalServiceError working")
        
    except Exception as e:
        print(f"❌ Error classes test failed: {e}")
        return False
    
    return True

def test_error_handler():
    """Test error handler functionality"""
    print("🧪 Testing Error Handler...")
    
    try:
        from core.errors import error_handler, ValidationError, ErrorCode
        
        # Test error handling
        test_error = ValidationError("Test validation error")
        error_response = error_handler.handle_api_error(test_error, {
            "user_id": "test_user",
            "endpoint": "/test/endpoint"
        })
        
        assert error_response["error"] is True
        assert "error_id" in error_response
        assert error_response["status_code"] == 400
        assert "message" in error_response
        print("✅ Error handler working")
        
    except Exception as e:
        print(f"❌ Error handler test failed: {e}")
        return False
    
    return True

def test_logging_config():
    """Test logging configuration"""
    print("🧪 Testing Logging Configuration...")
    
    try:
        from core.logging_config import setup_logging, get_logger
        
        # Setup logging
        setup_logging()
        print("✅ Logging setup completed")
        
        # Test component loggers
        api_logger = get_logger("api")
        db_logger = get_logger("db")
        genomic_logger = get_logger("genomic")
        
        assert api_logger.name == "curagenie_api"
        assert db_logger.name == "curagenie_db"
        assert genomic_logger.name == "curagenie_genomic"
        print("✅ Component loggers working")
        
        # Test logging functions
        from core.logging_config import log_api_request, log_database_operation
        
        log_api_request("GET", "/test", 200, 0.1, "test_user", "req_123")
        log_database_operation("SELECT", "users", True, 0.05)
        print("✅ Logging functions working")
        
    except Exception as e:
        print(f"❌ Logging configuration test failed: {e}")
        return False
    
    return True

def test_error_utilities():
    """Test error utility functions"""
    print("🧪 Testing Error Utilities...")
    
    try:
        from core.error_utils import (
            validate_required_fields, create_success_response,
            create_error_response, sanitize_error_message
        )
        
        # Test validation
        test_data = {"name": "test", "email": "test@example.com"}
        validate_required_fields(test_data, ["name", "email"])
        print("✅ Field validation working")
        
        # Test response creation
        success_resp = create_success_response({"id": 1}, "User created")
        assert success_resp["success"] is True
        assert "data" in success_resp
        
        error_resp = create_error_response("Test error", "TEST_ERROR")
        assert error_resp["success"] is False
        assert error_resp["error"] is True
        print("✅ Response creation working")
        
        # Test message sanitization
        debug_msg = "Password: secret123, Token: abc123"
        sanitized = sanitize_error_message(debug_msg, debug=False)
        assert "secret123" not in sanitized
        assert "abc123" not in sanitized
        print("✅ Message sanitization working")
        
    except Exception as e:
        print(f"❌ Error utilities test failed: {e}")
        return False
    
    return True

def test_middleware_functions():
    """Test middleware utility functions"""
    print("🧪 Testing Middleware Functions...")
    
    try:
        from core.middleware import get_request_id, log_api_call
        
        # Test request ID generation
        request_id = get_request_id(None)
        assert isinstance(request_id, str)
        assert len(request_id) > 0
        print("✅ Request ID generation working")
        
        # Test API call logging
        log_api_call(None, "test_operation", True, {"test": "data"})
        print("✅ API call logging working")
        
    except Exception as e:
        print(f"❌ Middleware functions test failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing Configuration...")
    
    try:
        from core.config import settings
        
        # Test basic settings
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'log_level')
        assert hasattr(settings, 'enable_request_logging')
        assert hasattr(settings, 'enable_operation_logging')
        print("✅ Configuration loading working")
        
        # Test CORS origins parsing
        cors_origins = settings.get_cors_origins()
        assert isinstance(cors_origins, list)
        print("✅ CORS origins parsing working")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting CuraGenie Error Handling System Tests")
    print("=" * 60)
    
    tests = [
        test_error_classes,
        test_error_handler,
        test_logging_config,
        test_error_utilities,
        test_middleware_functions,
        test_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Error handling system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
