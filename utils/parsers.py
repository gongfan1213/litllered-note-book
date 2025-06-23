import re
import json
import random
from typing import List, Dict, Any, Tuple

def extract_xml_tags(text: str, tags: List[str]) -> Dict[str, str]:
    """
    从文本中提取指定的XML标签内容。
    这是一个通用的函数，用于替代原始工作流中的多个 '提取xml'  javascript代码。

    Args:
        text: 包含XML标签的原始字符串。
        tags: 需要提取的标签名列表, e.g., ['topic1', 'topic2']

    Returns:
        一个字典，键是标签名，值是标签内容。
    """
    # 确保text是字符串类型
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    
    extractions = {}
    for tag in tags:
        # 使用非贪婪模式匹配来找到标签内容
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extractions[tag] = match.group(1).strip()
        else:
            # 如果找不到，返回一个错误或默认值，以增加健壮性
            extractions[tag] = f"Error: Cannot find {tag} tag"
    return extractions

def parse_and_format_hot_topics(response_body: str) -> str:
    """
    解析来自 'fisherman' (Coze API) 的响应，并将其格式化为Markdown表格。
    替代 '整理md表格' javascript 代码。

    Args:
        response_body: HTTP请求的原始响应体，通常是一个JSON字符串。

    Returns:
        一个Markdown格式的表格字符串，或者在出错时返回错误信息。
    """
    try:
        # 1. 解析最外层的JSON
        data = json.loads(response_body)
        
        # 2. 尝试直接解析，如果失败再尝试嵌套解析
        topics = None
        
        # 直接格式：{"topics": [...]}
        if "topics" in data and isinstance(data["topics"], list):
            topics = data["topics"]
        # 嵌套格式：{"data": "{\"output\": [...]}"}
        elif "data" in data:
            try:
                inner_data_str = data.get("data")
                if isinstance(inner_data_str, str):
                    inner_data = json.loads(inner_data_str)
                    output_list = inner_data.get("output")
                    if isinstance(output_list, list):
                        topics = []
                        for item_str in output_list:
                            if isinstance(item_str, str):
                                item = json.loads(item_str)
                                topics.append(item)
                            else:
                                topics.append(item_str)
            except (json.JSONDecodeError, TypeError):
                pass
        
        if not topics:
            return "错误: 无法解析话题数据。"

        # 3. 构建Markdown表格
        markdown_table = "| 话题 | 浏览量 | 趋势 |\n| :--- | ---: | :---: |\n"
        for item in topics:
            try:
                name = item.get("name", "N/A")
                view_num_str = item.get("view_num", "0")
                trend = item.get("trend", "N/A")
                
                # 格式化数字，例如 10000 -> 10,000
                try:
                    # 移除逗号并转换为整数
                    view_num_clean = view_num_str.replace(",", "")
                    formatted_view_num = f"{int(view_num_clean):,}"
                except (ValueError, TypeError):
                    formatted_view_num = view_num_str
                    
                markdown_table += f"| {name} | {formatted_view_num} | {trend} |\n"
            except (TypeError, ValueError) as e:
                # 增加对不规范item的容错处理
                markdown_table += f"| 解析单个条目出错 | {e} | N/A |\n"
                
        return markdown_table
    except (json.JSONDecodeError, TypeError) as e:
        return f"错误: 解析响应失败 - {e}"

def parse_articles_from_response(response_body: str) -> Tuple[List[Dict[str, str]], str]:
    """
    从帖子检索API的响应中解析出文章列表。
    替代 '提取帖子' javascript 代码。

    Args:
        response_body: HTTP请求的原始响应体 (JSON字符串)。

    Returns:
        一个元组，包含:
        - articles (List[Dict[str, str]]): 解析后的文章列表, 每个文章是{'title': '...', 'content': '...'}。
        - debug_url (str): 调试URL。
    """
    try:
        response = json.loads(response_body)
        data_obj = json.loads(response.get("data", "{}"))
        debug_url = response.get("debug_url", "")
        
        articles = []
        output_list = data_obj.get("output", [])

        if not isinstance(output_list, list):
            raise ValueError("响应中的 'output' 不是一个列表。")

        for item in output_list:
            # 正则表达式比 `split` 更健壮，可以处理 "正文：" 不存在的情况
            title_match = re.search(r"^标题：(.*?)(?=\n正文：|$)", item, re.DOTALL)
            content_match = re.search(r"正文：(.*)", item, re.DOTALL)

            title = title_match.group(1).strip() if title_match else ""
            content = content_match.group(1).strip() if content_match else ""

            # 如果没有找到 "标题：" 或 "正文："，但内容不为空，则将整个item作为content
            if not title and not content and item.strip():
                content = item.strip()
            # 如果只有标题没有正文
            elif title and not content:
                pass # title已经提取，content为空
            
            articles.append({"title": title, "content": content})
        
        return articles, debug_url

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # 在出错时返回空列表和错误信息，而不是让整个流程崩溃
        return [], f"解析帖子失败: {e}"


def filter_and_select_articles(articles: List[Dict[str, str]], results: List[str]) -> List[Dict[str, str]]:
    """
    根据过滤结果，筛选并随机选择最多5篇优质文章。
    替代 'milker' javascript 代码。

    Args:
        articles: 原始文章列表。
        results: 过滤结果列表，每个元素是 "0" 或 "1"。

    Returns:
        筛选和随机选择后的文章列表。
    """
    if not articles or not results:
        return []

    # 1. 过滤文章
    filtered_articles = [
        article for i, article in enumerate(articles) 
        if i < len(results) and results[i] == "1" and article.get("title") and article.get("content")
    ]

    if not filtered_articles:
        return []

    # 2. 随机洗牌 (Fisher-Yates 算法)
    shuffled = filtered_articles[:] # 创建副本
    for i in range(len(shuffled) - 1, 0, -1):
        j = random.randint(0, i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    
    # 3. 选择前5篇
    return shuffled[:5]

def parse_markdown_posts(markdown_content: str) -> List[Dict[str, Any]]:
    """解析markdown格式的帖子内容"""
    posts = []
    lines = markdown_content.strip().split('\n')
    
    # 跳过表头
    start_idx = 0
    for i, line in enumerate(lines):
        if '|' in line and '---' in line:
            start_idx = i + 1
            break
    
    # 解析表格行
    for line in lines[start_idx:]:
        if '|' in line and line.strip():
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 4:
                post = {
                    "title": parts[1] if len(parts) > 1 else "",
                    "content": parts[2] if len(parts) > 2 else "",
                    "author": parts[3] if len(parts) > 3 else "",
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "views": 0,
                    "quality_score": 0.0,
                    "tags": []
                }
                posts.append(post)
    
    return posts

def parse_xhs_posts(json_content: str) -> List[Dict[str, Any]]:
    """解析XHS API返回的JSON格式帖子"""
    try:
        data = json.loads(json_content)
        posts = []
        
        # 根据XHS API的实际返回格式解析
        if isinstance(data, dict) and 'data' in data:
            items = data['data'].get('items', [])
        elif isinstance(data, list):
            items = data
        else:
            items = []
        
        for item in items:
            post = {
                "title": item.get('title', ''),
                "content": item.get('content', ''),
                "author": item.get('author', ''),
                "likes": item.get('likes', 0),
                "comments": item.get('comments', 0),
                "shares": item.get('shares', 0),
                "views": item.get('views', 0),
                "quality_score": 0.0,
                "tags": item.get('tags', [])
            }
            posts.append(post)
        
        return posts
    except Exception as e:
        logger.error(f"解析XHS JSON失败: {e}")
        return [] 