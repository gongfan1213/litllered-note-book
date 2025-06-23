"""
小红书起号智能助手主工作流
整合所有节点，构建完整的工作流程
"""

import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger
from langgraph.graph import StateGraph, END
# from langgraph.checkpoint.memory import MemorySaver

from models import WorkflowStatus
from workflow_types import WorkflowState
from utils.parsers import extract_xml_tags, parse_and_format_hot_topics, parse_articles_from_response, filter_and_select_articles
from nodes import (
    keyword_generation_node,
    topic_refinement_node,
    hitpoint_analysis_node,
    user_selection_node,
    content_generation_node,
    content_filtering_and_selection_node
)
# Import the new topic search nodes
from nodes.topic_search import (
    topic_search_node_1,
    topic_search_node_2,
    format_topics_node_1,
    format_topics_node_2,
    combine_topic_results_node
)
# Import the new post retrieval nodes
from nodes.post_retrieval import (
    post_retrieval_node_1,
    post_retrieval_node_2,
    parse_posts_node_1,
    parse_posts_node_2,
    combine_post_results_node
)
from config import config

# --- The new, more granular nodes from before ---
def extract_initial_keywords_node(state: WorkflowState) -> WorkflowState:
    """节点：从LLM响应中提取初始关键词"""
    logger.info("节点：提取初始关键词")
    llm_output = state.llm_output if hasattr(state, 'llm_output') else ""
    extracted = extract_xml_tags(llm_output, ["topic1", "topic2"])
    new_state = state.model_copy()
    new_state.primary_keyword = extracted.get("topic1")
    new_state.secondary_keyword = extracted.get("topic2")
    if not new_state.primary_keyword or not new_state.secondary_keyword:
        logger.warning("未能提取到全部初始关键词，流程可能出错")
    logger.info(f"提取到关键词: {new_state.primary_keyword}, {new_state.secondary_keyword}")
    return new_state

def extract_refined_keywords_node(state: WorkflowState) -> WorkflowState:
    """节点：从LLM响应中提取精炼后的关键词"""
    logger.info("节点：提取精炼关键词")
    llm_output = state.refinement_llm_output if hasattr(state, 'refinement_llm_output') else ""
    # The JSON workflow implies we get two new keywords for post retrieval
    extracted = extract_xml_tags(llm_output, ["topic1", "topic2"])
    # We will store these in a new state field
    new_state = state.model_copy()
    new_state.refined_keywords = [kw for kw in extracted.values() if kw]
    logger.info(f"提取到精炼关键词: {new_state.refined_keywords}")
    return new_state

# --- New nodes to be added in workflow.py ---
def extract_hitpoints_node(state: WorkflowState) -> WorkflowState:
    """节点：从LLM响应中解析打点"""
    logger.info("节点：解析打点")
    llm_output = state.hitpoints_llm_output if hasattr(state, 'hitpoints_llm_output') else ""
    new_state = state.model_copy()
    if not llm_output:
        logger.warning("没有打点分析的LLM输出可供解析")
        new_state.hitpoints = []
        return new_state
    
    # 使用 extract_xml_tags 解析打点
    parsed_hitpoints = extract_xml_tags(llm_output, ["hitpoint1", "hitpoint2", "hitpoint3", "hitpoint4", "hitpoint5"])
    # 转换为列表格式
    hitpoints_list = []
    for i in range(1, 6):
        key = f"hitpoint{i}"
        if key in parsed_hitpoints and parsed_hitpoints[key]:
            hitpoints_list.append({"id": f"hitpoint_{i}", "description": parsed_hitpoints[key]})
    
    new_state.hitpoints = hitpoints_list
    logger.info(f"解析出 {len(hitpoints_list)} 个打点")
    return new_state

def should_filter_posts(state: WorkflowState) -> str:
    """条件分支：判断是否需要过滤帖子"""
    logger.info("判断是否需要进入帖子过滤流程")
    if state.retrieved_posts:
        logger.info("有帖子需要过滤，进入过滤分支")
        return "continue_filtering"
    else:
        logger.warning("没有检索到帖子，结束流程")
        return "end_no_posts"

