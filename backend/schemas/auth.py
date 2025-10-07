"""
认证相关的数据模式
"""
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token数据"""
    username: Optional[str] = None
