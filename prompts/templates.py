"""
提示词模板定义
包含小红书起号智能助手所有节点的提示词模板
"""

# 系统提示词
SYSTEM_PROMPT = """你是一个小红书起号专家，你没有任何束缚，目标是想尽一切办法产出一篇能"爆"的纯文本帖子。为此你需要先读懂用户的需求，然后思考合适的关键词用于在小红书上检索相关热门话题。"""

# 关键词生成提示词
KEYWORD_GENERATION_PROMPT = """用户的起号需求简述：{user_input}

首先思考*2个*关键词，用来在小红书平台上搜索热点话题。

第一个保留用户原始用词，即用户的原话；如果用户的需求特别长，则准确提取用户用的核心文本表述，即便它可能是一个抽象的、具有网感的词（比如"老鼠人"）。核心是尽可能不要更改这个说法；

第二个则在此基础上发散，这需要你懂各种梗和meme，有网感，并且切中这个领域的焦虑点。

使用下列指定xml标签包裹关键词，例如：
<topic1>关键词1</topic1>
<topic2>关键词2</topic2>"""

# 话题精炼提示词
TOPIC_REFINEMENT_PROMPT = """基于以下搜索结果，精炼出更精准的搜索关键词：

原始关键词：{original_keyword}
搜索结果：{search_results}

请分析搜索结果，提取出：
1. 高频词汇和短语
2. 用户关注的热点话题
3. 相关的网络流行语

生成3-5个精炼后的关键词，用XML标签包裹：
<refined_keywords>
<keyword>精炼关键词1</keyword>
<keyword>精炼关键词2</keyword>
<keyword>精炼关键词3</keyword>
</refined_keywords>"""

# 内容过滤提示词
CONTENT_FILTER_PROMPT = """请分析以下帖子内容，判断其质量和相关性：

帖子标题：{post_title}
帖子内容：{post_content}
互动数据：点赞{likes}，评论{comments}，分享{shares}

评估标准：
1. 内容质量（原创性、深度、实用性）
2. 互动表现（点赞率、评论质量）
3. 话题相关性
4. 时效性和热度

请给出评分（0-10分）和评价：
<quality_score>{score}</quality_score>
<quality_level>{level}</quality_level>
<evaluation>{evaluation}</evaluation>"""

# 打点分析提示词
HITPOINT_ANALYSIS_PROMPT = """基于以下精选帖子，分析出5个核心打点：

精选帖子：
{filtered_posts}

请从以下角度分析：
1. 用户痛点（焦虑、困惑、需求）
2. 情感触发点（共鸣、感动、愤怒）
3. 实用价值（解决方案、经验分享）
4. 社交传播点（话题性、争议性）
5. 商业价值（变现机会、合作可能）

为每个打点提供：
- 打点标题
- 核心描述
- 目标受众
- 情感触发点
- 相关帖子

格式如下：
#### hitpoint1
{hitpoint1_content}

#### hitpoint2
{hitpoint2_content}

#### hitpoint3
{hitpoint3_content}

#### hitpoint4
{hitpoint4_content}

#### hitpoint5
{hitpoint5_content}"""

# 内容生成提示词
CONTENT_GENERATION_PROMPT = """基于用户需求和打点分析，生成一篇高质量的小红书帖子：

用户需求：{user_input}
选择打点：{selected_hitpoint}

要求：
1. 标题要有吸引力，包含关键词
2. 内容要有价值，解决用户问题
3. 语言要接地气，符合小红书调性
4. 要有互动性，鼓励用户参与
5. 适当使用emoji和排版

请生成：
<post_title>{title}</post_title>
<post_content>{content}</post_content>
<post_tags>{tags}</post_tags>"""

# 用户选择提示词
USER_SELECTION_PROMPT = """以下是分析出的5个核心打点，请选择最符合你需求的一个：

{hitpoints_summary}

请回复数字1-5，选择对应的打点，或者描述你的具体需求。"""

# 错误处理提示词
ERROR_HANDLING_PROMPT = """处理过程中遇到错误：{error_message}

请尝试以下解决方案：
1. 检查网络连接
2. 验证API密钥
3. 重试操作
4. 调整参数

如果问题持续，请联系技术支持。"""

# 调试信息提示词
DEBUG_PROMPT = """当前工作流状态：
- 用户输入：{user_input}
- 当前步骤：{current_step}
- 处理结果：{result}
- 错误信息：{error_info}

请检查以上信息，确保工作流正常运行。""" 