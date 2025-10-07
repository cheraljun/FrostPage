# FrostPage 架构设计文档

> 深入剖析单页应用的底层实现逻辑

---

## 设计哲学

**INTP 的逻辑追求**：
- 清晰的系统架构
- 严格的关注点分离
- 可验证的设计原则
- 无冗余的代码组织

**INFP 的美学追求**：
- 冰霜粗野主义视觉语言
- 每个元素都有存在理由
- 简洁而有力的表达

两者统一于：**合理的结构自然呈现美感**。

---

## 一、单页应用（SPA）架构

### 1.1 什么是单页应用？

**传统多页应用**：

```
用户点击链接
    ↓
浏览器发起 HTTP 请求
    ↓
服务器返回完整 HTML 页面
    ↓
浏览器刷新，重新解析 HTML/CSS/JS
    ↓
页面完全重新加载（白屏）
```

**单页应用**：

```
用户点击导航
    ↓
JavaScript 拦截点击事件
    ↓
更新页面状态（State）
    ↓
局部重新渲染（DOM 更新）
    ↓
视图切换完成（无刷新）
```

**本质区别**：单页应用将页面导航转化为**状态管理**问题。

### 1.2 StateManager（状态管理器）

**设计模式**：Observer（观察者） + Singleton（单例）

**数据结构**：

```javascript
class StateManager {
  currentType: string | null;     // 当前激活的内容类型
  states: {                        // 各类型独立状态
    research: State | null,
    media: State | null,
    activity: State | null,
    shop: State | null,
    chat: State | null
  };
  listeners: Function[];           // 订阅者列表
}

interface State {
  view: 'list' | 'detail' | 'chat' | 'empty';
  itemId: string | null;
}
```

**核心方法**：

```javascript
// 显示列表页
showList(type) {
  this.currentType = type;
  this.states[type] = { view: 'list', itemId: null };
  this.notify();  // 通知所有订阅者
}

// 显示详情页
showDetail(type, itemId) {
  this.currentType = type;
  this.states[type] = { view: 'detail', itemId };
  this.notify();
}

// 订阅状态变化
subscribe(listener) {
  this.listeners.push(listener);
}

// 通知订阅者
notify() {
  const state = this.getCurrentState();
  const type = this.getCurrentType();
  this.listeners.forEach(fn => fn(state, type));
}
```

**状态隔离机制**：

每个内容类型的状态独立保存：

```javascript
// 用户操作流程示例：
1. 点击"研究" → states.research = { view: 'list' }
2. 点击某篇文章 → states.research = { view: 'detail', itemId: '123' }
3. 切换到"媒体" → states.media = { view: 'list' }
4. 再切回"研究" → 自动恢复 { view: 'detail', itemId: '123' }
```

**优势**：用户切换内容类型后再切回，能回到之前的浏览位置。

### 1.3 MainContentArea（主内容区渲染器）

**职责**：将状态转换为视图。

**Observer 模式实现**：

```javascript
class MainContentArea {
  constructor(container, stateManager) {
    this.container = container;
    this.stateManager = stateManager;
    
    // 订阅状态变化
    this.stateManager.subscribe((state, type) => {
      this.render(state, type);
    });
  }
  
  render(state, type) {
    // 根据状态渲染不同视图
    switch (state.view) {
      case 'list':   this.renderList(type); break;
      case 'detail': this.renderDetail(type, state.itemId); break;
      case 'chat':   this.renderChat(); break;
      case 'empty':  this.renderEmpty(); break;
    }
  }
}
```

**单向数据流**：

```
StateManager (状态源)
      ↓
   notify()
      ↓
MainContentArea.render() (视图)
      ↓
   DOM 更新
```

**关键原则**：视图**永远不能**直接修改状态，必须通过 StateManager 提供的方法。

### 1.4 Hash 路由与 URL 分享

**设计动机**：

传统 SPA 的问题：
- 所有页面 URL 相同（`/index.html`）
- 无法分享特定内容
- 浏览器前进/后退不工作
- 刷新页面丢失状态

