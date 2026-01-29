import api from './api';
import type { Parent } from '@/types';

export interface ParentCreate {
  first_name: string;
  last_name: string;
  email?: string;
  phone_primary: string;
  phone_secondary?: string;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  address_zip?: string;
}

export interface ParentUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_primary?: string;
  phone_secondary?: string;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  address_zip?: string;
}

export const parentsService = {
  // Get all parents with pagination and search
  async getParents(params?: {
    page?: number;
    page_size?: number;
    search?: string;
  }): Promise<Parent[]> {
    const response = await api.get<Parent[]>('/api/v1/parents/', { params });
    return response.data;
  },

  // Get a specific parent by ID
  async getParent(parentId: string): Promise<Parent> {
    const response = await api.get<Parent>(`/api/v1/parents/${parentId}`);
    return response.data;
  },

  // Create a new parent
  async createParent(data: ParentCreate): Promise<Parent> {
    const response = await api.post<Parent>('/api/v1/parents/', data);
    return response.data;
  },

  // Update a parent
  async updateParent(parentId: string, data: ParentUpdate): Promise<Parent> {
    const response = await api.put<Parent>(`/api/v1/parents/${parentId}`, data);
    return response.data;
  },

  // Delete a parent
  async deleteParent(parentId: string): Promise<void> {
    await api.delete(`/api/v1/parents/${parentId}`);
  },
};
