"""
管理员内容管理路由（简化版 - 以草稿为主）
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pathlib import Path
import json
from datetime import datetime
from backend.routers.auth import get_current_admin

router = APIRouter()

# 数据目录
ADMIN_DATA_DIR = Path(__file__).parent.parent.parent / "admin_data"
DRAFTS_DIR = ADMIN_DATA_DIR / "drafts"
PUBLISHED_DIR = ADMIN_DATA_DIR / "published"
IMAGES_DIR = ADMIN_DATA_DIR / "images"

def ensure_dirs():
    """确保目录存在"""
    ADMIN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

def get_draft_path(content_type: str) -> Path:
    """获取草稿文件路径"""
    if content_type not in ['research', 'media', 'activity', 'shop', 'announcement']:
        raise HTTPException(status_code=400, detail="无效的内容类型")
    return DRAFTS_DIR / f"{content_type}.json"

def get_content_path(content_type: str) -> Path:
    """获取正文发布文件路径"""
    if content_type not in ['research', 'media', 'activity', 'shop', 'announcement']:
        raise HTTPException(status_code=400, detail="无效的内容类型")
    return PUBLISHED_DIR / f"{content_type}.json"

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

@router.get("/{content_type}")
async def get_all_drafts(
    content_type: str,
    admin: str = Depends(get_current_admin)
):
    """
    获取所有草稿（包括 draft 和 published 状态）
    管理员看到所有内容
    """
    draft_path = get_draft_path(content_type)
    data = read_json(draft_path)
    return data.get("posts", [])

@router.post("/{content_type}")
async def save_draft(
    content_type: str,
    post_data: dict,
    admin: str = Depends(get_current_admin)
):
    """
    保存草稿（新建或更新）
    如果状态是 draft，同时从正文中删除（撤销发布）
    """
    ensure_dirs()
    draft_path = get_draft_path(content_type)
    content_path = get_content_path(content_type)
    
    data = read_json(draft_path)
    posts = data.get("posts", [])
    
    # 添加时间戳
    post_data['updated_at'] = datetime.now().isoformat()
    if 'created_at' not in post_data:
        post_data['created_at'] = datetime.now().isoformat()
    if 'id' not in post_data:
        post_data['id'] = datetime.now().strftime('%Y%m%d%H%M%S%f')
    
    # 查找是否已存在
    existing_index = None
    for i, post in enumerate(posts):
        if post.get('id') == post_data['id']:
            existing_index = i
            break
    
    # 🔥 如果是更新操作，删除被移除的图片
    if existing_index is not None:
        old_post = posts[existing_index]
        old_images = set(old_post.get('images', []))
        new_images = set(post_data.get('images', []))
        removed_images = old_images - new_images
        
        for img_url in removed_images:
            filename = img_url.split('/')[-1]
            (IMAGES_DIR / filename).unlink(missing_ok=True)
    
    # 更新或添加
    if existing_index is not None:
        posts[existing_index] = post_data
    else:
        posts.insert(0, post_data)
    
    data['posts'] = posts
    write_json(draft_path, data)
    
    # 如果保存为草稿状态，从正文中删除（撤销发布）
    if post_data.get('status') == 'draft':
        content_data = read_json(content_path)
        content_posts = content_data.get("posts", [])
        # 删除正文中对应的文章
        content_posts = [p for p in content_posts if p.get('id') != post_data['id']]
        content_data['posts'] = content_posts
        write_json(content_path, content_data)
    
    return post_data

@router.post("/{content_type}/{post_id}/publish")
async def publish_draft(
    content_type: str,
    post_id: str,
    admin: str = Depends(get_current_admin)
):
    """
    发布草稿：
    1. 更新草稿状态为 published
    2. 复制到正文区
    """
    ensure_dirs()
    draft_path = get_draft_path(content_type)
    content_path = get_content_path(content_type)
    
    # 读取草稿
    draft_data = read_json(draft_path)
    posts = draft_data.get("posts", [])
    
    # 找到要发布的文章
    post_to_publish = None
    for post in posts:
        if post.get('id') == post_id:
            post['status'] = 'published'
            post['published_at'] = datetime.now().isoformat()
            post_to_publish = post
            break
    
    if not post_to_publish:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    # 保存更新后的草稿
    write_json(draft_path, draft_data)
    
    # 复制到正文
    content_data = read_json(content_path)
    content_posts = content_data.get("posts", [])
    
    # 查找是否已存在该ID的正文
    existing_index = None
    for i, post in enumerate(content_posts):
        if post.get('id') == post_id:
            existing_index = i
            break
    
    # 更新或添加到正文
    if existing_index is not None:
        content_posts[existing_index] = post_to_publish
    else:
        content_posts.insert(0, post_to_publish)
    
    content_data['posts'] = content_posts
    write_json(content_path, content_data)
    
    return {"success": True, "message": "发布成功"}

@router.post("/{content_type}/{post_id}/edit")
async def edit_post(
    content_type: str,
    post_id: str,
    admin: str = Depends(get_current_admin)
):
    """
    编辑文章（以草稿为主）：
    1. 从草稿中查找要编辑的文章
    2. 立即从正文中删除该文章（避免重复显示）
    3. 保持草稿不变，让用户编辑
    """
    ensure_dirs()
    draft_path = get_draft_path(content_type)
    content_path = get_content_path(content_type)
    
    # 读取草稿和正文
    draft_data = read_json(draft_path)
    content_data = read_json(content_path)
    
    # 从草稿中查找要编辑的文章（草稿是主数据源）
    post_to_edit = None
    for post in draft_data.get("posts", []):
        if post.get('id') == post_id:
            post_to_edit = post.copy()
            break
    
    if not post_to_edit:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    # 立即从正文中删除该文章（避免重复显示）
    content_posts = content_data.get("posts", [])
    content_posts = [p for p in content_posts if p.get('id') != post_id]
    content_data['posts'] = content_posts
    write_json(content_path, content_data)
    
    # 更新草稿中的文章状态为 draft（确保状态正确）
    post_to_edit['status'] = 'draft'
    post_to_edit['updated_at'] = datetime.now().isoformat()
    
    # 更新草稿中的文章
    draft_posts = draft_data.get("posts", [])
    for i, post in enumerate(draft_posts):
        if post.get('id') == post_id:
            draft_posts[i] = post_to_edit
            break
    
    draft_data['posts'] = draft_posts
    write_json(draft_path, draft_data)
    
    return {"success": True, "message": "已进入编辑模式，文章已从正文中移除"}

@router.delete("/{content_type}/{post_id}")
async def delete_draft(
    content_type: str,
    post_id: str,
    admin: str = Depends(get_current_admin)
):
    """
    删除草稿：
    1. 删除草稿
    2. 同时删除对应的正文
    3. 同步删除关联的图片文件
    """
    ensure_dirs()
    draft_path = get_draft_path(content_type)
    content_path = get_content_path(content_type)
    
    # 从草稿中删除（先找到文章并删除图片）
    draft_data = read_json(draft_path)
    posts = draft_data.get("posts", [])
    
    # 🔥 删除图片文件
    post_to_delete = next((p for p in posts if p.get('id') == post_id), None)
    if post_to_delete and post_to_delete.get('images'):
        for img_url in post_to_delete['images']:
            filename = img_url.split('/')[-1]
            (IMAGES_DIR / filename).unlink(missing_ok=True)
    
    posts = [p for p in posts if p.get('id') != post_id]
    draft_data['posts'] = posts
    write_json(draft_path, draft_data)
    
    # 从正文中删除
    content_data = read_json(content_path)
    content_posts = content_data.get("posts", [])
    content_posts = [p for p in content_posts if p.get('id') != post_id]
    content_data['posts'] = content_posts
    write_json(content_path, content_data)
    
    return {"success": True, "message": "删除成功"}

@router.get("/cleanup/scan")
async def scan_unreferenced_images(admin: str = Depends(get_current_admin)):
    """
    扫描未引用图片（不删除）
    """
    ensure_dirs()
    
    # 扫描磁盘所有图片
    all_images = set()
    if IMAGES_DIR.exists():
        for ext in ['*.webp', '*.gif']:
            for img_file in IMAGES_DIR.glob(ext):
                all_images.add(img_file.name)
    
    # 扫描所有JSON中引用的图片
    referenced_images = set()
    
    # 扫描草稿
    for content_type in ['research', 'media', 'activity', 'shop', 'announcement']:
        draft_path = get_draft_path(content_type)
        draft_data = read_json(draft_path)
        for post in draft_data.get("posts", []):
            for img_url in post.get("images", []):
                filename = img_url.split('/')[-1]
                referenced_images.add(filename)
    
    # 扫描正文
    for content_type in ['research', 'media', 'activity', 'shop', 'announcement']:
        content_path = get_content_path(content_type)
        content_data = read_json(content_path)
        for post in content_data.get("posts", []):
            for img_url in post.get("images", []):
                filename = img_url.split('/')[-1]
                referenced_images.add(filename)
    
    # 计算未引用图片
    unreferenced = all_images - referenced_images
    
    # 获取详细信息
    unreferenced_details = []
    total_size = 0
    for filename in unreferenced:
        file_path = IMAGES_DIR / filename
        if file_path.exists():
            size = file_path.stat().st_size
            total_size += size
            unreferenced_details.append({
                "filename": filename,
                "size": size,
                "size_mb": round(size / (1024 * 1024), 2)
            })
    
    return {
        "total_images": len(all_images),
        "referenced_images": len(referenced_images),
        "unreferenced_count": len(unreferenced),
        "unreferenced_details": unreferenced_details,
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }

@router.post("/cleanup/execute")
async def cleanup_unreferenced_images(admin: str = Depends(get_current_admin)):
    """
    执行清理未引用图片
    """
    ensure_dirs()
    
    # 扫描磁盘所有图片
    all_images = set()
    if IMAGES_DIR.exists():
        for ext in ['*.webp', '*.gif']:
            for img_file in IMAGES_DIR.glob(ext):
                all_images.add(img_file.name)
    
    # 扫描所有JSON中引用的图片
    referenced_images = set()
    
    # 扫描草稿
    for content_type in ['research', 'media', 'activity', 'shop', 'announcement']:
        draft_path = get_draft_path(content_type)
        draft_data = read_json(draft_path)
        for post in draft_data.get("posts", []):
            for img_url in post.get("images", []):
                filename = img_url.split('/')[-1]
                referenced_images.add(filename)
    
    # 扫描正文
    for content_type in ['research', 'media', 'activity', 'shop', 'announcement']:
        content_path = get_content_path(content_type)
        content_data = read_json(content_path)
        for post in content_data.get("posts", []):
            for img_url in post.get("images", []):
                filename = img_url.split('/')[-1]
                referenced_images.add(filename)
    
    # 计算未引用图片
    unreferenced = all_images - referenced_images
    
    # 删除未引用图片
    deleted_count = 0
    freed_space = 0
    
    for filename in unreferenced:
        file_path = IMAGES_DIR / filename
        if file_path.exists():
            size = file_path.stat().st_size
            file_path.unlink()
            deleted_count += 1
            freed_space += size
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "freed_space": freed_space,
        "freed_space_mb": round(freed_space / (1024 * 1024), 2)
    }
