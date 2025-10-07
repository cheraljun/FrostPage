# FrostPage

> 冰霜粗野主义风格的单页应用博客系统

FrostPage 是一个采用冰霜粗野主义（Frost Brutalism）设计风格的单页应用博客系统。

**核心特性**：
- ✅ **无框架依赖** - 纯原生 JavaScript ES6 模块化，代码永不过时
- ✅ **无数据库依赖** - JSON 文件存储，轻量部署
- ✅ **严格分离** - HTML/CSS/JS 完全解耦，职责清晰
- ✅ **单页应用** - 基于状态管理的 SPA 架构，无刷新切换
- ✅ **Hash 路由** - 每篇文章有独立 URL，可直接分享
- ✅ **双存储模型** - 草稿与发布物理隔离，编辑安全
- ✅ **智能图片处理** - PNG/JPG 自动转 WebP 压缩，GIF 保留动画效果
- ✅ **极简后台** - 文字链接 + 1px 分隔线，一切从简
- ✅ **移动优化** - 完整的响应式支持，触摸友好

**技术栈**：FastAPI 0.104 + Uvicorn + JWT + Pillow | 原生 JavaScript ES6

---

## 一句话概述

基于 FastAPI + 原生 JavaScript 的无框架、无数据库单页应用，严格遵循 HTML/CSS/JS 分离原则，采用双存储模型和 Hash 路由实现完整的博客功能。

---

## 设计理念

**冰霜粗野主义（Frost Brutalism）**
- 冷色调（蓝灰色系）+ 简洁边框
- 功能至上，无装饰
- 每个元素都有存在的理由

**技术哲学**
- HTML 负责结构，CSS 负责样式，JS 负责行为
- 三者完全分离，互不依赖
- 无框架依赖，代码永不过时

---

## 核心功能

### 用户端
- **单页应用**：无刷新切换页面
- **Hash 路由**：每篇文章有独立 URL，可直接分享
- **内容展示**：研究、媒体、活动、商店四个板块
- **图片灯箱**：点击图片全屏查看
- **全文搜索**：搜索所有已发布内容
- **聊天留言**：用户可留言
- **电台播放**：背景音乐播放器
- **书籍滚动栏**：顶部文字滚动展示
- **移动端优化**：完整的响应式支持

### 管理端
- **草稿管理**：创建、编辑、删除草稿
- **发布管理**：草稿发布、编辑已发布内容
- **图片上传**：支持多张图片上传（PNG/JPG → WebP，GIF 保持原格式）
- **图片清理**：扫描并清理未引用的图片
- **公告管理**：全局公告编辑
- **留言管理**：查看和删除用户留言
- **极简设计**：文字链接 + 1px 分隔线，无装饰

---

## 技术栈

```
后端: FastAPI 0.104 + Uvicorn + JWT + Pillow
前端: 原生 JavaScript ES6 模块化（无框架）
存储: JSON 文件（无数据库）
认证: JWT Token (HS256)
图片: PNG/JPG → WebP 压缩，GIF 保留动画
```

---

## 项目结构

