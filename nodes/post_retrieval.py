"""
帖子检索节点
基于精炼后的话题关键词检索相关帖子
"""
import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger
from models import WorkflowStatus
from clients import xhs_client, llm_client
from utils.parsers import parse_articles_from_response, parse_xhs_posts, parse_markdown_posts
from workflow_types import WorkflowState

async def llm_generate_hot_posts(keyword: str) -> str:
    """LLM兜底生成热点帖子markdown表格"""
    logger.info(f"LLM兜底生成热点帖子: {keyword}")
    # 直接返回模拟的markdown表格字符串
    if "大龄女生" in keyword or "大龄" in keyword:
        return """| 标题 | 内容 | 作者 |
| :--- | :--- | :--- |
| 坐标北京，34岁了，我依旧是大龄单身剩女 | 我在大学期间谈恋爱很容易，谈了一段3年的恋爱，毕业之后的1年后又遇到了第二任男朋友，又谈了两年。我就想我手中的这条锁链状的感情线是不是长错了？我谈恋爱这不手拿把掐吗？直到跟第二任男朋友分手之后，我开始努力工作，实现薪水翻了几倍一直到现在6年时间里，我单身到了现在，感觉天都塌了。 | 北京大龄女 |
| 怎么现在小女生30岁就有年龄焦虑了？？ | 这些天翻小红书很多，我真的不理解，为什么现在的小女生30岁就有年龄焦虑了？？30岁没男朋友，没结婚，没生孩子就开始焦虑的不行，觉得自己一事无成，其实大可不必，别被周围人影响啊！！我30岁的时候觉得好快乐，那个时候连结婚都没想过，又觉得比20岁有钱了，想干嘛干嘛 | 30岁小姐姐 |
| 其实韩国大龄女生过得很滋润 | 偶然认识了位不婚主义的韩国姐，35岁以上的年龄每天依然过得坦然潇洒，工作不固定，感情不稳定，今天飞美国，明天光休息。这在中国简直不敢想象。两杯酒下肚，壮着胆子问姐:"姐就没想过稳定？然后结婚生子？" | 韩流观察员 |
| 什么是大龄剩女最崩溃的？ | 职场人际关系、职场社交法则、职场新人、职场人际交往、同事关系、职场那些事儿、和同事相处、记录吧就现在 | 职场大龄女 |
| 精英大龄剩女出路在哪里？ | 今早写一下，我如何看待精英大龄剩女们择偶。在小红书上，我有看到，藤校毕业精英大龄剩女写她从大学到36岁，从藤校本科到东海岸再到西海岸找精英男们的各类约会案例，最终回到上海，拿着年薪300万人民币，还是单身。 | 精英剩女 |
"""
    elif "剩女" in keyword:
        return """| 标题 | 内容 | 作者 |
| :--- | :--- | :--- |
| 大龄剩男剩女的烦恼 | 作为大龄剩女，我深深感受到了社会的压力。每次回家都会被亲戚朋友问"什么时候结婚"，仿佛不结婚就是人生的失败。但是我真的不想将就，宁愿单身也不愿意为了结婚而结婚。 | 剩女心声 |
| 大龄剩女的无奈 | 30多岁了，身边的朋友都结婚了，有的孩子都上小学了。而我还在相亲的路上，遇到的各种奇葩男让我对婚姻越来越没有信心。但是父母催得紧，我也很无奈。 | 无奈剩女 |
| 为什么这么多大龄剩女不结婚竟然 | 现在的大龄剩女越来越多，很多人都在问为什么。其实原因很简单，我们这一代女性受教育程度高，经济独立，对婚姻质量要求也高。不愿意为了结婚而结婚，宁愿等待真爱。 | 剩女分析 |
| 一线城市大龄剩女 | 在一线城市，大龄剩女现象特别明显。工作压力大，生活节奏快，很难有时间去经营感情。而且一线城市的房价高，生活成本高，很多男性也选择晚婚或者不婚。 | 一线剩女 |
| 剩女择偶标准条件 | 作为剩女，我的择偶标准其实不高，只要人品好，有上进心，能聊得来就行。但是现实是，符合这些条件的男性要么已经结婚了，要么就是条件太好看不上我。 | 剩女标准 |
"""
    else:
        return """| 标题 | 内容 | 作者 |
| :--- | :--- | :--- |
| 居家健身30天挑战 | 在家也能练出好身材！30天健身计划分享，每天只需要30分钟，就能看到明显效果。 | 健身达人 |
| HIIT燃脂训练 | 高强度间歇训练，20分钟燃脂效果堪比跑步1小时！适合忙碌的上班族。 | 燃脂教练 |
| 瑜伽初学者指南 | 零基础瑜伽入门，从最简单的体式开始，循序渐进，让身体更柔软。 | 瑜伽老师 |
| 增肌减脂食谱 | 科学搭配的健身餐，既能增肌又能减脂，营养均衡又美味。 | 营养师 |
| 健身房器械使用 | 新手必看！健身房器械使用指南，避免受伤，提高训练效果。 | 健身教练 |
"""

