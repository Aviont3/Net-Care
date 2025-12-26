# Compliance Endpoint Tests
# ============================================

import pytest
from datetime import date, timedelta
from fastapi import status
from app.core.config import settings


class TestEnrollmentForms:
    """Test enrollment form endpoints"""

    def test_create_enrollment_form(self, client, auth_headers, test_child):
        """Test creating an enrollment form"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/compliance/enrollment-forms/",
            headers=auth_headers,
            json={
                "child_id": str(test_child.id),
                "enrollment_date": "2024-01-10",
                "is_complete": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["child_id"] == str(test_child.id)
        assert data["enrollment_date"] == "2024-01-10"
        assert data["is_complete"] is True

    def test_get_enrollment_forms(self, client, auth_headers, test_child, db):
        """Test getting all enrollment forms"""
        from app.models.compliance import EnrollmentForm

        # Create test forms
        form1 = EnrollmentForm(
            child_id=test_child.id,
            enrollment_date=date.today(),
            is_complete=True
        )
        form2 = EnrollmentForm(
            child_id=test_child.id,
            enrollment_date=date.today(),
            is_complete=False
        )
        db.add_all([form1, form2])
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/enrollment-forms/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2

    def test_get_incomplete_forms(self, client, auth_headers, test_child, db):
        """Test getting incomplete enrollment forms"""
        from app.models.compliance import EnrollmentForm

        incomplete_form = EnrollmentForm(
            child_id=test_child.id,
            enrollment_date=date.today(),
            is_complete=False
        )
        db.add(incomplete_form)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/enrollment-forms/incomplete/list",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert data[0]["has_parent_signature"] is False or data[0]["has_staff_signature"] is False


class TestImmunizationRecords:
    """Test immunization record endpoints"""

    def test_create_immunization_record(self, client, auth_headers, test_child):
        """Test creating an immunization record"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/compliance/immunizations/",
            headers=auth_headers,
            json={
                "child_id": str(test_child.id),
                "vaccine_name": "MMR",
                "administration_date": "2023-06-15",
                "expiration_date": "2028-06-15",
                "provider_name": "Dr. Smith",
                "is_verified": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["vaccine_name"] == "MMR"
        assert data["provider_name"] == "Dr. Smith"
        assert data["is_verified"] is True

    def test_get_child_immunizations(self, client, auth_headers, test_child, db):
        """Test getting immunizations for a specific child"""
        from app.models.compliance import ImmunizationRecord

        record = ImmunizationRecord(
            child_id=test_child.id,
            vaccine_name="Hepatitis B",
            administration_date=date(2023, 1, 15),
            expiration_date=date(2028, 1, 15),
            provider_name="Dr. Johnson",
            is_verified=True
        )
        db.add(record)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/immunizations/child/{test_child.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert data[0]["vaccine_name"] == "Hepatitis B"

    def test_get_expiring_immunizations(self, client, auth_headers, test_child, db):
        """Test getting soon-to-expire immunizations"""
        from app.models.compliance import ImmunizationRecord

        # Create immunization expiring in 20 days
        expiring_record = ImmunizationRecord(
            child_id=test_child.id,
            vaccine_name="Flu Shot",
            administration_date=date.today() - timedelta(days=345),
            expiration_date=date.today() + timedelta(days=20),
            provider_name="Dr. Brown",
            is_verified=True
        )
        db.add(expiring_record)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/immunizations/expiring/soon?days=30",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert data[0]["vaccine_name"] == "Flu Shot"
        assert data[0]["days_until_expiration"] <= 30


class TestStaffCredentials:
    """Test staff credential endpoints"""

    def test_create_staff_credential(self, client, auth_headers, test_user):
        """Test creating a staff credential"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/compliance/staff-credentials/",
            headers=auth_headers,
            json={
                "user_id": str(test_user.id),
                "credential_type": "CPR",
                "credential_number": "CPR123456",
                "issue_date": "2024-01-15",
                "expiration_date": "2026-01-15",
                "is_verified": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["credential_type"] == "CPR"
        assert data["credential_number"] == "CPR123456"
        assert data["is_verified"] is True

    def test_get_user_credentials(self, client, auth_headers, test_user, db):
        """Test getting credentials for a specific user"""
        from app.models.compliance import StaffCredential

        credential = StaffCredential(
            user_id=test_user.id,
            credential_type="First Aid",
            credential_number="FA987654",
            issue_date=date(2024, 1, 1),
            expiration_date=date(2025, 1, 1),
            is_verified=True
        )
        db.add(credential)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/staff-credentials/user/{test_user.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert data[0]["credential_type"] == "First Aid"

    def test_get_expired_credentials(self, client, auth_headers, test_user, db):
        """Test getting expired credentials"""
        from app.models.compliance import StaffCredential

        expired_credential = StaffCredential(
            user_id=test_user.id,
            credential_type="Background Check",
            credential_number="BC123456",
            issue_date=date(2022, 1, 1),
            expiration_date=date.today() - timedelta(days=30),
            is_verified=True,
            is_expired=True
        )
        db.add(expired_credential)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/staff-credentials/expired/list",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0

    def test_get_expiring_credentials(self, client, auth_headers, test_user, db):
        """Test getting soon-to-expire credentials"""
        from app.models.compliance import StaffCredential

        expiring_credential = StaffCredential(
            user_id=test_user.id,
            credential_type="TB Test",
            credential_number="TB789456",
            issue_date=date.today() - timedelta(days=335),
            expiration_date=date.today() + timedelta(days=25),
            is_verified=True
        )
        db.add(expiring_credential)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/compliance/staff-credentials/expiring/soon?days=30",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert data[0]["credential_type"] == "TB Test"
        assert data[0]["days_until_expiration"] <= 30

    def test_invalid_credential_type(self, client, auth_headers, test_user):
        """Test creating credential with invalid type"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/compliance/staff-credentials/",
            headers=auth_headers,
            json={
                "user_id": str(test_user.id),
                "credential_type": "INVALID_TYPE",
                "credential_number": "INV123",
                "issue_date": "2024-01-15",
                "expiration_date": "2026-01-15",
                "is_verified": True
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
