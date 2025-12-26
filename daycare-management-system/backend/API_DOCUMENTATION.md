# API Documentation

## Overview
RESTful API for Netta's Bounce Around Daycare Management System built with FastAPI, PostgreSQL, and SQLAlchemy.

## Base URL
```
Development: http://localhost:8000
API Prefix: /api/v1
```

## Authentication
All endpoints (except `/auth/login` and `/auth/register`) require JWT Bearer token authentication.

### Get Access Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "staff@nettasbounce.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Use Token in Requests
```http
GET /api/v1/children/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

### Authentication (`/auth`)

#### Register New Staff User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "staff@nettasbounce.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Doe",
  "role": "staff"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "staff@nettasbounce.com",
  "password": "securepassword"
}
```

#### Get Current User Info
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

---

### Children Management (`/children`)

#### Create Child
```http
POST /api/v1/children/
Authorization: Bearer <token>
Content-Type: application/json

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

#### Get All Children (Paginated)
```http
GET /api/v1/children/?page=1&page_size=20&search=emma&is_active=true
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (default: 1) - Page number
- `page_size` (default: 20, max: 100) - Items per page
- `search` - Search by first or last name
- `is_active` - Filter by active status (true/false)

**Response:**
```json
{
  "children": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "first_name": "Emma",
      "last_name": "Johnson",
      "date_of_birth": "2020-05-15",
      "gender": "female",
      "allergies": "Peanuts, tree nuts",
      "enrollment_date": "2024-01-15",
      "is_active": true,
      "created_at": "2024-01-10T10:00:00",
      "updated_at": "2024-01-10T10:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

#### Get Single Child
```http
GET /api/v1/children/{child_id}
Authorization: Bearer <token>
```

#### Update Child
```http
PUT /api/v1/children/{child_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "allergies": "Peanuts, tree nuts, dairy",
  "dietary_restrictions": "Vegan"
}
```

#### Deactivate Child (Soft Delete)
```http
PATCH /api/v1/children/{child_id}/deactivate
Authorization: Bearer <token>
```

#### Activate Child
```http
PATCH /api/v1/children/{child_id}/activate
Authorization: Bearer <token>
```

#### Delete Child (Hard Delete - Admin Only)
```http
DELETE /api/v1/children/{child_id}
Authorization: Bearer <token>
```

---

## Pydantic Schemas

### Available Schemas

#### Children & Family
- `ChildCreate`, `ChildUpdate`, `ChildResponse`, `ChildListResponse`
- `ParentCreate`, `ParentUpdate`, `ParentResponse`
- `ChildParentCreate`, `ChildParentUpdate`, `ChildParentResponse`
- `EmergencyContactCreate`, `EmergencyContactUpdate`, `EmergencyContactResponse`
- `AuthorizedPickupCreate`, `AuthorizedPickupUpdate`, `AuthorizedPickupResponse`

#### DCFS Compliance
- `EnrollmentFormCreate`, `EnrollmentFormUpdate`, `EnrollmentFormResponse`
- `ImmunizationRecordCreate`, `ImmunizationRecordUpdate`, `ImmunizationRecordResponse`
- `StaffCredentialCreate`, `StaffCredentialUpdate`, `StaffCredentialResponse`

#### Daily Operations
- `AttendanceCreate`, `AttendanceCheckOut`, `AttendanceResponse`
- `ActivityCreate`, `ActivityUpdate`, `ActivityResponse`
- `PhotoCreate`, `PhotoUpdate`, `PhotoResponse`
- `ChildPhotoCreate`, `ChildPhotoResponse`

#### Health & Safety
- `IncidentReportCreate`, `IncidentReportUpdate`, `IncidentReportResponse`
- `MedicationAuthorizationCreate`, `MedicationAuthorizationUpdate`, `MedicationAuthorizationResponse`
- `MedicationLogCreate`, `MedicationLogUpdate`, `MedicationLogResponse`

#### Parent Communication
- `DailyReportCreate`, `DailyReportUpdate`, `DailyReportResponse`, `DailyReportGenerate`
- `ReportPhotoCreate`, `ReportPhotoResponse`
- `AnnouncementCreate`, `AnnouncementUpdate`, `AnnouncementResponse`
- `ComplianceAlertCreate`, `ComplianceAlertUpdate`, `ComplianceAlertResponse`

## Common Patterns

### Pagination Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

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

## Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting
Currently no rate limiting implemented. Recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per user

## CORS Configuration
Configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000`
- `http://localhost:8000`

Update `BACKEND_CORS_ORIGINS` in `.env` for production domains.

## Interactive API Documentation

### Swagger UI
```
http://localhost:8000/docs
```
Full interactive API documentation with request/response examples and test functionality.

### ReDoc
```
http://localhost:8000/redoc
```
Alternative API documentation with better readability.

## Development Workflow

### 1. Start Development Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Create New Endpoint

**Step 1:** Create route file
```python
# app/api/v1/endpoints/my_endpoint.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_items():
    return {"items": []}
```

**Step 2:** Add to router
```python
# app/api/v1/router.py
from app.api.v1.endpoints import my_endpoint

api_router.include_router(
    my_endpoint.router,
    prefix="/my-endpoint",
    tags=["My Endpoint"]
)
```

### 3. Create Schema

```python
# app/schemas/my_schema.py
from pydantic import BaseModel

class MyItemCreate(BaseModel):
    name: str
    description: str

class MyItemResponse(MyItemCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
```

## Testing

### Manual Testing with cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"staff@nettasbounce.com","password":"password"}'

# Get children (with token)
curl -X GET http://localhost:8000/api/v1/children/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Testing with Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "staff@nettasbounce.com", "password": "password"}
)
token = response.json()["access_token"]

# Get children
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/children/",
    headers=headers
)
print(response.json())
```

## Security Best Practices

1. **Never commit `.env` file** - Contains secrets
2. **Use strong SECRET_KEY** - 32+ random characters
3. **Rotate tokens regularly** - Set appropriate expiration
4. **Validate all inputs** - Pydantic handles this
5. **Use HTTPS in production** - Never send tokens over HTTP
6. **Implement rate limiting** - Prevent abuse
7. **Log security events** - Track authentication failures
8. **Sanitize error messages** - Don't leak sensitive info

## Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for production domains
- [ ] Implement rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Review security headers
- [ ] Test all endpoints
- [ ] Document API versioning strategy

## Future Enhancements

### Planned Features
- WebSocket support for real-time updates
- File upload endpoints (photos, documents)
- Advanced search and filtering
- Bulk operations
- Data export (CSV, PDF)
- Webhook notifications
- API versioning (v2, v3)
- GraphQL endpoint (optional)

### Performance Optimizations
- Redis caching for frequently accessed data
- Database query optimization
- Background task processing (Celery)
- CDN for static files
- Database connection pooling

## Support

For questions or issues:
1. Check the interactive docs at `/docs`
2. Review error messages carefully
3. Check database connection
4. Verify JWT token is valid
5. Ensure all required fields are provided
