# Transloadit 媒体处理

使用 Transloadit 的云基础设施对媒体文件进行处理、转换和编码。
支持视频、音频、图像和文档，拥有 86+ 种专业处理机器人。

## 使用此技能的场景

当您需要执行以下操作时，请使用此技能：

- 将视频编码为 HLS、MP4、WebM 或其他格式
- 从视频中生成缩略图或动画 GIF
- 调整图像大小、裁剪、添加水印或优化图像
- 在图像格式之间转换（JPEG、PNG、WebP、AVIF、HEIF）
- 提取或转换音频（MP3、AAC、FLAC、WAV）
- 连接视频或音频片段
- 在视频上添加字幕或叠加文本
- 对文档进行 OCR（PDF、扫描图像）
- 运行语音转文本或文本转语音
- 应用基于 AI 的内容审核或对象检测
- 构建多步骤媒体管道，将操作串联起来

## 设置

### 选项 A：MCP 服务器（推荐用于 Copilot）

将 Transloadit MCP 服务器添加到您的 IDE 配置中。这使代理能够直接访问 Transloadit 工具（`create_template`、`create_assembly`、`list_assembly_notifications` 等）。

**VS Code / GitHub Copilot**（`.vscode/mcp.json` 或用户设置）：

```json
{
  "servers": {
    "transloadit": {
      "command": "npx",
      "args": ["-y", "@transloadit/mcp-server", "stdio"],
      "env": {
        "TRANSLOADIT_KEY": "YOUR_AUTH_KEY",
        "TRANSLOADIT_SECRET": "YOUR_AUTH_SECRET"
      }
    }
  }
}
```

在 https://transloadit.com/c/-/api-credentials 获取您的 API 凭证

### 选项 B：CLI

如果您更喜欢直接运行命令：

```bash
npx -y @transloadit/node assemblies create \
  --steps '{"encoded": {"robot": "/video/encode", "use": ":original", "preset": "hls-1080p"}}' \
  --wait \
  --input ./my-video.mp4
```

## 核心工作流

### 将视频编码为 HLS（自适应流）

```json
{
  "steps": {
    "encoded": {
      "robot": "/video/encode",
      "use": ":original",
      "preset": "hls-1080p"
    }
  }
}
```

### 从视频中生成缩略图

```json
{
  "steps": {
    "thumbnails": {
      "robot": "/video/thumbs",
      "use": ":original",
      "count": 8,
      "width": 320,
      "height": 240
    }
  }
}
```

### 调整图像大小并添加水印

```json
{
  "steps": {
    "resized": {
      "robot": "/image/resize",
      "use": ":original",
      "width": 1200,
      "height": 800,
      "resize_strategy": "fit"
    },
    "watermarked": {
      "robot": "/image/resize",
      "use": "resized",
      "watermark_url": "https://example.com/logo.png",
      "watermark_position": "bottom-right",
      "watermark_size": "15%"
    }
  }
}
```

### 对文档进行 OCR

```json
{
  "steps": {
    "recognized": {
      "robot": "/document/ocr",
      "use": ":original",
      "provider": "aws",
      "format": "text"
    }
  }
}
```

### 连接音频片段

```json
{
  "steps": {
    "imported": {
      "robot": "/http/import",
      "url": ["https://example.com/clip1.mp3", "https://example.com/clip2.mp3"]
    },
    "concatenated": {
      "robot": "/audio/concat",
      "use": "imported",
      "preset": "mp3"
    }
  }
}
```

## 多步骤管道

使用 `"use"` 字段可以串联步骤。每个步骤引用前一个步骤的输出：

```json
{
  "steps": {
    "resized": {
      "robot": "/image/resize",
      "use": ":original",
      "width": 1920
    },
    "optimized": {
      "robot": "/image/optimize",
      "use": "resized"
    },
    "exported": {
      "robot": "/s3/store",
      "use": "optimized",
      "bucket": "my-bucket",
      "path": "processed/${file.name}"
    }
  }
}
```

## 关键概念

- **Assembly**：单个处理任务。通过 `create_assembly`（MCP）或 `assemblies create`（CLI）创建。
- **Template**：存储在 Transloadit 上的可重用步骤集。通过 `create_template`（MCP）或 `templates create`（CLI）创建。
- **Robot**：处理单元（例如 `/video/encode`、`/image/resize`）。完整列表请参见 https://transloadit.com/docs/transcoding/
- **Steps**：定义管道的 JSON 对象。每个键是步骤名称，每个值配置一个机器人。
- **`:original`**：引用上传的输入文件。

## 小贴士

- 使用 CLI 时的 `--wait` 选项可阻塞直到处理完成。
- 使用 `preset` 值（例如 `"hls-1080p"`、`"mp3"`、`"webp"`）针对常见格式目标，而不是指定每个参数。
- 通过 `"use": "step_name"` 串联，构建多步骤管道而无需中间下载。
- 对于批量处理，使用 `/http/import` 从 URL、S3、GCS、Azure、FTP 或 Dropbox 拉取文件。
- 模板可以包含 `${variables}`，用于在创建 assembly 时传递动态值。