```
FrostPage/
│
├─ backend/                           # Python 后端
│   ├─ __init__.py
│   ├─ main.py                        # FastAPI 应用入口
│   ├─ config.py                      # 配置管理
│   ├─ database.py                    # 数据库配置（预留）
│   │
│   ├─ routers/                       # API 路由模块
│   │   ├─ __init__.py
│   │   ├─ auth.py                    # JWT 认证路由
│   │   ├─ admin.py                   # 管理员 CRUD 路由
│   │   ├─ public.py                  # 公开内容访问路由
│   │   ├─ upload.py                  # 文件上传路由
│   │   ├─ search.py                  # 全文搜索路由
│   │   ├─ chat.py                    # 聊天消息路由
│   │   ├─ book.py                    # 书籍内容路由
│   │   ├─ announcement.py            # 公告路由
│   │   ├─ config.py                  # 配置信息路由
│   │   └─ draft.py                   # 草稿操作路由
│   │
│   ├─ schemas/                       # Pydantic 数据验证
│   │   ├─ __init__.py
│   │   ├─ auth.py                    # 认证相关 schema
│   │   └─ content.py                 # 内容相关 schema
│   │
│   ├─ models/                        # SQLAlchemy 模型（预留）
│   │   ├─ __init__.py
│   │   └─ post.py
│   │
│   ├─ services/                      # 业务逻辑层（预留）
│   │   └─ __init__.py
│   │
│   └─ utils/                         # 工具函数
│       ├─ __init__.py
│       ├─ auth.py                    # JWT 工具函数
│       └─ file_storage.py            # JSON 文件读写
│
├─ frontend/                          # 纯前端代码
│   ├─ index.html                     # 用户界面主入口（SPA）
│   │
│   ├─ admin/                         # 管理后台
│   │   ├─ index.html                 # 管理后台主页
│   │   └─ login.html                 # 登录页
│   │
│   ├─ pages/                         # 其他页面
│   │   └─ chat.html                  # 聊天页（iframe 嵌入）
│   │
│   ├─ css/                           # 样式文件（完全分离）
│   │   ├─ style.css                  # 全局样式（CSS 变量定义）
│   │   ├─ index.css                  # 主页布局样式
│   │   ├─ components.css             # 可复用组件样式
│   │   ├─ chat.css                   # 聊天页样式
│   │   ├─ admin.css                  # 管理后台样式
│   │   ├─ admin-simple.css           # 管理后台简化版样式
│   │   ├─ uploader.css               # 图片上传器样式
│   │   └─ lib/                       # 第三方 CSS 库
│   │       └─ video-js.min.css
│   │
│   ├─ js/                            # JavaScript 模块（完全分离）
│   │   ├─ main.js                    # 应用入口（初始化 SPA）
│   │   │
│   │   ├─ core/                      # 核心系统模块
│   │   │   ├─ StateManager.js        # 状态管理器（SPA 核心）
│   │   │   └─ ContentPageBase.js     # 页面基类（预留）
│   │   │
│   │   ├─ components/                # 可复用组件
│   │   │   ├─ MainContentArea.js     # 主内容区渲染器
│   │   │   ├─ ContentCard.js         # 内容卡片组件
│   │   │   ├─ EmptyState.js          # 空状态组件
│   │   │   ├─ RadioPlayer.js         # 音频播放器组件
│   │   │   ├─ ImageUploader.js       # 图片上传组件
│   │   │   ├─ ImageLightbox.js       # 图片灯箱组件
│   │   │   ├─ Toast.js               # 提示消息组件
│   │   │   └─ AnnouncementModal.js   # 公告弹窗组件
│   │   │
│   │   ├─ utils/                     # 工具函数（纯函数）
│   │   │   ├─ apiClient.js           # HTTP 客户端封装
│   │   │   ├─ htmlHelpers.js         # HTML 处理工具
│   │   │   └─ navIconLoader.js       # 导航图标加载器
│   │   │
│   │   ├─ config/                    # 配置模块
│   │   │   └─ pageConfigs.js         # 页面配置定义
│   │   │
│   │   ├─ pages/                     # 页面逻辑（SPA 子模块）
│   │   │   ├─ research.js            # 研究页逻辑（预留）
│   │   │   ├─ media.js               # 媒体页逻辑（预留）
│   │   │   ├─ activity.js            # 活动页逻辑（预留）
│   │   │   ├─ shop.js                # 商店页逻辑（预留）
│   │   │   └─ chat.js                # 聊天页逻辑
│   │   │
│   │   ├─ admin/                     # 管理后台逻辑
│   │   │   ├─ admin.js               # 管理后台主逻辑
│   │   │   └─ login.js               # 登录逻辑
│   │   │
│   │   └─ lib/                       # 第三方 JavaScript 库
│   │       ├─ jquery-3.7.1.min.js
│   │       └─ video.min.js
│   │
│   └─ images/                        # 静态图片资源
│       ├─ background.webp            # 背景图片（WebP 格式）
│       ├─ background.jpg             # 背景图片（JPG 备份）
│       ├─ doge.gif                   # Doge 动图
│       ├─ play.png                   # 播放按钮
│       ├─ pause.png                  # 暂停按钮
│       ├─ nav-research.png           # 研究导航图标
│       ├─ nav-media.png              # 媒体导航图标
│       ├─ nav-activity.gif           # 活动导航图标（GIF 动图）
│       ├─ nav-shop.png               # 商店导航图标
│       └─ nav-chat.png               # 留言导航图标
│
├─ admin_data/                        # 管理员数据目录
│   ├─ config.json                    # 系统配置（密码、JWT、电台）
│   │
│   ├─ drafts/                        # 草稿存储（管理员工作区）
│   │   ├─ research.json              # 研究类草稿
│   │   ├─ media.json                 # 媒体类草稿
│   │   ├─ activity.json              # 活动类草稿
│   │   ├─ shop.json                  # 商店类草稿
│   │   └─ announcement.json          # 公告类草稿
│   │
│   ├─ published/                     # 发布内容（用户可见）
│   │   ├─ research.json              # 已发布研究
│   │   ├─ media.json                 # 已发布媒体
│   │   ├─ activity.json              # 已发布活动
│   │   ├─ shop.json                  # 已发布商店
│   │   └─ announcement.json          # 已发布公告
│   │
│   ├─ images/                        # 图片资源（WebP + GIF）
│   │
│   └─ book/                          # 书籍文本内容
│       └─ 查拉图斯特拉如是说.txt
│
├─ user_data/                         # 用户数据目录
│   └─ chat_messages.json             # 聊天消息（最多 500 条）
│
├─ requirements.txt                   # Python 依赖
├─ README.md                          # 项目说明
├─ ARCHITECTURE.md                    # 架构文档
├─ Nginx命令手册.txt                   # Nginx 配置手册
└─ 提交git前运行.py                    # Git 提交前清理脚本
```

