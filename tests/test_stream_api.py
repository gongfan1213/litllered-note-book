#!/usr/bin/env python3
"""
测试Coze stream_run API端点
"""

import asyncio
import json
import httpx
from loguru import logger
from config import config

async def test_stream_run_api():
    """测试stream_run API"""
    print("🔍 测试Coze stream_run API...")
    print(f"📋 API Key: {config.COZE_API_KEY[:20]}...")
    print(f"🔗 API URL: {config.COZE_API_URL}")
    print(f"🆔 Workflow ID: {config.COZE_WORKFLOW_ID}")
    print("-" * 50)
    
    # 测试数据
    test_input = "春夏"
    
    headers = {
        "Authorization": f"Bearer {config.COZE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "workflow_id": config.COZE_WORKFLOW_ID,
        "parameters": {
            "input": test_input
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            print(f"📤 发送请求: {test_input}")
            response = await client.post(
                config.COZE_API_URL,
                headers=headers,
                json=data
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📋 响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ 请求成功!")
                try:
                    response_data = response.json()
                    print(f"📄 响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                except json.JSONDecodeError:
                    print(f"📄 响应文本: {response.text}")
            else:
                print("❌ 请求失败!")
                print(f"🚨 错误信息: {response.text}")
                
                # 分析错误
                if response.status_code == 401:
                    print("\n🔑 问题诊断: API Token无效或已过期")
                elif response.status_code == 404:
                    print("\n🔑 问题诊断: Workflow ID不存在")
                elif response.status_code == 400:
                    print("\n🔑 问题诊断: 请求参数错误")
                    
    except Exception as e:
        print(f"❌ 请求异常: {e}")

async def test_with_curl_format():
    """使用curl格式测试"""
    print("\n🔄 使用curl格式测试...")
    print("-" * 50)
    
    # 模拟curl命令
    curl_command = f"""
curl -X POST '{config.COZE_API_URL}' \\
-H "Authorization: Bearer {config.COZE_API_KEY}" \\
-H "Content-Type: application/json" \\
-d '{{
  "workflow_id": "{config.COZE_WORKFLOW_ID}",
  "parameters": {{
    "input": "春夏\\n"
  }}
}}'
"""
    print("📋 对应的curl命令:")
    print(curl_command)
    
    # 实际执行请求
    await test_stream_run_api()

async def main():
    """主函数"""
    print("🚀 Coze stream_run API 测试")
    print("="*60)
    
    # 检查配置
    if not config.COZE_API_KEY:
        print("❌ 缺少COZE_API_KEY配置")
        return
        
    if not config.COZE_WORKFLOW_ID:
        print("❌ 缺少COZE_WORKFLOW_ID配置")
        return
    
    # 测试API
    await test_with_curl_format()

if __name__ == "__main__":
    asyncio.run(main()) 