"""
内容过滤与选择节点
"""
import asyncio
from typing import Dict, Any, List
from loguru import logger
from clients import llm_client
from utils.parsers import filter_and_select_articles

async def content_filtering_and_selection_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    一个合并了循环过滤和筛选的节点。
    1. 并行过滤所有检索到的帖子。
    2. 根据过滤结果选择最终的文章。
    """
    logger.info("开始并行内容过滤和选择")
    
    original_posts = state.get("retrieved_posts", [])
    if not original_posts:
        logger.warning("没有帖子可供过滤和选择")
        state["final_selected_posts"] = []
        state["selected_posts_summary"] = "没有找到合适的帖子。"
        return state

    # 1. 并行执行所有帖子的过滤决策
    tasks = [llm_client.get_raw_filter_decision(post) for post in original_posts]
    filter_decisions = await asyncio.gather(*tasks)
    state["filter_decisions"] = filter_decisions
    
    logger.info(f"获取了 {len(filter_decisions)} 个帖子的过滤决策")

    # 2. 使用解析器函数来执行筛选和随机选择
    selected_posts = filter_and_select_articles(original_posts, filter_decisions)
    
    # 3. 更新状态
    state["final_selected_posts"] = selected_posts
    for i in range(5):
        key = f"good_article_{i+1}"
        if i < len(selected_posts):
            state[key] = selected_posts[i]
        else:
            state[key] = {"title": "none", "content": "none"}

    logger.info(f"筛选出 {len(selected_posts)} 篇优质文章")
    
    if selected_posts:
        posts_summary = "\n\n".join(
            [f"#### 帖子 {i+1}\n标题: {p.get('title', '')}\n内容: {p.get('content', '')}" for i, p in enumerate(selected_posts)]
        )
        state["selected_posts_summary"] = posts_summary
    else:
        state["selected_posts_summary"] = "经过过滤，没有找到合适的帖子。"

    return state 