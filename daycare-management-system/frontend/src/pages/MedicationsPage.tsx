import React, { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { childrenService } from '@/services/childrenService';
import {
  medicationService,
  type MedicationAuthorization,
  type MedicationLog,
  type MedicationAuthorizationCreate,
  type MedicationLogCreate,
} from '@/services/medicationService';
import type { Child } from '@/types';

type Tab = 'authorizations' | 'log' | 'history';

const today = new Date().toISOString().split('T')[0];
const nowTime = new Date().toTimeString().slice(0, 5);

const EMPTY_AUTH: MedicationAuthorizationCreate = {
  child_id: '', medication_name: '', dosage: '', frequency: '',
  administration_instructions: '', start_date: today, end_date: '', prescribing_doctor: '',
};

const EMPTY_LOG: MedicationLogCreate = {
  child_id: '', authorization_id: '', administration_date: today,
  administration_time: nowTime, dosage_given: '', notes: '',
};

function authStatus(auth: MedicationAuthorization): 'expired' | 'expiring' | 'active' {
  if (!auth.is_active) return 'expired';
  if (!auth.end_date) return 'active';
  const diff = (new Date(auth.end_date).getTime() - Date.now()) / 86400000;
  if (diff < 0) return 'expired';
  if (diff <= 7) return 'expiring';
  return 'active';
}

const STATUS_STYLES = {
  active: 'border-green-200 bg-green-50',
  expiring: 'border-yellow-200 bg-yellow-50',
  expired: 'border-red-200 bg-red-50',
};
const STATUS_BADGE = {
  active: 'bg-green-100 text-green-700',
  expiring: 'bg-yellow-100 text-yellow-700',
  expired: 'bg-red-100 text-red-700',
};

export const MedicationsPage: React.FC = () => {
  const [tab, setTab] = useState<Tab>('authorizations');
  const [children, setChildren] = useState<Child[]>([]);
  const [authorizations, setAuthorizations] = useState<MedicationAuthorization[]>([]);
  const [logs, setLogs] = useState<MedicationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [authForm, setAuthForm] = useState<MedicationAuthorizationCreate>(EMPTY_AUTH);
  const [logForm, setLogForm] = useState<MedicationLogCreate>(EMPTY_LOG);
  const [showAuthForm, setShowAuthForm] = useState(false);

  // History filters
  const [filterChild, setFilterChild] = useState('');
  const [filterDate, setFilterDate] = useState('');

  const childName = (id: string) => {
    const c = children.find(ch => ch.id === id);
    return c ? `${c.first_name} ${c.last_name}` : '—';
  };

  const authName = (id: string) => {
    const a = authorizations.find(a => a.id === id);
    return a ? `${a.medication_name} (${a.dosage})` : '—';
  };

  useEffect(() => {
    const init = async () => {
      try {
        const [childRes, authRes, logRes] = await Promise.all([
          childrenService.getChildren({ is_active: true, page_size: 200 }),
          medicationService.getAuthorizations(),
          medicationService.getLogs(),
        ]);
        setChildren(childRes.children);
        setAuthorizations(authRes);
        setLogs(logRes);
      } catch { setError('Failed to load data.'); }
      finally { setLoading(false); }
    };
    init();
  }, []);

  const handleAuthChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setAuthForm(f => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleLogChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setLogForm(f => {
      const updated = { ...f, [name]: value };
      // Auto-fill child_id and dosage when authorization changes
      if (name === 'authorization_id') {
        const auth = authorizations.find(a => a.id === value);
        if (auth) updated.child_id = auth.child_id, updated.dosage_given = auth.dosage;
      }
      return updated;
    });
  };

  const flash = (msg: string) => { setSuccess(msg); setTimeout(() => setSuccess(''), 3500); };

  const submitAuthorization = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authForm.child_id || !authForm.medication_name || !authForm.dosage) {
      setError('Child, medication name, and dosage are required.'); return;
    }
    setError(''); setSubmitting(true);
    try {
      const payload = { ...authForm, end_date: authForm.end_date || undefined, prescribing_doctor: authForm.prescribing_doctor || undefined };
      const created = await medicationService.createAuthorization(payload);
      setAuthorizations(prev => [created, ...prev]);
      setAuthForm(EMPTY_AUTH);
      setShowAuthForm(false);
      flash('Authorization added.');
    } catch { setError('Failed to save authorization.'); }
    finally { setSubmitting(false); }
  };

  const submitLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!logForm.authorization_id || !logForm.dosage_given) {
      setError('Medication and dosage given are required.'); return;
    }
    setError(''); setSubmitting(true);
    try {
      const payload = { ...logForm, notes: logForm.notes || undefined };
      const created = await medicationService.createLog(payload);
      setLogs(prev => [created, ...prev]);
      setLogForm({ ...EMPTY_LOG, administration_date: today, administration_time: new Date().toTimeString().slice(0, 5) });
      flash('Dose logged successfully.');
      setTab('history');
    } catch { setError('Failed to log dose. Check authorization dates.'); }
    finally { setSubmitting(false); }
  };

  const startLogDose = (auth: MedicationAuthorization) => {
    setLogForm({ ...EMPTY_LOG, authorization_id: auth.id, child_id: auth.child_id, dosage_given: auth.dosage, administration_date: today, administration_time: new Date().toTimeString().slice(0, 5) });
    setTab('log');
  };

  const filteredLogs = logs.filter(l =>
    (!filterChild || l.child_id === filterChild) &&
    (!filterDate || l.administration_date === filterDate)
  );

  const formatTime = (t: string) => {
    try { return new Date(`1970-01-01T${t}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
    catch { return t; }
  };

  const TABS: { id: Tab; label: string }[] = [
    { id: 'authorizations', label: 'Active Authorizations' },
    { id: 'log', label: 'Log Dose' },
    { id: 'history', label: 'Administration History' },
  ];

  return (
    <AdminLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Medications</h1>
        <p className="mt-1 text-gray-600">Manage authorizations and track every dose administered.</p>
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}
      {success && <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">{success}</div>}

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6 gap-1">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${tab === t.id ? 'bg-white border border-b-white border-gray-200 text-primary-600 -mb-px' : 'text-gray-500 hover:text-gray-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="p-12 text-center text-gray-500">Loading...</div>
      ) : (
        <>
          {/* ── AUTHORIZATIONS TAB ── */}
          {tab === 'authorizations' && (
            <div>
              <div className="flex justify-end mb-4">
                <button onClick={() => setShowAuthForm(v => !v)}
                  className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors">
                  {showAuthForm ? 'Cancel' : '+ Add Authorization'}
                </button>
              </div>

              {showAuthForm && (
                <form onSubmit={submitAuthorization} className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                  <h3 className="text-base font-semibold text-gray-900 mb-4">New Medication Authorization</h3>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Child *</label>
                      <select name="child_id" value={authForm.child_id} onChange={handleAuthChange}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                        <option value="">Select child...</option>
                        {children.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Medication Name *</label>
                      <input type="text" name="medication_name" value={authForm.medication_name} onChange={handleAuthChange}
                        placeholder="e.g. Amoxicillin"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Dosage *</label>
                      <input type="text" name="dosage" value={authForm.dosage} onChange={handleAuthChange}
                        placeholder="e.g. 250mg"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Frequency *</label>
                      <input type="text" name="frequency" value={authForm.frequency} onChange={handleAuthChange}
                        placeholder="e.g. Twice daily"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
                      <input type="date" name="start_date" value={authForm.start_date} onChange={handleAuthChange}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                      <input type="date" name="end_date" value={authForm.end_date} onChange={handleAuthChange}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Prescribing Doctor</label>
                      <input type="text" name="prescribing_doctor" value={authForm.prescribing_doctor} onChange={handleAuthChange}
                        placeholder="Dr. Smith"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Administration Instructions *</label>
                      <input type="text" name="administration_instructions" value={authForm.administration_instructions} onChange={handleAuthChange}
                        placeholder="e.g. Give with food at 12pm"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    </div>
                  </div>
                  <div className="flex justify-end mt-4">
                    <button type="submit" disabled={submitting}
                      className="px-5 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors">
                      {submitting ? 'Saving...' : 'Save Authorization'}
                    </button>
                  </div>
                </form>
              )}

              {authorizations.length === 0 ? (
                <div className="p-12 text-center text-gray-500">No medication authorizations on file.</div>
              ) : (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {authorizations.map(auth => {
                    const status = authStatus(auth);
                    return (
                      <div key={auth.id} className={`rounded-xl border p-4 ${STATUS_STYLES[status]}`}>
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-semibold text-gray-900">{auth.medication_name}</p>
                            <p className="text-sm text-gray-600">{childName(auth.child_id)}</p>
                          </div>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[status]}`}>
                            {status === 'expiring' ? 'Expiring soon' : status}
                          </span>
                        </div>
                        <dl className="text-sm space-y-1 text-gray-700">
                          <div><span className="font-medium">Dosage:</span> {auth.dosage}</div>
                          <div><span className="font-medium">Frequency:</span> {auth.frequency}</div>
                          <div><span className="font-medium">Instructions:</span> {auth.administration_instructions}</div>
                          {auth.end_date && <div><span className="font-medium">Expires:</span> {auth.end_date}</div>}
                          {auth.prescribing_doctor && <div><span className="font-medium">Dr:</span> {auth.prescribing_doctor}</div>}
                        </dl>
                        {status !== 'expired' && (
                          <button onClick={() => startLogDose(auth)}
                            className="mt-3 w-full py-1.5 text-sm font-medium text-primary-600 border border-primary-300 rounded-lg hover:bg-primary-50 transition-colors">
                            Log Dose
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ── LOG DOSE TAB ── */}
          {tab === 'log' && (
            <div className="max-w-lg">
              <form onSubmit={submitLog} className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">Log Dose</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Medication *</label>
                  <select name="authorization_id" value={logForm.authorization_id} onChange={handleLogChange}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">Select medication...</option>
                    {authorizations.filter(a => authStatus(a) !== 'expired').map(a => (
                      <option key={a.id} value={a.id}>{childName(a.child_id)} — {a.medication_name} ({a.dosage})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Dosage Given *</label>
                  <input type="text" name="dosage_given" value={logForm.dosage_given} onChange={handleLogChange}
                    placeholder="e.g. 250mg"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date *</label>
                    <input type="date" name="administration_date" value={logForm.administration_date} onChange={handleLogChange}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Time *</label>
                    <input type="time" name="administration_time" value={logForm.administration_time} onChange={handleLogChange}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea name="notes" value={logForm.notes} onChange={handleLogChange} rows={2}
                    placeholder="Any observations..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none" />
                </div>
                <button type="submit" disabled={submitting}
                  className="w-full py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  {submitting ? 'Logging...' : 'Log Dose'}
                </button>
              </form>
            </div>
          )}

          {/* ── HISTORY TAB ── */}
          {tab === 'history' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  Administration History
                  <span className="ml-2 text-sm font-normal text-gray-500">({filteredLogs.length})</span>
                </h2>
                <div className="flex gap-2 flex-wrap">
                  <select value={filterChild} onChange={e => setFilterChild(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">All children</option>
                    {children.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
                  </select>
                  <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                  {(filterChild || filterDate) && (
                    <button onClick={() => { setFilterChild(''); setFilterDate(''); }}
                      className="text-sm text-gray-500 hover:text-gray-700 px-2">Clear</button>
                  )}
                </div>
              </div>
              {filteredLogs.length === 0 ? (
                <div className="p-12 text-center text-gray-500">No administration records found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>
                        {['Date', 'Time', 'Child', 'Medication', 'Dosage Given', 'Notes'].map(h => (
                          <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {filteredLogs.map(log => (
                        <tr key={log.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-gray-900">{log.administration_date}</td>
                          <td className="px-4 py-3 text-gray-700">{formatTime(log.administration_time)}</td>
                          <td className="px-4 py-3 font-medium text-gray-900">{childName(log.child_id)}</td>
                          <td className="px-4 py-3 text-gray-700">{authName(log.authorization_id)}</td>
                          <td className="px-4 py-3 text-gray-700">{log.dosage_given}</td>
                          <td className="px-4 py-3 text-gray-500">{log.notes ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </AdminLayout>
  );
};
