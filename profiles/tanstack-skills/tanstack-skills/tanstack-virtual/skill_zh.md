## 概述

TanStack Virtual 提供了虚拟化逻辑，用于仅渲染大型列表、网格和表格中的可见项。它计算哪些项位于视口内，并使用绝对定位进行定位，无论数据集大小如何，都保持 DOM 节点数量最小。

**包:** `@tanstack/react-virtual`
**核心:** `@tanstack/virtual-core` (框架无关)

## 安装

```bash
npm install @tanstack/react-virtual
```

## 核心模式

```tsx
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualList() {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: 10000,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35, // 估计的行高（像素）
    overscan: 5,
  })

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            行 {virtualItem.index}
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 虚拟化器选项

### 必填

| 选项 | 类型 | 描述 |
|------|------|------|
| `count` | `number` | 项目总数 |
| `getScrollElement` | `() => Element \| null` | 返回滚动容器 |
| `estimateSize` | `(index) => number` | 估计项目大小（建议高估） |

### 可选

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `overscan` | `number` | `1` | 视口外额外渲染的项目 |
| `horizontal` | `boolean` | `false` | 水平虚拟化 |
| `gap` | `number` | `0` | 项目之间的间隙（像素） |
| `lanes` | `number` | `1` | 轨道数量（马赛克/网格） |
| `paddingStart` | `number` | `0` | 第一个项目前的填充 |
| `paddingEnd` | `number` | `0` | 最后一个项目后的填充 |
| `scrollPaddingStart` | `number` | `0` | scrollTo 定位的偏移量 |
| `scrollPaddingEnd` | `number` | `0` | scrollTo 定位的偏移量 |
| `initialOffset` | `number` | `0` | 起始滚动位置 |
| `initialRect` | `Rect` | - | 初始尺寸（服务器端渲染） |
| `enabled` | `boolean` | `true` | 启用/禁用 |
| `getItemKey` | `(index) => Key` | `(i) => i` | 项目的稳定键 |
| `rangeExtractor` | `(range) => number[]` | 默认 | 自定义可见索引 |
| `scrollToFn` | `(offset, options, instance) => void` | 默认 | 自定义滚动行为 |
| `measureElement` | `(el, entry, instance) => number` | 默认 | 自定义测量 |
| `onChange` | `(instance, sync) => void` | - | 状态变化回调 |
| `isScrollingResetDelay` | `number` | `150` | 滚动完成前的延迟 |

## 虚拟化器 API

```typescript
// 获取可见项
virtualizer.getVirtualItems(): VirtualItem[]

// 获取总滚动尺寸
virtualizer.getTotalSize(): number

// 滚动到特定索引
virtualizer.scrollToIndex(index, { align: 'start' | 'center' | 'end' | 'auto', behavior: 'auto' | 'smooth' })

// 滚动到偏移量
virtualizer.scrollToOffset(offset, options)

// 强制重新计算
virtualizer.measure()
```

## VirtualItem 属性

```typescript
interface VirtualItem {
  key: Key           // 唯一键
  index: number      // 源数据中的索引
  start: number      // 像素偏移量（用于 transform）
  end: number        // 结束像素偏移量
  size: number       // 项目尺寸
  lane: number       // 轨道索引（多列）
}
```

## 动态/可变高度

使用 `measureElement` 引用未知高度的项目：

```tsx
const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 50, // 高估
})

{virtualizer.getVirtualItems().map((virtualItem) => (
  <div
    key={virtualItem.key}
    data-index={virtualItem.index}  // 必须用于测量
    ref={virtualizer.measureElement} // 用于动态测量
    style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      transform: `translateY(${virtualItem.start}px)`,
      // 不要设置固定高度 - 让内容决定它
    }}
  >
    {items[virtualItem.index].content}
  </div>
))}
```

## 水平虚拟化

```tsx
const virtualizer = useVirtualizer({
  count: columns.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 100,
  horizontal: true,
})

// 使用宽度作为容器，translateX 用于定位
<div style={{ width: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
  {virtualizer.getVirtualItems().map((item) => (
    <div style={{
      position: 'absolute',
      height: '100%',
      width: `${item.size}px`,
      transform: `translateX(${item.start}px)`,
    }}>
      列 {item.index}
    </div>
  ))}
</div>
```

## 网格虚拟化（两个虚拟化器）

```tsx
function VirtualGrid() {
  const parentRef = useRef<HTMLDivElement>(null)

  const rowVirtualizer = useVirtualizer({
    count: 10000,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 5,
  })

  const columnVirtualizer = useVirtualizer({
    count: 10000,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
    horizontal: true,
    overscan: 5,
  })

  return (
    <div ref={parentRef} style={{ height: '500px', width: '500px', overflow: 'auto' }}>
      <div style={{
        height: `${rowVirtualizer.getTotalSize()}px`,
        width: `${columnVirtualizer.getTotalSize()}px`,
        position: 'relative',
      }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <Fragment key={virtualRow.key}>
            {columnVirtualizer.getVirtualItems().map((virtualColumn) => (
              <div
                key={virtualColumn.key}
                style={{
                  position: 'absolute',
                  width: `${virtualColumn.size}px`,
                  height: `${virtualRow.size}px`,
                  transform: `translateX(${virtualColumn.start}px) translateY(${virtualRow.start}px)`,
                }}
              >
                单元格 {virtualRow.index},{virtualColumn.index}
              </div>
            ))}
          </Fragment>
        ))}
      </div>
    </div>
  )
}
```

## 窗口滚动

```tsx
import { useWindowVirtualizer } from '@tanstack/react-virtual'

