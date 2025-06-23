"""
测试文件 - 小红书起号助手
"""
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from models import WorkflowState, Article, TopicSearchResult, Hitpoint
from workflow import agent
from utils.parsers import extract_xml_tags, parse_and_format_hot_topics
from utils.prompt_loader import prompt_loader

class TestWorkflowState:
    """测试工作流状态"""
    
    def test_workflow_state_creation(self):
        """测试工作流状态创建"""
        state = WorkflowState(user_request="测试需求")
        assert state.user_request == "测试需求"
        assert state.current_step == "initial"
        assert not state.is_completed
    
    def test_workflow_state_defaults(self):
        """测试工作流状态默认值"""
        state = WorkflowState()
        assert state.topic1_results == []
        assert state.topic2_results == []
        assert state.articles_topic1 == []
        assert state.articles_topic2 == []
        assert state.hitpoints == []

class TestParsers:
    """测试解析器"""
    
    def test_extract_xml_tags(self):
        """测试XML标签提取"""
        text = "<topic1>大厂生活</topic1><topic2>程序员日常</topic2>"
        result = extract_xml_tags(text, ["topic1", "topic2"])
        
        assert result["topic1"] == "大厂生活"
        assert result["topic2"] == "程序员日常"
    
    def test_extract_xml_tags_missing(self):
        """测试缺失的XML标签"""
        text = "<topic1>大厂生活</topic1>"
        result = extract_xml_tags(text, ["topic1", "topic2"])
        
        assert result["topic1"] == "大厂生活"
        assert "Error" in result["topic2"]
    
    def test_parse_and_format_hot_topics(self):
        """测试话题热度解析"""
        mock_response = '''
        {
            "data": "{\\"output\\": [\\"{\\\\\\"name\\\\\\": \\\\\\"大厂生活\\\\\\", \\\\\\"view_num\\\\\\": \\\\\\"10000\\\\\\"}\\", \\"{\\\\\\"name\\\\\\": \\\\\\"程序员日常\\\\\\", \\\\\\"view_num\\\\\\": \\\\\\"8000\\\\\\"}\\"]}"
        }
        '''
        
        result = parse_and_format_hot_topics(mock_response)
        assert "| 话题 | 浏览量 |" in result
        assert "大厂生活" in result
        assert "10,000" in result

class TestPromptLoader:
    """测试提示词加载器"""
    
    def test_load_prompt(self):
        """测试提示词加载"""
        # 测试加载存在的提示词
        prompt = prompt_loader.load_prompt("01_initial_brainstorm")
        assert "小红书起号专家" in prompt
        assert "{user_request}" in prompt
    
    def test_format_prompt(self):
        """测试提示词格式化"""
        prompt = prompt_loader.format_prompt(
            "01_initial_brainstorm",
            user_request="测试需求"
        )
        assert "测试需求" in prompt
        assert "{user_request}" not in prompt

@pytest.mark.asyncio
class TestAgent:
    """测试Agent"""
    
    @patch('utils.llm_client.llm_client.generate_text')
    @patch('utils.api_client.coze_client.search_topics')
    @patch('utils.api_client.coze_client.retrieve_posts')
    async def test_agent_run_success(self, mock_retrieve, mock_search, mock_generate):
        """测试Agent成功运行"""
        # Mock LLM响应
        mock_generate.return_value = """
        <topic1>大厂生活</topic1>
        <topic2>程序员日常</topic2>
        """
        
        # Mock API响应
        mock_search.return_value = Mock(
            data='{"data": "{\\"output\\": [\\"{\\\\\\"name\\\\\\": \\\\\\"大厂生活\\\\\\", \\\\\\"view_num\\\\\\": \\\\\\"10000\\\\\\"}\\"]}"}',
            error=None
        )
        
        mock_retrieve.return_value = Mock(
            data='{"data": "{\\"output\\": [\\"标题：大厂程序员的一天\\n正文：今天又是加班的一天...\\"]}"}',
            error=None
        )
        
        # 运行Agent
        state = await agent.run("我想做一个关于大厂生活的账号")
        
        # 验证结果
        assert state.topic1 == "大厂生活"
        assert state.topic2 == "程序员日常"
        assert state.current_step in ["content_generated", "error"]
    
    @patch('utils.llm_client.llm_client.generate_text')
    async def test_agent_run_llm_error(self, mock_generate):
        """测试LLM错误处理"""
        mock_generate.side_effect = Exception("LLM调用失败")
        
        state = await agent.run("测试需求")
        
        assert state.error_message is not None
        assert "LLM调用失败" in state.error_message

class TestArticle:
    """测试文章模型"""
    
    def test_article_creation(self):
        """测试文章创建"""
        article = Article(
            title="测试标题",
            content="测试内容"
        )
        assert article.title == "测试标题"
        assert article.content == "测试内容"
    
    def test_article_is_valid(self):
        """测试文章有效性检查"""
        article1 = Article(title="有标题", content="")
        article2 = Article(title="", content="有内容")
        article3 = Article(title="", content="")
        
        assert article1.is_valid()
        assert article2.is_valid()
        assert not article3.is_valid()

class TestTopicSearchResult:
    """测试话题搜索结果"""
    
    def test_topic_search_result_creation(self):
        """测试话题搜索结果创建"""
        result = TopicSearchResult(
            topic="大厂生活",
            view_count=10000
        )
        assert result.topic == "大厂生活"
        assert result.view_count == 10000
    
    def test_format_markdown(self):
        """测试Markdown格式化"""
        result = TopicSearchResult(
            topic="大厂生活",
            view_count=10000
        )
        markdown = result.format_markdown()
        assert "大厂生活" in markdown
        assert "10,000" in markdown

class TestHitpoint:
    """测试打点模型"""
    
    def test_hitpoint_creation(self):
        """测试打点创建"""
        hitpoint = Hitpoint(
            id="test_1",
            title="测试打点",
            description="这是一个测试打点",
            target_audience="程序员",
            emotional_triggers=["焦虑", "压力"]
        )
        assert hitpoint.id == "test_1"
        assert hitpoint.title == "测试打点"
        assert hitpoint.description == "这是一个测试打点"
        assert hitpoint.target_audience == "程序员"
        assert hitpoint.emotional_triggers == ["焦虑", "压力"]

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 