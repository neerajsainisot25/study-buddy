# Unified AI App

A modular, scalable Flask application combining Chat, Quiz, and Calendar features with AI capabilities.

## Features

- **💬 Advanced Chat**: AI-powered chatbot with multiple modes:
  - **Normal Mode**: Standard conversation
  - **Thinking Mode**: Multi-layer deep reasoning (4 reasoning layers)
  - **Research Mode**: Web search + AI synthesis (using free DuckDuckGo)
  - **RAG Mode**: Knowledge base-powered answers using LangChain & LangGraph
- **📚 RAG System**: Document-based knowledge base with:
  - Document upload (PDF, TXT, DOCX, MD)
  - Vector embeddings (FAISS + HuggingFace)
  - Semantic search
  - LangGraph workflow orchestration
- **🎯 Quiz**: Generate and take quizzes on any topic
- **📅 Calendar**: Event management with AI-powered suggestions

## Project Structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── routes/              # Route blueprints
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat routes
│   │   ├── quiz.py          # Quiz routes
│   │   └── calendar.py      # Calendar routes
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── llm_service.py   # LLM API service
│   │   └── storage.py       # Data storage service
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── helpers.py       # Helper functions
├── static/
│   └── js/                  # Frontend JavaScript modules
│       ├── app.js           # Main app controller
│       ├── chat.js          # Chat module
│       ├── quiz.js          # Quiz module
│       └── calendar.js     # Calendar module
├── main.py                  # Application entry point
├── index.html               # Main HTML template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment (optional):**
   ```bash
   export OPENROUTER_API_KEY="your-api-key"
   export FLASK_DEBUG=True
   export PORT=5001
   export STORAGE_TYPE=memory  # Options: 'memory' or 'file'
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Access the app:**
   Open your browser and navigate to `http://localhost:5001` (or the port shown in terminal)

## Configuration

Configuration is managed in `app/config.py`. You can override settings using environment variables:

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `FLASK_DEBUG`: Enable/disable debug mode (default: True)
- `PORT`: Server port (default: 5001)
- `STORAGE_TYPE`: Storage type - 'memory' or 'file' (default: 'memory')
- `STORAGE_FILE`: File path for file storage (default: 'data/storage.json')

## Architecture

### Backend

- **Modular Routes**: Each feature has its own blueprint in `app/routes/`
- **Service Layer**: Business logic separated into services
  - `LLMService`: Handles all LLM API calls
  - `StorageService`: Manages data persistence
- **Configuration**: Centralized config management
- **Error Handling**: Consistent error responses across all routes

### Frontend

- **Modular JavaScript**: Each feature is a separate class/module
- **Separation of Concerns**: UI logic separated from business logic
- **Reusable Components**: Easy to extend and maintain

## Adding New Features

1. **Create a new route blueprint:**
   ```python
   # app/routes/new_feature.py
   from flask import Blueprint
   new_feature_bp = Blueprint('new_feature', __name__)
   
   @new_feature_bp.route('/endpoint')
   def handler():
       return {"message": "Hello"}
   ```

2. **Register the blueprint in `app/__init__.py`:**
   ```python
   from app.routes import new_feature_bp
   app.register_blueprint(new_feature_bp, url_prefix='/api/new-feature')
   ```

3. **Create a frontend module:**
   ```javascript
   // static/js/new_feature.js
   class NewFeature {
       init() {
           // Initialize feature
       }
   }
   window.NewFeature = NewFeature;
   ```

4. **Add to HTML:**
   - Add tab/button in navigation
   - Include JS file
   - Initialize in app.js

## API Endpoints

### Chat
- `POST /api/chat` - Send a chat message
- `POST /api/chat/clear` - Clear chat history

### Quiz
- `POST /api/quiz/generate` - Generate quiz questions
- `POST /api/quiz/submit` - Submit quiz answers

### Calendar
- `GET /api/calendar/events?date=YYYY-MM-DD` - Get events for a date
- `POST /api/calendar/events` - Add a new event
- `DELETE /api/calendar/events/<date>/<event_id>` - Delete an event
- `POST /api/calendar/suggest` - Get AI event suggestions

## Storage

The app supports multiple storage backends:

- **Memory**: Data stored in memory (lost on restart) - default
- **File**: Data persisted to JSON file

## Development

- **Debug Mode**: Set `FLASK_DEBUG=True` for development
- **Hot Reload**: Flask auto-reloads on code changes in debug mode
- **Error Handling**: All errors return consistent JSON responses

## License

MIT License

