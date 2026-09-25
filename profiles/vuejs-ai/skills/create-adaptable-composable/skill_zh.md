# 创建可适应的组合式函数

可适应的组合式函数是可重用的函数，它们可以接受响应式和非响应式的输入。这使得开发人员能够在各种上下文中使用组合式函数，而无需担心输入的响应性。

在 Vue.js 中设计可适应的组合式函数的步骤：
1. 确认组合式函数的用途、API 设计以及预期的输入/输出。
2. 确定哪些输入参数应该是响应式的（MaybeRef / MaybeRefOrGetter）。
3. 在响应式效果内部使用 `toValue()` 或 `toRef()` 来规范化输入。
4. 使用 Vue 的响应性 API 实现组合式函数的核心逻辑。

## 核心类型概念

### 类型工具

```ts
/**
 * 值或可写的响应式引用（值/引用/浅响应式引用/可写计算属性）
 */
export type MaybeRef<T = any> = T | Ref<T> | ShallowRef<T> | WritableComputedRef<T>;

/**
 * MaybeRef<T> + ComputedRef<T> + () => T
 */
export type MaybeRefOrGetter<T = any> = MaybeRef<T> | ComputedRef<T> | (() => T);
```

### 策略和规则

- 只读、适用于计算属性的输入：使用 `MaybeRefOrGetter`
- 需要是可写的/双向输入：使用 `MaybeRef`
- 参数可能是一个函数值（回调/谓词/比较器）：不要使用 `MaybeRefOrGetter`，否则可能会意外地将其作为获取器调用。
- DOM/元素目标：如果你需要计算/派生目标，使用 `MaybeRefOrGetter`。

当使用 `MaybeRefOrGetter` 或 `MaybeRef` 时：
- 使用 `toRef()` 解析响应式值（例如，观察者源）
- 使用 `toValue()` 解析非响应式值

### 示例

可适应的 `useDocumentTitle` 组合式函数：只读标题参数

```ts
import { watch, toRef } from 'vue'
import type { MaybeRefOrGetter } from 'vue'

export function useDocumentTitle(title: MaybeRefOrGetter<string>) {
  watch(toRef(title), (t) => {
    document.title = t
  }, { immediate: true })
}
```

可适应的 `useCounter` 组合式函数：双向可写的计数参数

```ts
import { watch, toRef } from 'vue'
import type { MaybeRef } from 'vue'

function useCounter(count: MaybeRef<number>) {
  const countRef = toRef(count)
  function add() {
    countRef.value++
  }
  return { add }
}
```
