# @json-render/remotion

一个将 JSON 时间轴规范转换为视频组合的 Remotion 渲染器。

## 快速入门

```typescript
import { Player } from "@remotion/player";
import { Renderer, type TimelineSpec } from "@json-render/remotion";

function VideoPlayer({ spec }: { spec: TimelineSpec }) {
  return (
    <Player
      component={Renderer}
      inputProps={{ spec }}
      durationInFrames={spec.composition.durationInFrames}
      fps={spec.composition.fps}
      compositionWidth={spec.composition.width}
      compositionHeight={spec.composition.height}
      controls
    />
  );
}
```

## 使用标准组件

```typescript
import { defineCatalog } from "@json-render/core";
import {
  schema,
  standardComponentDefinitions,
  standardTransitionDefinitions,
  standardEffectDefinitions,
} from "@json-render/remotion";

export const videoCatalog = defineCatalog(schema, {
  components: standardComponentDefinitions,
  transitions: standardTransitionDefinitions,
  effects: standardEffectDefinitions,
});
```

## 添加自定义组件

```typescript
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    ...standardComponentDefinitions,
    MyCustomClip: {
      props: z.object({ text: z.string() }),
      type: "scene",
      defaultDuration: 90,
      description: "我的自定义视频片段",
    },
  },
});

// 将自定义组件传递给 Renderer
<Player
  component={Renderer}
  inputProps={{
    spec,
    components: { MyCustomClip: MyCustomComponent },
  }}
/>
```

## 时间轴规范结构

```json
{
  "composition": { "id": "video", "fps": 30, "width": 1920, "height": 1080, "durationInFrames": 300 },
  "tracks": [{ "id": "main", "name": "Main", "type": "video", "enabled": true }],
  "clips": [
    { "id": "clip-1", "trackId": "main", "component": "TitleCard", "props": { "title": "Hello" }, "from": 0, "durationInFrames": 90 }
  ],
  "audio": { "tracks": [] }
}
```

## 标准组件

| 组件 | 类型 | 描述 |
|------|------|------|
| `TitleCard` | scene | 全屏标题带副标题 |
| `TypingText` | scene | 终端风格的打字动画 |
| `ImageSlide` | image | 全屏图片显示 |
| `SplitScreen` | scene | 双面板对比 |
| `QuoteCard` | scene | 带署名的引言卡片 |
| `StatCard` | scene | 动画统计显示 |
| `TextOverlay` | overlay | 文本覆盖 |
| `LowerThird` | overlay | 名称/标题覆盖 |

## 关键导出

| 导出 | 目的 |
|------|------|
| `Renderer` | 将规范渲染为 Remotion 组合 |
| `schema` | 时间轴模式 |
| `standardComponents` | 预构建组件注册表 |
| `standardComponentDefinitions` | 目录定义 |
| `useTransition` | 过渡动画钩子 |
| `ClipWrapper` | 带过渡包裹片段 |
