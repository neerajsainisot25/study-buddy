/**
 * Chat Module
 * Handles all chat functionality
 */

class Chat {
    constructor() {
        this.sessionId = 'session_' + Date.now();
        this.messagesContainer = null;
        this.input = null;
        this.sendButton = null;
        this.clearButton = null;
        this.modeSelect = null;
        this.modeDescription = null;
        this.ragStatus = null;
        this.currentMode = 'normal';
    }

    init() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.input = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.modeSelect = document.getElementById('chatMode');
        this.modeDescription = document.getElementById('modeDescription');
        this.ragStatus = document.getElementById('ragStatus');

        if (!this.messagesContainer || !this.input) return;

        this.setupEventListeners();
        this.addWelcomeMessage();
        this.updateModeDescription();
        this.checkRAGStatus();
    }

    setupEventListeners() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => this.clearChat());
        }
        if (this.modeSelect) {
            this.modeSelect.addEventListener('change', (e) => {
                this.currentMode = e.target.value;
                this.updateModeDescription();
            });
        }
        if (this.input) {
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.sendButton.disabled) {
                    this.sendMessage();
                }
            });
            this.input.focus();
        }
    }

    updateModeDescription() {
        if (!this.modeDescription) return;
        
        const descriptions = {
            'normal': 'Standard conversation (auto-enhanced with knowledge base if available)',
            'thinking': 'Multi-layer deep reasoning (enhanced with knowledge base)',
            'research': 'Searches the web and synthesizes information',
            'rag': 'Fully RAG-powered: Uses knowledge base documents for answers'
        };
        
        this.modeDescription.textContent = descriptions[this.currentMode] || descriptions['normal'];
    }

    async checkRAGStatus() {
        try {
            const response = await fetch('/api/rag/status');
            const data = await response.json();
            if (data.ready && this.ragStatus) {
                this.ragStatus.style.display = 'inline';
            } else if (this.ragStatus) {
                this.ragStatus.style.display = 'none';
            }
        } catch (error) {
            console.error('Error checking RAG status:', error);
        }
    }

    addWelcomeMessage() {
        if (this.messagesContainer && this.messagesContainer.children.length === 0) {
            this.addMessage("Hello! I'm your AI assistant. How can I help you today?", false);
        }
    }

    addMessage(content, isUser, thinkingLayers = null, searchResults = null, retrievedDocs = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Add multi-layer thinking section if available
        if (thinkingLayers && thinkingLayers.length > 0 && !isUser) {
            const thinkingContainer = document.createElement('div');
            thinkingContainer.className = 'thinking-container';
            thinkingContainer.style.cssText = 'margin-bottom: 16px;';
            
            const header = document.createElement('div');
            header.style.cssText = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 16px; border-radius: 8px 8px 0 0; font-weight: 600; font-size: 14px;';
            header.textContent = '🧠 Multi-Layer Reasoning Process';
            thinkingContainer.appendChild(header);
            
            const layersDiv = document.createElement('div');
            layersDiv.style.cssText = 'background: #f8f9fa; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px; padding: 16px;';
            
            thinkingLayers.forEach((layer, index) => {
                const layerDiv = document.createElement('div');
                layerDiv.style.cssText = `margin-bottom: ${index < thinkingLayers.length - 1 ? '20px' : '0'}; padding-bottom: ${index < thinkingLayers.length - 1 ? '20px' : '0'}; border-bottom: ${index < thinkingLayers.length - 1 ? '2px solid #e0e0e0' : 'none'};`;
                
                const layerHeader = document.createElement('div');
                layerHeader.style.cssText = 'display: flex; align-items: center; margin-bottom: 10px;';
                layerHeader.innerHTML = `
                    <div style="background: #667eea; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; margin-right: 10px;">
                        ${layer.number}
                    </div>
                    <div style="font-weight: 600; color: #333; font-size: 15px;">
                        ${this.escapeHtml(layer.name)}
                    </div>
                `;
                
                const layerContent = document.createElement('div');
                layerContent.style.cssText = 'background: white; padding: 12px; border-radius: 6px; margin-top: 8px; border-left: 3px solid #667eea; color: #555; white-space: pre-wrap; font-size: 14px; line-height: 1.6;';
                layerContent.textContent = layer.reasoning;
                
                layerDiv.appendChild(layerHeader);
                layerDiv.appendChild(layerContent);
                layersDiv.appendChild(layerDiv);
            });
            
            thinkingContainer.appendChild(layersDiv);
            contentDiv.appendChild(thinkingContainer);
        }
        
        // Add retrieved documents if available (RAG mode)
        if (retrievedDocs && retrievedDocs.length > 0 && !isUser) {
            const docsDiv = document.createElement('div');
            docsDiv.className = 'retrieved-docs';
            docsDiv.style.cssText = 'background: #e7f3ff; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #2196F3;';
            docsDiv.innerHTML = `<strong style="color: #1976D2;">📚 Retrieved from Knowledge Base:</strong>`;
            const docsList = document.createElement('ul');
            docsList.style.cssText = 'margin: 8px 0 0 0; padding-left: 20px;';
            retrievedDocs.forEach((doc, index) => {
                const li = document.createElement('li');
                li.style.cssText = 'margin-bottom: 8px;';
                const source = doc.metadata?.source || 'Unknown source';
                li.innerHTML = `<strong style="color: #1976D2;">${this.escapeHtml(source)}</strong><br><span style="font-size: 12px; color: #666;">${this.escapeHtml(doc.content.substring(0, 200))}...</span>`;
                docsList.appendChild(li);
            });
            docsDiv.appendChild(docsList);
            contentDiv.appendChild(docsDiv);
        }
        
        // Add search results if available
        if (searchResults && searchResults.length > 0 && !isUser) {
            const searchDiv = document.createElement('div');
            searchDiv.className = 'search-results';
            searchDiv.style.cssText = 'background: #fff3cd; padding: 12px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #ffc107;';
            searchDiv.innerHTML = `<strong style="color: #856404;">🔍 Sources Found:</strong>`;
            const resultsList = document.createElement('ul');
            resultsList.style.cssText = 'margin: 8px 0 0 0; padding-left: 20px;';
            searchResults.forEach(result => {
                const li = document.createElement('li');
                li.style.cssText = 'margin-bottom: 8px;';
                li.innerHTML = `<a href="${result.url}" target="_blank" style="color: #856404; text-decoration: none; font-weight: 600;">${this.escapeHtml(result.title)}</a><br><span style="font-size: 12px; color: #666;">${this.escapeHtml(result.snippet)}</span>`;
                resultsList.appendChild(li);
            });
            searchDiv.appendChild(resultsList);
            contentDiv.appendChild(searchDiv);
        }
        
        // Add main content
        const textDiv = document.createElement('div');
        textDiv.style.cssText = 'white-space: pre-wrap;';
        textDiv.textContent = content;
        contentDiv.appendChild(textDiv);
        
        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'typingIndicator';
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        
        messageDiv.appendChild(typingDiv);
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        this.addMessage(message, true);
        this.input.value = '';
        if (this.sendButton) this.sendButton.disabled = true;

        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: message,
                    session_id: this.sessionId,
                    mode: this.currentMode
                })
            });

            const data = await response.json();
            this.removeTypingIndicator();

            if (response.ok) {
                // Show RAG enhancement indicator if applicable
                if (data.rag_enhanced && data.retrieved_docs && data.retrieved_docs.length > 0) {
                    console.log('✅ Answer enhanced with knowledge base');
                }
                
                this.addMessage(
                    data.answer, 
                    false, 
                    data.thinking_layers || null,
                    data.search_results || null,
                    data.retrieved_docs || null
                );
            } else {
                this.addMessage('Error: ' + (data.error || 'Unknown error'), false);
            }
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('Error: Please try again.', false);
            console.error('Chat error:', error);
        } finally {
            if (this.sendButton) this.sendButton.disabled = false;
            if (this.input) this.input.focus();
        }
    }

    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) return;

        this.messagesContainer.innerHTML = '';
        this.addWelcomeMessage();

        try {
            await fetch('/api/chat/clear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }
}

// Export for use in other modules
window.Chat = Chat;

