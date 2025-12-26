# Netta's Bounce Around - Frontend

React + TypeScript + Vite frontend for the Daycare Management System.

## Features

- **Authentication**: Login and registration pages with form validation
- **Protected Routes**: Role-based access control (admin, staff, parent)
- **Responsive Design**: Built with Tailwind CSS
- **Type Safety**: Full TypeScript support
- **API Integration**: Axios with interceptors for authentication

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS 3.4
- React Router DOM v6
- Axios

## Getting Started

### Prerequisites

- Node.js 20+
- npm

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at [http://localhost:5173](http://localhost:5173)

The Vite dev server proxies API requests to the backend at `http://localhost:8000`

### Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── auth/          # Authentication components
│   │   └── ProtectedRoute.tsx
│   ├── layout/        # Layout components
│   │   └── DashboardLayout.tsx
│   └── common/        # Reusable components
├── pages/             # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   └── DashboardPage.tsx
├── services/          # API services
│   ├── api.ts         # Axios instance with interceptors
│   └── authService.ts # Authentication service
├── context/           # React context
│   └── AuthContext.tsx
├── types/             # TypeScript type definitions
│   └── index.ts
├── utils/             # Utility functions
├── hooks/             # Custom React hooks
├── App.tsx            # Main app component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Available Routes

- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/` - Redirects to dashboard

## Environment Variables

The Vite proxy is configured to forward `/api` requests to `http://localhost:8000`.

## Authentication Flow

1. User logs in via LoginPage
2. Credentials sent to backend `/api/v1/auth/login`
3. Access token stored in localStorage
4. AuthContext updates with user data
5. Axios interceptor adds token to all requests
6. Protected routes check authentication status
7. Unauthorized requests redirect to login

## Role-Based Access

- **Parent**: Can view their children's information
- **Staff**: Can manage children, attendance, and activities
- **Admin**: Full access to all features including compliance

## Custom Utility Classes

Tailwind utilities defined in index.css:

- `.btn` - Base button styles
- `.btn-primary` - Primary button (blue)
- `.btn-secondary` - Secondary button (gray)
- `.input` - Input field styles
- `.card` - Card container
- `.badge-*` - Status badges

## API Integration

All API calls go through the Axios instance in `src/services/api.ts` which:

- Adds authentication token to requests
- Handles 401 errors (redirects to login)
- Handles other error responses
- Provides consistent error handling

## Next Steps

To extend the application:

1. Create additional pages (Children, Attendance, Activities, etc.)
2. Add more layout components (Sidebar, Footer)
3. Implement data fetching hooks
4. Add forms for creating/editing records
5. Add data tables for listing records
6. Implement real-time notifications
