"""
文件上传路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
from pathlib import Path
from PIL import Image
import io
from backend.routers.auth import get_current_admin

router = APIRouter()

# 管理员数据目录（统一存储所有管理员数据）
ADMIN_DATA_DIR = Path(__file__).parent.parent.parent / "admin_data"
IMAGES_DIR = ADMIN_DATA_DIR / "images"

# 确保目录存在
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 允许的图片格式（输入）
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}

# WebP 压缩质量（0-100，推荐85-95）
WEBP_QUALITY = 90

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

def convert_to_webp(image_data: bytes, original_filename: str) -> tuple:
    """
    将图片转换为WebP格式（GIF除外）
    返回: (webp_data, new_filename, original_size, compressed_size, compression_ratio)
    """
    try:
        # 如果是GIF，直接保存不转换
        if get_file_extension(original_filename) == '.gif':
            new_filename = f"{uuid.uuid4().hex}.gif"
            original_size = len(image_data)
            return image_data, new_filename, original_size, original_size, 0.0
        
        # 打开图片
        image = Image.open(io.BytesIO(image_data))
        
        # 如果是RGBA模式（PNG透明），保持透明度
        if image.mode == 'RGBA':
            pass
        # 如果是调色板模式，转换为RGB
        elif image.mode == 'P':
            image = image.convert('RGBA')
        # 其他模式转为RGB
        elif image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        
        # 生成新文件名（使用UUID + .webp）
        new_filename = f"{uuid.uuid4().hex}.webp"
        
        # 转换为WebP
        output = io.BytesIO()
        image.save(
            output, 
            format='WEBP',
            quality=WEBP_QUALITY,
            method=6  # 压缩方法（0-6，6最慢但压缩最好）
        )
        webp_data = output.getvalue()
        
        # 获取原始和压缩后的大小
        original_size = len(image_data)
        compressed_size = len(webp_data)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        return webp_data, new_filename, original_size, compressed_size, compression_ratio
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"图片处理失败: {str(e)}"
        )

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    admin: str = Depends(get_current_admin)
):
    """
    上传单张图片（自动转换为WebP）
    需要管理员权限
    """
    # 检查文件类型
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 转换为WebP
    webp_data, new_filename, original_size, compressed_size, compression_ratio = convert_to_webp(
        content, 
        file.filename
    )
    
    # 保存文件
    file_path = IMAGES_DIR / new_filename
    with open(file_path, 'wb') as f:
        f.write(webp_data)
    
    # 返回图片 URL
    image_url = f"/media/images/{new_filename}"
    
    return {
        "success": True,
        "url": image_url,
        "filename": new_filename,
        "original_filename": file.filename,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": f"{compression_ratio:.1f}%",
        "format": "webp"
    }

@router.post("/images")
async def upload_images(
    files: List[UploadFile] = File(...),
    admin: str = Depends(get_current_admin)
):
    """
    批量上传图片（自动转换为WebP）
    需要管理员权限
    """
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="一次最多上传 20 张图片"
        )
    
    uploaded_images = []
    errors = []
    
    for file in files:
        try:
            # 检查文件类型
            if not is_allowed_file(file.filename):
                errors.append({
                    "filename": file.filename,
                    "error": "不支持的文件类型"
                })
                continue
            
            # 读取文件内容
            content = await file.read()
            
            # 转换为WebP
            webp_data, new_filename, original_size, compressed_size, compression_ratio = convert_to_webp(
                content,
                file.filename
            )
            
            # 保存文件
            file_path = IMAGES_DIR / new_filename
            with open(file_path, 'wb') as f:
                f.write(webp_data)
            
            # 添加到成功列表
            uploaded_images.append({
                "url": f"/media/images/{new_filename}",
                "filename": new_filename,
                "original_filename": file.filename,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": f"{compression_ratio:.1f}%",
                "format": "webp"
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(uploaded_images) > 0,
        "uploaded": uploaded_images,
        "errors": errors,
        "total": len(files),
        "success_count": len(uploaded_images),
        "error_count": len(errors)
    }

@router.delete("/image/{filename}")
async def delete_image(
    filename: str,
    admin: str = Depends(get_current_admin)
):
    """
    删除图片
    需要管理员权限
    """
    file_path = IMAGES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")
    
    # 安全检查：确保文件在images目录下
    if not str(file_path.resolve()).startswith(str(IMAGES_DIR.resolve())):
        raise HTTPException(status_code=403, detail="无效的文件路径")
    
    # 删除文件
    file_path.unlink()
    
    return {
        "success": True,
        "message": "图片已删除"
    }