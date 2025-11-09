# StudyMate - Academic Companion Application

## Overview

StudyMate is a Flask-based web application designed to enhance academic learning through AI-powered features. The application provides students with an intelligent chatbot for questions, quiz generation capabilities, calendar management for events and deadlines, and analytics tracking for study progress. The system leverages OpenRouter's free LLM models, supports RAG (Retrieval-Augmented Generation) for knowledge base queries, web search integration, and advanced reasoning capabilities.

The application uses a modern single-page application (SPA) architecture with component-based frontend design and PostgreSQL database for persistent storage with session-based user identification.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack:**
- Vanilla JavaScript with component-based architecture
- Tailwind CSS for styling with custom nature-inspired theme
- Dynamic HTML component loading system
- No frontend framework dependencies (React, Vue, etc.)

**Design Pattern:**
The frontend follows a modular component structure where each feature (Chat, Quiz, Calendar, Analytics, Profile) is implemented as a separate JavaScript class with its own initialization and state management.

**Theme System:**
A custom "Focused Horizon" nature-inspired color palette is implemented with Deep Teal (#00796B), Soft Lavender (#B0A6C7), and Light Peach (#FFB088) as primary colors.

### Backend Architecture

**Framework:** Flask 3.0.0 with application factory pattern

**Structure:**
- `app/__init__.py`: Application factory with blueprint registration
- `app/routes/`: Blueprint modules for different features (chat, quiz, calendar, analytics, RAG)
- `app/services/`: Business logic and external integrations
- `app/config.py`: Centralized configuration management

**Storage Strategy:**
PostgreSQL database (Replit built-in Neon) for persistent storage with session-based user identification. All features (chat, quiz, calendar, profile, analytics) store data in the database with automatic fallback to in-memory storage when database is unavailable.

**Database Models:**
- `User`: User profiles with name, email, bio, and study preferences
- `ChatMessage`: Conversation history by session
- `Quiz`: Generated quizzes with questions and metadata
- `QuizAttempt`: Quiz results and performance tracking
- `CalendarEvent`: Events, deadlines, and study sessions
- `AnalyticsData`: Study metrics and progress data

**Session Management:**
Flask sessions automatically assign a unique session_id to each user, enabling personalized data storage without explicit authentication.

### LLM Integration

**Service:** OpenRouter API with 100% free models
**Primary Model:** `minimax/minimax-m2:free`
**Fallback Model:** `google/gemini-flash-1.5`

**Advanced Features:**
1. **RAG (Retrieval-Augmented Generation)**: Implemented via `RAGService` using FAISS vector store and HuggingFace embeddings
2. **Web Search**: DuckDuckGo search integration for real-time information retrieval
3. **Reasoning Service**: Multi-layer chain-of-thought processing
4. **LangGraph Integration**: Advanced RAG workflows with state management

### Quiz System

The quiz system supports multiple question types (multiple choice, true/false, fill-in-blank, short answer) with configurable difficulty levels and source materials.

### Chat System

**Capabilities System:**
The chat supports simultaneous multi-modal capabilities:
- RAG (knowledge base search)
- Web search
- Iterative research
- Advanced reasoning/thinking

### Calendar & Analytics

**Calendar:** Event management system with date-based storage
**Analytics:** Real-time dashboard tracking study progress

## External Dependencies

### Core Services

**OpenRouter API**
- Purpose: LLM inference using 100% free models
- Configuration: `OPENROUTER_API_KEY`
- Default Model: `minimax/minimax-m2:free`

### LLM Services

**LangChain Ecosystem**
- `langchain` (>=1.0.0): Core framework
- `langchain-community` (>=0.4.0): Community integrations
- `langchain-openai` (>=1.0.0): OpenRouter integration
- `langgraph` (>=1.0.0): State graph workflows

### Search & Retrieval

**DuckDuckGo Search**
- Library: `duckduckgo-search` (4.1.1)

**Vector Store & Embeddings**
- FAISS: `faiss-cpu` (>=1.7.4)
- HuggingFace: `sentence-transformers` (>=2.2.2)

### Document Processing

**File Format Support**
- PDF: `pypdf` (>=3.17.0)
- Word Documents: `python-docx` (>=1.1.0)
- HTML: `beautifulsoup4` (4.12.2)

### Database

**PostgreSQL**
- Replit built-in Neon PostgreSQL database
- SQLAlchemy ORM (>=2.0.0)
- Connection pooling with scoped sessions
- Automatic migration support

### Supporting Libraries

- `flask-cors` (4.0.0): CORS handling
- `requests` (>=2.32.5): HTTP client
- `python-dotenv` (>=1.0.0): Environment variable management

## Environment Configuration

**Required Environment Variables:**
- `OPENROUTER_API_KEY`: API key for LLM access
- `DATABASE_URL`: PostgreSQL connection string (auto-configured by Replit)

**Optional Configuration:**
- `LLM_URL`: Custom LLM endpoint
- `FLASK_DEBUG`: Debug mode toggle
- `PORT`: Server port (default: 5000)

## Recent Changes

**November 9, 2025 - Dynamic Calendar with Schedule View**
- Implemented dual-view calendar system with toggle between Calendar and Schedule views
- **Calendar View (Grid):**
  - Prominent 2px grid borders for clear date separation
  - Block-style event display with gradient backgrounds
  - Event count badges on dates with scheduled events
  - Increased cell height (120px) for better event visibility
  - Shadow effects on hover for interactivity
  - Shows up to 3 events per day with "+X more" indicator
- **Schedule View (Timeline):**
  - Chronological list of all events organized by day
  - Full event details with time slots visible
  - Today's schedule highlighted with teal accent
  - Each day shows event count and full descriptions
  - Easy-to-scan timeline format for planning
- Dynamic view switching with instant updates
- Calendar layout features:
  - View toggle buttons (Calendar/Schedule) in header
  - Right sidebar with Add Event form, Today's Events, and Upcoming Events
  - Streamlined event management in one view
- Visual improvements:
  - Today highlighted with teal background and border
  - Event blocks with gradient design and left accent border
  - Day numbers displayed as rounded blocks
- Fixed all JavaScript syntax errors and cleaned up codebase
- All calendar navigation buttons working (Previous, Next, Today, AI Suggest)
- Full PostgreSQL backend integration with real-time updates
- Calendar dynamically loads events from database

**November 9, 2025 - Real-Time Dashboard Analytics**
- Completed PostgreSQL database integration across all features
- Implemented real-time dashboard analytics with session-scoped data
- Updated analytics.py to query database for quiz, chat, event, and user metrics
- Replaced all mock/hardcoded dashboard data with live database queries
- Dashboard now displays:
  - Real quiz performance by topic with aggregated scores
  - Recent chat sessions from database
  - Upcoming events from calendar
  - Study streaks and metrics from actual user activity
  - Daily performance trends (last 7 days)
- Fixed analytics bug: quiz_by_type calculation corrected
- All dashboard metrics update dynamically from PostgreSQL data
- Removed Preferences section from profile page
