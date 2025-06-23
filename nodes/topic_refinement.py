"""
主题优化节点
优化和筛选搜索到的主题
"""

from typing import Dict, Any
from loguru import logger
from models import WorkflowStatus, Topic
from clients import llm_client

async def topic_refinement_node(state: 'WorkflowState') -> 'WorkflowState':
    """主题优化节点 - 仅调用LLM"""
    logger.info("开始主题优化(LLM调用)")
    
    try:
        state.update_state(WorkflowStatus.TOPIC_REFINEMENT)
        
        # 这个节点的输入是合并后的主题搜索结果
        search_results = getattr(state, 'combined_topic_results', "")
        user_input = getattr(state, 'user_input', "")
        
        if not search_results:
            logger.warning("没有主题搜索结果可供优化")
            state.refinement_llm_output = ""
            return state

        # 调用LLM获取原始响应
        raw_content = await llm_client.get_raw_refinement_response(user_input, search_results)
        
        if not raw_content:
            raise ValueError("LLM未能生成主题优化内容。")

        state.refinement_llm_output = raw_content
        
        logger.info("主题优化(LLM调用)完成")
        return state
        
    except Exception as e:
        logger.error(f"主题优化节点执行失败: {e}")
        state.set_error(f"主题优化失败: {str(e)}")
        return state 