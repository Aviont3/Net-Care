import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { childrenService } from '@/services/childrenService';
import { attendanceService } from '@/services/attendanceService';

interface Child {
  id: string;
  first_name: string;
  last_name: string;
  photo_url?: string;
  is_checked_in: boolean;
  attendance_id?: string; // Store attendance ID for check-out
}

export const CheckInKiosk: React.FC = () => {
  const navigate = useNavigate();
  const [children, setChildren] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showExitModal, setShowExitModal] = useState(false);
  const [passcode, setPasscode] = useState('');
  const [passcodeError, setPasscodeError] = useState('');
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Fetch children and today's attendance
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch both children and today's attendance in parallel
        const [childrenResponse, attendanceRecords] = await Promise.all([
          childrenService.getChildren({ is_active: true }),
          attendanceService.getTodayAttendance()
        ]);

        // Create a map of child_id to attendance record
        const attendanceMap = new Map(
          attendanceRecords.map(record => [record.child_id, record])
        );

        // Map children with check-in status
        const childrenWithCheckInStatus = childrenResponse.children.map(child => {
          const attendance = attendanceMap.get(child.id);
          return {
            id: child.id,
            first_name: child.first_name,
            last_name: child.last_name,
            photo_url: child.photo_url,
            is_checked_in: attendance ? !attendance.check_out_time : false,
            attendance_id: attendance?.id,
          };
        });

        setChildren(childrenWithCheckInStatus);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Correct passcode - in production, this should come from settings
  const ADMIN_PASSCODE = '1234';

  const filteredChildren = children.filter(child =>
    `${child.first_name} ${child.last_name}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleChildClick = (child: Child) => {
    setSelectedChild(child);
    setShowConfirmModal(true);
  };

  const handleCheckInOut = async () => {
    if (!selectedChild) return;

    try {
      const currentTime = new Date().toTimeString().split(' ')[0]; // HH:MM:SS format

      if (selectedChild.is_checked_in) {
        // Check out the child
        if (selectedChild.attendance_id) {
          await attendanceService.checkOut(selectedChild.attendance_id, {
            check_out_time: currentTime,
            check_out_by_name: 'Kiosk User', // In production, get actual name
          });

          // Update local state
          setChildren(prev =>
            prev.map(child =>
              child.id === selectedChild.id
                ? { ...child, is_checked_in: false, attendance_id: undefined }
                : child
            )
          );
        }
      } else {
        // Check in the child
        const response = await attendanceService.checkIn({
          child_id: selectedChild.id,
          check_in_time: currentTime,
          check_in_by_name: 'Kiosk User', // In production, get actual name
        });

        // Update local state with new attendance ID
        setChildren(prev =>
          prev.map(child =>
            child.id === selectedChild.id
              ? { ...child, is_checked_in: true, attendance_id: response.id }
              : child
          )
        );
      }

      // Close modal
      setShowConfirmModal(false);
      setSelectedChild(null);
    } catch (error: any) {
      console.error('Error checking in/out:', error);
      alert(error.response?.data?.detail || 'Failed to update attendance. Please try again.');
      // Don't close modal on error so user can retry
    }
  };

  const handleExitAttempt = () => {
    setShowExitModal(true);
    setPasscode('');
    setPasscodeError('');
  };

  const handlePasscodeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (passcode === ADMIN_PASSCODE) {
      navigate('/dashboard');
    } else {
      setPasscodeError('Incorrect passcode');
      setPasscode('');
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName[0]}${lastName[0]}`.toUpperCase();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary-900">
                Netta's Bounce Around
              </h1>
              <p className="text-sm text-gray-600 mt-1">Child Check-In/Out Station</p>
            </div>
            <button
              onClick={handleExitAttempt}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Search Bar */}
          <div className="mt-4">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search for a child..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Children Grid */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {filteredChildren.map((child) => (
              <button
                key={child.id}
                onClick={() => handleChildClick(child)}
                className={`
                  relative p-6 rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105
                  ${child.is_checked_in
                    ? 'bg-green-500 text-white'
                    : 'bg-white text-gray-900 hover:shadow-xl'
                  }
                `}
              >
                {/* Status Badge */}
                <div className="absolute top-2 right-2">
                  <div className={`
                    w-3 h-3 rounded-full
                    ${child.is_checked_in ? 'bg-white' : 'bg-gray-300'}
                  `} />
                </div>

                {/* Avatar */}
                <div className={`
                  w-20 h-20 mx-auto rounded-full flex items-center justify-center text-2xl font-bold mb-3
                  ${child.is_checked_in ? 'bg-green-600' : 'bg-primary-500 text-white'}
                `}>
                  {getInitials(child.first_name, child.last_name)}
                </div>

                {/* Name */}
                <div className="text-center">
                  <p className="font-semibold text-lg">{child.first_name}</p>
                  <p className="font-semibold text-lg">{child.last_name}</p>
                  <p className={`text-sm mt-2 ${child.is_checked_in ? 'text-green-100' : 'text-gray-500'}`}>
                    {child.is_checked_in ? 'Checked In' : 'Tap to Check In'}
                  </p>
                </div>
              </button>
              ))}
            </div>
          )}

          {!loading && filteredChildren.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No children found</h3>
              <p className="mt-1 text-sm text-gray-500">Try a different search term.</p>
            </div>
          )}
        </div>
      </main>

      {/* Confirm Check-In/Out Modal */}
      {showConfirmModal && selectedChild && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Confirm {selectedChild.is_checked_in ? 'Check-Out' : 'Check-In'}
              </h3>
              <p className="text-sm text-gray-500 mb-6">
                {selectedChild.is_checked_in ? 'Check out' : 'Check in'}{' '}
                <span className="font-semibold">{selectedChild.first_name} {selectedChild.last_name}</span>?
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowConfirmModal(false);
                    setSelectedChild(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCheckInOut}
                  className={`flex-1 px-4 py-2 rounded-md shadow-sm text-sm font-medium text-white ${
                    selectedChild.is_checked_in
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {selectedChild.is_checked_in ? 'Check Out' : 'Check In'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Exit Passcode Modal */}
      {showExitModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Enter Admin Passcode
                </h3>
                <button
                  onClick={() => setShowExitModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handlePasscodeSubmit}>
                <div className="mb-4">
                  <label htmlFor="passcode" className="block text-sm font-medium text-gray-700 mb-2">
                    Passcode
                  </label>
                  <input
                    type="password"
                    id="passcode"
                    value={passcode}
                    onChange={(e) => {
                      setPasscode(e.target.value);
                      setPasscodeError('');
                    }}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-lg text-center tracking-widest"
                    placeholder="••••"
                    maxLength={4}
                    autoFocus
                  />
                  {passcodeError && (
                    <p className="mt-2 text-sm text-red-600">{passcodeError}</p>
                  )}
                </div>

                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowExitModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                  >
                    Exit Kiosk
                  </button>
                </div>
              </form>

              <p className="mt-4 text-xs text-gray-500 text-center">
                Contact an administrator if you've forgotten the passcode
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
