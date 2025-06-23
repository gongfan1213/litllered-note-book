"""
小红书起号智能助手数据模型
定义工作流状态、数据结构等
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class WorkflowStatus(str, Enum):
    """工作流状态枚举"""
    INITIALIZED = "initialized"
    KEYWORD_GENERATION = "keyword_generation"
    TOPIC_SEARCH = "topic_search"
    TOPIC_REFINEMENT = "topic_refinement"
    POST_RETRIEVAL = "post_retrieval"
    CONTENT_FILTERING = "content_filtering"
    HITPOINT_ANALYSIS = "hitpoint_analysis"
    USER_SELECTION = "user_selection"
    CONTENT_GENERATION = "content_generation"
    COMPLETED = "completed"
    ERROR = "error"

class PostQuality(str, Enum):
    """帖子质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"

class Keyword(BaseModel):
    """关键词模型"""
    text: str = Field(..., description="关键词文本")
    relevance_score: float = Field(default=0.0, description="相关性评分")
    search_volume: Optional[int] = Field(default=None, description="搜索量")
    created_at: datetime = Field(default_factory=datetime.now)

class Topic(BaseModel):
    """话题模型"""
    keyword: str = Field(..., description="话题关键词")
    posts: List[Dict[str, Any]] = Field(default_factory=list, description="相关帖子")
    search_results: Optional[Dict[str, Any]] = Field(default=None, description="搜索结果")
    created_at: datetime = Field(default_factory=datetime.now)

class Post(BaseModel):
    """帖子模型"""
    id: str = Field(..., description="帖子ID")
    title: str = Field(..., description="帖子标题")
    content: str = Field(..., description="帖子内容")
    author: str = Field(..., description="作者")
    likes: int = Field(default=0, description="点赞数")
    comments: int = Field(default=0, description="评论数")
    shares: int = Field(default=0, description="分享数")
    views: int = Field(default=0, description="浏览量")
    quality_score: float = Field(default=0.0, description="质量评分")
    quality_level: PostQuality = Field(default=PostQuality.AVERAGE, description="质量等级")
    tags: List[str] = Field(default_factory=list, description="标签")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def engagement_rate(self) -> float:
        """计算互动率"""
        if self.views == 0:
            return 0.0
        return (self.likes + self.comments + self.shares) / self.views

class Hitpoint(BaseModel):
    """打点分析模型"""
    id: str = Field(..., description="打点ID")
    title: str = Field(..., description="打点标题")
    description: str = Field(..., description="打点描述")
    posts: List[Post] = Field(default_factory=list, description="相关帖子")
    analysis: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    created_at: datetime = Field(default_factory=datetime.now)

class GeneratedContent(BaseModel):
    """生成内容模型"""
    title: str = Field(..., description="内容标题")
    content: str = Field(..., description="内容正文")
    tags: List[str] = Field(default_factory=list, description="标签")
    hitpoints: List[str] = Field(default_factory=list, description="相关打点")
    quality_score: float = Field(default=0.0, description="质量评分")
    created_at: datetime = Field(default_factory=datetime.now)

class Article(BaseModel):
    """文章模型"""
    id: str = Field(..., description="文章ID")
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容")
    author: str = Field(..., description="作者")
    publish_date: Optional[datetime] = Field(default=None, description="发布日期")
    tags: List[str] = Field(default_factory=list, description="标签")
    created_at: datetime = Field(default_factory=datetime.now)

class ContentFilterResult(BaseModel):
    """内容过滤结果模型"""
    post_id: str = Field(..., description="帖子ID")
    quality_score: float = Field(..., description="质量评分")
    quality_level: PostQuality = Field(..., description="质量等级")
    is_approved: bool = Field(..., description="是否通过过滤")
    reason: Optional[str] = Field(default=None, description="过滤原因")
    created_at: datetime = Field(default_factory=datetime.now)

class ModelConfig(BaseModel):
    """模型配置"""
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=4000, description="最大token数")
    top_p: float = Field(default=1.0, description="top_p参数")
    frequency_penalty: float = Field(default=0.0, description="频率惩罚")
    presence_penalty: float = Field(default=0.0, description="存在惩罚")

