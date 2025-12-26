# Test Suite Documentation

## Overview

Comprehensive test suite for Netta's Bounce Around Daycare Management System API.

## Test Structure

```
tests/
├── conftest.py                    # Test configuration and fixtures
├── pytest.ini                     # Pytest configuration
└── api/
    └── v1/
        └── endpoints/
            ├── test_auth.py       # Authentication tests (10 tests)
            ├── test_children.py   # Children management tests (11 tests)
            ├── test_parents.py    # Parents management tests (9 tests)
            └── test_compliance.py # Compliance tests (11 tests)
```

**Total Tests:** 41 comprehensive test cases

## Running Tests

### Run All Tests
```bash
cd backend
.venv/Scripts/python -m pytest tests/ -v
```

### Run Specific Test File
```bash
.venv/Scripts/python -m pytest tests/api/v1/endpoints/test_auth.py -v
```

### Run with Coverage
```bash
.venv/Scripts/python -m pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test Class
```bash
.venv/Scripts/python -m pytest tests/api/v1/endpoints/test_auth.py::TestUserLogin -v
```

### Run Specific Test
```bash
.venv/Scripts/python -m pytest tests/api/v1/endpoints/test_auth.py::TestUserLogin::test_login_success -v
```

## Test Categories

### 1. Authentication Tests (`test_auth.py`)

**TestUserRegistration:**
- ✅ `test_register_new_user` - Successful user registration
- ✅ `test_register_duplicate_email` - Prevent duplicate email registration
- ✅ `test_register_invalid_email` - Email format validation

**TestUserLogin:**
- ✅ `test_login_success` - Successful login with valid credentials
- ✅ `test_login_wrong_password` - Reject incorrect password
- ✅ `test_login_nonexistent_user` - Reject non-existent email
- ✅ `test_login_inactive_user` - Reject inactive user accounts

**TestCurrentUser:**
- ✅ `test_get_current_user` - Get authenticated user info
- ✅ `test_get_current_user_no_token` - Reject requests without token
- ✅ `test_get_current_user_invalid_token` - Reject invalid tokens

### 2. Children Tests (`test_children.py`)

**TestChildrenEndpoints:**
- ✅ `test_create_child` - Create new child record
- ✅ `test_get_all_children` - List all children
- ✅ `test_get_active_children_only` - Filter active children
- ✅ `test_get_child_by_id` - Get specific child details
- ✅ `test_update_child` - Update child information
- ✅ `test_deactivate_child` - Deactivate child enrollment
- ✅ `test_activate_child` - Reactivate child enrollment
- ✅ `test_get_nonexistent_child` - Handle 404 for missing child
- ✅ `test_create_child_unauthenticated` - Require authentication

**TestChildParentRelationships:**
- ✅ `test_link_parent_to_child` - Create child-parent relationship
- ✅ `test_get_child_parents` - Get all parents for a child

### 3. Parents Tests (`test_parents.py`)

**TestParentsEndpoints:**
- ✅ `test_create_parent` - Create new parent record
- ✅ `test_get_all_parents` - List all parents
- ✅ `test_get_parent_by_id` - Get specific parent details
- ✅ `test_update_parent` - Update parent information
- ✅ `test_search_parents_by_name` - Search parents by name
- ✅ `test_search_parents_by_email` - Search parents by email
- ✅ `test_get_parent_children` - Get all children for a parent
- ✅ `test_delete_parent_admin_only` - Enforce admin-only deletion
- ✅ `test_delete_parent_as_admin` - Allow admin to delete parents

### 4. Compliance Tests (`test_compliance.py`)

**TestEnrollmentForms:**
- ✅ `test_create_enrollment_form` - Create DCFS Form 602
- ✅ `test_get_enrollment_forms` - List all enrollment forms
- ✅ `test_get_incomplete_forms` - Find incomplete forms

**TestImmunizationRecords:**
- ✅ `test_create_immunization_record` - Add vaccine record
- ✅ `test_get_child_immunizations` - Get child's vaccination history
- ✅ `test_get_expiring_immunizations` - Alert for expiring vaccines

**TestStaffCredentials:**
- ✅ `test_create_staff_credential` - Add staff credential (CPR, First Aid, etc.)
- ✅ `test_get_user_credentials` - Get all credentials for a staff member
- ✅ `test_get_expired_credentials` - Find expired credentials
- ✅ `test_get_expiring_credentials` - Alert for soon-to-expire credentials
- ✅ `test_invalid_credential_type` - Validate credential types

## Test Fixtures

### Database Fixtures
- **`db`** - Fresh in-memory SQLite database for each test
- **`client`** - TestClient with database dependency override

### User Fixtures
- **`test_user`** - Standard staff user account
- **`test_admin`** - Admin user account
- **`auth_headers`** - Authentication headers for test_user
- **`admin_headers`** - Authentication headers for test_admin

### Data Fixtures
- **`test_child`** - Sample child record
- **`test_parent`** - Sample parent record
- **`test_child_with_parent`** - Child with linked parent relationship

## Test Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short --disable-warnings
```

