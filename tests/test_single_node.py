"""
测试单个节点
"""

import asyncio
from loguru import logger
from nodes.keyword_generation import keyword_generation_node
from models import WorkflowStatus

async def test_single_node():
    """测试单个节点"""
    logger.info("🚀 开始测试单个节点...")
    
    try:
        # 创建测试状态
        test_state = {
            "user_input": "美食制作",
            "current_state": WorkflowStatus.INITIALIZED.value,
            "keywords": [],
            "primary_keyword": "",
            "secondary_keyword": "",
            "topics": [],
            "search_results": {},
            "retrieved_posts": [],
            "filtered_posts": [],
            "hitpoints": [],
            "generated_content": {},
            "error_message": "",
            "total_posts_processed": 0,
            "total_hitpoints_generated": 0,
            "selected_hitpoint": {}
        }
        
        logger.info(f"📊 测试状态: {test_state}")
        
        # 测试关键词生成节点
        logger.info("🔄 开始测试关键词生成节点...")
        result = await keyword_generation_node(test_state)
        
        logger.info(f"📊 结果类型: {type(result)}")
        logger.info(f"📊 结果内容: {result}")
        
        if result is None:
            logger.error("❌ 节点返回了None")
        else:
            logger.info("✅ 节点执行成功")
            
            # 打印结果摘要
            current_state = result.get("current_state", "未知")
            error_message = result.get("error_message", "")
            
            if error_message:
                logger.error(f"❌ 节点执行出错: {error_message}")
            else:
                logger.info(f"✅ 节点状态: {current_state}")
                
                # 打印关键信息
                keywords = result.get("keywords", [])
                primary_keyword = result.get("primary_keyword", "")
                secondary_keyword = result.get("secondary_keyword", "")
                
                logger.info(f"🔑 生成关键词: {len(keywords)} 个")
                logger.info(f"🔑 主要关键词: {primary_keyword}")
                logger.info(f"🔑 次要关键词: {secondary_keyword}")
        
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
    asyncio.run(test_single_node()) 