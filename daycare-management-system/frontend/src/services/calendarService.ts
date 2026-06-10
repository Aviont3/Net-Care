import { apiRequest } from './api';

// ─── Types ────────────────────────────────────────────────────────
export interface CalendarMonthDay {
  date: string;
  attendance_count: number;
  meal_count: number;
  activity_count: number;
  incident_count: number;
  medication_count: number;
  report_count: number;
  status: 'normal' | 'attention' | 'incident';
}

export interface DayAttendance {
  child_name: string;
  check_in_time: string;
  check_out_time: string | null;
  is_late_pickup: boolean;
}

export interface DayActivity {
  child_name: string;
  activity_type: string;
  activity_name: string;
  time: string;
  mood: string | null;
  duration_minutes: number | null;
}

export interface DayIncident {
  child_name: string;
  incident_type: string;
  description: string;
  time: string;
  parent_notified: boolean;
}

export interface DayMedication {
  child_name: string;
  medication_name: string;
  dosage_given: string;
  time: string;
  administered_by: string;
}

export interface DayReport {
  child_name: string;
  id: string;
  generated_at: string;
}

export interface CalendarDayDetail {
  date: string;
  attendance: DayAttendance[];
  activities: DayActivity[];
  meals: DayActivity[];
  incidents: DayIncident[];
  medications: DayMedication[];
  reports: DayReport[];
  summary: {
    total_attendance: number;
    total_activities: number;
    total_meals: number;
    total_incidents: number;
    total_medications: number;
    total_reports: number;
  };
}

// ─── Service ──────────────────────────────────────────────────────
export const calendarService = {
  getMonth: (year: number, month: number) =>
    apiRequest<CalendarMonthDay[]>({
      method: 'GET',
      url: '/api/v1/calendar/month',
      params: { year, month },
    }),

  getDay: (date: string) =>
    apiRequest<CalendarDayDetail>({
      method: 'GET',
      url: '/api/v1/calendar/day',
      params: { date },
    }),

  getChildMonth: (childId: string, year: number, month: number) =>
    apiRequest<CalendarMonthDay[]>({
      method: 'GET',
      url: `/api/v1/calendar/child/${childId}/month`,
      params: { year, month },
    }),
};
