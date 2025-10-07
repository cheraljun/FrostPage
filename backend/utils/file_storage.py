"""
文件存储工具
用于读写 JSON 数据文件
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

# 数据目录
ADMIN_DATA_DIR = Path(__file__).parent.parent.parent / "admin_data"
USER_DATA_DIR = Path(__file__).parent.parent.parent / "user_data"

class ContentStorage:
    """内容存储管理器（正文内容存储）"""
    
    def __init__(self, content_type: str):
        """
        初始化存储管理器
        :param content_type: 内容类型 (research, media, activity, shop)
        """
        self.content_type = content_type
        # 正文文件存储在 published/ 目录
        self.file_path = ADMIN_DATA_DIR / "published" / f"{content_type}.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保数据文件和目录存在"""
        # 确保 published 目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save_data({"posts": []})
    
    def _load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有内容"""
        data = self._load_data()
        return data.get('posts', [])
    
    def get_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取内容"""
        posts = self.get_all()
        for post in posts:
            if post.get('id') == post_id:
                return post
        return None
    
    def create(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """创建新内容"""
        data = self._load_data()
        posts = data.get('posts', [])
        
        # 生成ID和时间戳
        new_post = {
            'id': str(uuid.uuid4()),
            'type': self.content_type,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            **content
        }
        
        posts.append(new_post)
        data['posts'] = posts
        self._save_data(data)
        
        return new_post
    
    def update(self, post_id: str, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新内容"""
        data = self._load_data()
        posts = data.get('posts', [])
        
        for i, post in enumerate(posts):
            if post.get('id') == post_id:
                # 保留原有的创建时间和ID
                updated_post = {
                    **post,
                    **content,
                    'id': post_id,
                    'created_at': post.get('created_at'),
                    'updated_at': datetime.utcnow().isoformat()
                }
                posts[i] = updated_post
                data['posts'] = posts
                self._save_data(data)
                return updated_post
        
        return None
    
    def delete(self, post_id: str) -> bool:
        """删除内容"""
        data = self._load_data()
        posts = data.get('posts', [])
        
        new_posts = [p for p in posts if p.get('id') != post_id]
        
        if len(new_posts) < len(posts):
            data['posts'] = new_posts
            self._save_data(data)
            return True
        
        return False


class ChatStorage:
    """聊天消息存储管理器"""
    
    def __init__(self):
        self.file_path = USER_DATA_DIR / "chat_messages.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保数据文件存在"""
        if not self.file_path.exists():
            self._save_data({"messages": []})
    
    def _load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的聊天消息"""
        data = self._load_data()
        messages = data.get('messages', [])
        return messages[-limit:] if len(messages) > limit else messages
    
    def add_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """添加聊天消息"""
        data = self._load_data()
        messages = data.get('messages', [])
        
        new_message = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            **message
        }
        
        messages.append(new_message)
        
        # 只保留最近500条消息
        if len(messages) > 500:
            messages = messages[-500:]
        
        data['messages'] = messages
        self._save_data(data)
        
        return new_message
