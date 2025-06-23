"""
返回字典格式的LangGraph测试
LangGraph 0.0.20版本期望节点返回字典
"""

import asyncio
from typing import Dict, Any
from loguru import logger
from langgraph.graph import StateGraph, END

# 最简单的节点函数，返回字典
def simple_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """最简单的节点函数，返回字典格式"""
    logger.info("执行简单节点")
    logger.info(f"输入状态: {state}")
    
    # 更新状态
    state["result"] = f"处理了: {state['user_input']}"
    
    logger.info(f"输出状态: {state}")
    return state

async def test_dict_node():
    """测试返回字典格式的节点"""
    print("🚀 开始字典节点测试...")
    
    try:
        # 创建工作流图
        workflow = StateGraph({
            "user_input": str,
            "result": str
        })
        
        # 添加节点
        workflow.add_node("simple", simple_node)
        
        # 设置入口点
        workflow.set_entry_point("simple")
        
        # 添加边
        workflow.add_edge("simple", END)
        
        # 编译工作流
        compiled_workflow = workflow.compile()
        
        print("✅ 工作流图构建完成")
        
        # 创建初始状态（字典格式）
        initial_state = {
            "user_input": "测试输入",
            "result": ""
        }
        print(f"初始状态: {initial_state}")
        
        # 运行工作流
        result = await compiled_workflow.ainvoke(initial_state)
        print(f"工作流结果: {result}")
        
        if result:
            print("✅ 字典节点测试成功")
            print(f"结果: {result['result']}")
        else:
            print("❌ 字典节点测试失败：返回None")
        
        return result
        
    except Exception as e:
        print(f"❌ 字典节点测试异常: {e}")
        logger.error(f"字典节点测试异常: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_dict_node()) 