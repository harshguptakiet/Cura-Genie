# CuraGenie Error Handling and Logging System Implementation

## Overview

This document describes the comprehensive error handling and logging system implemented for the CuraGenie platform. The system provides centralized error handling, structured logging, consistent error responses, and user-friendly error reporting.

## 🏗️ Architecture

The error handling system is built with a layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ErrorBoundary | ErrorReporter | Toast Notifications      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Layer                                │
├─────────────────────────────────────────────────────────────┤
│  Middleware | Exception Handlers | Error Utilities         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Layer                                │
├─────────────────────────────────────────────────────────────┤
│  Error Handler | Logging Config | Error Classes            │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Backend Implementation

### 1. Core Error Classes (`backend/core/errors.py`)

#### Error Code Enumeration
- **Validation Errors (1000-1999)**: Input validation failures
- **Authentication Errors (2000-2999)**: Auth and permission issues
- **Processing Errors (3000-3999)**: File processing and analysis failures
- **Database Errors (4000-4999)**: Database operation failures
- **External Service Errors (5000-5999)**: Third-party service failures
- **System Errors (9000-9999)**: Internal system failures

#### Exception Classes
```python
class CuraGenieError(Exception):
    """Base exception class with error codes and context"""
    
class ValidationError(CuraGenieError):
    """Raised when input validation fails"""
    
class AuthenticationError(CuraGenieError):
    """Raised when authentication fails"""
    
class ProcessingError(CuraGenieError):
    """Raised when file processing fails"""
    
class DatabaseError(CuraGenieError):
    """Raised when database operations fail"""
    
class ExternalServiceError(CuraGenieError):
    """Raised when external service calls fail"""
```

#### Error Handler
```python
class CuraGenieErrorHandler:
    """Centralized error handler with structured logging"""
    
    def handle_api_error(self, error: Exception, context: dict) -> dict:
        # Generates unique error ID
        # Logs structured error information
        # Returns user-friendly error response
```

### 2. Middleware (`backend/core/middleware.py`)

#### Request ID Middleware
- Generates unique request ID for each request
- Adds request ID to response headers (`X-Request-ID`)
- Enables request tracing across the system

#### Logging Middleware
- Logs request start/end with timing information
- Adds process time to response headers (`X-Process-Time`)
- Captures request context for debugging

#### Error Handling Middleware
- Ensures all errors are caught and handled
- Integrates with global exception handlers

### 3. Exception Handlers (`backend/core/exception_handlers.py`)

#### Global Exception Handlers
```python
# Pydantic validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError)

# CuraGenie-specific exceptions
async def curagenie_exception_handler(request: Request, exc: CuraGenieError)

# General unhandled exceptions
async def general_exception_handler(request: Request, exc: Exception)
```

#### Standardized Error Responses
All errors return consistent JSON format:
```json
{
  "error": true,
  "error_id": "uuid-string",
  "message": "User-friendly error message",
  "status_code": 400,
  "details": {} // Only in debug mode
}
```

### 4. Logging Configuration (`backend/core/logging_config.py`)

#### Structured Logging
- JSON format for machine-readable logs
- Console and file handlers
- Log rotation with configurable retention
- Component-specific loggers

#### Log Categories
- **Application Logs**: General application events
- **Error Logs**: All error occurrences
- **Request Logs**: HTTP request/response details
- **Operation Logs**: Business operation results

### 5. Error Utilities (`backend/core/error_utils.py`)

#### Decorators and Helpers
```python
@handle_errors
async def api_endpoint():
    # Automatic error handling and logging
    
@safe_database_operation("user_creation")
def create_user():
    # Database operation with retry logic
```

#### Validation Functions
```python
validate_file_upload(file_size, max_size, allowed_types)
validate_user_permissions(user_id, required_role, resource_owner_id)
validate_required_fields(data, required_fields)
```

## 🎨 Frontend Implementation

