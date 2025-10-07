/**
 * 公告弹窗组件
 */
import { api } from '../utils/apiClient.js';
import { HtmlHelpers } from '../utils/htmlHelpers.js';

export class AnnouncementModal {
    constructor() {
        this.createModal();
        this.bindEvents();
    }

    /**
     * 创建弹窗DOM
     */
    createModal() {
        const modal = document.createElement('div');
        modal.id = 'announcement-modal';
        modal.className = 'announcement-modal';
        modal.innerHTML = `
            <div class="announcement-modal-overlay"></div>
            <div class="announcement-modal-content">
                <button class="announcement-modal-close">×</button>
                <div class="announcement-modal-body" id="announcement-modal-body">
                    加载中...
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        this.modal = modal;
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        const closeBtn = this.modal.querySelector('.announcement-modal-close');
        const overlay = this.modal.querySelector('.announcement-modal-overlay');

        closeBtn.addEventListener('click', () => this.hide());
        overlay.addEventListener('click', () => this.hide());
    }

    /**
     * 显示弹窗
     */
    async show() {
        this.modal.classList.add('show');
        await this.loadContent();
    }

    /**
     * 隐藏弹窗
     */
    hide() {
        this.modal.classList.remove('show');
    }

    /**
     * 加载公告内容
     */
    async loadContent() {
        const body = document.getElementById('announcement-modal-body');
        
        try {
            const data = await api.get('/announcement');
            
            if (!data.items || data.items.length === 0) {
                body.innerHTML = '<p style="text-align: center; color: #666;">暂无公告</p>';
                return;
            }

            const html = data.items.map(item => {
                if (item.type === 'text') {
                    return `<p style="margin-bottom: 1rem; line-height: 1.6; word-wrap: break-word; word-break: break-word; overflow-wrap: break-word; max-width: 100%;">${HtmlHelpers.formatContent(item.content)}</p>`;
                } else if (item.type === 'image') {
                    return `<img src="${item.content}" style="max-width: 100%; height: auto; display: block; margin: 0 auto 1rem;" alt="公告图片">`;
                }
                return '';
            }).join('');

            body.innerHTML = html;
        } catch (error) {
            console.error('加载公告失败:', error);
            body.innerHTML = '<p style="text-align: center; color: #f44;">加载失败</p>';
        }
    }
}

