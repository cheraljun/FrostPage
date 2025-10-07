"""
配置API路由（公开接口）
返回前端需要的配置信息
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent.parent / "admin_data" / "config.json"

def read_config() -> dict:
    """读取配置文件"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置失败: {str(e)}")

@router.get("/stream")
async def get_stream_config():
    """
    获取电台流配置（公开接口）
    """
    config = read_config()
    stream_config = config.get('stream', {})
    
    return {
        "url": stream_config.get('url', 'https://n10as.radiocult.fm/stream'),
        "name": stream_config.get('name', 'RadioCult.fm')
    }

