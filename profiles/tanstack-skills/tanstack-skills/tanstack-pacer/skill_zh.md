## 概述

TanStack Pacer 提供了一套统一的、类型安全的工具集，用于控制函数执行时机。它提供了基于类的 API、工厂函数和 React 钩子，用于防抖、节流、速率限制、排队和批处理。

**核心:** `@tanstack/pacer`
**React:** `@tanstack/react-pacer`
**状态:** Beta

## 安装

```bash
npm install @tanstack/pacer
npm install @tanstack/react-pacer  # React 钩子
```

## 防抖

在一段无活动期后延迟执行。

### 类 API

```typescript
import { Debouncer } from '@tanstack/pacer'

const debouncer = new Debouncer(
  (query: string) => fetchSearchResults(query),
  {
    wait: 300,            // 无活动前的毫秒数后执行
    leading: false,       // 在前沿执行 (默认: false)
    trailing: true,       // 在后沿执行 (默认: true)
    maxWait: 1000,        // 连续调用 1 秒后强制执行
    enabled: true,
    onExecute: (result) => console.log(result),
  }
)

debouncer.maybeExecute('search term')
debouncer.cancel()
debouncer.getExecutionCount()
debouncer.setOptions({ wait: 500 }) // 动态重新配置
```

### 工厂函数

```typescript
import { debounce } from '@tanstack/pacer'

const debouncedSearch = debounce(
  (query: string) => fetchResults(query),
  { wait: 300 }
)

debouncedSearch('term')
debouncedSearch.cancel()
```

### React 钩子

```typescript
import {
  useDebouncer,
  useDebouncedCallback,
  useDebouncedState,
  useDebouncedValue,
} from '@tanstack/react-pacer'

// 完整的防抖实例
const debouncer = useDebouncer(fn, { wait: 300 })

// 简单的防抖函数
const debouncedFn = useDebouncedCallback(fn, { wait: 300 })

// 防抖状态管理
const [debouncedValue, setValue] = useDebouncedState(initialValue, { wait: 300 })

// 防抖响应式值
const debouncedValue = useDebouncedValue(reactiveValue, { wait: 300 })
```

## 节流

限制执行频率，每间隔最多执行一次。

### 类 API

```typescript
import { Throttler } from '@tanstack/pacer'

const throttler = new Throttler(
  (position: { x: number; y: number }) => updatePosition(position),
  {
    wait: 100,            // 执行之间的最小间隔
    leading: true,        // 第一次调用时立即执行 (默认: true)
    trailing: true,       // 间隔后使用最后参数执行 (默认: true)
    enabled: true,
    onExecute: (result) => console.log(result),
  }
)

throttler.maybeExecute({ x: 100, y: 200 })
throttler.cancel()
```

### React 钩子

```typescript
import {
  useThrottler,
  useThrottledCallback,
  useThrottledState,
  useThrottledValue,
} from '@tanstack/react-pacer'

const throttledFn = useThrottledCallback(handleScroll, { wait: 100 })
const [throttledPos, setPos] = useThrottledState({ x: 0, y: 0 }, { wait: 100 })
```

## 速率限制

在时间窗口内控制执行次数，最多执行指定次数。

### 类 API

```typescript
import { RateLimiter } from '@tanstack/pacer'

const limiter = new RateLimiter(
  async (endpoint: string) => fetch(endpoint).then(r => r.json()),
  {
    limit: 10,            // 时间窗口内的最大执行次数
    window: 60000,        // 毫秒时间窗口 (60 秒)
    enabled: true,
    onExecute: (result) => console.log(result),
    onReject: (...args) => console.warn('速率限制:', args),
  }
)

limiter.maybeExecute('/api/data')  // 超过限制时被拒绝
limiter.getExecutionCount()
limiter.getRejectionCount()
```

### React 钩子

```typescript
import {
  useRateLimiter,
  useRateLimitedCallback,
  useRateLimitedState,
  useRateLimitedValue,
} from '@tanstack/react-pacer'

const rateLimitedFn = useRateLimitedCallback(apiCall, { limit: 5, window: 1000 })
```

## 排队

可配置并发量的顺序执行。

```typescript
import { Queue } from '@tanstack/pacer'

const queue = new Queue({
  concurrency: 1,         // 最大并发任务数
  started: true,          // 立即开始处理
})

queue.add(() => uploadFile(file1))
queue.add(() => uploadFile(file2))

queue.start()
queue.pause()
queue.clear()
queue.getSize()           // 待处理计数
queue.getPending()        // 当前执行计数
```

## 批处理

将调用分组进行组合处理。

```typescript
import { Batcher } from '@tanstack/pacer'

const batcher = new Batcher(
  (items: LogEntry[]) => sendBatchToServer(items),
  {
    maxSize: 50,          // 达到 50 项时自动刷新
    wait: 1000,           // 1 秒后自动刷新
  }
)

batcher.add(logEntry)    // 累积
batcher.flush()          // 手动刷新
batcher.getSize()        // 当前批次大小
batcher.clear()          // 放弃批次
```

## 异步变体

```typescript
import { AsyncDebouncer, asyncDebounce, AsyncThrottler, asyncThrottle } from '@tanstack/pacer'

const asyncDebouncer = new AsyncDebouncer(
  async (query: string) => {
    const response = await fetch(`/api/search?q=${query}`)
    return response.json()
  },
  { wait: 300 }
)

// React 异步钩子
import { useAsyncDebouncer, useAsyncThrottler } from '@tanstack/react-pacer'
```

## 选择合适的工具

| 场景 | 工具 | 原因 |
|------|------|------|
| 搜索输入 | 防抖 | 等待用户停止输入 |
| 滚动事件 | 节流 | 活动期间周期性更新 |
| API 保护 | 速率限制 | 限制调用频率 |
| 文件上传 | 排队 | 顺序处理 |
| 分析事件 | 批处理 | 效率分组 |
| 网络请求 | AsyncDebouncer | 处理中止/重试 |

## 前沿与后沿

- **前沿** (`leading: true`): 立即执行，等待超时后抑制。适用于按钮点击。
- **后沿** (`trailing: true`): 活动停止后执行。适用于搜索输入。
- **两者**：立即执行且最终等待后执行。适用于滚动节流。

## 最佳实践

1. **使用 `maxWait` 与防抖** 保证连续活动期间的执行
2. **使用异步变体** 处理网络请求 (处理中止/取消)
3. **React 钩子自动处理清理** - 无需手动拆除
4. **使用 `setOptions`** 进行动态重新配置 (例如，为高级用户减少等待时间)
5. **组合工具** 处理复杂场景 (速率限制的排队)
6. **使用 `onReject`** 在 RateLimiter 中通知用户速率限制

## 常见陷阱

- 使用防抖时需要节流 (防抖等待无活动，节流保证周期性执行)
- 防抖未使用 `maxWait` 处理长时间连续事件
- 每次渲染创建新实例 (使用钩子或模块级)
- 非React环境忘记清理 (调用 `cancel()`)
