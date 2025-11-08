// File management functionality
class FileManager {
    constructor() {
        this.modal = null;
        this.fileList = null;
    }

    init() {
        this.modal = document.getElementById('fileUploadModal');
        this.fileList = document.getElementById('fileList');
        this.setupEventListeners();
    }

    setupEventListeners() {
        const closeBtn = document.getElementById('closeModal');
        const cancelBtn = document.getElementById('cancelUpload');
        const uploadBtn = document.getElementById('uploadFiles');
        const fileZone = document.getElementById('fileUploadZone');
        const fileInput = document.getElementById('fileInput');

        if (closeBtn) closeBtn.addEventListener('click', () => this.close());
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.close());
        if (uploadBtn) uploadBtn.addEventListener('click', () => this.uploadFiles());
        
        if (fileZone) {
            fileZone.addEventListener('click', () => fileInput?.click());
            fileZone.addEventListener('dragover', (e) => this.handleDragOver(e));
            fileZone.addEventListener('drop', (e) => this.handleDrop(e));
        }

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }

    show() {
        if (this.modal) {
            this.modal.classList.add('active');
            this.loadFileList();
        }
    }

    close() {
        if (this.modal) {
            this.modal.classList.remove('active');
        }
    }

    async loadFileList() {
        try {
            const response = await fetch('/api/rag/files');
            const data = await response.json();
            
            if (!this.fileList) return;
            
            this.fileList.innerHTML = '';
            
            if (data.files && data.files.length > 0) {
                data.files.forEach(file => {
                    const fileItem = this.createFileItem(file);
                    this.fileList.appendChild(fileItem);
                });
            } else {
                this.fileList.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 20px; font-size: 13px;">No files uploaded yet</div>';
            }
        } catch (error) {
            console.error('Error loading file list:', error);
        }
    }

    createFileItem(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const uploadDate = new Date(file.uploaded * 1000);
        const dateStr = uploadDate.toLocaleDateString();
        
        fileItem.innerHTML = `
            <div style="flex: 1;">
                <div class="file-item-name">${this.escapeHtml(file.filename)}</div>
                <div class="file-item-size">${file.size_mb} MB • ${dateStr}</div>
            </div>
            <button class="file-item-remove" onclick="window.fileManagerInstance.deleteFile('${this.escapeHtml(file.filename)}')" title="Delete file">×</button>
        `;
        
        return fileItem;
    }

    async deleteFile(filename) {
        if (!confirm(`Delete "${filename}"?`)) return;
        
        try {
            const response = await fetch(`/api/rag/files/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.loadFileList();
                if (window.dashboardInstance) {
                    window.dashboardInstance.loadStats();
                }
            } else {
                alert('Error deleting file');
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            alert('Error deleting file');
        }
    }

    async uploadFiles() {
        const fileInput = document.getElementById('fileInput');
        if (!fileInput || !fileInput.files.length) {
            alert('Please select files to upload');
            return;
        }

        const formData = new FormData();
        Array.from(fileInput.files).forEach(file => {
            formData.append('files', file);
        });

        const progressDiv = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const uploadStatus = document.getElementById('uploadStatus');

        try {
            if (progressDiv) progressDiv.classList.remove('hidden');
            if (progressFill) progressFill.style.width = '50%';
            if (uploadStatus) uploadStatus.textContent = 'Uploading...';

            const response = await fetch('/api/rag/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                if (progressFill) progressFill.style.width = '100%';
                if (uploadStatus) uploadStatus.textContent = 'Upload complete!';
                
                setTimeout(() => {
                    if (progressDiv) progressDiv.classList.add('hidden');
                    if (progressFill) progressFill.style.width = '0%';
                    fileInput.value = '';
                    this.loadFileList();
                    if (window.dashboardInstance) {
                        window.dashboardInstance.loadStats();
                    }
                }, 1000);
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
            alert('Error uploading files');
            if (progressDiv) progressDiv.classList.add('hidden');
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        const fileInput = document.getElementById('fileInput');
        if (fileInput && e.dataTransfer.files) {
            fileInput.files = e.dataTransfer.files;
        }
    }

    handleFileSelect(e) {
        // File selection handled
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global file manager instance
window.fileManagerInstance = new FileManager();

// Global function for onclick handlers
function showFileManager() {
    window.fileManagerInstance.show();
}
