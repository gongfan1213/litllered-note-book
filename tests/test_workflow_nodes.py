#!/usr/bin/env python3
"""
工作流节点测试脚本
测试小红书起号智能助手的各个节点功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import json
from loguru import logger
from workflow_types import WorkflowState
from nodes.topic_search import (
    topic_search_node_1, topic_search_node_2,
    format_topics_node_1, format_topics_node_2,
    combine_topic_results_node
)
from nodes.post_retrieval import (
    post_retrieval_node_1, post_retrieval_node_2,
    parse_posts_node_1, parse_posts_node_2,
    combine_post_results_node
)
from nodes.content_filter import content_filter_node
from nodes.hitpoint_analysis import hitpoint_analysis_node
from nodes.user_selection import user_selection_node
from nodes.content_generation import content_generation_node
from nodes.topic_refinement import topic_refinement_node
from nodes.keyword_generation import keyword_generation_node
from models import WorkflowState, WorkflowStatus

async def test_keyword_generation():
    """测试关键词生成节点"""
    print("\n🔍 测试关键词生成节点...")
    print("-" * 50)
    
    # 创建初始状态
    state = WorkflowState(
        user_input="大龄剩女",
        current_state=WorkflowStatus.INITIALIZED
    )
    
    # 调用关键词生成节点
    result_state = await keyword_generation_node(state)
    
    print("✅ 关键词生成完成!")
    print(f"📝 LLM输出: {result_state.llm_output[:100] if result_state.llm_output else ''}...")
    
    return result_state

def test_extract_initial_keywords(state):
    """测试初始关键词提取"""
    print("\n🔍 测试初始关键词提取...")
    print("-" * 50)
    
    from workflow import extract_initial_keywords_node
    
    result_state = extract_initial_keywords_node(state)
    
    print("✅ 关键词提取完成!")
    print(f"📝 主要关键词: {result_state.primary_keyword}")
    print(f"📝 次要关键词: {result_state.secondary_keyword}")
    
    return result_state

async def test_topic_search_nodes(state):
    """测试话题搜索节点"""
    print("\n🔍 测试话题搜索节点...")
    print("-" * 50)
    
    # 并行执行两个话题搜索
    task1 = topic_search_node_1(state)
    task2 = topic_search_node_2(state)
    
    result1, result2 = await asyncio.gather(task1, task2)
    
    print("✅ 话题搜索完成!")
    print(f"📝 搜索1结果: {result1.topic_search_result_1[:100] if result1.topic_search_result_1 else ''}...")
    print(f"📝 搜索2结果: {result2.topic_search_result_2[:100] if result2.topic_search_result_2 else ''}...")
    
    # 格式化结果
    formatted1 = format_topics_node_1(result1)
    formatted2 = format_topics_node_2(result2)
    
    # 合并结果
    combined_state = formatted1.model_copy()
    # 手动合并状态
    combined_state.topic_search_result_2 = formatted2.topic_search_result_2
    combined_state.formatted_topics_2 = formatted2.formatted_topics_2
    final_result = combine_topic_results_node(combined_state)
    
    print("✅ 话题结果格式化完成!")
    print(f"📝 合并结果: {final_result.combined_topic_results[:200] if final_result.combined_topic_results else ''}...")
    
    return final_result

async def test_topic_refinement(state):
    """测试话题精炼节点"""
    print("\n🔍 测试话题精炼节点...")
    print("-" * 50)
    
    result_state = await topic_refinement_node(state)
    
    print("✅ 话题精炼完成!")
    print(f"📝 精炼输出: {result_state.refinement_llm_output[:200] if result_state.refinement_llm_output else ''}...")
    
    return result_state

def test_extract_refined_keywords(state):
    """测试精炼关键词提取"""
    print("\n🔍 测试精炼关键词提取...")
    print("-" * 50)
    
    from workflow import extract_refined_keywords_node
    
    result_state = extract_refined_keywords_node(state)
    
    print("✅ 精炼关键词提取完成!")
    print(f"📝 精炼关键词: {result_state.refined_keywords}")
    
    return result_state

async def test_post_retrieval_nodes(state):
    """测试帖子检索节点"""
    print("\n🔍 测试帖子检索节点...")
    print("-" * 50)
    
    # 并行执行两个帖子检索
    task1 = post_retrieval_node_1(state)
    task2 = post_retrieval_node_2(state)
    
    result1, result2 = await asyncio.gather(task1, task2)
    
    print("✅ 帖子检索完成!")
    print(f"📝 检索1结果类型: {type(result1.post_retrieval_result_1)}")
    print(f"📝 检索2结果类型: {type(result2.post_retrieval_result_2)}")
    
    # 解析结果
    parsed1 = parse_posts_node_1(result1)
    parsed2 = parse_posts_node_2(result2)
    
    # 合并结果
    combined_state = parsed1.model_copy()
    # 手动合并状态
    combined_state.post_retrieval_result_2 = parsed2.post_retrieval_result_2
    combined_state.parsed_posts_2 = parsed2.parsed_posts_2
    final_result = combine_post_results_node(combined_state)
    
    print("✅ 帖子结果解析完成!")
    print(f"📝 合并后帖子数量: {len(final_result.retrieved_posts)}")
    
    return final_result

async def test_content_filter(state):
    """测试内容过滤节点"""
    print("\n🔍 测试内容过滤节点...")
    print("-" * 50)
    
    result_state = await content_filter_node(state)
    
    print("✅ 内容过滤完成!")
    print(f"📝 过滤后帖子数量: {len(result_state.filtered_posts)}")
    
    return result_state

async def test_hitpoint_analysis(state):
    """测试打点分析节点"""
    print("\n🔍 测试打点分析节点...")
    print("-" * 50)
    
    result_state = await hitpoint_analysis_node(state)
    
    print("✅ 打点分析完成!")
    print(f"📝 打点分析输出: {result_state.hitpoints_llm_output[:200] if result_state.hitpoints_llm_output else ''}...")
    
    return result_state

def test_extract_hitpoints(state):
    """测试打点提取"""
    print("\n🔍 测试打点提取...")
    print("-" * 50)
    
    from workflow import extract_hitpoints_node
    
    result_state = extract_hitpoints_node(state)
    
    print("✅ 打点提取完成!")
    print(f"📝 提取的打点: {result_state.hitpoints}")
    
    return result_state

async def test_user_selection(state):
    """测试用户选择节点"""
    print("\n🔍 测试用户选择节点...")
    print("-" * 50)
    
    result_state = await user_selection_node(state)
    
    print("✅ 用户选择完成!")
    print(f"📝 用户选择输出: {result_state.user_selection_llm_output[:200] if result_state.user_selection_llm_output else ''}...")
    
    return result_state

async def test_content_generation(state):
    """测试内容生成节点"""
    print("\n🔍 测试内容生成节点...")
    print("-" * 50)
    
    result_state = await content_generation_node(state)
    
    print("✅ 内容生成完成!")
    if result_state.generated_content:
        print(f"📝 生成的内容标题: {result_state.generated_content.title}")
        print(f"📝 生成的内容: {result_state.generated_content.content[:300] if result_state.generated_content.content else ''}...")
    else:
        print("📝 生成的内容: 无")
    
    return result_state

async def main():
    """主测试函数"""
    print("🚀 开始测试工作流节点")
    print("=" * 60)
    
    try:
        # 1. 关键词生成
        state = await test_keyword_generation()
        
        # 2. 提取初始关键词
        state = test_extract_initial_keywords(state)
        
        # 3. 话题搜索
        state = await test_topic_search_nodes(state)
        
        # 4. 话题精炼
        state = await test_topic_refinement(state)
        
        # 5. 提取精炼关键词
        state = test_extract_refined_keywords(state)
        
        # 6. 帖子检索
        state = await test_post_retrieval_nodes(state)
        
        # 7. 内容过滤
        state = await test_content_filter(state)
        
        # 8. 打点分析
        state = await test_hitpoint_analysis(state)
        
        # 9. 提取打点
        state = test_extract_hitpoints(state)
        
        # 10. 用户选择
        state = await test_user_selection(state)
        
        # 11. 内容生成
        state = await test_content_generation(state)
        
        print("\n" + "=" * 60)
        print("🎉 所有节点测试完成!")
        print("\n📋 测试总结:")
        print("✅ 关键词生成和提取功能正常")
        print("✅ 话题搜索和精炼功能正常")
        print("✅ 帖子检索和解析功能正常")
        print("✅ 内容过滤功能正常")
        print("✅ 打点分析功能正常")
        print("✅ 用户选择功能正常")
        print("✅ 内容生成功能正常")
        print("✅ 模拟数据工作正常，可以测试后续节点")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 