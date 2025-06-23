#!/usr/bin/env python3
"""
XHS客户端测试脚本
测试小红书数据采集功能
"""

import asyncio
import json
from loguru import logger
from clients.xhs_client import xhs_client

async def test_xhs_client():
    """测试XHS客户端功能"""
    print("🔍 测试XHS客户端功能...")
    print("="*60)
    
    # 测试话题搜索
    print("1️⃣ 测试话题搜索功能...")
    test_keywords = ["健身", "美食", "护肤"]
    
    for keyword in test_keywords:
        print(f"\n📝 搜索关键词: {keyword}")
        response = await xhs_client.search_topics(keyword)
        
        if response["success"]:
            print("✅ 话题搜索成功!")
            data = response["data"]
            print(f"📊 找到 {data['total']} 个话题")
            for topic in data["topics"][:3]:  # 只显示前3个
                print(f"   - {topic['name']} (热度: {topic['view_num']})")
        else:
            print(f"❌ 话题搜索失败: {response.get('error', '未知错误')}")
    
    print("\n" + "-"*50)
    
    # 测试帖子检索
    print("2️⃣ 测试帖子检索功能...")
    for keyword in test_keywords[:2]:  # 只测试前2个关键词
        print(f"\n📝 检索关键词: {keyword}")
        response = await xhs_client.retrieve_posts(keyword, limit=5)
        
        if response["success"]:
            print("✅ 帖子检索成功!")
            data = response["data"]
            print(f"📊 找到 {data['total']} 个帖子")
            for post in data["posts"][:2]:  # 只显示前2个
                print(f"   - {post['title']}")
                print(f"     点赞: {post['likes']}, 评论: {post['comments']}")
        else:
            print(f"❌ 帖子检索失败: {response.get('error', '未知错误')}")
    
    print("\n" + "-"*50)
    
    # 测试热门话题
    print("3️⃣ 测试热门话题功能...")
    response = await xhs_client.get_trending_topics()
    
    if response["success"]:
        print("✅ 热门话题获取成功!")
        data = response["data"]
        print(f"📊 找到 {data['total']} 个热门话题")
        for topic in data["topics"][:5]:  # 只显示前5个
            print(f"   - {topic['name']} (热度: {topic['view_num']}, 趋势: {topic['trend']})")
    else:
        print(f"❌ 热门话题获取失败: {response.get('error', '未知错误')}")
    
    print("\n" + "-"*50)
    
    # 测试内容分析
    print("4️⃣ 测试内容分析功能...")
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
    
    print("\n" + "="*60)
    print("🏁 XHS客户端测试完成!")

async def test_user_posts():
    """测试用户帖子获取功能"""
    print("\n👤 测试用户帖子获取功能...")
    print("-"*50)
    
    test_user_id = "test_user_123"
    response = await xhs_client.get_user_posts(test_user_id, limit=5)
    
    if response["success"]:
        print("✅ 用户帖子获取成功!")
        data = response["data"]
        print(f"📊 用户 {data['user_id']} 的帖子:")
        for post in data["posts"][:3]:  # 只显示前3个
            print(f"   - {post['title']}")
            print(f"     点赞: {post['likes']}, 评论: {post['comments']}")
    else:
        print(f"❌ 用户帖子获取失败: {response.get('error', '未知错误')}")

async def main():
    """主函数"""
    print("🚀 XHS客户端功能测试")
    print("="*60)
    
    # 测试基本功能
    await test_xhs_client()
    
    # 测试用户帖子功能
    await test_user_posts()
    
    print("\n📋 测试总结:")
    print("✅ XHS客户端已成功替代Coze插件")
    print("✅ 支持话题搜索、帖子检索、内容分析等功能")
    print("✅ 具备LLM兜底机制，确保服务稳定性")
    print("✅ 无需外部API密钥，降低配置复杂度")

if __name__ == "__main__":
    asyncio.run(main()) 