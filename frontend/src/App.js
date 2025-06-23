import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Paper,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Avatar,
  Divider,
  Button,
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Badge,
  Tabs,
  Tab,
} from '@mui/material';
import {
  AutoAwesome,
  TrendingUp,
  Search,
  FilterList,
  Psychology,
  Person,
  Create,
  CheckCircle,
  PlayArrow,
  Refresh,
  ContentCopy,
  Favorite,
  Share,
  Comment,
} from '@mui/icons-material';

// 模拟数据
const mockData = {
  userInput: "大龄剩女",
  keywords: {
    primary: "大龄女生",
    secondary: "剩女"
  },
  refinedKeywords: ["大龄女生脱单日记", "大龄未婚女生找工作"],
  topics: [
    {
      name: "大龄女生脱单日记 #大龄女生",
      views: "1,000,032",
      trend: "上升"
    },
    {
      name: "大龄未婚女生找工作 #大龄女生", 
      views: "321,686",
      trend: "稳定"
    },
    {
      name: "大龄读研女生 #大龄女生",
      views: "54,915", 
      trend: "下降"
    }
  ],
  posts: [
    {
      title: "坐标北京，34岁了，我依旧是大龄单身剩女",
      content: "又双叒叕被安排'关心'了，七大姑八大姨轮番上阵...",
      likes: 1234,
      comments: 89,
      shares: 45,
      quality_score: 9.0
    },
    {
      title: "怎么现在小女生30岁就有年龄焦虑了？？",
      content: "最近发现身边很多30岁左右的女生都开始焦虑...",
      likes: 2156,
      comments: 156,
      shares: 78,
      quality_score: 9.0
    }
  ],
  hitpoints: [
    {
      id: "hitpoint_1",
      description: "别再劝我'差不多就嫁了吧'！我的35岁，有钱有闲有爱好，比你们困在婚姻里的潇洒多了"
    },
    {
      id: "hitpoint_2", 
      description: "过了30岁，我连生病的资格都没有了，因为没人照顾"
    },
    {
      id: "hitpoint_3",
      description: "年薪百万，藤校毕业，为何我成了婚恋市场的'老大难'？"
    },
    {
      id: "hitpoint_4",
      description: "相亲N次后我悟了：遇到'普信男'比嫁不出去更可怕"
    },
    {
      id: "hitpoint_5",
      description: "不是不想结，是真的遇不到：一个'普通'大龄女生的真实困境与自我救赎"
    }
  ],
  selectedHitpoint: {
    id: "hitpoint_1",
    description: "别再劝我'差不多就嫁了吧'！我的35岁，有钱有闲有爱好，比你们困在婚姻里的潇洒多了"
  },
  generatedContent: {
    title: "那些劝我'差不多得了'的，大概没见过我现在的样子",
    content: "又双叒叕被安排'关心'了，七大姑八大姨轮番上阵，核心思想就一个：'你都三十好几了，别太挑，找个差不多的赶紧嫁了，不然以后更难。' 我听着，心里默默翻了个白眼，但脸上还是保持着礼貌的微笑。\n\n'差不多'是个什么标准呢？为了结婚而结婚，然后一头扎进柴米油盐的琐碎，为了孩子学区房焦头烂额，为了平衡工作家庭心力交瘁？如果是这样，那我宁愿'不差不多'。\n\n我的生活，说不上大富大贵，但经济独立，想买什么喜欢的，不用看谁脸色。工作之余，报了个一直想学的陶艺班，周末捏捏泥巴，放空自己，挺解压。上个月刚跟朋友自驾去了趟西北，大漠孤烟的壮阔，是困在写字楼里想象不到的。",
    tags: ["#大龄不将就", "#我的快乐我做主", "#人间清醒发言", "#单身万岁"],
    quality_score: 8.5
  }
};

const steps = [
  '关键词生成',
  '话题搜索',
  '帖子检索', 
  '内容过滤',
  '打点分析',
  '用户选择',
  '内容生成'
];

