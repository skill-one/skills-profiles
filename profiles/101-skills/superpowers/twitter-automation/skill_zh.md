> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Twitter/X 自动化

通过 [inference.sh](https://inference.sh) CLI 自动化 Twitter/X。

![Twitter/X 自动化](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgad3pxsh3z3hnfpjyjpx4x4.jpeg)

## 快速开始

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 发布推文
belt app run x/post-tweet --input '{" text": "Hello from inference.sh!"}'
```

## 可用应用

| 应用 | 应用 ID | 描述 |
|-----|--------|-------------|
| 发布推文 | `x/post-tweet` | 发布文字推文 |
| 创建帖子 | `x/post-create` | 包含媒体发布帖子 |
| 点赞帖子 | `x/post-like` | 点赞推文 |
| 转发 | `x/post-retweet` | 转发帖子 |
| 删除帖子 | `x/post-delete` | 删除推文 |
| 获取帖子 | `x/post-get` | 通过 ID 获取推文 |
| 发送私信 | `x/dm-sell` | 发送私信 |
| 关注用户 | `x/user-follow` | 关注用户 |
| 获取用户 | `x/user-get` | 获取用户资料 |

## 示例

### 发布推文

```bash
belt app run x/post-tweet --input '{" text": "刚刚发布了一个新功能！🚀"}'
```

### 包含媒体发布

```bash
belt app sample x/post-create --save input.json

# 编辑 input.json:
# {
#   " text": "来看看这张 AI 生成的图片！",
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
belt app run x/dm-sell --input '{
  "recipient_id": "user_id_here",
  " text": "Hey! 感谢你的关注。"
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
belt app run falai/flux-dev-lora --input '{"prompt": "sunset over mountains"}' > image.json

# 2. 使用图片 URL 发布到 Twitter
belt app run x/post-create --input '{
  " text": "AI 生成的日落艺术 🌅",
  "media_url": "<image-url-from-step-1>"
}'
```

## 工作流：生成并发布视频

```bash
# 1. 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "waves on a beach"}' > video.json

# 2. 发布到 Twitter
belt app run x/post-create --input '{
  " text": "AI 生成的视频 🎬",
  "media_url": "<video-url-from-step-1>"
}'
```

## 相关技能

```bash
# 全平台技能（包含所有应用）
npx skills add inference-sh/skills@infsh-cli

# 图像生成（用于发布图片）
npx skills add inference-sh/skills@ai-image-generation

# 视频生成（用于发布视频）
npx skills add inference-sh/skills@ai-video-generation

# AI 头像（用于创建演示视频）
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有应用：`belt app list`

## 文档

- [X.com 集成](https://inference.sh/docs/integrations/x) - 设置 Twitter/X 集成
- [X.com 集成示例](https://inference.sh/docs/examples/x-integration) - 完整的 Twitter 工作流
- [应用概览](https://inference.sh/docs/apps/overview) - 了解应用生态
