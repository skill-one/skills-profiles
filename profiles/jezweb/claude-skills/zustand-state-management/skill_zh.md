# Zustand 状态管理

**最后更新**: 2026-01-21
**最新版本**: zustand@5.0.10 (发布于 2026-01-12)
**依赖**: React 18-19, TypeScript 5+

---

## 快速入门

```bash
npm install zustand
```

**TypeScript Store** (关键：使用 `create<T>()()` 双括号):
```typescript
import { create } from 'zustand'

interface BearStore {
  bears: number
  increase: (by: number) => void
}

const useBearStore = create<BearStore>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}))
```

**在组件中使用**:
```tsx
const bears = useBearStore((state) => state.bears)  // 仅在 bears 变化时重新渲染
const increase = useBearStore((state) => state.increase)
```

---

## 核心模式

**基本 Store** (JavaScript):
```javascript
const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))
```

**TypeScript Store** (推荐):
```typescript
interface CounterStore { count: number; increment: () => void }
const useStore = create<CounterStore>()((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))
```

**持久化 Store** (跨页面刷新存活):
```typescript
import { persist, createJSONStorage } from 'zustand/middleware'

const useStore = create<UserPreferences>()(
  persist(
    (set) => ({ theme: 'system', setTheme: (theme) => set({ theme }) }),
    { name: 'user-preferences', storage: createJSONStorage(() => localStorage) },
  ),
)
```

---

## 关键规则

### 必须做

✅ 在 TypeScript 中使用 `create<T>()()` (双括号) 以兼容中间件
✅ 为状态和操作定义分离的接口
✅ 使用选择器函数提取特定状态片段
✅ 使用 `set` 与更新器函数处理派生状态: `set((state) => ({ count: state.count + 1 }))`
✅ 为持久化中间件存储键使用唯一名称
✅ 使用 `hasHydrated` 标志模式处理 Next.js 缓存
✅ 使用 `useShallow` 钩子选择多个值
✅ 保持操作纯净 (除状态更新外无副作用)

### 绝对不要

❌ 在 TypeScript 中使用 `create<T>(...)` (单括号) - 会破坏中间件类型
❌ 直接修改状态: `set((state) => { state.count++; return state })` - 使用不可变更新
❌ 在选择器中创建新对象: `useStore((state) => ({ a: state.a }))` - 导致无限渲染
❌ 对多个 Store 使用相同存储名 - 导致数据冲突
❌ 在 SSR 期间未进行缓存检查时访问 localStorage
❌ 使用 Zustand 处理服务器状态 - 使用 TanStack Query 代替
❌ 直接导出 Store 实例 - 始终导出钩子

---

## 已知问题预防

此技能可预防 **6** 个已知问题:

### 问题 #1: Next.js 缓存不匹配

**错误**: `"Text content does not match server-rendered HTML"` 或 `"Hydration failed"`

**来源**:
- [DEV Community: Next.js 中的持久化中间件](https://dev.to/abdulsamad/how-to-use-zustands-persist-middleware-in-nextjs-4lb5)
- GitHub 讨论区 #2839

**原因**:
持久化中间件在客户端从 localStorage 读取但在服务器上不读取，导致状态不匹配。

**预防**:
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface StoreWithHydration {
  count: number
  _hasHydrated: boolean
  setHasHydrated: (hydrated: boolean) => void
  increase: () => void
}

const useStore = create<StoreWithHydration>()(
  persist(
    (set) => ({
      count: 0,
      _hasHydrated: false,
      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),
      increase: () => set((state) => ({ count: state.count + 1 })),
    }),
    {
      name: 'my-store',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    },
  ),
)

// 在组件中
function MyComponent() {
  const hasHydrated = useStore((state) => state._hasHydrated)

  if (!hasHydrated) {
    return <div>加载中...</div>
  }

  // 现在可以安全地渲染持久化状态
  return <ActualContent />
}
```

### 问题 #2: TypeScript 双括号缺失

**错误**: 类型推断失败，`StateCreator` 类型与中间件冲突

**来源**: [官方 Zustand TypeScript 指南](https://zustand.docs.pmnd.rs/guides/typescript)

**原因**:
需要使用柯里化语法 `create<T>()()` 才能让中间件与 TypeScript 推断兼容。

**预防**:
```typescript
// ❌ 错误 - 单括号
const useStore = create<MyStore>((set) => ({
  // ...
}))

