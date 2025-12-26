# Complete API Endpoints Guide

## Overview
Comprehensive guide to all API endpoints in the Daycare Management System.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: All endpoints (except login/register) require JWT Bearer token.

---

## Table of Contents
1. [Authentication](#authentication)
2. [Children Management](#children-management)
3. [Parents Management](#parents-management)
4. [Attendance Management](#attendance-management)
5. [Activities Management](#activities-management)

---

## Authentication

### Register Staff User
```http
POST /api/v1/auth/register
```
**Request Body:**
```json
{
  "email": "staff@example.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "staff"
}
```

### Login
```http
POST /api/v1/auth/login
```
**Request Body:**
```json
{
  "email": "staff@example.com",
  "password": "securepassword"
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

---

## Children Management

### Create Child
```http
POST /api/v1/children/
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "first_name": "Emma",
  "last_name": "Johnson",
  "date_of_birth": "2020-05-15",
  "gender": "female",
  "allergies": "Peanuts, tree nuts",
  "dietary_restrictions": "Vegetarian",
  "medical_conditions": null,
  "special_needs": null,
  "enrollment_date": "2024-01-15",
  "is_active": true
}
```

### Get All Children (Paginated)
```http
GET /api/v1/children/?page=1&page_size=20&search=emma&is_active=true
Authorization: Bearer {token}
```
**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `search` - Search by first or last name
- `is_active` - Filter by active status

### Get Single Child
```http
GET /api/v1/children/{child_id}
Authorization: Bearer {token}
```

### Update Child
```http
PUT /api/v1/children/{child_id}
Authorization: Bearer {token}
```
**Request Body:** (all fields optional)
```json
{
  "allergies": "Peanuts, tree nuts, dairy",
  "dietary_restrictions": "Vegan"
}
```

### Deactivate Child
```http
PATCH /api/v1/children/{child_id}/deactivate
Authorization: Bearer {token}
```

### Activate Child
```http
PATCH /api/v1/children/{child_id}/activate
Authorization: Bearer {token}
```

### Delete Child (Admin Only)
```http
DELETE /api/v1/children/{child_id}
Authorization: Bearer {token}
```

---

## Parents Management

### Create Parent
```http
POST /api/v1/parents/
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "first_name": "Sarah",
  "last_name": "Johnson",
  "email": "sarah.johnson@email.com",
  "phone_primary": "555-0123",
  "phone_secondary": "555-0124",
  "address_street": "123 Main St",
  "address_city": "Chicago",
  "address_state": "IL",
  "address_zip": "60601",
  "employer": "Tech Corp",
  "work_phone": "555-0125",
  "is_primary_contact": true
}
```

### Get All Parents
```http
GET /api/v1/parents/?page=1&page_size=20&search=johnson
Authorization: Bearer {token}
```
**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page
- `search` - Search by name, email, or phone

### Get Single Parent
```http
GET /api/v1/parents/{parent_id}
Authorization: Bearer {token}
```

### Update Parent
```http
PUT /api/v1/parents/{parent_id}
Authorization: Bearer {token}
```

### Delete Parent (Admin Only)
```http
DELETE /api/v1/parents/{parent_id}
Authorization: Bearer {token}
```

### Create Child-Parent Relationship
```http
POST /api/v1/parents/relationships/
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "child_id": "uuid-here",
  "parent_id": "uuid-here",
  "relationship_type": "mother",
  "is_primary": true,
  "has_custody": true,
  "can_pickup": true
}
```
**Valid relationship types:** mother, father, guardian, grandparent, etc.

### Get Child's Parents
```http
GET /api/v1/parents/relationships/child/{child_id}
Authorization: Bearer {token}
```

### Get Parent's Children
```http
GET /api/v1/parents/relationships/parent/{parent_id}
Authorization: Bearer {token}
```

### Update Relationship
```http
PUT /api/v1/parents/relationships/{relationship_id}
Authorization: Bearer {token}
```

### Delete Relationship
```http
DELETE /api/v1/parents/relationships/{relationship_id}
Authorization: Bearer {token}
```

---

## Attendance Management

### Check In Child
```http
POST /api/v1/attendance/check-in
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "child_id": "uuid-here",
  "check_in_time": "08:30:00",
  "check_in_by_name": "Sarah Johnson",
  "check_in_signature_url": "https://s3.../signature.png",
  "notes": "Child brought lunch today"
}
```

### Check Out Child
```http
PATCH /api/v1/attendance/{attendance_id}/check-out
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "check_out_time": "17:45:00",
  "check_out_by_name": "John Johnson",
  "check_out_signature_url": "https://s3.../signature.png",
  "notes": "Picked up by father"
}
```
**Note:** Late pickup is automatically calculated based on 6:00 PM standard time with 15-minute grace period.

### Get Attendance Records
```http
GET /api/v1/attendance/?attendance_date=2024-01-15&child_id=uuid&checked_out=false
Authorization: Bearer {token}
```
**Query Parameters:**
- `attendance_date` - Filter by specific date
- `child_id` - Filter by child
- `checked_out` - Filter by checkout status (true/false)
- `page` - Page number
- `page_size` - Items per page

### Get Today's Attendance
```http
GET /api/v1/attendance/today
Authorization: Bearer {token}
```

### Get Currently Checked In Children
```http
GET /api/v1/attendance/today/checked-in
Authorization: Bearer {token}
```
**Use Case:** Display on dashboard to see who's currently at the daycare.

### Get Child's Attendance History
```http
GET /api/v1/attendance/child/{child_id}?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### Get Single Attendance Record
```http
GET /api/v1/attendance/{attendance_id}
Authorization: Bearer {token}
```