**解决方案**：Hash 路由（`#/type/view/id`）

**URL 格式**：

```
http://example.com/#/research/list         # 研究列表页
http://example.com/#/research/detail/123   # 研究详情页 ID=123
http://example.com/#/media/detail/456      # 媒体详情页 ID=456
http://example.com/#/chat                  # 聊天页
```

**实现机制**：

```javascript
// 1. 状态变化时更新 URL
updateUrl(type, view, itemId) {
  if (this.syncing) return;  // 防止循环
  
  let hash = '#/';
  if (type === 'chat') {
    hash += 'chat';
  } else if (view === 'list') {
    hash += `${type}/list`;
  } else if (view === 'detail') {
    hash += `${type}/detail/${itemId}`;
  }
  
  window.location.hash = hash;
}

// 2. URL 变化时同步状态
syncFromUrl() {
  const hash = window.location.hash.slice(2);  // 去掉 '#/'
  const parts = hash.split('/');
  
  if (parts[0] === 'chat') {
    this.showChat();
  } else if (parts[1] === 'list') {
    this.showList(parts[0]);
  } else if (parts[1] === 'detail') {
    this.showDetail(parts[0], parts[2]);
  }
}

// 3. 监听 URL 变化（浏览器前进/后退）
window.addEventListener('hashchange', () => this.syncFromUrl());
```

**双向绑定**：

```
State ⟷ URL

用户点击 → State 更新 → URL 更新
URL 变化 → State 同步 → 视图更新
```

**优势**：
- 每篇文章有唯一 URL
- 支持直接分享
- 浏览器前进/后退正常工作
- 刷新页面保持状态
- 无需服务器配置

### 1.5 完整的导航流程

**用户操作**：点击"研究"导航按钮

```javascript
// 1. 事件绑定（main.js）
btn.addEventListener('click', () => {
  const type = btn.dataset.nav;
  app.showList(type);
});

// 2. App 方法（main.js）
showList(type) {
  this.stateManager.showList(type);
}

// 3. StateManager 更新状态（core/StateManager.js）
showList(type) {
  this.currentType = 'research';
  this.states.research = { view: 'list', itemId: null };
  this.notify();
}

// 4. MainContentArea 响应（components/MainContentArea.js）
render(state, type) {
  // state = { view: 'list', itemId: null }
  // type = 'research'
  this.renderList('research');
}

// 5. 渲染列表视图
async renderList(type) {
  const posts = await api.get(`/content/${type}`);
  const html = posts.map(post => 
    new ContentCard(post).renderSimple()
  ).join('');
  this.container.innerHTML = html;
}
```

**整个过程无页面刷新，只有局部 DOM 更新。**

---

## 二、HTML/CSS/JS 分离架构

### 2.1 分离原则的深层逻辑

**为什么要分离？**

不仅是"代码组织"问题，而是**关注点分离**（Separation of Concerns）：

- **HTML** 关注**结构**：内容的语义和层次
- **CSS** 关注**表现**：视觉样式和布局
- **JavaScript** 关注**行为**：交互逻辑和状态管理

当三者混在一起时：
- 修改样式可能破坏逻辑
- 修改逻辑需要同时修改 HTML
- 组件难以复用
- 测试变得困难

### 2.2 分离的实现标准

#### HTML 层标准

**允许**：

```html
<!-- 语义化标签 -->
<nav class="admin-nav">
  <button class="nav-btn" data-nav="research">研究</button>
</nav>

<!-- data-* 属性传递数据 -->
<div class="card" data-post-id="123">...</div>
```

**禁止**：

```html
<!-- ✗ 内联样式 -->
<div style="color: red;">...</div>

<!-- ✗ 内联脚本 -->
<button onclick="handleClick()">...</button>

<!-- ✗ 表现性属性 -->
<font color="red">...</font>
```

#### CSS 层标准

**允许**：

```css
/* CSS 变量 */
:root {
  --frost-deep: #2c4a5c;
}

/* 伪类处理交互 */
.nav-btn:hover {
  background: var(--frost-accent);
}

/* 状态类 */
.nav-btn.active {
  background: var(--frost-deep);
}
```