---

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python backend/main.py
```

### 3. 访问地址

- **用户界面**: http://127.0.0.1:8000
- **管理后台**: http://127.0.0.1:8000/admin/login
  - 默认账号: `admin`
  - 默认密码: `password`

---

## 核心架构

### 1. 单页应用（SPA）设计

**单页应用**：整个网站只有一个 HTML 文件（`index.html`），所有页面切换通过 JavaScript 动态更新 DOM，无需刷新。

**核心组件**：

```
StateManager（状态管理器）
    ↓ 状态变化通知
MainContentArea（主内容区）
    ↓ 根据状态渲染
DOM 更新（视图切换）
```

**状态管理**：

```javascript
states: {
  research: { view: 'list', itemId: null },   // 研究：列表页
  media: { view: 'detail', itemId: '123' },   // 媒体：详情页 ID=123
  activity: null,                              // 活动：未访问
  shop: null                                   // 商店：未访问
}
```

**单向数据流**：

```
用户操作 → StateManager.showList() → 状态更新 → notify() → 视图重新渲染
```

视图**不能**直接修改状态，必须通过 StateManager 提供的方法。

### 2. Hash 路由系统

**问题**：单页应用的 URL 始终是 `/index.html`，无法分享特定文章。

**解决**：使用 Hash 路由（`#/type/view/id`）

**URL 示例**：

```
http://example.com/#/research/list           # 研究列表页
http://example.com/#/research/detail/123     # 研究详情页 ID=123
http://example.com/#/media/detail/456        # 媒体详情页 ID=456
```

**双向绑定**：

```
State 变化 → URL 更新    （用户点击导航）
URL 变化  → State 同步   （浏览器前进/后退、刷新页面）
```

**效果**：
- 每篇文章有独立 URL
- 支持直接分享
- 浏览器前进/后退正常工作
- 刷新页面保持当前状态

### 3. HTML/CSS/JS 完全分离

**为什么要分离？**

- **可维护性**：修改样式不影响逻辑
- **可复用性**：同一组件可应用不同样式
- **可测试性**：逻辑与表现解耦

**分离标准**：

| 层级 | 职责 | 禁止内容 |
|------|------|----------|
| **HTML** | 结构 | ❌ 内联样式 `style="..."` <br> ❌ 内联脚本 `onclick="..."` |
| **CSS** | 表现 | ❌ JavaScript 逻辑 <br> ❌ 依赖 JS 计算的值 |
| **JavaScript** | 行为 | ❌ 直接操作样式 `element.style.xxx` <br> ❌ 在 JS 中写 CSS |

