# Content Creator Platform

自动化内容创作平台，帮助内容博主从信息爬取、话题筛选、内容研究、视频生成到发布准备的全流程自动化。

## 技术栈

- **Backend**: Python 3.10+ / FastAPI / SQLAlchemy / SQLite
- **Frontend**: TypeScript / Next.js / Tailwind CSS
- **AI**: 通义千问 (DashScope SDK)
- **通知**: 钉钉机器人 Webhook
- **视频生成**: moviepy + Pillow
- **爬虫**: httpx + BeautifulSoup
- **调度**: APScheduler

## 项目结构

```
qorder-one/
├── backend/                  # Python 后端
│   ├── app/
│   │   ├── main.py           # FastAPI 入口
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # 请求/响应 Schema
│   │   ├── crawlers/         # 爬虫模块 (微博/知乎/百度/arXiv)
│   │   ├── ai/               # AI 模块 (通义千问)
│   │   ├── video/            # 视频生成模块
│   │   ├── notification/     # 钉钉通知模块
│   │   ├── scheduler/        # 定时任务
│   │   ├── pipeline/         # 流水线编排
│   │   └── api/              # API 路由
│   ├── assets/               # 静态资源 (字体/音乐/模板)
│   ├── output/               # 生成的视频/脚本/封面
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Next.js 前端
│   └── src/
│       ├── app/              # 页面 (Dashboard/Topics/Pipeline/Videos/Analytics)
│       ├── lib/api.ts        # 后端 API 客户端
│       └── types/index.ts    # TypeScript 类型定义
└── config/                   # 配置文件
    ├── topic_categories.yaml # 话题分类配置
    ├── prompts.yaml          # AI 提示词模板
    └── schedule.yaml         # 定时任务配置
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- pip

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `backend/.env`，填入以下必要配置：

```env
# 通义千问 API Key (必填，用于 AI 内容生成)
DASHSCOPE_API_KEY=your_api_key_here

# 钉钉机器人 (必填，用于每日话题推送)
DINGDING_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
DINGDING_SECRET=your_secret_here

# 图片 API (可选，用于视频配图)
UNSPLASH_ACCESS_KEY=your_key_here
PEXELS_API_KEY=your_key_here
```

### 4. 启动后端

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动后会自动：
- 创建 SQLite 数据库和所有表
- 启动定时调度器（每天 6:00 爬取，7:00 推送话题）

### 5. 安装并启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:3000`，会自动代理 API 请求到后端 `http://localhost:8000`。

## 使用流程

### 自动模式（推荐）

1. **每天 6:00** — 系统自动爬取微博热搜、知乎热榜、百度热搜、arXiv 论文
2. **每天 7:00** — AI 筛选 5-8 个候选话题，通过钉钉机器人推送给你
3. **你在钉钉回复** — 回复话题编号确认，如 `1,3,5` 或 `全部`
4. **系统自动生成** — 对确认的话题进行深度研究、生成脚本、制作视频
5. **手动上传** — 从 `output/` 目录获取视频和文案，上传到抖音/小红书

### 手动模式

通过前端 Dashboard 或 API 手动操作：

```bash
# 手动触发爬取
curl -X POST http://localhost:8000/api/crawl/run

# 运行完整流水线（爬取 + 话题筛选）
curl -X POST http://localhost:8000/api/pipeline/run

# 手动推送话题到钉钉
curl -X POST http://localhost:8000/api/notifications/send-topics

# 创建自定义话题
curl -X POST http://localhost:8000/api/topics \
  -H "Content-Type: application/json" \
  -d '{"title":"话题标题","description":"描述","category":"科技前沿","priority":8}'

# 确认话题
curl -X PATCH http://localhost:8000/api/topics/{topic_id}/confirm

# 生成内容（研究 + 大纲 + 脚本）
curl -X POST http://localhost:8000/api/content/generate/{topic_id}

# 生成视频
curl -X POST http://localhost:8000/api/videos/generate/{script_id}

# 准备发布（生成各平台文案和标签）
curl -X POST http://localhost:8000/api/publishing/prepare/{video_id}
```

## 前端页面

| 页面 | 路径 | 功能 |
|------|------|------|
| Dashboard | `/` | 今日概览、流水线状态、快捷操作 |
| Topics | `/topics` | 话题列表，确认/拒绝/生成内容 |
| Pipeline | `/pipeline` | 流水线控制，手动触发爬取和推送 |
| Videos | `/videos` | 视频列表，预览和下载 |
| Analytics | `/analytics` | 数据统计，手动录入各平台表现数据 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/crawl/run` | 触发爬取 |
| GET | `/api/crawl/sources` | 查看可用数据源 |
| GET | `/api/topics` | 话题列表 |
| GET | `/api/topics/candidates` | 今日候选话题 |
| POST | `/api/topics` | 创建话题 |
| PATCH | `/api/topics/{id}/confirm` | 确认话题 |
| PATCH | `/api/topics/{id}/reject` | 拒绝话题 |
| POST | `/api/topics/confirm-batch` | 批量确认 |
| POST | `/api/content/generate/{topic_id}` | 生成内容 |
| POST | `/api/videos/generate/{script_id}` | 生成视频 |
| GET | `/api/videos` | 视频列表 |
| GET | `/api/videos/{id}/download` | 下载视频 |
| POST | `/api/publishing/prepare/{video_id}` | 准备发布 |
| GET | `/api/pipeline/status` | 流水线状态 |
| POST | `/api/pipeline/run` | 运行完整流水线 |
| POST | `/api/analytics/record` | 录入分析数据 |
| GET | `/api/analytics/summary` | 分析数据汇总 |
| POST | `/api/notifications/send-topics` | 推送话题到钉钉 |

## 话题分类配置

编辑 `config/topic_categories.yaml` 调整关注的领域：

```yaml
categories:
  - name: tech_trends
    display_name: "科技前沿"
    keywords: ["AI", "人工智能", "大模型", "芯片"]
    sources: [weibo, zhihu, baidu, arxiv]
    priority_weight: 1.2
    enabled: true
```

目前支持的分类：
- **科技前沿** — AI、芯片、量子计算、新能源等
- **历史人文** — 历史、朝代、文明、考古等
- **经济投资** — 经济、投资、理财、股票等
- **汽车评测** — 新能源车、评测、对比等

## 输出目录结构

每次生成的内容存放在 `backend/output/` 下：

```
output/
└── 2026-03-18/
    └── AI大模型最新突破/
        ├── video.mp4          # 生成的短视频 (1080x1920, 9:16竖版)
        ├── cover.png          # 封面图
        ├── douyin/
        │   ├── metadata.json  # 发布标题、描述、标签
        │   └── script.txt     # 讲解文稿
        └── xiaohongshu/
            ├── metadata.json
            └── script.txt
```

## 钉钉机器人配置

1. 在钉钉群中添加自定义机器人，选择"加签"安全设置
2. 复制 Webhook URL 和签名密钥到 `.env`
3. 如需接收用户回复确认话题，需配置机器人的回调地址为 `http://你的服务器:8000/api/notifications/callback`

## 数据分析与优化

在 Analytics 页面手动录入每条视频在抖音/小红书的表现数据（播放量、点赞、评论、转发），系统会：
- 计算互动率
- 汇总各项指标
- 后续可基于数据反馈优化话题选择和内容风格

**抖音最佳发布时间**: 12:00-13:00, 18:00-20:00, 21:00-23:00

**小红书最佳发布时间**: 7:00-9:00, 12:00-14:00, 18:00-22:00
