"""
小红书起号智能助手主程序
提供命令行接口和API服务
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any
from loguru import logger
from workflow import agent
from config import config
from clients import llm_client

def setup_logging():
    """设置日志配置"""
    logger.remove()  # 移除默认处理器
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件处理器
    logger.add(
        config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.LOG_LEVEL,
        rotation="10 MB",
        retention="7 days"
    )

async def test_llm_connection():
    """测试LLM连接"""
    logger.info("测试LLM API连接...")
    success = await llm_client.test_connection()
    if success:
        logger.info("✅ LLM API连接测试成功")
        return True
    else:
        logger.error("❌ LLM API连接测试失败")
        return False

async def run_workflow(user_input: str, config_id: str = None) -> Dict[str, Any]:
    """运行工作流"""
    try:
        logger.info(f"开始处理用户请求: {user_input}")
        
        # 运行工作流
        result = await agent.run(user_input, config_id)
        
        # 构建响应
        response = {
            "success": result.current_state != "error",
            "user_input": user_input,
            "current_state": result.current_state.value if hasattr(result.current_state, 'value') else str(result.current_state),
            "error_message": result.error_message,
            "generated_content": None,
            "hitpoints": [],
            "statistics": {
                "total_posts_processed": result.total_posts_processed,
                "total_hitpoints_generated": result.total_hitpoints_generated
            }
        }
        
        # 添加生成的内容
        if result.generated_content:
            response["generated_content"] = {
                "title": result.generated_content.title,
                "content": result.generated_content.content,
                "tags": result.generated_content.tags,
                "quality_score": result.generated_content.quality_score
            }
        
        # 添加打点信息
        if result.hitpoints:
            response["hitpoints"] = [
                {
                    "id": hp.id,
                    "title": hp.title,
                    "description": hp.description
                }
                for hp in result.hitpoints
            ]
        
        logger.info("工作流执行完成")
        return response
        
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        return {
            "success": False,
            "user_input": user_input,
            "error_message": f"工作流执行失败: {str(e)}",
            "current_state": "error"
        }

def print_result(result: Dict[str, Any]):
    """打印结果"""
    print("\n" + "="*50)
    print("小红书起号智能助手 - 执行结果")
    print("="*50)
    
    if result["success"]:
        print(f"✅ 执行成功")
        print(f"📝 用户输入: {result['user_input']}")
        print(f"🔄 当前状态: {result['current_state']}")
        
        # 显示打点
        if result["hitpoints"]:
            print(f"\n🎯 分析出的打点 ({len(result['hitpoints'])} 个):")
            for i, hitpoint in enumerate(result["hitpoints"], 1):
                print(f"  {i}. {hitpoint['title']}")
                print(f"     {hitpoint['description'][:100]}...")
        
        # 显示生成的内容
        if result["generated_content"]:
            content = result["generated_content"]
            print(f"\n📄 生成的内容:")
            print(f"标题: {content['title']}")
            print(f"内容: {content['content'][:200]}...")
            print(f"标签: {', '.join(content['tags'])}")
            print(f"质量评分: {content['quality_score']}")
        
        # 显示统计信息
        stats = result["statistics"]
        print(f"\n📊 统计信息:")
        print(f"处理帖子数: {stats['total_posts_processed']}")
        print(f"生成打点数: {stats['total_hitpoints_generated']}")
        
    else:
        print(f"❌ 执行失败")
        print(f"📝 用户输入: {result['user_input']}")
        print(f"🔄 当前状态: {result['current_state']}")
        print(f"❌ 错误信息: {result['error_message']}")
    
    print("="*50)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小红书起号智能助手")
    parser.add_argument("input", nargs="?", help="用户输入的需求描述")
    parser.add_argument("--config-id", help="配置ID，用于检查点恢复")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    parser.add_argument("--test", action="store_true", help="测试LLM连接")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 验证配置
    if not config.validate_config():
        logger.error("配置验证失败，请检查环境变量")
        print("❌ 配置验证失败，请检查环境变量")
        print("请确保设置了以下环境变量:")
        print("  - LLM_API_KEY")
        print("  - COZE_API_KEY")
        sys.exit(1)
    
    try:
        # 测试LLM连接
        if args.test:
            success = await test_llm_connection()
            if not success:
                print("❌ LLM连接测试失败，请检查配置")
                sys.exit(1)
            print("✅ LLM连接测试成功")
            return
        
        # 在开始前测试LLM连接
        logger.info("测试LLM连接...")
        if not await test_llm_connection():
            print("❌ LLM连接失败，请检查配置")
            sys.exit(1)
        
        if args.interactive:
            # 交互模式
            print("🎉 欢迎使用小红书起号智能助手！")
            print("请输入您的起号需求，输入 'quit' 退出")
            
            while True:
                try:
                    user_input = input("\n💬 请输入您的需求: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', '退出']:
                        print("👋 再见！")
                        break
                    
                    if not user_input:
                        print("❌ 请输入有效的需求描述")
                        continue
                    
                    print("🔄 正在处理，请稍候...")
                    result = await run_workflow(user_input)
                    
                    if args.json:
                        print(json.dumps(result, ensure_ascii=False, indent=2))
                    else:
                        print_result(result)
                        
                except KeyboardInterrupt:
                    print("\n👋 再见！")
                    break
                except Exception as e:
                    logger.error(f"交互模式执行失败: {e}")
                    print(f"❌ 执行失败: {e}")
        
        elif args.input:
            # 命令行模式
            result = await run_workflow(args.input, args.config_id)
            
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print_result(result)
        
        else:
            # 显示帮助信息
            parser.print_help()
            print("\n💡 使用示例:")
            print("  python main.py '我想做一个关于健身的小红书账号'")
            print("  python main.py --interactive")
            print("  python main.py '美食分享' --json")
            print("  python main.py --test")
    
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 