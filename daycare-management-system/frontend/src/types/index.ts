// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

// User Types
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'staff' | 'parent';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Child Types
export interface Child {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender?: string;
  allergies?: string;
  dietary_restrictions?: string;
  medical_conditions?: string;
  special_needs?: string;
  photo_url?: string;
  enrollment_date: string;
  withdrawal_date?: string;
  is_active: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ChildCreate {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender?: string;
  allergies?: string;
  dietary_restrictions?: string;
  medical_conditions?: string;
  special_needs?: string;
  photo_url?: string;
  enrollment_date: string;
  withdrawal_date?: string;
  is_active?: boolean;
}

export interface ChildUpdate {
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  gender?: string;
  allergies?: string;
  dietary_restrictions?: string;
  medical_conditions?: string;
  special_needs?: string;
  photo_url?: string;
  enrollment_date?: string;
  withdrawal_date?: string;
  is_active?: boolean;
}

export interface ChildListResponse {
  children: Child[];
  total: number;
  page: number;
  page_size: number;
}

// Emergency Contact Types
export interface EmergencyContact {
  id: string;
  child_id: string;
  name: string;
  relationship_type: string;
  phone_primary: string;
  phone_secondary?: string;
  priority_order: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContactCreate {
  child_id: string;
  name: string;
  relationship_type: string;
  phone_primary: string;
  phone_secondary?: string;
  priority_order: number;
  notes?: string;
}

// Authorized Pickup Types
export interface AuthorizedPickup {
  id: string;
  child_id: string;
  name: string;
  relationship_type: string;
  phone: string;
  photo_url?: string;
  identification_notes?: string;
  requires_password: boolean;
  password_hint?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthorizedPickupCreate {
  child_id: string;
  name: string;
  relationship_type: string;
  phone: string;
  photo_url?: string;
  identification_notes?: string;
  requires_password?: boolean;
  password_hint?: string;
  is_active?: boolean;
}

// Parent Types
export interface Parent {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone_primary: string;
  phone_secondary?: string;
  address_street?: string;
  address_city?: string;
  address_state?: string;
  address_zip?: string;
  created_at: string;
  updated_at: string;
}

// Attendance Types
export interface Attendance {
  id: string;
  child_id: string;
  attendance_date: string;
  check_in_time: string;
  check_out_time?: string;
  checked_in_by_name: string;
  checked_out_by_name?: string;
  is_late_pickup: boolean;
  late_fee?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Activity Types
export interface Activity {
  id: string;
  child_id: string;
  activity_type: string;
  activity_date: string;
  start_time?: string;
  end_time?: string;
  description?: string;
  mood?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// Compliance Types
export interface ImmunizationRecord {
  id: string;
  child_id: string;
  vaccine_name: string;
  administration_date: string;
  expiration_date?: string;
  provider_name?: string;
  document_url?: string;
  notes?: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface StaffCredential {
  id: string;
  user_id: string;
  credential_type: string;
  credential_number?: string;
  issue_date: string;
  expiration_date?: string;
  document_url?: string;
  is_verified: boolean;
  is_expired: boolean;
  created_at: string;
  updated_at: string;
}

// Incident Report Types
export interface IncidentReport {
  id: string;
  child_id: string;
  incident_type: string;
  incident_date: string;
  incident_time: string;
  description: string;
  injury_type?: string;
  body_part_affected?: string;
  treatment_provided?: string;
  parent_notified: boolean;
  parent_notified_at?: string;
  parent_notification_method?: string;
  dcfs_notification_required: boolean;
  dcfs_notified_at?: string;
  reported_by: string;
  created_at: string;
  updated_at: string;
}

// Medication Types
export interface MedicationAuthorization {
  id: string;
  child_id: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  start_date: string;
  end_date?: string;
  prescribing_doctor?: string;
  parent_signature_url?: string;
  staff_signature_url?: string;
  special_instructions?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MedicationLog {
  id: string;
  authorization_id: string;
  child_id: string;
  administration_date: string;
  administration_time: string;
  dosage_given: string;
  administered_by: string;
  administered_by_signature_url?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// Form State Types
export interface FormErrors {
  [key: string]: string;
}

// Pagination Types
export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
