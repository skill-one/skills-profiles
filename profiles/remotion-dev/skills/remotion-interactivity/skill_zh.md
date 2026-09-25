通过以特定方式编写 Remotion 标记，Remotion Studio 能够识别代码的结构并使其具有交互性：

- 允许通过点击选择项目
- 允许拖放、调整大小和旋转
- 编辑 CSS 样式
- 使关键帧和缓动值可编辑

如果标记对 Studio 来说太复杂而无法使其具有交互性，则值会变为灰色。

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

这允许在 Studio 中设置样式和关键帧。要明智一些，如果一个组件有多个元素，时间轴可能会变得混乱。

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

为元素添加 `name` 属性，以便它们易于识别。
避免计算名称，直接硬编码它们。

```tsx title="交互式名称"
<>
  <Interactive.Div name="英雄标题" style={{fontSize: 80}}>
    发售日
  </Interactive.Div>
  <Img name="头像" src="https://remotion.media/image.jpeg" />
  <Video name="背景" src="https://remotion.media/video.mp4" />
  <Sequence name="标题">
    发售日
  </Sequence>
</>
```

## 保留所有 CSS 样式为内联

最佳方式是将一个普通对象传递给 `style` - 不要引用常量，不要对象展开，不要数学运算。

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
    ...baseStyle, // ❌ 不支持展开
    color: RED, // ❌ 不支持引用常量
    scale: frame * 10 // ❌ 不支持数学运算
  }}
>
  Hello World!
</Interactive.Div>
```

## 使用 `interpolate()` 进行动画

将动画作为要更改属性的 `interpolate()` 调用编写。
输出范围、缓动、外推和 `output` 属性应使用硬编码值。

输入范围可以额外使用 `durationInFrames`、`fps`、`width` 和从 `useVideoConfig()` 直接解构的 `height`。裸标识符（如 `durationInFrames`）、与数字相乘（如 `2 * fps` 或 `fps * 2`）以及减去数字（如 `durationInFrames - 1`）是受支持的。

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
    scale: interpolate(anyVariable, [0, 30], [0, 1]) // ❌ 仅能解释 `frame` 变量。
  }}
/>
```

## 使用 `scale`、`translate`、`rotate` CSS 属性

避免使用 `transform` CSS 属性。
如果可能，使用 `scale`、`rotate` 和 `translate`，因为只有它们是可交互编辑的。

## 保留组合元数据为内联

在搭建组合时，将 `width`、`height`、`fps`、`durationInFrames` 和 `defaultProps` 保留为内联，不要进行类型断言。

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
const defaultProps = {title: 'Hello', color: '#0b84ff'}; // ❌ 不要提取 defaultProps，必须为内联
const calculateMetadata = useMemo(() => {
  // ❌ 无需计算，因为未进行任何计算
  return {durationInFrames: 150, fps: 30, width: 1920, height: 1080};
});

<Composition
  id="my-video"
  component={MyComponent}
  calculateMetadata={calculateMetadata}
  defaultProps={{
    title: 'Hello',
  } as Props} // ❌ 不要进行类型断言，而是正确地类型化 MyComponent
/>
```

仅使用 `calculateMetadata()` 来处理元数据中动态的部分。

## 效果也应为内联

效果数组不应进行计算。
设置 `interpolate()` 关键帧的相同规则也适用于这里：所有值也应该是硬编码的：输入范围、输出范围、缓动、外推、`output` 属性。

```tsx title="效果"
// 👍 参数为内联，数组形状是稳定的
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
  // ❌ 条件效果不可动画
  effects={enabled ? [
    radialProgressiveBlur({
      // ❌ 非内联
      center,
      rotation,
    }),
  ] : []}
/>
```

如果其中一个版本应有效果而另一个版本不应，请渲染单独的元素。

## 使自己的组件具有交互性

在使用 `Interactive.withSchema()` 时，在模式中包含 `Interactive.baseSchema`，以便标准时间轴控件（如修剪和可见性）保持可用。

要使自定义用户组件具有交互性，请使用：
[使组件具有交互性](https://www.remotion.dev/docs/studio/make-component-interactive.md)

## 视频编辑

如果一个 Remotion 组件主要由视频和音频片段组成，请参阅视频编辑以了解如何构建 Remotion 标记的最佳实践，以便片段可以在时间轴中交互式编辑。
