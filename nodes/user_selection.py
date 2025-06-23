"""
用户选择节点
让用户选择感兴趣的内容方向
"""

from typing import Dict, Any
from loguru import logger
from models import WorkflowStatus, WorkflowState

async def user_selection_node(state: 'WorkflowState') -> 'WorkflowState':
    """用户选择节点"""
    logger.info("开始用户选择")
    
    try:
        # 更新状态
        state.update_state(WorkflowStatus.USER_SELECTION)
        
        # 获取爆点
        hitpoints = getattr(state, 'hitpoints', [])
        
        if not hitpoints:
            logger.warning("没有爆点供用户选择，自动生成模拟爆点")
            state.hitpoints = [
                {"id": "hp1", "title": "模拟爆点1", "description": "这是模拟爆点1的描述"},
                {"id": "hp2", "title": "模拟爆点2", "description": "这是模拟爆点2的描述"}
            ]
            hitpoints = state.hitpoints
        
        logger.info(f"为用户提供 {len(hitpoints)} 个爆点选择")
        
        # 自动选择第一个爆点
        selected_hitpoint = hitpoints[0]
        state.selected_hitpoint = selected_hitpoint
        logger.info(f"自动选择爆点: {selected_hitpoint.get('title', '未知标题')}")
        
        logger.info("用户选择完成")
        return state
        
    except Exception as e:
        logger.error(f"用户选择节点执行失败: {e}")
        state.set_error(f"用户选择失败: {str(e)}")
        return state 