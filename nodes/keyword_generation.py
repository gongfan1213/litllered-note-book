"""
关键词生成节点
基于用户输入生成相关关键词
"""

from typing import Dict, Any
from loguru import logger
from models import WorkflowStatus, Keyword
from workflow_types import WorkflowState
from clients import llm_client

async def keyword_generation_node(state: WorkflowState) -> WorkflowState:
    """关键词生成节点 - 现在只负责调用LLM并返回原始响应"""
    logger.info("开始关键词生成(仅LLM调用)")
    
    try:
        state.update_state(WorkflowStatus.KEYWORD_GENERATION)
        
        # 这个函数现在只调用LLM并返回原始文本
        raw_content = await llm_client.get_raw_keyword_response(state.user_input)
        
        if not raw_content:
            raise ValueError("LLM未能生成关键词内容。")
            
        # 将原始响应放入状态，供下一个节点解析
        state.llm_output = raw_content
        
        logger.info("关键词生成(LLM调用)完成")
        return state
        
    except Exception as e:
        logger.error(f"关键词生成节点执行失败: {e}")
        state.set_error(f"关键词生成失败: {str(e)}")
        return state 