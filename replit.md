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
- **OpenRouter API** - LLM provider (using GPT-3.5-turbo)
- **Supabase** (optional) - Database and authentication
- **BeautifulSoup4** - Web scraping
- **DuckDuckGo Search** - Web search integration

### Frontend
- **HTML5/CSS3** - Modern semantic markup and styling
- **Tailwind CSS** - Utility-first CSS framework (via CDN)
- **JavaScript ES6+** - Modern JavaScript
- **"Focused Horizon" Theme** - Minimalist design with professional academic aesthetic

### Design Theme: "Minimal Gradient"

A minimal, modern aesthetic with vibrant gradient accents for an energizing study experience.

**Color Palette:**
- **Pure White** (#FFFFFF) - Primary background for clean, distraction-free interface
- **Deep Black** (#000000) - Primary text color for maximum readability
- **Vibrant Yellow** (#FBBF24) - Gradient start color for energy and focus
- **Fresh Green** (#10B981) - Gradient middle color for growth and balance
- **Bright Blue** (#3B82F6) - Gradient end color for clarity and inspiration
- **Soft Gray** (#F9FAFB) - Subtle backgrounds for cards and sections
- **Medium Gray** (#6B7280) - Secondary text for hierarchy

The theme emphasizes minimalism with strategic use of vibrant yellow-green-blue gradients for visual interest and user engagement. Clean white backgrounds ensure optimal readability while the gradient accents energize the interface.

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

- `OPENROUTER_API_KEY` - **Required for AI features** - OpenRouter API key for LLM access
- `SUPABASE_URL` - (Optional) Supabase project URL
- `SUPABASE_KEY` - (Optional) Supabase anonymous key
- `SUPABASE_SERVICE_KEY` - (Optional) Supabase service role key
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
2. **AI Chat** - Powered by OpenRouter/GPT-3.5
3. **Quiz Generation** - AI-generated quizzes with multiple question types
4. **Calendar** - Event management and scheduling
5. **Analytics** - Performance tracking and metrics
6. **Profile Management** - User settings and preferences

### Optional Features (Require Configuration)
- **Supabase Integration** - For database persistence (configure Supabase keys)
- **RAG/Document Search** - Limited without sentence-transformers (warning shown in logs)
- **Web Search** - DuckDuckGo integration for enhanced chat

## Known Issues & Warnings

1. **Sentence Transformers Warning**: The app shows a warning about missing `sentence-transformers` package. This is expected and doesn't affect core functionality. RAG features will work with limited capability.

2. **Supabase Warning**: If Supabase is not configured, you'll see a warning. This is normal - the app uses in-memory storage as a fallback.

3. **Tailwind CDN Warning**: The browser console shows a warning about using Tailwind via CDN in production. This is for development convenience - for production, consider installing Tailwind locally.

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
- ✅ All API endpoints responding (200 OK)
- ✅ Deployment configured for Autoscale
- ✅ **"Focused Horizon" theme fully implemented** with teal/lavender/peach palette
- ✅ StudyMate logo integrated in sidebar
- ⚠️ RAG features have limited functionality (no local embeddings)

### Recent Changes
- Simplified dependencies to fit Replit disk quota
- Disabled Flask debug mode and reloader for stability
- Configured CORS to allow all origins for Replit iframe proxy
- Updated RAG service to gracefully handle missing dependencies
- **Implemented "Minimal Gradient" theme** (Nov 8, 2025)
  - Complete UI redesign with minimal white/black aesthetic
  - Added vibrant yellow-green-blue gradients for visual energy
  - Ensured maximum readability with pure white backgrounds and black text
  - Gradient accents on banners, active navigation, and progress bars
- **Replaced logo with custom StudyMate branding** (Nov 8, 2025)
  - Integrated uploaded StudyMate logo image
  - Replaced all geometric S² branding
  - Modern SVG icons throughout navigation
- **Removed all hardcoded mock data** (Nov 8, 2025)
  - Dashboard metrics now fetch from `/api/analytics/dashboard`
  - Quiz performance loads from `/api/analytics/quiz`
  - Recent chat sessions display from `/api/chat/history`
  - Upcoming events pull from `/api/calendar/upcoming`
  - Proper empty states when no user data exists
- **Simplified dashboard layout** (Nov 8, 2025)
  - Removed Quick Actions section as requested
  - Cleaner, more focused interface
  - Improved data visualization with real API integration

## Next Steps

To fully utilize all features:

1. **Add OpenRouter API Key** - Required for AI chat and quiz generation
   - Get key from https://openrouter.ai/
   - Add to Replit Secrets as `OPENROUTER_API_KEY`

2. **(Optional) Configure Supabase** - For persistent storage
   - Create a Supabase project
   - Add URL and keys to Replit Secrets

3. **(Optional) Upgrade for Full RAG** - If you need document embeddings
   - Consider using cloud-based embeddings (OpenAI)
   - Or upgrade Replit plan for more disk space

## Support & Documentation

Full documentation is available in the `docs/` folder:
- See `docs/QUICK_REFERENCE.md` for common tasks
- See `docs/COMPLETE_FEATURE_LIST.md` for all features
- See README.md for detailed project information

## Version

- **Version**: 2.1
- **Last Updated**: November 8, 2025
- **Status**: ✅ Running on Replit
