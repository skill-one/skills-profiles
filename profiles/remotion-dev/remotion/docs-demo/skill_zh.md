# 在文档中添加交互式演示

交互式演示使用 `@remotion/player` 在文档页面中内联渲染 Remotion 组合。它们位于 `packages/docs/components/demos/` 中。

效果演示是独立的：使用 `<EffectsDemo type="effects-..." />` 并在 `packages/docs/components/effects-demos/registry.ts` 中注册它们，使用真实的 `effect schema`，而不是通用的 `<Demo>` 选项数组。

## 步骤

1. **在 `packages/docs/components/demos/` 中创建一个组件**（例如 `MyDemo.tsx`）。它应该是一个标准的 React 组件，使用 Remotion 钩子，如 `useCurrentFrame()` 和 `useVideoConfig()`。

2. **在 `packages/docs/components/demos/types.ts` 中注册演示**：
   - 导入组件
   - 导出一个 `DemoType` 对象，包含以下字段：
     - `id`：在 `<Demo type="..." />` 中使用的唯一字符串
     - `comp`：React 组件
     - `compWidth` / `compHeight`：画布尺寸（例如 1280x720）
     - `fps`：帧率（通常为 30）
     - `durationInFrames`：动画长度
     - `autoPlay`：是否自动播放
     - `options`：交互式控制的数组（可以为空 `[]`）

3. **添加到 `packages/docs/components/demos/index.tsx` 中的演示数组**：
   - 从 `./types` 导入演示常量
   - 将其添加到 `demos` 数组中

4. **在 MDX 中使用 `<Demo type="your-id" />`**

## 选项

选项在播放器下方添加交互式控制。每个选项需要 `name` 和 `optional`（`'no'`、`'default-enabled'` 或 `'default-disabled'`）。

支持的类型：

- `type: 'numeric'` — 滑块，带有 `min`、`max`、`step`、`default`
- `type: 'boolean'` — 复选框，带有 `default`
- `type: 'enum'` — 下拉菜单，带有 `values` 数组和 `default`
- `type: 'string'` — 文本输入，带有 `default`

选项值作为 `inputProps` 传递给组件。像普通 React 属性一样访问它们。

## 示例注册

```ts
export const myDemo: DemoType = {
  comp: MyDemoComp,
  compHeight: 720,
  compWidth: 1280,
  durationInFrames: 150,
  fps: 30,
  id: 'my-demo',
  autoPlay: true,
  options: [],
};
```
