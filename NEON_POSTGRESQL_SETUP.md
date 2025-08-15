# 🚀 Neon PostgreSQL Setup Guide for CuraGenie

This guide will help you configure CuraGenie to use your Neon PostgreSQL database instead of the default SQLite database.

## 📋 Prerequisites

- Neon PostgreSQL database account and connection URL
- Python 3.8+ installed
- CuraGenie backend codebase

## 🔧 Configuration Steps

### Step 1: Set Environment Variable

Set your Neon PostgreSQL URL as an environment variable:

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database"
```

**Windows (Command Prompt):**
```cmd
set DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database
```

**Linux/macOS:**
```bash
export DATABASE_URL="postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database"
```

### Step 2: Create .env File (Alternative)

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database

# Other configurations...
SECRET_KEY=your-super-secret-key-here
DEBUG=True
```

### Step 3: Verify Dependencies

Ensure PostgreSQL dependencies are installed:

```bash
cd backend
pip install psycopg2-binary sqlalchemy
```

## 🧪 Testing the Configuration

### Run Database Connection Test

```bash
cd backend
python test_database_connection.py
```

This script will:
- ✅ Check if DATABASE_URL is set
- ✅ Verify PostgreSQL URL format
- ✅ Test database connection
- ✅ Create database tables
- ✅ Provide detailed feedback

### Expected Output

```
🚀 Starting CuraGenie Database Connection Tests
============================================================

🔍 Running: Environment Setup
✅ DATABASE_URL found: postgresql://username:passwor...
✅ Valid PostgreSQL URL format

🔍 Running: Module Imports
✅ Core config imported successfully
✅ Database modules imported successfully

🔍 Running: Database Connection
📊 Database URL: postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database...
✅ Database connection successful!

🔍 Running: Schema Creation
✅ Database tables created successfully!

============================================================
📊 Test Results: 4/4 tests passed
🎉 All tests passed! Your Neon PostgreSQL database is ready to use.
```

## 🚀 Starting the Application

### Test Database Connection on Startup

The application now automatically tests the database connection on startup. You'll see:

```
🔍 Testing database connection...
✅ Connected to Neon PostgreSQL database successfully!
```

### Start the Backend

```bash
cd backend
python main.py
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Connection Timeout
```
❌ Database connection failed: connection to server at "host" failed: timeout expired
```

**Solution:** Check your Neon database status and network connectivity.

#### 2. Authentication Failed
```
❌ Database connection failed: FATAL: password authentication failed
```

**Solution:** Verify your username and password in the DATABASE_URL.

#### 3. Database Not Found
```
❌ Database connection failed: FATAL: database "database_name" does not exist
```

**Solution:** Create the database in your Neon dashboard or check the database name.

#### 4. Module Import Errors
```
❌ Import error: No module named 'psycopg2'
```

**Solution:** Install the PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

### Environment Variable Issues

#### Check if DATABASE_URL is Set

**Windows (PowerShell):**
```powershell
echo $env:DATABASE_URL
```

**Windows (Command Prompt):**
```cmd
echo %DATABASE_URL%
```

**Linux/macOS:**
```bash
echo $DATABASE_URL
```

#### Verify URL Format

Your Neon URL should look like:
```
postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database
```

## 📊 Database Schema

The application will automatically create the following tables in your Neon PostgreSQL database:

- **users** - User authentication and profiles
- **patient_profiles** - Patient-specific medical information
- **medical_reports** - Medical reports and documents
- **genomic_data** - Genomic file metadata
- **genomic_variants** - Individual genetic variants
- **prs_scores** - Polygenic risk scores
- **ml_predictions** - Machine learning predictions
- **timeline_events** - User activity timeline
- **uploaded_files** - File upload tracking

## 🔒 Security Considerations

- **Never commit your .env file** to version control
- **Use strong passwords** for your database
- **Enable SSL connections** if available in Neon
- **Regularly rotate database credentials**
- **Monitor database access logs**

## 📈 Performance Optimization

### Connection Pooling

The application is configured with PostgreSQL-optimized connection pooling:

- **Pool Size:** 10 connections
- **Max Overflow:** 20 connections
- **Connection Timeout:** 10 seconds
- **Pool Recycle:** 300 seconds

### Neon-Specific Optimizations

- **Connection Pre-ping:** Enabled for connection health checks
- **Application Name:** Set to "CuraGenie" for monitoring
- **Automatic Cleanup:** Old connections are automatically recycled

## 🔄 Migration from SQLite

If you're migrating from an existing SQLite database:

1. **Backup your SQLite database**
2. **Set up Neon PostgreSQL**
3. **Run the database connection test**
4. **The application will create new tables automatically**
5. **Data migration scripts are available in the `migrations/` directory**

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Run the database connection test script**
3. **Verify your Neon database status**
4. **Check the application logs for detailed error messages**

## 🎯 Next Steps

After successful configuration:

1. **Test the authentication system** with the new database
2. **Upload and process genomic files** to verify data storage
3. **Monitor database performance** in your Neon dashboard
4. **Set up database backups** and monitoring

---

**🎉 Congratulations!** Your CuraGenie application is now configured to use Neon PostgreSQL for production-ready, scalable database operations.