function WindowList() {
  const listRef = useRef<HTMLDivElement>(null)

  const virtualizer = useWindowVirtualizer({
    count: 10000,
    estimateSize: () => 45,
    overscan: 5,
    scrollMargin: listRef.current?.offsetTop ?? 0,
  })

  return (
    <div ref={listRef}>
      <div style={{
        height: `${virtualizer.getTotalSize()}px`,
        position: 'relative',
      }}>
        {virtualizer.getVirtualItems().map((item) => (
          <div
            key={item.key}
            style={{
              position: 'absolute',
              height: `${item.size}px`,
              transform: `translateY(${item.start - virtualizer.options.scrollMargin}px)`,
            }}
          >
            行 {item.index}
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 无限滚动

```tsx
import { useVirtualizer } from '@tanstack/react-virtual'
import { useInfiniteQuery } from '@tanstack/react-query'

function InfiniteList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['items'],
    queryFn: ({ pageParam = 0 }) => fetchItems(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })

  const allItems = data?.pages.flatMap((page) => page.items) ?? []

  const virtualizer = useVirtualizer({
    count: hasNextPage ? allItems.length + 1 : allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  })

  useEffect(() => {
    const items = virtualizer.getVirtualItems()
    const lastItem = items[items.length - 1]
    if (lastItem && lastItem.index >= allItems.length - 1 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage()
    }
  }, [virtualizer.getVirtualItems(), hasNextPage, isFetchingNextPage, allItems.length])

  // 渲染虚拟项，如果正在加载，则为最后一项显示加载行
}
```

## 粘性项

```tsx
import { defaultRangeExtractor, Range } from '@tanstack/react-virtual'

const stickyIndexes = [0, 10, 20, 30] // 头部索引

const virtualizer = useVirtualizer({
  count: 1000,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 50,
  rangeExtractor: useCallback((range: Range) => {
    const next = new Set([...stickyIndexes, ...defaultRangeExtractor(range)])
    return [...next].sort((a, b) => a - b)
  }, [stickyIndexes]),
})

// 渲染粘性项，使用 position: sticky; top: 0; zIndex: 1
```

## 平滑滚动

```tsx
const virtualizer = useVirtualizer({
  scrollToFn: (offset, { behavior }, instance) => {
    if (behavior === 'smooth') {
      // 自定义缓动动画
      instance.scrollElement?.scrollTo({ top: offset, behavior: 'smooth' })
    } else {
      instance.scrollElement?.scrollTo({ top: offset })
    }
  },
})

// 使用
virtualizer.scrollToIndex(500, { align: 'center', behavior: 'smooth' })
```

## 最佳实践

1. **高估 `estimateSize`** - 防止滚动跳跃（项目缩小会导致问题）
2. **增加 `overscan`** (3-5) 以减少快速滚动时的空白闪烁
3. **使用 `transform: translateY()`** 而不是 `top` 进行 GPU 合成定位
4. **添加 `data-index` 属性** 当使用 `measureElement` 进行动态尺寸时
5. **不要在动态测量的项目上设置固定高度**
6. **使用 `getItemKey`** 当项目可以重新排序时
7. **使用 `gap` 选项** 而不是边距（边距会干扰测量）
8. **使用 `paddingStart/End`** 而不是容器的 CSS 填充
9. **使用 `enabled: false`** 当列表隐藏时暂停
10. **记忆化回调** (`estimateSize`, `getItemKey`, `rangeExtractor`)
11. **在项目上使用 CSS `will-change: transform`** 以实现 GPU 加速

## 常见陷阱

- 在动态测量的项目上设置固定高度
- 使用 CSS 边距而不是 `gap` 选项
- 忘记 `data-index` 与 `measureElement`
- 忘记在内部容器上提供 `position: relative`
- 低估 `estimateSize`（导致滚动跳跃）
- 设置 `overscan` 太低（快速滚动时出现空白项）
- 在窗口滚动中忘记减去 `scrollMargin` 从 `translateY`
- 不记忆化 `estimateSize` 函数（导致重新渲染）
