"""
草稿管理路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pathlib import Path
import json
from backend.routers.auth import get_current_admin

router = APIRouter()

# 草稿目录路径
ADMIN_DATA_DIR = Path(__file__).parent.parent.parent / "admin_data"
DRAFTS_DIR = ADMIN_DATA_DIR / "drafts"

def ensure_drafts_dir():
    """确保草稿目录存在"""
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

def get_draft_path(content_type: str) -> Path:
    """获取草稿文件路径"""
    if content_type not in ['research', 'media', 'activity', 'shop']:
        raise HTTPException(status_code=400, detail="无效的内容类型")
    return DRAFTS_DIR / f"{content_type}.json"

@router.get("/{content_type}")
async def get_draft(
    content_type: str,
    admin: str = Depends(get_current_admin)
):
    """
    获取指定类型的草稿
    """
    draft_path = get_draft_path(content_type)
    
    if not draft_path.exists():
        return {"posts": []}
    
    try:
        with open(draft_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取草稿失败: {str(e)}")

@router.post("/{content_type}")
async def save_draft(
    content_type: str,
    draft_data: Dict[str, Any],
    admin: str = Depends(get_current_admin)
):
    """
    保存草稿
    """
    ensure_drafts_dir()
    draft_path = get_draft_path(content_type)
    
    try:
        with open(draft_path, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "message": "草稿保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存草稿失败: {str(e)}")

@router.post("/{content_type}/publish")
async def publish_draft(
    content_type: str,
    admin: str = Depends(get_current_admin)
):
    """
    发布草稿到正文（将草稿复制到正文）
    """
    draft_path = get_draft_path(content_type)
    content_path = ADMIN_DATA_DIR / f"{content_type}.json"
    
    if not draft_path.exists():
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    try:
        # 读取草稿
        with open(draft_path, 'r', encoding='utf-8') as f:
            draft_data = json.load(f)
        
        # 写入正文
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "message": "发布成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")

