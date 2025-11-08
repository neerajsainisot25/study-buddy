-- ============================================================================
-- Supabase Database Schema
-- Complete schema for Chat, Quiz, Calendar, and RAG functionality
-- Includes pgvector support with IVFFLAT indexing (dimension: 1536)
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable pg_trgm extension for text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- CHAT TABLES
-- ============================================================================

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- QUIZ TABLES
-- ============================================================================

-- Quizzes table (quiz definitions)
CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    topic TEXT NOT NULL,
    topics TEXT[], -- Array of topics for multi-topic quizzes
    quiz_type TEXT NOT NULL CHECK (quiz_type IN ('multiple_choice', 'true_false', 'fill_blank', 'short_answer')),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    source_material TEXT CHECK (source_material IN ('general', 'knowledge_base', 'web_search')),
    num_questions INTEGER NOT NULL CHECK (num_questions > 0 AND num_questions <= 20),
    questions JSONB NOT NULL, -- Store full question data as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quiz attempts table (quiz results)
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    correct INTEGER NOT NULL CHECK (correct >= 0),
    total INTEGER NOT NULL CHECK (total > 0),
    time_taken INTEGER NOT NULL DEFAULT 0, -- Time in seconds
    answers JSONB NOT NULL, -- Store user answers and results
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CALENDAR TABLES
-- ============================================================================

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    time TIME,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- RAG TABLES
-- ============================================================================

-- RAG documents table (document metadata)
CREATE TABLE IF NOT EXISTS rag_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    filename TEXT NOT NULL,
    title TEXT,
    file_type TEXT NOT NULL CHECK (file_type IN ('txt', 'pdf', 'docx', 'md')),
    file_size BIGINT NOT NULL, -- Size in bytes
    content_hash TEXT, -- Hash of content for deduplication
    metadata JSONB DEFAULT '{}',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RAG chunks table (document chunks with embeddings)
