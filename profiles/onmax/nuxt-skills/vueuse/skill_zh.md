# VueUse

Vue组合式实用工具集合。在编写自定义组合式之前，请先查看VueUse——大多数模式已实现。

**当前稳定版本：** VueUse 14.x for Vue 3.5+

## 安装

**Vue 3:**

```bash
pnpm add @vueuse/core
```

**Nuxt:**

```bash
pnpm add @vueuse/nuxt @vueuse/core
```

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@vueuse/nuxt'],
})
```

Nuxt模块自动导入组合式——无需导入。

## 分类

| 分类   | 示例                                                         |
| ------ | ------------------------------------------------------------ |
| 状态   | useLocalStorage, useSessionStorage, useRefHistory            |
| 元素   | useElementSize, useIntersectionObserver, useResizeObserver |
| 浏览器  | useClipboard, useFullscreen, useMediaQuery                 |
| 传感器  | useMouse, useKeyboard, useDeviceOrientation                |
| 网络   | useFetch, useWebSocket, useEventSource                     |
| 动画   | useTransition, useInterval, useTimeout                     |
| 组件  | useVModel, useVirtualList, useTemplateRefsList             |
| 观察   | watchDebounced, watchThrottled, watchOnce                  |
| 响应性 | createSharedComposable, toRef, toReactive                  |
| 数组   | useArrayFilter, useArrayMap, useSorted                     |
| 时间   | useDateFormat, useNow, useTimeAgo                          |
| 工具   | useDebounce, useThrottle, useMemoize                       |

## 快速参考

根据您的需求加载组合式文件：

| 正在处理...      | 加载文件                                              |
| --------------- | ------------------------------------------------------ |
| 查找组合式      | [references/composables.md](references/composables.md) |
| 具体组合式      | `composables/<name>.md`                                |

## 加载文件

**根据您的任务考虑加载这些参考文件：**

- [ ] [references/composables.md](references/composables.md) - 如果按分类或功能搜索VueUse组合式

**不要一次性加载所有文件。** 只加载与您当前任务相关的文件。

## 常见模式

**状态持久化：**

```ts
const state = useLocalStorage('my-key', { count: 0 })
```

**鼠标跟踪：**

```ts
const { x, y } = useMouse()
```

**防抖引用：**

```ts
const search = ref('')
const debouncedSearch = refDebounced(search, 300)
```

**共享组合式（单例）：**

```ts
const useSharedMouse = createSharedComposable(useMouse)
```

## SSR注意事项

许多VueUse组合式使用在服务器端渲染期间不可用的浏览器API。

**使用`isClient`进行检查：**

```ts
import { isClient } from '@vueuse/core'

if (isClient) {
  // 仅浏览器代码
  const { width } = useWindowSize()
}
```

**包裹在`onMounted`中：**

```ts
const width = ref(0)

onMounted(() => {
  // 仅在浏览器中运行
  const { width: w } = useWindowSize()
  width.value = w.value
})
```

**使用SSR安全的组合式：**

```ts
// 这些内部检查isClient
const mouse = useMouse() // 在服务器上返回 {x: 0, y: 0}
const storage = useLocalStorage('key', 'default') // 在服务器上使用默认值
```

**`@vueuse/nuxt`自动处理SSR** - 组合式在服务器上返回安全的默认值。

## 目标元素引用

当针对组件引用而不是DOM元素时：

```ts
import type { MaybeElementRef } from '@vueuse/core'

// 组件引用需要 .$el 才能获取DOM元素
const compRef = ref<ComponentInstance>()
const { width } = useElementSize(compRef) // ❌ 不起作用

// 使用MaybeElementRef模式
import { unrefElement } from '@vueuse/core'

const el = computed(() => unrefElement(compRef)) // 获取 .$el
const { width } = useElementSize(el) // ✅ 起作用
```

**或者直接访问`$el`：**

```ts
const compRef = ref<ComponentInstance>()

onMounted(() => {
  const el = compRef.value?.$el as HTMLElement
  const { width } = useElementSize(el)
})
```
