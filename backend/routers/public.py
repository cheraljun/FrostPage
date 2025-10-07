"""
公开API路由（无需认证）
"""
from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.content import ContentResponse
from backend.utils.file_storage import ContentStorage

router = APIRouter()

@router.get("/{content_type}", response_model=List[ContentResponse])
async def get_public_content(content_type: str):
    """
    获取公开发布的内容（只返回已发布的内容）
    """
    if content_type not in ['research', 'media', 'activity', 'shop', 'announcement']:
        raise HTTPException(status_code=400, detail="无效的内容类型")
    
    storage = ContentStorage(content_type)
    all_posts = storage.get_all()
    
    # 只返回已发布的内容，按创建时间倒序
    published_posts = [p for p in all_posts if p.get('status') == 'published']
    published_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return published_posts
