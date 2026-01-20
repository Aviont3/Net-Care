import api from './api';
import type {
  Child,
  ChildCreate,
  ChildUpdate,
  ChildListResponse,
  EmergencyContact,
  EmergencyContactCreate,
  AuthorizedPickup,
  AuthorizedPickupCreate,
  Parent
} from '@/types';

export const childrenService = {
  // Get paginated list of children
  async getChildren(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    is_active?: boolean;
  }): Promise<ChildListResponse> {
    const response = await api.get<ChildListResponse>('/api/v1/children/', { params });
    return response.data;
  },

  // Get single child by ID
  async getChild(childId: string): Promise<Child> {
    const response = await api.get<Child>(`/api/v1/children/${childId}`);
    return response.data;
  },

  // Create new child
  async createChild(childData: ChildCreate): Promise<Child> {
    const response = await api.post<Child>('/api/v1/children/', childData);
    return response.data;
  },

  // Update child information
  async updateChild(childId: string, childData: ChildUpdate): Promise<Child> {
    const response = await api.put<Child>(`/api/v1/children/${childId}`, childData);
    return response.data;
  },

  // Deactivate child (soft delete)
  async deactivateChild(childId: string): Promise<Child> {
    const response = await api.patch<Child>(`/api/v1/children/${childId}/deactivate`);
    return response.data;
  },

  // Activate child
  async activateChild(childId: string): Promise<Child> {
    const response = await api.patch<Child>(`/api/v1/children/${childId}/activate`);
    return response.data;
  },

  // Delete child (hard delete - admin only)
  async deleteChild(childId: string): Promise<void> {
    await api.delete(`/api/v1/children/${childId}`);
  },

  // Get child's parents
  async getChildParents(childId: string): Promise<Parent[]> {
    const response = await api.get<Parent[]>(`/api/v1/children/${childId}/parents`);
    return response.data;
  },

  // Get child's emergency contacts
  async getEmergencyContacts(childId: string): Promise<EmergencyContact[]> {
    const response = await api.get<EmergencyContact[]>(`/api/v1/children/${childId}/emergency-contacts`);
    return response.data;
  },

  // Create emergency contact
  async createEmergencyContact(contactData: EmergencyContactCreate): Promise<EmergencyContact> {
    const response = await api.post<EmergencyContact>(
      `/api/v1/children/${contactData.child_id}/emergency-contacts`,
      contactData
    );
    return response.data;
  },

  // Get authorized pickup persons
  async getAuthorizedPickups(childId: string): Promise<AuthorizedPickup[]> {
    const response = await api.get<AuthorizedPickup[]>(`/api/v1/children/${childId}/authorized-pickups`);
    return response.data;
  },

  // Create authorized pickup person
  async createAuthorizedPickup(pickupData: AuthorizedPickupCreate): Promise<AuthorizedPickup> {
    const response = await api.post<AuthorizedPickup>(
      `/api/v1/children/${pickupData.child_id}/authorized-pickups`,
      pickupData
    );
    return response.data;
  },
};
