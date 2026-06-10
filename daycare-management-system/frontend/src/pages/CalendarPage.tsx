import React, { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { calendarService } from '@/services/calendarService';
import type { CalendarMonthDay, CalendarDayDetail } from '@/services/calendarService';

// ─── Helpers ──────────────────────────────────────────────────────
function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number): number {
  // 0=Sun, 1=Mon ... 6=Sat — adjust so Mon=0
  const day = new Date(year, month - 1, 1).getDay();
  return day === 0 ? 6 : day - 1;
}

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const DAY_HEADERS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const STATUS_COLORS: Record<string, string> = {
  normal: 'bg-emerald-500',
  attention: 'bg-amber-500',
  incident: 'bg-red-500',
};

// ─── Component ────────────────────────────────────────────────────
export const CalendarPage: React.FC = () => {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [monthData, setMonthData] = useState<CalendarMonthDay[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [dayDetail, setDayDetail] = useState<CalendarDayDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [dayLoading, setDayLoading] = useState(false);
  const [view, setView] = useState<'month' | 'week'>('month');

  // Fetch month data
  useEffect(() => {
    setLoading(true);
    calendarService.getMonth(year, month)
      .then(data => setMonthData(data))
      .catch(() => setMonthData([]))
      .finally(() => setLoading(false));
  }, [year, month]);

  // Fetch day detail when selected
  useEffect(() => {
    if (!selectedDate) {
      setDayDetail(null);
      return;
    }
    setDayLoading(true);
    calendarService.getDay(selectedDate)
      .then(data => setDayDetail(data))
      .catch(() => setDayDetail(null))
      .finally(() => setDayLoading(false));
  }, [selectedDate]);

  // Navigation
  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(y => y - 1); }
    else setMonth(m => m - 1);
    setSelectedDate(null);
  };
  const nextMonth = () => {
    if (month === 12) { setMonth(1); setYear(y => y + 1); }
    else setMonth(m => m + 1);
    setSelectedDate(null);
  };

  // Build calendar grid
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);
  const dayMap = new Map(monthData.map(d => [d.date, d]));

  const calendarCells: (CalendarMonthDay | null)[] = [];
  // Padding for days before the 1st
  for (let i = 0; i < firstDay; i++) calendarCells.push(null);
  // Actual days
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    calendarCells.push(dayMap.get(dateStr) || { date: dateStr, attendance_count: 0, meal_count: 0, activity_count: 0, incident_count: 0, medication_count: 0, report_count: 0, status: 'normal' });
  }

  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

  return (
    <AdminLayout>
      <div className="flex flex-col lg:flex-row gap-6 p-6">
        {/* Calendar Grid */}
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">📅 Unified Calendar</h1>
            <div className="flex items-center gap-2">
              <button onClick={() => setView('month')} className={`px-3 py-1.5 rounded-lg text-sm font-medium ${view === 'month' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>Month</button>
              <button onClick={() => setView('week')} className={`px-3 py-1.5 rounded-lg text-sm font-medium ${view === 'week' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>Week</button>
            </div>
          </div>

          {/* Month Navigation */}
          <div className="flex items-center justify-between mb-4 bg-white rounded-xl shadow-sm p-4">
            <button onClick={prevMonth} className="p-2 hover:bg-gray-100 rounded-lg transition">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            </button>
            <h2 className="text-lg font-semibold text-gray-800">{MONTH_NAMES[month - 1]} {year}</h2>
            <button onClick={nextMonth} className="p-2 hover:bg-gray-100 rounded-lg transition">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            {/* Day Headers */}
            <div className="grid grid-cols-7 border-b">
              {DAY_HEADERS.map(d => (
                <div key={d} className="py-3 text-center text-xs font-semibold text-gray-500 uppercase">{d}</div>
              ))}
            </div>

            {/* Day Cells */}
            {loading ? (
              <div className="p-12 text-center text-gray-400">Loading calendar...</div>
            ) : (
              <div className="grid grid-cols-7">
                {calendarCells.map((cell, idx) => {
                  if (!cell) return <div key={idx} className="h-24 border-b border-r bg-gray-50" />;

                  const dayNum = parseInt(cell.date.split('-')[2]);
                  const isToday = cell.date === todayStr;
                  const isSelected = cell.date === selectedDate;
                  const hasData = cell.attendance_count > 0 || cell.activity_count > 0 || cell.incident_count > 0;

                  return (
                    <button
                      key={cell.date}
                      onClick={() => setSelectedDate(cell.date === selectedDate ? null : cell.date)}
                      className={`h-24 border-b border-r p-2 text-left hover:bg-indigo-50 transition relative ${isSelected ? 'bg-indigo-50 ring-2 ring-indigo-500 ring-inset' : ''}`}
                    >
                      <span className={`text-sm font-medium ${isToday ? 'bg-indigo-600 text-white w-7 h-7 rounded-full inline-flex items-center justify-center' : 'text-gray-700'}`}>
                        {dayNum}
                      </span>

                      {hasData && (
                        <div className="mt-1 space-y-0.5">
                          {cell.attendance_count > 0 && (
                            <div className="text-[10px] text-gray-500 flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block" />
                              {cell.attendance_count} present
                            </div>
                          )}
                          {cell.meal_count > 0 && (
                            <div className="text-[10px] text-gray-500 flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
                              {cell.meal_count} meals
                            </div>
                          )}
                          {cell.incident_count > 0 && (
                            <div className="text-[10px] text-red-600 flex items-center gap-1 font-medium">
                              <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" />
                              {cell.incident_count} incident{cell.incident_count > 1 ? 's' : ''}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Status dot */}
                      <span className={`absolute top-2 right-2 w-2 h-2 rounded-full ${STATUS_COLORS[cell.status] || ''} ${cell.status === 'normal' && !hasData ? 'opacity-0' : ''}`} />
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" /> Attendance</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Meals</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Incidents</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500" /> Medications</span>
          </div>
        </div>

        {/* Day Detail Panel */}
        <div className="w-full lg:w-96 shrink-0">
          {selectedDate && dayLoading && (
            <div className="bg-white rounded-xl shadow-sm p-6 text-center text-gray-400">Loading day details...</div>
          )}

          {selectedDate && dayDetail && !dayLoading && (
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="bg-indigo-600 px-5 py-4">
                <h3 className="text-white font-semibold text-lg">
                  {new Date(selectedDate + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                </h3>
                <div className="flex gap-3 mt-2 text-indigo-200 text-sm">
                  <span>{dayDetail.summary.total_attendance} checked in</span>
                  <span>•</span>
                  <span>{dayDetail.summary.total_activities} activities</span>
                </div>
              </div>

              <div className="divide-y max-h-[600px] overflow-y-auto">
                {/* Attendance */}
                {dayDetail.attendance.length > 0 && (
                  <div className="p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-blue-500" /> Attendance ({dayDetail.summary.total_attendance})
                    </h4>
                    <div className="space-y-1.5">
                      {dayDetail.attendance.map((a, i) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span className="text-gray-700">{a.child_name}</span>
                          <span className="text-gray-500 text-xs">
                            {a.check_in_time}{a.check_out_time ? ` → ${a.check_out_time}` : ' (still here)'}
                            {a.is_late_pickup && <span className="ml-1 text-red-500">⚠️ Late</span>}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Activities */}
                {dayDetail.activities.length > 0 && (
                  <div className="p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" /> Activities ({dayDetail.summary.total_activities})
                    </h4>
                    <div className="space-y-1.5">
                      {dayDetail.activities.slice(0, 10).map((a, i) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span className="text-gray-700">{a.child_name} — <span className="text-gray-500">{a.activity_name}</span></span>
                          <span className="text-xs text-gray-400">{a.mood && `${a.mood} `}{a.activity_type}</span>
                        </div>
                      ))}
                      {dayDetail.activities.length > 10 && (
                        <p className="text-xs text-gray-400">+ {dayDetail.activities.length - 10} more</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Meals */}
                {dayDetail.meals.length > 0 && (
                  <div className="p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-green-500" /> Meals ({dayDetail.summary.total_meals})
                    </h4>
                    <div className="space-y-1.5">
                      {dayDetail.meals.map((m, i) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span className="text-gray-700">{m.child_name} — {m.activity_name}</span>
                          <span className="text-xs text-gray-400">{m.time}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Incidents */}
                {dayDetail.incidents.length > 0 && (
                  <div className="p-4 bg-red-50">
                    <h4 className="text-sm font-semibold text-red-700 mb-2 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-red-500" /> Incidents ({dayDetail.summary.total_incidents})
                    </h4>
                    <div className="space-y-2">
                      {dayDetail.incidents.map((inc, i) => (
                        <div key={i} className="text-sm">
                          <div className="flex justify-between">
                            <span className="font-medium text-red-800">{inc.child_name}</span>
                            <span className="text-xs text-red-600 uppercase">{inc.incident_type}</span>
                          </div>
                          <p className="text-red-700 text-xs mt-0.5 line-clamp-2">{inc.description}</p>
                          <span className="text-xs text-red-500">{inc.parent_notified ? '✓ Parent notified' : '⚠ Parent NOT notified'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Medications */}
                {dayDetail.medications.length > 0 && (
                  <div className="p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-purple-500" /> Medications ({dayDetail.summary.total_medications})
                    </h4>
                    <div className="space-y-1.5">
                      {dayDetail.medications.map((med, i) => (
                        <div key={i} className="text-sm">
                          <span className="text-gray-700">{med.child_name}</span>
                          <span className="text-gray-500 text-xs ml-2">{med.medication_name} ({med.dosage_given}) at {med.time}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Empty state */}
                {dayDetail.summary.total_attendance === 0 && dayDetail.summary.total_activities === 0 && (
                  <div className="p-8 text-center text-gray-400">
                    <p className="text-lg">No data for this day</p>
                    <p className="text-sm mt-1">Activities will show up here once staff logs them</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {!selectedDate && (
            <div className="bg-white rounded-xl shadow-sm p-6 text-center text-gray-400">
              <p className="text-lg">👈 Click a day to see details</p>
              <p className="text-sm mt-2">View attendance, activities, meals, incidents, and medications for any day</p>
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};
