"""
内容生成节点
基于选择的爆点生成最终内容
"""

from typing import Dict, Any
from loguru import logger
from models import WorkflowStatus, GeneratedContent
from clients import llm_client

async def content_generation_node(state: 'WorkflowState') -> 'WorkflowState':
    """内容生成节点"""
    logger.info("开始内容生成")
    
    try:
        # 更新状态
        state.update_state(WorkflowStatus.CONTENT_GENERATION)
        
        # 获取选择的爆点
        selected_hitpoint = getattr(state, 'selected_hitpoint', None)
        user_input = getattr(state, 'user_input', "")
        
        if not selected_hitpoint:
            logger.warning("没有选择的爆点，使用默认内容")
            # 生成默认内容
            default_content = GeneratedContent(
                title="内容生成失败",
                content="抱歉，内容生成过程中出现错误，请重试。",
                tags=[],
                hitpoints=[],
                quality_score=0.0
            )
            state.generated_content = default_content
            return state
        
        logger.info(f"基于爆点生成内容: {selected_hitpoint.get('title', '未知标题')}")
        
        # 使用模拟数据生成内容
        from clients.llm_client import get_raw_content_generation_response
        raw_content = await get_raw_content_generation_response(user_input, selected_hitpoint)
        
        if raw_content:
            # 解析生成的内容
            lines = raw_content.strip().split('\n')
            title = ""
            content = ""
            tags = []
            
            for line in lines:
                if line.startswith("标题："):
                    title = line.replace("标题：", "").strip()
                elif line.startswith("正文："):
                    content = line.replace("正文：", "").strip()
                elif line.startswith("Hashtag:"):
                    tag_line = line.replace("Hashtag:", "").strip()
                    tags = [tag.strip() for tag in tag_line.split("#") if tag.strip()]
            
            generated_content = GeneratedContent(
                title=title or "生成的内容",
                content=content or raw_content,
                tags=tags,
                hitpoints=[selected_hitpoint.get('id', 'unknown')],
                quality_score=8.5
            )
            state.generated_content = generated_content
            logger.info("内容生成完成")
        else:
            logger.warning("内容生成失败，使用默认内容")
            # 使用默认内容
            default_content = GeneratedContent(
                title="内容生成失败",
                content="抱歉，内容生成过程中出现错误，请重试。",
                tags=[],
                hitpoints=[],
                quality_score=0.0
            )
            state.generated_content = default_content
        
        logger.info("内容生成完成")
        return state
        
    except Exception as e:
        logger.error(f"内容生成失败: {e}")
        # 创建默认内容
        default_content = GeneratedContent(
            title="内容生成失败",
            content="抱歉，内容生成过程中出现错误，请重试。",
            tags=[],
            hitpoints=[],
            quality_score=0.0
        )
        state.generated_content = default_content
        state.set_error(f"内容生成失败: {str(e)}")
        return state 