**实现方式**：

```html
<!-- HTML：纯结构，用 data-* 传递数据 -->
<button class="nav-btn" data-nav="research">研究</button>
```

```css
/* CSS：纯样式，用类名控制状态 */
.nav-btn {
  background: transparent;
  border: 2px solid var(--frost-medium);
}

.nav-btn.active {
  background: var(--frost-accent);
}
```

```javascript
// JavaScript：纯行为，通过类名操作样式
btn.addEventListener('click', () => {
  btn.classList.add('active');
  stateManager.showList(btn.dataset.nav);
});
```

**关键原则**：JavaScript 只能通过**添加/移除类名**来改变样式，不能直接操作 `style` 属性。

### 4. 组件化与复用

**可复用组件的特征**：

- 单一职责：只负责一件事
- 明确接口：输入输出清晰
- 无副作用：不依赖全局状态
- 可组合：可与其他组件组合

**本系统的可复用组件**：

| 组件 | 输入 | 输出 | 功能 |
|------|------|------|------|
| `ContentCard` | post 对象 | HTML 字符串 | 渲染内容卡片 |
| `ImageLightbox` | 图片 URL | DOM 元素 | 全屏查看图片 |
| `Toast` | 消息文本 | DOM 元素 | 显示提示消息 |
| `EmptyState` | 状态类型 | HTML 字符串 | 空状态展示 |
| `RadioPlayer` | 无 | DOM 元素 | 音频播放器 |

**复用原则**：

```javascript
// ✓ 好的设计：纯函数，无副作用
class ContentCard {
  constructor(post) {
    this.post = post;  // 输入
  }
  
  render() {
    return `<div>...</div>`;  // 输出
  }
}

// ✗ 不好的设计：依赖全局状态
class BadCard {
  render() {
    return window.globalData.title;  // 耦合
  }
}
```

### 5. 双存储模型

**设计动机**：草稿和发布内容物理隔离，确保编辑安全。

**目录结构**：

```
admin_data/
  ├─ drafts/      # 草稿区（管理员工作区）
  └─ published/   # 发布区（用户可见）
```

**操作语义**：

| 操作 | 草稿区 | 发布区 | 效果 |
|------|--------|--------|------|
| 保存草稿 | 写入 | 如果存在则删除 | 编辑已发布内容会自动撤销发布 |
| 发布 | 状态改为 published | 复制过去 | 发布后两区都有 |
| 编辑已发布 | 状态改为 draft | 删除 | 立即从前台消失 |
| 删除 | 删除 | 删除 | 彻底删除 |

**优势**：

- 草稿是主数据源，发布区是副本
- 编辑草稿不影响已发布内容
- 编辑已发布内容 = 撤销发布 + 进入草稿模式
- 查询高效：无需过滤状态

---

## API 接口

### 公开接口

```http
GET  /api/content/{type}              # 获取已发布内容（type: research/media/activity/shop）
GET  /api/search?q={keyword}          # 全文搜索
GET  /api/announcement                # 获取公告
GET  /api/book/content                # 获取书籍滚动内容
GET  /api/chat/messages               # 获取聊天消息
POST /api/chat/messages               # 发送聊天消息
GET  /api/config/stream               # 获取电台配置
```

### 管理接口（需 JWT Token）

```http
POST   /api/auth/login                    # 登录获取 Token
GET    /api/admin/{type}                  # 获取草稿列表
POST   /api/admin/{type}                  # 保存草稿
POST   /api/admin/{type}/{id}/publish     # 发布草稿
POST   /api/admin/{type}/{id}/edit        # 编辑已发布内容（撤销发布）
DELETE /api/admin/{type}/{id}             # 删除内容
POST   /api/upload/images                 # 上传图片（多张）
GET    /api/admin/cleanup/scan            # 扫描未引用图片
POST   /api/admin/cleanup/execute         # 清理未引用图片
```

---

## 数据模型

