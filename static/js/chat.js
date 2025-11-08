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
        this.modeDescription = null;
        this.ragStatus = null;
        this.selectedFiles = [];
        this.capabilities = {
            rag: true,
            web_search: false,
            research: false,
            thinking: false
        };
    }

    init() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.input = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.modeDescription = document.getElementById('modeDescription');
        this.ragStatus = document.getElementById('ragStatus');

        if (!this.messagesContainer || !this.input) return;

        this.setupEventListeners();
        this.setupFileUpload();
        this.setupCapabilityToggles();
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
        if (this.input) {
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.sendButton.disabled) {
                    this.sendMessage();
                }
            });
            this.input.focus();
        }
    }

    setupCapabilityToggles() {
        const toggles = document.querySelectorAll('.capability-toggle input[type="checkbox"]');
        toggles.forEach(toggle => {
            const capability = toggle.getAttribute('data-capability');
            toggle.checked = this.capabilities[capability] || false;
            this.updateToggleStyle(toggle);
            
            toggle.addEventListener('change', (e) => {
                this.capabilities[capability] = e.target.checked;
                this.updateToggleStyle(e.target);
                this.updateModeDescription();
            });
        });
    }

    updateToggleStyle(checkbox) {
        const label = checkbox.closest('.capability-toggle');
        if (checkbox.checked) {
            label.classList.add('active');
        } else {
            label.classList.remove('active');
        }
    }

    setupFileUpload() {
        const modal = document.getElementById('fileUploadModal');
        const addFilesButton = document.getElementById('addFilesButton');
        const closeModal = document.getElementById('closeModal');
        const fileInput = document.getElementById('fileInput');
        const fileUploadZone = document.getElementById('fileUploadZone');
        const fileList = document.getElementById('fileList');
        const uploadFilesButton = document.getElementById('uploadFiles');
        const cancelUpload = document.getElementById('cancelUpload');

        // Open modal
        if (addFilesButton) {
            addFilesButton.addEventListener('click', () => {
                modal.classList.add('active');
                if (typeof loadFileList === 'function') {
                    loadFileList();
                }
            });
        }

        // Close modal
        const closeModalFunc = () => {
            modal.classList.remove('active');
            this.selectedFiles = [];
            this.updateFileList();
        };

        if (closeModal) {
            closeModal.addEventListener('click', closeModalFunc);
        }

        if (cancelUpload) {
            cancelUpload.addEventListener('click', closeModalFunc);
        }

        // Click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModalFunc();
            }
        });

        // File input change
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(Array.from(e.target.files));
            });
        }

        // Drag and drop
        if (fileUploadZone) {
            fileUploadZone.addEventListener('click', () => {
                fileInput.click();
            });

            fileUploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileUploadZone.classList.add('dragover');
            });

            fileUploadZone.addEventListener('dragleave', () => {
                fileUploadZone.classList.remove('dragover');
            });

            fileUploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                fileUploadZone.classList.remove('dragover');
                const files = Array.from(e.dataTransfer.files);
                this.handleFileSelection(files);
            });
        }

        // Upload files
        if (uploadFilesButton) {
            uploadFilesButton.addEventListener('click', () => {
                this.uploadFiles();
            });
        }
    }

    handleFileSelection(files) {
        const allowedExtensions = ['.txt', '.pdf', '.docx', '.md'];
        const validFiles = files.filter(file => {
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            return allowedExtensions.includes(ext);
        });

        validFiles.forEach(file => {
            if (!this.selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                this.selectedFiles.push(file);
            }
        });

        this.updateFileList();
    }

    updateFileList() {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;

        fileList.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileSize = (file.size / 1024).toFixed(2) + ' KB';
            
            fileItem.innerHTML = `
                <div class="file-item-info">
                    <span class="file-item-name">${this.escapeHtml(file.name)}</span>
                    <span class="file-item-size">${fileSize}</span>
                </div>
                <button class="file-item-remove" data-index="${index}">&times;</button>
            `;

            const removeButton = fileItem.querySelector('.file-item-remove');
            removeButton.addEventListener('click', () => {
                this.selectedFiles.splice(index, 1);
                this.updateFileList();
            });

            fileList.appendChild(fileItem);
        });
    }

    async uploadFiles() {
        if (this.selectedFiles.length === 0) {
            alert('Please select at least one file to upload.');
            return;
        }

        const uploadProgress = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const uploadStatus = document.getElementById('uploadStatus');
        const uploadFilesButton = document.getElementById('uploadFiles');

        uploadProgress.classList.add('active');
        uploadFilesButton.disabled = true;

        let successCount = 0;
        let errorCount = 0;

        for (let i = 0; i < this.selectedFiles.length; i++) {
            const file = this.selectedFiles[i];
            const formData = new FormData();
            formData.append('file', file);

            const progress = ((i + 1) / this.selectedFiles.length) * 100;
            progressFill.style.width = progress + '%';
            uploadStatus.textContent = `Uploading ${file.name}... (${i + 1}/${this.selectedFiles.length})`;

            try {
                const response = await fetch('/api/rag/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (response.ok) {
                    successCount++;
                } else {
                    errorCount++;
                    console.error(`Error uploading ${file.name}:`, data.error);
                }
            } catch (error) {
                errorCount++;
                console.error(`Error uploading ${file.name}:`, error);
            }
        }

        uploadStatus.textContent = `Upload complete: ${successCount} successful, ${errorCount} failed`;
        progressFill.style.width = '100%';

        setTimeout(() => {
            uploadProgress.classList.remove('active');
            uploadFilesButton.disabled = false;
            
            if (successCount > 0) {
                this.selectedFiles = [];
                this.updateFileList();
                this.checkRAGStatus();
                if (typeof loadDashboardStats === 'function') {
                    loadDashboardStats();
                }
                if (typeof loadFileList === 'function') {
                    loadFileList();
                }
                document.getElementById('fileUploadModal').classList.remove('active');
            }
        }, 2000);
    }

    updateModeDescription() {
        if (!this.modeDescription) return;
        
        const activeCapabilities = [];
        if (this.capabilities.rag) activeCapabilities.push('RAG');
        if (this.capabilities.web_search) activeCapabilities.push('Web Search');
        if (this.capabilities.research) activeCapabilities.push('Research');
        if (this.capabilities.thinking) activeCapabilities.push('Thinking');

        if (activeCapabilities.length === 0) {
            this.modeDescription.textContent = 'No capabilities selected. Enable at least one capability.';
        } else {
            this.modeDescription.textContent = `Active: ${activeCapabilities.join(', ')}`;
        }
    }

    async checkRAGStatus() {
        try {
            const response = await fetch('/api/rag/status');
            const data = await response.json();
            if (data.ready && this.ragStatus) {
                this.ragStatus.style.display = 'inline';
                if (data.document_count !== undefined) {
                    this.ragStatus.textContent = `📚 KB Ready (${data.document_count} docs)`;
                } else {
                    this.ragStatus.textContent = '📚 KB Ready';
                }
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
            
            const header = document.createElement('div');
            header.className = 'thinking-header';
            header.textContent = '🧠 Chain of Thought Reasoning';
            thinkingContainer.appendChild(header);
            
            const layersDiv = document.createElement('div');
            layersDiv.className = 'thinking-layers';
            
            thinkingLayers.forEach((layer, index) => {
                const layerDiv = document.createElement('div');
                layerDiv.className = 'thinking-layer';
                
                const layerHeader = document.createElement('div');
                layerHeader.className = 'layer-header';
                layerHeader.innerHTML = `
                    <div class="layer-number">${layer.number}</div>
                    <div class="layer-name">${this.escapeHtml(layer.name)}</div>
                `;
                
                const layerContent = document.createElement('div');
                layerContent.className = 'layer-content';
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
                    use_rag: this.capabilities.rag,
                    use_web_search: this.capabilities.web_search,
                    use_research: this.capabilities.research,
                    use_thinking: this.capabilities.thinking
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

