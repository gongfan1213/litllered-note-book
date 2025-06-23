#!/usr/bin/env python3
"""
LLM连接测试脚本
测试新的API端点和模型配置
"""

import asyncio
import sys
from loguru import logger
from config import config
from clients.llm_client import LLMClient

async def test_models():
    """测试不同的模型"""
    print("🧪 开始测试不同模型...")
    print()
    
    # 测试默认模型
    try:
        llm_client = LLMClient()
        
        # 发送测试请求
        response = await llm_client.default_model.ainvoke([
            {"role": "user", "content": "请用一句话介绍你自己"}
        ])
        
        print(f"✅ 默认模型 ({config.DEFAULT_MODEL}): 连接成功")
        print(f"   响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"❌ 默认模型: 连接失败 - {e}")
    
    print()

async def test_api_endpoint():
    """测试API端点"""
    print("🔗 测试API端点配置...")
    print(f"Base URL: {config.LLM_BASE_URL}")
    print(f"API Key: {config.LLM_API_KEY[:10]}...")
    print()
    
    try:
        llm_client = LLMClient()
        success = await llm_client.test_connection()
        
        if success:
            print("✅ API端点测试成功")
        else:
            print("❌ API端点测试失败")
            
    except Exception as e:
        print(f"❌ API端点测试异常: {e}")

async def test_keyword_generation():
    """测试关键词生成功能"""
    print("🎯 测试关键词生成功能...")
    
    try:
        llm_client = LLMClient()
        user_input = "我想做一个关于健身的小红书账号"
        
        # 使用新的方法
        raw_response = await llm_client.get_raw_keyword_response(user_input)
        keywords = llm_client.parse_keywords(raw_response)
        
        if keywords:
            print("✅ 关键词生成成功")
            for i, keyword in enumerate(keywords, 1):
                print(f"   {i}. {keyword.text}")
        else:
            print("❌ 关键词生成失败")
            
    except Exception as e:
        print(f"❌ 关键词生成测试异常: {e}")

async def main():
    """主测试函数"""
    print("🚀 LLM配置测试开始")
    print("="*50)
    
    # 验证配置
    if not config.validate_config():
        print("❌ 配置验证失败")
        return
    
    print("✅ 配置验证通过")
    print()
    
    # 测试API端点
    await test_api_endpoint()
    print()
    
    # 测试模型
    await test_models()
    print()
    
    # 测试关键词生成
    await test_keyword_generation()
    print()
    
    print("🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 