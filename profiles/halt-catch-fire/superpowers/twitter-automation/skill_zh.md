> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Twitter/X 自动化

通过 [inference.sh](https://inference.sh) CLI 自动化 Twitter/X。

![Twitter/X 自动化](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgad3pxsh3z3hnfpjyjpx4x4.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 发布推文
belt app run x/post-tweet --input '{"text": "来自 inference.sh 的问候！"}'
```

## 可用应用

| 应用 | 应用 ID | 描述 |
|-----|--------|-------------|
| 发布推文 | `x/post-tweet` | 发布文本推文 |
| 创建发布 | `x/post-create` | 带有媒体发布 |
| 点赞推文 | `x/post-like` | 点赞推文 |
| 转发 | `x/post-retweet` | 转发帖子 |
| 删除推文 | `x/post-delete` | 删除推文 |
| 获取推文 | `x/post-get` | 通过 ID 获取推文 |
| 发送私信 | `x/dm-send` | 发送私信 |
| 关注用户 | `x/user-follow` | 关注用户 |
| 获取用户 | `x/user-get` | 获取用户资料 |

## 示例

### 发布推文

```bash
belt app run x/post-tweet --input '{"text": "刚刚发布了一个新功能！ 🚀"}'
```

### 带有媒体发布

```bash
belt app sample x/post-create --save input.json

# 编辑 input.json：
# {
#   "text": "看看这个 AI 生成的图像！",
#   "media_url": "https://你的图像 URL.jpg"
# }

belt app run x/post-create --input input.json
```

### 点赞推文

```bash
belt app run x/post-like --input '{"tweet_id": "1234567890"}'
```

### 转发

```bash
belt app run x/post-retweet --input '{"tweet_id": "1234567890"}'
```

### 发送私信

```bash
belt app run x/dm-send --input '{
  "recipient_id": "用户 ID 这里",
  "text": "嘿！感谢你的关注。"
}'
```

### 关注用户

```bash
belt app run x/user-follow --input '{"username": "elonmusk"}'
```

### 获取用户资料

```bash
belt app run x/user-get --input '{"username": "OpenAI"}'
```

### 获取推文详情

```bash
belt app run x/post-get --input '{"tweet_id": "1234567890"}'
```

### 删除推文

```bash
belt app run x/post-delete --input '{"tweet_id": "1234567890"}'
```

## 工作流：生成 AI 图像并发布

```bash
# 1. 生成图像
belt app run falai/flux-dev-lora --input '{"prompt": "山脉上的日落"}' > image.json

# 2. 带有图像 URL 发布到 Twitter
belt app run x/post-create --input '{
  "text": "AI 生成的日落艺术 🌅",
  "media_url": "<步骤 1 中的图像 URL>"
}'
```

## 工作流：生成并发布视频

```bash
# 1. 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "海滩上的波浪"}' > video.json

# 2. 发布到 Twitter
belt app run x/post-create --input '{
  "text": "AI 生成的视频 🎬",
  "media_url": "<步骤 1 中的视频 URL>"
}'
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 图像生成（创建用于发布的图像）
npx skills add inference-sh/skills@ai-image-generation

# 视频生成（创建用于发布的视频）
npx skills add inference-sh/skills@ai-video-generation

# AI 头像（创建主讲人视频）
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [X.com 集成](https://inference.sh/docs/integrations/x) - 设置 Twitter/X 集成
- [X.com 集成示例](https://inference.sh/docs/examples/x-integration) - 完整的 Twitter 工作流
- [应用概览](https://inference.sh/docs/apps/overview) - 了解应用生态系统
