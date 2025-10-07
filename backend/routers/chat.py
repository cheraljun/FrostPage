"""
聊天消息路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pathlib import Path
import json
import uuid
from datetime import datetime
from pydantic import BaseModel
from backend.routers.auth import get_current_admin

router = APIRouter()

# 聊天消息文件路径
USER_DATA_DIR = Path(__file__).parent.parent.parent / "user_data"
CHAT_FILE = USER_DATA_DIR / "chat_messages.json"

class ChatMessage(BaseModel):
    """聊天消息模型"""
    user: str
    text: str
    timestamp: str = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    messages: List[Dict[str, Any]]

def read_messages() -> List[Dict[str, Any]]:
    """读取聊天消息"""
    if not CHAT_FILE.exists():
        return []
    
    with open(CHAT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('messages', [])

def write_messages(messages: List[Dict[str, Any]]):
    """写入聊天消息"""
    USER_DATA_DIR.mkdir(exist_ok=True)
    
    with open(CHAT_FILE, 'w', encoding='utf-8') as f:
        json.dump({'messages': messages}, f, ensure_ascii=False, indent=2)

@router.get("/messages", response_model=ChatResponse)
async def get_messages(limit: int = 50):
    """
    获取聊天消息（支持限制数量）
    """
    try:
        messages = read_messages()
        # 限制返回数量
        if limit > 0:
            messages = messages[-limit:]
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取消息失败: {str(e)}")

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, admin: str = Depends(get_current_admin)):
    """
    删除单条消息（需要管理员权限）
    """
    try:
        messages = read_messages()
        
        # 查找要删除的消息
        message_to_delete = None
        for msg in messages:
            if msg.get('id') == message_id:
                message_to_delete = msg
                break
        
        if not message_to_delete:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        # 删除消息
        messages = [msg for msg in messages if msg.get('id') != message_id]
        write_messages(messages)
        
        return {"success": True, "message": "消息已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")

@router.delete("/messages")
async def clear_all_messages(admin: str = Depends(get_current_admin)):
    """
    清空所有消息（需要管理员权限）
    """
    try:
        write_messages([])
        return {"success": True, "message": "所有消息已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空消息失败: {str(e)}")

@router.post("/messages")
async def send_message(message: ChatMessage):
    """
    发送新消息
    """
    try:
        # 读取现有消息
        messages = read_messages()
        
        # 添加时间戳和ID（使用 user 和 text 字段与前端保持一致）
        new_message = {
            "id": str(uuid.uuid4()),
            "user": message.user,
            "text": message.text,
            "timestamp": message.timestamp or datetime.now().isoformat()
        }
        
        # 添加到消息列表
        messages.append(new_message)
        
        # 只保留最近100条消息
        if len(messages) > 100:
            messages = messages[-100:]
        
        # 写入文件
        write_messages(messages)
        
        return {"success": True, "message": new_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

