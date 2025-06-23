# 小红书起号智能助手

一个基于LangGraph的AI驱动小红书内容创作助手，能够自动分析用户输入、搜索热门话题、生成爆点内容，并创作高质量的小红书文案。

![image](https://github.com/user-attachments/assets/814db0a6-27ba-40e4-b6cc-ffa41c658d34)

## 🚀 快速开始

### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp env.example .env
# 编辑 .env 文件，填入你的API密钥

# 运行测试
python tests/test_workflow_nodes.py
```

### 前端界面

项目包含一个精美的React前端界面，展示所有工作流内容：

```bash
# 进入前端目录
cd frontend

# 安装依赖并启动
npm install
npm start
```

前端将在 http://localhost:3000 启动，提供：
- 🎨 小红书风格设计
- 📊 可视化工作流状态
- 📱 响应式布局
- 🔄 实时数据展示

## 🎯 核心功能

### 1. 智能关键词生成
- 分析用户输入，生成相关关键词
- 支持关键词精炼和优化

### 2. 热门话题搜索
- 自动搜索小红书热门话题
- 分析话题热度和趋势

### 3. 内容质量过滤
- AI驱动的帖子质量评估
- 自动筛选高质量内容

### 4. 爆点分析
- 智能识别内容爆点
- 生成多个内容方向

### 5. 文案生成
- 基于选定爆点生成文案
- 包含标题、正文、标签

## 🏗️ 项目结构

```
langgraph-xiaohongshu-agent/
├── frontend/                 # React前端界面
│   ├── src/
│   │   ├── App.js           # 主应用组件
│   │   └── index.js         # 应用入口
│   ├── package.json         # 前端依赖
│   └── README.md            # 前端说明
├── nodes/                   # 工作流节点
│   ├── keyword_generation.py
│   ├── topic_search.py
│   ├── post_retrieval.py
│   ├── content_filter.py
│   ├── hitpoint_analysis.py
│   ├── user_selection.py
│   └── content_generation.py
├── clients/                 # API客户端
│   ├── llm_client.py       # LLM客户端
│   └── xhs_client.py       # 小红书客户端
├── prompts/                 # 提示词模板
├── tests/                   # 测试文件
├── models.py               # 数据模型
├── workflow.py             # 工作流定义
└── requirements.txt        # Python依赖
```

## 🎨 前端界面特色

### 设计风格
- **小红书品牌色彩** - 采用官方红色 (#ff2442)
- **现代UI设计** - Material UI组件库
- **清晰信息架构** - 分标签页展示内容
- **响应式布局** - 适配各种设备

### 功能展示
- **工作流状态** - 实时显示7个执行阶段
- **关键词分析** - 展示初始和精炼关键词
- **话题搜索** - 显示热门话题及数据
- **帖子内容** - 展示检索到的帖子
- **打点分析** - 可视化AI生成的爆点
- **生成内容** - 展示最终文案

### 交互体验
- **一键运行** - 模拟完整工作流
- **实时更新** - 动态显示执行状态
- **内容复制** - 快速复制生成文案
- **标签切换** - 查看不同阶段内容

## 🔧 配置说明

### 环境变量
```bash
# LLM API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_api_base_url

# 小红书配置
XHS_USE_MOCK=true  # 使用模拟数据
```

### 模拟数据
项目支持全局Mock模式，无需真实API即可测试：
- 关键词生成模拟
- 话题搜索模拟
- 帖子检索模拟
- 内容生成模拟

## 📊 测试结果

```
✅ 关键词生成和提取功能正常
✅ 话题搜索和精炼功能正常
✅ 帖子检索和解析功能正常
✅ 内容过滤功能正常
✅ 打点分析功能正常
✅ 用户选择功能正常
✅ 内容生成功能正常
✅ 模拟数据工作正常，可以测试后续节点
```

## 🚀 部署

### 后端部署
```bash
# 生产环境部署
pip install -r requirements.txt
python main.py
```

### 前端部署
```bash
cd frontend
npm run build
# 将 build 文件夹部署到静态服务器
```

## 📝 开发说明

- 使用LangGraph构建AI工作流
- 支持异步处理和状态管理
- 模块化设计，易于扩展
- 完整的测试覆盖
- 前端后端分离架构

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## �� 许可证

MIT License
