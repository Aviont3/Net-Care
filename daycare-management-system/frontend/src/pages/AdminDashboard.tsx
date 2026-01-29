import React, { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { useAuth } from '@/context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { AddEditChildModal } from '@/components/children/AddEditChildModal';
import { childrenService } from '@/services/childrenService';

export const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showAddChildModal, setShowAddChildModal] = useState(false);
  const [totalChildren, setTotalChildren] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  // Fetch total children count
  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const response = await childrenService.getChildren({ is_active: true });
        setTotalChildren(response.total);
      } catch (error) {
        console.error('Error fetching children count:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchChildren();
  }, []);

  // Mock data - will be replaced with actual API calls
  const stats = [
    {
      name: 'Total Children',
      value: loading ? '...' : totalChildren.toString(),
      change: '+4',
      changeType: 'increase',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      color: 'bg-blue-500'
    },
    {
      name: 'Present Today',
      value: '38',
      change: '90%',
      changeType: 'neutral',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'bg-green-500'
    },
    {
      name: 'Staff On Duty',
      value: '12',
      change: '100%',
      changeType: 'neutral',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      color: 'bg-purple-500'
    },
    {
      name: 'Pending Alerts',
      value: '3',
      change: '-2',
      changeType: 'decrease',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      color: 'bg-yellow-500'
    }
  ];

  const quickActions = [
    {
      title: 'Check In Child',
      description: 'Record arrival',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
        </svg>
      ),
      link: '/attendance',
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Add Activity',
      description: 'Log daily activity',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
      ),
      link: '/activities',
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Record Incident',
      description: 'Report incident',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      link: '/incidents',
      color: 'from-red-500 to-red-600'
    },
    {
      title: 'Add Child',
      description: 'Enroll new child',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      ),
      link: '#',
      color: 'from-purple-500 to-purple-600',
      onClick: () => setShowAddChildModal(true)
    }
  ];

  const recentActivity = [
    { type: 'check-in', child: 'Emma Johnson', time: '8:45 AM', status: 'success' },
    { type: 'activity', child: 'Liam Smith', time: '10:30 AM', status: 'info' },
    { type: 'medication', child: 'Olivia Brown', time: '12:15 PM', status: 'warning' },
    { type: 'check-out', child: 'Noah Davis', time: '2:30 PM', status: 'success' },
    { type: 'incident', child: 'Ava Wilson', time: '3:00 PM', status: 'danger' }
  ];

  const upcomingTasks = [
    { task: 'Monthly fire drill', due: 'Today', priority: 'high' },
    { task: 'Update immunization records', due: 'Tomorrow', priority: 'medium' },
    { task: 'Staff meeting', due: 'Friday', priority: 'low' },
    { task: 'Parent-teacher conferences', due: 'Next Week', priority: 'medium' }
  ];

  return (
    <AdminLayout>
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's what's happening at Netta's Bounce Around today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                <div className="mt-2 flex items-center text-sm">
                  <span className={`
                    ${stat.changeType === 'increase' ? 'text-green-600' : ''}
                    ${stat.changeType === 'decrease' ? 'text-red-600' : ''}
                    ${stat.changeType === 'neutral' ? 'text-gray-600' : ''}
                    font-medium
                  `}>
                    {stat.change}
                  </span>
                  <span className="ml-2 text-gray-500">from last month</span>
                </div>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <div className="text-white">
                  {stat.icon}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => {
            const Component = action.onClick ? 'button' : Link;
            const props = action.onClick
              ? { onClick: action.onClick, type: 'button' as const }
              : { to: action.link };

            return (
              <Component
                key={action.title}
                {...props}
                className="group relative bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-lg transition-all overflow-hidden text-left w-full"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity`}></div>
                <div className="relative">
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${action.color} text-white mb-4`}>
                    {action.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </Component>
            );
          })}
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Recent Activity</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`
                    flex-shrink-0 w-2 h-2 mt-2 rounded-full
                    ${activity.status === 'success' ? 'bg-green-500' : ''}
                    ${activity.status === 'info' ? 'bg-blue-500' : ''}
                    ${activity.status === 'warning' ? 'bg-yellow-500' : ''}
                    ${activity.status === 'danger' ? 'bg-red-500' : ''}
                  `}></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 capitalize">
                      {activity.type.replace('-', ' ')}: {activity.child}
                    </p>
                    <p className="text-sm text-gray-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6">
              <Link to="/activities" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                View all activity →
              </Link>
            </div>
          </div>
        </div>

        {/* Upcoming Tasks */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Upcoming Tasks</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {upcomingTasks.map((task, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:border-primary-200 hover:bg-primary-50 transition-colors">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{task.task}</p>
                    <p className="text-xs text-gray-500 mt-1">Due: {task.due}</p>
                  </div>
                  <span className={`
                    px-2.5 py-1 rounded-full text-xs font-medium
                    ${task.priority === 'high' ? 'bg-red-100 text-red-700' : ''}
                    ${task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' : ''}
                    ${task.priority === 'low' ? 'bg-green-100 text-green-700' : ''}
                  `}>
                    {task.priority}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-6">
              <Link to="/tasks" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                View all tasks →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Overview (Admin Only) */}
      {user?.role === 'admin' && (
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Compliance Overview</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 rounded-lg bg-green-50 border border-green-200">
                <div className="text-3xl font-bold text-green-600">98%</div>
                <div className="text-sm text-gray-600 mt-1">Immunizations Up-to-date</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
                <div className="text-3xl font-bold text-blue-600">12/12</div>
                <div className="text-sm text-gray-600 mt-1">Staff Certifications Current</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-yellow-50 border border-yellow-200">
                <div className="text-3xl font-bold text-yellow-600">2</div>
                <div className="text-sm text-gray-600 mt-1">Forms Pending Review</div>
              </div>
            </div>
            <div className="mt-6">
              <Link to="/compliance" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                View full compliance report →
              </Link>
            </div>
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
          // Refresh children count
          try {
            const response = await childrenService.getChildren({ is_active: true });
            setTotalChildren(response.total);
          } catch (error) {
            console.error('Error refreshing children count:', error);
          }
          // Navigate to children page
          navigate('/children');
        }}
      />
    </AdminLayout>
  );
};