function App() {
  const [activeStep, setActiveStep] = useState(6);
  const [tabValue, setTabValue] = useState(0);
  const [userInput, setUserInput] = useState(mockData.userInput);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleRunWorkflow = () => {
    // 模拟工作流运行
    setActiveStep(0);
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 1000);
  };

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#fafafa', minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <AppBar position="static" elevation={0} sx={{ backgroundColor: '#ffffff', borderBottom: '1px solid #f0f0f0' }}>
        <Toolbar>
          <AutoAwesome sx={{ color: '#ff2442', mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#333333', fontWeight: 600 }}>
            小红书起号智能助手
          </Typography>
          <Button 
            variant="contained" 
            startIcon={<PlayArrow />}
            onClick={handleRunWorkflow}
            sx={{ mr: 2 }}
          >
            运行工作流
          </Button>
          <Button 
            variant="outlined" 
            startIcon={<Refresh />}
          >
            重置
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Grid container spacing={3}>
          {/* 左侧工作流状态 */}
          <Grid item xs={12} md={4}>
            <Paper elevation={0} sx={{ p: 3, height: 'fit-content' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                工作流状态
              </Typography>
              
              <Stepper activeStep={activeStep} orientation="vertical">
                {steps.map((label, index) => (
                  <Step key={label}>
                    <StepLabel 
                      StepIconComponent={index <= activeStep ? CheckCircle : undefined}
                      sx={{ 
                        '& .MuiStepLabel-iconContainer': {
                          color: index <= activeStep ? '#ff2442' : '#ccc'
                        }
                      }}
                    >
                      {label}
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="text.secondary">
                        {index <= activeStep ? '已完成' : '等待中...'}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Paper>
          </Grid>

          {/* 右侧内容展示 */}
          <Grid item xs={12} md={8}>
            <Paper elevation={0} sx={{ p: 3 }}>
              <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
                <Tab label="关键词分析" />
                <Tab label="话题搜索" />
                <Tab label="帖子内容" />
                <Tab label="打点分析" />
                <Tab label="生成内容" />
              </Tabs>

              {/* 关键词分析 */}
              {tabValue === 0 && (
                <Box>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                    关键词分析
                  </Typography>
                  
                  <Card sx={{ mb: 3 }}>
                    <CardHeader 
                      title="用户输入"
                      avatar={<Person sx={{ color: '#ff2442' }} />}
                    />
                    <CardContent>
                      <Typography variant="h6" color="primary">
                        {userInput}
                      </Typography>
                    </CardContent>
                  </Card>

                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardHeader 
                          title="初始关键词"
                          avatar={<Search sx={{ color: '#ff2442' }} />}
                        />
                        <CardContent>
                          <Chip 
                            label={mockData.keywords.primary} 
                            color="primary" 
                            sx={{ mr: 1, mb: 1 }}
                          />
                          <Chip 
                            label={mockData.keywords.secondary} 
                            variant="outlined"
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardHeader 
                          title="精炼关键词"
                          avatar={<AutoAwesome sx={{ color: '#ff2442' }} />}
                        />
                        <CardContent>
                          {mockData.refinedKeywords.map((keyword, index) => (
                            <Chip 
                              key={index}
                              label={keyword} 
                              color="secondary"
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* 话题搜索 */}
              {tabValue === 1 && (
                <Box>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                    话题搜索
                  </Typography>
                  
                  <Grid container spacing={2}>
                    {mockData.topics.map((topic, index) => (
                      <Grid item xs={12} md={6} key={index}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {topic.name}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Chip 
                                label={`${topic.views} 浏览`}
                                size="small"
                                color="primary"
                              />
                              <Chip 
                                label={topic.trend}
                                size="small"
                                variant="outlined"
                                color={topic.trend === '上升' ? 'success' : 'default'}
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* 帖子内容 */}
              {tabValue === 2 && (
                <Box>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                    帖子内容
                  </Typography>
                  
                  <List>
                    {mockData.posts.map((post, index) => (
                      <ListItem key={index} sx={{ mb: 2, p: 0 }}>
                        <Card sx={{ width: '100%' }}>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {post.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                              {post.content}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Favorite sx={{ fontSize: 16, color: '#ff2442' }} />
                                <Typography variant="body2">{post.likes}</Typography>
                              </Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Comment sx={{ fontSize: 16, color: '#666' }} />
                                <Typography variant="body2">{post.comments}</Typography>
                              </Box>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Share sx={{ fontSize: 16, color: '#666' }} />
                                <Typography variant="body2">{post.shares}</Typography>
                              </Box>
                              <Chip 
                                label={`质量: ${post.quality_score}`}
                                size="small"
                                color="success"
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* 打点分析 */}
              {tabValue === 3 && (
                <Box>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                    打点分析
                  </Typography>
                  
                  <Grid container spacing={2}>
                    {mockData.hitpoints.map((hitpoint, index) => (
                      <Grid item xs={12} key={index}>
                        <Card 
                          sx={{ 
                            border: hitpoint.id === mockData.selectedHitpoint.id ? '2px solid #ff2442' : '1px solid #f0f0f0',
                            backgroundColor: hitpoint.id === mockData.selectedHitpoint.id ? '#fff5f5' : '#ffffff'
                          }}
                        >
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                              <Avatar sx={{ bgcolor: '#ff2442', width: 32, height: 32 }}>
                                {index + 1}
                              </Avatar>
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="body1" sx={{ fontWeight: 500, mb: 1 }}>
                                  打点 {index + 1}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {hitpoint.description}
                                </Typography>
                                {hitpoint.id === mockData.selectedHitpoint.id && (
                                  <Chip 
                                    label="已选择"
                                    color="primary"
                                    size="small"
                                    sx={{ mt: 1 }}
                                  />
                                )}
                              </Box>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* 生成内容 */}
              {tabValue === 4 && (
                <Box>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                    生成内容
                  </Typography>
                  
                  <Card>
                    <CardHeader 
                      title="小红书文案"
                      avatar={<Create sx={{ color: '#ff2442' }} />}
                      action={
                        <Button 
                          startIcon={<ContentCopy />}
                          variant="outlined"
                          size="small"
                        >
                          复制文案
                        </Button>
                      }
                    />
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#333' }}>
                        {mockData.generatedContent.title}
                      </Typography>
                      
                      <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.8, whiteSpace: 'pre-line' }}>
                        {mockData.generatedContent.content}
                      </Typography>
                      
                      <Box sx={{ mb: 2 }}>
                        {mockData.generatedContent.tags.map((tag, index) => (
                          <Chip 
                            key={index}
                            label={tag}
                            variant="outlined"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Chip 
                          label={`质量评分: ${mockData.generatedContent.quality_score}`}
                          color="success"
                        />
                        <Typography variant="body2" color="text.secondary">
                          基于打点: {mockData.selectedHitpoint.description.substring(0, 30)}...
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default App; 