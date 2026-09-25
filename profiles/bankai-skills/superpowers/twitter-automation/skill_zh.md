> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Twitter/X 自动化

通过 [inference.sh](https://inference.sh) CLI 自动化 Twitter/X。

![Twitter/X 自动化](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgad3pxsh3z3hnfpjyjpx4x4.jpeg)

## 快速开始

> 需要 inference.sh CLI（`belt`）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# Post a tweet
belt app run x/post-tweet --input '{"text": "Hello from inference.sh!"}'
```

## 可用应用

| 应用 | 应用 ID | 说明 |
|-----|--------|------|
| 发布推文 | `x/post-tweet` | 发布纯文本推文 |
| 发布带媒体内容的推文 | `x/post-create` | 发布带媒体内容的推文 |
| 点赞推文 | `x/post-like` | 点赞一条推文 |
| 转推 | `x/post-retweet` | 转推一条帖子 |
| 删除推文 | `x/post-delete` | 删除一条推文 |
| 获取推文 | `x/post-get` | 按 ID 获取推文 |
| 发送私信 | `x/dm-send` | 发送私信 |
| 关注用户 | `x/user-follow` | 关注一名用户 |
| 获取用户信息 | `x/user-get` | 获取用户主页信息 |

## 示例

### 发布推文

```bash
belt app run x/post-tweet --input '{"text": "Just shipped a new feature! 🚀"}'
```

### 发布带媒体内容的推文

```bash
belt app sample x/post-create --save input.json

# 编辑 input.json：
# {
#   "text": "Check out this AI-generated image!",
#   "media_url": "https://your-image-url.jpg"
# }

belt app run x/post-create --input input.json
```

### 点赞推文

```bash
belt app run x/post-like --input '{"tweet_id": "1234567890"}'
```

### 转推

```bash
belt app run x/post-retweet --input '{"tweet_id": "1234567890"}'
```

### 发送私信

```bash
belt app run x/dm-send --input '{
  "recipient_id": "user_id_here",
  "text": "Hey! Thanks for the follow."
}'
```

### 关注用户

```bash
belt app run x/user-follow --input '{"username": "elonmusk"}'
```

### 获取用户主页信息

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
belt app run falai/flux-dev-lora --input '{"prompt": "sunset over mountains"}' > image.json

# 2. 使用图像 URL 发布到 Twitter
belt app run x/post-create --input '{
  "text": "AI-generated art of a sunset 🌅",
  "media_url": "<image-url-from-step-1>"
}'
```

## 工作流：生成并发布视频

```bash
# 1. 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "waves on a beach"}' > video.json

# 2. 发布到 Twitter
belt app run x/post-create --input '{
  "text": "AI-generated video 🎬",
  "media_url": "<video-url-from-step-1>"
}'
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 图像生成（生成图像用于发布）
npx skills add inference-sh/skills@ai-image-generation

# 视频生成（生成视频用于发布）
npx skills add inference-sh/skills@ai-video-generation

# AI 头像（生成演示视频）
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [X.com 集成](https://inference.sh/docs/integrations/x) - 设置 Twitter/X 集成
- [X.com 集成示例](https://inference.sh/docs/examples/x-integration) - 完整的 Twitter 工作流
- [应用总览](https://inference.sh/docs/apps/overview) - 理解应用生态系统