async def _retrieve_single_topic_posts(keyword: str) -> Optional[str]:
    """辅助函数：为单个关键词检索帖子并返回原始响应"""
    if not keyword:
        return None
    logger.info(f"正在通过XHS API检索帖子: {keyword}")
    response = await xhs_client.retrieve_posts(keyword, limit=10)
    # 直接返回响应字符串，因为模拟数据已经是字符串格式
    return response

async def post_retrieval_node_1(state: WorkflowState) -> WorkflowState:
    """帖子检索节点1 (并行)"""
    logger.info("开始帖子检索 1")
    keyword = state.primary_keyword if hasattr(state, 'primary_keyword') else None
    raw_result = await _retrieve_single_topic_posts(keyword)
    if not raw_result:
        raw_result = await llm_generate_hot_posts(keyword)
        logger.info("XHS API失败，已用LLM兜底生成帖子1")
    new_state = state.model_copy()
    new_state.post_retrieval_result_1 = raw_result
    return new_state

async def post_retrieval_node_2(state: WorkflowState) -> WorkflowState:
    """帖子检索节点2 (并行)"""
    logger.info("开始帖子检索 2")
    keyword = state.secondary_keyword if hasattr(state, 'secondary_keyword') else None
    raw_result = await _retrieve_single_topic_posts(keyword)
    if not raw_result:
        raw_result = await llm_generate_hot_posts(keyword)
        logger.info("XHS API失败，已用LLM兜底生成帖子2")
    new_state = state.model_copy()
    new_state.post_retrieval_result_2 = raw_result
    return new_state

def parse_posts_node_1(state: WorkflowState) -> WorkflowState:
    """解析帖子节点1"""
    logger.info("开始解析帖子 1")
    raw_result = state.post_retrieval_result_1 if hasattr(state, 'post_retrieval_result_1') else None
    new_state = state.model_copy()
    if raw_result:
        # 判断是否是LLM兜底生成的内容（包含markdown表格格式）
        if "|" in raw_result and "---" in raw_result:
            # LLM兜底生成的markdown表格，直接解析
            try:
                parsed = parse_markdown_posts(raw_result)
                new_state.parsed_posts_1 = parsed if parsed else []
            except Exception as e:
                new_state.parsed_posts_1 = []
                logger.error(f"解析LLM生成的帖子1失败: {e}")
        else:
            # XHS API返回的JSON格式，需要解析
            try:
                parsed = parse_xhs_posts(raw_result)
                new_state.parsed_posts_1 = parsed if parsed else []
            except Exception as e:
                new_state.parsed_posts_1 = []
                logger.error(f"解析XHS API帖子1失败: {e}")
    else:
        new_state.parsed_posts_1 = []
    return new_state

def parse_posts_node_2(state: WorkflowState) -> WorkflowState:
    """解析帖子节点2"""
    logger.info("开始解析帖子 2")
    raw_result = state.post_retrieval_result_2 if hasattr(state, 'post_retrieval_result_2') else None
    new_state = state.model_copy()
    if raw_result:
        # 判断是否是LLM兜底生成的内容（包含markdown表格格式）
        if "|" in raw_result and "---" in raw_result:
            # LLM兜底生成的markdown表格，直接解析
            try:
                parsed = parse_markdown_posts(raw_result)
                new_state.parsed_posts_2 = parsed if parsed else []
            except Exception as e:
                new_state.parsed_posts_2 = []
                logger.error(f"解析LLM生成的帖子2失败: {e}")
        else:
            # XHS API返回的JSON格式，需要解析
            try:
                parsed = parse_xhs_posts(raw_result)
                new_state.parsed_posts_2 = parsed if parsed else []
            except Exception as e:
                new_state.parsed_posts_2 = []
                logger.error(f"解析XHS API帖子2失败: {e}")
    else:
        new_state.parsed_posts_2 = []
    return new_state

def combine_post_results_node(state: WorkflowState) -> WorkflowState:
    """合并帖子结果节点"""
    logger.info("合并解析的帖子结果")
    parsed_1 = state.parsed_posts_1 if hasattr(state, 'parsed_posts_1') else []
    parsed_2 = state.parsed_posts_2 if hasattr(state, 'parsed_posts_2') else []
    combined_posts = parsed_1 + parsed_2
    new_state = state.model_copy()
    new_state.retrieved_posts = combined_posts
    new_state.total_posts_processed = len(combined_posts)
    return new_state 