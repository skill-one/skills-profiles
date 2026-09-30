---
name: remotion-markup
description: 内容、动画和效果最佳实践
---

这是编写 Remotion React 标记的指南。
如果与此不相关，请加载 Remotion 最佳实践。

## 保留用户更改

用户可以在对话之外的代码中进行编辑。

如果你检测到在此期间做出的令人惊讶的更改，不要覆盖它，假设它是故意的或请求确认。

## 一般规则

使用 `useCurrentFrame()` 和 `interpolate()` 驱动动画。
CSS `transition` 或 `animation` 将无法正确渲染，它们需要被重构。
Tailwind 动画类将无法正确渲染，它们需要被重构。

使用 `Easing.bezier()` 和 `Easing.spring()` 来自定义时间。

根据 Remotion 交互性最佳实践来构建你的标记

```tsx
import { useCurrentFrame, Easing, interpolate, Interactive } from "remotion";

export const FadeIn = () => {
  const frame = useCurrentFrame();

  return (
    <Interactive.Div
      name="Title"
      style={{
        opacity: interpolate(frame, [0, 2 * fps], [0, 1], {
          extrapolateRight: "clamp",
          extrapolateLeft: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
      }}
    >
      Hello World!
    </Interactive.Div>
  );
};
```

在 `style` 属性中将 `interpolate()` 调用保持内联。
使用 `scale`、`translate`、`rotate` CSS 属性而不是 `transform`。

```tsx
// 👍 内联可编辑的关键帧和 transform 简写
style={{
  scale: interpolate(frame, [0, 100], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}),
    output: 'perceptual-scale' // 对于 `scale` 动画，使用 "output: 'perceptual-scale'"
  }),
  translate: interpolate(frame, [0, 100], ["0px 0px", "100px 100px"], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}),
  }),
  rotate: interpolate(frame, [0, 100], ["20deg", "90deg"], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}),
  }),
}}

// 👎 非内联值和 transform 字符串在 Studio 中更难编辑
const scale = interpolate(frame, [0, 100], [0, 1]);

style={{
  transform: `scale(${scale})`,
}}
```

## 资产

将资产放置在项目根目录下的 `public/` 文件夹中。
使用 `staticFile()` 来引用 `public/` 文件夹中的文件。

## 媒体组件

使用 `@remotion/media` 中的 `<Video>` 和 `<Audio>` 添加视频和音频。
使用 `<CanvasImage>` 组件添加图像。
使用 `<AnimatedImage>` 添加动画 GIF、APNG、WebP 或 AVIF 图像，如果不用 Chrome，则使用 `@remotion/gif`。
使用 `staticFile()` 引用 `public/` 中的文件或直接传递远程 URL：

```tsx
import { Audio, Video } from "@remotion/media";
import { staticFile, CanvasImage, AnimatedImage } from "remotion";

export const MyComposition = () => {
  return (
    <>
      <Video src={staticFile("video.mp4")} style={{ opacity: 0.5 }} />
      <Audio src={staticFile("audio.mp3")} />
      <CanvasImage
        src={staticFile("logo.png")}
        style={{ width: 100, height: 100 }}
      />
      <Video src="https://remotion.media/video.mp4" />
      <AnimatedImage src={staticFile('nyancat.gif')} />
    </>
  );
};
```

## 示例场景

```tsx
import {
  AbsoluteFill,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
  useVideoConfig
} from "remotion";

export const Empty = () => {
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      name="Scene"
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'white'
      }}
    >
      <Interactive.Div
        name="Title"
        style={{
          opacity: interpolate(frame, [1 * fps, 2 * fps], [0, 1], {
            extrapolateRight: "clamp",
            extrapolateLeft: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
          fontSize: 88
        }}
      >
        Title
      </Interactive.Div>
      <Interactive.Div
        name="Subtitle"
        style={{
          opacity: interpolate(frame, [2 * fps, 3 * fps, 8 * fps, 10 * fps], [0, 1, 1, 0], {
            extrapolateRight: "clamp",
            extrapolateLeft: "clamp",
            easing: [Easing.bezier(0.16, 1, 0.3, 1), Easing.linear, Easing.bezier(0.16, 1, 0.3, 1)],
          }),
          fontSize: 32
        }}
      >
        Subtitle
      </Interactive.Div>
    </AbsoluteFill>
  );
}
```

## 延迟、修剪

大多数组件（`<AbsoluteFill>`、`<Interactive.*>` `<Img>`、`<AnimatedImage>`、`<CanvasImage>`、`<HtmlInCanvas>`、`<Solid>`、`<Sequence>` 从 `remotion`、`<Video>` 和 `<Audio>` 从 `@remotion/media`、`<Gif>` 等）支持以下属性：

### from

```tsx
<Img from={1 * fps} {/* ... */}/>
<Video from={1 * fps} {/* ... */}/>
<Interactive.Div from={1 * fps} {/* ... */}/>
```

当元素开始在时间轴上出现时。

### durationInFrames

```tsx
<Img durationInFrames={20 * fps} {/* ... */}/>
<Interactive.Div durationInFrames={20 * fps} {/* ... */}/>
```

层在时间轴上播放的持续时间。
对于媒体，传递媒体的自然持续时间：`<Video durationInFrames={29.322 * fps}/>`。

### `trimBefore`

对于内部时钟应开始较晚的组件很有用：

```tsx
// 剪掉前 2 秒的片段
<Video trimBefore={2 * fps} {/* ... */} />

// `useCurrenFrame()` for children starts at `10 * fps`
<Sequence trimBefore={10 * fps} {/* ... */} />
```

### Fallback

如果一个组件不支持这些属性，用 `remotion` 的 `<Sequence>` 包裹它，它具有这些属性。

