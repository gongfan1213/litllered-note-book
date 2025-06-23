#!/usr/bin/env python3
"""
小红书真实数据采集专项测试脚本

本脚本旨在专门测试和验证小红书线上数据的实时采集功能。
它会直接调用带有加密签名的API请求，并且不会触发模拟数据兜底。
如果此脚本运行成功，说明您的Cookie和加密签名算法均有效。
"""

import asyncio
import json
from loguru import logger
from clients.xhs_client import XHSClient # 导入类而非实例
from config import config

async def main():
    """主测试函数"""
    print("🚀 小红书【真实数据】采集专项测试")
    print("="*60)
    print("ℹ️  注意：测试将以非无头模式启动浏览器，您会看到一个浏览器窗口弹出。")
    print("   请观察浏览器中的页面加载情况，判断是否被卡在验证码或其它页面。")

    # 以非无头模式启动，方便调试
    client = XHSClient(headless=False) 

    try:
        # 1. 检查先决条件
        print("1️⃣ 检查配置...")
        if not config.XHS_COOKIE:
            print("❌ 致命错误: .env 文件中未找到或未配置 XHS_COOKIE。")
            print("   请从浏览器获取最新的Cookie并配置到 .env 文件中。")
            return
        print("✅ Cookie配置已找到。")
        print("-" * 50)

        # 2. 测试话题搜索
        print("2️⃣ 测试【话题搜索】接口...")
        keyword_topic = "上海探店"
        print(f"   - 搜索关键词: '{keyword_topic}'")
        topic_response = await client.search_topics(keyword_topic)

        if topic_response.get("success"):
            topics = topic_response.get("data", {}).get("topics", [])
            if topics:
                print(f"✅ 成功! 采集到 {len(topics)} 个相关话题。")
                print("   - 部分结果:")
                for topic in topics[:3]:
                    print(f"     - 话题: {topic.get('name', 'N/A')}, 热度: {topic.get('view_num', 'N/A')}")
            else:
                print("⚠️ 注意: API请求成功，但未返回任何话题数据。可能是关键词冷门或接口返回格式变化。")
        else:
            print(f"❌ 失败! 错误信息: {topic_response.get('error', '未知错误')}")
        print("-" * 50)

        # 3. 测试帖子检索
        print("3️⃣ 测试【帖子检索】接口...")
        keyword_post = "OOTD"
        print(f"   - 搜索关键词: '{keyword_post}'")
        post_response = await client.retrieve_posts(keyword_post, limit=5)

        if post_response.get("success"):
            posts = post_response.get("data", {}).get("posts", [])
            if posts:
                print(f"✅ 成功! 采集到 {len(posts)} 篇相关帖子。")
                print("   - 部分结果:")
                for post in posts[:2]:
                    print(f"     - 标题: {post.get('title', 'N/A')}")
                    print(f"       作者: {post.get('author', 'N/A')}, 点赞: {post.get('likes', 'N/A')}")
            else:
                print("⚠️ 注意: API请求成功，但未返回任何帖子数据。")
        else:
            print(f"❌ 失败! 错误信息: {post_response.get('error', '未知错误')}")
        print("-" * 50)
        
        # 4. 测试用户主页帖子
        print("4️⃣ 测试【用户主页】接口...")
        # 使用小红书官方账号的用户ID作为示例
        user_id = "5b497b41e8ac2b5f976e5399" 
        print(f"   - 采集用户ID: '{user_id}' (小红书官方账号)")
        user_post_response = await client.get_user_posts(user_id, limit=5)

        if user_post_response.get("success"):
            user_posts = user_post_response.get("data", {}).get("posts", [])
            if user_posts:
                print(f"✅ 成功! 采集到 {len(user_posts)} 篇该用户的帖子。")
                print("   - 部分结果:")
                for post in user_posts[:2]:
                    print(f"     - 标题: {post.get('title', 'N/A')}")
                    print(f"       点赞: {post.get('likes', 'N/A')}")
            else:
                print("⚠️ 注意: API请求成功，但未返回任何用户帖子数据（可能该用户无帖子或为私密账户）。")
        else:
            print(f"❌ 失败! 错误信息: {user_post_response.get('error', '未知错误')}")
        print("-" * 50)

        # 5. 测试热搜榜采集
        print("5️⃣ 测试【热搜榜】接口...")
        trending_response = await client.get_trending_topics()
        
        if trending_response.get("success"):
            trending_topics = trending_response.get("data", {}).get("topics", [])
            if trending_topics:
                print(f"✅ 成功! 采集到 {len(trending_topics)} 条热搜。")
                print("   - 部分结果:")
                for topic in trending_topics[:3]:
                    print(f"     - 热搜: {topic.get('name', 'N/A')}, 热度: {topic.get('view_num', 'N/A')}")
            else:
                print("⚠️ 注意: API请求成功，但未返回任何热搜数据。")
        else:
            print(f"❌ 失败! 错误信息: {trending_response.get('error', '未知错误')}")
        print("-" * 50)

        print("🏁 测试完成。请根据以上输出判断采集功能是否正常。")

    finally:
        print("ℹ️ 正在关闭浏览器...")
        await client.shutdown()

if __name__ == "__main__":
    # 配置loguru只显示ERROR级别以上的日志，避免INFO/WARNING干扰判断
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level="ERROR")
    asyncio.run(main()) 