**禁止**：

```css
/* ✗ 依赖 JavaScript 计算的样式 */
.element {
  width: calc(var(--js-computed-width));  /* 不应该 */
}
```

**关键**：CSS 必须独立工作，不依赖 JavaScript 状态。

#### JavaScript 层标准

**允许**：

```javascript
// 事件监听
btn.addEventListener('click', handler);

// 类名切换
element.classList.add('active');
element.classList.remove('inactive');

// 属性修改
element.setAttribute('data-state', 'loading');
```

**禁止**：

```javascript
// ✗ 直接操作样式
element.style.color = 'red';
element.style.display = 'none';

// ✗ 在 JS 中写 CSS
const styles = `
  .element { color: red; }
`;
```

**关键**：样式变化通过**类名切换**实现，不直接操作 `style` 属性。

### 2.3 分离的验证方法

**测试 1**：删除所有 CSS 文件
- 结果：页面应该显示正常的 HTML 结构
- 验证：HTML 的语义是否完整

**测试 2**：禁用 JavaScript
- 结果：页面应该显示静态内容
- 验证：基础内容是否可访问

**测试 3**：替换 CSS 文件
- 结果：应该能无缝切换主题
- 验证：样式是否完全独立

---

## 三、组件化与复用

### 3.1 组件分类

#### 渲染组件（Rendering Components）

**特征**：
- 纯函数：输入确定 → 输出确定
- 无副作用：不修改输入，不访问全局状态
- 可预测：相同输入永远产生相同输出

**示例**：

```javascript
class ContentCard {
  constructor(post) {
    this.post = post;  // 输入
  }
  
  renderSimple() {
    // 纯函数转换
    return `
      <div class="card">
        <h3>${this.post.title}</h3>
        <p>${this.post.content}</p>
      </div>
    `;
  }
}

// 使用
const card = new ContentCard(postData);
const html = card.renderSimple();  // 无副作用
```

#### 控制组件（Controller Components）

**特征**：
- 有副作用：API 请求、DOM 操作、状态更新
- 编排逻辑：协调多个渲染组件
- 处理异步：加载状态、错误处理

**示例**：

```javascript
class MainContentArea {
  async renderList(type) {
    // 副作用 1: API 请求
    const posts = await api.get(`/content/${type}`);
    
    // 副作用 2: DOM 操作
    this.container.innerHTML = posts.map(post => 
      new ContentCard(post).renderSimple()
    ).join('');
  }
}
```

### 3.2 组件复用原则

**1. 单一职责**

```javascript
// ✓ 好的设计
class ContentCard {
  render() { return html; }  // 只负责渲染
}

class MainContentArea {
  renderList() { ... }       // 只负责列表逻辑
}

// ✗ 不好的设计
class ContentCard {
  render() { ... }
  fetchData() { ... }        // 职责过多
  saveToDatabase() { ... }
}
```

**2. 明确接口**

```javascript
// 输入：post 对象
// 输出：HTML 字符串
class ContentCard {
  constructor(post: Post) { }
  render(): string { }
}
```

**3. 无全局依赖**

```javascript
// ✗ 依赖全局状态
class BadComponent {
  render() {
    return window.globalData.title;  // 耦合
  }
}

// ✓ 通过参数传入
class GoodComponent {
  constructor(data) {
    this.data = data;  // 显式依赖
  }
  render() {
    return this.data.title;
  }
}
```

### 3.3 事件委托优化

**问题**：大量元素需要绑定事件

```javascript
// ✗ 为每个卡片绑定事件（O(n) 监听器）
cards.forEach(card => {
  card.addEventListener('click', () => {
    handleClick(card.dataset.id);
  });
});
// 100 个卡片 = 100 个监听器
```

**解决**：事件委托（Event Delegation）

```javascript
// ✓ 在父元素上统一处理（O(1) 监听器）
container.addEventListener('click', (e) => {
  const card = e.target.closest('.card');
  if (card) {
    handleClick(card.dataset.id);
  }
});
// 100 个卡片 = 1 个监听器
```

