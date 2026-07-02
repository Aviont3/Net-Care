import api from './api';

export interface Activity {
  id: string;
  child_id: string;
  activity_date: string;
  activity_time: string;
  activity_type: string;
  meal_type?: string;
  activity_name: string;
  description?: string;
  mood?: string;
  duration_minutes?: number;
  notes?: string;
  photo_url?: string;
  food_components?: Record<string, string | boolean | null>;
  cacfp_compliant?: boolean | null;
  compliance_notes?: string | null;
  logged_by: string;
  created_at: string;
}

export interface ActivityCreate {
  child_id: string;
  activity_type: string;
  meal_type?: string;
  activity_name: string;
  description?: string;
  mood?: string;
  duration_minutes?: number;
  notes?: string;
  food_components?: Record<string, string | boolean | null>;
}

export const activityService = {
  async getActivities(params?: { child_id?: string; activity_date?: string; activity_type?: string }) {
    const response = await api.get<Activity[]>('/api/v1/activities/', { params });
    return response.data;
  },
  async getTodayActivities(params?: { child_id?: string; activity_type?: string }) {
    const response = await api.get<Activity[]>('/api/v1/activities/today', { params });
    return response.data;
  },
  async createActivity(data: ActivityCreate) {
    const response = await api.post<Activity>('/api/v1/activities/', data);
    return response.data;
  },
  async uploadPhoto(activityId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<Activity>(`/api/v1/activities/${activityId}/photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
