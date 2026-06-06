import { apiRequest } from './api';

export interface DashboardSummary {
  total_children: number;
  present_today: number;
  staff_on_duty: number;
  pending_alerts: number;
  attendance_percentage: number;
}

export const dashboardService = {
  getSummary: () =>
    apiRequest<DashboardSummary>({ method: 'GET', url: '/api/v1/dashboard/summary' }),
};
