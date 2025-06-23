# Coze插件设置指南

## 插件功能需求

你的项目需要以下功能：
1. **话题搜索**：根据关键词搜索小红书热门话题
2. **帖子检索**：根据话题检索相关帖子
3. **内容分析**：分析帖子内容，提取关键信息

## 创建步骤

### 1. 登录Coze平台
- 访问：https://www.coze.cn/
- 登录你的账号

### 2. 创建新Bot
1. 点击"创建Bot"
2. 选择"工作流Bot"类型
3. 设置名称：小红书数据助手

### 3. 配置工作流节点

#### 节点1：话题搜索
- **输入参数**：keyword (string)
- **功能**：根据关键词搜索热门话题
- **输出**：topics (array)

#### 节点2：帖子检索  
- **输入参数**：topic (string), limit (number)
- **功能**：检索相关帖子
- **输出**：posts (array)

#### 节点3：内容分析
- **输入参数**：posts (array)
- **功能**：分析帖子内容
- **输出**：analysis (object)

### 4. 获取配置信息

创建完成后，获取：
- **Workflow ID**：在插件详情页查看
- **API Key**：在API管理页面生成

### 5. 更新项目配置

```bash
# 编辑 .env 文件
COZE_API_KEY=你的新API Key
COZE_WORKFLOW_ID=你的新Workflow ID
```

## 测试配置

运行测试脚本验证配置：
```bash
python test_api_connection.py
```

## 注意事项

1. 确保插件有足够的权限
2. API Key要妥善保管
3. 定期检查API调用额度
4. 测试所有功能节点是否正常工作 