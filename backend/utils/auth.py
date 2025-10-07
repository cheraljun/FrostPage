"""
JWT 认证工具
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from pathlib import Path

# 配置文件路径
CONFIG_PATH = Path(__file__).parent.parent.parent / "admin_data" / "config.json"

def ensure_config():
    """确保配置文件存在"""
    if not CONFIG_PATH.exists():
        # 创建目录
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建默认配置
        default_config = {
            "admin": {
                "username": "admin",
                "password": "password"
            },
            "jwt": {
                "secret_key": "your-secret-key-change-in-production",
                "algorithm": "HS256",
                "access_token_expire_minutes": 1440
            }
        }
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

def load_config():
    """加载配置文件"""
    ensure_config()
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_admin(username: str, password: str) -> bool:
    """验证管理员账号密码"""
    config = load_config()
    admin = config.get('admin', {})
    return username == admin.get('username') and password == admin.get('password')

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    config = load_config()
    jwt_config = config.get('jwt', {})
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=jwt_config.get('access_token_expire_minutes', 1440))
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        jwt_config.get('secret_key'), 
        algorithm=jwt_config.get('algorithm', 'HS256')
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """验证 JWT token"""
    try:
        config = load_config()
        jwt_config = config.get('jwt', {})
        
        payload = jwt.decode(
            token, 
            jwt_config.get('secret_key'), 
            algorithms=[jwt_config.get('algorithm', 'HS256')]
        )
        return payload
    except JWTError:
        return None
