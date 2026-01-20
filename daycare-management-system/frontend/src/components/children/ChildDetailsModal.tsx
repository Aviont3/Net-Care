import React, { useState, useEffect } from 'react';
import type { Child, Parent, EmergencyContact, AuthorizedPickup } from '@/types';
import { childrenService } from '@/services/childrenService';

interface ChildDetailsModalProps {
  child: Child;
  isOpen: boolean;
  onClose: () => void;
  onEdit: (child: Child) => void;
}

export const ChildDetailsModal: React.FC<ChildDetailsModalProps> = ({
  child,
  isOpen,
  onClose,
  onEdit,
}) => {
  const [parents, setParents] = useState<Parent[]>([]);
  const [emergencyContacts, setEmergencyContacts] = useState<EmergencyContact[]>([]);
  const [authorizedPickups, setAuthorizedPickups] = useState<AuthorizedPickup[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'parents' | 'emergency' | 'authorized'>('overview');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && child) {
      loadRelatedData();
    }
  }, [isOpen, child]);

  const loadRelatedData = async () => {
    setLoading(true);
    try {
      const [parentsData, emergencyData, pickupsData] = await Promise.all([
        childrenService.getChildParents(child.id),
        childrenService.getEmergencyContacts(child.id),
        childrenService.getAuthorizedPickups(child.id),
      ]);
      setParents(parentsData);
      setEmergencyContacts(emergencyData);
      setAuthorizedPickups(pickupsData);
    } catch (err) {
      console.error('Error loading related data:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateAge = (dateOfBirth: string): string => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    if (age < 2) {
      const months = age * 12 + monthDiff;
      return `${months} months old`;
    }

    return `${age} years old`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getInitials = (firstName: string, lastName: string): string => {
    return `${firstName[0]}${lastName[0]}`.toUpperCase();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full mx-4 my-8">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-primary-600 to-primary-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {child.photo_url ? (
                <img
                  src={child.photo_url}
                  alt={`${child.first_name} ${child.last_name}`}
                  className="h-16 w-16 rounded-full object-cover border-2 border-white"
                />
              ) : (
                <div className="h-16 w-16 rounded-full bg-white flex items-center justify-center">
                  <span className="text-primary-600 font-bold text-2xl">
                    {getInitials(child.first_name, child.last_name)}
                  </span>
                </div>
              )}
              <div>
                <h3 className="text-2xl font-bold text-white">
                  {child.first_name} {child.last_name}
                </h3>
                <p className="text-primary-100">
                  {calculateAge(child.date_of_birth)} • Born {formatDate(child.date_of_birth)}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'overview'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('parents')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'parents'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Parents ({parents.length})
            </button>
            <button
              onClick={() => setActiveTab('emergency')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'emergency'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Emergency Contacts ({emergencyContacts.length})
            </button>
            <button
              onClick={() => setActiveTab('authorized')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'authorized'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Authorized Pickups ({authorizedPickups.length})
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="px-6 py-4 max-h-[60vh] overflow-y-auto">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Basic Information */}
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h4>
                <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                    <dd className="mt-1 text-sm text-gray-900">{child.first_name} {child.last_name}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Gender</dt>
                    <dd className="mt-1 text-sm text-gray-900">{child.gender || 'Not specified'}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                    <dd className="mt-1 text-sm text-gray-900">{formatDate(child.date_of_birth)}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Age</dt>
                    <dd className="mt-1 text-sm text-gray-900">{calculateAge(child.date_of_birth)}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Enrollment Date</dt>
                    <dd className="mt-1 text-sm text-gray-900">{formatDate(child.enrollment_date)}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Status</dt>
                    <dd className="mt-1">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        child.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {child.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              {/* Medical Information */}
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">Medical & Dietary Information</h4>
                <div className="space-y-4">
                  {child.allergies && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h5 className="text-sm font-medium text-red-800">Allergies</h5>
                          <p className="mt-1 text-sm text-red-700">{child.allergies}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {child.dietary_restrictions && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h5 className="text-sm font-medium text-green-900">Dietary Restrictions</h5>
                      <p className="mt-1 text-sm text-green-800">{child.dietary_restrictions}</p>
                    </div>
                  )}

                  {child.medical_conditions && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h5 className="text-sm font-medium text-yellow-900">Medical Conditions</h5>
                      <p className="mt-1 text-sm text-yellow-800">{child.medical_conditions}</p>
                    </div>
                  )}

                  {child.special_needs && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h5 className="text-sm font-medium text-blue-900">Special Needs</h5>
                      <p className="mt-1 text-sm text-blue-800">{child.special_needs}</p>
                    </div>
                  )}

                  {!child.allergies && !child.dietary_restrictions && !child.medical_conditions && !child.special_needs && (
                    <p className="text-sm text-gray-500 italic">No medical or dietary information on file</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'parents' && (
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : parents.length > 0 ? (
                parents.map((parent) => (
                  <div key={parent.id} className="border border-gray-200 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">
                      {parent.first_name} {parent.last_name}
                      {parent.is_primary_contact && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                          Primary Contact
                        </span>
                      )}
                    </h5>
                    <dl className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      {parent.email && (
                        <div>
                          <dt className="text-gray-500">Email</dt>
                          <dd className="text-gray-900">{parent.email}</dd>
                        </div>
                      )}
                      <div>
                        <dt className="text-gray-500">Primary Phone</dt>
                        <dd className="text-gray-900">{parent.phone_primary}</dd>
                      </div>
                      {parent.phone_secondary && (
                        <div>
                          <dt className="text-gray-500">Secondary Phone</dt>
                          <dd className="text-gray-900">{parent.phone_secondary}</dd>
                        </div>
                      )}
                      {parent.employer && (
                        <div>
                          <dt className="text-gray-500">Employer</dt>
                          <dd className="text-gray-900">{parent.employer}</dd>
                        </div>
                      )}
                      {parent.address_street && (
                        <div className="md:col-span-2">
                          <dt className="text-gray-500">Address</dt>
                          <dd className="text-gray-900">
                            {parent.address_street}
                            {parent.address_city && `, ${parent.address_city}`}
                            {parent.address_state && `, ${parent.address_state}`}
                            {parent.address_zip && ` ${parent.address_zip}`}
                          </dd>
                        </div>
                      )}
                    </dl>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500">No parent information on file</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'emergency' && (
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : emergencyContacts.length > 0 ? (
                emergencyContacts.map((contact) => (
                  <div key={contact.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">
                          {contact.name}
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                            Priority {contact.priority_order}
                          </span>
                        </h5>
                        <p className="text-sm text-gray-500">{contact.relationship_type}</p>
                      </div>
                    </div>
                    <dl className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div>
                        <dt className="text-gray-500">Primary Phone</dt>
                        <dd className="text-gray-900">{contact.phone_primary}</dd>
                      </div>
                      {contact.phone_secondary && (
                        <div>
                          <dt className="text-gray-500">Secondary Phone</dt>
                          <dd className="text-gray-900">{contact.phone_secondary}</dd>
                        </div>
                      )}
                      {contact.notes && (
                        <div className="md:col-span-2">
                          <dt className="text-gray-500">Notes</dt>
                          <dd className="text-gray-900">{contact.notes}</dd>
                        </div>
                      )}
                    </dl>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500">No emergency contacts on file</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'authorized' && (
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : authorizedPickups.length > 0 ? (
                authorizedPickups.map((pickup) => (
                  <div key={pickup.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900">{pickup.name}</h5>
                        <p className="text-sm text-gray-500">{pickup.relationship_type}</p>
                      </div>
                      {pickup.requires_password && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Password Required
                        </span>
                      )}
                    </div>
                    <dl className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div>
                        <dt className="text-gray-500">Phone</dt>
                        <dd className="text-gray-900">{pickup.phone}</dd>
                      </div>
                      {pickup.identification_notes && (
                        <div className="md:col-span-2">
                          <dt className="text-gray-500">Identification Notes</dt>
                          <dd className="text-gray-900">{pickup.identification_notes}</dd>
                        </div>
                      )}
                      {pickup.password_hint && (
                        <div className="md:col-span-2">
                          <dt className="text-gray-500">Password Hint</dt>
                          <dd className="text-gray-900">{pickup.password_hint}</dd>
                        </div>
                      )}
                    </dl>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500">No authorized pickup persons on file</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Close
          </button>
          <button
            onClick={() => onEdit(child)}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Edit Child
          </button>
        </div>
      </div>
    </div>
  );
};
