# Remotion - 使用 React 创建视频

使用 Remotion 框架（一个使用 React 程序化创建视频的框架）创建程序化视频的全面技能集。

## 使用场景

每当您处理 Remotion 代码时，使用此技能以获得以下特定领域的知识：

- 使用 React 组件创建视频合成
- 使用基于帧的动画动画元素
- 处理音频、视频和图像资源
- 构建图表和数据可视化
- 实现文本动画和字幕
- 使用 Three.js 的 3D 内容
- 应用过渡和序列
- 集成 Tailwind CSS 和 Lottie 动画

## 核心概念

Remotion 允许您使用以下方式创建视频：

- **React 组件**：使用熟悉的 React 语法构建视频内容
- **基于帧的动画**：所有动画由 `useCurrentFrame()` 钩子驱动
- **合成**：定义具有持续时间、尺寸和属性的视频合成
- **资源**：导入和操作图像、视频、音频和字体
- **渲染**：使用可自定义设置程序化导出视频

## 主要功能

- 帧级动画控制
- 动态元数据计算
- 媒体处理（修剪、音量、速度、音调）
- 字幕生成和显示
- 使用图表进行数据可视化
- 3D 内容集成
- 专业文本动画
- 场景过渡和序列

## 使用方法

阅读单个规则文件以获取详细的解释和代码示例：

### 核心动画与时间
- **[references/animations.md](references/animations.md)** - Remotion 的基本动画技术
- **[references/timing.md](references/timing.md)** - 插值曲线：线性、缓动、弹簧动画
- **[references/sequencing.md](references/sequencing.md)** - 延迟、修剪和限制项目的持续时间
- **[references/trimming.md](references/trimming.md)** - 切割动画的开头或结尾

### 合成与元数据
- **[references/compositions.md](references/compositions.md)** - 定义合成、静态图像、文件夹、默认属性
- **[references/calculate-metadata.md](references/calculate-metadata.md)** - 动态设置合成持续时间、尺寸和属性

### 资源与媒体
- **[references/assets.md](references/assets.md)** - 导入图像、视频、音频和字体
- **[references/images.md](references/images.md)** - 使用 Img 组件嵌入图像
- **[references/videos.md](references/videos.md)** - 嵌入视频，支持修剪、音量、速度、循环、音调
- **[references/audio.md](references/audio.md)** - 使用音频和声音，支持修剪、音量、速度、音调
- **[references/gifs.md](references/gifs.md)** - 同步显示与时间轴的 GIF

### 文本与排版
- **[references/text-animations.md](references/text-animations.md)** - 排版和文本动画模式
- **[references/measuring-text.md](references/measuring-text.md)** - 测量文本尺寸，调整文本，检查溢出
- **[references/fonts.md](references/fonts.md)** - 加载 Google 字体和本地字体

### 字幕与转录
- **[references/display-captions.md](references/display-captions.md)** - 使用 TikTok 风格的页面和单词高亮显示字幕
- **[references/import-srt-captions.md](references/import-srt-captions.md)** - 使用 @remotion/captions 导入 .srt 字幕文件
- **[references/transcribe-captions.md](references/transcribe-captions.md)** - 将音频转录为生成字幕

### 数据可视化
- **[references/charts.md](references/charts.md)** - 图表和数据可视化模式

### 高级功能
- **[references/3d.md](references/3d.md)** - 使用 Three.js 和 React Three Fiber 的 3D 内容
- **[references/lottie.md](references/lottie.md)** - 嵌入 Lottie 动画
- **[references/transitions.md](references/transitions.md)** - 场景过渡模式

### 样式与布局
- **[references/tailwind.md](references/tailwind.md)** - 在 Remotion 中使用 TailwindCSS
- **[references/measuring-dom-nodes.md](references/measuring-dom-nodes.md)** - 测量 DOM 元素尺寸

### 媒体处理（Mediabunny）
- **[references/can-decode.md](references/can-decode.md)** - 检查浏览器是否可以解码视频
- **[references/extract-frames.md](references/extract-frames.md)** - 在特定时间戳从视频中提取帧
- **[references/get-audio-duration.md](references/get-audio-duration.md)** - 获取音频文件的持续时间
- **[references/get-video-dimensions.md](references/get-video-dimensions.md)** - 获取视频文件的宽度和高度
- **[references/get-video-duration.md](references/get-video-duration.md)** - 获取视频文件的持续时间

## 快速入门示例

```tsx
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export const MyComposition = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, 2 * fps], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ opacity }}>
      <h1>Hello Remotion!</h1>
    </div>
  );
};
```

## 最佳实践

1. **始终使用 `useCurrentFrame()`** - 从当前帧驱动所有动画
2. **避免 CSS 动画** - 它们不会在视频中正确渲染
3. **以秒为单位思考** - 将秒数乘以 `fps` 进行帧计算
4. **使用 interpolate 实现平滑动画** - 内置的具有缓动函数的插值
5. **限制外推** - 防止值超出预期范围
6. **频繁测试** - 在渲染之前在 Remotion Studio 中预览

## 资源

- **文档**：https://www.remotion.dev/docs
- **仓库**：https://github.com/remotion-dev/remotion
- **技能仓库**：https://github.com/remotion-dev/skills
- **社区**：Discord 和 GitHub 讨论区
- **许可证**：MIT
