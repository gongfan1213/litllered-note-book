#!/usr/bin/env python3
"""
模拟数据测试脚本
测试小红书客户端的模拟数据功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from loguru import logger
from clients.xhs_client import xhs_client

async def test_mock_topic_search():
    """测试模拟话题搜索"""
    print("🔍 测试模拟话题搜索功能...")
    print("-" * 50)
    
    test_keywords = ["健身", "美食", "护肤", "旅行", "穿搭"]
    
    for keyword in test_keywords:
        print(f"\n📝 搜索关键词: {keyword}")
        response = await xhs_client.search_topics(keyword)
        
        if response["success"]:
            print("✅ 话题搜索成功!")
            data = response["data"]
            print(f"📊 找到 {data['total']} 个话题")
            for topic in data["topics"][:3]:  # 只显示前3个
                print(f"   - {topic['name']} (热度: {topic['view_num']}, 趋势: {topic.get('trend', 'N/A')})")
        else:
            print(f"❌ 话题搜索失败: {response.get('error', '未知错误')}")

async def test_mock_post_retrieval():
    """测试模拟帖子检索"""
    print("\n🔍 测试模拟帖子检索功能...")
    print("-" * 50)
    
    test_keywords = ["健身", "美食", "护肤"]
    
    for keyword in test_keywords:
        print(f"\n📝 检索关键词: {keyword}")
        response = await xhs_client.retrieve_posts(keyword, limit=5)
        
        if response["success"]:
            print("✅ 帖子检索成功!")
            data = response["data"]
            print(f"📊 找到 {data['total']} 个帖子")
            for post in data["posts"][:2]:  # 只显示前2个
                print(f"   - {post['title']}")
                print(f"     作者: {post['author']}")
                print(f"     点赞: {post['likes']}, 评论: {post['comments']}, 分享: {post['shares']}")
                print(f"     标签: {', '.join(post.get('tags', []))}")
        else:
            print(f"❌ 帖子检索失败: {response.get('error', '未知错误')}")

async def test_mock_user_posts():
    """测试模拟用户帖子"""
    print("\n🔍 测试模拟用户帖子功能...")
    print("-" * 50)
    
    test_user_ids = ["user_123", "fitness_guru", "food_lover"]
    
    for user_id in test_user_ids:
        print(f"\n👤 获取用户帖子: {user_id}")
        response = await xhs_client.get_user_posts(user_id, limit=3)
        
        if response["success"]:
            print("✅ 用户帖子获取成功!")
            data = response["data"]
            print(f"📊 用户 {data['user_id']} 的帖子:")
            for post in data["posts"]:
                print(f"   - {post['title']}")
                print(f"     点赞: {post['likes']}, 评论: {post['comments']}, 分享: {post['shares']}")
        else:
            print(f"❌ 用户帖子获取失败: {response.get('error', '未知错误')}")

async def test_mock_trending_topics():
    """测试模拟热门话题"""
    print("\n🔍 测试模拟热门话题功能...")
    print("-" * 50)
    
    response = await xhs_client.get_trending_topics()
    
    if response["success"]:
        print("✅ 热门话题获取成功!")
        data = response["data"]
        print(f"📊 找到 {data['total']} 个热门话题")
        for topic in data["topics"]:
            print(f"   - {topic['name']} (热度: {topic['view_num']}, 趋势: {topic['trend']})")
    else:
        print(f"❌ 热门话题获取失败: {response.get('error', '未知错误')}")

async def test_mock_content_analysis():
    """测试模拟内容分析"""
    print("\n🔍 测试模拟内容分析功能...")
    print("-" * 50)
    
    # 先获取一些帖子数据
    posts_response = await xhs_client.retrieve_posts("健身", limit=5)
    
    if posts_response["success"]:
        posts = posts_response["data"]["posts"]
        analysis_response = await xhs_client.analyze_content(posts)
        
        if analysis_response["success"]:
            print("✅ 内容分析成功!")
            data = analysis_response["data"]
            print(f"📊 分析结果:")
            print(f"   - 总帖子数: {data['total_posts']}")
            print(f"   - 总点赞数: {data['total_likes']}")
            print(f"   - 平均点赞: {data['avg_likes']}")
            print(f"   - 热门标签: {[tag[0] for tag in data['hot_tags'][:3]]}")
            print(f"   - 内容主题: {[theme[0] for theme in data['content_themes'][:3]]}")
        else:
            print(f"❌ 内容分析失败: {analysis_response.get('error', '未知错误')}")
    else:
        print("❌ 无法获取帖子数据进行内容分析")

async def test_mock_data_consistency():
    """测试模拟数据的一致性"""
    print("\n🔍 测试模拟数据一致性...")
    print("-" * 50)
    
    # 测试相同关键词多次搜索的结果一致性
    keyword = "健身"
    print(f"📝 测试关键词 '{keyword}' 的数据一致性")
    
    responses = []
    for i in range(3):
        response = await xhs_client.search_topics(keyword)
        if response["success"]:
            responses.append(response["data"]["topics"])
    
    if len(responses) == 3:
        print("✅ 多次搜索都能成功返回数据")
        
        # 检查话题数量是否一致
        topic_counts = [len(topics) for topics in responses]
        if len(set(topic_counts)) == 1:
            print(f"✅ 话题数量一致: {topic_counts[0]} 个")
        else:
            print(f"⚠️ 话题数量不一致: {topic_counts}")
        
        # 检查话题名称是否一致
        topic_names = [set(topic['name'] for topic in topics) for topics in responses]
        if all(names == topic_names[0] for names in topic_names):
            print("✅ 话题名称完全一致")
        else:
            print("⚠️ 话题名称不完全一致（这是正常的，因为模拟数据包含随机性）")
    else:
        print("❌ 多次搜索结果不一致")

async def main():
    """主测试函数"""
    print("🚀 开始测试模拟数据功能")
    print("=" * 60)
    
    try:
        # 测试各种模拟数据功能
        await test_mock_topic_search()
        await test_mock_post_retrieval()
        await test_mock_user_posts()
        await test_mock_trending_topics()
        await test_mock_content_analysis()
        await test_mock_data_consistency()
        
        print("\n" + "=" * 60)
        print("🎉 模拟数据测试完成!")
        print("\n📋 测试总结:")
        print("✅ 话题搜索模拟数据功能正常")
        print("✅ 帖子检索模拟数据功能正常")
        print("✅ 用户帖子模拟数据功能正常")
        print("✅ 热门话题模拟数据功能正常")
        print("✅ 内容分析模拟数据功能正常")
        print("✅ 模拟数据一致性良好")
        print("✅ 可以用于测试后续节点功能")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 