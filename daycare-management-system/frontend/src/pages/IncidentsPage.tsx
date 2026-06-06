import React, { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { childrenService } from '@/services/childrenService';
import { incidentService, type IncidentReport, type IncidentReportCreate } from '@/services/incidentService';
import type { Child } from '@/types';

const INCIDENT_TYPES = ['injury', 'illness', 'behavioral', 'accident', 'other'] as const;
const TYPE_LABELS: Record<string, string> = {
  injury: '🩹 Injury', illness: '🤒 Illness', behavioral: '⚠️ Behavioral',
  accident: '💥 Accident', other: '📋 Other',
};
const SEVERITY_COLORS: Record<string, string> = {
  injury: 'bg-red-100 text-red-700 border-red-200',
  illness: 'bg-orange-100 text-orange-700 border-orange-200',
  behavioral: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  accident: 'bg-red-100 text-red-700 border-red-200',
  other: 'bg-gray-100 text-gray-700 border-gray-200',
};

const today = new Date().toISOString().split('T')[0];
const nowTime = new Date().toTimeString().slice(0, 5);

const EMPTY_FORM: IncidentReportCreate = {
  child_id: '', incident_date: today, incident_time: nowTime,
  incident_type: 'injury', description: '', circumstances: '', action_taken: '',
  injury_description: '', body_part_affected: '', witnesses: '',
  parent_notified: false, dcfs_notification_required: false,
};

export const IncidentsPage: React.FC = () => {
  const [children, setChildren] = useState<Child[]>([]);
  const [incidents, setIncidents] = useState<IncidentReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState<IncidentReportCreate>(EMPTY_FORM);
  const [filterType, setFilterType] = useState('');
  const [notifyingId, setNotifyingId] = useState<string | null>(null);

  const childName = (id: string) => {
    const c = children.find(ch => ch.id === id);
    return c ? `${c.first_name} ${c.last_name}` : '—';
  };

  const fetchIncidents = async () => {
    try {
      const data = await incidentService.getIncidents(filterType ? { incident_type: filterType } : undefined);
      setIncidents(data);
    } catch { /* non-critical */ }
  };

  useEffect(() => {
    const init = async () => {
      try {
        const [childRes, incRes] = await Promise.all([
          childrenService.getChildren({ is_active: true, page_size: 200 }),
          incidentService.getIncidents(),
        ]);
        setChildren(childRes.children);
        setIncidents(incRes);
      } catch { setError('Failed to load data.'); }
      finally { setLoading(false); }
    };
    init();
  }, []);

  useEffect(() => { if (!loading) fetchIncidents(); }, [filterType]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setForm(f => ({
      ...f,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.child_id) { setError('Please select a child.'); return; }
    if (!form.description.trim()) { setError('Description is required.'); return; }
    if (!form.circumstances.trim()) { setError('Circumstances are required.'); return; }
    if (!form.action_taken.trim()) { setError('Actions taken is required.'); return; }
    setError('');
    setSubmitting(true);
    try {
      const payload: IncidentReportCreate = {
        ...form,
        injury_description: form.injury_description || undefined,
        body_part_affected: form.body_part_affected || undefined,
        witnesses: form.witnesses || undefined,
      };
      await incidentService.createIncident(payload);
      setSuccess('Incident report filed successfully.');
      setForm({ ...EMPTY_FORM, incident_date: today, incident_time: new Date().toTimeString().slice(0, 5) });
      await fetchIncidents();
      setTimeout(() => setSuccess(''), 4000);
    } catch { setError('Failed to file incident report. Please try again.'); }
    finally { setSubmitting(false); }
  };

  const handleNotifyParent = async (id: string) => {
    setNotifyingId(id);
    try {
      await incidentService.markParentNotified(id, 'phone');
      await fetchIncidents();
    } catch { setError('Failed to record parent notification.'); }
    finally { setNotifyingId(null); }
  };

  const formatDateTime = (dateStr: string, timeStr: string) => {
    try {
      const d = new Date(`${dateStr}T${timeStr}`);
      return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch { return `${dateStr} ${timeStr}`; }
  };

  const unnotified = incidents.filter(i => !i.parent_notified);

  return (
    <AdminLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Incident Reports</h1>
        <p className="mt-1 text-gray-600">DCFS Form 337 — document all incidents requiring parent or state notification.</p>
      </div>

      {/* Alert banner for unnotified parents */}
      {unnotified.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
          <svg className="w-5 h-5 text-red-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <p className="font-semibold text-red-700">{unnotified.length} incident{unnotified.length !== 1 ? 's' : ''} pending parent notification</p>
            <p className="text-sm text-red-600 mt-0.5">DCFS requires immediate parent notification for all incidents.</p>
          </div>
        </div>
      )}

      {/* File Report Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">File Incident Report</h2>

        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}
        {success && <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">{success}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Child *</label>
              <select name="child_id" value={form.child_id} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="">Select child...</option>
                {children.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Incident Type *</label>
              <select name="incident_type" value={form.incident_type} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                {INCIDENT_TYPES.map(t => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date *</label>
              <input type="date" name="incident_date" value={form.incident_date} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Time *</label>
              <input type="time" name="incident_time" value={form.incident_time} onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea name="description" value={form.description} onChange={handleChange} rows={3}
                placeholder="What happened? Be specific..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Circumstances *</label>
              <textarea name="circumstances" value={form.circumstances} onChange={handleChange} rows={3}
                placeholder="What was happening before the incident?"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Actions Taken *</label>
            <textarea name="action_taken" value={form.action_taken} onChange={handleChange} rows={2}
              placeholder="First aid given, parent called, ice pack applied..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none" />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Injury Description</label>
              <input type="text" name="injury_description" value={form.injury_description} onChange={handleChange}
                placeholder="e.g. Scraped knee, bump on head..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Body Part Affected</label>
              <input type="text" name="body_part_affected" value={form.body_part_affected} onChange={handleChange}
                placeholder="e.g. Left knee, forehead..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Witnesses</label>
              <input type="text" name="witnesses" value={form.witnesses} onChange={handleChange}
                placeholder="Staff or children who witnessed..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
          </div>

          <div className="flex flex-wrap gap-6">
            <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" name="parent_notified" checked={form.parent_notified} onChange={handleChange}
                className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
              Parent notified at time of filing
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" name="dcfs_notification_required" checked={form.dcfs_notification_required} onChange={handleChange}
                className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
              DCFS notification required
            </label>
          </div>

          <div className="flex justify-end pt-2">
            <button type="submit" disabled={submitting}
              className="px-6 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors">
              {submitting ? 'Filing...' : 'File Incident Report'}
            </button>
          </div>
        </form>
      </div>

      {/* Incident Log */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h2 className="text-lg font-semibold text-gray-900">
            Incident Log
            <span className="ml-2 text-sm font-normal text-gray-500">({incidents.length})</span>
          </h2>
          <select value={filterType} onChange={e => setFilterType(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="">All types</option>
            {INCIDENT_TYPES.map(t => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
          </select>
        </div>

        {loading ? (
          <div className="p-12 text-center text-gray-500">Loading...</div>
        ) : incidents.length === 0 ? (
          <div className="p-12 text-center text-gray-500">No incidents on record.</div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {incidents.map(inc => (
              <li key={inc.id} className="px-6 py-4">
                <div className="flex flex-col sm:flex-row sm:items-start gap-3">
                  <span className={`shrink-0 self-start px-2.5 py-1 rounded-full text-xs font-medium border ${SEVERITY_COLORS[inc.incident_type] ?? 'bg-gray-100 text-gray-700 border-gray-200'}`}>
                    {TYPE_LABELS[inc.incident_type] ?? inc.incident_type}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-baseline gap-x-2">
                      <span className="font-medium text-gray-900 text-sm">{childName(inc.child_id)}</span>
                      <span className="text-xs text-gray-500">{formatDateTime(inc.incident_date, inc.incident_time)}</span>
                    </div>
                    <p className="text-sm text-gray-700 mt-1">{inc.description}</p>
                    <p className="text-xs text-gray-500 mt-0.5"><span className="font-medium">Action:</span> {inc.action_taken}</p>
                    <div className="flex flex-wrap gap-x-4 mt-2">
                      {inc.parent_notified ? (
                        <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Parent notified
                        </span>
                      ) : (
                        <button onClick={() => handleNotifyParent(inc.id)} disabled={notifyingId === inc.id}
                          className="text-xs text-red-600 font-medium hover:underline disabled:opacity-50">
                          {notifyingId === inc.id ? 'Recording...' : '⚠ Mark parent notified'}
                        </button>
                      )}
                      {inc.dcfs_notification_required && (
                        <span className={`text-xs font-medium ${inc.dcfs_notified_at ? 'text-green-600' : 'text-orange-600'}`}>
                          {inc.dcfs_notified_at ? '✓ DCFS notified' : '⚠ DCFS notification required'}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </AdminLayout>
  );
};
