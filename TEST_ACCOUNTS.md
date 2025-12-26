# Test Accounts for Netta's Bounce Around Daycare Management System

## Available Test Accounts

These accounts have been pre-configured in the database for testing purposes.

### 1. Admin Account
- **Email**: `admin@nettas.com`
- **Password**: `admin123`
- **Role**: `admin`
- **Name**: Admin User
- **Permissions**: Full access to all features including compliance management

### 2. Staff Account
- **Email**: `staff@nettas.com`
- **Password**: `staff123`
- **Role**: `staff`
- **Name**: Sarah Staff
- **Permissions**: Can manage children, attendance, and activities

### 3. Parent Account
- **Email**: `parent@nettas.com`
- **Password**: `parent123`
- **Role**: `parent`
- **Name**: Paula Parent
- **Permissions**: Can view their own children's information

## How to Use

### Login via Frontend
1. Navigate to [http://localhost:5173](http://localhost:5173)
2. Click on the login page (or you'll be redirected automatically)
3. Enter one of the test account credentials above
4. You'll be redirected to the dashboard

### Login via API
```bash
# Example: Admin login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nettas.com","password":"admin123"}'
```

This will return an access token that you can use for authenticated requests:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Making Authenticated Requests
```bash
# Use the token in the Authorization header
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Testing Different Roles

### As Admin:
- Full access to all endpoints
- Can manage compliance records
- Can view all children and activities
- Can manage staff credentials

### As Staff:
- Can manage children records
- Can record attendance
- Can log activities
- Cannot access compliance endpoints

### As Parent:
- Can view their own children
- Can view activities for their children
- Limited access compared to staff

## Registering New Accounts

You can create new test accounts using the registration endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "staff"
  }'
```

Or use the frontend registration page at [http://localhost:5173/register](http://localhost:5173/register)

## Security Notes

⚠️ **Important**: These are test accounts for development purposes only.

- Change all default passwords before deploying to production
- Implement additional security measures for production (email verification, password complexity requirements, etc.)
- Consider implementing admin-only registration for production environments
- These passwords are intentionally simple for testing and should never be used in production

## Next Steps

1. Try logging in with each account to test role-based access
2. Explore the different UI elements available to each role
3. Test the API endpoints with different roles
4. Create child records, attendance logs, and activities as staff/admin
5. View data as a parent to see the limited access

## Troubleshooting

If you can't log in:
- Make sure both backend ([http://localhost:8000](http://localhost:8000)) and frontend ([http://localhost:5173](http://localhost:5173)) are running
- Check the browser console for errors
- Verify the password is exactly as shown (case-sensitive)
- Try clearing your browser's localStorage and cookies

## Database Reset

If you need to reset the test data:

```bash
cd daycare-management-system/backend
.venv/Scripts/python -m alembic downgrade base
.venv/Scripts/python -m alembic upgrade head
```

Then recreate the test accounts by running the registration script again.
