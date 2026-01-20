import React from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({ title, description, icon }) => {
  return (
    <AdminLayout>
      <div className="flex items-center justify-center min-h-[calc(100vh-300px)]">
        <div className="text-center max-w-md">
          {icon && (
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                <div className="text-primary-600">
                  {icon}
                </div>
              </div>
            </div>
          )}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
          <p className="text-gray-600 mb-8">{description}</p>
          <div className="inline-flex items-center px-4 py-2 bg-primary-50 text-primary-700 rounded-lg text-sm font-medium">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Coming Soon
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};