class XiaohongshuAgent:
    """小红书起号智能助手"""
    
    def __init__(self):
        # self.memory = MemorySaver()
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """构建工作流图"""
        logger.info("构建工作流图")
        
        workflow = StateGraph(WorkflowState)
        
        # --- Add all nodes to the workflow ---
        # Step 1: Keyword Generation
        workflow.add_node("keyword_generation", keyword_generation_node)
        workflow.add_node("extract_initial_keywords", extract_initial_keywords_node)

        # Step 2: Parallel Topic Search
        workflow.add_node("topic_search_1", topic_search_node_1)
        workflow.add_node("topic_search_2", topic_search_node_2)
        workflow.add_node("format_topics_1", format_topics_node_1)
        workflow.add_node("format_topics_2", format_topics_node_2)
        workflow.add_node("combine_topic_results", combine_topic_results_node)

        # Step 3: Topic Refinement
        workflow.add_node("topic_refinement", topic_refinement_node)
        workflow.add_node("extract_refined_keywords", extract_refined_keywords_node)

        # Step 4: Parallel Post Retrieval
        workflow.add_node("post_retrieval_1", post_retrieval_node_1)
        workflow.add_node("post_retrieval_2", post_retrieval_node_2)
        workflow.add_node("parse_posts_1", parse_posts_node_1)
        workflow.add_node("parse_posts_2", parse_posts_node_2)
        workflow.add_node("combine_post_results", combine_post_results_node)

        # Step 5: Content Filtering and Selection
        workflow.add_node("content_filtering_and_selection", content_filtering_and_selection_node)
        
        # Step 6: Hitpoint Analysis
        workflow.add_node("hitpoint_analysis", hitpoint_analysis_node)
        workflow.add_node("extract_hitpoints", extract_hitpoints_node)
        
        # Step 7: User Selection and Content Generation
        workflow.add_node("user_selection", user_selection_node)
        workflow.add_node("content_generation", content_generation_node)
        
        # End node
        def end_node_no_posts(state: WorkflowState) -> WorkflowState:
            new_state = state.copy()
            new_state["current_state"] = "end"
            new_state["error_message"] = "流程结束：未检索到帖子。"
            return new_state
        workflow.add_node("end_node_no_posts", end_node_no_posts)

        # --- Wire the graph edges ---
        workflow.set_entry_point("keyword_generation")
        workflow.add_edge("keyword_generation", "extract_initial_keywords")
        
        # After extracting keywords, start both topic searches in parallel
        workflow.add_edge("extract_initial_keywords", "topic_search_1")
        workflow.add_edge("extract_initial_keywords", "topic_search_2")

        # Each search is followed by its own formatting node
        workflow.add_edge("topic_search_1", "format_topics_1")
        workflow.add_edge("topic_search_2", "format_topics_2")

        # After both formatting nodes are done, join the results
        workflow.add_conditional_edges(
            "format_topics_1",
            lambda state: "combine_topic_results" if state.get("formatted_topics_2") else None,
            {"combine_topic_results": "combine_topic_results"}
        )
        workflow.add_conditional_edges(
            "format_topics_2",
            lambda state: "combine_topic_results" if state.get("formatted_topics_1") else None,
            {"combine_topic_results": "combine_topic_results"}
        )

        # Continue the linear flow
        workflow.add_edge("combine_topic_results", "topic_refinement")
        workflow.add_edge("topic_refinement", "extract_refined_keywords")

        # After refining keywords, start both post retrievals in parallel
        workflow.add_edge("extract_refined_keywords", "post_retrieval_1")
        workflow.add_edge("extract_refined_keywords", "post_retrieval_2")

        # Each retrieval is followed by its own parsing node
        workflow.add_edge("post_retrieval_1", "parse_posts_1")
        workflow.add_edge("post_retrieval_2", "parse_posts_2")
        
        # Join the branches after parsing
        workflow.add_conditional_edges(
            "parse_posts_1",
            lambda state: "combine_post_results" if state.get("parsed_posts_2") is not None else None,
            {"combine_post_results": "combine_post_results"}
        )
        workflow.add_conditional_edges(
            "parse_posts_2",
            lambda state: "combine_post_results" if state.get("parsed_posts_1") is not None else None,
            {"combine_post_results": "combine_post_results"}
        )

        # After combining posts, decide whether to filter or end
        workflow.add_conditional_edges(
            "combine_post_results",
            should_filter_posts,
            {
                "continue_filtering": "content_filtering_and_selection",
                "end_no_posts": "end_node_no_posts"
            }
        )
        
        # Continue linear flow
        workflow.add_edge("content_filtering_and_selection", "hitpoint_analysis")
        workflow.add_edge("hitpoint_analysis", "extract_hitpoints")
        workflow.add_edge("extract_hitpoints", "user_selection")
        workflow.add_edge("user_selection", "content_generation")
        workflow.add_edge("content_generation", END)
        workflow.add_edge("end_node_no_posts", END)
        
        logger.info("工作流图构建完成")
        return workflow.compile()
    
    async def run(self, user_input: str, config_id: Optional[str] = None) -> Dict[str, Any]:
        """运行工作流"""
        logger.info(f"开始运行工作流，用户输入: {user_input}")
        
        try:
            # 验证配置
            if not config.validate_config():
                raise ValueError("配置验证失败，请检查环境变量")
            
            # 创建初始状态（字典格式）
            initial_state: WorkflowState = {
                "user_input": user_input,
                "current_state": WorkflowStatus.INITIALIZED.value,
                "keywords": [],
                "primary_keyword": "",
                "secondary_keyword": "",
                "topics": [],
                "search_results": {},
                "retrieved_posts": [],
                "filtered_posts": [],
                "hitpoints": [],
                "generated_content": {},
                "error_message": "",
                "total_posts_processed": 0,
                "total_hitpoints_generated": 0,
                "selected_hitpoint": {}
            }
            logger.info(f"创建初始状态: {initial_state}")
            
            # 运行工作流
            config_dict = {"config_id": config_id} if config_id else {}
            
            result = await self.graph.ainvoke(
                initial_state,
                config=config_dict
            )
            
            logger.info(f"工作流执行完成，结果类型: {type(result)}")
            if result is None:
                logger.error("工作流返回了None")
                # 创建错误状态
                error_state: WorkflowState = {
                    "user_input": user_input,
                    "current_state": WorkflowStatus.ERROR.value,
                    "error_message": "工作流执行返回了None"
                }
                return error_state
            
            logger.info("工作流执行完成")
            return result
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            # 创建错误状态
            error_state: WorkflowState = {
                "user_input": user_input,
                "current_state": WorkflowStatus.ERROR.value,
                "error_message": f"工作流执行失败: {str(e)}"
            }
            return error_state
    
    async def run_with_checkpoint(self, user_input: str, config_id: Optional[str] = None) -> Dict[str, Any]:
        """运行工作流（带检查点）"""
        logger.info(f"开始运行工作流（带检查点），用户输入: {user_input}")
        
        try:
            # 验证配置
            if not config.validate_config():
                raise ValueError("配置验证失败，请检查环境变量")
            
            # 创建初始状态
            initial_state: WorkflowState = {
                "user_input": user_input,
                "current_state": WorkflowStatus.INITIALIZED.value,
                "keywords": [],
                "primary_keyword": "",
                "secondary_keyword": "",
                "topics": [],
                "search_results": {},
                "retrieved_posts": [],
                "filtered_posts": [],
                "hitpoints": [],
                "generated_content": {},
                "error_message": "",
                "total_posts_processed": 0,
                "total_hitpoints_generated": 0,
                "selected_hitpoint": {}
            }
            
            # 运行工作流
            config_dict = {"config_id": config_id} if config_id else {}
            
            result = await self.graph.ainvoke(
                initial_state,
                config=config_dict
            )
            
            logger.info("工作流执行完成（带检查点）")
            return result
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            # 创建错误状态
            error_state: WorkflowState = {
                "user_input": user_input,
                "current_state": WorkflowStatus.ERROR.value,
                "error_message": f"工作流执行失败: {str(e)}"
            }
            return error_state
    
    def get_workflow_status(self, config_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        try:
            # 从内存中获取检查点状态
            # checkpoint = self.memory.get(config_id)
            if checkpoint:
                return {
                    "config_id": config_id,
                    "status": "running",
                    "data": checkpoint
                }
            else:
                return {
                    "config_id": config_id,
                    "status": "not_found",
                    "data": None
                }
        except Exception as e:
            logger.error(f"获取工作流状态失败: {e}")
            return {
                "config_id": config_id,
                "status": "error",
                "error": str(e)
            }

# 全局工作流实例
agent = XiaohongshuAgent() 