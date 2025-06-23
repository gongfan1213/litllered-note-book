"""
类型定义模块
定义工作流中使用的所有类型
"""

from typing import TypedDict, List, Any

class WorkflowState(TypedDict, total=False):
    """工作流状态类型定义"""
    user_input: str
    current_state: str
    error_message: str

    llm_output: str
    primary_keyword: str
    secondary_keyword: str

    topic_search_result_1: dict
    topic_search_result_2: dict
    formatted_topics_1: str
    formatted_topics_2: str
    combined_topic_results: str

    refinement_llm_output: str
    refined_keywords: List[str]

    post_retrieval_result_1: str
    post_retrieval_result_2: str
    parsed_posts_1: List[Any]
    parsed_posts_2: List[Any]
    retrieved_posts: List[Any]

    final_selected_posts: List[Any]
    selected_posts_summary: str

    hitpoints_llm_output: str
    hitpoints: List[Any]
    selected_hitpoint: dict

    generated_content: dict 