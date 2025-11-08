# Authentication Flow Documentation

## Overview

StudyMate now uses a **centralized authentication system** where users must authenticate ONCE before accessing any features. This replaces the previous per-feature authentication checks.

## How It Works

### 1. Page Load
When the user first loads the application:

```
1. Page loads → auth.js initializes → AuthManager created
2. Components load (sidebar, modals, etc.)
3. ✅ CRITICAL CHECK: authManager.checkAuthAndEnforce() called
4. If NOT authenticated:
   - Hide all app content (.main-content display: none)
   - Show auth modal (login/signup form)
   - Stop - don't initialize any features
5. If authenticated:
   - Show all app content
   - Initialize all features (dashboard, chat, quiz, calendar, analytics, profile)
```

### 2. User Signs Up or Logs In

```
1. User enters email/password in auth modal
2. API call to /api/auth/signup or /api/auth/login
3. On success:
   - Save session to localStorage (JWT token, user data)
   - Call authManager.showAppContent()
     → Show main app content
     → Hide auth modal
     → Initialize ALL features
4. User can now access everything!
```

### 3. User Logs Out

```
1. User clicks "Logout" button in sidebar
2. authManager.logout() called
3. API call to /api/auth/logout
4. Clear session from localStorage
5. Call authManager.showLoginRequired()
   → Hide app content
   → Show auth modal
6. User must sign in again to access features
```

## Key Files

### Frontend
- `static/js/auth.js` - AuthManager class, handles all authentication logic
- `index.html` - Global auth check on page load (line 162-166)
- All feature files NO LONGER have individual auth checks

### Backend
- `app/routes/auth.py` - Authentication endpoints (signup, login, logout, profile)
- `app/middleware/auth.py` - Middleware to protect API routes
- `app/services/supabase_service.py` - Supabase authentication service

## Authentication Flow Diagram

```
┌─────────────────┐
│  User visits    │
│  StudyMate      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Auth      │◄─── Centralized check
│ Token Exists?   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ▼         ▼
┌─────┐   ┌──────┐
│Show │   │ Show │
│ App │   │Login │
└──┬──┘   │Modal │
   │      └───┬──┘
   │          │
   │          ▼
   │      ┌──────┐
   │      │User  │
   │      │Signs │
   │      │  In  │
   │      └───┬──┘
   │          │
   │          ▼
   │      ┌──────┐
   │      │Save  │
   │      │Token │
   │      └───┬──┘
   │          │
   └──────────┘
         │
         ▼
   ┌──────────┐
   │  Access  │
   │   All    │
   │Features  │
   └──────────┘
```

## Benefits of Centralized Authentication

1. **Single Sign-On** - User logs in once, accesses everything
2. **Cleaner Code** - No repeated auth checks in every feature file
3. **Better UX** - No confusing "Sign In" buttons on every page
4. **Easier Maintenance** - Auth logic in one place
5. **More Secure** - Consistent auth enforcement

## Testing the Flow

### Test 1: New User
1. Open StudyMate in incognito window
2. Should see: Login modal, NO app content visible
3. Sign up with email/password
4. Should see: Login modal disappears, full app shows
5. Can navigate to all features (dashboard, chat, quiz, calendar, analytics, profile)

### Test 2: Returning User
1. Open StudyMate (with existing session)
2. Should see: Immediately see app, NO login modal
3. Can access all features

### Test 3: Logout
1. While logged in, click "Logout" in sidebar
2. Should see: App content hidden, login modal appears
3. Must sign in again to use app

## Important Notes

- **Session Persistence**: JWT token stored in localStorage, persists across page reloads
- **Automatic Redirect**: No manual redirect needed, just show/hide content
- **Backend Protection**: All API endpoints still verify JWT token
- **Row-Level Security**: Supabase policies ensure users only see their own data
