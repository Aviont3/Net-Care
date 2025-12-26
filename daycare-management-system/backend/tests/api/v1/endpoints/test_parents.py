# Parents Endpoint Tests
# ============================================

import pytest
from fastapi import status
from app.core.config import settings


class TestParentsEndpoints:
    """Test parents management endpoints"""

    def test_create_parent(self, client, auth_headers):
        """Test creating a new parent"""
        response = client.post(
            f"{settings.API_V1_PREFIX}/parents/",
            headers=auth_headers,
            json={
                "first_name": "Michael",
                "last_name": "Johnson",
                "email": "michael.j@example.com",
                "phone_primary": "555-1234",
                "address_street": "456 Oak Ave",
                "address_city": "Chicago",
                "address_state": "IL",
                "address_zip": "60602"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["first_name"] == "Michael"
        assert data["last_name"] == "Johnson"
        assert data["email"] == "michael.j@example.com"
        assert "id" in data

    def test_get_all_parents(self, client, auth_headers, test_parent):
        """Test getting all parents"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/parents/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(parent["id"] == str(test_parent.id) for parent in data)

    def test_get_parent_by_id(self, client, auth_headers, test_parent):
        """Test getting a specific parent by ID"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/parents/{test_parent.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_parent.id)
        assert data["first_name"] == test_parent.first_name

    def test_update_parent(self, client, auth_headers, test_parent):
        """Test updating a parent's information"""
        response = client.put(
            f"{settings.API_V1_PREFIX}/parents/{test_parent.id}",
            headers=auth_headers,
            json={
                "phone_primary": "555-9999",
                "phone_secondary": "555-8888"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone_primary"] == "555-9999"
        assert data["phone_secondary"] == "555-8888"

    def test_search_parents_by_name(self, client, auth_headers, test_parent):
        """Test searching parents by name"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/parents/search?query=Jane",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert any("Jane" in parent["first_name"] for parent in data)

    def test_search_parents_by_email(self, client, auth_headers, test_parent):
        """Test searching parents by email"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/parents/search?query=jane.johnson",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0

    def test_get_parent_children(self, client, auth_headers, test_child_with_parent, test_parent):
        """Test getting all children for a parent"""
        response = client.get(
            f"{settings.API_V1_PREFIX}/parents/{test_parent.id}/children",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0

    def test_delete_parent_admin_only(self, client, auth_headers, test_parent):
        """Test deleting parent requires admin role"""
        response = client.delete(
            f"{settings.API_V1_PREFIX}/parents/{test_parent.id}",
            headers=auth_headers
        )
        # Should fail for non-admin users
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_parent_as_admin(self, client, admin_headers, test_parent):
        """Test admin can delete parent"""
        response = client.delete(
            f"{settings.API_V1_PREFIX}/parents/{test_parent.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