- `layout="absolute-fill"` 使 Sequence 行为像 AbsoluteFill
- `layout="none"` 是“无头”模式，不使用包装元素。

## 地图

如果想在视频中包含地图，请查看 [Remotion Maps](./remotion-maps/REFERENCE.md)。

## 文本高亮和注释

查看 [text-highlights.md](text-highlights.md) 以获取文本高亮（高亮标记）、圆圈、下划线、删除线、划掉文本、方框。

## 多场景视频

如果计划制作具有多个后续场景的视频，请查看 [multi-scene-video.md](multi-scene-video.md)。

## 连接的合成

当一个场景或一组图层值得它自己的可编辑时间轴时，请遵循 [connected-compositions.md](connected-compositions.md)。对于多场景视频中的主要场景，请优先使用这种结构。

## 配音

查看 [voiceover.md](voiceover.md)，以使用 ElevenLabs TTS 为 Remotion 合成添加 AI 生成配音。

## 嵌入视频

查看 [embedding-videos.md](embedding-videos.md)，以获取有关嵌入视频的高级知识——修剪、音量、速度、循环、音调。

## 嵌入音频

查看 [audio.md](audio.md)，以获取高级音频功能，如修剪、音量、速度、音调。

## 视频编辑

查看 [video-editing.md](video-editing.md)，以在 Remotion Studio 中构建可编辑的视频时间轴。

## 裁剪

如果需要裁剪组件的可视矩形，请查看 [cropping.md](cropping.md)。

## 过渡

查看 [transitions.md](transitions.md)，以获取场景过渡模式。

## 运动模糊

当添加运动模糊或运动轨迹时，请阅读 [motion-blur.md](motion-blur.md)，以获取首选的 HTML-in-canvas 方法、预览要求以及替代方案。

## 视觉和像素效果

当创建视觉效果时，请考虑是否可以使用 CSS 和 HTML 实现，或者是否需要着色器。
顺序或优先级：

1. 常规 HTML + CSS 或其他网页技术
2. 直接对元素应用效果（`<Video>`、`<Img>`），或通过将内容包裹在 [`<HtmlInCanvas>`](html-in-canvas.md) 中，它也接受 `effects`：

- 通过 [effects.md](effects.md) 列出的效果
- 当没有预设时，通过 [effects.md](effects.md) 使用自定义 `createEffect()`。

## 3D 内容

查看 [./3d.md](./3d.md)，以了解使用 Three.js 和 React Three Fiber 在 Remotion 中创建 3D 内容。

## 音效

当需要使用音效时，加载 [./sfx.md](./sfx.md) 文件以获取更多信息。

## 音频可视化

当需要可视化音频（频谱条、波形、低音反应效果）时，加载 [./audio-visualization.md](./audio-visualization.md) 文件以获取更多信息。

## 地图

对于静态地图、动画路线和标记、地理解释、Mapbox、MapLibre、MapTiler、GeoJSON 或 3D 地理飞越，请加载 [Remotion Maps](./remotion-maps/REFERENCE.md)。

## 字幕

当处理字幕或字幕时，请加载 Remotion 字幕技能以获取更多信息。

## Google Fonts

是 Remotion 中加载字体的推荐方式。查看 [google-fonts.md](google-fonts.md)，以了解如何加载 Google Fonts。

## 本地字体

查看 [local-fonts.md](local-fonts.md)，以了解如何加载本地字体。

## GIFs

查看 [gifs.md](gifs.md)，以了解如何显示与 Remotion 时间轴同步的 GIF。

## 高级图像

查看 [images.md](images.md)，以了解图像的尺寸和定位、动态图像路径以及获取图像尺寸。

## Lottie 动画

查看 [lottie.md](lottie.md)，以了解如何在 Remotion 中嵌入 Lottie 动画。

## 时间

查看 [timing.md](timing.md)，以获取更多 `interpolate()` 的时间技术。

## 参数化视频

查看 [parameters.md](parameters.md)，以通过添加 Zod 模式使合成可参数化。

## 测量 DOM 节点

查看 [measuring-dom-nodes.md](measuring-dom-nodes.md)，以在 Remotion 中测量 DOM 元素的尺寸。

## 测量文本

查看 [measuring-text.md](measuring-text.md)，以测量文本尺寸、将文本适配到容器以及检查溢出。

## 使用 FFmpeg

对于某些视频操作，例如修剪视频或检测静音，应使用 FFmpeg。加载 [./ffmpeg.md](./ffmpeg.md) 文件以获取更多信息。

## 静音检测

当需要检测并修剪视频或音频文件中的静音段时，请加载 [./silence-detection.md](./silence-detection.md) 文件。

## 动态持续时间、尺寸和数据

查看 [calculate-metadata.md](calculate-metadata.md)，以动态设置合成持续时间、尺寸和属性。

## 高级合成

查看 [compositions.md](compositions.md)，以了解如何定义静态图像、文件夹、默认属性以及如何嵌套合成。对于 Studio 导航到场景自己的时间轴，请使用 [连接的合成](connected-compositions.md)。

## 高级序列

查看 [sequencing.md](sequencing.md)，以获取更多序列模式——延迟、修剪、限制项目的持续时间。

## 安装模块

使用 `npx remotion add` 添加新包并使用正确的版本：

```
npx remotion add @remotion/media
```

这适用于 `@remotion/*` 包、`mediabunny`、`@mediabunny/*`、`zod` 和 `@huggingface/transformers`。

## 视觉检查

当进行视觉检查有用时，请打开 Remotion Studio 以进行交互式预览。

你也可以使用 Rendering 来检查一个或多个帧作为图像。
