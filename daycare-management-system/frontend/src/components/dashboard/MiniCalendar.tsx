import React, { useState, useEffect } from 'react';
import { dashboardService, type CalendarDay } from '@/services/dashboardService';

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

function monthRange(year: number, month: number) {
  const pad = (n: number) => String(n).padStart(2, '0');
  const last = new Date(year, month + 1, 0).getDate();
  return {
    start: `${year}-${pad(month + 1)}-01`,
    end:   `${year}-${pad(month + 1)}-${pad(last)}`,
  };
}

export const MiniCalendar: React.FC = () => {
  const today = new Date();
  const [year, setYear]   = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth());
  const [data, setData]   = useState<Record<string, CalendarDay>>({});
  const [selected, setSelected] = useState<CalendarDay | null>(null);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    setLoading(true);
    const { start, end } = monthRange(year, month);
    dashboardService.getCalendarSummary(start, end)
      .then(days => {
        const map: Record<string, CalendarDay> = {};
        days.forEach(d => { map[d.date] = d; });
        setData(map);
        setSelected(null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [year, month]);

  const prevMonth = () => { if (month === 0) { setYear(y => y - 1); setMonth(11); } else setMonth(m => m - 1); };
  const nextMonth = () => { if (month === 11) { setYear(y => y + 1); setMonth(0); } else setMonth(m => m + 1); };

  // Build calendar grid
  const firstDow = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const pad = (n: number) => String(n).padStart(2, '0');
  const todayStr = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`;

  const cells: (number | null)[] = [
    ...Array(firstDow).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];
  // pad to full weeks
  while (cells.length % 7 !== 0) cells.push(null);

  const dotColor = (d: CalendarDay) => {
    if (d.incident_count > 0) return 'bg-red-400';
    if (d.attendance_count > 0) return 'bg-green-400';
    return 'bg-gray-300';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900">Calendar</h2>
        <div className="flex items-center gap-2">
          <button onClick={prevMonth} className="p-1 rounded hover:bg-gray-100 text-gray-500">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="text-sm font-medium text-gray-700 w-32 text-center">{MONTHS[month]} {year}</span>
          <button onClick={nextMonth} className="p-1 rounded hover:bg-gray-100 text-gray-500">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-4">
        {/* Day-of-week headers */}
        <div className="grid grid-cols-7 mb-1">
          {DAYS.map(d => (
            <div key={d} className="text-center text-xs font-medium text-gray-400 py-1">{d}</div>
          ))}
        </div>

        {/* Grid */}
        {loading ? (
          <div className="h-40 flex items-center justify-center text-gray-400 text-sm">Loading…</div>
        ) : (
          <div className="grid grid-cols-7 gap-y-1">
            {cells.map((day, i) => {
              if (!day) return <div key={i} />;
              const dateStr = `${year}-${pad(month + 1)}-${pad(day)}`;
              const dayData = data[dateStr];
              const isToday = dateStr === todayStr;
              const isSelected = selected?.date === dateStr;

              return (
                <button
                  key={dateStr}
                  onClick={() => setSelected(isSelected ? null : (dayData ?? { date: dateStr, attendance_count: 0, activity_count: 0, meal_count: 0, incident_count: 0 }))}
                  className={`flex flex-col items-center py-1.5 rounded-lg transition-colors ${isSelected ? 'bg-primary-100' : 'hover:bg-gray-50'}`}
                >
                  <span className={`text-xs font-medium w-6 h-6 flex items-center justify-center rounded-full ${isToday ? 'bg-primary-600 text-white' : 'text-gray-700'}`}>
                    {day}
                  </span>
                  {dayData && (
                    <span className={`mt-0.5 w-1.5 h-1.5 rounded-full ${dotColor(dayData)}`} />
                  )}
                </button>
              );
            })}
          </div>
        )}

        {/* Day Detail Panel */}
        {selected && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wide">
              {new Date(selected.date + 'T12:00:00').toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })}
            </p>
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: 'Attendance',  value: selected.attendance_count, color: 'text-green-600' },
                { label: 'Activities',  value: selected.activity_count,   color: 'text-blue-600'  },
                { label: 'Meals',       value: selected.meal_count,       color: 'text-orange-600'},
                { label: 'Incidents',   value: selected.incident_count,   color: selected.incident_count > 0 ? 'text-red-600' : 'text-gray-400' },
              ].map(item => (
                <div key={item.label} className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg">
                  <span className="text-xs text-gray-600">{item.label}</span>
                  <span className={`text-sm font-bold ${item.color}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="mt-3 pt-3 border-t border-gray-100 flex gap-4 justify-end">
          {[['bg-green-400','Active day'],['bg-red-400','Incident'],['bg-gray-300','No data']].map(([cls, label]) => (
            <div key={label} className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${cls}`} />
              <span className="text-xs text-gray-400">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
