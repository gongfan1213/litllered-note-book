#!/usr/bin/env python3
"""
简化的LLM连接测试脚本
"""

import asyncio
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config import config

async def test_simple_llm():
    """简单的LLM测试"""
    print("🧪 开始简单LLM测试...")
    
    try:
        # 直接创建ChatOpenAI实例
        llm = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            openai_api_base=config.LLM_BASE_URL,
            openai_api_key=config.LLM_API_KEY,
            temperature=0.7,
            max_tokens=100
        )
        
        # 发送简单测试消息
        response = await llm.ainvoke([
            HumanMessage(content="你好，请用一句话回复我。")
        ])
        
        print(f"✅ LLM连接成功！")
        print(f"   响应: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ LLM连接失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_simple_llm()) 