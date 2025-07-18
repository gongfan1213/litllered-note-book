# 前端界面截图说明

## 🎨 界面预览

### 主界面布局
```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 小红书起号智能助手                    [运行工作流] [重置] │
├─────────────────┬───────────────────────────────────────────┤
│                 │                                           │
│   工作流状态     │             内容展示区域                  │
│                 │                                           │
│ ○ 关键词生成     │  [关键词分析] [话题搜索] [帖子内容]       │
│ ○ 话题搜索       │  [打点分析] [生成内容]                   │
│ ○ 帖子检索       │                                           │
│ ○ 内容过滤       │  ┌─────────────────────────────────────┐ │
│ ○ 打点分析       │  │                                     │ │
│ ○ 用户选择       │  │        当前标签页内容                │ │
│ ● 内容生成       │  │                                     │ │
│                 │  └─────────────────────────────────────┘ │
└─────────────────┴───────────────────────────────────────────┘
```

## 📱 功能展示

### 1. 关键词分析标签页
- **用户输入卡片** - 显示用户输入的原始内容
- **初始关键词卡片** - 展示AI生成的初始关键词
- **精炼关键词卡片** - 显示优化后的关键词

### 2. 话题搜索标签页
- **话题卡片网格** - 展示搜索到的话题
- **热度数据** - 显示浏览量、趋势等信息
- **趋势标识** - 用不同颜色标识上升/下降/稳定

### 3. 帖子内容标签页
- **帖子列表** - 显示检索到的帖子
- **互动数据** - 点赞、评论、分享数量
- **质量评分** - 显示AI评估的质量分数

### 4. 打点分析标签页
- **打点卡片** - 展示AI生成的5个打点
- **选择状态** - 突出显示已选择的打点
- **编号标识** - 每个打点有唯一编号

### 5. 生成内容标签页
- **文案标题** - 生成的标题
- **文案正文** - 完整的小红书文案
- **标签展示** - 相关的标签
- **质量评分** - 内容质量评估
- **复制按钮** - 快速复制文案

## 🎯 交互功能

### 工作流控制
- **运行工作流按钮** - 模拟完整工作流执行
- **重置按钮** - 清空当前状态
- **实时状态更新** - 步骤条动态显示进度

### 内容操作
- **标签页切换** - 查看不同阶段内容
- **复制文案** - 一键复制生成内容
- **响应式布局** - 适配不同屏幕尺寸

## 🎨 设计特色

### 色彩方案
- **主色调** - 小红书红 (#ff2442)
- **背景色** - 浅灰 (#fafafa)
- **卡片色** - 纯白 (#ffffff)
- **文字色** - 深灰 (#333333)

### 视觉元素
- **圆角设计** - 12px圆角营造现代感
- **阴影效果** - 轻微阴影增加层次感
- **图标使用** - Material Icons图标库
- **间距规范** - 8px网格系统

### 响应式设计
- **桌面端** - 左右分栏布局
- **平板端** - 自适应布局
- **移动端** - 上下堆叠布局

## 🚀 启动方式

### 方式一：使用演示脚本
```bash
python demo_frontend.py
```

### 方式二：手动启动
```bash
cd frontend
npm install
npm start
```

### 方式三：使用启动脚本
```bash
# Windows
frontend/start.bat

# Linux/Mac
chmod +x frontend/start.sh
./frontend/start.sh
```

## 📊 数据展示

界面使用模拟数据展示完整的工作流程：

1. **用户输入**: "大龄剩女"
2. **关键词生成**: "大龄女生"、"剩女"
3. **话题搜索**: 热门话题及热度数据
4. **帖子检索**: 相关帖子及互动数据
5. **内容过滤**: 质量评分和筛选结果
6. **打点分析**: 5个AI生成的爆点
7. **内容生成**: 完整的小红书文案

## 🔧 技术实现

- **React 18** - 现代化前端框架
- **Material UI 5** - 企业级UI组件库
- **Emotion** - CSS-in-JS样式解决方案
- **响应式设计** - 适配各种设备
- **主题系统** - 统一的设计语言 