// ✅ 正确 - 双括号
const useStore = create<MyStore>()((set) => ({
  // ...
}))
```

**规则**: 即使没有中间件，TypeScript 中也始终使用 `create<T>()()` (为未来做准备)。

### 问题 #3: 持久化中间件导入错误

**错误**: `"Attempted import error: 'createJSONStorage' is not exported from 'zustand/middleware'"`

**来源**: GitHub 讨论区 #2839

**原因**:
导入路径错误或 zustand 与构建工具版本不匹配。

**预防**:
```typescript
// ✅ 正确的 v5 导入
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

// 验证版本
// zustand@5.0.9 包含 createJSONStorage
// zustand@4.x 使用不同 API

// 检查你的 package.json
// "zustand": "^5.0.9"
```

### 问题 #4: 无限渲染循环

**错误**: 组件无限渲染，浏览器卡死
```
Uncaught Error: Maximum update depth exceeded. This can happen when a component repeatedly calls setState inside componentWillUpdate or componentDidUpdate.
```

**来源**:
- GitHub 讨论区 #2642
- [Issue #2863](https://github.com/pmndrs/zustand/issues/2863)

**原因**:
在选择器中创建新的对象引用会导致 Zustand 认为状态已更改。

**v5 版本变更**: Zustand v5 使此错误比 v4 更明显。在 v4 中，此行为是"非理想"但可能未被注意到。在 v5 中，你会立即看到"Maximum update depth exceeded"错误。

**预防**:
```typescript
import { useShallow } from 'zustand/shallow'

// ❌ 错误 - 每次创建新的对象
const { bears, fishes } = useStore((state) => ({
  bears: state.bears,
  fishes: state.fishes,
}))

// ✅ 正确选项 1 - 分开选择原始值
const bears = useStore((state) => state.bears)
const fishes = useStore((state) => state.fishes)

// ✅ 正确选项 2 - 使用 useShallow 钩子选择多个值
const { bears, fishes } = useStore(
  useShallow((state) => ({ bears: state.bears, fishes: state.fishes }))
)
```

### 问题 #5: 切片模式 TypeScript 复杂性

**错误**: `StateCreator` 类型无法推断，复杂中间件类型破坏

**来源**: [官方切片模式指南](https://github.com/pmndrs/zustand/blob/main/docs/guides/slices-pattern.md)

**原因**:
组合多个切片需要为中间件兼容性显式声明类型。

**预防**:
```typescript
import { create, StateCreator } from 'zustand'

// 定义切片类型
interface BearSlice {
  bears: number
  addBear: () => void
}

interface FishSlice {
  fishes: number
  addFish: () => void
}

// 使用正确类型创建切片
const createBearSlice: StateCreator<
  BearSlice & FishSlice,  // 合并的 Store 类型
  [],                      // 中间件可变函数 (如果没有则为空)
  [],                      // 链接的中间件 (如果没有则为空)
  BearSlice               // 此切片的类型
> = (set) => ({
  bears: 0,
  addBear: () => set((state) => ({ bears: state.bears + 1 })),
})

const createFishSlice: StateCreator<
  BearSlice & FishSlice,
  [],
  [],
  FishSlice
> = (set) => ({
  fishes: 0,
  addFish: () => set((state) => ({ fishes: state.fishes + 1 })),
})

// 合并切片
const useStore = create<BearSlice & FishSlice>()((...a) => ({
  ...createBearSlice(...a),
  ...createFishSlice(...a),
}))
```

### 问题 #6: 持久化中间件竞态条件 (v5.0.10+ 已修复)

**错误**: 并发缓存尝试期间状态不一致

**来源**:
- [GitHub PR #3336](https://github.com/pmndrs/zustand/pull/3336)
- [v5.0.10 发布](https://github.com/pmndrs/zustand/releases/tag/v5.0.10)

**原因**:
在 Zustand v5.0.9 及更早版本中，持久化中间件初始化期间并发缓存调用会导致竞态条件，多个缓存尝试会相互干扰，导致状态不一致。

**预防**:
升级到 Zustand v5.0.10 或更高版本。无需代码更改 - 修复是持久化中间件内部的。

```bash
npm install zustand@latest  # 确保使用 v5.0.10+
```

**注意**: 此问题已在 v5.0.10 (2026 年 1 月) 中修复。如果你使用 v5.0.9 或更早版本且在持久化中间件中遇到状态不一致，请立即升级。

---

## 中间件

**持久化** (localStorage):
```typescript
import { persist, createJSONStorage } from 'zustand/middleware'

const useStore = create<MyStore>()(
  persist(
    (set) => ({ data: [], addItem: (item) => set((state) => ({ data: [...state.data, item] })) }),
    {
      name: 'my-storage',
      partialize: (state) => ({ data: state.data }),  // 仅持久化 'data'
    },
  ),
)
```

**Devtools** (Redux DevTools):
```typescript
import { devtools } from 'zustand/middleware'