### Key Features
- **In-memory SQLite** for fast test execution
- **Function-scoped fixtures** for test isolation
- **Automatic database cleanup** after each test
- **JWT token authentication** testing
- **Comprehensive error handling** verification

## Test Credentials

**Test User:**
- Email: `test@example.com`
- Password: `testpass123`
- Role: `staff`

**Test Admin:**
- Email: `admin@example.com`
- Password: `adminpass123`
- Role: `admin`

## Expected Test Results

When properly configured, all tests should pass:
```
============================= test session starts ==============================
collected 41 items

tests/api/v1/endpoints/test_auth.py::TestUserRegistration::... PASSED
tests/api/v1/endpoints/test_auth.py::TestUserLogin::... PASSED
tests/api/v1/endpoints/test_auth.py::TestCurrentUser::... PASSED
tests/api/v1/endpoints/test_children.py::TestChildrenEndpoints::... PASSED
tests/api/v1/endpoints/test_children.py::TestChildParentRelationships::... PASSED
tests/api/v1/endpoints/test_parents.py::TestParentsEndpoints::... PASSED
tests/api/v1/endpoints/test_compliance.py::TestEnrollmentForms::... PASSED
tests/api/v1/endpoints/test_compliance.py::TestImmunizationRecords::... PASSED
tests/api/v1/endpoints/test_compliance.py::TestStaffCredentials::... PASSED

============================== 41 passed in X.XXs ===============================
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
```bash
# In CI/CD environment
python -m pytest tests/ --cov=app --cov-report=xml
```

## Adding New Tests

### 1. Create Test File
```python
# tests/api/v1/endpoints/test_feature.py
import pytest
from fastapi import status
from app.core.config import settings

class TestFeature:
    def test_create_feature(self, client, auth_headers):
        response = client.post(
            f"{settings.API_V1_PREFIX}/feature/",
            headers=auth_headers,
            json={"name": "test"}
        )
        assert response.status_code == status.HTTP_201_CREATED
```

### 2. Use Fixtures
```python
def test_with_test_data(self, client, auth_headers, test_child):
    # test_child fixture provides a pre-created child
    response = client.get(
        f"{settings.API_V1_PREFIX}/children/{test_child.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
```

### 3. Add Custom Fixtures
```python
# In conftest.py
@pytest.fixture(scope="function")
def test_feature(db):
    feature = Feature(name="Test Feature")
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature
```

## Troubleshooting

### Tests Failing
1. Ensure virtual environment is activated
2. Install test dependencies: `pip install pytest pytest-cov httpx`
3. Check database is not locked
4. Verify all models are properly imported in `conftest.py`

### Database Errors
- Tests use in-memory SQLite, not PostgreSQL
- Each test gets a fresh database
- Check model definitions for SQLite compatibility

### Authentication Errors
- Verify JWT secret key is set
- Check token expiration settings
- Ensure password hashing is working correctly

## Next Steps

- Add integration tests for workflow scenarios
- Add performance benchmarks
- Add API documentation tests
- Implement test coverage reporting
- Add mutation testing
