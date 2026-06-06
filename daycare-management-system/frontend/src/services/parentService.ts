import api from './api';

export interface ParentChild {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  photo_url?: string;
  today_mood?: string;
  today_checked_in: boolean;
  today_checked_out: boolean;
}

export interface ChildReport {
  id: string;
  report_date: string;
  ai_generated_summary?: string;
  overall_mood?: string;
  custom_notes?: string;
  activities_summary?: Record<string, unknown>;
}

export interface ChildAttendanceRecord {
  id: string;
  attendance_date: string;
  check_in_time?: string;
  check_out_time?: string;
}

export const parentService = {
  async getMyChildren() {
    const r = await api.get<ParentChild[]>('/api/v1/parent/children');
    return r.data;
  },
  async getChildReports(childId: string) {
    const r = await api.get<ChildReport[]>(`/api/v1/parent/children/${childId}/reports`);
    return r.data;
  },
  async getChildAttendance(childId: string) {
    const r = await api.get<ChildAttendanceRecord[]>(`/api/v1/parent/children/${childId}/attendance`);
    return r.data;
  },
};
