import { apiRequest } from './api';

export interface DashboardSummary {
  total_children: number;
  present_today: number;
  staff_on_duty: number;
  pending_alerts: number;
  attendance_percentage: number;
}

export interface CalendarDay {
  date: string;
  attendance_count: number;
  activity_count: number;
  meal_count: number;
  incident_count: number;
}

export const dashboardService = {
  getSummary: () =>
    apiRequest<DashboardSummary>({ method: 'GET', url: '/api/v1/dashboard/summary' }),

  getCalendarSummary: (start_date: string, end_date: string) =>
    apiRequest<CalendarDay[]>({
      method: 'GET',
      url: '/api/v1/dashboard/calendar-summary',
      params: { start_date, end_date },
    }),
};
