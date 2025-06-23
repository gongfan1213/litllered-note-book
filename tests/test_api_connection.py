#!/usr/bin/env python3
"""
API连接测试脚本
用于验证Coze API token是否有效
"""

import asyncio
import json
from loguru import logger
from clients.api_client import coze_client
from config import config

async def test_coze_api_connection():
    """测试Coze API连接"""
    print("🔍 开始测试Coze API连接...")
    print(f"📋 使用的API Key: {config.COZE_API_KEY[:20]}...")
    print(f"🔗 API URL: {config.COZE_API_URL}")
    print(f"🆔 Workflow ID: {config.COZE_WORKFLOW_ID}")
    print("-" * 50)
    
    # 测试话题搜索
    print("1️⃣ 测试话题搜索功能...")
    test_keyword = "健身"
    response = await coze_client.search_topics(test_keyword)
    
    if response.success:
        print("✅ 话题搜索成功!")
        print(f"📊 响应数据: {json.dumps(response.data, ensure_ascii=False, indent=2)}")
    else:
        print("❌ 话题搜索失败!")
        print(f"🚨 错误信息: {response.error}")
        
        # 分析错误类型
        if "401" in response.error or "unauthorized" in response.error.lower():
            print("\n🔑 问题诊断: API Token已过期或无效")
            print("💡 解决方案: 请重新获取Coze API Token")
        elif "404" in response.error:
            print("\n🔑 问题诊断: Workflow ID不存在或无效")
            print("💡 解决方案: 请检查Workflow ID是否正确")
        elif "timeout" in response.error.lower():
            print("\n🔑 问题诊断: 网络连接超时")
            print("💡 解决方案: 请检查网络连接")
    
    print("-" * 50)
    
    # 测试帖子检索
    print("2️⃣ 测试帖子检索功能...")
    response = await coze_client.retrieve_posts(test_keyword, limit=5)
    
    if response.success:
        print("✅ 帖子检索成功!")
        print(f"📊 响应数据: {json.dumps(response.data, ensure_ascii=False, indent=2)}")
    else:
        print("❌ 帖子检索失败!")
        print(f"🚨 错误信息: {response.error}")
    
    print("-" * 50)
    print("🏁 测试完成!")

async def test_llm_connection():
    """测试LLM连接"""
    print("\n🤖 开始测试LLM连接...")
    print(f"🔗 LLM Base URL: {config.LLM_BASE_URL}")
    print(f"🔑 LLM API Key: {config.LLM_API_KEY[:20]}...")
    print("-" * 50)
    
    try:
        from clients.llm_client import llm_client
        
        # 测试简单对话
        response = await llm_client.chat("你好，请简单回复'测试成功'")
        
        if response.success:
            print("✅ LLM连接成功!")
            print(f"🤖 回复: {response.content}")
        else:
            print("❌ LLM连接失败!")
            print(f"🚨 错误信息: {response.error}")
            
    except Exception as e:
        print(f"❌ LLM测试异常: {e}")

def print_token_help():
    """打印获取Token的帮助信息"""
    print("\n" + "="*60)
    print("🔑 如何获取新的Coze API Token")
    print("="*60)
    print("""
1️⃣ 登录Coze平台
   📍 访问: https://www.coze.cn/
   🔐 使用你的账号登录

2️⃣ 获取API Token
   👤 点击右上角头像 → 设置
   🔧 找到"开发者"或"API设置"
   ➕ 点击"创建API Key"或"生成Token"
   📋 复制生成的token

3️⃣ 更新配置文件
   📝 编辑 .env 文件:
   COZE_API_KEY=你的新token
   
4️⃣ 重新测试
   🧪 运行: python test_api_connection.py
    """)

async def main():
    """主函数"""
    print("🚀 小红书起号智能助手 - API连接测试")
    print("="*60)
    
    # 检查配置
    if not config.validate_config():
        print("❌ 配置验证失败，请检查环境变量")
        return
    
    # 测试Coze API
    await test_coze_api_connection()
    
    # 测试LLM
    await test_llm_connection()
    
    # 打印帮助信息
    print_token_help()

if __name__ == "__main__":
    asyncio.run(main()) 