"""
简单工作流测试
只包含关键词生成节点，用于调试LangGraph问题
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models import WorkflowState, WorkflowStatus
from nodes.keyword_generation import keyword_generation_node
from config import config

class SimpleAgent:
    """简单工作流代理"""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """构建简单工作流图"""
        logger.info("构建简单工作流图")
        
        # 创建工作流图
        workflow = StateGraph(WorkflowState)
        
        # 只添加关键词生成节点
        workflow.add_node("keyword_generation", keyword_generation_node)
        
        # 设置入口点
        workflow.set_entry_point("keyword_generation")
        
        # 直接连接到结束
        workflow.add_edge("keyword_generation", END)
        
        logger.info("简单工作流图构建完成")
        return workflow.compile(checkpointer=self.memory)
    
    async def run(self, user_input: str) -> WorkflowState:
        """运行简单工作流"""
        logger.info(f"开始运行简单工作流，用户输入: {user_input}")
        
        try:
            # 验证配置
            if not config.validate_config():
                raise ValueError("配置验证失败，请检查环境变量")
            
            # 创建初始状态
            initial_state = WorkflowState(user_input=user_input)
            logger.info(f"创建初始状态: {initial_state}")
            
            # 运行工作流
            result = await self.graph.ainvoke(initial_state)
            
            logger.info(f"简单工作流执行完成，结果类型: {type(result)}")
            if result is None:
                logger.error("简单工作流返回了None")
                # 创建错误状态
                error_state = WorkflowState(user_input=user_input)
                error_state.set_error("简单工作流执行返回了None")
                return error_state
            
            logger.info("简单工作流执行完成")
            return result
            
        except Exception as e:
            logger.error(f"简单工作流执行失败: {e}")
            # 创建错误状态
            error_state = WorkflowState(user_input=user_input)
            error_state.set_error(f"简单工作流执行失败: {str(e)}")
            return error_state

# 全局简单工作流实例
simple_agent = SimpleAgent()

async def test_simple_workflow():
    """测试简单工作流"""
    print("🚀 开始简单工作流测试...")
    
    try:
        result = await simple_agent.run("我想做一个关于健身的小红书账号")
        print(f"简单工作流结果: {result}")
        
        if result.current_state != WorkflowStatus.ERROR:
            print(f"✅ 简单工作流测试成功")
            print(f"关键词数量: {len(result.keywords)}")
            print(f"主要关键词: {result.primary_keyword}")
            print(f"次要关键词: {result.secondary_keyword}")
        else:
            print(f"❌ 简单工作流测试失败: {result.error_message}")
        
        return result
        
    except Exception as e:
        print(f"❌ 简单工作流测试异常: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_simple_workflow()) 