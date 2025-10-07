"""
应用配置文件
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置
DATABASE_URL = f"sqlite:///{BASE_DIR}/blog.db"

# 媒体文件路径
MEDIA_ROOT = BASE_DIR / "frontend" / "media"
IMAGES_DIR = MEDIA_ROOT / "images"
AUDIO_DIR = MEDIA_ROOT / "audio"
VIDEOS_DIR = MEDIA_ROOT / "videos"

# 上传文件配置
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg"}

# 应用配置
APP_NAME = "FrostPage"
APP_DESCRIPTION = "个人博客网站"
VERSION = "1.0.0"

