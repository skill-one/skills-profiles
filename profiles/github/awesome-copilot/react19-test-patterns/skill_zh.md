# React 19 测试迁移模式

React 19 所需的所有测试文件迁移的参考。

## 优先级顺序

按此顺序修复测试文件；每一层都依赖于前一层：

1. **`act` 导入**  首先修复，它阻塞了其他所有操作
2. **`Simulate` → `fireEvent`**  在 `act` 修复后立即修复
3. **`react-dom/test-utils` 完整清理**  移除剩余的导入
4. **StrictMode 调用次数**  实际测量，不要猜测
5. **异步 `act` 包装**  用于剩余的 "未在 `act` 中包装" 警告
6. **自定义渲染辅助函数**  每个代码库验证一次，而不是每个测试

---

## 1. `act()` 导入修复

```jsx
// 之前  在 React 19 中已移除：
import { act } from 'react-dom/test-utils';

// 之后：
import { act } from 'react';
```

如果与其他 `test-utils` 导入混合：
```jsx
// 之前：
import { act, Simulate, renderIntoDocument } from 'react-dom/test-utils';

// 之后  分离导入：
import { act } from 'react';
import { fireEvent, render } from '@testing-library/react'; // 替换 Simulate + renderIntoDocument
```

---

## 2. `Simulate` → `fireEvent`

```jsx
// 之前  在 React 19 中已移除 `Simulate`：
import { Simulate } from 'react-dom/test-utils';
Simulate.click(element);
Simulate.change(input, { target: { value: 'hello' } });
Simulate.submit(form);
Simulate.keyDown(element, { key: 'Enter', keyCode: 13 });

// 之后：
import { fireEvent } from '@testing-library/react';
fireEvent.click(element);
fireEvent.change(input, { target: { value: 'hello' } });
fireEvent.submit(form);
fireEvent.keyDown(element, { key: 'Enter', keyCode: 13 });
```

---

## 3. `react-dom/test-utils` 完整 API 对照表

| 旧版本 (react-dom/test-utils) | 新位置 |
|---|---|
| `act` | `import { act } from 'react'` |
| `Simulate` | `@testing-library/react` 中的 `fireEvent` |
| `renderIntoDocument` | `@testing-library/react` 中的 `render` |
| `findRenderedDOMComponentWithTag` | RTL 中的 `getByRole`, `getByTestId` |
| `findRenderedDOMComponentWithClass` | `getByRole` 或 `container.querySelector` |
| `scryRenderedDOMComponentsWithTag` | RTL 中的 `getAllByRole` |
| `isElement`, `isCompositeComponent` | 移除  使用 RTL 后不再需要 |
| `isDOMComponent` | 移除 |

---

## 4. StrictMode 调用次数修复

React 19 中的 StrictMode 在开发环境中不再双重调用 `useEffect`。用于 effect 调用计数的监视断言必须更新。

**策略：始终测量，从不猜测**
```bash
# 运行失败的测试，从错误中读取实际计数：
npm test -- --watchAll=false --testPathPattern="[filename]" --forceExit 2>&1 | grep -E "Expected|Received"
```

```jsx
// 之前 (React 18 StrictMode  effects 被调用两次)：
expect(mockFn).toHaveBeenCalledTimes(2);  // 1 次调用 × 2 (strict double-invoke)

// 之后 (React 19 StrictMode  effects 被调用一次)：
expect(mockFn).toHaveBeenCalledTimes(1);
```

```jsx
// 渲染阶段调用 (组件体)  在 React 19 StrictMode 中仍然被双重调用：
expect(renderSpy).toHaveBeenCalledTimes(2);  // 渲染体调用仍为 2
```
