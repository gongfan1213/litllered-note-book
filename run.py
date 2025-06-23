#!/usr/bin/env python3
"""
小红书起号智能助手启动脚本
简化启动过程，提供快速体验
"""

import asyncio
import sys
from main import run_workflow, print_result, test_llm_connection
from workflow import XiaohongshuAgent
from clients import xhs_client  # 导入客户端

async def quick_start():
    """快速启动体验"""
    print("🎉 欢迎使用小红书起号智能助手！")
    print("这是一个快速体验版本，将使用示例需求进行演示。")
    print()
    
    # 测试LLM连接
    print("🔗 正在测试LLM连接...")
    if not await test_llm_connection():
        print("❌ LLM连接失败，请检查配置")
        print("请确保在 .env 文件中正确配置了 LLM_API_KEY")
        return
    
    print("✅ LLM连接成功！")
    print()
    
    # 示例需求
    demo_inputs = [
        "我想做一个关于健身的小红书账号",
        "我想做一个关于美食分享的账号", 
        "我想做一个关于大厂生活的账号"
    ]
    
    print("可选的示例需求：")
    for i, demo_input in enumerate(demo_inputs, 1):
        print(f"  {i}. {demo_input}")
    print("  4. 自定义输入")
    print()
    
    try:
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            user_input = demo_inputs[0]
        elif choice == "2":
            user_input = demo_inputs[1]
        elif choice == "3":
            user_input = demo_inputs[2]
        elif choice == "4":
            user_input = input("请输入您的需求: ").strip()
            if not user_input:
                print("❌ 输入不能为空")
                return
        else:
            print("❌ 无效选择")
            return
        
        print(f"\n🔄 正在处理: {user_input}")
        print("请稍候，这可能需要几分钟时间...")
        print()
        
        # 运行工作流
        result = await run_workflow(user_input)
        
        # 显示结果
        print_result(result)
        
        # 询问是否继续
        print("\n是否继续体验其他需求？(y/n): ", end="")
        continue_choice = input().strip().lower()
        
        if continue_choice in ['y', 'yes', '是']:
            await quick_start()
        else:
            print("👋 感谢使用！")
    
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
    finally:
        # 无论成功还是失败，都确保关闭浏览器
        print("\n正在关闭浏览器资源...")
        await xhs_client.shutdown()
        print("✅ 资源已安全关闭。")

if __name__ == "__main__":
    print("🚀 启动小红书起号智能助手...")
    asyncio.run(quick_start()) 