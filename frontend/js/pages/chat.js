/**
 * 简化版留言板
 * - 不需要登录
 * - 直接查看和发送留言
 */

import { toast } from '/js/components/Toast.js';

class ChatApp {
    constructor() {
        this.messages = [];
        this.userColors = new Map();
        this.colorIndex = 1;
        this.maxColors = 6;
        this.pollInterval = null;
        
        this.initElements();
        this.bindEvents();
        this.loadMessages();
        this.startPolling();
    }

    initElements() {
        this.messagesContainer = document.getElementById('messages');
        this.usernameInput = document.getElementById('username-input');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
    }

    bindEvents() {
        // 发送消息
        this.sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // 昵称输入框：Enter跳转到留言输入框
        this.usernameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.messageInput.focus();
            }
        });

        // 留言输入框：Enter直接发送
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const username = this.usernameInput.value.trim();
        const text = this.messageInput.value.trim();
        
        // 验证
        if (!username) {
            toast.info('请输入昵称');
            this.usernameInput.focus();
            return;
        }

        if (!text) {
            toast.info('请输入留言内容');
            this.messageInput.focus();
            return;
        }

        if (username.length < 2) {
            toast.info('昵称至少需要2个字符');
            this.usernameInput.focus();
            return;
        }

        const message = {
            user: username,
            text: text,
            timestamp: new Date().toISOString()
        };

        try {
            const response = await fetch('/api/chat/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(message)
            });

            if (!response.ok) {
                throw new Error('发送失败');
            }

            // 清空输入框
            this.messageInput.value = '';
            this.messageInput.focus();
            
            // 立即刷新消息列表
            await this.loadMessages();
        } catch (error) {
            console.error('发送消息失败:', error);
            toast.error('发送失败，请重试');
        }
    }

    renderMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message';
        
        const time = this.formatTime(message.timestamp);
        const color = this.getUserColor(message.user);
        
        messageEl.innerHTML = `
            <span class="message-time">[${time}]</span>
            <span class="message-user color-${color}">&lt;${this.escapeHtml(message.user)}&gt;</span>
            <span class="message-text">${this.escapeHtml(message.text)}</span>
        `;
        
        this.messagesContainer.appendChild(messageEl);
    }

    getUserColor(username) {
        if (!this.userColors.has(username)) {
            this.userColors.set(username, this.colorIndex);
            this.colorIndex = (this.colorIndex % this.maxColors) + 1;
        }
        return this.userColors.get(username);
    }

    formatTime(date) {
        const d = new Date(date);
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async loadMessages() {
        try {
            const response = await fetch('/api/chat/messages');
            const data = await response.json();
            
            const serverMessages = data.messages || [];
            
            // 只在消息数量变化时重新渲染
            if (serverMessages.length !== this.messages.length) {
                this.messages = serverMessages;
                
                // 清空并重新渲染所有消息
                this.messagesContainer.innerHTML = '';
                this.messages.forEach(msg => {
                    this.renderMessage(msg);
                });
                
                this.scrollToBottom();
            }
        } catch (e) {
            console.error('加载消息失败:', e);
        }
    }

    startPolling() {
        // 每3秒自动刷新消息
        this.pollInterval = setInterval(() => {
            this.loadMessages();
        }, 3000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }
}

// 初始化留言板
document.addEventListener('DOMContentLoaded', () => {
    const app = new ChatApp();
    
    // 页面卸载时停止轮询
    window.addEventListener('beforeunload', () => {
        app.stopPolling();
    });
});

export default ChatApp;
