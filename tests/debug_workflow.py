"""
调试工作流
"""

import asyncio
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models import WorkflowStatus
from nodes import (
    keyword_generation_node,
    topic_search_node,
    topic_refinement_node,
    post_retrieval_node,
    content_filtering_node,
    hitpoint_analysis_node,
    user_selection_node,
    content_generation_node
)
from config import config

async def debug_workflow():
    """调试工作流"""
    logger.info("🚀 开始调试工作流...")
    
    try:
        # 验证配置
        if not config.validate_config():
            logger.error("❌ 配置验证失败")
            return
        
        logger.info("✅ 配置验证通过")
        
        # 创建内存检查点
        memory = MemorySaver()
        
        # 创建工作流图
        logger.info("🔧 构建工作流图...")
        workflow = StateGraph({
            "user_input": str,
            "current_state": str,
            "keywords": list,
            "primary_keyword": str,
            "secondary_keyword": str,
            "topics": list,
            "search_results": dict,
            "retrieved_posts": list,
            "filtered_posts": list,
            "hitpoints": list,
            "generated_content": dict,
            "error_message": str,
            "total_posts_processed": int,
            "total_hitpoints_generated": int,
            "selected_hitpoint": dict
        })
        
        # 添加节点
        workflow.add_node("keyword_generation", keyword_generation_node)
        workflow.add_node("topic_search", topic_search_node)
        workflow.add_node("topic_refinement", topic_refinement_node)
        workflow.add_node("post_retrieval", post_retrieval_node)
        workflow.add_node("content_filtering", content_filtering_node)
        workflow.add_node("hitpoint_analysis", hitpoint_analysis_node)
        workflow.add_node("user_selection", user_selection_node)
        workflow.add_node("content_generation", content_generation_node)
        
        # 设置入口点
        workflow.set_entry_point("keyword_generation")
        
        # 使用简单的线性流程
        workflow.add_edge("keyword_generation", "topic_search")
        workflow.add_edge("topic_search", "topic_refinement")
        workflow.add_edge("topic_refinement", "post_retrieval")
        workflow.add_edge("post_retrieval", "content_filtering")
        workflow.add_edge("content_filtering", "hitpoint_analysis")
        workflow.add_edge("hitpoint_analysis", "user_selection")
        workflow.add_edge("user_selection", "content_generation")
        workflow.add_edge("content_generation", END)
        
        # 编译工作流
        compiled_workflow = workflow.compile(checkpointer=memory)
        logger.info("✅ 工作流图构建完成")
        
        # 测试用户输入
        user_input = "美食制作"
        logger.info(f"📝 用户输入: {user_input}")
        
        # 创建初始状态
        initial_state = {
            "user_input": user_input,
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
        logger.info(f"📊 初始状态: {initial_state}")
        
        # 运行工作流
        logger.info("🔄 开始运行工作流...")
        result = await compiled_workflow.ainvoke(initial_state)
        
        logger.info(f"📊 结果类型: {type(result)}")
        logger.info(f"📊 结果内容: {result}")
        
        if result is None:
            logger.error("❌ 工作流返回了None")
        else:
            logger.info("✅ 工作流执行成功")
            
            # 打印结果摘要
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
                logger.info(f"📚 找到主题: {len(topics)} 个")
                logger.info(f"💡 分析爆点: {len(hitpoints)} 个")
                
                if generated_content:
                    title = generated_content.get("title", "未知标题")
                    logger.info(f"📝 生成内容标题: {title}")
        
        logger.info("🎉 调试完成")
        
    except Exception as e:
        logger.error(f"❌ 调试失败: {e}")
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
    
    # 运行调试
    asyncio.run(debug_workflow()) 