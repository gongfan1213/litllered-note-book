"""
测试两个节点
"""

import asyncio
from loguru import logger
from nodes.keyword_generation import keyword_generation_node
from nodes.topic_search import topic_search_node
from models import WorkflowStatus

async def test_two_nodes():
    """测试两个节点"""
    logger.info("🚀 开始测试两个节点...")
    
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
        
        logger.info(f"📊 初始状态: {test_state}")
        
        # 测试关键词生成节点
        logger.info("🔄 开始测试关键词生成节点...")
        result1 = await keyword_generation_node(test_state)
        
        if result1 is None:
            logger.error("❌ 关键词生成节点返回了None")
            return
        
        logger.info(f"✅ 关键词生成节点成功，状态: {result1.get('current_state')}")
        
        # 测试主题搜索节点
        logger.info("🔄 开始测试主题搜索节点...")
        result2 = await topic_search_node(result1)
        
        if result2 is None:
            logger.error("❌ 主题搜索节点返回了None")
            return
        
        logger.info(f"✅ 主题搜索节点成功，状态: {result2.get('current_state')}")
        
        # 打印最终结果摘要
        keywords = result2.get("keywords", [])
        topics = result2.get("topics", [])
        
        logger.info(f"🔑 生成关键词: {len(keywords)} 个")
        logger.info(f"📚 找到主题: {len(topics)} 个")
        
        logger.info("🎉 两个节点测试完成")
        
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
    asyncio.run(test_two_nodes()) 