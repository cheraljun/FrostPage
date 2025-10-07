"""
FastAPI主应用入口
提供静态文件服务和API路由
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径（使用 resolve() 确保获取绝对路径）
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# ========== 首先初始化所有必需的目录和文件 ==========
def init_directories():
    """在应用启动前初始化所有必需的目录和文件"""
    # 1. 创建用户数据目录
    user_dir = ROOT_DIR / "user_data"
    user_dir.mkdir(exist_ok=True)
    
    chat_file = user_dir / "chat_messages.json"
    if not chat_file.exists():
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump({"messages": []}, f, ensure_ascii=False, indent=2)
    
    # 2. 创建管理员数据目录结构
    admin_dir = ROOT_DIR / "admin_data"
    admin_dir.mkdir(exist_ok=True)
    
    # 创建草稿目录
    drafts_dir = admin_dir / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    
    # 创建正文发布目录
    published_dir = admin_dir / "published"
    published_dir.mkdir(exist_ok=True)
    
    # 创建图片目录
    images_dir = admin_dir / "images"
    images_dir.mkdir(exist_ok=True)
    
    # 创建书籍目录
    book_dir = admin_dir / "book"
    book_dir.mkdir(exist_ok=True)
    
    # 3. 初始化配置文件
    config_file = admin_dir / "config.json"
    if not config_file.exists():
        default_config = {
            "admin": {
                "username": "admin",
                "password": "password"
            },
            "jwt": {
                "secret_key": "your-secret-key-change-in-production",
                "algorithm": "HS256",
                "access_token_expire_minutes": 1440
            },
            "stream": {
                "url": "https://n10as.radiocult.fm/stream",
                "name": "RadioCult.fm"
            }
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    # 4. 初始化所有内容类型的空文件
    content_types = ['research', 'media', 'activity', 'shop', 'announcement']
    
    for content_type in content_types:
        # 草稿文件
        draft_file = drafts_dir / f"{content_type}.json"
        if not draft_file.exists():
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump({"posts": []}, f, ensure_ascii=False, indent=2)
        
        # 正文发布文件（在 published 目录）
        published_file = published_dir / f"{content_type}.json"
        if not published_file.exists():
            with open(published_file, 'w', encoding='utf-8') as f:
                json.dump({"posts": []}, f, ensure_ascii=False, indent=2)

# 初始化目录（必须在挂载静态文件之前）
init_directories()

# 创建FastAPI应用
app = FastAPI(
    title="FrostPage API",
    description="个人博客网站的后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（使用绝对路径，不依赖工作目录）
app.mount("/css", StaticFiles(directory=str(ROOT_DIR / "frontend/css")), name="css")
app.mount("/js", StaticFiles(directory=str(ROOT_DIR / "frontend/js")), name="js")
app.mount("/pages", StaticFiles(directory=str(ROOT_DIR / "frontend/pages")), name="pages")
app.mount("/admin-static", StaticFiles(directory=str(ROOT_DIR / "frontend/admin")), name="admin-static")
app.mount("/images", StaticFiles(directory=str(ROOT_DIR / "frontend/images")), name="images")

# 挂载管理员数据目录（图片等资源）
app.mount("/media/images", StaticFiles(directory=str(ROOT_DIR / "admin_data/images")), name="admin-images")

# 根路由 - 返回首页（SPA入口）
@app.get("/")
async def read_root():
    return FileResponse(str(ROOT_DIR / "frontend/index.html"))

# 管理员路由
@app.get("/admin/login")
async def admin_login_page():
    return FileResponse(str(ROOT_DIR / "frontend/admin/login.html"))

@app.get("/admin")
async def admin_page():
    return FileResponse(str(ROOT_DIR / "frontend/admin/index.html"))

# 健康检查
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# 导入API路由
from backend.routers import auth, admin, public, upload, search, chat, draft, book, announcement, config

# 认证路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])

# 管理员内容管理路由
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])

# 公开内容路由
app.include_router(public.router, prefix="/api/content", tags=["公开内容"])

# 配置路由（公开）
app.include_router(config.router, prefix="/api/config", tags=["配置"])

# 文件上传路由
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])

# 搜索路由
app.include_router(search.router, prefix="/api", tags=["搜索"])

# 聊天路由
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])

# 草稿路由
app.include_router(draft.router, prefix="/api/draft", tags=["草稿"])

# 书籍滚动路由
app.include_router(book.router, prefix="/api/book", tags=["书籍"])

# 公告路由
app.include_router(announcement.router, prefix="/api/announcement", tags=["公告"])

def convert_background_to_webp():
    """将背景图片转换为 WebP 格式"""
    from PIL import Image
    from pathlib import Path
    
    images_dir = ROOT_DIR / "frontend" / "images"
    images_dir.mkdir(exist_ok=True)
    
    # 检查是否已有 WebP 格式
    webp_path = images_dir / "background.webp"
    if webp_path.exists():
        print("✅ 背景图片已是 WebP 格式")
        return "background.webp"
    
    # 查找其他格式的背景图片
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        bg_path = images_dir / f"background{ext}"
        if bg_path.exists():
            print(f"🔄 发现 {bg_path.name}，正在转换为 WebP 格式...")
            try:
                # 打开图片并转换为 WebP
                img = Image.open(bg_path)
                # 如果是 PNG 带透明度，保留 alpha 通道
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
                
                # 保存为 WebP，质量设为 85
                img.save(webp_path, 'WEBP', quality=85)
                print(f"✅ 成功转换为 WebP 格式: {webp_path.name}")
                
                # 更新 CSS 文件
                update_css_background_path("background.webp")
                
                return "background.webp"
            except Exception as e:
                print(f"❌ 转换失败: {e}")
                return f"background{ext}"
    
    print("⚠️  未找到背景图片文件")
    return None

def update_css_background_path(filename):
    """更新 CSS 文件中的背景图片路径"""
    css_file = ROOT_DIR / "frontend" / "css" / "style.css"
    if not css_file.exists():
        return
    
    content = css_file.read_text(encoding='utf-8')
    
    # 替换所有背景图片引用
    import re
    pattern = r"url\(['\"]?\.\./images/background\.[a-zA-Z]+['\"]?\)"
    replacement = f"url('../images/{filename}')"
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        css_file.write_text(new_content, encoding='utf-8')
        print(f"✅ 已更新 CSS 文件中的背景图片路径: {filename}")

if __name__ == "__main__":
    import uvicorn
    
    # 转换背景图片为 WebP 格式
    print("\n" + "=" * 50)
    convert_background_to_webp()
    print("=" * 50 + "\n")
    
    print("🚀 启动服务器...")
    print("📍 访问地址: http://127.0.0.1:8000")
    print("🔐 管理后台: http://127.0.0.1:8000/admin/login")
    print("👤 默认账号: admin / password")
    print("-" * 50)
    
    # # ========== 开发环境配置 ==========
    # uvicorn.run(
    #     app, 
    #     host="127.0.0.1", 
    #     port=8000,
    #     reload=True,              # 代码变更自动重载
    #     log_level="info"          # 详细日志
    # )
    
    # ========== 生产环境配置（2核2G服务器优化）==========
    uvicorn.run(
        "main:app",
        host="0.0.0.0",              # 监听所有网络接口
        port=8000,
        log_level="info",            # 显示info级别日志（便于调试）
        limit_concurrency=200,       # 2核2G服务器的合理并发数
        timeout_keep_alive=60,       # Keep-Alive超时（节省连接资源）
        access_log=False             # 禁用访问日志（节省I/O）
    )

