## 概述

TanStack Store 是一个轻量级的响应式存储（类似 signals），为 TanStack 库的内部功能提供支持。它提供 `Store` 用于状态管理，`Derived` 用于计算值，`Effect` 用于副作用，以及 `batch` 用于原子更新。框架适配器提供响应式钩子。

**核心:** `@tanstack/store`
**React:** `@tanstack/react-store`

## 安装

```bash
npm install @tanstack/store @tanstack/react-store
```

## 存储

### 创建存储

```typescript
import { Store } from '@tanstack/store'

const countStore = new Store(0)

const userStore = new Store<{ name: string; email: string }>({
  name: 'Alice',
  email: 'alice@example.com',
})
```

### 更新状态

```typescript
// 函数更新器（不可变更新）
countStore.setState((prev) => prev + 1)

userStore.setState((prev) => ({ ...prev, name: 'Bob' }))
```

### 订阅变更

```typescript
const unsub = countStore.subscribe(() => {
  console.log('Count:', countStore.state)
})

// 清理
unsub()
```

### 存储选项

```typescript
const store = new Store(initialState, {
  // 自定义更新函数
  updateFn: (prevValue) => (updater) => {
    return updater(prevValue) // 自定义逻辑
  },
  // 订阅时的回调
  onSubscribe: (listener, store) => {
    console.log('New subscriber')
    return () => console.log('Unsubscribed')
  },
  // 每次更新时的回调
  onUpdate: () => {
    console.log('State updated:', store.state)
  },
})
```

### 存储属性

```typescript
store.state      // 当前状态
store.prevState  // 上一个状态
store.listeners  // 订阅回调集合
```

## Derived（计算值）

```typescript
import { Store, Derived } from '@tanstack/store'

const count = new Store(5)
const multiplier = new Store(2)

const doubled = new Derived({
  deps: [count, multiplier],
  fn: ({ currDepVals }) => currDepVals[0] * currDepVals[1],
})

// MUST mount to activate
const unmount = doubled.mount()

console.log(doubled.state) // 10

count.setState(() => 10)
console.log(doubled.state) // 20

// 清理
unmount()
```

### Derived 与上一个值

```typescript
const accumulated = new Derived({
  deps: [count],
  fn: ({ prevVal, currDepVals }) => {
    return currDepVals[0] + (prevVal ?? 0)
  },
})
```

### 链式 Derived

```typescript
const filtered = new Derived({
  deps: [dataStore, filterStore],
  fn: ({ currDepVals }) => currDepVals[0].filter(matchesFilter(currDepVals[1])),
})

const sorted = new Derived({
  deps: [filtered, sortStore],
  fn: ({ currDepVals }) => [...currDepVals[0]].sort(comparator(currDepVals[1])),
})

const paginated = new Derived({
  deps: [sorted, pageStore],
  fn: ({ currDepVals }) => currDepVals[0].slice(
    currDepVals[1].offset,
    currDepVals[1].offset + currDepVals[1].limit,
  ),
})
```

## Effect（副作用）

```typescript
import { Store, Effect } from '@tanstack/store'

const count = new Store(0)

const logger = new Effect({
  deps: [count],
  fn: () => {
    console.log('Count changed:', count.state)
    // 可选地返回清理函数
    return () => console.log('Cleaning up')
  },
  eager: false, // true = 挂载时立即执行
})

const unmount = logger.mount()

count.setState(() => 1) // 记录: "Count changed: 1"

unmount()
```

### Effect 带有清理

```typescript
const timerEffect = new Effect({
  deps: [intervalStore],
  fn: () => {
    const id = setInterval(() => { /* ... */ }, intervalStore.state)
    return () => clearInterval(id) // 在下次运行或卸载时清理
  },
})
```

## Batch

将多个更新组合为一次通知：

```typescript
import { batch } from '@tanstack/store'

// 订阅者只会在最终状态时触发一次
batch(() => {
  countStore.setState(() => 1)
  nameStore.setState(() => 'Alice')
  settingsStore.setState((prev) => ({ ...prev, theme: 'dark' }))
})
```

## React 集成

### useStore 钩子

```tsx
import { useStore } from '@tanstack/react-store'

// 订阅完整状态
function Counter() {
  const count = useStore(countStore)
  return <button onClick={() => countStore.setState((c) => c + 1)}>{count}</button>
}

// 带有选择器的订阅（性能优化）
function UserName() {
  const name = useStore(userStore, (state) => state.name)
  return <span>{name}</span>
}

// 订阅 Derived
function DoubledDisplay() {
  const value = useStore(doubledDerived)
  return <span>{value}</span>
}
```

### 浅比较函数

当选择器返回结构上相等的对象时防止重新渲染：

```tsx
import { useStore } from '@tanstack/react-store'
import { shallow } from '@tanstack/react-store'

function TodoList() {
  // 没有 shallow: 任何状态变更都会重新渲染（新的对象引用）
  // 带有 shallow: 只有实际变更时才重新渲染
  const items = useStore(todosStore, (state) => state.items, shallow)
  return <ul>{items.map(/* ... */)}</ul>
}
```

### 在 React 中挂载 Derived/Effect

```tsx
function MyComponent() {
  useEffect(() => {
    const unmountDerived = myDerived.mount()
    const unmountEffect = myEffect.mount()
    return () => {
      unmountDerived()
      unmountEffect()
    }
  }, [])

  const value = useStore(myDerived)
  return <span>{value}</span>
}
```

## 模块级存储模式

```typescript
// stores/counter.ts
import { Store, Derived } from '@tanstack/store'

export const counterStore = new Store(0)

export const doubledCount = new Derived({
  deps: [counterStore],
  fn: ({ currDepVals }) => currDepVals[0] * 2,
})

// 行为作为普通函数
export function increment() {
  counterStore.setState((c) => c + 1)
}

export function reset() {
  counterStore.setState(() => 0)
}
```

## 框架适配器

| 框架 | 包 | 钩子/组合器 |
|-------|-----|------------|
| React | `@tanstack/react-store` | `useStore(store, selector?, equalityFn?)` |
| Vue | `@tanstack/vue-store` | `useStore(store, selector?)`（返回计算引用） |
| Solid | `@tanstack/solid-store` | `useStore(store, selector?)`（返回信号） |
| Angular | `@tanstack/angular-store` | `injectStore(store, selector?)`（返回信号） |
| Svelte | `@tanstack/svelte-store` | `useStore(store, selector?)`（返回 $state） |

## 最佳实践

1. **在模块级别定义存储** - 它们是单例的
2. **在 `useStore` 中使用选择器** - 防止不必要的重新渲染
3. **使用 `shallow`** 当选择器返回对象/数组时
4. **始终调用 `mount()`** 在 Derived 和 Effect 实例上
5. **始终清理** 卸载函数（尤其是在 React useEffect 中）
6. **不要直接修改状态** - 始终使用 `setState`
7. **使用 `batch`** 进行多个相关更新
8. **使用 Derived 链** 进行数据转换（过滤 -> 排序 -> 分页）
9. **从 Effect `fn` 返回清理函数** 用于计时器/监听器
10. **尽可能选择原始类型**（不需要相等函数）

## 常见陷阱

- 忘记调用 `mount()` Derived/Effect（它们不会激活）
- 不清理订阅/卸载函数（内存泄漏）
- 直接修改 `store.state` 而不是使用 `setState`
- 在选择器中创建新的对象引用而不使用 `shallow`
- 使用 `useStore` 而没有选择器（订阅所有内容）
- 忘记 `eager: true` 当 Effect 应该立即执行时
