/**
 * 管理员登录页面逻辑
 */

class AdminLogin {
    constructor() {
        this.form = document.getElementById('login-form');
        this.loginBtn = document.getElementById('login-btn');
        this.errorMessage = document.getElementById('error-message');
        this.successMessage = document.getElementById('success-message');
        
        this.bindEvents();
        this.checkExistingToken();
    }

    bindEvents() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
    }

    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.showError('请输入用户名和密码');
            return;
        }

        // 禁用按钮
        this.loginBtn.disabled = true;
        this.loginBtn.textContent = '登录中...';
        this.hideMessages();

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // 登录成功，保存 token
                localStorage.setItem('admin_token', data.access_token);
                localStorage.setItem('admin_username', username);
                
                this.showSuccess('登录成功！正在跳转...');
                
                // 跳转到管理后台
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 1000);
            } else {
                this.showError(data.detail || '登录失败');
                this.loginBtn.disabled = false;
                this.loginBtn.textContent = '登录';
            }
        } catch (error) {
            console.error('登录错误:', error);
            this.showError('网络错误，请检查后端是否运行');
            this.loginBtn.disabled = false;
            this.loginBtn.textContent = '登录';
        }
    }

    checkExistingToken() {
        const token = localStorage.getItem('admin_token');
        if (token) {
            // 验证 token 是否有效
            this.verifyToken(token);
        }
    }

    async verifyToken(token) {
        try {
            const response = await fetch('/api/auth/verify', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                // Token 有效，直接跳转
                window.location.href = '/admin';
            } else {
                // Token 无效，清除
                localStorage.removeItem('admin_token');
                localStorage.removeItem('admin_username');
            }
        } catch (error) {
            console.error('验证错误:', error);
        }
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.classList.add('show');
        this.successMessage.classList.remove('show');
    }

    showSuccess(message) {
        this.successMessage.textContent = message;
        this.successMessage.classList.add('show');
        this.errorMessage.classList.remove('show');
    }

    hideMessages() {
        this.errorMessage.classList.remove('show');
        this.successMessage.classList.remove('show');
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new AdminLogin();
});

export default AdminLogin;
