import React, { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { childrenService } from '@/services/childrenService';
import { attendanceService } from '@/services/attendanceService';
import type { Child, Attendance } from '@/types';

interface WeekDay {
  date: Date;
  dateString: string;
  dayName: string;
  dayNumber: number;
}

interface ChildAttendance extends Child {
  weekAttendance: Map<string, Attendance | null>;
}

export const AttendanceCalendar: React.FC = () => {
  const [children, setChildren] = useState<ChildAttendance[]>([]);
  const [weekDays, setWeekDays] = useState<WeekDay[]>([]);
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(getStartOfWeek(new Date()));
  const [loading, setLoading] = useState(true);

  // Get start of week (Monday)
  function getStartOfWeek(date: Date): Date {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
    return new Date(d.setDate(diff));
  }

  // Format date to YYYY-MM-DD
  function formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  // Generate week days
  function generateWeekDays(startDate: Date): WeekDay[] {
    const days: WeekDay[] = [];
    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    for (let i = 0; i < 5; i++) { // Only show weekdays (Mon-Fri)
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      days.push({
        date,
        dateString: formatDate(date),
        dayName: dayNames[i],
        dayNumber: date.getDate(),
      });
    }
    return days;
  }

  // Fetch attendance data for the week
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Generate week days
        const days = generateWeekDays(currentWeekStart);
        setWeekDays(days);

        // Fetch children
        const childrenResponse = await childrenService.getChildren({ is_active: true });

        // Fetch attendance for the week
        const startDate = days[0].dateString;
        const endDate = days[days.length - 1].dateString;

        // Get all attendance records (we'll need to make multiple calls or create a batch endpoint)
        const attendancePromises = childrenResponse.children.map(child =>
          attendanceService.getChildAttendanceHistory(child.id, {
            start_date: startDate,
            end_date: endDate,
            page_size: 100,
          })
        );

        const allAttendanceRecords = await Promise.all(attendancePromises);

        // Map children with their week attendance
        const childrenWithAttendance: ChildAttendance[] = childrenResponse.children.map((child, index) => {
          const weekAttendance = new Map<string, Attendance | null>();

          // Initialize all days as null (not attended)
          days.forEach(day => {
            weekAttendance.set(day.dateString, null);
          });

          // Fill in actual attendance records
          allAttendanceRecords[index].forEach(record => {
            weekAttendance.set(record.attendance_date, record);
          });

          return {
            ...child,
            weekAttendance,
          };
        });

        setChildren(childrenWithAttendance);
      } catch (error) {
        console.error('Error fetching attendance data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentWeekStart]);

  // Navigate to previous week
  const previousWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(currentWeekStart.getDate() - 7);
    setCurrentWeekStart(newStart);
  };

  // Navigate to next week
  const nextWeek = () => {
    const newStart = new Date(currentWeekStart);
    newStart.setDate(currentWeekStart.getDate() + 7);
    setCurrentWeekStart(newStart);
  };

  // Go to current week
  const goToCurrentWeek = () => {
    setCurrentWeekStart(getStartOfWeek(new Date()));
  };

  // Get attendance status color
  const getStatusColor = (attendance: Attendance | null): string => {
    if (!attendance) return 'bg-gray-100';
    if (attendance.check_out_time) return 'bg-green-500';
    return 'bg-blue-500'; // Checked in but not checked out
  };

  // Get attendance status text
  const getStatusText = (attendance: Attendance | null): string => {
    if (!attendance) return 'Absent';
    if (attendance.check_out_time) return 'Present';
    return 'In Progress';
  };

  // Format month and year for display
  const getWeekRangeText = (): string => {
    const startDate = weekDays[0]?.date;
    const endDate = weekDays[weekDays.length - 1]?.date;

    if (!startDate || !endDate) return '';

    const options: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric', year: 'numeric' };
    const start = startDate.toLocaleDateString('en-US', options);
    const end = endDate.toLocaleDateString('en-US', options);

    return `${start} - ${end}`;
  };

  return (
    <AdminLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Weekly Attendance</h1>
        <p className="mt-2 text-gray-600">Track children's attendance throughout the week</p>
      </div>

      {/* Week Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center justify-between">
          <button
            onClick={previousWeek}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <div className="text-center">
            <h2 className="text-lg font-semibold text-gray-900">{getWeekRangeText()}</h2>
            <button
              onClick={goToCurrentWeek}
              className="mt-1 text-sm text-primary-600 hover:text-primary-700"
            >
              Go to Current Week
            </button>
          </div>

          <button
            onClick={nextWeek}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Attendance Grid */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="sticky left-0 z-10 bg-gray-50 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Child Name
                  </th>
                  {weekDays.map(day => (
                    <th key={day.dateString} className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <div>{day.dayName}</div>
                      <div className="text-lg font-semibold text-gray-900">{day.dayNumber}</div>
                    </th>
                  ))}
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {children.map(child => {
                  const totalPresent = weekDays.filter(day => {
                    const attendance = child.weekAttendance.get(day.dateString);
                    return attendance && attendance.check_out_time;
                  }).length;

                  return (
                    <tr key={child.id} className="hover:bg-gray-50">
                      <td className="sticky left-0 z-10 bg-white px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-primary-500 rounded-full flex items-center justify-center">
                            <span className="text-white font-semibold text-sm">
                              {child.first_name[0]}{child.last_name[0]}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {child.first_name} {child.last_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      {weekDays.map(day => {
                        const attendance = child.weekAttendance.get(day.dateString);
                        return (
                          <td key={day.dateString} className="px-6 py-4 whitespace-nowrap text-center">
                            <div className="flex flex-col items-center">
                              <div
                                className={`w-12 h-12 rounded-full flex items-center justify-center ${getStatusColor(attendance)}`}
                                title={getStatusText(attendance)}
                              >
                                {attendance ? (
                                  attendance.check_out_time ? (
                                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                  ) : (
                                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                  )
                                ) : (
                                  <span className="text-gray-400 text-xs">-</span>
                                )}
                              </div>
                              {attendance && (
                                <div className="text-xs text-gray-500 mt-1">
                                  {attendance.check_in_time.substring(0, 5)}
                                </div>
                              )}
                            </div>
                          </td>
                        );
                      })}
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-lg font-semibold text-gray-900">
                          {totalPresent}/{weekDays.length}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {children.length === 0 && (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No children found</h3>
                <p className="mt-1 text-sm text-gray-500">Start by adding children to the system.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Legend</h3>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center mr-2">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span className="text-sm text-gray-700">Present (Checked In & Out)</span>
          </div>
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center mr-2">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-sm text-gray-700">Currently Checked In</span>
          </div>
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mr-2">
              <span className="text-gray-400 text-xs">-</span>
            </div>
            <span className="text-sm text-gray-700">Absent</span>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};