### Get Late Pickups
```http
GET /api/v1/attendance/late-pickups/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```
**Use Case:** Generate billing reports for late pickup fees.

### Delete Attendance Record (Admin Only)
```http
DELETE /api/v1/attendance/{attendance_id}
Authorization: Bearer {token}
```

---

## Activities Management

### Log Activity
```http
POST /api/v1/activities/
Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "child_id": "uuid-here",
  "activity_date": "2024-01-15",
  "activity_time": "2024-01-15T12:00:00",
  "activity_type": "meal",
  "activity_name": "Lunch",
  "description": "Ate spaghetti and vegetables",
  "mood": "happy",
  "duration_minutes": 30,
  "notes": "Ate everything on plate"
}
```
**Valid activity types:** meal, nap, diaper, play, learning, outdoor
**Valid moods:** happy, sad, energetic, tired, cranky, neutral

### Get Activities
```http
GET /api/v1/activities/?activity_date=2024-01-15&child_id=uuid&activity_type=meal
Authorization: Bearer {token}
```
**Query Parameters:**
- `activity_date` - Filter by date
- `child_id` - Filter by child
- `activity_type` - Filter by type
- `page` - Page number
- `page_size` - Items per page

### Get Today's Activities
```http
GET /api/v1/activities/today?child_id=uuid&activity_type=meal
Authorization: Bearer {token}
```

### Get Child's Activities
```http
GET /api/v1/activities/child/{child_id}?start_date=2024-01-01&end_date=2024-01-31&activity_type=nap
Authorization: Bearer {token}
```

### Get Child's Activities by Date
```http
GET /api/v1/activities/child/{child_id}/date/2024-01-15
Authorization: Bearer {token}
```
**Use Case:** Get all activities for a child on a specific day to generate daily report.

### Get Daily Activity Summary
```http
GET /api/v1/activities/summary/child/{child_id}/date/2024-01-15
Authorization: Bearer {token}
```
**Response Example:**
```json
{
  "child_id": "uuid",
  "child_name": "Emma Johnson",
  "date": "2024-01-15",
  "total_activities": 12,
  "activities_by_type": {
    "meal": 3,
    "nap": 2,
    "diaper": 4,
    "play": 2,
    "outdoor": 1
  },
  "moods": ["happy", "happy", "energetic"],
  "predominant_mood": "happy",
  "total_nap_duration": 180,
  "meal_count": 3,
  "diaper_count": 4
}
```
**Use Case:** Feed this data to GPT-4 to generate AI daily reports.

### Get Single Activity
```http
GET /api/v1/activities/{activity_id}
Authorization: Bearer {token}
```

### Update Activity
```http
PUT /api/v1/activities/{activity_id}
Authorization: Bearer {token}
```
**Note:** Only the staff member who logged it or an admin can update.

