"""
认证路由
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.schemas.auth import LoginRequest, TokenResponse
from backend.utils.auth import verify_admin, create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    管理员登录
    """
    if not verify_admin(request.username, request.password):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": request.username})
    
    return TokenResponse(access_token=access_token)

@router.get("/verify")
async def verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    验证 token 是否有效
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token 无效或已过期"
        )
    
    return {
        "valid": True,
        "username": payload.get("sub")
    }

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    获取当前登录的管理员（依赖注入）
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="未授权：请先登录"
        )
    
    return payload.get("sub")
