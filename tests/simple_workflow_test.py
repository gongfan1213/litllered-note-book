"""
简单工作流测试
"""

import asyncio
from loguru import logger
from workflow import agent
from config import config

async def test_simple_workflow():
    """测试简单工作流"""
    logger.info("🚀 开始简单工作流测试...")
    
    try:
        # 验证配置
        if not config.validate_config():
            logger.error("❌ 配置验证失败")
            return
        
        logger.info("✅ 配置验证通过")
        
        # 测试用户输入
        user_input = "美食制作"
        
        logger.info(f"📝 用户输入: {user_input}")
        
        # 运行工作流
        logger.info("🔄 开始运行工作流...")
        result = await agent.run(user_input)
        
        logger.info(f"📊 结果类型: {type(result)}")
        
        if result is None:
            logger.error("❌ 工作流返回了None")
            return
        
        # 打印结果摘要
        if isinstance(result, dict):
            current_state = result.get("current_state", "未知")
            error_message = result.get("error_message", "")
            
            if error_message:
                logger.error(f"❌ 工作流执行出错: {error_message}")
            else:
                logger.info(f"✅ 工作流状态: {current_state}")
                
                # 打印关键信息
                keywords = result.get("keywords", [])
                topics = result.get("topics", [])
                hitpoints = result.get("hitpoints", [])
                generated_content = result.get("generated_content", {})
                
                logger.info(f"🔑 生成关键词: {len(keywords)} 个")
                if keywords:
                    logger.info(f"   关键词: {[kw.get('text', '') for kw in keywords]}")
                
                logger.info(f"📚 找到主题: {len(topics)} 个")
                if topics:
                    logger.info(f"   主题: {[topic.get('title', '') for topic in topics]}")
                
                logger.info(f"💡 分析爆点: {len(hitpoints)} 个")
                if hitpoints:
                    logger.info(f"   爆点: {[hp.get('title', '') for hp in hitpoints]}")
                
                if generated_content:
                    title = generated_content.get("title", "未知标题")
                    logger.info(f"📝 生成内容标题: {title}")
        
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
    asyncio.run(test_simple_workflow()) 