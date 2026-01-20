# Login to Admin Dashboard Navigation Flow

## Complete Authentication & Navigation Flow

### 🔐 Login Process

#### Step-by-Step Flow:

1. **User Visits App** → Redirected to `/login`
   - If not authenticated, ProtectedRoute redirects to login page
   - Login page displays at `http://localhost:5173/login`

2. **User Enters Credentials**
   - Email: `admin@nettas.com`
   - Password: `admin123`
   - Form validation runs (email format, required fields)

3. **Form Submission** → `LoginPage.tsx` (line 46-70)
   ```typescript
   const handleSubmit = async (e: React.FormEvent) => {
     e.preventDefault();

     if (!validateForm()) {
       return;
     }

     setLoading(true);
     setApiError('');

     try {
       await login(formData);  // Calls AuthContext.login()

       // Redirect to dashboard
       const from = (location.state as any)?.from?.pathname || '/dashboard';
       navigate(from, { replace: true });
     } catch (error: any) {
       setApiError(error.response?.data?.detail || 'Login failed');
     } finally {
       setLoading(false);
     }
   };
   ```

4. **AuthContext.login()** → `AuthContext.tsx` (line 49-60)
   ```typescript
   const login = async (credentials: LoginRequest) => {
     setLoading(true);
     try {
       await authService.login(credentials);    // Step 5
       const currentUser = await authService.getCurrentUser();  // Step 6
       setUser(currentUser);  // Updates global user state
     } catch (error) {
       setLoading(false);
       throw error;
     }
     setLoading(false);
   };
   ```

5. **authService.login()** → `authService.ts` (line 6-23)
   ```typescript
   async login(credentials: LoginRequest): Promise<AuthResponse> {
     const formData = new FormData();
     formData.append('username', credentials.username);
     formData.append('password', credentials.password);

     // POST to backend API
     const response = await api.post<AuthResponse>('/api/v1/auth/login', formData, {
       headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
     });

     // Store JWT token in localStorage
     if (response.data.access_token) {
       localStorage.setItem('access_token', response.data.access_token);
     }

     return response.data;
   }
   ```

6. **authService.getCurrentUser()** → `authService.ts` (line 32-41)
   ```typescript
   async getCurrentUser(): Promise<User> {
     // GET with Authorization header (token added by api interceptor)
     const response = await api.get<User>('/api/v1/auth/me');

     // Store user data in localStorage
     if (response.data) {
       localStorage.setItem('user', JSON.stringify(response.data));
     }

     return response.data;
   }
   ```

7. **Navigation** → React Router navigates to `/dashboard`

8. **Dashboard Loads** → `AdminDashboard.tsx`
   - ProtectedRoute checks authentication
   - User is authenticated, so dashboard renders
   - AdminLayout wraps the dashboard content
   - AdminSidebar displays with user profile and navigation

### 📡 API Calls Made During Login

#### 1. Login Request
```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@nettas.com&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Get Current User Request
```http
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "admin@nettas.com",
  "first_name": "Admin",
  "last_name": "User",
  "role": "admin",
  "is_active": true
}
```

### 🗂️ localStorage State After Login

After successful login, localStorage contains:

```javascript
localStorage.getItem('access_token')
// "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

localStorage.getItem('user')
// '{"id":"...","email":"admin@nettas.com","first_name":"Admin","last_name":"User","role":"admin","is_active":true}'
```

### 🎯 Protected Route Behavior

The ProtectedRoute component checks authentication:

```typescript
// ProtectedRoute.tsx
if (loading) {
  return <LoadingSpinner />;
}

if (!user) {
  // Not authenticated → redirect to login
  return <Navigate to="/login" state={{ from: location }} replace />;
}

if (requiredRole && user.role !== requiredRole) {
  // Wrong role → redirect to dashboard
  return <Navigate to="/dashboard" replace />;
}

