# Children Endpoint Tests
# ============================================

import pytest
from datetime import date
from fastapi import status
from app.core.config import settings


class TestChildrenEndpoints:
    """Test children management endpoints"""

    def test_create_child(self, client, auth_headers):
        """Test creating a new child"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/children/",
            headers=auth_headers,
            json={
                "first_name": "Lucas",
                "last_name": "Smith",
                "date_of_birth": "2021-03-20",
                "gender": "male",
                "enrollment_date": "2024-01-15"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["first_name"] == "Lucas"
        assert data["last_name"] == "Smith"
        assert data["gender"] == "male"
        assert data["is_active"] is True
        assert "id" in data

    def test_get_all_children(self, client, auth_headers, test_child):
        """Test getting all children"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/children/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(child["id"] == str(test_child.id) for child in data)

    def test_get_active_children_only(self, client, auth_headers, test_child, db):
        """Test getting only active children"""
        from app.models.child import Child

        # Create inactive child
        inactive_child = Child(
            first_name="Inactive",
            last_name="Child",
            date_of_birth=date(2020, 1, 1),
            gender="female",
            enrollment_date=date.today(),
            is_active=False
        )
        db.add(inactive_child)
        db.commit()

        response = client.get(
            f"{settings.API_V1_PREFIX}/children/?is_active=true",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(child["is_active"] is True for child in data)

    def test_get_child_by_id(self, client, auth_headers, test_child):
        """Test getting a specific child by ID"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/children/{test_child.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_child.id)
        assert data["first_name"] == test_child.first_name

    def test_update_child(self, client, auth_headers, test_child):
        """Test updating a child's information"""
        response = client.put(
            f"{settings.API_V1_PREFIX}/children/{test_child.id}",
            headers=auth_headers,
            json={
                "first_name": "Emma Updated",
                "allergies": "Peanuts, dairy"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Emma Updated"
        assert data["allergies"] == "Peanuts, dairy"

    def test_deactivate_child(self, client, auth_headers, test_child):
        """Test deactivating a child"""
        response = client.patch(
            f"{settings.API_V1_PREFIX}/children/{test_child.id}/deactivate",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False

    def test_activate_child(self, client, auth_headers, test_child, db):
        """Test activating a deactivated child"""
        test_child.is_active = False
        db.commit()

        response = client.patch(
            f"{settings.API_V1_PREFIX}/children/{test_child.id}/activate",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is True

    def test_get_nonexistent_child(self, client, auth_headers):
        """Test getting a child that doesn't exist"""
        from uuid import uuid4
        fake_id = uuid4()

        response = client.get(
            f"{settings.API_V1_PREFIX}/children/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_child_unauthenticated(self, client):
        """Test creating child without authentication fails"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/children/",
            json={
                "first_name": "Test",
                "last_name": "Child",
                "date_of_birth": "2020-01-01",
                "gender": "male",
                "enrollment_date": "2024-01-01"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestChildParentRelationships:
    """Test child-parent relationship endpoints"""

    def test_link_parent_to_child(self, client, auth_headers, test_child, test_parent):
        """Test linking a parent to a child"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/children/{test_child.id}/parents",
            headers=auth_headers,
            json={
                "parent_id": str(test_parent.id),
                "relationship_type": "mother",
                "is_primary_contact": True,
                "is_authorized_pickup": True,
                "has_legal_custody": True
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["relationship_type"] == "mother"
        assert data["is_primary_contact"] is True

    def test_get_child_parents(self, client, auth_headers, test_child_with_parent):
        """Test getting all parents for a child"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/children/{test_child_with_parent.id}/parents",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
