# Supabase Database Setup Guide

This guide will help you set up the Supabase database for StudyMate.

## Prerequisites

1. A Supabase account (free tier works fine)
2. A Supabase project created
3. Your Supabase credentials added to Replit Secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (anon/public key)
   - `SUPABASE_SERVICE_KEY` (service role key)

## Step 1: Access Supabase SQL Editor

1. Go to your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New query" to create a new SQL query

## Step 2: Run the Database Schema

1. Open the file `database_schema.sql` in this project
2. Copy the **ENTIRE** contents of that file
3. Paste it into the Supabase SQL Editor
4. Click "Run" button (or press Ctrl+Enter / Cmd+Enter)

The schema will create:
- **profiles** table - User profile information linked to auth.users
- **quizzes** table - Generated quizzes
- **quiz_attempts** table - User quiz attempt history
- **events** table - Calendar events
- **conversations** table - Chat conversation sessions
- **messages** table - Individual chat messages
- **study_sessions** table - Study session tracking

## Step 3: Verify Tables Created

After running the schema:

1. Click on "Table Editor" in the left sidebar
2. You should see all the tables listed:
   - profiles
   - quizzes
   - quiz_attempts
   - events
   - conversations
   - messages
   - study_sessions

## Step 4: Enable Row Level Security (RLS)

The schema automatically enables RLS and creates policies that:
- Users can only access their own data
- Profiles are automatically created when users sign up
- All queries and attempts are linked to the authenticated user

## Step 5: Test Authentication

1. Go back to StudyMate (reload the page if needed)
2. Click "Sign In" or "Sign Up"
3. Create a new account with email and password
4. Upon successful signup, a profile should be automatically created in the `profiles` table

## Troubleshooting

### If signup fails:
1. Check that all three Supabase secrets are set correctly in Replit
2. Verify the database schema was executed without errors
3. Check the Supabase logs in Dashboard → Logs

### If RLS policies block access:
1. Make sure you're using the correct authentication token
2. Verify the user is logged in (check browser console)
3. Check Supabase Dashboard → Authentication to see registered users

### To reset the database:
If you need to start fresh, run this in Supabase SQL Editor:
```sql
DROP TABLE IF EXISTS study_sessions CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS quiz_attempts CASCADE;
DROP TABLE IF EXISTS quizzes CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
```

Then re-run the `database_schema.sql` file.

## What's Next?

After setting up the database:
1. All user data will be stored in Supabase
2. Each user will have their own isolated data
3. Quiz history, events, chats, and analytics will persist
4. Your app is production-ready!

## Notes

- The schema includes automatic timestamps (created_at, updated_at)
- All tables have proper indexes for performance
- RLS policies ensure data security
- Profile data is automatically populated from auth.users
