import api from './api';

export interface IncidentReport {
  id: string;
  child_id: string;
  incident_date: string;
  incident_time: string;
  incident_type: string;
  description: string;
  circumstances: string;
  injury_description?: string;
  body_part_affected?: string;
  action_taken: string;
  witnesses?: string;
  parent_notified: boolean;
  parent_notified_at?: string;
  parent_notification_method?: string;
  dcfs_notification_required: boolean;
  dcfs_notified_at?: string;
  reported_by: string;
  created_at: string;
}

export interface IncidentReportCreate {
  child_id: string;
  incident_date: string;
  incident_time: string;
  incident_type: string;
  description: string;
  circumstances: string;
  injury_description?: string;
  body_part_affected?: string;
  action_taken: string;
  witnesses?: string;
  parent_notified?: boolean;
  dcfs_notification_required?: boolean;
}

export const incidentService = {
  async getIncidents(params?: { child_id?: string; incident_type?: string; start_date?: string; end_date?: string }) {
    const response = await api.get<IncidentReport[]>('/api/v1/incidents/', { params });
    return response.data;
  },
  async createIncident(data: IncidentReportCreate) {
    const response = await api.post<IncidentReport>('/api/v1/incidents/', data);
    return response.data;
  },
  async markParentNotified(id: string, notification_method: string) {
    const response = await api.patch<IncidentReport>(`/api/v1/incidents/${id}/notify-parent`, null, {
      params: { notification_method },
    });
    return response.data;
  },
};
