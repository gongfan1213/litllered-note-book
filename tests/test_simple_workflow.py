"""
简化工作流测试
只测试前两个节点，确保基本流程正常
"""

import asyncio
from loguru import logger
from models import WorkflowState, WorkflowStatus
from nodes.keyword_generation import keyword_generation_node
from nodes.topic_search import topic_search_node

async def test_simple_workflow():
    """测试简化工作流"""
    print("🚀 开始简化工作流测试...")
    
    try:
        # 创建初始状态
        state = WorkflowState(user_input="我想做一个关于健身的小红书账号")
        print(f"初始状态: {state.current_state}")
        
        # 测试关键词生成节点
        print("\n🔍 测试关键词生成节点...")
        state = await keyword_generation_node(state)
        print(f"关键词生成后状态: {state.current_state}")
        print(f"关键词数量: {len(state.keywords)}")
        print(f"主要关键词: {state.primary_keyword}")
        print(f"次要关键词: {state.secondary_keyword}")
        
        # 测试话题搜索节点
        print("\n🔍 测试话题搜索节点...")
        state = await topic_search_node(state)
        print(f"话题搜索后状态: {state.current_state}")
        print(f"话题数量: {len(state.topics)}")
        
        print("\n✅ 简化工作流测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 简化工作流测试失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_simple_workflow()) 