import api from './api';
import type { Attendance } from '@/types';

export const attendanceService = {
  // Get today's attendance records
  async getTodayAttendance(): Promise<Attendance[]> {
    const response = await api.get<Attendance[]>('/api/v1/attendance/today');
    return response.data;
  },

  // Get currently checked in children (not yet checked out)
  async getCurrentlyCheckedIn(): Promise<Attendance[]> {
    const response = await api.get<Attendance[]>('/api/v1/attendance/today/checked-in');
    return response.data;
  },

  // Check in a child
  async checkIn(data: {
    child_id: string;
    check_in_time: string;
    check_in_by_name: string;
    check_in_signature_url?: string;
    notes?: string;
  }): Promise<Attendance> {
    const response = await api.post<Attendance>('/api/v1/attendance/check-in', data);
    return response.data;
  },

  // Check out a child
  async checkOut(
    attendanceId: string,
    data: {
      check_out_time: string;
      check_out_by_name: string;
      check_out_signature_url?: string;
      notes?: string;
    }
  ): Promise<Attendance> {
    const response = await api.patch<Attendance>(
      `/api/v1/attendance/${attendanceId}/check-out`,
      data
    );
    return response.data;
  },

  // Get attendance records with filters
  async getAttendance(params?: {
    attendance_date?: string;
    child_id?: string;
    checked_out?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<Attendance[]> {
    const response = await api.get<Attendance[]>('/api/v1/attendance/', { params });
    return response.data;
  },

  // Get child attendance history
  async getChildAttendanceHistory(
    childId: string,
    params?: {
      start_date?: string;
      end_date?: string;
      page?: number;
      page_size?: number;
    }
  ): Promise<Attendance[]> {
    const response = await api.get<Attendance[]>(
      `/api/v1/attendance/child/${childId}`,
      { params }
    );
    return response.data;
  },
};
