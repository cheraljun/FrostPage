/**
 * 管理员界面 - 极简版
 * 遵循HTML/CSS/JS分离原则
 */

import { toast } from '/js/components/Toast.js';
import { ImageUploader } from '/js/components/ImageUploader.js';
import { api } from '/js/utils/apiClient.js';

class SimpleAdmin {
    constructor() {
        this.currentType = 'research';
        this.token = localStorage.getItem('admin_token');
        this.posts = [];
        this.editingPost = null;
        this.imageUploader = null;  // 图片上传组件实例
        
        if (!this.token) {
            window.location.href = '/admin/login';
            return;
        }
        
        // 设置全局 API 客户端的 token（供 ImageUploader 等组件使用）
        api.setToken(this.token);
        
        this.init();
    }
    
    // 检查当前类型是否为特殊类型
    isSpecialType() {
        return this.currentType === 'announcement' || this.currentType === 'chat';
    }
    
    init() {
        this.bindNavigation();
        this.bindEditor();
        this.bindLogout();
        this.bindActions();  // 绑定列表操作按钮
        this.loadContent();
    }
    
    // ========== 导航 ==========
    bindNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const type = btn.dataset.type;
                if (!type) return;
                
                // 更新激活状态
                document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                this.currentType = type;
                
                // 清理图片页面特殊处理
                if (type === 'cleanup') {
                    this.showCleanupPage();
                } else {
                    this.loadContent();
                }
            });
        });
    }
    
    bindLogout() {
        const logoutBtn = document.getElementById('logout-btn');
        
        logoutBtn.addEventListener('click', () => {
            // 检查是否已经在确认状态
            if (logoutBtn.dataset.confirm === 'true') {
                // 第二次点击：确认退出
                localStorage.removeItem('admin_token');
                window.location.href = '/admin/login';
                return;
            }
            
            // 第一次点击：显示确认状态
            logoutBtn.dataset.confirm = 'true';
            logoutBtn.dataset.originalText = logoutBtn.textContent;
            logoutBtn.textContent = '确认退出';
            logoutBtn.style.background = '#ff6b6b';
            logoutBtn.style.fontWeight = 'bold';
            
            // 3秒后自动恢复
            setTimeout(() => {
                if (logoutBtn.dataset.confirm === 'true') {
                    logoutBtn.dataset.confirm = 'false';
                    logoutBtn.textContent = logoutBtn.dataset.originalText;
                    logoutBtn.style.background = '';
                    logoutBtn.style.fontWeight = '';
                }
            }, 3000);
        });
    }
    
    // ========== 绑定列表操作（事件委托）==========
    bindActions() {
        const contentList = document.getElementById('content-list');
        
        contentList.addEventListener('click', (e) => {
            const target = e.target;
            
            // 检查是否点击了操作链接
            if (!target.classList.contains('action-link')) return;
            
            e.preventDefault();
            
            const action = target.dataset.action;
            const postId = target.dataset.id;
            const isConfirm = target.dataset.confirm === 'true';
            
            if (!action || !postId) return;
            
            // 需要二次确认的操作（发布、删除）
            if ((action === 'publish' || action === 'delete' || action === 'delete-chat') && !isConfirm) {
                // 第一次点击：显示确认状态
                target.dataset.confirm = 'true';
                target.dataset.originalText = target.textContent;
                target.textContent = action === 'publish' ? '确认发布' : '确认删除';
                target.style.background = action === 'publish' ? '#ff6b6b' : '#c00';
                target.style.fontWeight = 'bold';
                
                // 3秒后自动恢复
                setTimeout(() => {
                    if (target.dataset.confirm === 'true') {
                        target.dataset.confirm = 'false';
                        target.textContent = target.dataset.originalText;
                        target.style.background = '';
                        target.style.fontWeight = '';
                    }
                }, 3000);
                return;
            }
            
            // 第二次点击或不需要确认的操作：执行实际操作
            if (isConfirm) {
                target.dataset.confirm = 'false';
                target.textContent = target.dataset.originalText;
                target.style.background = '';
                target.style.fontWeight = '';
            }
            
            // 根据操作类型调用对应方法
            switch (action) {
                case 'edit':
                    this.editPost(postId);
                    break;
                case 'publish':
                    this.publishPost(postId);
                    break;
                case 'delete':
                    this.deletePost(postId);
                    break;
                case 'delete-chat':
                    this.deleteChatMessage(postId);
                    break;
            }
        });
    }
    
    // ========== 加载内容 ==========
    async loadContent() {
        // 恢复页面标题和新建按钮
        const mainHeader = document.querySelector('.main-header');
        mainHeader.querySelector('h2').textContent = '内容管理';
        mainHeader.querySelector('#new-btn').style.display = 'block';
        
        try {
            let url = `/api/admin/${this.currentType}`;
            
            // 留言类型使用特殊接口
            if (this.currentType === 'chat') {
                url = '/api/chat/messages?limit=500';
            }
            
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!res.ok) throw new Error('加载失败');
            
            const data = await res.json();
            
            // 留言返回格式不同
            if (this.currentType === 'chat') {
                this.posts = data.messages || [];
            } else {
                this.posts = Array.isArray(data) ? data : [];
            }
            
            this.renderList();
        } catch (err) {
            console.error(err);
            toast.error('加载失败');
        }
    }
    
    // ========== 渲染列表 ==========
    renderList() {
        const list = document.getElementById('content-list');
        
        if (this.posts.length === 0) {
            list.innerHTML = '<div class="empty">暂无内容</div>';
            return;
        }
        
        // 留言类型特殊渲染
        if (this.currentType === 'chat') {
            list.innerHTML = this.posts.map(msg => `
                <div class="post-item">
                    <div class="post-info">
                        <div class="post-title">${this.escape(msg.user || '匿名用户')}</div>
                        <div class="post-meta">
                            <span class="date">${this.formatDate(msg.timestamp)}</span>
                        </div>
                        <div class="post-content">${this.escape(msg.text || msg.content || '')}</div>
                    </div>
                    <div class="post-actions">
                        <a href="#" class="action-link danger" data-action="delete-chat" data-id="${msg.id}">删除</a>
                    </div>
                </div>
            `).join('');
            return;
        }
        
        // 普通内容类型渲染（包括公告）
        list.innerHTML = this.posts.map(post => {
            const content = post.content || post.text || '';
            const preview = content.length > 100 ? content.substring(0, 100) + '...' : content;
            
            return `
                <div class="post-item">
                    <div class="post-info">
                        <div class="post-title">${this.escape(post.title || '(无标题)')}</div>
                        <div class="post-meta">
                            <span class="status ${post.status}">${post.status === 'published' ? '已发布' : '草稿'}</span>
                            <span class="date">${this.formatDate(post.created_at)}</span>
                        </div>
                        <div class="post-content">${this.escape(preview)}</div>
                    </div>
                    <div class="post-actions">
                        <a href="#" class="action-link" data-action="edit" data-id="${post.id}">编辑</a>
                        ${post.status === 'draft' ? `<a href="#" class="action-link" data-action="publish" data-id="${post.id}">发布</a>` : ''}
                        <a href="#" class="action-link danger" data-action="delete" data-id="${post.id}">删除</a>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // ========== 编辑器 ==========
    bindEditor() {
        document.getElementById('new-btn').addEventListener('click', () => {
            // 留言不能新建（只能查看用户发送的留言）
            if (this.currentType === 'chat') {
                toast.info('留言由用户发送，不能手动创建');
                return;
            }
            this.openEditor();
        });
        
        document.getElementById('cancel-btn').addEventListener('click', () => {
            this.closeEditor();
        });
        
        document.getElementById('save-btn').addEventListener('click', () => {
            this.savePost();
        });
        
        // 初始化图片上传组件
        this.initImageUploader();
    }
    
    initImageUploader() {
        const container = document.getElementById('image-uploader-container');
        
        // 创建上传组件（紧凑模式）
        this.imageUploader = new ImageUploader({
            compactMode: true,
            maxFiles: 16,
            multiple: true
        });
        
        // 挂载到容器
        container.innerHTML = '';
        container.appendChild(this.imageUploader.render());
    }
    
    openEditor(post = null) {
        this.editingPost = post;
        
        const overlay = document.getElementById('editor-overlay');
        const title = document.getElementById('editor-title');
        const content = document.getElementById('editor-content');
        
        title.value = post ? (post.title || '') : '';
        content.value = post ? post.content : '';
        
        // 设置图片
        if (this.imageUploader) {
            if (post && post.images && post.images.length > 0) {
                this.imageUploader.setImages(post.images);
            } else {
                this.imageUploader.clear();
            }
        }
        
        overlay.classList.add('show');
    }
    
    closeEditor() {
        document.getElementById('editor-overlay').classList.remove('show');
        this.editingPost = null;
    }
    
    // ========== 保存 ==========
    async savePost() {
        const title = document.getElementById('editor-title').value.trim();
        const content = document.getElementById('editor-content').value.trim();
        
        if (!content) {
            toast.info('请输入内容');
            return;
        }
        
        const postData = {
            id: this.editingPost ? this.editingPost.id : undefined,
            title: title || null,
            content: content,
            images: this.imageUploader ? this.imageUploader.getUploadedImages() : [],
            status: 'draft',
            type: this.currentType
        };
        
        try {
            const res = await fetch(`/api/admin/${this.currentType}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });
            
            if (!res.ok) throw new Error('保存失败');
            
            toast.success('保存成功');
            this.closeEditor();
            this.loadContent();
        } catch (err) {
            console.error(err);
            toast.error('保存失败');
        }
    }
    
    // ========== 发布 ==========
    async publishPost(postId) {
        try {
            const res = await fetch(`/api/admin/${this.currentType}/${postId}/publish`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!res.ok) throw new Error('发布失败');
            
            toast.success('发布成功');
            this.loadContent();
        } catch (err) {
            console.error(err);
            toast.error('发布失败');
        }
    }
    
    // ========== 删除 ==========
    async deletePost(postId) {
        try {
            const res = await fetch(`/api/admin/${this.currentType}/${postId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!res.ok) throw new Error('删除失败');
            
            toast.success('删除成功');
            this.loadContent();
        } catch (err) {
            console.error(err);
            toast.error('删除失败');
        }
    }
    
    // ========== 编辑 ==========
    async editPost(postId) {
        // 留言不能编辑
        if (this.currentType === 'chat') {
            toast.info('留言由用户发送，不能编辑');
            return;
        }
        
        try {
            // 先调用编辑接口，立即从正文中删除
            const res = await fetch(`/api/admin/${this.currentType}/${postId}/edit`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!res.ok) throw new Error('进入编辑模式失败');
            
            // 重新加载内容
            await this.loadContent();
            
            // 找到编辑的文章并打开编辑器
            const post = this.posts.find(p => p.id === postId);
            if (post) {
                this.openEditor(post);
            }
        } catch (err) {
            console.error(err);
            toast.error('进入编辑模式失败');
        }
    }
    
    // ========== 删除留言 ==========
    async deleteChatMessage(messageId) {
        try {
            const res = await fetch(`/api/chat/messages/${messageId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!res.ok) throw new Error('删除失败');
            
            toast.success('删除成功');
            this.loadContent();
        } catch (err) {
            console.error(err);
            toast.error('删除失败');
        }
    }
    
    // ========== 清理图片 ==========
    async showCleanupPage() {
        const mainHeader = document.querySelector('.main-header');
        const contentList = document.getElementById('content-list');
        
        // 隐藏"新建"按钮
        mainHeader.querySelector('h2').textContent = '清理图片';
        mainHeader.querySelector('#new-btn').style.display = 'none';
        
        // 显示加载状态
        contentList.innerHTML = '<div class="empty">正在扫描...</div>';
        
        try {
            const res = await fetch('/api/admin/cleanup/scan', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!res.ok) throw new Error('扫描失败');
            
            const data = await res.json();
            this.renderCleanupPage(data);
            
        } catch (err) {
            console.error(err);
            contentList.innerHTML = '<div class="empty">扫描失败</div>';
        }
    }
    
    renderCleanupPage(data) {
        const contentList = document.getElementById('content-list');
        
        // 统计信息（复用 post-item）
        const statsHtml = `
            <div class="post-item">
                <div class="post-info">
                    <div class="post-title">扫描结果</div>
                    <div class="post-content">
                        总图片：${data.total_images} 个 | 
                        被引用：${data.referenced_images} 个 | 
                        未引用图片：${data.unreferenced_count} 个 (${data.total_size_mb} MB)
                    </div>
                </div>
            </div>
        `;
        
        // 如果没有未引用图片
        if (data.unreferenced_count === 0) {
            contentList.innerHTML = statsHtml + '<div class="empty">无未引用图片</div>';
            return;
        }
        
        // 未引用图片列表（复用 post-item）
        const unreferencedHtml = data.unreferenced_details.map(img => `
            <div class="post-item">
                <div class="post-info">
                    <div class="post-title">${img.filename}</div>
                    <div class="post-meta">
                        <span class="date">${img.size_mb} MB</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        // 清理按钮（复用 post-item + action-link）
        const actionHtml = `
            <div class="post-item">
                <div class="post-info"></div>
                <div class="post-actions">
                    <a href="#" class="action-link danger" id="cleanup-execute-btn">清理全部</a>
                </div>
            </div>
        `;
        
        contentList.innerHTML = statsHtml + unreferencedHtml + actionHtml;
        
        // 绑定清理按钮（事件委托已经在 bindActions 中处理）
        // 但清理按钮需要特殊处理，单独绑定
        document.getElementById('cleanup-execute-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.executeCleanup();
        });
    }
    
    async executeCleanup() {
        const btn = document.getElementById('cleanup-execute-btn');
        const originalText = btn.textContent;
        
        // 二次确认
        if (btn.dataset.confirm !== 'true') {
            btn.dataset.confirm = 'true';
            btn.textContent = '确认清理';
            btn.style.background = '#c00';
            btn.style.fontWeight = 'bold';
            
            setTimeout(() => {
                btn.dataset.confirm = 'false';
                btn.textContent = originalText;
                btn.style.background = '';
                btn.style.fontWeight = '';
            }, 3000);
            return;
        }
        
        // 执行清理
        btn.style.opacity = '0.5';
        btn.textContent = '清理中...';
        
        try {
            const res = await fetch('/api/admin/cleanup/execute', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!res.ok) throw new Error('清理失败');
            
            const data = await res.json();
            toast.success(`清理成功：删除 ${data.deleted_count} 个文件，释放 ${data.freed_space_mb} MB 空间`);
            
            // 重新扫描
            this.showCleanupPage();
            
        } catch (err) {
            console.error(err);
            toast.error('清理失败');
            btn.style.opacity = '';
            btn.textContent = originalText;
        }
    }
    
    // ========== 工具函数 ==========
    escape(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
    
    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// 初始化
let admin;
document.addEventListener('DOMContentLoaded', () => {
    admin = new SimpleAdmin();
});

