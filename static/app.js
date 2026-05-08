const API = '';
let sessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    const uploadScreen = document.getElementById('upload-screen');
    const editorScreen = document.getElementById('editor-screen');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const chooseBtn = document.getElementById('choose-btn');
    const docFilename = document.getElementById('doc-filename');
    const docContent = document.getElementById('doc-content');
    const chatMessages = document.getElementById('chat-messages');
    const msgInput = document.getElementById('msg-input');
    const sendBtn = document.getElementById('send-btn');
    const downloadBtn = document.getElementById('download-btn');
    const newBtn = document.getElementById('new-btn');

    // Upload Logic
    chooseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleUpload(e.target.files[0]));

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => dropZone.classList.remove('drag-over'));
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleUpload(e.dataTransfer.files[0]);
    });

    async function handleUpload(file) {
        if (!file) return;
        if (!file.name.toLowerCase().endsWith('.docx')) {
            alert('Please upload a .docx file only');
            return;
        }

        const originalBtnText = chooseBtn.innerText;
        chooseBtn.innerText = 'Uploading...';
        chooseBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(API + '/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                sessionId = data.session_id;
                docFilename.innerText = file.name;
                uploadScreen.classList.add('hidden');
                editorScreen.classList.remove('hidden');
                editorScreen.style.display = 'flex';
                renderPreview();
                addBubble(`Hi! I've loaded "${file.name}". How can I help you edit it?`, 'ai');
            } else {
                alert(data.detail || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Something went wrong during upload.');
        } finally {
            chooseBtn.innerText = originalBtnText;
            chooseBtn.disabled = false;
        }
    }

    // Preview Rendering
    async function renderPreview() {
        docContent.innerHTML = '<div style="text-align:center; padding: 40px; color: #6e6e73;">Refreshing preview...</div>';

        try {
            const response = await fetch(API + '/preview/' + sessionId);
            if (!response.ok) throw new Error('Preview failed');

            const blob = await response.blob();
            const arrayBuffer = await blob.arrayBuffer();
            
            const result = await mammoth.convertToHtml({ arrayBuffer: arrayBuffer });
            docContent.innerHTML = result.value || '<p>Empty document.</p>';
        } catch (error) {
            console.error('Preview error:', error);
            docContent.innerHTML = `<p style="color: red;">Error rendering preview: ${error.message}</p>`;
        }
    }

    // Chat Logic
    function addBubble(text, type, showEditBadge = false) {
        const bubble = document.createElement('div');
        bubble.className = type === 'user' ? 'user-bubble' : 'ai-bubble';
        
        const textSpan = document.createElement('span');
        textSpan.textContent = text;
        bubble.appendChild(textSpan);

        if (showEditBadge) {
            const badge = document.createElement('span');
            badge.className = 'edit-badge';
            badge.innerText = '✏️ Edit applied';
            bubble.appendChild(document.createElement('br'));
            bubble.appendChild(badge);
        }

        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showLoadingBubble() {
        const bubble = document.createElement('div');
        bubble.className = 'ai-bubble loading-bubble';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            dot.className = 'dot';
            bubble.appendChild(dot);
        }
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return bubble;
    }

    async function sendMessage() {
        const text = msgInput.value.trim();
        if (!text || !sessionId) return;

        addBubble(text, 'user');
        msgInput.value = '';
        msgInput.style.height = 'auto';

        const loader = showLoadingBubble();

        try {
            const response = await fetch(API + '/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, message: text })
            });

            const data = await response.json();
            loader.remove();

            if (response.ok) {
                addBubble(data.reply, 'ai', data.edited);
                if (data.edited) {
                    renderPreview();
                }
            } else {
                addBubble(data.detail || 'Something went wrong.', 'ai');
            }
        } catch (error) {
            loader.remove();
            console.error('Chat error:', error);
            addBubble('Something went wrong. Is the server running?', 'ai');
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    
    msgInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    msgInput.addEventListener('input', () => {
        msgInput.style.height = 'auto';
        msgInput.style.height = (msgInput.scrollHeight) + 'px';
    });

    newBtn.addEventListener('click', () => {
        if (confirm('Start over with a new file?')) {
            window.location.reload();
        }
    });

    downloadBtn.addEventListener('click', () => {
        window.open(API + '/download/' + sessionId, '_blank');
    });
});