const useStore = create<CounterStore>()(
  devtools(
    (set) => ({ count: 0, increment: () => set((s) => ({ count: s.count + 1 }), undefined, 'increment') }),
    { name: 'CounterStore' },
  ),
)
```

**v4→v5 迁移说明**: 在 Zustand v4 中，devtools 从 `'zustand/middleware/devtools'` 导入。在 v5 中，使用 `'zustand/middleware'` (如上所示)。如果你看到"Module not found: Can't resolve 'zustand/middleware/devtools'"，请更新你的导入路径。

**组合中间件** (顺序重要):
```typescript
const useStore = create<MyStore>()(devtools(persist((set) => ({ /* ... */ }), { name: 'storage' }), { name: 'MyStore' }))
```

---

## 常见模式

**计算/派生值** (在选择器中，不存储):
```typescript
const count = useStore((state) => state.items.length)  // 读取时计算
```

**异步操作**:
```typescript
const useAsyncStore = create<AsyncStore>()((set) => ({
  data: null,
  isLoading: false,
  fetchData: async () => {
    set({ isLoading: true })
    const response = await fetch('/api/data')
    set({ data: await response.text(), isLoading: false })
  },
}))
```

**重置 Store**:
```typescript
const initialState = { count: 0, name: '' }
const useStore = create<ResettableStore>()((set) => ({
  ...initialState,
  reset: () => set(initialState),
}))
```

**带参数的选择器**:
```typescript
const todo = useStore((state) => state.todos.find((t) => t.id === id))
```

---

## 打包资源

**模板**: `basic-store.ts`, `typescript-store.ts`, `persist-store.ts`, `slices-pattern.ts`, `devtools-store.ts`, `nextjs-store.ts`, `computed-store.ts`, `async-actions-store.ts`

**参考**: `middleware-guide.md` (持久化/devtools/immer/自定义), `typescript-patterns.md` (类型推断问题), `nextjs-hydration.md` (SSR/缓存), `migration-guide.md` (从 Redux/Context/v4 迁移)

**脚本**: `check-versions.sh` (版本兼容性)

---

## 高级主题

**Vanilla Store** (无 React):
```typescript
import { createStore } from 'zustand/vanilla'

const store = createStore<CounterStore>()((set) => ({ count: 0, increment: () => set((s) => ({ count: s.count + 1 })) }))
const unsubscribe = store.subscribe((state) => console.log(state.count))
store.getState().increment()
```

**自定义中间件**:
```typescript
const logger: Logger = (f, name) => (set, get, store) => {
  const loggedSet: typeof set = (...a) => { set(...a); console.log(`[${name}]:`, get()) }
  return f(loggedSet, get, store)
}
```

**Immer 中间件** (可变更新):
```typescript
import { immer } from 'zustand/middleware/immer'

const useStore = create<TodoStore>()(immer((set) => ({
  todos: [],
  addTodo: (text) => set((state) => { state.todos.push({ id: Date.now().toString(), text }) }),
})))
```

**v5.0.3→v5.0.4 迁移说明**: 如果从 v5.0.3 升级到 v5.0.4+ 且 immer 中间件停止工作，请确认使用上述正确的导入路径 (`zustand/middleware/immer`)。一些用户报告 v5.0.4 更新后出现的问题通过确认正确导入得到解决。

**实验性 SSR 安全中间件** (v5.0.9+):

**状态**: 实验性 (API 可能会变化)

Zustand v5.0.9 引入了实验性 `unstable_ssrSafe` 中间件用于 Next.js 使用。这为 `_hasHydrated` 模式 (见问题 #1) 提供了替代方法。

```typescript
import { unstable_ssrSafe } from 'zustand/middleware'

const useStore = create<Store>()(
  unstable_ssrSafe(
    persist(
      (set) => ({ /* state */ }),
      { name: 'my-store' }
    )
  )
)
```

**建议**: 继续使用文档中 Issue #1 中记录的 `_hasHydrated` 模式，直到此 API 稳定。监控 [讨论 #2740](https://github.com/pmndrs/zustand/discussions/2740) 以了解何时此 API 将会稳定。

---

## 官方文档

- **Zustand**: https://zustand.docs.pmnd.rs/
- **GitHub**: https://github.com/pmndrs/zustand
- **TypeScript 指南**: https://zustand.docs.pmnd.rs/guides/typescript
- **Context7 库 ID**: `/pmndrs/zustand`
