"""
小红书数据采集客户端
替代Coze插件，直接采集小红书数据
"""

import asyncio
import json
import re
from typing import List, Dict, Optional, Any
from loguru import logger
try:
    from playwright.async_api import async_playwright, Page, BrowserContext, Playwright
except ImportError:
    # Mock模式下不需要playwright
    async_playwright = None
    Page = None
    BrowserContext = None
    Playwright = None
from config import config
import time
import hashlib
import urllib.parse
from config import XHS_USE_MOCK

class XHSClient:
    """
    使用 Playwright 控制真实浏览器来采集小红书数据的客户端。
    这能有效绕过反爬虫机制，如 x-s, x-t 签名。
    """
    _playwright: Optional[Playwright] = None
    _browser: Optional[BrowserContext] = None
    
    def __init__(self, headless: bool = True):
        """
        初始化客户端
        :param headless: 是否以无头模式运行浏览器，调试时建议设为 False
        """
        self.headless = headless

    async def _get_browser_context(self) -> BrowserContext:
        """
        初始化并返回一个带有Cookie的浏览器上下文。
        使用单例模式确保全局只有一个浏览器实例。
        """
        if self._browser and self._browser.pages:
            return self._browser

        logger.info("正在启动并初始化浏览器...")
        self._playwright = await async_playwright().start()
        browser = await self._playwright.chromium.launch(headless=self.headless)

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        if config.XHS_COOKIE:
            logger.info("正在为浏览器设置Cookie...")
            try:
                cookies = self._parse_cookie_string(config.XHS_COOKIE)
                await context.add_cookies(cookies)
                logger.success("Cookie设置成功！")
            except Exception as e:
                logger.error(f"Cookie解析或设置失败，将以未登录状态访问: {e}")
        else:
            logger.warning("未在.env中找到XHS_COOKIE，将以未登录状态访问，可能影响采集效果。")

        self._browser = context
        return self._browser

    def _parse_cookie_string(self, cookie_string: str) -> List[Dict[str, any]]:
        cookies = []
        for item in cookie_string.split(';'):
            item = item.strip()
            if not item:
                continue
            parts = item.split('=', 1)
            if len(parts) == 2:
                cookies.append({
                    "name": parts[0],
                    "value": parts[1],
                    "domain": ".xiaohongshu.com",
                    "path": "/"
                })
        return cookies

    async def _intercept_api_response(self, page: Page, api_path: str, timeout: int = 30000) -> Optional[Dict]:
        try:
            async with page.expect_response(
                lambda response: api_path in response.url,
                timeout=timeout
            ) as response_info:
                response = await response_info.value
                if response.ok:
                    return await response.json()
                else:
                    logger.error(f"API请求失败: {response.status} {response.status_text}")
                    return None
        except Exception as e:
            logger.error(f"等待API '{api_path}' 响应超时或发生错误: {e}")
            try:
                content = await page.content()
                logger.error(f"页面当前内容:\n{content[:2000]}") # 打印前2000个字符以防过长
            except Exception as page_err:
                logger.error(f"获取页面内容时也发生错误: {page_err}")
            return None

    async def search_topics(self, keyword: str, limit: int = 10) -> Optional[str]:
        """搜索话题"""
        logger.info(f"开始使用Playwright搜索话题: {keyword}")
        
        if XHS_USE_MOCK:
            logger.info("全局Mock开关已开启，强制使用模拟数据")
            return self._get_mock_topics_data(keyword)
        
        # 真实搜索逻辑...
        return None

    async def retrieve_posts(self, keyword: str, limit: int = 10) -> Optional[str]:
        """检索帖子"""
        logger.info(f"开始使用Playwright检索帖子: {keyword}")
        
        if XHS_USE_MOCK:
            logger.info("全局Mock开关已开启，强制使用模拟数据")
            return self._get_mock_posts_data(keyword)
        
        # 真实检索逻辑...
        return None

    async def get_user_posts(self, user_id: str, limit: int = 20) -> dict:
        logger.info(f"开始使用Playwright获取用户帖子: {user_id}")
        if XHS_USE_MOCK:
            logger.info("全局Mock开关已开启，强制使用模拟数据")
            return await self._mock_get_user_posts(user_id, limit)
        if not config.XHS_COOKIE:
            logger.warning("未配置XHS_COOKIE，使用模拟数据")
            return await self._mock_get_user_posts(user_id, limit)
        context = await self._get_browser_context()
        page = await context.new_page()
        try:
            # 监听所有XHR请求，寻找包含用户帖子的API响应
            api_responses = []
            
            def handle_response(response):
                if response.request.resource_type == "xhr":
                    url = response.url
                    if any(path in url for path in ["user", "notes", "profile", "posted"]):
                        api_responses.append({
                            "url": url,
                            "response": response
                        })
            
            page.on("response", handle_response)
            
            # 访问用户主页
            await page.goto(f"https://www.xiaohongshu.com/user/profile/{user_id}", wait_until="domcontentloaded")
            
            # 等待页面加载完成
            await page.wait_for_timeout(3000)
            
            # 模拟用户滚动行为，触发更多API请求
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                
                # 尝试点击"全部笔记"或类似按钮
                try:
                    buttons = await page.query_selector_all("button, a")
                    for button in buttons:
                        text = await button.text_content()
                        if text and any(keyword in text for keyword in ["全部", "笔记", "动态", "发布"]):
                            await button.click()
                            await page.wait_for_timeout(2000)
                            break
                except Exception:
                    pass
            
            # 等待一段时间让API响应完成
            await page.wait_for_timeout(5000)
            
            # 分析收集到的API响应
            for api_data in api_responses:
                try:
                    response = api_data["response"]
                    if response.ok:
                        json_data = await response.json()
                        if json_data and json_data.get("success"):
                            # 尝试不同的数据结构
                            notes = (json_data.get("data", {})
                                    .get("notes", []) or 
                                    json_data.get("data", {})
                                    .get("items", []) or
                                    json_data.get("data", {})
                                    .get("user_notes", []))
                            
                            if notes:
                                posts = []
                                for note in notes[:limit]:
                                    post = {
                                        "id": note.get("note_id", note.get("id", "")),
                                        "title": note.get("display_title", note.get("title", "")),
                                        "content": note.get("desc", note.get("content", "")),
                                        "author": note.get("user", {}).get("nickname", ""),
                                        "likes": str(note.get("interact_info", {}).get("liked_count", 0)),
                                        "comments": str(note.get("interact_info", {}).get("comment_count", 0)),
                                        "shares": str(note.get("interact_info", {}).get("share_count", 0)),
                                        "images": [img.get("url", "") for img in note.get("cover", {}).get("image_list", [])]
                                    }
                                    posts.append(post)
                                
                                if posts:
                                    logger.info(f"成功从API {api_data['url']} 获取到 {len(posts)} 篇用户帖子")
                                    return {"success": True, "data": {"posts": posts, "user_id": user_id, "total": len(posts)}}
                except Exception as e:
                    logger.debug(f"解析API响应失败: {e}")
                    continue
            
            # 如果API方法失败，尝试直接从页面DOM提取
            logger.info("尝试从页面DOM直接提取用户帖子...")
            posts = await self._extract_posts_from_dom(page, limit)
            if posts:
                return {"success": True, "data": {"posts": posts, "user_id": user_id, "total": len(posts)}}
            
            logger.warning(f"未能通过Playwright采集到用户 '{user_id}' 的帖子，将使用模拟数据。")
            return await self._mock_get_user_posts(user_id, limit)
        finally:
            await page.close()
    
    async def _extract_posts_from_dom(self, page, limit: int = 20) -> List[Dict]:
        """从页面DOM中直接提取帖子信息"""
        try:
            # 等待帖子容器加载
            await page.wait_for_selector("[data-id], .note-item, .post-item", timeout=10000)
            
            # 执行JavaScript提取帖子信息
            posts_data = await page.evaluate("""
                () => {
                    const posts = [];
                    // 尝试多种选择器
                    const selectors = [
                        '[data-id]',
                        '.note-item',
                        '.post-item',
                        '.user-note-item',
                        'a[href*="/explore/"]'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            elements.forEach((el, index) => {
                                if (index >= 20) return; // 限制数量
                                
                                const post = {
                                    id: el.getAttribute('data-id') || el.getAttribute('href')?.split('/').pop() || '',
                                    title: el.querySelector('.title, .note-title, h3, h4')?.textContent?.trim() || '',
                                    content: el.querySelector('.desc, .note-desc, .content')?.textContent?.trim() || '',
                                    author: el.querySelector('.author, .user-name')?.textContent?.trim() || '',
                                    likes: el.querySelector('.like-count, .likes')?.textContent?.trim() || '0',
                                    comments: el.querySelector('.comment-count, .comments')?.textContent?.trim() || '0',
                                    shares: el.querySelector('.share-count, .shares')?.textContent?.trim() || '0',
                                    images: []
                                };
                                
                                // 提取图片
                                const imgs = el.querySelectorAll('img');
                                imgs.forEach(img => {
                                    const src = img.src || img.getAttribute('data-src');
                                    if (src) post.images.push(src);
                                });
                                
                                if (post.id) posts.push(post);
                            });
                            break;
                        }
                    }
                    return posts;
                }
            """)
            
            return posts_data[:limit]
        except Exception as e:
            logger.debug(f"从DOM提取帖子失败: {e}")
            return []

    async def get_trending_topics(self) -> Dict[str, Any]:
        logger.info("开始使用Playwright采集小红书热搜榜")
        if XHS_USE_MOCK:
            logger.info("全局Mock开关已开启，强制使用模拟数据")
            return await self._mock_get_trending_topics()
        if not config.XHS_COOKIE:
            logger.warning("未配置XHS_COOKIE，使用模拟数据")
            return await self._mock_get_trending_topics()
        context = await self._get_browser_context()
        page = await context.new_page()
        try:
            # 首先尝试API拦截方法
            api_paths = [
                "/api/v2/search/hot_list",
                "/api/sns/web/v1/search/hot_list",
                "/api/sns/web/v1/hot_list"
            ]
            
            urls = [
                "https://www.xiaohongshu.com/hot-board",
                "https://www.xiaohongshu.com/explore",
                "https://www.xiaohongshu.com"
            ]
            
            api_success = False
            for url in urls:
                for api_path in api_paths:
                    try:
                        logger.info(f"尝试API路径: {api_path} 在页面: {url}")
                        task = asyncio.create_task(self._intercept_api_response(page, api_path, timeout=20000))
                        await page.goto(url, wait_until="domcontentloaded")
                        # 等待页面完全加载
                        await page.wait_for_timeout(3000)
                        api_data = await task
                        if api_data and api_data.get("success"):
                            items = api_data.get("data", {}).get("items", [])
                            if not items:
                                items = api_data.get("data", {}).get("topics", [])  # 尝试其他字段名
                            if items:
                                topics = [{"name": item.get("title", item.get("name", "")), "view_num": item.get("explore_num_text", item.get("view_num", "0")), "hot": True, "trend": item.get("trend", "")} for item in items]
                                logger.info(f"成功通过API获取到 {len(topics)} 个热搜")
                                return {"success": True, "data": {"topics": topics, "total": len(topics)}}
                    except Exception as e:
                        logger.debug(f"热搜榜API路径 {api_path} 在页面 {url} 失败: {e}")
                        continue
            
            # 如果API方法全部失败，尝试直接从页面DOM提取热搜榜
            logger.info("所有API方法失败，尝试从页面DOM直接提取热搜榜...")
            topics = await self._extract_trending_from_dom(page)
            if topics:
                logger.info(f"成功从DOM提取到 {len(topics)} 个热搜")
                return {"success": True, "data": {"topics": topics, "total": len(topics)}}
            
            logger.warning("未能通过Playwright采集到热搜榜数据，将使用模拟数据。")
            return await self._mock_get_trending_topics()
        finally:
            await page.close()
    
    async def _extract_trending_from_dom(self, page) -> List[Dict]:
        """从页面DOM中直接提取热搜榜信息"""
        try:
            # 尝试访问热搜榜页面
            await page.goto("https://www.xiaohongshu.com/hot-board", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # 执行JavaScript提取热搜信息
            topics_data = await page.evaluate("""
                () => {
                    const topics = [];
                    
                    // 尝试多种选择器来找到热搜元素
                    const selectors = [
                        '.hot-item',
                        '.trending-item',
                        '.hot-list-item',
                        '[data-testid*="hot"]',
                        '.hot-board-item',
                        'a[href*="/explore/"]',
                        '.hot-topic-item'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            elements.forEach((el, index) => {
                                if (index >= 50) return; // 限制数量
                                
                                const topic = {
                                    name: '',
                                    view_num: '0',
                                    hot: true,
                                    trend: ''
                                };
                                
                                // 提取标题/名称
                                const titleEl = el.querySelector('.title, .name, .topic-title, h3, h4, a');
                                if (titleEl) {
                                    topic.name = titleEl.textContent?.trim() || titleEl.getAttribute('title') || '';
                                }
                                
                                // 提取热度/浏览量
                                const viewEl = el.querySelector('.view-count, .hot-count, .trending-count, .num');
                                if (viewEl) {
                                    topic.view_num = viewEl.textContent?.trim() || '0';
                                }
                                
                                // 提取趋势
                                const trendEl = el.querySelector('.trend, .trending, .hot-trend');
                                if (trendEl) {
                                    topic.trend = trendEl.textContent?.trim() || '';
                                }
                                
                                // 如果找到了有效的标题，添加到结果中
                                if (topic.name && topic.name.length > 1) {
                                    topics.push(topic);
                                }
                            });
                            break;
                        }
                    }
                    
                    // 如果没有找到特定元素，尝试从页面文本中提取
                    if (topics.length === 0) {
                        const allText = document.body.textContent;
                        const lines = allText.split('\\n').filter(line => line.trim().length > 2);
                        
                        lines.forEach((line, index) => {
                            if (index >= 20) return;
                            const trimmed = line.trim();
                            if (trimmed.length > 2 && trimmed.length < 100) {
                                topics.push({
                                    name: trimmed,
                                    view_num: '未知',
                                    hot: true,
                                    trend: ''
                                });
                            }
                        });
                    }
                    
                    return topics;
                }
            """)
            
            # 过滤和清理数据
            filtered_topics = []
            for topic in topics_data:
                if topic.get('name') and len(topic['name']) > 1:
                    # 清理名称中的多余字符
                    name = topic['name'].replace('\n', ' ').replace('\r', ' ').strip()
                    if name and len(name) < 100:  # 避免过长的标题
                        filtered_topics.append({
                            'name': name,
                            'view_num': topic.get('view_num', '未知'),
                            'hot': True,
                            'trend': topic.get('trend', '')
                        })
            
            return filtered_topics[:20]  # 返回前20个热搜
        except Exception as e:
            logger.debug(f"从DOM提取热搜榜失败: {e}")
            return []

    async def get_note_download_url(self, note_id: str) -> dict:
        logger.info(f"尝试从帖子详情页获取下载链接: {note_id}")
        context = await self._get_browser_context()
        page = await context.new_page()
        try:
            await page.goto(f"https://www.xiaohongshu.com/explore/{note_id}", wait_until="domcontentloaded")
            content = await page.content()
            m = re.search(r'"imageList":(\[.*?\])', content)
            if m:
                # 简单的字符串替换来修复不规范的JSON
                image_json_string = m.group(1).replace('\\', '')
                images = json.loads(image_json_string)
                return {"success": True, "images": images}
            return {"success": False, "error": "未在页面中找到图片列表"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await page.close()

    async def shutdown(self):
        """优雅关闭浏览器和Playwright实例"""
        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
                logger.info("浏览器上下文已关闭。")
        except Exception as e:
            logger.warning(f"关闭浏览器时出现异常: {e}")
        
        try:
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                logger.info("Playwright实例已停止。")
        except Exception as e:
            logger.warning(f"停止Playwright时出现异常: {e}")
        
        # 强制清理asyncio资源
        try:
            import gc
            gc.collect()
        except Exception:
            pass

    # --- MOCK METHODS ---
    async def _mock_search_topics(self, keyword):
        """模拟话题搜索数据"""
        import random
        
        # 根据关键词生成相关话题
        topic_templates = {
            "健身": [
                "居家健身30天挑战", "HIIT燃脂训练", "瑜伽初学者指南", 
                "增肌减脂食谱", "健身房器械使用", "跑步技巧分享"
            ],
            "美食": [
                "快手家常菜", "网红甜品制作", "减脂餐搭配", 
                "烘焙入门教程", "火锅底料配方", "早餐营养搭配"
            ],
            "护肤": [
                "敏感肌护理", "痘痘肌修复", "美白精华推荐", 
                "防晒产品测评", "面膜使用技巧", "护肤品搭配"
            ],
            "旅行": [
                "周末短途游", "民宿推荐", "美食探店", 
                "拍照技巧分享", "旅行装备清单", "景点避坑指南"
            ],
            "穿搭": [
                "春季穿搭", "职场穿搭", "小个子穿搭", 
                "平价品牌推荐", "配饰搭配技巧", "色彩搭配"
            ]
        }
        
        # 获取相关话题模板
        templates = topic_templates.get(keyword, topic_templates.get("美食", []))
        
        # 生成模拟话题数据
        topics = []
        for i, template in enumerate(templates[:5]):
            view_num = random.randint(1000, 50000)
            topics.append({
                "name": f"{template} #{keyword}",
                "view_num": f"{view_num:,}",
                "hot": True,
                "trend": random.choice(["上升", "稳定", "下降"])
            })
        
        return {
            "success": True, 
            "data": {
                "topics": topics, 
                "keyword": keyword, 
                "total": len(topics)
            },
            "raw_data": json.dumps({
                "topics": topics, 
                "keyword": keyword, 
                "total": len(topics)
            }, ensure_ascii=False)
        }

    async def _mock_retrieve_posts(self, keyword, limit):
        """模拟帖子检索数据"""
        import random
        
        # 根据关键词生成相关帖子
        post_templates = {
            "健身": [
                {
                    "title": f"30天健身挑战第{random.randint(1, 30)}天",
                    "content": f"今天完成了{random.randint(20, 60)}分钟的{keyword}训练，感觉超棒！分享几个实用的小技巧...",
                    "author": random.choice(["健身达人小王", "瑜伽老师小李", "私教阿强"]),
                    "likes": random.randint(100, 5000),
                    "comments": random.randint(10, 200),
                    "shares": random.randint(5, 100),
                    "tags": ["健身", "运动", "健康生活"]
                },
                {
                    "title": f"{keyword}新手必看！避坑指南",
                    "content": f"作为一个{keyword}新手，我踩过很多坑。今天来分享我的经验，希望能帮到大家...",
                    "author": random.choice(["运动小白", "健身博主", "健康达人"]),
                    "likes": random.randint(200, 8000),
                    "comments": random.randint(20, 300),
                    "shares": random.randint(10, 150),
                    "tags": ["新手", "教程", "经验分享"]
                }
            ],
            "美食": [
                {
                    "title": f"超简单的{keyword}做法，新手也能学会",
                    "content": f"今天教大家做一道超级简单的{keyword}，只需要3步就能完成，味道绝对不输外面卖的！",
                    "author": random.choice(["美食博主小美", "家常菜达人", "烘焙师小王"]),
                    "likes": random.randint(500, 10000),
                    "comments": random.randint(50, 500),
                    "shares": random.randint(20, 300),
                    "tags": ["美食", "教程", "家常菜"]
                },
                {
                    "title": f"{keyword}的10种创新吃法",
                    "content": f"厌倦了传统的{keyword}做法？来看看这10种创新吃法，每一种都让人惊艳！",
                    "author": random.choice(["创意美食家", "美食摄影师", "料理达人"]),
                    "likes": random.randint(300, 6000),
                    "comments": random.randint(30, 400),
                    "shares": random.randint(15, 250),
                    "tags": ["创新", "美食", "创意料理"]
                }
            ],
            "护肤": [
                {
                    "title": f"{keyword}产品测评，真实使用感受",
                    "content": f"用了3个月的{keyword}产品，今天来分享真实的使用感受，优缺点都有，绝对不吹不黑！",
                    "author": random.choice(["护肤博主小美", "美妆达人", "皮肤科医生"]),
                    "likes": random.randint(800, 15000),
                    "comments": random.randint(100, 800),
                    "shares": random.randint(50, 400),
                    "tags": ["护肤", "测评", "真实感受"]
                },
                {
                    "title": f"{keyword}的正确使用方法",
                    "content": f"很多人用{keyword}产品都用错了方法，今天来教大家正确的使用步骤和注意事项...",
                    "author": random.choice(["护肤专家", "美妆博主", "皮肤管理师"]),
                    "likes": random.randint(600, 12000),
                    "comments": random.randint(80, 600),
                    "shares": random.randint(40, 350),
                    "tags": ["使用方法", "护肤", "技巧"]
                }
            ]
        }
        
        # 获取相关帖子模板
        templates = post_templates.get(keyword, post_templates.get("美食", []))
        
        # 生成模拟帖子数据
        posts = []
        for i in range(min(limit, len(templates) * 2)):
            template = templates[i % len(templates)]
            post = template.copy()
            post["id"] = f"mock_post_{keyword}_{i}"
            post["title"] = post["title"].replace("{keyword}", keyword)
            post["content"] = post["content"].replace("{keyword}", keyword)
            posts.append(post)
        
        return {
            "success": True, 
            "data": {
                "posts": posts, 
                "keyword": keyword, 
                "total": len(posts)
            },
            "raw_data": json.dumps({
                "posts": posts, 
                "keyword": keyword, 
                "total": len(posts)
            }, ensure_ascii=False)
        }

    async def _mock_get_user_posts(self, user_id, limit):
        """模拟用户帖子数据"""
        import random
        
        posts = []
        for i in range(limit):
            post = {
                "id": f"user_post_{user_id}_{i}",
                "title": f"用户{user_id}的第{i+1}篇分享",
                "content": f"这是用户{user_id}分享的第{i+1}篇内容，希望能给大家带来一些启发和帮助...",
                "author": user_id,
                "likes": random.randint(50, 2000),
                "comments": random.randint(5, 100),
                "shares": random.randint(2, 50),
                "tags": ["用户分享", "生活记录", "经验分享"]
            }
            posts.append(post)
        
        return {
            "success": True, 
            "data": {
                "posts": posts, 
                "user_id": user_id, 
                "total": len(posts)
            },
            "raw_data": json.dumps({
                "posts": posts, 
                "user_id": user_id, 
                "total": len(posts)
            }, ensure_ascii=False)
        }

    async def _mock_get_trending_topics(self):
        """模拟热门话题数据"""
        import random
        
        trending_topics = [
            {
                "name": "春季穿搭指南",
                "view_num": f"{random.randint(10000, 100000):,}",
                "trend": "上升",
                "hot": True
            },
            {
                "name": "减脂餐搭配",
                "view_num": f"{random.randint(8000, 80000):,}",
                "trend": "稳定",
                "hot": True
            },
            {
                "name": "敏感肌护理",
                "view_num": f"{random.randint(6000, 60000):,}",
                "trend": "上升",
                "hot": True
            },
            {
                "name": "周末短途游",
                "view_num": f"{random.randint(5000, 50000):,}",
                "trend": "下降",
                "hot": True
            },
            {
                "name": "快手家常菜",
                "view_num": f"{random.randint(12000, 120000):,}",
                "trend": "上升",
                "hot": True
            }
        ]
        
        return {
            "success": True, 
            "data": {
                "topics": trending_topics, 
                "total": len(trending_topics)
            },
            "raw_data": json.dumps({
                "topics": trending_topics, 
                "total": len(trending_topics)
            }, ensure_ascii=False)
        }

    def _get_xs_xt(self, api_path: str, params: dict) -> tuple[str, str]:
        """
        生成小红书API请求所需的 x-s 和 x-t 加密签名
        """
        # x-t 是毫秒级时间戳
        xt = str(int(time.time() * 1000))
        
        # 将参数进行URL编码
        query = urllib.parse.urlencode(params)
        
        # 这是社区发现的加密盐，如果未来失效需要更新
        salt = "WSUDD"
        
        # 构造待加密的字符串
        pre_hash_str = f"{api_path}?{query}{salt}"
        
        # 计算MD5哈希值作为 x-s
        xs = hashlib.md5(pre_hash_str.encode()).hexdigest()
        
        return xs, xt

    async def _make_signed_request(self, api_path: str, params: dict):
        """
        发送带有 x-s 和 x-t 签名的请求
        """
        xs, xt = self._get_xs_xt(api_path, params)
        
        headers = {
            "x-s": xs,
            "x-t": xt
        }
        
        url = f"https://www.xiaohongshu.com{api_path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code == 200:
                    try:
                        return {"success": True, "data": resp.json(), "raw_data": resp.text}
                    except json.JSONDecodeError:
                        return {"success": False, "error": "JSON解析失败", "raw_data": resp.text}
                else:
                    logger.error(f"带签名请求失败: {resp.status_code} - {resp.text}")
                    return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            logger.error(f"带签名请求异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_content(self, posts: List[Dict]) -> Dict[str, Any]:
        """分析帖子内容"""
        logger.info(f"分析内容: {len(posts)} 个帖子")
        
        if not posts:
            return {
                "success": False,
                "error": "没有帖子数据可供分析"
            }
        
        # 分析热门标签
        all_tags = []
        for post in posts:
            if "tags" in post:
                all_tags.extend(post["tags"])
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 分析互动数据
        total_likes = sum(int(post.get("likes", 0)) for post in posts)
        total_comments = sum(int(post.get("comments", 0)) for post in posts)
        total_shares = sum(int(post.get("shares", 0)) for post in posts)
        
        # 找出最热门的帖子
        hot_posts = sorted(posts, key=lambda x: int(x.get("likes", 0)), reverse=True)[:3]
        
        analysis_result = {
            "total_posts": len(posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "avg_likes": total_likes // len(posts) if posts else 0,
            "avg_comments": total_comments // len(posts) if posts else 0,
            "avg_shares": total_shares // len(posts) if posts else 0,
            "hot_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "hot_posts": hot_posts,
            "content_themes": self._extract_content_themes(posts)
        }
        
        return {
            "success": True,
            "data": analysis_result,
            "raw_data": json.dumps(analysis_result, ensure_ascii=False)
        }
    
    def _extract_content_themes(self, posts: List[Dict]) -> List[str]:
        """提取内容主题"""
        themes = []
        for post in posts:
            content = post.get("content", "").lower()
            if "健身" in content or "运动" in content:
                themes.append("健身运动")
            elif "美食" in content or "探店" in content:
                themes.append("美食探店")
            elif "护肤" in content or "美妆" in content:
                themes.append("护肤美妆")
            elif "旅行" in content or "旅游" in content:
                themes.append("旅行分享")
            elif "穿搭" in content or "时尚" in content:
                themes.append("时尚穿搭")
            else:
                themes.append("生活分享")
        
        # 统计主题频率
        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        return sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)

    def _get_mock_topics_data(self, keyword: str) -> str:
        """获取模拟话题数据"""
        if "大龄女生" in keyword or "大龄" in keyword:
            return json.dumps({
                "topics": [
                    {"name": "大龄女生脱单日记 #大龄女生", "view_num": "1,000,032", "hot": True, "trend": "上升"},
                    {"name": "大龄未婚女生找工作 #大龄女生", "view_num": "321,686", "hot": True, "trend": "稳定"},
                    {"name": "大龄读研女生 #大龄女生", "view_num": "54,915", "hot": False, "trend": "下降"},
                    {"name": "大龄女生相亲实录 #大龄女生", "view_num": "25,580", "hot": True, "trend": "上升"},
                    {"name": "大龄女生的坦白局 #大龄女生", "view_num": "2,882", "hot": False, "trend": "稳定"}
                ]
            })
        elif "剩女" in keyword:
            return json.dumps({
                "topics": [
                    {"name": "大龄剩男剩女的烦恼 #剩女", "view_num": "178,351", "hot": True, "trend": "上升"},
                    {"name": "大龄剩女的无奈 #剩女", "view_num": "153,161", "hot": True, "trend": "稳定"},
                    {"name": "为什么这么多大龄剩女不结婚竟然 #剩女", "view_num": "138,736", "hot": True, "trend": "上升"},
                    {"name": "一线城市大龄剩女 #剩女", "view_num": "73,348", "hot": False, "trend": "下降"},
                    {"name": "剩女择偶标准条件 #剩女", "view_num": "43,773", "hot": True, "trend": "稳定"}
                ]
            })
        else:
            return json.dumps({
                "topics": [
                    {"name": "居家健身30天挑战 #健身", "view_num": "47,719", "hot": True, "trend": "稳定"},
                    {"name": "HIIT燃脂训练 #健身", "view_num": "15,928", "hot": True, "trend": "上升"},
                    {"name": "瑜伽初学者指南 #健身", "view_num": "4,238", "hot": False, "trend": "上升"},
                    {"name": "增肌减脂食谱 #健身", "view_num": "49,466", "hot": True, "trend": "稳定"},
                    {"name": "健身房器械使用 #健身", "view_num": "31,981", "hot": False, "trend": "下降"}
                ]
            })

    def _get_mock_posts_data(self, keyword: str) -> str:
        """获取模拟帖子数据"""
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

# 全局客户端实例
xhs_client = XHSClient() 