### 1. Error Handler (`frontend/src/lib/error-handler.ts`)

#### Error Classes
```typescript
class CuraGenieError extends Error {
  public readonly errorId: string;
  public readonly statusCode: number;
  public readonly details?: any;
  public readonly context?: ErrorContext;
}

class ValidationError extends CuraGenieError {}
class AuthenticationError extends CuraGenieError {}
class ProcessingError extends CuraGenieError {}
class NetworkError extends CuraGenieError {}
```

#### Global Error Handling
- Catches unhandled promise rejections
- Catches JavaScript errors
- Provides error reporting to backend
- Maintains error queue for debugging

### 2. Error Boundary (`frontend/src/components/error/ErrorBoundary.tsx`)

#### React Error Boundary
- Catches JavaScript errors in component tree
- Provides fallback UI when errors occur
- Integrates with error handler for reporting
- Supports custom fallback components

#### Higher-Order Component
```typescript
const SafeComponent = withErrorBoundary(MyComponent, 'MyComponent');
```

### 3. Toast Notifications (`frontend/src/components/ui/toast-notifications.tsx`)

#### Toast System
- Success, error, warning, and info notifications
- Configurable duration and positioning
- Global functions for use outside React components
- Accessible design with ARIA labels

#### Usage
```typescript
const { showSuccess, showError } = useToast();
showSuccess('Operation completed', 'Your file was uploaded successfully');
showError('Upload failed', 'Please check your file and try again');
```

### 4. Error Reporter (`frontend/src/components/error/ErrorReporter.tsx`)

#### User Error Reporting
- Allows users to describe what they were doing
- Provides technical error details (in development)
- Integrates with backend error tracking
- Copy error details to clipboard

## 📊 Logging Structure

### Error Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "service": "curagenie-backend",
  "error_id": "err_abc123",
  "user_id": "user_456",
  "endpoint": "/api/genomic-data/upload",
  "error_type": "FileProcessingError",
  "error_code": 3000,
  "message": "Failed to process VCF file",
  "status_code": 422,
  "context": {
    "filename": "sample.vcf",
    "file_size": 1024000,
    "file_type": "vcf"
  },
  "stack_trace": "...",
  "request_id": "req_789"
}
```

### Request Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "curagenie-backend",
  "request_id": "req_789",
  "user_id": "user_456",
  "endpoint": "POST /api/genomic-data/upload",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "process_time": 1.234
}
```

## 🚀 Usage Examples

### Backend API Endpoints

#### Basic Error Handling
```python
from core.errors import ValidationError, ProcessingError
from core.error_utils import handle_errors

@handle_errors
async def upload_file(request: Request, file: UploadFile):
    # Validate file
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("File too large", {
            "file_size": file.size,
            "max_size": MAX_FILE_SIZE
        })
    
    # Process file
    try:
        result = process_genomic_file(file)
        return {"success": True, "result": result}
    except Exception as e:
        raise ProcessingError(f"Failed to process file: {e}")
```

#### Database Operations
```python
from core.error_utils import safe_database_operation

@safe_database_operation("user_creation")
def create_user(user_data):
    # Database operation with automatic retry logic
    return db.users.create(user_data)
```

### Frontend Components

#### Error Boundary Usage
```tsx
import { ErrorBoundary } from '@/components/error/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary componentName="App">
      <YourApp />
    </ErrorBoundary>
  );
}
```

#### Error Handling in Components
```tsx
import { useErrorHandler } from '@/components/error/ErrorBoundary';
import { withErrorHandling } from '@/lib/error-handler';

function MyComponent() {
  const { handleError } = useErrorHandler();
  
  const handleSubmit = withErrorHandling(async (data) => {
    const response = await api.submit(data);
    return response;
  }, 'MyComponent', 'form_submit');
  
  return (
    <form onSubmit={handleSubmit}>
      {/* form content */}
    </form>
  );
}
```

