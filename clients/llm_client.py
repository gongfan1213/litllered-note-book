"""
LLM客户端模块
处理与AI模型的通信和对话
"""

import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import config, XHS_USE_MOCK
from models import Keyword, Post, Hitpoint, GeneratedContent

class LLMClient:
    """LLM客户端"""
    
    def __init__(self):
        # 使用OpenAI客户端连接到自定义API端点
        llm_config = config.get_llm_config()
        
        self.default_model = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            openai_api_base=llm_config["base_url"],
            openai_api_key=llm_config["api_key"],
            temperature=0.7,
            max_tokens=4000,
            timeout=llm_config["timeout"]
        )
        
        self.thinking_model = ChatOpenAI(
            model=config.THINKING_MODEL,
            openai_api_base=llm_config["base_url"],
            openai_api_key=llm_config["api_key"],
            temperature=0.3,
            max_tokens=4400,
            timeout=llm_config["timeout"]
        )
        
        # 创建原生OpenAI客户端用于直接调用
        self.openai_client = OpenAI(
            base_url=llm_config["base_url"],
            api_key=llm_config["api_key"]
        )
    
    async def get_raw_keyword_response(self, user_input: str) -> str:
        """获取关键词生成的原始LLM响应"""
        if XHS_USE_MOCK:
            # 针对"大龄剩女"的模拟响应
            if "大龄剩女" in user_input or "剩女" in user_input:
                return """<topic1>大龄女生</topic1><topic2>剩女</topic2>"""
            else:
                return """<topic1>健身</topic1><topic2>美食</topic2>"""
        else:
            # 真实LLM调用逻辑
            pass

    def parse_keywords(self, content: str) -> List[Keyword]:
        """从原始响应中解析关键词"""
        keywords_text = self._extract_keywords_from_xml(content)
        return [
            Keyword(text=kw, relevance_score=1.0)
            for kw in keywords_text
        ]
    
    async def get_raw_refinement_response(self, user_input: str, search_results: str) -> str:
        """调用LLM获取精炼话题的原始响应"""
        logger.info(f"向LLM请求精炼话题")
        
        try:
            from prompts import TOPIC_REFINEMENT_PROMPT
            
            prompt = TOPIC_REFINEMENT_PROMPT.format(
                user_input=user_input, # The prompt needs user_input
                search_results=search_results
            )
            
            messages = [
                SystemMessage(content=config.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.thinking_model.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"LLM请求精炼话题失败: {e}")
            return ""

    def parse_refined_keywords(self, content: str) -> List[str]:
        """从XML中解析精炼后的关键词"""
        return self._extract_keywords_from_xml(content) # Reusing the same XML extractor for <topic1>, <topic2>
    
    async def get_raw_filter_decision(self, post: Dict[str, Any]) -> str:
        """为单个帖子获取过滤决策的原始LLM响应"""
        logger.info(f"为帖子 '{post.get('title')}' 请求过滤决策")
        try:
            from prompts import CONTENT_FILTER_PROMPT
            
            # 确保即使某些键不存在也不会出错
            prompt = CONTENT_FILTER_PROMPT.format(
                post_title=post.get('title', 'N/A'),
                post_content=post.get('content', 'N/A')
            )
            
            messages = [
                # System prompt for filtering is specific
                SystemMessage(content="你是一个内容审核员。你需要判断一篇社媒帖子是否属于低质量内容（如商业推广、引流、内容空洞）。如果是低质量内容，回复<result>0</result>，否则回复<result>1</result>。不要有任何其他多余的回复。"),
                HumanMessage(content=prompt)
            ]
            
            # Using a fast model for this simple classification task
            response = await self.thinking_model.ainvoke(messages)
            
            # Directly extract the '0' or '1'
            decision = self._extract_xml_tag_content(response.content, "result")
            return decision if decision else "0" # Default to filtering out if parsing fails

        except Exception as e:
            logger.error(f"LLM请求过滤决策失败: {e}")
            return "0" # Default to filtering out on error

    def _extract_xml_tag_content(self, content: str, tag: str) -> Optional[str]:
        """通用函数：从XML中提取单个标签的内容"""
        import re
        match = re.search(rf'<{tag}>(.*?)</{tag}>', content, re.DOTALL)
        return match.group(1).strip() if match else None

    async def get_raw_hitpoints_response(*args, **kwargs):
        """模拟LLM打点分析返回"""
        return """<hitpoint1>别再劝我'差不多就嫁了吧'！我的35岁，有钱有闲有爱好，比你们困在婚姻里的潇洒多了</hitpoint1><hitpoint2>过了30岁，我连生病的资格都没有了，因为没人照顾</hitpoint2><hitpoint3>年薪百万，藤校毕业，为何我成了婚恋市场的'老大难'？</hitpoint3><hitpoint4>相亲N次后我悟了：遇到'普信男'比嫁不出去更可怕</hitpoint4><hitpoint5>不是不想结，是真的遇不到：一个'普通'大龄女生的真实困境与自我救赎</hitpoint5>"""

    def parse_hitpoints(self, content: str) -> List[Dict[str, str]]:
        """从LLM响应中解析打点"""
        logger.info("从LLM响应中解析打点")
        # The prompt asks for <hitpoint1>, <hitpoint2>, etc.
        hitpoints = []
        for i in range(1, 6): # Assuming max 5 hitpoints
            tag = f"hitpoint{i}"
            hitpoint_content = self._extract_xml_tag_content(content, tag)
            if hitpoint_content and hitpoint_content != "Error: Cannot find hitpoint tags":
                hitpoints.append({"id": f"hitpoint_{i}", "description": hitpoint_content})
        
        logger.info(f"解析到 {len(hitpoints)} 个打点")
        return hitpoints

    async def filter_content(self, posts: List[Post]) -> List[Post]:
        """过滤内容"""
        logger.info(f"过滤内容: {len(posts)} 个帖子")
        
        try:
            from prompts import CONTENT_FILTER_PROMPT
            
            filtered_posts = []
            
            for post in posts:
                prompt = CONTENT_FILTER_PROMPT.format(
                    post_title=post.title,
                    post_content=post.content,
                    likes=post.likes,
                    comments=post.comments,
                    shares=post.shares
                )
                
                messages = [
                    SystemMessage(content=config.SYSTEM_PROMPT),
                    HumanMessage(content=prompt)
                ]
                
                response = await self.default_model.ainvoke(messages)
                content = response.content
                
                # 解析质量评分
                quality_info = self._extract_quality_info(content)
                
                if quality_info:
                    post.quality_score = quality_info.get("score", 0.0)
                    post.quality_level = quality_info.get("level", "average")
                    
                    # 只保留质量较高的帖子
                    if post.quality_score >= 6.0:
                        filtered_posts.append(post)
            
            return filtered_posts
            
        except Exception as e:
            logger.error(f"过滤内容失败: {e}")
            return posts
    
    async def analyze_hitpoints(self, filtered_posts: List[Post]) -> List[Hitpoint]:
        """分析打点"""
        logger.info(f"分析打点: {len(filtered_posts)} 个帖子")
        
        try:
            from prompts import HITPOINT_ANALYSIS_PROMPT
            
            # 格式化帖子信息
            posts_summary = self._format_posts_summary(filtered_posts)
            
            prompt = HITPOINT_ANALYSIS_PROMPT.format(
                filtered_posts=posts_summary
            )
            
            messages = [
                SystemMessage(content=config.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.thinking_model.ainvoke(messages)
            content = response.content
            
            # 解析打点信息
            hitpoints = self._extract_hitpoints(content)
            
            return hitpoints
            
        except Exception as e:
            logger.error(f"分析打点失败: {e}")
            return []
    
    async def generate_content(self, user_input: str, selected_hitpoint: Hitpoint) -> GeneratedContent:
        """生成内容"""
        logger.info(f"生成内容: {user_input}")
        
        try:
            from prompts import CONTENT_GENERATION_PROMPT
            
            prompt = CONTENT_GENERATION_PROMPT.format(
                user_input=user_input,
                selected_hitpoint=selected_hitpoint.description
            )
            
            messages = [
                SystemMessage(content=config.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.default_model.ainvoke(messages)
            content = response.content
            
            # 解析生成的内容
            generated_content = self._extract_generated_content(content)
            
            return generated_content
            
        except Exception as e:
            logger.error(f"生成内容失败: {e}")
            return GeneratedContent(
                title="生成失败",
                content="内容生成过程中出现错误，请重试。",
                tags=[],
                hitpoints=[selected_hitpoint.id],
                quality_score=0.0
            )
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            # 使用LangChain的异步方法进行测试
            from langchain_core.messages import HumanMessage
            response = await self.default_model.ainvoke([
                HumanMessage(content="Hello, this is a test message.")
            ])
            logger.info("LLM API连接测试成功")
            return True
        except Exception as e:
            logger.error(f"LLM API连接测试失败: {e}")
            return False
    
    def _extract_keywords_from_xml(self, content: str) -> List[str]:
        """从XML中提取关键词"""
        import re
        
        keywords = []
        
        # 提取topic1和topic2标签
        topic1_match = re.search(r'<topic1>(.*?)</topic1>', content, re.DOTALL)
        topic2_match = re.search(r'<topic2>(.*?)</topic2>', content, re.DOTALL)
        
        if topic1_match:
            keywords.append(topic1_match.group(1).strip())
        if topic2_match:
            keywords.append(topic2_match.group(1).strip())
        
        return keywords
    
    def _extract_refined_keywords(self, content: str) -> List[str]:
        """提取精炼关键词"""
        import re
        
        keywords = []
        
        # 提取refined_keywords标签中的关键词
        keyword_matches = re.findall(r'<keyword>(.*?)</keyword>', content, re.DOTALL)
        
        for match in keyword_matches:
            keywords.append(match.strip())
        
        return keywords
    
    def _extract_quality_info(self, content: str) -> Dict[str, Any]:
        """提取质量信息"""
        import re
        
        quality_info = {}
        
        # 提取质量评分
        score_match = re.search(r'<quality_score>(\d+(?:\.\d+)?)</quality_score>', content)
        if score_match:
            quality_info["score"] = float(score_match.group(1))
        
        # 提取质量等级
        level_match = re.search(r'<quality_level>(\w+)</quality_level>', content)
        if level_match:
            quality_info["level"] = level_match.group(1)
        
        return quality_info
    
    def _format_posts_summary(self, posts: List[Post]) -> str:
        """格式化帖子摘要"""
        summary = []
        
        for i, post in enumerate(posts, 1):
            summary.append(f"""
帖子 {i}:
标题: {post.title}
内容: {post.content[:200]}...
互动: 点赞{post.likes}, 评论{post.comments}, 分享{post.shares}
""")
        
        return "\n".join(summary)
    
    def _extract_hitpoints(self, content: str) -> List[Hitpoint]:
        """提取打点信息"""
        import re
        
        hitpoints = []
        
        # 提取hitpoint1到hitpoint5
        for i in range(1, 6):
            pattern = rf'#### hitpoint{i}\n(.*?)(?=#### hitpoint{i+1}|$)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                hitpoint_content = match.group(1).strip()
                hitpoint = Hitpoint(
                    id=f"hitpoint_{i}",
                    title=f"打点{i}",
                    description=hitpoint_content,
                    posts=[],
                    analysis={}
                )
                hitpoints.append(hitpoint)
        
        return hitpoints
    
    def _extract_generated_content(self, content: str) -> GeneratedContent:
        """提取生成的内容"""
        import re
        
        # 提取标题
        title_match = re.search(r'<post_title>(.*?)</post_title>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else "生成的内容"
        
        # 提取正文
        content_match = re.search(r'<post_content>(.*?)</post_content>', content, re.DOTALL)
        post_content = content_match.group(1).strip() if content_match else "内容生成失败"
        
        # 提取标签
        tags_match = re.search(r'<post_tags>(.*?)</post_tags>', content, re.DOTALL)
        tags = []
        if tags_match:
            tags_text = tags_match.group(1).strip()
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
        
        return GeneratedContent(
            title=title,
            content=post_content,
            tags=tags,
            hitpoints=[],
            quality_score=8.0  # 默认评分
        )

async def get_raw_keyword_response(user_input: str) -> str:
    """获取关键词生成的原始LLM响应"""
    if XHS_USE_MOCK:
        # 针对"大龄剩女"的模拟响应
        if "大龄剩女" in user_input or "剩女" in user_input:
            return """<topic1>大龄女生</topic1><topic2>剩女</topic2>"""
        else:
            return """<topic1>健身</topic1><topic2>美食</topic2>"""
    else:
        # 真实LLM调用逻辑
        pass

async def get_raw_refinement_response(*args, **kwargs):
    """模拟LLM话题精炼返回"""
    return """<topic1>大龄女生脱单日记</topic1><topic2>大龄未婚女生找工作</topic2>"""

async def get_raw_user_selection_response(*args, **kwargs):
    """模拟LLM用户选择返回"""
    return """我已经理解了你选择的第3个打点： "别再劝我'差不多就嫁了吧'！我的35岁，有钱有闲有爱好，比你们困在婚姻里的潇洒多了" – 以一种略带"凡尔赛"但又真实的口吻，展现大龄单身女性享受生活、经济独立、精神富足的状态。反驳"年龄到了就贬值"、"不结婚就是失败"的论调，强调个人选择和生活品质。暗中迎合"不婚主义"或"晚婚主义"的思潮，同时 subtly 挑战传统婚恋观，制造话题性。目的：为选择单身或晚婚的女性提供价值认同和情绪出口。"""

async def get_raw_content_generation_response(*args, **kwargs):
    """模拟LLM内容生成返回"""
    return """标题：那些劝我"差不多得了"的，大概没见过我现在的样子

正文：又双叒叕被安排"关心"了，七大姑八大姨轮番上阵，核心思想就一个："你都三十好几了，别太挑，找个差不多的赶紧嫁了，不然以后更难。" 我听着，心里默默翻了个白眼，但脸上还是保持着礼貌的微笑。

"差不多"是个什么标准呢？为了结婚而结婚，然后一头扎进柴米油盐的琐碎，为了孩子学区房焦头烂额，为了平衡工作家庭心力交瘁？如果是这样，那我宁愿"不差不多"。

我的生活，说不上大富大贵，但经济独立，想买什么喜欢的，不用看谁脸色。工作之余，报了个一直想学的陶艺班，周末捏捏泥巴，放空自己，挺解压。上个月刚跟朋友自驾去了趟西北，大漠孤烟的壮阔，是困在写字楼里想象不到的。

偶尔也会羡慕别人成双入对，但更多时候，我享受一个人的清净和自由。不用迁就谁的作息，不用为"今晚谁洗碗"这种事儿烦恼。

可能在他们眼里我是"剩下了"，但在我看来，我只是选择了自己更舒服的生活方式。这种"有钱有闲有爱好，没人管我几点睡"的日子，不香吗？那些"差不多"的幸福，还是留给需要的人吧。

Hashtag: #大龄不将就 #我的快乐我做主 #人间清醒发言 #单身万岁"""

async def get_raw_hitpoints_response(*args, **kwargs):
    """模拟LLM打点分析返回"""
    return """<hitpoint1>别再劝我'差不多就嫁了吧'！我的35岁，有钱有闲有爱好，比你们困在婚姻里的潇洒多了</hitpoint1><hitpoint2>过了30岁，我连生病的资格都没有了，因为没人照顾</hitpoint2><hitpoint3>年薪百万，藤校毕业，为何我成了婚恋市场的'老大难'？</hitpoint3><hitpoint4>相亲N次后我悟了：遇到'普信男'比嫁不出去更可怕</hitpoint4><hitpoint5>不是不想结，是真的遇不到：一个'普通'大龄女生的真实困境与自我救赎</hitpoint5>"""

# 全局LLM客户端实例
llm_client = LLMClient() 