**优势**：
- 内存占用更少
- 支持动态添加的元素
- 性能更好

---

## 四、极简管理后台设计

### 4.1 设计原则："一切从简"

**理念**：管理后台是给内容创作者使用的工具，不是展示给用户的界面，应该追求极致的简洁和效率。

**简化策略**：
1. 自适应导航 → 平均分配空间
2. 文字超链接 → 清晰操作语义
3. 无装饰边框 → 1px 细线分隔
4. 无背景色 → 透明/白色
5. 无大间距 → 紧凑布局
6. 无动画效果 → 直接反馈

### 4.2 导航栏自适应布局

**HTML 结构**（完全扁平化）：

```html
<nav class="admin-nav">
  <button class="nav-item nav-btn active" data-type="research">研究</button>
  <button class="nav-item nav-btn" data-type="media">媒体</button>
  <button class="nav-item nav-btn" data-type="activity">活动</button>
  <button class="nav-item nav-btn" data-type="shop">商店</button>
  <button class="nav-item nav-btn" data-type="announcement">公告</button>
  <button class="nav-item nav-btn" data-type="chat">留言</button>
  <button class="nav-item nav-btn" data-type="cleanup">清理</button>
  <button class="nav-item" id="logout-btn">退出</button>
</nav>
```

**CSS 实现**（Flexbox 自适应）：

```css
.admin-nav {
  display: flex;
  height: 3.5rem;
  border-bottom: 2px solid var(--frost-light);
}

.nav-item {
  flex: 1;                          /* 平均分配空间 */
  border-right: 1px solid var(--frost-light);
  background: transparent;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(123, 163, 184, 0.1);
}

.nav-btn.active {
  background: var(--frost-accent);
  color: white;
}
```

**优势**：
- 每个按钮占据相等宽度
- 响应式自适应：窗口变化时自动调整
- 无需手动计算宽度

### 4.3 按钮到文本链接的转变

**传统按钮设计**：

```html
<button class="btn btn-primary">编辑</button>
<button class="btn btn-danger">删除</button>
```

```css
.btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: 2px solid #0056b3;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

**极简文本链接**：

```html
<a href="#" class="action-link">编辑</a>
<a href="#" class="action-link danger">删除</a>
```

```css
.action-link {
  color: var(--frost-accent);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.action-link:hover {
  color: var(--frost-deep);
  border-bottom: 2px solid var(--frost-accent);
}

.action-link.danger {
  color: #c00;
}
```

**对比**：

| 项目 | 传统按钮 | 极简链接 |
|------|---------|---------|
| 视觉重量 | 重（有背景色） | 轻（只有文字） |
| 空间占用 | 大（padding 大） | 小（紧凑） |
| 扫描效率 | 低（颜色干扰） | 高（文字清晰） |
| 维护成本 | 高（样式复杂） | 低（几乎无样式） |

### 4.4 图片上传组件设计

**需求**：
- 支持多张图片上传（最多 16 张）
- 支持拖拽上传
- 点击"+"按钮可选择单张或多张
- 上传后预览，可删除

**旧设计问题**：

```
0 张图片时：[+][+][+][+][+][+][+][+][+][+][+][+][+][+][+][+]  (16 个 "+")
5 张图片时：[图1][图2][图3][图4][图5][+][+][+][+][+][+][+][+][+][+][+]  (11 个 "+")
```

**问题**：
- 视觉混乱：多个"+"号没有意义
- 用户困惑：点击任何"+"都是同一个操作

**新设计**：

```
0 张图片时：[+]  （只显示 1 个 "+"）
5 张图片时：[图1][图2][图3][图4][图5][+]  （5 张图 + 1 个 "+"）
16 张图片时：[图1][图2]...[图16]  （无 "+"，已满）
```

**实现逻辑**：

```javascript
renderImageGrid(images = []) {
  let html = '';
  
  // 渲染已上传的图片
  images.forEach((img, i) => {
    html += `
      <div class="img-cell has-img">
        <img src="${img}" alt="">
        <button class="remove" data-index="${i}">×</button>
      </div>
    `;
  });
  
  // 如果未达到上限（16 张），显示唯一的 "+" 按钮
  if (images.length < 16) {
    html += `
      <div class="img-cell empty add-image">
        <span>+</span>
      </div>
    `;
  }
  
  return html;
}
```

**CSS 布局**：

```css
#image-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  /* 4 列网格 */
  gap: 0.5rem;
}

