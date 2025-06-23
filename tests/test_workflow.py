"""
工作流测试
测试工作流的各个组件和功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from models import WorkflowState, Keyword, Post, Hitpoint, GeneratedContent
from workflow import XiaohongshuAgent
from config import config

class TestWorkflowState:
    """测试工作流状态"""
    
    def test_workflow_state_creation(self):
        """测试工作流状态创建"""
        state = WorkflowState(user_input="测试输入")
        assert state.user_input == "测试输入"
        assert state.current_state.value == "initialized"
        assert len(state.keywords) == 0
        assert len(state.topics) == 0
        assert len(state.retrieved_posts) == 0
    
    def test_workflow_state_update(self):
        """测试工作流状态更新"""
        state = WorkflowState(user_input="测试输入")
        
        # 测试添加关键词
        keyword = Keyword(text="测试关键词", relevance_score=1.0)
        state.add_keyword(keyword)
        assert len(state.keywords) == 1
        assert state.keywords[0].text == "测试关键词"
        
        # 测试添加帖子
        post = Post(
            id="test_1",
            title="测试帖子",
            content="测试内容",
            author="测试作者"
        )
        state.add_post(post)
        assert len(state.retrieved_posts) == 1
        assert state.total_posts_processed == 1
        
        # 测试添加打点
        hitpoint = Hitpoint(
            id="hitpoint_1",
            title="测试打点",
            description="测试描述"
        )
        state.add_hitpoint(hitpoint)
        assert len(state.hitpoints) == 1
        assert state.total_hitpoints_generated == 1
    
    def test_workflow_state_error(self):
        """测试工作流状态错误处理"""
        state = WorkflowState(user_input="测试输入")
        state.set_error("测试错误")
        
        assert state.current_state.value == "error"
        assert state.error_message == "测试错误"

class TestXiaohongshuAgent:
    """测试小红书助手"""
    
    @pytest.fixture
    def agent(self):
        """创建助手实例"""
        return XiaohongshuAgent()
    
    def test_agent_initialization(self, agent):
        """测试助手初始化"""
        assert agent.graph is not None
        assert agent.memory is not None
    
    def test_check_error(self, agent):
        """测试错误检查"""
        # 测试正常状态
        normal_state = WorkflowState(user_input="测试")
        result = agent._check_error(normal_state)
        assert result == "continue"
        
        # 测试错误状态
        error_state = WorkflowState(user_input="测试")
        error_state.set_error("测试错误")
        result = agent._check_error(error_state)
        assert result == "error"
    
    @pytest.mark.asyncio
    async def test_agent_run_success(self, agent):
        """测试助手运行成功"""
        with patch('config.config.validate_config', return_value=True):
            with patch.object(agent.graph, 'ainvoke', new_callable=AsyncMock) as mock_invoke:
                # 模拟成功结果
                mock_result = WorkflowState(user_input="测试输入")
                mock_result.update_state(WorkflowState.COMPLETED)
                mock_invoke.return_value = mock_result
                
                result = await agent.run("测试输入")
                
                assert result.current_state == WorkflowState.COMPLETED
                mock_invoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_run_error(self, agent):
        """测试助手运行错误"""
        with patch('config.config.validate_config', return_value=True):
            with patch.object(agent.graph, 'ainvoke', side_effect=Exception("测试错误")):
                result = await agent.run("测试输入")
                
                assert result.current_state == WorkflowState.ERROR
                assert "测试错误" in result.error_message

class TestModels:
    """测试数据模型"""
    
    def test_keyword_model(self):
        """测试关键词模型"""
        keyword = Keyword(
            text="测试关键词",
            relevance_score=0.8,
            search_volume=1000
        )
        
        assert keyword.text == "测试关键词"
        assert keyword.relevance_score == 0.8
        assert keyword.search_volume == 1000
    
    def test_post_model(self):
        """测试帖子模型"""
        post = Post(
            id="test_1",
            title="测试标题",
            content="测试内容",
            author="测试作者",
            likes=100,
            comments=50,
            shares=20,
            views=1000
        )
        
        assert post.id == "test_1"
        assert post.title == "测试标题"
        assert post.engagement_rate == 0.17  # (100+50+20)/1000
    
    def test_hitpoint_model(self):
        """测试打点模型"""
        hitpoint = Hitpoint(
            id="hitpoint_1",
            title="测试打点",
            description="测试描述",
            analysis={"type": "test", "priority": "high"}
        )
        
        assert hitpoint.id == "hitpoint_1"
        assert hitpoint.title == "测试打点"
        assert hitpoint.analysis["type"] == "test"
    
    def test_generated_content_model(self):
        """测试生成内容模型"""
        content = GeneratedContent(
            title="测试标题",
            content="测试内容",
            tags=["标签1", "标签2"],
            hitpoints=["hitpoint_1"],
            quality_score=8.5
        )
        
        assert content.title == "测试标题"
        assert content.content == "测试内容"
        assert len(content.tags) == 2
        assert content.quality_score == 8.5

@pytest.mark.asyncio
async def test_integration_workflow():
    """集成测试：完整工作流"""
    # 这里可以添加完整的端到端测试
    # 由于涉及外部API，建议使用mock
    pass

if __name__ == "__main__":
    pytest.main([__file__]) 