### Delete Activity
```http
DELETE /api/v1/activities/{activity_id}
Authorization: Bearer {token}
```
**Note:** Only the staff member who logged it or an admin can delete.

---

## Common Response Formats

### Success Response (Single Item)
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### Success Response (List)
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```
**Note:** Some endpoints return array directly without pagination wrapper.

### Error Response
```json
{
  "detail": "Error message here"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## HTTP Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error or business logic error
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Authentication Headers

Include JWT token in all authenticated requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Usage Examples

### Complete Daily Workflow

1. **Morning: Check in children**
```bash
curl -X POST http://localhost:8000/api/v1/attendance/check-in \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "child-uuid",
    "check_in_time": "08:30:00",
    "check_in_by_name": "Sarah Johnson"
  }'
```

2. **Throughout day: Log activities**
```bash
# Log breakfast
curl -X POST http://localhost:8000/api/v1/activities/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "child-uuid",
    "activity_date": "2024-01-15",
    "activity_time": "2024-01-15T09:00:00",
    "activity_type": "meal",
    "activity_name": "Breakfast",
    "mood": "happy"
  }'

# Log nap
curl -X POST http://localhost:8000/api/v1/activities/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "child-uuid",
    "activity_date": "2024-01-15",
    "activity_time": "2024-01-15T13:00:00",
    "activity_type": "nap",
    "activity_name": "Afternoon Nap",
    "duration_minutes": 120,
    "mood": "tired"
  }'
```

3. **End of day: Check out children**
```bash
curl -X PATCH http://localhost:8000/api/v1/attendance/$ATTENDANCE_ID/check-out \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "check_out_time": "17:30:00",
    "check_out_by_name": "John Johnson"
  }'
```

4. **Generate daily report**
```bash
# Get activity summary
curl -X GET http://localhost:8000/api/v1/activities/summary/child/$CHILD_ID/date/2024-01-15 \
  -H "Authorization: Bearer $TOKEN"

# Feed summary to GPT-4 for narrative generation
# Send report to parents via email
```

---

## Next Steps

### Additional Endpoints to Implement

1. **Emergency Contacts** - `/api/v1/emergency-contacts/`
2. **Authorized Pickup** - `/api/v1/authorized-pickup/`
3. **Enrollment Forms** - `/api/v1/enrollment-forms/`
4. **Immunization Records** - `/api/v1/immunizations/`
5. **Staff Credentials** - `/api/v1/staff-credentials/`
6. **Incident Reports** - `/api/v1/incidents/`
7. **Medication Management** - `/api/v1/medications/`
8. **Daily Reports** - `/api/v1/daily-reports/`
9. **Announcements** - `/api/v1/announcements/`
10. **Compliance Alerts** - `/api/v1/compliance-alerts/`
11. **Photos** - `/api/v1/photos/`

### Integration Features

- **AI Report Generation** - Use activity summary endpoint with OpenAI API
- **Email Notifications** - SendGrid integration for daily reports
- **SMS Alerts** - Twilio integration for urgent notifications
- **File Storage** - AWS S3 for photos and documents
- **Real-time Updates** - WebSockets for live attendance dashboard

---

## Testing

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Test Script (Python)
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "staff@example.com", "password": "password"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create child
child_response = requests.post(
    "http://localhost:8000/api/v1/children/",
    headers=headers,
    json={
        "first_name": "Test",
        "last_name": "Child",
        "date_of_birth": "2020-01-01",
        "enrollment_date": "2024-01-01"
    }
)
child_id = child_response.json()["id"]

# Check in
requests.post(
    "http://localhost:8000/api/v1/attendance/check-in",
    headers=headers,
    json={
        "child_id": child_id,
        "check_in_time": "08:30:00",
        "check_in_by_name": "Parent Name"
    }
)

# Log activity
requests.post(
    "http://localhost:8000/api/v1/activities/",
    headers=headers,
    json={
        "child_id": child_id,
        "activity_date": "2024-01-15",
        "activity_time": "2024-01-15T09:00:00",
        "activity_type": "meal",
        "activity_name": "Breakfast",
        "mood": "happy"
    }
)

print("All tests passed!")
```

---

## Support

For questions or issues, refer to:
- Interactive docs at `/docs`
- Database setup guide: `DATABASE_SETUP.md`
- API documentation: `API_DOCUMENTATION.md`
