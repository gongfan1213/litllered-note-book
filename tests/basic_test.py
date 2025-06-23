"""
最基本的LangGraph测试
用于确认LangGraph是否正常工作
"""

import asyncio
from typing import Dict, Any
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel

# 简单的状态模型
class SimpleState(BaseModel):
    user_input: str
    result: str = ""

# 最简单的节点函数
def simple_node(state: SimpleState) -> SimpleState:
    """最简单的节点函数"""
    logger.info("执行简单节点")
    state.result = f"处理了: {state.user_input}"
    return state

async def test_basic_langgraph():
    """测试基本LangGraph功能"""
    print("🚀 开始基本LangGraph测试...")
    
    try:
        # 创建内存保存器
        memory = MemorySaver()
        
        # 创建工作流图
        workflow = StateGraph(SimpleState)
        
        # 添加节点
        workflow.add_node("simple", simple_node)
        
        # 设置入口点
        workflow.set_entry_point("simple")
        
        # 添加边
        workflow.add_edge("simple", END)
        
        # 编译工作流
        compiled_workflow = workflow.compile(checkpointer=memory)
        
        print("✅ 工作流图构建完成")
        
        # 创建初始状态
        initial_state = SimpleState(user_input="测试输入")
        print(f"初始状态: {initial_state}")
        
        # 运行工作流
        result = await compiled_workflow.ainvoke(initial_state)
        print(f"工作流结果: {result}")
        
        if result:
            print("✅ 基本LangGraph测试成功")
            print(f"结果: {result.result}")
        else:
            print("❌ 基本LangGraph测试失败：返回None")
        
        return result
        
    except Exception as e:
        print(f"❌ 基本LangGraph测试异常: {e}")
        logger.error(f"基本LangGraph测试异常: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_basic_langgraph()) 