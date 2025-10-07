"""
公告管理路由 - 统一草稿系统
"""
from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import json
from datetime import datetime
from backend.routers.auth import get_current_admin

router = APIRouter()

# 数据目录
ADMIN_DATA_DIR = Path(__file__).parent.parent.parent / "admin_data"
DRAFTS_DIR = ADMIN_DATA_DIR / "drafts"
PUBLISHED_DIR = ADMIN_DATA_DIR / "published"

def ensure_dirs():
    """确保目录存在"""
    ADMIN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

def get_draft_path() -> Path:
    """获取草稿文件路径"""
    return DRAFTS_DIR / "announcement.json"

def get_content_path() -> Path:
    """获取正文发布文件路径"""
    return PUBLISHED_DIR / "announcement.json"

def read_json(file_path: Path) -> dict:
    """读取JSON文件"""
    if not file_path.exists():
        return {"posts": []}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"posts": []}

def write_json(file_path: Path, data: dict):
    """写入JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get("")
async def get_announcement():
    """获取已发布的公告（公开接口）"""
    content_path = get_content_path()
    data = read_json(content_path)
    posts = data.get("posts", [])
    
    # 只返回已发布的公告
    published = [p for p in posts if p.get('status') == 'published']
    
    # 转换为前端期望的 items 格式
    if published:
        latest = published[0]
        items = []
        
        # 添加文本内容
        if latest.get('content'):
            items.append({
                "type": "text",
                "content": latest.get('content')
            })
        
        # 添加图片
        for img_url in latest.get('images', []):
            items.append({
                "type": "image",
                "content": img_url
            })
        
        return {
            "items": items,
            "status": "published",
            "updated_at": latest.get('updated_at')
        }
    
    return {
        "items": [],
        "status": "draft",
        "updated_at": None
    }

# 以下接口与其他内容类型保持一致，放在 admin.py 路由中统一管理
