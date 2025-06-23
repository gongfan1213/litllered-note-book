"""
测试修复后的工作流
"""

import asyncio
import json
from loguru import logger
from workflow import agent
from config import config

async def test_fixed_workflow():
    """测试修复后的工作流"""
    logger.info("🚀 开始测试修复后的工作流...")
    
    try:
        # 验证配置
        if not config.validate_config():
            logger.error("❌ 配置验证失败")
            return
        
        logger.info("✅ 配置验证通过")
        
        # 测试用户输入
        user_input = "我想在小红书上分享美食制作经验"
        
        logger.info(f"📝 用户输入: {user_input}")
        
        # 运行工作流
        logger.info("🔄 开始运行工作流...")
        result = await agent.run(user_input)
        
        if result is None:
            logger.error("❌ 工作流返回了None")
            return
        
        logger.info("✅ 工作流执行完成")
        logger.info(f"📊 结果类型: {type(result)}")
        
        # 打印结果摘要
        if isinstance(result, dict):
            current_state = result.get("current_state", "未知")
            error_message = result.get("error_message")
            
            if error_message:
                logger.error(f"❌ 工作流执行出错: {error_message}")
            else:
                logger.info(f"✅ 工作流状态: {current_state}")
                
                # 打印关键信息
                keywords = result.get("keywords", [])
                topics = result.get("topics", [])
                hitpoints = result.get("hitpoints", [])
                generated_content = result.get("generated_content")
                
                logger.info(f"🔑 生成关键词: {len(keywords)} 个")
                logger.info(f"📚 找到主题: {len(topics)} 个")
                logger.info(f"💡 分析爆点: {len(hitpoints)} 个")
                
                if generated_content:
                    title = generated_content.get("title", "未知标题")
                    logger.info(f"📝 生成内容标题: {title}")
                
                # 保存详细结果到文件
                with open("workflow_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info("💾 详细结果已保存到 workflow_result.json")
        
        logger.info("🎉 测试完成")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # 设置日志格式
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 运行测试
    asyncio.run(test_fixed_workflow()) 