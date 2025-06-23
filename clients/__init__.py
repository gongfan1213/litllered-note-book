"""
API客户端模块
"""

# 暂时注释掉 llm_client 导入，避免 langchain_openai 依赖问题
# from .llm_client import llm_client
from .xhs_client import XHSClient, xhs_client

__all__ = [
    # "llm_client",
    "XHSClient",
    "xhs_client"
] 