> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Twitter/X 自动化

通过 [inference.sh](https://inference.sh) CLI 自动化 Twitter/X。

![Twitter/X 自动化](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgad3pxsh3z3hnfpjyjpx4x4.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 发布推文
belt app run x/post-tweet --input '{"text": "Hello from inference.sh!"}'
```


## 可用应用

| 应用 | 应用 ID | 说明 |
|-----|--------|------|
| 发布推文 | `x/post-tweet` | 发布纯文本推文 |
| 发布带媒体内容 | `x/post-create` | 发布包含媒体内容的内容 |
| 点赞推文 | `x/post-like` | 点赞推文 |
| 转发 | `x/post-retweet` | 转发推文 |
| 删除推文 | `x/post-delete` | 删除推文 |
| 获取推文 | `x/post-get` | 根据 ID 获取推文 |
| 发送私信 | `x/dm-send` | 发送直接消息 |
| 关注用户 | `x/user-follow` | 关注用户 |
| 获取用户 | `x/user-get` | 获取用户资料 |

## 示例

### 发布推文

```bash
belt app run x/post-tweet --input '{"text": "刚发布了新功能！🚀"}'
```

### 发布带媒体内容

```bash
belt app sample x/post-create --save input.json

# 编辑 input.json：
# {
#   "text": "看看这个 AI 生成的图片！",
#   "media_url": "https://your-image-url.jpg"
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
  "recipient_id": "user_id_here",
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

## 工作流：生成 AI 图片并发布

```bash
# 1. 生成图片
belt app run falai/flux-dev-lora --input '{"prompt": "mountain sunset"}' > image.json

# 2. 使用图片 URL 发布到 Twitter
belt app run x/post-create --input '{
  "text": "AI 生成的日落艺术图 🌅",
  "media_url": "<第一步中的图片 URL>"
}'
```

## 工作流：生成并发布视频

```bash
# 1. 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "海边的波涛"}' > video.json

# 2. 发布到 Twitter
belt app run x/post-create --input '{
  "text": "AI 生成的视频 🎬",
  "media_url": "<第一步中的视频 URL>"
}'
```

## 相关技能

```bash
# 完整平台技能（包含所有应用）
npx skills add inference-sh/skills@infsh-cli

# 图片生成（生成图片发布）
npx skills add inference-sh/skills@ai-image-generation

# 视频生成（生成视频发布）
npx skills add inference-sh/skills@ai-video-generation

# AI 头像（生成演示视频）
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [X.com 集成](https://inference.sh/docs/integrations/x) - 设置 Twitter/X 集成
- [X.com 集成示例](https://inference.sh/docs/examples/x-integration) - 完整的 Twitter 工作流程
- [应用概览](https://inference.sh/docs/apps/overview) - 了解应用生态
