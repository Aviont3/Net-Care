import api from './api';

export interface ImmunizationRecord {
  id: string;
  child_id: string;
  vaccine_name: string;
  administration_date: string;
  expiration_date: string | null;
  is_verified: boolean;
  provider_name?: string;
  notes?: string;
}

export interface StaffCredential {
  id: string;
  user_id: string;
  credential_type: string;
  credential_number?: string;
  issue_date: string;
  expiration_date: string | null;
  is_verified: boolean;
  is_expired: boolean;
}

export interface EnrollmentForm {
  id: string;
  child_id: string;
  enrollment_date: string;
  is_complete: boolean;
  parent_signed_at?: string;
  staff_signed_at?: string;
}

export interface ComplianceAlert {
  id: string;
  alert_type: string;
  entity_type: string;
  entity_id: string;
  description: string;
  due_date?: string;
  severity: string;
  is_resolved: boolean;
  resolved_at?: string;
}

export const complianceService = {
  async getImmunizations(params?: { child_id?: string; is_verified?: boolean }) {
    const r = await api.get<ImmunizationRecord[]>('/api/v1/compliance/immunizations/', { params });
    return r.data;
  },
  async verifyImmunization(id: string) {
    const r = await api.patch<ImmunizationRecord>(`/api/v1/compliance/immunizations/${id}/verify`);
    return r.data;
  },
  async getCredentials(params?: { is_expired?: boolean; is_verified?: boolean }) {
    const r = await api.get<StaffCredential[]>('/api/v1/compliance/staff-credentials/', { params });
    return r.data;
  },
  async verifyCredential(id: string) {
    const r = await api.patch<StaffCredential>(`/api/v1/compliance/staff-credentials/${id}/verify`);
    return r.data;
  },
  async getEnrollmentForms(params?: { is_complete?: boolean }) {
    const r = await api.get<EnrollmentForm[]>('/api/v1/compliance/enrollment-forms/', { params });
    return r.data;
  },
  async getAlerts(params?: { is_resolved?: boolean; severity?: string }) {
    const r = await api.get<ComplianceAlert[]>('/api/v1/compliance/alerts/', { params });
    return r.data;
  },
  async resolveAlert(id: string) {
    const r = await api.patch<ComplianceAlert>(`/api/v1/compliance/alerts/${id}/resolve`);
    return r.data;
  },
};
