# AI Assistant - Academic Dashboard

## Project Overview

A modern, feature-rich academic assistant application with AI-powered features including:
- AI chatbot with RAG (Retrieval-Augmented Generation) support
- Quiz generation and management
- Calendar and event management
- Analytics and performance tracking
- File upload and document processing

## Tech Stack

### Backend
- **Flask 3.0.0** - Python web framework
- **LangChain** - AI/LLM integration framework
- **LangGraph** - Advanced AI workflow orchestration
- **OpenRouter API** - LLM provider (using FREE models: minimax-m2 with Google Gemini Flash 1.5 fallback)
- **Supabase** (optional) - Database backend (not required for core features)
- **BeautifulSoup4** - Web scraping
- **DuckDuckGo Search** - Web search integration

### Frontend
- **HTML5/CSS3** - Modern semantic markup and styling
- **Tailwind CSS** - Utility-first CSS framework (via CDN)
- **JavaScript ES6+** - Modern JavaScript
- **"Focused Horizon" Theme** - Minimalist design with professional academic aesthetic

### Design Theme: "Focused Horizon"

A balanced theme combining academic focus with supportive study companion vibes.

**Color Palette:**
- **Deep Teal** (#00796B) - Primary color representing wisdom, stability, and concentration
- **Soft Lavender** (#B0A6C7) - Secondary accent for imagination and elegant touches
- **Peach Gradient** (#FFB088-#FFCCB3) - Accent color for warmth, enthusiasm, and creativity
- **Warm Cream** (#F5F5DC) - Background providing clean, inviting, low-strain reading
- **Charcoal** (#36454F) - Text color offering strong contrast without harshness

The theme emphasizes clean lines, generous whitespace, and a calming yet stimulating atmosphere perfect for focused study.

## Project Structure

```
/
├── app/                      # Flask application
│   ├── routes/              # API endpoints (chat, quiz, calendar, analytics, RAG)
│   ├── services/            # Business logic (LLM, RAG, storage, web search)
│   ├── utils/               # Helper functions
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   └── extensions.py        # Flask extensions
├── static/                  # Frontend assets
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript modules
├── templates/               # HTML templates
│   ├── components/         # Reusable components (sidebar, modals)
│   └── pages/              # Page templates
├── docs/                    # Documentation
├── data/                    # Runtime data (storage, uploads)
├── main.py                  # Application entry point
├── requirements-minimal.txt # Python dependencies (optimized for Replit)
└── index.html              # Main entry page
```

## Setup and Configuration

### Environment Variables

The application uses the following environment variables (configure via Replit Secrets):

- `OPENROUTER_API_KEY` - **Required** - OpenRouter API key for AI chat and quiz generation (uses FREE models: minimax-m2 and Google Gemini Flash 1.5)
- `SUPABASE_URL` - **Optional** - Supabase project URL (not required for core features)
- `SUPABASE_KEY` - **Optional** - Supabase anonymous key (not required for core features)
- `SUPABASE_SERVICE_KEY` - **Optional** - Supabase service role key (not required for core features)
- `PORT` - Server port (default: 5000)
- `FLASK_DEBUG` - Debug mode (default: False for production)
- `STORAGE_TYPE` - Storage backend: 'memory' or 'file' (default: memory)

### Running Locally

The application is already configured to run via the "Flask App" workflow on port 5000.

### Dependencies

The project uses `requirements-minimal.txt` which excludes heavy dependencies like PyTorch and sentence-transformers to fit within Replit's disk quota. This means:

- ✅ Core features work: Chat, Quiz, Calendar, Analytics
- ⚠️ RAG features are limited without sentence-transformers embeddings
- To enable full RAG support with local embeddings, you would need to upgrade the Replit plan or use cloud-based embeddings

## Features

### Core Features (Currently Working)
1. **Dashboard** - Overview with metrics and quick actions
2. **AI Chat** - Powered by OpenRouter with FREE models (no login required)
3. **Quiz Generation** - AI-generated quizzes with multiple question types (no login required)
4. **Calendar** - Event management and scheduling (no login required)
5. **Analytics** - Performance tracking and metrics (no login required)
6. **Profile Management** - User settings and preferences (no login required)

### Advanced Features
- **RAG/Document Search** - Available but limited without sentence-transformers (requires more disk space)
- **Web Search** - DuckDuckGo integration for enhanced chat responses
- **OpenRouter Fallback** - Automatic fallback to free Google Gemini Flash 1.5 model if primary fails

## Known Issues & Warnings

1. **Sentence Transformers Warning**: The app shows a warning about missing `sentence-transformers` package. This is expected and doesn't affect core functionality. RAG features will work with limited capability.

2. **No Authentication Required**: The app is now fully open access - users can use all features without signing up or logging in.

3. **Supabase Optional**: Supabase database is optional and not required for core features to work.

4. **Tailwind CDN Warning**: The browser console shows a warning about using Tailwind via CDN in production. This is for development convenience - for production, consider installing Tailwind locally.

## API Endpoints

All API endpoints are prefixed with `/api/`:

- `/api/chat/` - Chat functionality
- `/api/quiz/` - Quiz management
- `/api/calendar/` - Calendar and events
- `/api/analytics/` - Analytics data
- `/api/rag/` - RAG (document search) features
- `/health` - Health check endpoint

## Deployment

The project is configured for Replit Autoscale deployment:
- Automatically scales based on traffic
- Uses the same `python main.py` command
- Port 5000 is automatically exposed

To deploy:
1. Ensure `OPENROUTER_API_KEY` is set in Secrets
2. Click the "Deploy" button in Replit
3. The app will be available at your Replit deployment URL

## Development Notes

### Current State (Nov 8, 2025)
- ✅ All Python dependencies installed (minimal set)
- ✅ Flask app running on port 5000
- ✅ CORS configured for Replit proxy
- ✅ Workflow configured and running
- ✅ **No authentication required** - All features fully accessible without login
- ✅ **Open access** - Users can start using the app immediately
- ✅ **Simplified logo** - "StudyMate" in teal without geometric design or subtitle
- ✅ **OpenRouter with 100% free models** - minimax-m2 and Google Gemini Flash 1.5
- ✅ **"Focused Horizon" theme** - Fully implemented with teal/lavender/peach palette
- ✅ Deployment configured for Autoscale
- ⚠️ RAG features have limited functionality (no local embeddings)

### Recent Changes

**Authentication Removal** (Nov 8, 2025)
- ✅ **Removed all authentication** - App is now fully open access without login requirement
- ✅ **Removed @require_auth decorators** - All API routes (quiz, calendar, analytics) are now public
- ✅ **Replaced authManager.apiCall() with fetch()** - All frontend calls now use standard fetch
- ✅ **Hidden auth modal** - Users no longer see login/signup prompts
- ✅ **Removed user profile display** - Sidebar no longer shows user info

**Logo Redesign** (Nov 8, 2025)
- ✅ **Simplified logo** - "StudyMate" text in teal color (#00796B)
- ✅ **Removed geometric design** - No more S² square graphic
- ✅ **Removed subtitle** - Clean single-line logo without "Academic Excellence"
- ✅ **Enhanced visibility** - Clear, readable logo in sidebar

**OpenRouter Integration** (Nov 8, 2025)
- ✅ **100% FREE models** - Uses minimax-m2:free as primary, Google Gemini Flash 1.5 as fallback
- ✅ **No cost AI** - Chat and quiz generation completely free with OpenRouter
- ✅ **Robust error handling** - Automatic fallback ensures chat always works
- ✅ **Streaming support** - Real-time chat responses with SSE

**Previous Changes**
- Simplified dependencies to fit Replit disk quota
- Disabled Flask debug mode and reloader for stability
- Configured CORS to allow all origins for Replit iframe proxy
- Updated RAG service to gracefully handle missing dependencies
- Implemented "Focused Horizon" theme with teal/lavender/peach palette
- Replaced emoji icons with modern SVG icons throughout navigation
- Enhanced welcome banner with teal gradient and white typography

## Setup Instructions

### Required Setup

1. **Add OpenRouter API Key** (REQUIRED)
   - Get **FREE** key from https://openrouter.ai/
   - Add to Replit Secrets as `OPENROUTER_API_KEY`
   - **Uses 100% FREE models** - No costs for chat or quiz generation!
   - Primary: minimax/minimax-m2:free
   - Fallback: google/gemini-flash-1.5 (also free)

### Optional Enhancements

2. **(Optional) Set up Supabase** - For user data persistence
   - Create a Supabase project at https://supabase.com
   - Add credentials to Replit Secrets (see above)
   - Run the database schema if needed

3. **(Optional) Upgrade for Full RAG** - For advanced document search
   - Consider using cloud-based embeddings (OpenAI)
   - Or upgrade Replit plan for more disk space to install sentence-transformers

## Support & Documentation

Full documentation is available in the `docs/` folder:
- See `docs/QUICK_REFERENCE.md` for common tasks
- See `docs/COMPLETE_FEATURE_LIST.md` for all features
- See README.md for detailed project information

## Version

- **Version**: 2.1
- **Last Updated**: November 8, 2025
- **Status**: ✅ Running on Replit
