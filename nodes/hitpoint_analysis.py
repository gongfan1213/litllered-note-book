"""
打点分析节点 - 仅调用LLM
"""
from typing import Dict, Any
from loguru import logger
from models import WorkflowStatus
from clients.llm_client import get_raw_hitpoints_response

async def hitpoint_analysis_node(state: 'WorkflowState') -> 'WorkflowState':
    """
    打点分析节点 - 仅负责调用LLM
    """
    logger.info("开始打点分析 (LLM 调用)")
    
    try:
        state.update_state(WorkflowStatus.HITPOINT_ANALYSIS)
        
        # 输入是筛选后的帖子摘要
        posts_summary = getattr(state, 'selected_posts_summary', "")
        user_input = getattr(state, 'user_input', "")
        
        # 如果没有帖子摘要，从过滤后的帖子生成摘要
        if not posts_summary or posts_summary == "没有找到合适的帖子。":
            filtered_posts = getattr(state, 'filtered_posts', [])
            if filtered_posts:
                # 生成帖子摘要
                posts_summary = "筛选后的帖子：\n"
                for i, post in enumerate(filtered_posts[:5], 1):  # 只取前5个帖子
                    posts_summary += f"{i}. {post.title}: {post.content[:100]}...\n"
            else:
                logger.warning("没有内容用于打点分析，跳过")
                state.hitpoints_llm_output = ""
                return state
        
        # 调用LLM获取原始响应
        raw_content = await get_raw_hitpoints_response(posts_summary, user_input)
        
        state.hitpoints_llm_output = raw_content
        logger.info("打点分析 (LLM 调用) 完成")
        return state
        
    except Exception as e:
        logger.error(f"打点分析节点执行失败: {e}")
        state.set_error(f"打点分析失败: {str(e)}")
        return state 