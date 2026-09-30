---
name: remotion-interactivity
description: 结构移除标记以实现交互
---

通过特定方式编写 Remotion 标记，Remotion Studio 能够识别代码结构并使其具有交互性：

- 允许通过点击选择项目
- 允许拖放、调整大小和旋转
- 编辑 CSS 样式
- 使关键帧和缓动值可编辑

如果标记对 Studio 来说过于复杂而无法使其具有交互性，则值会变为灰色。

## 使用 `Interactive` 使 HTML 元素具有交互性

每个 HTML 和 SVG 元素（`<Img>` 除外，它已经是交互式的），例如 `<div>`，都可以使用 `Interactive` 转换为交互式：

```tsx title="交互式元素"
<Interactive.Div
  name="问候卡片"
  style={{fontSize: 80, padding: 24}}
>
  Hello
</Interactive.Div>
```

这允许在 Studio 中设置样式和关键帧。要明智地处理，如果一个组件包含许多元素，时间轴可能会变得混乱。

## 优先使用内联文本

如果文本是固定的且仅使用一次，请直接将其写在交互式元素内部，而不是提取到常量中。

```tsx title="内联文本"
// 👍 固定文本保持可编辑
<Interactive.Div name="标题">
  Remotion 最佳实践
</Interactive.Div>
```

仅在文本是动态的或重复使用时才使用属性或变量。

## 为交互式元素提供描述性名称

为元素添加 `name` 属性，以便轻松识别它们。
避免计算名称，直接硬编码它们。

```tsx title="交互式名称"
<>
  <Interactive.Div name="英雄标题" style={{fontSize: 80}}>
    发布日
  </Interactive.Div>
  <Img name="头像" src="https://remotion.media/image.jpeg" />
  <Video name="背景" src="https://remotion.media/video.mp4" />
  <Sequence name="标题">
    发布日
  </Sequence>
</>
```

## 保持所有 CSS 样式内联

最佳方式是将一个普通对象直接传递给 `style` —— 不引用常量、不展开对象、不做数学运算。

```tsx title="交互式示例"
<Interactive.Div
  style={{
    fontSize: 80,
    color: 'red',
  }}
>
  Hello World!
</Interactive.Div>
```

```tsx title="❌ 不利于交互性"
const baseStyle = useMemo(() => {
  return {
    fontSize: 12 // ❌ 非内联样式不受支持
  }
}, []);

<Interactive.Div
  style={{
    ...baseStyle, // ❌ 展开不受支持
    color: RED, // ❌ 不支持引用常量
    scale: frame * 10 // ❌ 不支持数学运算
  }}
>
  Hello World!
</Interactive.Div>
```

## 使用 `interpolate()` 进行动画

将动画作为属性变化的内联 `interpolate()` 调用编写。
输出范围、缓动、外推和 `output` 属性应使用硬编码值。

输入范围可以额外使用 `durationInFrames`、`fps`、`width` 和 `height` 直接从 `useVideoConfig()` 解构。支持裸标识符，如 `durationInFrames`、乘以数字，如 `2 * fps` 或 `fps * 2`，以及减去数字，如 `durationInFrames - 1`。

```tsx title="内联值"
const {fps, durationInFrames} = useVideoConfig();

// 👍 内联值可以标准化和关键帧化
<Interactive.Div
  name="产品卡片"
  style={{
    color: 'white',
    fontSize: 80,
    scale: interpolate(frame, [0, fps], [0, 1], {
      easing: Easing.spring({damping: 200}),
      output: 'perceptual-scale',
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp'
    }),
    rotate: interpolate(frame, [0, 1 * fps], ['0deg', '20deg'], {
      easing: Easing.spring({damping: 200}),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp'
    }),
    translate: interpolate(
      frame,
      [durationInFrames - 30, durationInFrames],
      ['0px 0px', '0px 120px'],
      {
        easing: Easing.spring({damping: 200}),
        output: 'perceptual-scale',
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp'
      }
    ),
  }}
/>
```

```tsx title="❌ 不利于交互性"
const translateY = interpolate(frame, [0, 30], [0, 120]); // ❌ 数学运算应直接在标记中

<Interactive.Div
  name="产品卡片"
  style={{
    translate: translateY, // ❌ 仅支持内联 interpolate() 调用
    rotate: interpolate(frame, [start, start + 10], [0, Math.PI]), // ❌ 不能使用任意变量的数学运算，不能使用常量
    scale: interpolate(anyVariable, [0, 30], [0, 1]) // ❌ 仅能解释 `frame` 变量
  }}
/>
```

## 使用 `Interactive.Path` 保持 SVG 路径可编辑

使用 `remotion` 中的 `<Interactive.Path>` 而不是在 SVG 内部使用 `<path>`，以使路径在视觉上可编辑。

安装 `@remotion/paths` 以进行路径插值和 Studio 路径关键帧：

```sh
bunx remotion add @remotion/paths
```

如果几何形状是静态的，请将路径字符串直接放在 `d` 属性中。不要将其提取到常量中。