CREATE TABLE IF NOT EXISTS rag_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    document_id UUID NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order of chunk in document
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL, -- pgvector embedding with dimension 1536
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Chat indexes
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Quiz indexes
CREATE INDEX IF NOT EXISTS idx_quizzes_user_id ON quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_created_at ON quizzes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quizzes_topic_trgm ON quizzes USING GIN(topic gin_trgm_ops); -- For text search (requires pg_trgm)
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_quiz_id ON quiz_attempts(quiz_id);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_completed_at ON quiz_attempts(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_score ON quiz_attempts(score);

-- Calendar indexes
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_user_date ON events(user_id, date);

-- RAG indexes
CREATE INDEX IF NOT EXISTS idx_rag_documents_user_id ON rag_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_rag_documents_filename ON rag_documents(filename);
CREATE INDEX IF NOT EXISTS idx_rag_documents_uploaded_at ON rag_documents(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_document_id ON rag_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_user_id ON rag_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_chunk_index ON rag_chunks(document_id, chunk_index);

-- Vector similarity search index (IVFFLAT)
-- Note: IVFFLAT works best when created after data exists.
-- If table is empty, index will be created but should be recreated after loading data
-- for optimal performance. Lists parameter: sqrt(total_rows) is recommended.
-- For now using 100 as default; recreate with calculated lists after data load.
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding_ivfflat 
    ON rag_chunks 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES - CONVERSATIONS
-- ============================================================================

-- Drop existing policies if they exist (for idempotency)
DROP POLICY IF EXISTS "Users can view their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can insert their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can update their own conversations" ON conversations;
DROP POLICY IF EXISTS "Users can delete their own conversations" ON conversations;

CREATE POLICY "Users can view their own conversations"
    ON conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own conversations"
    ON conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own conversations"
    ON conversations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own conversations"
    ON conversations FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES - MESSAGES
-- ============================================================================

DROP POLICY IF EXISTS "Users can view their own messages" ON messages;
DROP POLICY IF EXISTS "Users can insert their own messages" ON messages;
DROP POLICY IF EXISTS "Users can update their own messages" ON messages;
DROP POLICY IF EXISTS "Users can delete their own messages" ON messages;

CREATE POLICY "Users can view their own messages"
    ON messages FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own messages"
    ON messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own messages"
    ON messages FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own messages"
    ON messages FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES - QUIZZES
-- ============================================================================

DROP POLICY IF EXISTS "Users can view their own quizzes" ON quizzes;
DROP POLICY IF EXISTS "Users can insert their own quizzes" ON quizzes;
DROP POLICY IF EXISTS "Users can update their own quizzes" ON quizzes;
DROP POLICY IF EXISTS "Users can delete their own quizzes" ON quizzes;

CREATE POLICY "Users can view their own quizzes"
    ON quizzes FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own quizzes"
    ON quizzes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own quizzes"
    ON quizzes FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own quizzes"
    ON quizzes FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES - QUIZ ATTEMPTS
-- ============================================================================

DROP POLICY IF EXISTS "Users can view their own quiz attempts" ON quiz_attempts;
DROP POLICY IF EXISTS "Users can insert their own quiz attempts" ON quiz_attempts;
DROP POLICY IF EXISTS "Users can update their own quiz attempts" ON quiz_attempts;
DROP POLICY IF EXISTS "Users can delete their own quiz attempts" ON quiz_attempts;

CREATE POLICY "Users can view their own quiz attempts"
    ON quiz_attempts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own quiz attempts"
    ON quiz_attempts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own quiz attempts"
    ON quiz_attempts FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own quiz attempts"
    ON quiz_attempts FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES - EVENTS
-- ============================================================================

DROP POLICY IF EXISTS "Users can view their own events" ON events;
DROP POLICY IF EXISTS "Users can insert their own events" ON events;
DROP POLICY IF EXISTS "Users can update their own events" ON events;
DROP POLICY IF EXISTS "Users can delete their own events" ON events;

CREATE POLICY "Users can view their own events"
    ON events FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own events"
    ON events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own events"
    ON events FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own events"
    ON events FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES - RAG DOCUMENTS
-- ============================================================================

DROP POLICY IF EXISTS "Users can view their own rag documents" ON rag_documents;
DROP POLICY IF EXISTS "Users can insert their own rag documents" ON rag_documents;
DROP POLICY IF EXISTS "Users can update their own rag documents" ON rag_documents;
DROP POLICY IF EXISTS "Users can delete their own rag documents" ON rag_documents;

CREATE POLICY "Users can view their own rag documents"
    ON rag_documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own rag documents"
    ON rag_documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own rag documents"
    ON rag_documents FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own rag documents"
    ON rag_documents FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICIES - RAG CHUNKS
-- ============================================================================

DROP POLICY IF EXISTS "Users can view their own rag chunks" ON rag_chunks;
DROP POLICY IF EXISTS "Users can insert their own rag chunks" ON rag_chunks;
DROP POLICY IF EXISTS "Users can update their own rag chunks" ON rag_chunks;
DROP POLICY IF EXISTS "Users can delete their own rag chunks" ON rag_chunks;

CREATE POLICY "Users can view their own rag chunks"
    ON rag_chunks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own rag chunks"
    ON rag_chunks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own rag chunks"
    ON rag_chunks FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own rag chunks"
    ON rag_chunks FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at (drop first for idempotency)
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_quizzes_updated_at ON quizzes;
CREATE TRIGGER update_quizzes_updated_at
    BEFORE UPDATE ON quizzes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_events_updated_at ON events;
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_rag_documents_updated_at ON rag_documents;
CREATE TRIGGER update_rag_documents_updated_at
    BEFORE UPDATE ON rag_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function for vector similarity search (cosine distance)
-- Usage: SELECT * FROM rag_chunks 
--        ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector 
--        LIMIT 10;
-- This function is built into pgvector, but we document it here for reference.

-- ============================================================================
-- NOTES
-- ============================================================================

-- IVFFLAT Index Notes:
-- 1. The IVFFLAT index requires data to exist before creation
-- 2. If you have no data yet, the index creation will succeed but may need
--    to be recreated after loading data for optimal performance
-- 3. To recreate the index after loading data:
--    DROP INDEX IF EXISTS idx_rag_chunks_embedding_ivfflat;
--    CREATE INDEX idx_rag_chunks_embedding_ivfflat 
--        ON rag_chunks 
--        USING ivfflat (embedding vector_cosine_ops)
--        WITH (lists = sqrt((SELECT COUNT(*) FROM rag_chunks))::int);
--
-- 4. For better performance with large datasets, consider using HNSW instead:
--    CREATE INDEX idx_rag_chunks_embedding_hnsw 
--        ON rag_chunks 
--        USING hnsw (embedding vector_cosine_ops)
--        WITH (m = 16, ef_construction = 64);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

