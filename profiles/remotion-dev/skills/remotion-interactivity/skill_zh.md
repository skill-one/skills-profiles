通过以特定方式编写 Remotion 标记，Remotion Studio 能够识别代码的结构并使其具备交互性：

- 允许通过点击选择项目
- 支持拖拽、调整大小和旋转
- 编辑 CSS 样式
- 使关键帧和缓动值可编辑

如果标记过于复杂，以至于 Studio 无法将其交互化，那么这些值将变为灰色。

## 使用 `Interactive` 将 HTML 元素设置为可交互

每个 HTML 和 SVG 元素（除了 `<Img>`，它本身已经是可交互的）例如 `<div>` 都可以通过 `Interactive` 设置为可交互：

```tsx title="Interactive elements"
<Interactive.Div
  name="Greeting card"
  style={{fontSize: 80, padding: 24}}
>
  Hello
</Interactive.Div>
```

这使得可以在 Studio 中设置样式和关键帧。请务必谨慎操作，如果一个组件包含多个元素，时间线可能会变得混乱。

## 优先使用内联文本

如果文本是固定的且仅使用一次，应将其直接编写在交互元素内部，而不是提取为常量。

```tsx title="Inline text"
// 👍 Fixed copy stays editable
<Interactive.Div name="Title">
  Remotion Best Practices
</Interactive.Div>
```

仅在文本为动态或可复用的情况下才使用属性或变量。

## 为交互元素提供描述性的名称

为元素添加 `name` 属性，以便轻松识别。避免使用计算得出的名称，应将其硬编码（固定）。

```tsx title="Interactive names"
<>
  <Interactive.Div name="Hero title" style={{fontSize: 80}}>
    Launch day
  </Interactive.Div>
  <Img name="Avatar" src="https://remotion.media/image.jpeg" />
  <Video name="Background" src="https://remotion.media/video.mp4" />
  <Sequence name="Title">
    Launch day
  </Sequence>
</>
```

## 保持所有 CSS 样式内联

最佳做法是直接将纯对象传递给 `style` 属性——不使用常量引用、对象展开，也不进行数学计算。

```tsx title="Interactive example"
<Interactive.Div
  style={{
    fontSize: 80,
    color: 'red',
  }}
>
  Hello World!
</Interactive.Div>
```

```tsx title="❌ Bad for interactivity"
const baseStyle = useMemo(() => {
  return {
    fontSize: 12 // ❌ Non-inline styles are not supported
  }
}, []);

<Interactive.Div
  style={{
    ...baseStyle, // ❌ Spreading is not supported
    color: RED, // ❌ Referring to constants is not supported
    scale: frame * 10 // ❌ Math is not supported
  }}
>
  Hello World!
</Interactive.Div>
```

## 使用 `interpolate()` 进行动画

在发生变化的属性上编写内联的 `interpolate()` 调用。输出范围、缓动、外推和 `output` 属性应使用硬编码的值。

输入范围还可额外使用从 `useVideoConfig()` 中直接解构出的 `durationInFrames`、`fps`、`width` 和 `height`。诸如 `durationInFrames` 之类的裸标识符、诸如 `2 * fps` 或 `fps * 2` 的与数字相乘，以及诸如 `durationInFrames - 1` 的与数字相减均受支持。

```tsx title="Inline values"
const {fps, durationInFrames} = useVideoConfig();

// 👍 Inline values can be standardized and keyframed
<Interactive.Div
  name="Product card"
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

```tsx title="❌ Bad interactivity"
const translateY = interpolate(frame, [0, 30], [0, 120]); // ❌ Math should be directly in the markup

<Interactive.Div
  name="Product card"
  style={{
    translate: translateY, // ❌ Only inline interpolate() calls are supported,
    rotate: interpolate(frame, [start, start + 10], [0, Math.PI]), // ❌ Cannot use math with arbitrary variables, cannot use constants
    scale: interpolate(anyVariable, [0, 30], [0, 1]) // ❌ Can only interpret the `frame` variable.
  }}
/>
```

## 使用 `scale`、`translate`、`rotate` CSS 属性

避免使用 `transform` CSS 属性。如果可能，请改用 `scale`、`rotate` 和 `translate`，因为它们是可以交互编辑的。

## 保持组合元数据内联

在搭建组合时，保持 `width`、`height`、`fps`、`durationInFrames` 和 `defaultProps` 内联，且不进行任何类型断言。

当 `<Composition>` 或 `<Still>` 上的 `defaultProps` 是内联对象字面量时，Props 编辑器可将视觉编辑保存回你的代码中。

```tsx
// 👍 Static values are in <Composition>, dynamic values are in calculateMetadata()
const calculateMetadata = useMemo(async () => {
  const dimensions = await getDimensions(); // just an example
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

```tsx title="Negative examples"
const defaultProps = {title: 'Hello', color: '#0b84ff'}; // ❌ Don't extract defaultProps, must be inline
const calculateMetadata = useMemo(() => {
  // ❌ Unnecessary because no calculation is being done,
  return {durationInFrames: 150, fps: 30, width: 1920, height: 1080};
});

<Composition
  id="my-video"
  component={MyComponent}
  calculateMetadata={calculateMetadata}
  defaultProps={{
    title: 'Hello',
  } as Props} // ❌ Don't have type assertions, instead type MyComponent correctly
/>
```

仅使用 `calculateMetadata()` 来处理元数据中动态的部分。

## 效果也应为内联

效果数组不应进行计算。与此处设置关键帧的规则相同，`interpolate()` 同样适用：所有值也应为硬编码的：输入范围、输出范围、缓动、外推、`output` 属性。

```tsx title="Effects"
// 👍 Parameters are inline and the array shape is stable
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
  // ❌ Conditional effect is not animateable
  effects={enabled ? [
    radialProgressiveBlur({
      // ❌ Not inline
      center,
      rotation,
    }),
  ] : []}
/>
```

如果一个版本应有效果而另一个版本不应有，则请渲染单独的元素。

## 使自己的组件可交互

在使用 `Interactive.withSchema()` 时，请在 schema 中包含 `Interactive.baseSchema`，以便保留修剪和可见性等标准时间线控件。

若要使自定义用户端（userland）组件可交互，请使用：
[使组件可交互](https://www.remotion.dev/docs/studio/make-component-interactive.md)

## 视频编辑

如果一个 Remotion 组件主要由视频和音频片段组成，请参阅“视频编辑”，以了解构建 Remotion 标记的最佳实践，从而使得这些片段能够在时间线中交互编辑。
