"""
主题搜索节点
基于关键词搜索相关主题
"""
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from models import WorkflowStatus, Topic
from clients import xhs_client, llm_client
from utils.parsers import parse_and_format_hot_topics
from workflow_types import WorkflowState

async def llm_generate_hot_topics(keyword: str) -> str:
    """LLM兜底生成热点话题markdown表格"""
    logger.info(f"LLM兜底生成热点话题: {keyword}")
    prompt = f'请列举当前与"{keyword}"相关的5个小红书最热门话题，并用markdown表格输出，包含话题名称和热度指数。'
    # 直接用 LLMClient 的 default_model
    response = await llm_client.default_model.ainvoke([
        {"role": "user", "content": prompt}
    ])
    return response.content if hasattr(response, "content") else str(response)

async def _search_single_topic(keyword: str) -> Optional[str]:
    """辅助函数：搜索单个主题并返回原始响应"""
    if not keyword:
        return None
    logger.info(f"正在通过XHS API搜索主题: {keyword}")
    response = await xhs_client.search_topics(keyword)
    # 直接返回响应字符串，因为模拟数据已经是字符串格式
    return response

async def topic_search_node_1(state: WorkflowState) -> WorkflowState:
    """主题搜索节点1 (并行)"""
    logger.info("开始主题搜索 1")
    keyword = state.primary_keyword if hasattr(state, 'primary_keyword') else None
    raw_result = await _search_single_topic(keyword)
    if not raw_result:
        raw_result = await llm_generate_hot_topics(keyword)
        logger.info("XHS API失败，已用LLM兜底生成话题1")
    new_state = state.model_copy()
    new_state.topic_search_result_1 = raw_result
    return new_state

async def topic_search_node_2(state: WorkflowState) -> WorkflowState:
    """主题搜索节点2 (并行)"""
    logger.info("开始主题搜索 2")
    keyword = state.secondary_keyword if hasattr(state, 'secondary_keyword') else None
    raw_result = await _search_single_topic(keyword)
    if not raw_result:
        raw_result = await llm_generate_hot_topics(keyword)
        logger.info("XHS API失败，已用LLM兜底生成话题2")
    new_state = state.model_copy()
    new_state.topic_search_result_2 = raw_result
    return new_state

def format_topics_node_1(state: WorkflowState) -> WorkflowState:
    """格式化主题结果节点1"""
    logger.info("开始格式化主题结果 1")
    raw_result = state.topic_search_result_1 if hasattr(state, 'topic_search_result_1') else None
    new_state = state.model_copy()
    if raw_result:
        # 判断是否是LLM兜底生成的内容（包含markdown表格格式）
        if "|" in raw_result and "---" in raw_result:
            # LLM兜底生成的markdown表格，直接使用
            new_state.formatted_topics_1 = raw_result
        else:
            # XHS API返回的JSON格式，需要解析
            try:
                formatted = parse_and_format_hot_topics(raw_result)
                new_state.formatted_topics_1 = formatted if formatted else "解析失败：XHS API返回格式异常"
            except Exception as e:
                new_state.formatted_topics_1 = f"解析失败：{str(e)}"
    else:
        new_state.formatted_topics_1 = "错误：未找到主题搜索结果1"
    return new_state

def format_topics_node_2(state: WorkflowState) -> WorkflowState:
    """格式化主题结果节点2"""
    logger.info("开始格式化主题结果 2")
    raw_result = state.topic_search_result_2 if hasattr(state, 'topic_search_result_2') else None
    new_state = state.model_copy()
    if raw_result:
        # 判断是否是LLM兜底生成的内容（包含markdown表格格式）
        if "|" in raw_result and "---" in raw_result:
            # LLM兜底生成的markdown表格，直接使用
            new_state.formatted_topics_2 = raw_result
        else:
            # XHS API返回的JSON格式，需要解析
            try:
                formatted = parse_and_format_hot_topics(raw_result)
                new_state.formatted_topics_2 = formatted if formatted else "解析失败：XHS API返回格式异常"
            except Exception as e:
                new_state.formatted_topics_2 = f"解析失败：{str(e)}"
    else:
        new_state.formatted_topics_2 = "错误：未找到主题搜索结果2"
    return new_state

def combine_topic_results_node(state: WorkflowState) -> WorkflowState:
    """合并主题结果节点"""
    logger.info("合并格式化的主题结果")
    formatted_1 = state.formatted_topics_1 if hasattr(state, 'formatted_topics_1') else ""
    formatted_2 = state.formatted_topics_2 if hasattr(state, 'formatted_topics_2') else ""
    combined_results = f"### 关键词: {state.primary_keyword}\n{formatted_1}\n\n### 关键词: {state.secondary_keyword}\n{formatted_2}"
    new_state = state.model_copy()
    new_state.combined_topic_results = combined_results
    new_state.topics = [formatted_1, formatted_2]
    return new_state 