#### Toast Notifications
```tsx
import { useToast } from '@/components/ui/toast-notifications';

function MyComponent() {
  const { showSuccess, showError } = useToast();
  
  const handleAction = async () => {
    try {
      await api.performAction();
      showSuccess('Success!', 'Action completed successfully');
    } catch (error) {
      showError('Error', 'Failed to perform action');
    }
  };
}
```

## ⚙️ Configuration

### Environment Variables
```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/curagenie.log
ERROR_LOG_PATH=logs/errors.log
REQUEST_LOG_PATH=logs/requests.log
OPERATION_LOG_PATH=logs/operations.log

# Error Handling
ENABLE_REQUEST_LOGGING=true
ENABLE_OPERATION_LOGGING=true
LOG_RETENTION_DAYS=30
ENABLE_ERROR_TRACKING=true
ERROR_ALERT_THRESHOLD=10
```

### Configuration File
```python
# backend/core/config.py
class Settings(BaseSettings):
    # Error Handling and Logging
    log_level: str = "INFO"
    log_file_path: str = "logs/curagenie.log"
    error_log_path: str = "logs/errors.log"
    request_log_path: str = "logs/requests.log"
    operation_log_path: str = "logs/operations.log"
    enable_request_logging: bool = True
    enable_operation_logging: bool = True
    log_retention_days: int = 30
    enable_error_tracking: bool = True
    error_alert_threshold: int = 10
```

## 🔍 Monitoring and Debugging

### Error Tracking
- Unique error IDs for each error occurrence
- Request ID tracing across the system
- Structured logging for easy parsing
- Error rate monitoring and alerting

### Debug Information
- Stack traces in development mode
- Request context and parameters
- User agent and IP address logging
- Performance timing information

### Log Analysis
- JSON format for easy parsing
- Component-specific loggers
- Log rotation and retention policies
- Centralized error reporting

## 🧪 Testing

### Error Scenarios
- Invalid input validation
- Authentication failures
- File processing errors
- Database connection issues
- External service failures
- Network timeouts

### Testing Utilities
```python
# Test error handling
def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_file_upload(0, 100, ['vcf'])
    assert exc_info.value.error_code == ErrorCode.INVALID_FILE_FORMAT

# Test error responses
def test_error_response_format():
    response = client.post("/api/test", json={"invalid": "data"})
    assert response.status_code == 422
    assert "error_id" in response.json()
    assert response.json()["error"] is True
```

## 📈 Benefits

### Developer Experience
- **Consistent Error Handling**: All errors follow the same pattern
- **Structured Logging**: Easy to parse and analyze logs
- **Request Tracing**: Track requests across the system
- **Debug Information**: Rich context for troubleshooting

### User Experience
- **User-Friendly Messages**: Clear, actionable error messages
- **Error Reporting**: Users can help improve the system
- **Toast Notifications**: Immediate feedback on actions
- **Error Recovery**: Automatic retry mechanisms

### System Reliability
- **Error Monitoring**: Track error patterns and rates
- **Performance Tracking**: Monitor operation timing
- **Centralized Logging**: Single source of truth for system events
- **Error Prevention**: Validation and error handling patterns

## 🚀 Future Enhancements

### Phase 4: Monitoring and Alerting
- Integration with external logging services (DataDog, LogRocket)
- Error rate monitoring and alerts
- Error pattern detection
- Performance monitoring for error-prone operations

### Advanced Features
- Machine learning for error pattern recognition
- Automated error resolution suggestions
- User behavior analysis during errors
- A/B testing for error message effectiveness

## 📚 Conclusion

The CuraGenie error handling and logging system provides a robust foundation for building reliable, user-friendly applications. By implementing structured error handling, comprehensive logging, and user-friendly error reporting, the system improves developer productivity, user experience, and system reliability.

The modular design allows for easy extension and customization, while the consistent patterns ensure that all new code follows proper error handling practices. This implementation addresses the fundamental infrastructure need identified in issue1.md and provides a solid foundation for future development.
