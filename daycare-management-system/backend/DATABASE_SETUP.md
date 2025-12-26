# Database Setup Guide

## Overview
This guide will help you set up the PostgreSQL database with all 24 models for Netta's Bounce Around Daycare Management System.

## Prerequisites
- PostgreSQL 12+ installed and running
- Python 3.9+ with virtual environment activated
- All dependencies installed (`pip install -r requirements.txt`)

## Database Models

### Summary
- **24 Total Models** across 6 categories
- All models use UUID primary keys
- Automatic timestamps (created_at, updated_at)
- Comprehensive relationships and cascading deletes
- DCFS compliance-focused design

### Model Categories

#### 1. Children & Family (5 models)
- `Child` - Core child profiles with medical information
- `Parent` - Parent/guardian contact information
- `ChildParent` - Many-to-many relationship table
- `EmergencyContact` - Emergency contacts (DCFS requires minimum 2)
- `AuthorizedPickup` - People authorized to pick up children

#### 2. DCFS Compliance (3 models)
- `EnrollmentForm` - DCFS Form 602 with electronic signatures
- `ImmunizationRecord` - Vaccination records with expiration tracking
- `StaffCredential` - Staff certifications (CPR, First Aid, etc.)

#### 3. Daily Operations (4 models)
- `Attendance` - Daily check-in/check-out with signatures
- `Activity` - Activity logs (meals, naps, diaper changes)
- `Photo` - Photo storage with metadata
- `ChildPhoto` - Many-to-many for photos containing multiple children

#### 4. Health & Safety (3 models)
- `IncidentReport` - DCFS Form 337 for incidents/accidents
- `MedicationAuthorization` - Parent authorization for medications
- `MedicationLog` - Medication administration logs

#### 5. Parent Communication (3 models)
- `DailyReport` - AI-generated daily reports
- `ReportPhoto` - Many-to-many for photos in reports
- `Announcement` - Broadcast announcements to parents

#### 6. Compliance Monitoring (1 model)
- `ComplianceAlert` - Automated alerts for missing/expiring documents

#### 7. User Management (1 model)
- `User` - Staff user accounts with role-based access control

## Setup Steps

### 1. Configure Environment Variables

Make sure your `.env` file has the correct database connection:

```bash
DATABASE_URL="postgresql://username:password@localhost:5432/daycare_db"
```

### 2. Create the Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create the database
CREATE DATABASE daycare_db;

# Exit psql
\q
```

### 3. Initialize Alembic (Already Done)

Alembic has been initialized and configured with:
- Custom `env.py` that imports all models
- Database URL pulled from settings
- Proper metadata configuration

### 4. Generate Migration

```bash
cd backend
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Generate migration
alembic revision --autogenerate -m "Add all daycare models"
```

### 5. Review Migration

Check the generated migration file in `alembic/versions/` to ensure all tables are being created correctly.

### 6. Run Migration

```bash
alembic upgrade head
```

### 7. Verify Database

```bash
# Connect to database
psql -U postgres -d daycare_db

# List all tables
\dt

# Expected tables:
# - alembic_version
# - users
# - children
# - parents
# - child_parents
# - emergency_contacts
# - authorized_pickup
# - enrollment_forms
# - immunization_records
# - staff_credentials
# - attendance
# - activities
# - photos
# - child_photos
# - incident_reports
# - medication_authorizations
# - medication_logs
# - daily_reports
# - report_photos
# - announcements
# - compliance_alerts
```

## Important Schema Notes

### Field Name Changes
The following fields were renamed to avoid conflicts with Python/SQLAlchemy reserved words:

- `child_parents.relationship` → `child_parents.relationship_type`
- `emergency_contacts.relationship` → `emergency_contacts.relationship_type`
- `authorized_pickup.relationship` → `authorized_pickup.relationship_type`

### Indexes
Indexes are automatically created on:
- All foreign keys
- Frequently queried fields (email, phone, dates, status flags)
- Composite indexes for common query patterns

### Cascading Deletes
Parent-child relationships use `cascade="all, delete-orphan"` for automatic cleanup:
- Deleting a child removes all associated records (attendance, activities, reports, etc.)
- Deleting a parent removes child-parent relationships
- Deleting a user removes their created records

## Troubleshooting

### Connection Refused Error
```
sqlalchemy.exc.OperationalError: connection to server at "localhost" refused
```
**Solution**: Start PostgreSQL service
```bash
# Windows
net start postgresql

# Linux/Mac
sudo systemctl start postgresql
```

### Permission Denied Error
**Solution**: Ensure your database user has CREATE privileges:
```sql
GRANT ALL PRIVILEGES ON DATABASE daycare_db TO your_user;
```

### Import Errors
**Solution**: Ensure all models are imported in `app/models/__init__.py`

## Next Steps

After database setup:

1. **Test Database Connection**
   ```bash
   python -c "from app.database import engine; print(engine.connect())"
   ```

2. **Create Initial Admin User**
   ```bash
   # Use the /api/v1/auth/register endpoint
   # Or create via Python script
   ```

3. **Test API Endpoints**
   ```bash
   # Start the server
   uvicorn app.main:app --reload

   # Visit http://localhost:8000/docs for interactive API docs
   ```

4. **Populate Test Data**
   - Create sample children
   - Add parent relationships
   - Test attendance check-in/check-out
   - Generate daily reports

## Maintenance

### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1  # Go back one version
alembic downgrade <revision_id>  # Go to specific version
```

### View Migration History
```bash
alembic history
alembic current
```

## Database Backup

### Backup
```bash
pg_dump -U postgres daycare_db > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
psql -U postgres daycare_db < backup_20250101.sql
```

## Support

For issues or questions:
1. Check the error logs
2. Verify environment variables
3. Ensure PostgreSQL is running
4. Review migration files for conflicts
