import React, { useState, useEffect, useCallback } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { childrenService } from '@/services/childrenService';
import {
  complianceService,
  type ImmunizationRecord,
  type StaffCredential,
  type EnrollmentForm,
  type ComplianceAlert,
} from '@/services/complianceService';
import type { Child } from '@/types';

type Tab = 'overview' | 'immunizations' | 'credentials' | 'enrollment' | 'alerts';

const SEVERITY_STYLE: Record<string, string> = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high:     'bg-orange-100 text-orange-700 border-orange-200',
  medium:   'bg-yellow-100 text-yellow-700 border-yellow-200',
  low:      'bg-blue-100 text-blue-700 border-blue-200',
};

function immunizationStatus(r: ImmunizationRecord): 'expired' | 'expiring' | 'current' {
  if (!r.expiration_date) return 'current';
  const diff = (new Date(r.expiration_date).getTime() - Date.now()) / 86400000;
  if (diff < 0) return 'expired';
  if (diff <= 30) return 'expiring';
  return 'current';
}

function credentialStatus(c: StaffCredential): 'expired' | 'expiring' | 'current' {
  if (c.is_expired) return 'expired';
  if (!c.expiration_date) return 'current';
  const diff = (new Date(c.expiration_date).getTime() - Date.now()) / 86400000;
  if (diff <= 30) return 'expiring';
  return 'current';
}

const STATUS_BADGE: Record<string, string> = {
  current:  'bg-green-100 text-green-700',
  expiring: 'bg-yellow-100 text-yellow-700',
  expired:  'bg-red-100 text-red-700',
};

const TABS: { id: Tab; label: string }[] = [
  { id: 'overview',      label: 'Overview' },
  { id: 'immunizations', label: 'Immunizations' },
  { id: 'credentials',   label: 'Staff Credentials' },
  { id: 'enrollment',    label: 'Enrollment Forms' },
  { id: 'alerts',        label: 'Alerts' },
];

