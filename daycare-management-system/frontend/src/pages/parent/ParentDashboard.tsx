import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  parentService,
  type ParentChild,
  type ChildReport,
  type ChildAttendanceRecord,
} from '@/services/parentService';

const MOOD_EMOJI: Record<string, string> = {
  happy: '😊', energetic: '⚡', neutral: '😐', tired: '😴', sad: '😢', cranky: '😤',
};

function AttendanceBadge({ child }: { child: ParentChild }) {
  if (child.today_checked_out) return <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">Checked out</span>;
  if (child.today_checked_in) return <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">✓ Here today</span>;
  return <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">Not checked in</span>;
}

function ChildDetail({ child }: { child: ParentChild }) {
  const [reports, setReports] = useState<ChildReport[]>([]);
  const [attendance, setAttendance] = useState<ChildAttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      parentService.getChildReports(child.id),
      parentService.getChildAttendance(child.id),
    ]).then(([r, a]) => { setReports(r); setAttendance(a); }).finally(() => setLoading(false));
  }, [child.id]);

  const latestReport = reports[0];

  const fmtDate = (d: string) => new Date(d).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
  const fmtTime = (t?: string) => t ? t.slice(0, 5) : '—';

  if (loading) return <div className="px-4 py-6 text-center text-gray-400 text-sm">Loading…</div>;

  return (
    <div className="border-t border-gray-100 bg-gray-50">
      {/* Latest Daily Report */}
      <div className="px-4 py-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Latest Daily Report</h3>
        {latestReport ? (
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500">{fmtDate(latestReport.report_date)}</span>
              {latestReport.overall_mood && (
                <span className="text-base" title={latestReport.overall_mood}>
                  {MOOD_EMOJI[latestReport.overall_mood] ?? latestReport.overall_mood}
                </span>
              )}
            </div>
            {latestReport.ai_generated_summary ? (
              <p className="text-sm text-gray-700 leading-relaxed">{latestReport.ai_generated_summary}</p>
            ) : (
              <p className="text-sm text-gray-400 italic">No summary available yet.</p>
            )}
            {latestReport.custom_notes && (
              <p className="mt-2 text-sm text-gray-600 border-t border-gray-100 pt-2">
                <span className="font-medium">Staff note:</span> {latestReport.custom_notes}
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-400 italic">No reports in the last 14 days.</p>
        )}
      </div>

      {/* Attendance — last 7 days */}
      <div className="px-4 pb-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Attendance (last 7 days)</h3>
        {attendance.length === 0 ? (
          <p className="text-sm text-gray-400 italic">No attendance records.</p>
        ) : (
          <div className="bg-white rounded-xl overflow-hidden border border-gray-100 shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Date</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Arrived</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Departed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {attendance.map(a => (
                  <tr key={a.id}>
                    <td className="px-3 py-2 text-gray-700">{fmtDate(a.attendance_date)}</td>
                    <td className="px-3 py-2 text-gray-700">{fmtTime(a.check_in_time)}</td>
                    <td className="px-3 py-2 text-gray-500">{fmtTime(a.check_out_time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export const ParentDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [children, setChildren] = useState<ParentChild[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    parentService.getMyChildren()
      .then(setChildren)
      .catch(() => setError('Could not load children. Please try again.'))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id: string) => setExpanded(prev => prev === id ? null : id);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-4 flex items-center justify-between sticky top-0 z-10">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Netta's Bounce Around</p>
          <h1 className="text-lg font-bold text-gray-900">
            Welcome, {user?.first_name}!
          </h1>
        </div>
        <button onClick={logout}
          className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          Sign out
        </button>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">{error}</div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        ) : children.length === 0 ? (
          <div className="text-center py-20 text-gray-500">
            <p className="text-lg font-medium">No children linked to your account.</p>
            <p className="text-sm mt-1">Please contact the daycare to update your profile.</p>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-gray-500 mb-4">
              {new Date().toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })}
            </p>
            {children.map(child => (
              <div key={child.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {/* Child card header — tap to expand */}
                <button
                  onClick={() => toggle(child.id)}
                  className="w-full px-4 py-4 flex items-center gap-3 text-left hover:bg-gray-50 transition-colors"
                >
                  {/* Avatar */}
                  <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center shrink-0 text-primary-700 font-bold text-lg">
                    {child.photo_url
                      ? <img src={child.photo_url} alt="" className="w-12 h-12 rounded-full object-cover" />
                      : `${child.first_name[0]}${child.last_name[0]}`}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-gray-900">{child.first_name} {child.last_name}</span>
                      {child.today_mood && (
                        <span className="text-base" title={child.today_mood}>{MOOD_EMOJI[child.today_mood] ?? child.today_mood}</span>
                      )}
                    </div>
                    <div className="mt-1">
                      <AttendanceBadge child={child} />
                    </div>
                  </div>
                  <svg
                    className={`w-5 h-5 text-gray-400 shrink-0 transition-transform ${expanded === child.id ? 'rotate-180' : ''}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Expanded detail */}
                {expanded === child.id && <ChildDetail child={child} />}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
