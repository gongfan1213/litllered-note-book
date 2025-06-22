# 小红书起号智能助手

基于LangGraph和LangChain构建的智能小红书起号助手，帮助用户快速生成高质量的内容策略和文案。

## 🚀 功能特性

- **智能关键词生成**: 基于用户需求自动生成相关关键词
- **热门话题搜索**: 搜索当前热门话题和趋势
- **内容质量过滤**: 智能过滤低质量内容，确保输出质量
- **打点分析**: 深度分析内容亮点和用户关注点
- **文案生成**: 生成符合小红书风格的高质量文案
- **多模型支持**: 支持多种AI模型，包括Claude、GPT、Qwen等

## 📋 系统要求

- Python 3.8+
- 网络连接（用于API调用）

## 🛠️ 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd langgraph-xiaohongshu-agent
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp env.example .env
   # 编辑 .env 文件，配置API密钥
   ```

## ⚙️ 配置说明

### 必需配置

在 `.env` 文件中配置以下参数：

```bash
# LLM API配置（必需）
LLM_BASE_URL=http://47.84.70.98:9000/v1/
LLM_API_KEY=sk-lBgsAkt3vZEGy2N5Qn738CmHL5ySK3d6ogaKH9SW1oKk6Nt9

# Coze API配置（必需）
COZE_API_KEY=your_coze_api_key_here
COZE_WORKFLOW_ID=7507182130938986537
```

### 可用模型

系统支持以下AI模型：

- **Claude系列**: claude-3-5-sonnet-20241022, claude-3-7-sonnet-20250219, claude-opus-4-20250514
- **GPT系列**: gpt-4, gpt-4o, gpt-3.5-turbo
- **Qwen系列**: qwen-max, qwen-plus, qwen-turbo
- **DeepSeek系列**: deepseek-v3, deepseek-r1
- **其他模型**: gemini-2.0-flash, moonshot-v1-32k, o1等

## 🎯 使用方法

### 快速体验

```bash
python run.py
```

### 命令行模式

```bash
# 基本使用
python main.py "我想做一个关于健身的小红书账号"

# 指定配置ID（用于恢复检查点）
python main.py "美食分享" --config-id my_config

# JSON格式输出
python main.py "大厂生活" --json

# 测试LLM连接
python main.py --test
```

### 交互模式

```bash
python main.py --interactive
```

### 测试LLM配置

```bash
python test_llm.py
```

## 📁 项目结构

```
langgraph-xiaohongshu-agent/
├── clients/                 # API客户端
│   ├── api_client.py       # 通用API客户端
│   └── llm_client.py       # LLM客户端
├── nodes/                  # 工作流节点
│   ├── keyword_generation.py    # 关键词生成
│   ├── topic_search.py          # 话题搜索
│   ├── topic_refinement.py      # 话题精炼
│   ├── post_retrieval.py        # 帖子检索
│   ├── content_filter.py        # 内容过滤
│   ├── hitpoint_analysis.py     # 打点分析
│   ├── user_selection.py        # 用户选择
│   └── content_generation.py    # 内容生成
├── prompts/                # 提示词模板
│   ├── templates.py        # 提示词模板
│   └── *.txt              # 具体提示词文件
├── utils/                  # 工具函数
│   ├── parsers.py         # 解析器
│   ├── prompt_loader.py   # 提示词加载器
│   └── llm_client.py      # LLM客户端（旧版本）
├── tests/                  # 测试文件
├── config.py              # 配置文件
├── models.py              # 数据模型
├── workflow.py            # 主工作流
├── main.py                # 主程序入口
├── run.py                 # 快速启动脚本
├── test_llm.py            # LLM测试脚本
└── requirements.txt       # 依赖包
```

## 🔧 工作流程

1. **关键词生成**: 基于用户输入生成相关关键词
2. **话题搜索**: 搜索热门话题和趋势
3. **话题精炼**: 精炼和优化话题关键词
4. **帖子检索**: 获取相关热门帖子
5. **内容过滤**: 过滤低质量内容
6. **打点分析**: 分析内容亮点和用户关注点
7. **用户选择**: 用户选择感兴趣的打点
8. **内容生成**: 生成最终的小红书文案

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_workflow.py

# 测试LLM连接
python test_llm.py
```

### 测试LLM配置

```bash
# 测试API连接
python main.py --test

# 详细测试
python test_llm.py
```

## 🐛 故障排除

### 常见问题

1. **LLM连接失败**
   - 检查 `LLM_API_KEY` 是否正确
   - 确认网络连接正常
   - 运行 `python test_llm.py` 进行诊断

2. **模型不可用**
   - 检查模型名称是否正确
   - 确认API端点支持该模型
   - 尝试使用其他可用模型

3. **配置验证失败**
   - 检查 `.env` 文件是否存在
   - 确认所有必需的环境变量都已设置
   - 运行 `python main.py --test` 验证配置

### 调试模式

```bash
# 设置详细日志
export LOG_LEVEL=DEBUG
python main.py "测试输入"
```

## 📊 性能优化

- **异步处理**: 所有API调用都使用异步处理
- **并发执行**: 支持并发处理多个任务
- **缓存机制**: 智能缓存减少重复请求
- **错误重试**: 自动重试失败的请求

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题，请提交Issue或联系开发者。

## 🔄 更新日志

### v1.0.0
- 初始版本发布
- 支持多种AI模型
- 完整的工作流程实现
- 交互式命令行界面

---

**注意**: 请确保在使用前正确配置API密钥，并遵守相关服务的使用条款。