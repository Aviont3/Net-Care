import api from './api';

export interface MedicationAuthorization {
  id: string;
  child_id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  administration_instructions: string;
  start_date: string;
  end_date?: string;
  prescribing_doctor?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MedicationAuthorizationCreate {
  child_id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  administration_instructions: string;
  start_date: string;
  end_date?: string;
  prescribing_doctor?: string;
}

export interface MedicationLog {
  id: string;
  child_id: string;
  authorization_id: string;
  administration_date: string;
  administration_time: string;
  dosage_given: string;
  administered_by: string;
  notes?: string;
  parent_notified: boolean;
  created_at: string;
}

export interface MedicationLogCreate {
  child_id: string;
  authorization_id: string;
  administration_date: string;
  administration_time: string;
  dosage_given: string;
  notes?: string;
  parent_notified?: boolean;
}

export const medicationService = {
  async getAuthorizations(params?: { child_id?: string; is_active?: boolean }) {
    const response = await api.get<MedicationAuthorization[]>('/api/v1/medications/authorizations/', { params });
    return response.data;
  },
  async createAuthorization(data: MedicationAuthorizationCreate) {
    const response = await api.post<MedicationAuthorization>('/api/v1/medications/authorizations/', data);
    return response.data;
  },
  async getLogs(params?: { child_id?: string; administration_date?: string }) {
    const response = await api.get<MedicationLog[]>('/api/v1/medications/logs/', { params });
    return response.data;
  },
  async createLog(data: MedicationLogCreate) {
    const response = await api.post<MedicationLog>('/api/v1/medications/logs/', data);
    return response.data;
  },
};