export const CompliancePage: React.FC = () => {
  const [tab, setTab] = useState<Tab>('overview');
  const [children, setChildren] = useState<Child[]>([]);
  const [immunizations, setImmunizations] = useState<ImmunizationRecord[]>([]);
  const [credentials, setCredentials] = useState<StaffCredential[]>([]);
  const [forms, setForms] = useState<EnrollmentForm[]>([]);
  const [alerts, setAlerts] = useState<ComplianceAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [filterImmunChild, setFilterImmunChild] = useState('');
  const [filterImmunStatus, setFilterImmunStatus] = useState('');
  const [filterCredStatus, setFilterCredStatus] = useState('');
  const [filterAlertResolved, setFilterAlertResolved] = useState('unresolved');

  const childName = (id: string) => {
    const c = children.find(ch => ch.id === id);
    return c ? `${c.first_name} ${c.last_name}` : '—';
  };

  useEffect(() => {
    const init = async () => {
      try {
        const [childRes, immRes, credRes, formRes, alertRes] = await Promise.all([
          childrenService.getChildren({ is_active: true, page_size: 200 }),
          complianceService.getImmunizations(),
          complianceService.getCredentials(),
          complianceService.getEnrollmentForms(),
          complianceService.getAlerts({ is_resolved: false }),
        ]);
        setChildren(childRes.children);
        setImmunizations(immRes);
        setCredentials(credRes);
        setForms(formRes);
        setAlerts(alertRes);
      } catch { setError('Failed to load compliance data.'); }
      finally { setLoading(false); }
    };
    init();
  }, []);

  const handleVerifyImmun = async (id: string) => {
    const updated = await complianceService.verifyImmunization(id);
    setImmunizations(prev => prev.map(r => r.id === id ? updated : r));
  };

  const handleVerifyCred = async (id: string) => {
    const updated = await complianceService.verifyCredential(id);
    setCredentials(prev => prev.map(c => c.id === id ? updated : c));
  };

  const handleResolveAlert = async (id: string) => {
    const updated = await complianceService.resolveAlert(id);
    setAlerts(prev => prev.map(a => a.id === id ? updated : a));
  };

  const refreshAlerts = useCallback(async () => {
    const is_resolved = filterAlertResolved === 'all' ? undefined : filterAlertResolved === 'resolved';
    const data = await complianceService.getAlerts({ is_resolved });
    setAlerts(data);
  }, [filterAlertResolved]);

  useEffect(() => { if (!loading) refreshAlerts(); }, [filterAlertResolved]);

  // Derived stats for overview
  const immunExpired  = immunizations.filter(r => immunizationStatus(r) === 'expired').length;
  const immunExpiring = immunizations.filter(r => immunizationStatus(r) === 'expiring').length;
  const immunCurrent  = immunizations.filter(r => immunizationStatus(r) === 'current').length;
  const immunPct = immunizations.length > 0
    ? Math.round(immunCurrent / immunizations.length * 100) : 100;

  const credExpired  = credentials.filter(c => credentialStatus(c) === 'expired').length;
  const credExpiring = credentials.filter(c => credentialStatus(c) === 'expiring').length;

  const formsComplete   = forms.filter(f => f.is_complete).length;
  const formsPending    = forms.filter(f => !f.is_complete).length;
  const activeAlerts    = alerts.filter(a => !a.is_resolved).length;

  // Filtered lists
  const filteredImmun = immunizations.filter(r =>
    (!filterImmunChild  || r.child_id === filterImmunChild) &&
    (!filterImmunStatus || immunizationStatus(r) === filterImmunStatus)
  );
  const filteredCreds = credentials.filter(c =>
    !filterCredStatus || credentialStatus(c) === filterCredStatus
  );
  const filteredAlerts = filterAlertResolved === 'all'
    ? alerts
    : alerts.filter(a => a.is_resolved === (filterAlertResolved === 'resolved'));

  return (
    <AdminLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">DCFS Compliance</h1>
        <p className="mt-1 text-gray-600">Immunizations, staff credentials, enrollment forms, and compliance alerts.</p>
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>}

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6 gap-1 overflow-x-auto">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap rounded-t-lg transition-colors ${tab === t.id ? 'bg-white border border-b-white border-gray-200 text-primary-600 -mb-px' : 'text-gray-500 hover:text-gray-700'}`}>
            {t.label}
            {t.id === 'alerts' && activeAlerts > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 bg-red-500 text-white text-xs rounded-full">{activeAlerts}</span>
            )}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="p-12 text-center text-gray-500">Loading compliance data…</div>
      ) : (
        <>
          {/* ── OVERVIEW ── */}
          {tab === 'overview' && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  label: 'Immunization Compliance',
                  value: `${immunPct}%`,
                  sub: `${immunExpired} expired · ${immunExpiring} expiring`,
                  color: immunExpired > 0 ? 'border-red-200 bg-red-50' : immunExpiring > 0 ? 'border-yellow-200 bg-yellow-50' : 'border-green-200 bg-green-50',
                  textColor: immunExpired > 0 ? 'text-red-700' : immunExpiring > 0 ? 'text-yellow-700' : 'text-green-700',
                },
                {
                  label: 'Staff Credentials',
                  value: `${credentials.length - credExpired} / ${credentials.length}`,
                  sub: `${credExpired} expired · ${credExpiring} expiring`,
                  color: credExpired > 0 ? 'border-red-200 bg-red-50' : credExpiring > 0 ? 'border-yellow-200 bg-yellow-50' : 'border-green-200 bg-green-50',
                  textColor: credExpired > 0 ? 'text-red-700' : credExpiring > 0 ? 'text-yellow-700' : 'text-green-700',
                },
                {
                  label: 'Enrollment Forms',
                  value: `${formsComplete} / ${forms.length}`,
                  sub: `${formsPending} pending completion`,
                  color: formsPending > 0 ? 'border-yellow-200 bg-yellow-50' : 'border-green-200 bg-green-50',
                  textColor: formsPending > 0 ? 'text-yellow-700' : 'text-green-700',
                },
                {
                  label: 'Active Alerts',
                  value: activeAlerts.toString(),
                  sub: 'Unresolved compliance issues',
                  color: activeAlerts > 0 ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50',
                  textColor: activeAlerts > 0 ? 'text-red-700' : 'text-green-700',
                },
              ].map(card => (
                <div key={card.label} className={`rounded-xl border p-5 ${card.color}`}>
                  <p className="text-sm font-medium text-gray-600">{card.label}</p>
                  <p className={`text-3xl font-bold mt-1 ${card.textColor}`}>{card.value}</p>
                  <p className="text-xs text-gray-500 mt-1">{card.sub}</p>
                </div>
              ))}
            </div>
          )}

          {/* ── IMMUNIZATIONS ── */}
          {tab === 'immunizations' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                <h2 className="font-semibold text-gray-900">Immunization Records ({filteredImmun.length})</h2>
                <div className="flex gap-2 flex-wrap">
                  <select value={filterImmunChild} onChange={e => setFilterImmunChild(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">All children</option>
                    {children.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
                  </select>
                  <select value={filterImmunStatus} onChange={e => setFilterImmunStatus(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                    <option value="">All statuses</option>
                    <option value="current">Current</option>
                    <option value="expiring">Expiring</option>
                    <option value="expired">Expired</option>
                  </select>
                </div>
              </div>
              {filteredImmun.length === 0 ? (
                <div className="p-12 text-center text-gray-500">No records found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>{['Child', 'Vaccine', 'Administered', 'Expires', 'Status', 'Verified', ''].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                      ))}</tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {filteredImmun.map(r => {
                        const st = immunizationStatus(r);
                        return (
                          <tr key={r.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium text-gray-900">{childName(r.child_id)}</td>
                            <td className="px-4 py-3 text-gray-700">{r.vaccine_name}</td>
                            <td className="px-4 py-3 text-gray-600">{r.administration_date}</td>
                            <td className="px-4 py-3 text-gray-600">{r.expiration_date ?? '—'}</td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[st]}`}>{st}</span>
                            </td>
                            <td className="px-4 py-3">
                              {r.is_verified
                                ? <span className="text-green-600 text-xs font-medium">✓ Verified</span>
                                : <span className="text-gray-400 text-xs">Unverified</span>}
                            </td>
                            <td className="px-4 py-3">
                              {!r.is_verified && (
                                <button onClick={() => handleVerifyImmun(r.id)}
                                  className="text-xs text-primary-600 hover:underline font-medium">Mark Verified</button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ── STAFF CREDENTIALS ── */}
          {tab === 'credentials' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                <h2 className="font-semibold text-gray-900">Staff Credentials ({filteredCreds.length})</h2>
                <select value={filterCredStatus} onChange={e => setFilterCredStatus(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="">All statuses</option>
                  <option value="current">Current</option>
                  <option value="expiring">Expiring (30 days)</option>
                  <option value="expired">Expired</option>
                </select>
              </div>
              {filteredCreds.length === 0 ? (
                <div className="p-12 text-center text-gray-500">No credentials found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>{['Staff', 'Credential', 'Issued', 'Expires', 'Status', 'Verified', ''].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                      ))}</tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {filteredCreds.map(c => {
                        const st = credentialStatus(c);
                        return (
                          <tr key={c.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium text-gray-900 text-xs text-gray-500">{c.user_id.slice(0, 8)}…</td>
                            <td className="px-4 py-3 text-gray-700">{c.credential_type}</td>
                            <td className="px-4 py-3 text-gray-600">{c.issue_date}</td>
                            <td className="px-4 py-3 text-gray-600">{c.expiration_date ?? '—'}</td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[st]}`}>{st}</span>
                            </td>
                            <td className="px-4 py-3">
                              {c.is_verified
                                ? <span className="text-green-600 text-xs font-medium">✓ Verified</span>
                                : <span className="text-gray-400 text-xs">Unverified</span>}
                            </td>
                            <td className="px-4 py-3">
                              {!c.is_verified && (
                                <button onClick={() => handleVerifyCred(c.id)}
                                  className="text-xs text-primary-600 hover:underline font-medium">Mark Verified</button>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ── ENROLLMENT FORMS ── */}
          {tab === 'enrollment' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="px-6 py-4 border-b border-gray-100">
                <h2 className="font-semibold text-gray-900">Enrollment Forms ({forms.length})</h2>
              </div>
              {forms.length === 0 ? (
                <div className="p-12 text-center text-gray-500">No enrollment forms on record.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr>{['Child', 'Enrolled', 'Complete', 'Parent Signed', 'Staff Signed'].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                      ))}</tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {forms.map(f => (
                        <tr key={f.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium text-gray-900">{childName(f.child_id)}</td>
                          <td className="px-4 py-3 text-gray-600">{f.enrollment_date}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${f.is_complete ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                              {f.is_complete ? 'Complete' : 'Incomplete'}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            {f.parent_signed_at
                              ? <span className="text-green-600 text-xs">✓ {new Date(f.parent_signed_at).toLocaleDateString()}</span>
                              : <span className="text-red-500 text-xs">Missing</span>}
                          </td>
                          <td className="px-4 py-3">
                            {f.staff_signed_at
                              ? <span className="text-green-600 text-xs">✓ {new Date(f.staff_signed_at).toLocaleDateString()}</span>
                              : <span className="text-red-500 text-xs">Missing</span>}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* ── ALERTS ── */}
          {tab === 'alerts' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="px-6 py-4 border-b border-gray-100 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                <h2 className="font-semibold text-gray-900">Compliance Alerts ({filteredAlerts.length})</h2>
                <select value={filterAlertResolved} onChange={e => setFilterAlertResolved(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                  <option value="unresolved">Unresolved</option>
                  <option value="resolved">Resolved</option>
                  <option value="all">All</option>
                </select>
              </div>
              {filteredAlerts.length === 0 ? (
                <div className="p-12 text-center text-gray-500">
                  {filterAlertResolved === 'unresolved' ? '✓ No active compliance alerts.' : 'No alerts found.'}
                </div>
              ) : (
                <ul className="divide-y divide-gray-100">
                  {filteredAlerts.map(a => (
                    <li key={a.id} className="px-6 py-4 flex items-start gap-3">
                      <span className={`shrink-0 self-start px-2.5 py-1 rounded-full text-xs font-medium border ${SEVERITY_STYLE[a.severity] ?? 'bg-gray-100 text-gray-700 border-gray-200'}`}>
                        {a.severity}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">{a.description}</p>
                        <p className="text-xs text-gray-500 mt-0.5 capitalize">{a.entity_type} · {a.alert_type.replace(/_/g, ' ')}{a.due_date ? ` · Due ${a.due_date}` : ''}</p>
                      </div>
                      {!a.is_resolved && (
                        <button onClick={() => handleResolveAlert(a.id)}
                          className="shrink-0 text-xs text-primary-600 hover:underline font-medium">Resolve</button>
                      )}
                      {a.is_resolved && <span className="shrink-0 text-xs text-green-600 font-medium">✓ Resolved</span>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}
    </AdminLayout>
  );
};