```tsx title="可编辑的静态路径"
import {Interactive} from 'remotion';

<Interactive.Svg width={300} height={300} viewBox="0 0 300 300">
  <Interactive.Path
    name="三角形"
    d="M 40 40 L 260 40 L 150 260 Z"
    fill="#0b84f3"
  />
</Interactive.Svg>
```

### 使用内联 `interpolatePaths()` 变形路径

直接在 `d` 中使用 `@remotion/paths` 的 `interpolatePaths()`。
它接受一个帧、一个输入范围、一个同样大小的路径字符串数组，以及用于缓动、外推和 posterization 的选项。
保持输出路径、范围和选项内联，遵循与 `interpolate()` 上相同的输入范围规则。
当路径关键帧应在 Studio 中保持可编辑时，不要使用 `interpolatePath()` API 或将插值结果提取到变量中。

```tsx title="可编辑的路径关键帧"
import {interpolatePaths} from '@remotion/paths';
import {Easing, Interactive, useCurrentFrame} from 'remotion';

export const 变形路径 = () => {
  const frame = useCurrentFrame();

  return (
    <Interactive.Svg width={300} height={300} viewBox="0 0 300 300">
      <Interactive.Path
        name="变形三角形"
        d={interpolatePaths(
          frame,
          [0, 30, 60],
          [
            'M 40 40 L 260 40 L 150 260 Z',
            'M 40 150 L 150 40 L 260 150 Z',
            'M 40 260 L 150 40 L 260 260 Z',
          ],
          {
            easing: Easing.bezier(0.42, 0, 0.58, 1),
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          },
        )}
        fill="#0b84f3"
      />
    </Interactive.Svg>
  );
};
```

Studio 可以在当前帧编辑路径，添加或移动关键帧，并调整它们的缓动。
使用 `strokeDasharray` 和 `strokeDashoffset` 使路径演变。

## 使用 `scale`、`translate`、`rotate` CSS 属性

避免使用 `transform` CSS 属性。
如果可能，使用 `scale`、`rotate` 和 `translate`，因为只有它们是交互式可编辑的。

## 保持组合元数据内联

在搭建组合时，保持 `width`、`height`、`fps`、`durationInFrames` 和 `defaultProps` 内联，不做类型断言。

当 `defaultProps` 是 `<Composition>` 或 `<Still>` 上的内联对象字面量时，Props 编辑器可以将视觉编辑保存回您的代码。

```tsx
// 👍 静态值在 <Composition> 中，动态值在 calculateMetadata() 中
const calculateMetadata = useMemo(async () => {
  const dimensions = await getDimensions(); // 仅为例子
  return {width: dimensions.width, height: dimensions.height};
});

<Composition
  id="my-video"
  component={MyComponent}
  durationInFrames={150}
  fps={30}
  calculateMetadata={calculateMetadata}
  defaultProps={{title: 'Hello', color: '#0b84ff'}}
/>
```

```tsx title="负面示例"
const defaultProps = {title: 'Hello', color: '#0b84ff'}; // ❌ 不要提取 defaultProps，必须内联
const calculateMetadata = useMemo(() => {
  // ❌ 无需计算，因为未进行计算
  return {durationInFrames: 150, fps: 30, width: 1920, height: 1080};
});

<Composition
  id="my-video"
  component={MyComponent}
  calculateMetadata={calculateMetadata}
  defaultProps={{
    title: 'Hello',
  } as Props} // ❌ 不要有类型断言，而是正确地类型化 MyComponent
/>
```

仅使用 `calculateMetadata()` 用于元数据的动态部分。

## 特效也应内联

特效数组不应进行计算。
设置关键帧与 `interpolate()` 的相同规则也适用于这里：所有值也应硬编码：输入范围、输出范围、缓动、外推、`output` 属性。

```tsx title="特效"
// 👍 参数内联，数组形状稳定
<CanvasImage
  src={src}
  width={1280}
  height={720}
  effects={[
    radialProgressiveBlur({
      center: [0.5, 0.5],
      width: 1.2,
      height: 0.8,
      start: 0.2,
      disabled: true,
      rotation: interpolate(frame, [0, 120], [0, 180]),
    }),
  ]}
/>

const center = [0.5, 0.5] as const;
const rotation = frame * 1.5;

<CanvasImage
  src={src}
  width={1280}
  height={720}
  // ❌ 条件性特效不可动画
  effects={enabled ? [
    radialProgressiveBlur({
      // ❌ 非内联
      center,
      rotation,
    }),
  ] : []}
/>
```

如果一种版本应有特效而另一种版本不应，请渲染单独的元素。

## 使自己的组件具有交互性

在使用 `Interactive.withSchema()` 时，在模式中包含 `Interactive.baseSchema`，以便标准时间轴控件（如修剪和可见性）保持可用。

要使自定义用户组件具有交互性，请使用：
[使组件具有交互性](https://www.remotion.dev/docs/studio/make-component-interactive.md)

## 视频编辑

如果 Remotion 组件主要由视频和音频片段组成，请查看视频编辑以了解如何结构化 Remotion 标记的最佳实践，以便片段在时间轴中可交互编辑。
