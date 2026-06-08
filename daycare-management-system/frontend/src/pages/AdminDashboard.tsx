import React, { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { useAuth } from '@/context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { AddEditChildModal } from '@/components/children/AddEditChildModal';
import { dashboardService, type DashboardSummary } from '@/services/dashboardService';
import { activityService, type Activity } from '@/services/activityService';
import { MiniCalendar } from '@/components/dashboard/MiniCalendar';

export const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showAddChildModal, setShowAddChildModal] = useState(false);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentActivities, setRecentActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSummary = async () => {
    try {
      const data = await dashboardService.getSummary();
      setSummary(data);
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    activityService.getTodayActivities()
      .then(data => setRecentActivities(data.slice(0, 5)))
      .catch(() => {});
  }, []);

  const fmt = (n: number | undefined) => loading ? '...' : (n ?? 0).toString();

  const stats = [
    {
      name: 'Total Children',
      value: fmt(summary?.total_children),
      change: '',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      color: 'bg-blue-500',
    },
    {
      name: 'Present Today',
      value: fmt(summary?.present_today),
      change: summary ? `${summary.attendance_percentage}%` : '',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-green-500',
    },
    {
      name: 'Staff On Duty',
      value: fmt(summary?.staff_on_duty),
      change: '',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      color: 'bg-purple-500',
    },
    {
      name: 'Pending Alerts',
      value: fmt(summary?.pending_alerts),
      change: '',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      color: 'bg-yellow-500',
    },
  ];

  const quickActions = [
    { title: 'Enroll New Family', description: 'Register a new family', link: '/enroll', color: 'from-emerald-500 to-emerald-700',
      icon: (<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>),
    },
    { title: 'Check In Child',   description: 'Record arrival',       link: '/attendance', color: 'from-green-500 to-green-600',
      icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" /></svg> },
    { title: 'Add Activity',     description: 'Log daily activity',   link: '/activities', color: 'from-blue-500 to-blue-600',
      icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg> },
    { title: 'Record Incident',  description: 'Report incident',      link: '/incidents',  color: 'from-red-500 to-red-600',
      icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg> },
    { title: 'Add Child',        description: 'Enroll new child',     link: '#',           color: 'from-purple-500 to-purple-600', onClick: () => setShowAddChildModal(true),
      icon: <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg> },
  ];

  const TYPE_COLORS: Record<string, string> = {
    meal: 'bg-orange-500', nap: 'bg-indigo-500', diaper: 'bg-pink-500',
    play: 'bg-green-500', learning: 'bg-blue-500', outdoor: 'bg-teal-500',
  };

  const formatTime = (iso: string) => {
    try { return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
    catch { return iso; }
  };

  return (
    <AdminLayout>
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.first_name}!</h1>
        <p className="mt-2 text-gray-600">Here's what's happening at Netta's Bounce Around today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map(stat => (
          <div key={stat.name} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                {stat.change && <p className="mt-2 text-sm font-medium text-gray-600">{stat.change}</p>}
              </div>
              <div className={`${stat.color} p-3 rounded-lg text-white`}>{stat.icon}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map(action => {
            const Component = action.onClick ? 'button' : Link;
            const props = action.onClick
              ? { onClick: action.onClick, type: 'button' as const }
              : { to: action.link };
            return (
              <Component key={action.title} {...props}
                className="group relative bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-lg transition-all overflow-hidden text-left w-full">
                <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity`} />
                <div className="relative">
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${action.color} text-white mb-4`}>{action.icon}</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </Component>
            );
          })}
        </div>
      </div>

      {/* Calendar + Recent Activity row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Mini Calendar */}
        <MiniCalendar />

        {/* Recent Activity — real data */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Today's Activity</h2>
          </div>
          <div className="p-6">
            {recentActivities.length === 0 ? (
              <p className="text-sm text-gray-400 italic">No activities logged today yet.</p>
            ) : (
              <div className="space-y-3">
                {recentActivities.map(a => (
                  <div key={a.id} className="flex items-center gap-3">
                    <span className={`shrink-0 w-2 h-2 rounded-full ${TYPE_COLORS[a.activity_type] ?? 'bg-gray-400'}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 capitalize truncate">
                        {a.activity_type}: {a.activity_name}
                      </p>
                      <p className="text-xs text-gray-500">{formatTime(a.activity_time)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-4">
              <Link to="/activities" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                View all activity →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Overview (Admin Only) — links to real compliance page */}
      {user?.role === 'admin' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Compliance Overview</h2>
          </div>
          <div className="p-6">
            <p className="text-sm text-gray-500 mb-4">View immunization records, staff credentials, and enrollment form status.</p>
            <Link to="/compliance"
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors">
              Open Compliance Dashboard →
            </Link>
          </div>
        </div>
      )}

      {/* Add Child Modal */}
      <AddEditChildModal
        child={null}
        isOpen={showAddChildModal}
        onClose={() => setShowAddChildModal(false)}
        onSuccess={async () => {
          setShowAddChildModal(false);
          await fetchSummary();
          navigate('/children');
        }}
      />
    </AdminLayout>
  );
};
