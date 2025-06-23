"""
API客户端 - 小红书起号助手
"""
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from asyncio_throttle import Throttler
from config import config
from models import CozeAPIResponse, HTTPRequestConfig

class CozeAPIClient:
    """Coze API客户端"""
    
    def __init__(self):
        self.base_url = config.COZE_API_BASE
        self.api_keys = config.COZE_API_KEYS
        self.workflow_ids = config.WORKFLOW_IDS
        self.throttler = Throttler(rate_limit=10, period=1)  # 每秒最多10个请求
        
    async def _make_request(
        self, 
        workflow_type: str, 
        input_data: str,
        timeout: int = None
    ) -> CozeAPIResponse:
        """发送请求到Coze API"""
        async with self.throttler:
            api_key = self.api_keys.get(workflow_type)
            if not api_key:
                raise ValueError(f"未找到工作流类型 {workflow_type} 的API密钥")
            
            workflow_id = self.workflow_ids.get(workflow_type)
            if not workflow_id:
                raise ValueError(f"未找到工作流类型 {workflow_type} 的工作流ID")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "workflow_id": workflow_id,
                "parameters": {
                    "input": input_data
                }
            }
            
            timeout = timeout or config.HTTP_TIMEOUT
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return CozeAPIResponse(
                                data=data.get("data", ""),
                                debug_url=data.get("debug_url")
                            )
                        else:
                            error_text = await response.text()
                            return CozeAPIResponse(
                                data="",
                                error=f"HTTP {response.status}: {error_text}"
                            )
            except asyncio.TimeoutError:
                return CozeAPIResponse(
                    data="",
                    error=f"请求超时 (>{timeout}s)"
                )
            except Exception as e:
                return CozeAPIResponse(
                    data="",
                    error=f"请求失败: {str(e)}"
                )
    
    async def search_topics(self, keyword: str) -> CozeAPIResponse:
        """搜索话题热度"""
        return await self._make_request("topic_search", keyword)
    
    async def retrieve_posts(self, keyword: str) -> CozeAPIResponse:
        """检索相关帖子"""
        return await self._make_request("post_retrieval", keyword)

class HTTPClient:
    """通用HTTP客户端"""
    
    def __init__(self):
        self.session = None
        self.throttler = Throttler(rate_limit=20, period=1)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def request(self, config: HTTPRequestConfig) -> Dict[str, Any]:
        """发送HTTP请求"""
        async with self.throttler:
            session = await self._get_session()
            
            try:
                async with session.request(
                    method=config.method,
                    url=config.url,
                    headers=config.headers,
                    timeout=aiohttp.ClientTimeout(total=config.timeout)
                ) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'application/json' in content_type:
                            data = await response.json()
                        else:
                            data = await response.text()
                        
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status,
                            "headers": dict(response.headers)
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status_code": response.status
                        }
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": f"请求超时 (>{config.timeout}s)"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"请求失败: {str(e)}"
                }
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()

# 全局API客户端实例
coze_client = CozeAPIClient()
http_client = HTTPClient() 