/* 响应式：手机端 2 列 */
@media (max-width: 768px) {
  #image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**优势**：
- 逻辑清晰：1 个"+"= 1 个操作入口
- 视觉简洁：不占用多余空间
- 功能完整：支持单选和多选

### 4.5 图片清理功能

**设计动机**：防止未引用图片（orphan files）占用磁盘空间。

**场景分析**：

```
用户操作流程：
1. 新建文章，上传图片 A、B、C
2. 编辑时删除图片 B（从编辑器移除）
3. 点击保存

问题：图片 B 已从文章中移除，但仍存在于磁盘
原因：前端删除只是从编辑器移除，未调用删除 API
```

**解决方案**：手动清理机制

**为什么选择手动清理？**

| 方案 | 优点 | 缺点 | 选择 |
|------|------|------|------|
| 前端实时删除 | 立即生效 | 误删风险高、复杂度高 | ❌ |
| 后端定时清理 | 自动化 | 误删风险、需要宽限期逻辑 | ❌ |
| 手动清理 | 完全可控、安全 | 需要手动操作 | ✅ |

**实现架构**：

1. **扫描 API**（`GET /api/admin/cleanup/scan`）：

```python
# 1. 扫描磁盘所有图片
all_images = set()
for ext in ['*.webp', '*.gif']:
    for img_file in IMAGES_DIR.glob(ext):
        all_images.add(img_file.name)

# 2. 扫描所有 JSON 引用
referenced_images = set()
for content_type in ['research', 'media', ...]:
    for post in drafts + published:
        for img_url in post.get('images', []):
            referenced_images.add(img_url.split('/')[-1])

# 3. 计算差集
unreferenced = all_images - referenced_images

return {
    "total_images": len(all_images),
    "referenced_images": len(referenced_images),
    "unreferenced_count": len(unreferenced),
    "unreferenced_details": [...],
    "total_size_mb": ...
}
```

2. **清理 API**（`POST /api/admin/cleanup/execute`）：

```python
# 重新扫描 + 删除
for filename in unreferenced:
    (IMAGES_DIR / filename).unlink(missing_ok=True)

return {
    "deleted_count": len(unreferenced),
    "freed_space_mb": ...
}
```

**前端实现**（复用现有组件）：

关键设计：**不引入新 CSS 类，完全复用现有样式**

```javascript
renderCleanupPage(data) {
  // 统计信息（复用 .post-item）
  const statsHtml = `
    <div class="post-item">
      <div class="post-info">
        <div class="post-title">扫描结果</div>
        <div class="post-content">
          总图片：${data.total_images} 个 | 
          未引用图片：${data.unreferenced_count} 个
        </div>
      </div>
    </div>
  `;
  
  // 清理按钮（复用 .action-link）
  const actionHtml = `
    <div class="post-item">
      <div class="post-actions">
        <a href="#" class="action-link danger" id="cleanup-execute-btn">
          清理全部
        </a>
      </div>
    </div>
  `;
}
```

**复用原则的体现**：
- ✅ 零新增 CSS 代码
- ✅ 完全复用现有类
- ✅ 保持视觉一致性
- ✅ 维护成本为零

---

## 五、后端架构

### 5.1 图片处理策略

**设计目标**：平衡文件大小与视觉质量，同时支持动画格式。

**处理流程**：

```python
def convert_to_webp(image_data: bytes, original_filename: str):
    # 1. 检测 GIF 格式
    if get_file_extension(original_filename) == '.gif':
        # GIF 直接保存，保留动画效果
        new_filename = f"{uuid.uuid4().hex}.gif"
        return image_data, new_filename, original_size, original_size, 0.0
    
    # 2. 其他格式转换为 WebP
    image = Image.open(io.BytesIO(image_data))
    
    # 3. 模式转换
    if image.mode == 'RGBA':
        pass  # 保持透明度
    elif image.mode == 'P':
        image = image.convert('RGBA')  # 调色板模式
    else:
        image = image.convert('RGB')
    
    # 4. 保存为 WebP
    new_filename = f"{uuid.uuid4().hex}.webp"
    image.save(output, format='WEBP', quality=90, method=6)
```

**格式处理策略**：

| 格式 | 处理方式 | 理由 |
|------|---------|------|
| PNG | → WebP | 压缩率高（30-70%），支持透明度 |
| JPG | → WebP | 质量相近，文件更小 |
| **GIF** | **保持原样** | **保留动画效果** |
| BMP | → WebP | 大幅压缩 |
| TIFF | → WebP | 大幅压缩 |

**GIF 特殊处理的原因**：
- GIF 的核心价值在于动画
- WebP 转换会丢失动画，只保留第一帧
- 静态 GIF 几乎不存在（都是动图）

**文件命名**：

```python
new_filename = f"{uuid.uuid4().hex}.{ext}"
# 示例:
# a1b2c3d4e5f6.webp
# f7e8d9c0b1a2.gif
```

**优势**：
- UUID 确保唯一性，无冲突
- 扩展名明确标识格式
- 删除简单：直接匹配文件名

### 5.2 双存储模型

**设计动机**：

传统单存储方式：

```json
{
  "posts": [
    {"id": "1", "status": "draft", "content": "草稿"},
    {"id": "2", "status": "published", "content": "已发布"}
  ]
}
```

**问题**：
- 草稿和发布内容混在一起
- 查询需要过滤：`posts.filter(p => p.status === 'published')`
- 误操作风险高

**解决**：物理隔离

```
admin_data/
  ├─ drafts/research.json      # 草稿区
  └─ published/research.json   # 发布区
```

### 5.3 操作语义详解

#### 保存草稿

```python
POST /api/admin/research
Body: {"id": "1", "status": "draft", "content": "..."}

逻辑:
1. 写入 drafts/research.json
2. 如果 published/research.json 中存在该 ID:
   删除（相当于撤销发布）
```

**效果**：编辑已发布内容时，自动从发布区移除，变回草稿。

#### 发布草稿

```python
POST /api/admin/research/1/publish

逻辑:
1. 读取 drafts/research.json 中 ID=1 的内容
2. 更新其 status 为 "published"
3. 保存回 drafts/research.json
4. 复制到 published/research.json
```

**效果**：草稿区保留副本，发布区也有一份。

#### 编辑已发布内容

```python
POST /api/admin/research/1/edit

逻辑:
1. 从 published/research.json 中删除 ID=1
2. 更新 drafts/research.json 中 ID=1 的 status 为 "draft"
```

**效果**：立即从前台消失，进入草稿编辑状态。

#### 删除内容

```python
DELETE /api/admin/research/1

逻辑:
1. 从 drafts/research.json 中删除 ID=1
2. 从 published/research.json 中删除 ID=1
3. 删除关联图片
```

**效果**：彻底删除。

### 5.4 数据一致性

**不变量**（Invariants）：

1. 发布区的内容必须存在于草稿区
2. 发布区的内容 `status` 必须为 `"published"`
3. 草稿区是唯一的数据源

**验证**：

```python
# 检查一致性
published_ids = {post['id'] for post in published_posts}
draft_ids = {post['id'] for post in draft_posts}

assert published_ids.issubset(draft_ids)  # 发布的必须在草稿中
```

---

## 六、移动端优化策略

### 6.1 响应式布局断点

**断点选择**：

```css
@media (max-width: 768px)  /* 平板竖屏及以下 */
@media (max-width: 480px)  /* 手机 */
```

**断点选择理由**：
- 768px: iPad 竖屏（768×1024），常见平板分界点
- 480px: iPhone 竖屏（375-428），手机分界点

### 6.2 触摸目标优化

**人体工程学标准**：Apple HIG 和 Material Design 都建议最小触摸目标为 44×44pt。

**实现**：

```css
@media (max-width: 768px) {
  .nav-btn,
  .player-btn,
  .btn {
    min-width: 44px;
    min-height: 44px;
  }
}
```

**原因**：
- 手指触摸面积约 40-50px
- 小于 44px 的按钮难以准确点击

### 6.3 图片网格适配

**桌面端**：9 列（图片小，适合大屏浏览）  
**平板端**：6 列（适中）  
**手机端**：3 列（图片足够大，易于点击）

```css
/* 桌面 */
.post-images-grid.grid-4 {
  grid-template-columns: repeat(9, 1fr);
}

/* 平板 */
@media (max-width: 1024px) {
  .post-images-grid.grid-4 {
    grid-template-columns: repeat(6, 1fr);
  }
}

/* 手机 */
@media (max-width: 768px) {
  .post-images-grid.grid-4 {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 6.4 导航栏优化

**桌面端**：

```
┌────────────────────────────┐
│ 搜索 │ 研究 │ 媒体 │ 活动 │...│  ← 全部横向排列
└────────────────────────────┘
```

**移动端**：

```
┌────────────────┐
│ 搜索框         │  ← 占一整行
├────────────────┤
│ 研│媒│活│商│留 │  ← 横向滚动（可滑动）
└────────────────┘
```

**实现**：

```css
@media (max-width: 768px) {
  /* 搜索框独立一行 */
  .search-item {
    flex: 0 0 100%;
  }
  
  /* 导航按钮横向排列，支持滚动 */
  .nav-row {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;  /* iOS 平滑滚动 */
  }
  
  .nav-item.nav-btn {
    flex: 0 0 auto;
    min-width: 80px;
  }
}
```

---

## 七、性能优化策略

### 7.1 状态缓存

**策略**：保留各类型的浏览状态

```javascript
states: {
  research: { view: 'detail', itemId: '123' },  // 已缓存
  media: { view: 'list', itemId: null },        // 已缓存
  activity: null                                 // 未访问
}
```

**效果**：
- 用户从"研究详情"切换到"媒体列表"，再切回"研究"
- 无需重新加载，直接恢复到详情页
- 减少 API 请求

### 7.2 搜索防抖

**策略**：延迟执行搜索

```javascript
let timeout;
searchInput.addEventListener('input', () => {
  clearTimeout(timeout);
  timeout = setTimeout(performSearch, 300);
});
```

**效果**：
- 用户输入 "hello"
- 不会发送 5 次请求（h、he、hel、hell、hello）
- 只在最后一个字符输入后 300ms 发送 1 次请求

### 7.3 事件委托

**策略**：父元素统一处理

**效果**：
- 100 个卡片：1 个监听器 vs 100 个监听器
- 内存占用：~1KB vs ~100KB
- 动态添加元素无需重新绑定

---

## 八、设计模式应用

### Observer 模式
- StateManager → MainContentArea
- 解耦状态管理与视图渲染

### Singleton 模式
- StateManager 全局唯一实例
- 确保状态集中管理

### Factory 模式
- EmptyState.loading(), EmptyState.error()
- 快速创建不同状态的组件

### Strategy 模式
- MainContentArea.render() 根据 state.view 切换策略
- renderList / renderDetail / renderChat

---

## 九、设计权衡

**优势**：
- 无框架依赖，轻量级（<50KB JS）
- 架构清晰，易于理解和学习
- 代码组织合理，易于维护和扩展
- URL 分享功能，每篇文章可独立分享
- 完整的移动端优化
- 极简管理后台

**局限**：
- 手动状态管理，复杂度较高
- JSON 存储，不适合大规模数据（>1000 篇）
- 无并发控制，适用于单用户管理场景
- Hash 路由对 SEO 不友好（需 SSR 解决）

**适用场景**：
- 个人博客系统
- 小型内容管理系统
- 技术演示项目
- 学习 SPA 架构的实践项目

---

**设计哲学**：美学与逻辑的统一，简洁与深度的平衡。