class WorkflowState(BaseModel):
    """工作流状态模型"""
    # 基础信息
    user_input: str = Field(..., description="用户输入")
    current_state: WorkflowStatus = Field(default=WorkflowStatus.INITIALIZED, description="当前状态")
    
    # LLM输出
    llm_output: Optional[str] = Field(default=None, description="LLM输出")
    refinement_llm_output: Optional[str] = Field(default=None, description="精炼LLM输出")
    hitpoints_llm_output: Optional[str] = Field(default=None, description="打点分析LLM输出")
    user_selection_llm_output: Optional[str] = Field(default=None, description="用户选择LLM输出")
    
    # 关键词生成
    keywords: List[Keyword] = Field(default_factory=list, description="生成的关键词")
    primary_keyword: Optional[str] = Field(default=None, description="主要关键词")
    secondary_keyword: Optional[str] = Field(default=None, description="次要关键词")
    refined_keywords: List[str] = Field(default_factory=list, description="精炼关键词")
    
    # 话题搜索
    topics: List[Topic] = Field(default_factory=list, description="搜索的话题")
    search_results: Dict[str, Any] = Field(default_factory=dict, description="搜索结果")
    topic_search_result_1: Optional[str] = Field(default=None, description="话题搜索结果1")
    topic_search_result_2: Optional[str] = Field(default=None, description="话题搜索结果2")
    formatted_topics_1: Optional[str] = Field(default=None, description="格式化话题结果1")
    formatted_topics_2: Optional[str] = Field(default=None, description="格式化话题结果2")
    combined_topic_results: Optional[str] = Field(default=None, description="合并话题结果")
    
    # 帖子检索
    retrieved_posts: List[Post] = Field(default_factory=list, description="检索的帖子")
    filtered_posts: List[Post] = Field(default_factory=list, description="过滤后的帖子")
    post_retrieval_result_1: Optional[str] = Field(default=None, description="帖子检索结果1")
    post_retrieval_result_2: Optional[str] = Field(default=None, description="帖子检索结果2")
    parsed_posts_1: List[Dict[str, Any]] = Field(default_factory=list, description="解析的帖子1")
    parsed_posts_2: List[Dict[str, Any]] = Field(default_factory=list, description="解析的帖子2")
    
    # 打点分析
    hitpoints: List[Hitpoint] = Field(default_factory=list, description="打点分析")
    selected_hitpoint: Optional[Dict[str, Any]] = Field(default=None, description="用户选择的打点")
    
    # 内容生成
    generated_content: Optional[GeneratedContent] = Field(default=None, description="生成的内容")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 统计信息
    total_posts_processed: int = Field(default=0, description="处理的帖子总数")
    total_hitpoints_generated: int = Field(default=0, description="生成的打点总数")
    
    def update_state(self, new_state: WorkflowStatus):
        """更新工作流状态"""
        self.current_state = new_state
        self.updated_at = datetime.now()
    
    def add_keyword(self, keyword: Keyword):
        """添加关键词"""
        self.keywords.append(keyword)
        self.updated_at = datetime.now()
    
    def add_topic(self, topic: Topic):
        """添加话题"""
        self.topics.append(topic)
        self.updated_at = datetime.now()
    
    def add_post(self, post: Post):
        """添加帖子"""
        self.retrieved_posts.append(post)
        self.total_posts_processed += 1
        self.updated_at = datetime.now()
    
    def add_hitpoint(self, hitpoint: Hitpoint):
        """添加打点"""
        self.hitpoints.append(hitpoint)
        self.total_hitpoints_generated += 1
        self.updated_at = datetime.now()
    
    def set_error(self, error_message: str):
        """设置错误信息"""
        self.error_message = error_message
        self.current_state = WorkflowStatus.ERROR
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_input": self.user_input,
            "current_state": self.current_state.value,
            "keywords": [kw.dict() for kw in self.keywords],
            "topics": [topic.dict() for topic in self.topics],
            "retrieved_posts": [post.dict() for post in self.retrieved_posts],
            "filtered_posts": [post.dict() for post in self.filtered_posts],
            "hitpoints": [hp.dict() for hp in self.hitpoints],
            "generated_content": self.generated_content.dict() if self.generated_content else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error_message": self.error_message,
            "total_posts_processed": self.total_posts_processed,
            "total_hitpoints_generated": self.total_hitpoints_generated
        }

class APIResponse(BaseModel):
    """API响应模型"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    raw_data: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

class SearchRequest(BaseModel):
    """搜索请求模型"""
    keyword: str = Field(..., description="搜索关键词")
    limit: int = Field(default=10, description="结果数量限制")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件")

class ContentGenerationRequest(BaseModel):
    """内容生成请求模型"""
    user_input: str = Field(..., description="用户输入")
    hitpoints: List[str] = Field(..., description="打点列表")
    style: Optional[str] = Field(default="casual", description="内容风格")
    length: Optional[str] = Field(default="medium", description="内容长度") 