// Authenticated and authorized → render children
return <>{children}</>;
```

### 🖥️ Admin Dashboard Features After Login

Once logged in, the admin sees:

1. **Left Sidebar** (AdminSidebar.tsx)
   - Logo: "Netta's" with "N" icon
   - User profile: Initials badge + name + role
   - Navigation menu (10 items for admin)
   - Logout button

2. **Top Header** (AdminLayout.tsx)
   - Mobile menu toggle (hamburger)
   - Notification bell icon
   - User badge (desktop)

3. **Dashboard Content** (AdminDashboard.tsx)
   - Welcome message: "Welcome back, Admin!"
   - 4 statistic cards
   - 4 quick action cards
   - Recent activity feed
   - Upcoming tasks list
   - Compliance overview (admin only)

### 🔄 Session Persistence

When the user refreshes the page:

1. **App loads** → AuthProvider runs useEffect
2. **Checks localStorage** for access_token
3. **If token exists** → calls `authService.getCurrentUser()`
4. **Sets user state** from API response
5. **User stays logged in** and sees dashboard

```typescript
// AuthContext.tsx - runs on app load
useEffect(() => {
  const initAuth = async () => {
    if (authService.isAuthenticated()) {  // Checks localStorage
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);  // Restores user state
      } catch (error) {
        console.error('Failed to fetch user:', error);
        authService.logout();  // Token invalid, logout
      }
    }
    setLoading(false);
  };

  initAuth();
}, []);
```

### 🚪 Logout Flow

When user clicks logout:

1. **Click logout button** in sidebar
2. **authService.logout()** is called
3. **Clears localStorage** (access_token and user)
4. **Redirects to** `/login`
5. **User sees login page**

### 🔐 Token Management

The Axios interceptor automatically adds the token to all API requests:

```typescript
// api.ts - request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

And handles 401 errors (invalid/expired tokens):

```typescript
// api.ts - response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

## Testing the Flow

### 1. Start Both Servers

```bash
# Terminal 1 - Backend
cd daycare-management-system/backend
.venv/Scripts/python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd daycare-management-system/frontend
npm run dev
```

### 2. Open Browser

Navigate to: `http://localhost:5173`

### 3. Login with Test Account

- **Email**: admin@nettas.com
- **Password**: admin123

### 4. Verify Navigation

- Should redirect to `/dashboard`
- Should see admin sidebar with all menu items
- Should see "Welcome back, Admin!" on dashboard
- Should see user initials "AU" in profile badges

### 5. Test Role-Based Access

- Try clicking "Compliance" → should work (admin only)
- Try clicking "Settings" → should work (admin only)
- Logout and login as staff to see restricted access

## File References

**Authentication Files:**
- `frontend/src/pages/LoginPage.tsx` - Login UI and form handling
- `frontend/src/context/AuthContext.tsx` - Global auth state management
- `frontend/src/services/authService.ts` - API calls for authentication
- `frontend/src/services/api.ts` - Axios instance with interceptors
- `frontend/src/components/auth/ProtectedRoute.tsx` - Route protection

**Layout Files:**
- `frontend/src/components/layout/AdminLayout.tsx` - Main layout wrapper
- `frontend/src/components/layout/AdminSidebar.tsx` - Navigation sidebar
- `frontend/src/pages/AdminDashboard.tsx` - Dashboard page

**Routing:**
- `frontend/src/App.tsx` - Route configuration

## Troubleshooting

### Login not working?
1. Check backend is running: `http://localhost:8000/docs`
2. Check frontend dev server: `http://localhost:5173`
3. Open browser console for errors
4. Verify network tab shows API calls

### Not redirecting to dashboard?
1. Check console for errors
2. Verify token is stored: `localStorage.getItem('access_token')`
3. Check ProtectedRoute is working
4. Verify App.tsx has correct route configuration

### Sidebar not showing?
1. Verify you're using AdminDashboard (not old DashboardPage)
2. Check AdminLayout is wrapping content
3. Inspect browser for CSS/Tailwind issues

---

**Last Updated**: December 26, 2025
**Flow Status**: ✅ Fully Functional
