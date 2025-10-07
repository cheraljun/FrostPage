"""
搜索路由 - 直接从 admin_data 读取并搜索
"""
from fastapi import APIRouter, Query
from typing import List, Dict, Any
import json
from pathlib import Path

router = APIRouter()

# admin_data 目录路径
ADMIN_DATA_DIR = Path(__file__).parent.parent.parent / "admin_data"
PUBLISHED_DIR = ADMIN_DATA_DIR / "published"

@router.get("/search")
async def search_content(q: str = Query(..., min_length=1)):
    """
    全局搜索 - 搜索所有已发布内容
    :param q: 搜索关键词
    """
    keyword = q.lower()
    results = {
        'research': [],
        'media': [],
        'activity': [],
        'shop': [],
        'total': 0
    }
    
    # 搜索所有类型
    content_types = ['research', 'media', 'activity', 'shop']
    
    for content_type in content_types:
        file_path = PUBLISHED_DIR / f"{content_type}.json"
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                posts = data.get('posts', [])
                
                # 过滤匹配的内容
                for post in posts:
                    # 只搜索已发布的内容
                    if post.get('status') != 'published':
                        continue
                    
                    title = (post.get('title') or '').lower()
                    content = (post.get('content') or '').lower()
                    
                    # 模糊匹配
                    if keyword in title or keyword in content:
                        # 计算相关度
                        relevance = 0
                        if keyword in title:
                            relevance += 10
                        if keyword in content:
                            relevance += 1
                        
                        # 添加类型和相关度
                        post_with_meta = {
                            **post,
                            'type': content_type,
                            'relevance': relevance
                        }
                        results[content_type].append(post_with_meta)
        
        except Exception as e:
            print(f"搜索 {content_type} 失败: {e}")
            continue
    
    # 计算总数
    results['total'] = sum(len(results[t]) for t in content_types)
    
    # 对每个类型的结果按相关度和时间排序
    for content_type in content_types:
        results[content_type].sort(
            key=lambda x: (-x.get('relevance', 0), x.get('created_at', '')),
            reverse=True
        )
    
    return results
