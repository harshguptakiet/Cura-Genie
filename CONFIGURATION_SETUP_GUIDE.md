# 🔧 CuraGenie Configuration Setup Guide

This guide covers the new structured configuration system that replaces hardcoded values with environment-specific, secure configurations.

## 📋 Overview

The new configuration system provides:
- **Environment-Specific Configurations**: Development, Staging, and Production
- **Secure Secrets Management**: No more hardcoded secrets
- **Automatic Validation**: Configuration validation on startup
- **Docker Support**: Multi-stage builds for each environment
- **Security Best Practices**: CORS validation, secret strength checking

## 🚀 Quick Start

### 1. **Choose Your Environment**
```bash
# Development (default)
ENVIRONMENT=development

# Staging
ENVIRONMENT=staging

# Production
ENVIRONMENT=production
```

### 2. **Copy Environment Template**
```bash
cd backend

# For development
cp env.development.template .env.development

# For staging
cp env.staging.template .env.staging

# For production
cp env.production.template .env.production
```

### 3. **Validate Configuration**
```bash
# Validate development config
python validate_config.py --env development

# Validate staging config
python validate_config.py --env staging

# Validate production config
python validate_config.py --env production
```

## 🔧 Environment-Specific Setup

### **Development Environment**
```bash
# Copy template
cp env.development.template .env.development

# Edit .env.development (optional - safe defaults provided)
nano .env.development

# Validate
python validate_config.py --env development
```

**Features:**
- ✅ Safe defaults for all values
- ✅ SQLite database support
- ✅ Localhost CORS origins
- ✅ Debug mode enabled
- ✅ Development logging

### **Staging Environment**
```bash
# Copy template
cp env.staging.template .env.staging

# Edit .env.staging (REQUIRED values)
nano .env.staging

# Validate
python validate_config.py --env staging
```

**Required Values:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CORS_ORIGINS` - Allowed origins
- `SECRET_KEY` - Strong secret key
- `JWT_SECRET_KEY` - Strong JWT secret

### **Production Environment**
```bash
# Copy template
cp env.production.template .env.production

# Edit .env.production (ALL values required)
nano .env.production

# Generate strong secrets
python validate_config.py --env production

# Validate
python validate_config.py --env production
```

**Required Values:**
- All staging values PLUS
- HTTPS-only CORS origins
- Strong secrets (32+ characters)
- Production logging settings

## 🔐 Secrets Management

### **Generating Strong Secrets**
```bash
# Use the validation tool to generate secrets
python validate_config.py --env production

# Or generate manually
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **Secret Requirements**
- **Minimum Length**: 32 characters
- **Format**: URL-safe base64
- **Storage**: Environment variables only
- **Rotation**: Regular rotation recommended

### **Forbidden Values**
```bash
# NEVER use these in production
"your-super-secret-key-here"
"dev-secret-key-change-in-production"
"your-staging-secret-key-here"
"your-production-secret-key-here"
```

## 🐳 Docker Configuration

### **Multi-Stage Builds**
```bash
# Build for specific environment
docker build -f backend/Dockerfile.multi --target development -t curagenie:dev .
docker build -f backend/Dockerfile.multi --target staging -t curagenie:staging .
docker build -f backend/Dockerfile.multi --target production -t curagenie:prod .
```

### **Docker Compose**
```bash
# Development
ENVIRONMENT=development docker-compose up

# Staging
ENVIRONMENT=staging docker-compose up

# Production
ENVIRONMENT=production docker-compose up
```

### **Environment Variables in Docker**
```bash
# Set environment for docker-compose
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@host:port/db
export SECRET_KEY=your-strong-secret-key
export CORS_ORIGINS=https://app.curagenie.com

# Start services
docker-compose up
```

## 🔍 Configuration Validation

### **What Gets Validated**
1. **Environment Variables**: Required vs. optional
2. **Secrets Strength**: Length and format
3. **Database Configuration**: Connection strings
4. **CORS Configuration**: Security and format
5. **Security Settings**: Production requirements

### **Validation Commands**
```bash
# Basic validation
python validate_config.py

# Environment-specific validation
python validate_config.py --env development
python validate_config.py --env staging
python validate_config.py --env production

# Help
python validate_config.py --help
```

### **Validation Output Example**
```
🚀 Starting configuration validation for production environment...

🔍 Validating environment variables for production environment...
🔐 Validating secrets strength for production environment...
🗄️ Validating database configuration...
🌐 Validating CORS configuration...

============================================================
📊 Configuration Validation Results
============================================================

🔍 Environment: production
✅ All required environment variables are set

🔐 Secrets Validation:
✅ All secrets meet strength requirements

🗄️ Database Validation:
✅ Database configuration is valid

🌐 CORS Validation:
✅ CORS configuration is valid

============================================================
🎉 Configuration validation PASSED!
✅ Your configuration is ready for deployment
```

