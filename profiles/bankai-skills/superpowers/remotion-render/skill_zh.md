> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Remotion 渲染

通过 [inference.sh](https://inference.sh) CLI 从 React/Remotion 组件代码渲染视频。

![Remotion 渲染](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kg2c0egyg243mnyth4y6g51q.jpeg)

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 渲染一个简单的动画
belt app run infsh/remotion-render --input '{
  "code": "import { useCurrentFrame, AbsoluteFill } from \"remotion\"; export default function Main() { const frame = useCurrentFrame(); return <AbsoluteFill style={{backgroundColor: \"#000\", display: \"flex\", justifyContent: \"center\", alignItems: \"center\"}}><h1 style={{color: \"white\", fontSize: 100, opacity: frame / 30}}>Hello World</h1></AbsoluteFill>; }",
  "duration_seconds": 3,
  "fps": 30,
  "width": 1920,
  "height": 1080
}'
```

## 输入模式

| 参数 | 类型 | 必填 | 描述 |
|-----------|------|----------|-------------|
| `code` | string | 是 | React 组件 TSX 代码。必须导出默认组件。 |
| `composition_id` | string | 否 | 渲染的合成 ID |
| `props` | object | 否 | 传递给组件的属性 |
| `width` | number | 否 | 视频宽度（像素） |
| `height` | number | 否 | 视频高度（像素） |
| `fps` | number | 否 | 每秒帧数 |
| `duration_seconds` | number | 否 | 视频时长（秒） |
| `codec` | string | 否 | 输出编解码器 |

## 可用导入

您的 TSX 代码可以导入 `remotion` 和 `react`：

```tsx
// Remotion API
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  AbsoluteFill,
  Sequence,
  Audio,
  Video,
  Img
} from "remotion";

// React
import React, { useState, useEffect } from "react";
```

## 示例

### 淡入文字

```bash
belt app run infsh/remotion-render --input '{
  "code": "import { useCurrentFrame, AbsoluteFill, interpolate } from \"remotion\"; export default function Main() { const frame = useCurrentFrame(); const opacity = interpolate(frame, [0, 30], [0, 1]); return <AbsoluteFill style={{backgroundColor: \"#1a1a2e\", display: \"flex\", justifyContent: \"center\", alignItems: \"center\"}}><h1 style={{color: \"#eee\", fontSize: 80, opacity}}>Welcome</h1></AbsoluteFill>; }",
  "duration_seconds": 2,
  "fps": 30,
  "width": 1920,
  "height": 1080
}'
```

### 动画计数器

```bash
belt app run infsh/remotion-render --input '{
  "code": "import { useCurrentFrame, useVideoConfig, AbsoluteFill } from \"remotion\"; export default function Main() { const frame = useCurrentFrame(); const { fps, durationInFrames } = useVideoConfig(); const progress = Math.floor((frame / durationInFrames) * 100); return <AbsoluteFill style={{backgroundColor: \"#000\", display: \"flex\", justifyContent: \"center\", alignItems: \"center\", flexDirection: \"column\"}}><h1 style={{color: \"#fff\", fontSize: 200}}>{progress}%</h1><p style={{color: \"#666\", fontSize: 30}}>Loading...</p></AbsoluteFill>; }",
  "duration_seconds": 5,
  "fps": 60,
  "width": 1080,
  "height": 1080
}'
```

### 弹簧动画

```bash
belt app run infsh/remotion-render --input '{
  "code": "import { useCurrentFrame, useVideoConfig, spring, AbsoluteFill } from \"remotion\"; export default function Main() { const frame = useCurrentFrame(); const { fps } = useVideoConfig(); const scale = spring({ frame, fps, config: { damping: 10, stiffness: 100 } }); return <AbsoluteFill style={{backgroundColor: \"#6366f1\", display: \"flex\", justifyContent: \"center\", alignItems: \"center\"}}><div style={{width: 200, height: 200, backgroundColor: \"white\", borderRadius: 20, transform: `scale(${scale})`}} /></AbsoluteFill>; }",
  "duration_seconds": 2,
  "fps": 60,
  "width": 1080,
  "height": 1080
}'
```

### 带属性

```bash
belt app run infsh/remotion-render --input '{
  "code": "import { AbsoluteFill } from \"remotion\"; export default function Main({ title, subtitle }) { return <AbsoluteFill style={{backgroundColor: \"#000\", display: \"flex\", justifyContent: \"center\", alignItems: \"center\", flexDirection: \"column\"}}><h1 style={{color: \"#fff\", fontSize: 80}}>{title}</h1><p style={{color: \"#888\", fontSize: 40}}>{subtitle}</p></AbsoluteFill>; }",
  "props": {"title": "My Video", "subtitle": "Created with Remotion"},
  "duration_seconds": 3,
  "fps": 30,
  "width": 1920,
  "height": 1080
}'
```

### 序列动画

```bash
belt app run infsh/remotion-render --input '{
  "code": "import { useCurrentFrame, AbsoluteFill, Sequence, interpolate } from \"remotion\"; function FadeIn({ children }) { const frame = useCurrentFrame(); const opacity = interpolate(frame, [0, 20], [0, 1]); return <div style={{ opacity }}>{children}</div>; } export default function Main() { return <AbsoluteFill style={{backgroundColor: \"#000\", display: \"flex\", justifyContent: \"center\", alignItems: \"center\", flexDirection: \"column\", gap: 20}}><Sequence from={0}><FadeIn><h1 style={{color: \"#fff\", fontSize: 60}}>First</h1></FadeIn></Sequence><Sequence from={30}><FadeIn><h1 style={{color: \"#fff\", fontSize: 60}}>Second</h1></FadeIn></Sequence><Sequence from={60}><FadeIn><h1 style={{color: \"#fff\", fontSize: 60}}>Third</h1></FadeIn></Sequence></AbsoluteFill>; }",
  "duration_seconds": 4,
  "fps": 30,
  "width": 1920,
  "height": 1080
}'
```

## Python SDK

```python
from inferencesh import inference

client = inference()

result = client.run({
    "app": "infsh/remotion-render",
    "input": {
        "code": """
import { useCurrentFrame, AbsoluteFill, interpolate } from "remotion";

export default function Main() {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1]);

  return (
    <AbsoluteFill style={{
      backgroundColor: "#1a1a2e",
      display: "flex",
      justifyContent: "center",
      alignItems: "center"
    }}>
      <h1 style={{ color: "#eee", fontSize: 80, opacity }}>
        Hello from Python
      </h1>
    </AbsoluteFill>
  );
}
""",
        "duration_seconds": 3,
        "fps": 30,
        "width": 1920,
        "height": 1080
    }
})

print(result["output"]["video"])
```

### 流式传输进度

```python
for update in client.run({
    "app": "infsh/remotion-render",
    "input": {
        "code": "...",
        "duration_seconds": 10
    }
}, stream=True):
    if update.get("progress"):
        print(f"Rendering: {update['progress']}%")
    if update.get("output"):
        print(f"Video: {update['output']['video']}")
```

## 相关技能

```bash
# Remotion 最佳实践（组件模式）
npx skills add remotion-dev/skills@remotion-best-practices

# AI 视频生成（用于 AI 生成的片段）
npx skills add inference-sh/skills@ai-video-generation

# 图像生成（用于视频资源）
npx skills add inference-sh/skills@ai-image-generation

# Python SDK 参考
npx skills add inference-sh/skills@python-sdk

# 完整平台技能
npx skills add inference-sh/skills@infsh-cli
```

## 文档

- [Remotion 文档](https://www.remotion.dev/docs) - 官方 Remotion 文档
- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [流式传输结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
