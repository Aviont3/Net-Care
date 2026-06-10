import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Mobile-only bottom navigation bar for staff.
 * Shows the 5 most-used actions as a persistent bottom tab bar.
 * Only visible on screens < 768px (md breakpoint).
 */
export const MobileBottomNav: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const tabs = [
    {
      name: 'Home',
      path: '/dashboard',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
    },
    {
      name: 'Check In',
      path: '/attendance',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
      ),
    },
    {
      name: 'Activity',
      path: '/activities',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      ),
      highlight: true, // Center action button
    },
    {
      name: 'Calendar',
      path: '/calendar',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      name: 'Children',
      path: '/children',
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
    },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg md:hidden safe-area-bottom">
      <div className="flex items-center justify-around h-16 px-2">
        {tabs.map((tab) => {
          const active = isActive(tab.path);

          if (tab.highlight) {
            // Center "+" action button — elevated
            return (
              <Link
                key={tab.path}
                to={tab.path}
                className="relative -mt-6"
              >
                <div className={`w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all ${
                  active
                    ? 'bg-indigo-600 text-white scale-110'
                    : 'bg-indigo-500 text-white hover:bg-indigo-600'
                }`}>
                  {tab.icon}
                </div>
                <span className="block text-[10px] text-center mt-1 text-gray-500 font-medium">{tab.name}</span>
              </Link>
            );
          }

          return (
            <Link
              key={tab.path}
              to={tab.path}
              className={`flex flex-col items-center justify-center w-16 h-full transition-colors ${
                active ? 'text-indigo-600' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              {tab.icon}
              <span className={`text-[10px] mt-0.5 font-medium ${active ? 'text-indigo-600' : 'text-gray-500'}`}>
                {tab.name}
              </span>
              {active && <span className="absolute bottom-1 w-5 h-0.5 bg-indigo-600 rounded-full" />}
            </Link>
          );
        })}
      </div>
    </nav>
  );
};
