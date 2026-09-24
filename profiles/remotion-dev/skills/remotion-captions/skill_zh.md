所有字幕必须以 JSON 格式处理。字幕必须使用 [`Caption`](https://www.remotion.dev/docs/captions/caption.md) 类型，定义如下：

```ts
import type { Caption } from "@remotion/captions";
```

```ts
type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
  pageBreakAfter?: boolean;
};
```

## 生成字幕

要转录视频和音频文件以生成字幕，请加载 [transcribe-captions.md](transcribe-captions.md) 文件以获取更多说明。

## 显示字幕

要在视频中显示字幕，请加载 [display-captions.md](display-captions.md) 文件以获取更多说明。

## 导入字幕

要从 .srt 文件导入字幕，请加载 [import-srt-captions.md](import-srt-captions.md) 文件以获取更多说明。