## 🚨 Common Issues & Solutions

### **Missing Environment Variables**
```bash
❌ Required variables missing: DATABASE_URL, SECRET_KEY

# Solution: Set the missing variables
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your-strong-secret-key"
```

### **Weak Secrets**
```bash
❌ SECRET_KEY is too short (minimum 32 characters)

# Solution: Generate strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **Invalid CORS Configuration**
```bash
❌ Wildcard CORS origin (*) not allowed in production

# Solution: Specify exact origins
export CORS_ORIGINS="https://app.curagenie.com,https://www.curagenie.com"
```

### **Database Connection Issues**
```bash
❌ DATABASE_URL not set

# Solution: Set database URL
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

## 📊 Environment Comparison

| Feature | Development | Staging | Production |
|---------|-------------|---------|------------|
| **Debug Mode** | ✅ Enabled | ❌ Disabled | ❌ Disabled |
| **Log Level** | DEBUG | DEBUG | INFO |
| **Database** | SQLite | PostgreSQL | PostgreSQL |
| **CORS Origins** | localhost | HTTPS | HTTPS Only |
| **Secrets** | Defaults OK | Strong Required | Strong Required |
| **Validation** | Basic | Strict | Strictest |

## 🔄 Migration from Old System

### **Step 1: Backup Current Configuration**
```bash
# Backup current .env file
cp .env .env.backup
```

### **Step 2: Create New Environment File**
```bash
# Choose your environment
cp env.development.template .env.development
# or
cp env.staging.template .env.staging
# or
cp env.production.template .env.production
```

### **Step 3: Migrate Values**
```bash
# Copy relevant values from old .env
grep -E "^(DATABASE_URL|SECRET_KEY|CORS_ORIGINS)=" .env.backup >> .env.development
```

### **Step 4: Validate**
```bash
python validate_config.py --env development
```

## 🧪 Testing Configuration

### **Test Configuration Loading**
```bash
cd backend
python -c "from core.config import config_manager; print('Config loaded successfully')"
```

### **Test Environment Detection**
```bash
export ENVIRONMENT=production
python -c "from core.config import config_manager; print(f'Environment: {config_manager.environment}')"
```

### **Test Secrets Management**
```bash
export SECRET_KEY="test-secret-key"
python -c "from core.config import config_manager; print(config_manager.get_secret('SECRET_KEY'))"
```

## 📝 Configuration Files Reference

### **Environment Templates**
- `env.development.template` - Development configuration
- `env.staging.template` - Staging configuration
- `env.production.template` - Production configuration

### **Configuration Files**
- `backend/core/config.py` - Main configuration system
- `backend/validate_config.py` - Configuration validation tool
- `backend/Dockerfile.multi` - Multi-stage Docker builds
- `docker-compose.yml` - Environment-aware Docker Compose

### **Generated Files**
- `.env.development` - Development environment (create from template)
- `.env.staging` - Staging environment (create from template)
- `.env.production` - Production environment (create from template)

## 🎯 Next Steps

### **Immediate Actions**
1. **Choose your environment** (development/staging/production)
2. **Copy the appropriate template** to `.env.{environment}`
3. **Fill in required values** (especially for staging/production)
4. **Validate your configuration** using the validation tool
5. **Test the application** with the new configuration

### **Advanced Configuration**
1. **Customize logging** for your environment
2. **Configure external services** (OpenAI, AWS, etc.)
3. **Set up monitoring** and health checks
4. **Configure backup strategies** for production

### **Security Hardening**
1. **Rotate secrets** regularly
2. **Monitor access logs** for suspicious activity
3. **Implement rate limiting** for production APIs
4. **Set up alerting** for configuration issues

---

## 🆘 Need Help?

### **Validation Issues**
```bash
# Run validation with verbose output
python validate_config.py --env production

# Check specific environment variables
echo $ENVIRONMENT
echo $DATABASE_URL
echo $SECRET_KEY
```

### **Configuration Problems**
```bash
# Test configuration loading
python -c "from core.config import config_manager; config_manager.print_config_summary()"

# Check environment detection
python -c "from core.config import config_manager; print(config_manager.environment)"
```

### **Docker Issues**
```bash
# Check environment variables in container
docker-compose exec backend env | grep -E "(ENVIRONMENT|DATABASE_URL|SECRET_KEY)"

# Validate configuration in container
docker-compose exec backend python validate_config.py --env production
```

---

**🎉 Congratulations!** You've successfully set up the new CuraGenie configuration system. Your application is now more secure, maintainable, and ready for production deployment.
