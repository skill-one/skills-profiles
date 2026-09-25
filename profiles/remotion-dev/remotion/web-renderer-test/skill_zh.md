使用此功能在需要时更新现有的网络渲染器测试，以适应实现变更。仅在用户明确要求时添加新测试。

网络渲染器位于 `packages/web-renderer` 中，测试套件位于 `packages/web-renderer/src/test`。

它使用 vitest 进行视觉快照测试。例如，可以使用以下命令执行测试文件：

```
bunx vitest src/test/video.test.tsx
```

## 示例

每个测试都由 `packages/web-renderer/src/test/fixtures` 中的 fixture 驱动。
一个 fixture 的示例如下：

```tsx
import {AbsoluteFill} from 'remotion';

const Component: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          backgroundColor: 'red',
          width: 100,
          height: 100,
          borderRadius: 20,
        }}
      />
    </AbsoluteFill>
  );
};

export const backgroundColor = {
  component: Component,
  id: 'background-color',
  width: 200,
  height: 200,
  fps: 25,
  durationInFrames: 1,
} as const;
```

相应的测试如下：

```tsx
import {test} from 'vitest';
import {renderStillOnWeb} from '../render-still-on-web';
import {backgroundColor} from './fixtures/background-color';
import {testImage} from './utils';

test('should render background-color', async () => {
  const blob = await renderStillOnWeb({
    licenseKey: 'free-license',
    composition: backgroundColor,
    frame: 0,
    inputProps: {},
    imageFormat: 'png',
  });

  await testImage({blob, testId: 'background-color'});
});
```

## 添加新测试

1. 在 `packages/web-renderer/src/test/fixtures` 中添加一个新的 fixture。
2. **重要**：将 fixture 添加到 `packages/web-renderer/src/test/Root.tsx` 以添加预览方式。
3. 在 `packages/web-renderer/src/test` 中添加一个新的测试。
4. 运行 `bunx vitest src/test/video.test.tsx` 执行测试。
5. **重要**：更新 `packages/docs/docs/client-side-rendering/limitations.mdx` 以反映新支持的特性。