```typescript
interface Post {
  id: string;                    // 格式: YYYYMMDDHHMMSSffffff
  title?: string;                // 标题（可选）
  content: string;               // 内容文本
  images?: string[];             // 图片 URL 数组
  status: 'draft' | 'published'; // 状态
  type: string;                  // 类型: research/media/activity/shop
  created_at: string;            // ISO 8601 格式
  updated_at: string;            // ISO 8601 格式
  published_at?: string;         // 发布时间（可选）
}
```

---

## 图片处理策略

**上传处理**：

| 格式 | 处理方式 | 原因 |
|------|---------|------|
| PNG/JPG | → WebP（质量 90%） | 大幅压缩，保持质量 |
| **GIF** | **保持原格式** | **保留动画效果** |
| BMP/TIFF | → WebP | 大幅压缩 |

**文件命名**：

```
UUID.扩展名
示例: a1b2c3d4e5f6.webp、f7e8d9c0b1a2.gif
```

**删除策略**：

1. **同步删除**：删除文章时自动删除关联图片
2. **手动清理**：扫描并清理未引用的孤儿图片

---

## CSS 变量系统

**冰霜粗野主义配色**：

```css
:root {
  /* 核心色彩 */
  --frost-deep: #2c4a5c;         /* 深蓝灰 - 主文字 */
  --frost-medium: #5a7a8c;       /* 中蓝灰 - 边框 */
  --frost-accent: #7ba3b8;       /* 青蓝 - 强调色 */
  --frost-light: #b8d4e0;        /* 浅蓝灰 - 次要元素 */
  --frost-dim: #8fa3b0;          /* 灰蓝 - 暗淡文字 */
  
  /* 背景系统 */
  --frost-bg: rgba(255, 255, 255, 0.7);        /* 半透明 */
  --frost-bg-solid: rgba(255, 255, 255, 0.85); /* 不透明 */
  
  /* 间距系统 */
  --content-padding: 1.2rem;
  --content-gap: 0.8rem;
  --section-gap: 1.8rem;
}
```

---

## 移动端优化

### 响应式布局

```css
/* 平板及以下（768px） */
- 导航栏：搜索框独立行，导航按钮横向滚动
- 图片网格：9列 → 6列
- 间距压缩：padding 和 font-size 缩小

/* 手机（480px） */
- 图片网格：6列 → 3列
- 触摸目标：最小 44x44px
- 触摸反馈：点击时缩放 + 透明度动画
```

---

## 性能优化

### 前端优化

1. **状态缓存**：保留各类型浏览状态，切换时无需重新加载
2. **事件委托**：父元素统一处理子元素事件，减少监听器数量
3. **搜索防抖**：300ms 延迟执行，避免频繁请求

### 后端优化

1. **图片压缩**：PNG/JPG → WebP，质量 90%
2. **图片清理**：手动扫描和清理未引用图片
3. **同步删除**：删除内容时自动删除关联图片

---

## 安全建议

**生产环境必须修改**：

1. `admin_data/config.json` 中的管理员密码
2. `admin_data/config.json` 中的 JWT `secret_key`
3. 使用 HTTPS 部署
4. 添加 API 限流中间件

---

## 备份与恢复

```bash
# Windows
Compress-Archive -Path admin_data,user_data -DestinationPath backup-$(Get-Date -Format "yyyyMMdd").zip

# Linux/Mac
tar -czf backup-$(date +%Y%m%d).tar.gz admin_data/ user_data/
```

---

## 设计原则

1. **关注点分离**：HTML/CSS/JS 独立，互不依赖
2. **单一职责**：每个模块只负责一件事
3. **显式优于隐式**：明确的依赖关系
4. **单页应用**：无刷新切换，流畅体验
5. **极简主义**：管理后台一切从简
6. **移动优先**：完整的移动端优化

详细架构: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 特色亮点

- ✅ **无框架依赖**：原生 JavaScript，永不过时
- ✅ **无数据库依赖**：JSON 文件存储，轻量部署
- ✅ **URL 分享**：每篇文章可独立分享
- ✅ **图片灯箱**：点击查看大图
- ✅ **图片管理**：智能压缩 + GIF 动图支持 + 清理功能
- ✅ **移动端优化**：完整的响应式支持
- ✅ **极简后台**：文字链接 + 1px 分隔线

---

**适用场景**：个人博客、技术笔记、作品集、小型内容站

**MIT License**
