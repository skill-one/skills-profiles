# @json-render/zustand

json-render 的 `StateStore` 接口所用的 Zustand 适配器。将 Zustand 原生 store 作为 json-render 的状态后端进行连接。

## 安装

```bash
npm install @json-render/zustand @json-render/core @json-render/react zustand
```

需要 Zustand v5+ 版本。由于原生 store 接口中的 API 发生了破坏性变更，Zustand v4 版本不受支持。

## 使用

```tsx
import { createStore } from "zustand/vanilla";
import { zustandStateStore } from "@json-render/zustand";
import { StateProvider } from "@json-render/react";

// 1. 创建一个 Zustand 原生 store
const bearStore = createStore(() => ({
  count: 0,
  name: "Bear",
}));

// 2. 创建 json-render 的 StateStore 适配器
const store = zustandStateStore({ store: bearStore });

// 3. 使用它
<StateProvider store={store}>
  {/* json-render 的读写操作通过 Zustand 进行 */}
</StateProvider>
```

### 带有嵌套切片

```tsx
const appStore = createStore(() => ({
  ui: { count: 0 },
  auth: { token: null },
}));

const store = zustandStateStore({
  store: appStore,
  selector: (s) => s.ui,
  updater: (next, s) => s.setState({ ui: next }),
});
```

## API

### `zustandStateStore(options)`

创建一个由 Zustand store 支持的 `StateStore`。

| 选项 | 类型 | 是否必需 | 描述 |
|------|------|----------|------|
| `store` | `StoreApi<S>` | 是 | Zustand 原生 store（来自 `zustand/vanilla` 中的 `createStore`） |
| `selector` | `(state) => StateModel` | 否 | 选择 json-render 的切片。默认为整个状态。 |
| `updater` | `(nextState, store) => void` | 否 | 将下一个状态应用到 store。默认为浅合并。用于嵌套切片时需要覆盖，或使用 `(next, s) => s.setState(next, true)` 进行完全替换。 |
