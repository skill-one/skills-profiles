## 概述

TanStack Ranger 提供了用于构建完全可访问的范围和多范围滑块组件的无头工具。它处理单值、范围和多滑块的所有复杂逻辑，同时让您完全控制样式和标记。

**包名：** `@tanstack/react-ranger`
**核心：** `@tanstack/ranger-core`（框架无关）
**状态：** 稳定

## 安装

```bash
npm install @tanstack/react-ranger
```

## 核心模式

```tsx
import { useRanger } from '@tanstack/react-ranger'

function RangeSlider() {
  const [values, setValues] = useState([25, 75])

  const rangerInstance = useRanger({
    getRangerElement: () => rangerRef.current,
    values,
    min: 0,
    max: 100,
    stepSize: 1,
    onChange: (instance) => setValues(instance.sortedValues),
  })

  const rangerRef = useRef<HTMLDivElement>(null)

  return (
    <div
      ref={rangerRef}
      style={{
        position: 'relative',
        height: '8px',
        background: '#ddd',
        borderRadius: '4px',
        width: '100%',
      }}
    >
      {/* 轨道段 */}
      {rangerInstance.getSteps().map(({ left, width }, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: `${left}%`,
            width: `${width}%`,
            height: '100%',
            background: i === 1 ? '#3b82f6' : '#ddd',
            borderRadius: '4px',
          }}
        />
      ))}

      {/* 滑块 */}
      {rangerInstance.handles.map((handle, i) => (
        <button
          key={i}
          {...handle.getHandleProps()}
          style={{
            position: 'absolute',
            left: `${handle.getPercentage()}%`,
            transform: 'translateX(-50%)',
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            background: '#3b82f6',
            border: '2px solid white',
            cursor: 'grab',
          }}
        />
      ))}
    </div>
  )
}
```

## Ranger 选项

### 必填

| 选项 | 类型 | 描述 |
|------|------|------|
| `getRangerElement` | `() => Element \| null` | 返回滑块轨道元素 |
| `values` | `number[]` | 当前滑块值 |
| `min` | `number` | 最小值 |
| `max` | `number` | 最大值 |
| `onChange` | `(instance) => void` | 值变化时调用 |

### 可选

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `stepSize` | `number` | `1` | 值之间的步长增量 |
| `steps` | `number[]` | - | 自定义步长位置（覆盖 stepSize） |
| `tickSize` | `number` | - | 刻度标记大小 |
| `ticks` | `number[]` | - | 自定义刻度位置 |
| `interpolator` | `Interpolator` | linear | 值插值函数 |
| `onDrag` | `(instance) => void` | - | 拖动操作期间调用 |

## Ranger 实例 API

```typescript
// 获取排序后的值（始终为升序）
rangerInstance.sortedValues: number[]

// 获取用于渲染滑块的滑块句柄
rangerInstance.handles: Handle[]

// 获取滑块之间的轨道段
rangerInstance.getSteps(): { left: number; width: number }[]

// 获取刻度标记
rangerInstance.getTicks(): { value: number; percentage: number }[]

// 程序化设置值
rangerInstance.setValues(newValues: number[])
```

## 滑块句柄 API

```typescript
interface Handle {
  // 获取轨道上的百分比位置（0-100）
  getPercentage(): number

  // 获取当前值
  getValue(): number

  // 获取要传播到滑块元素上的属性
  getHandleProps(): {
    role: 'slider'
    tabIndex: number
    'aria-valuemin': number
    'aria-valuemax': number
    'aria-valuenow': number
    onKeyDown: (e: KeyboardEvent) => void
    onMouseDown: (e: MouseEvent) => void
    onTouchStart: (e: TouchEvent) => void
  }
}
```

## 单值滑块

```tsx
function SingleSlider() {
  const [values, setValues] = useState([50])

  const rangerInstance = useRanger({
    getRangerElement: () => rangerRef.current,
    values,
    min: 0,
    max: 100,
    stepSize: 1,
    onChange: (instance) => setValues(instance.sortedValues),
  })

  const rangerRef = useRef<HTMLDivElement>(null)

  return (
    <div ref={rangerRef} className="slider-track">
      {rangerInstance.handles.map((handle, i) => (
        <button key={i} {...handle.getHandleProps()} className="slider-thumb">
          {handle.getValue()}
        </button>
      ))}
    </div>
  )
}
```

## 多范围滑块

```tsx
function MultiRangeSlider() {
  const [values, setValues] = useState([10, 40, 60, 90])

  const rangerInstance = useRanger({
    getRangerElement: () => rangerRef.current,
    values,
    min: 0,
    max: 100,
    stepSize: 5,
    onChange: (instance) => setValues(instance.sortedValues),
  })

  const rangerRef = useRef<HTMLDivElement>(null)

  return (
    <div ref={rangerRef} className="slider-track">
      {rangerInstance.getSteps().map(({ left, width }, i) => (
        <div
          key={i}
          className={`segment ${i % 2 === 1 ? 'active' : ''}`}
          style={{ left: `${left}%`, width: `${width}%` }}
        />
      ))}
      {rangerInstance.handles.map((handle, i) => (
        <button key={i} {...handle.getHandleProps()} className="slider-thumb" />
      ))}
    </div>
  )
}
```

## 自定义步长

```tsx
const rangerInstance = useRanger({
  getRangerElement: () => rangerRef.current,
  values,
  min: 0,
  max: 100,
  steps: [0, 10, 25, 50, 75, 100], // 仅允许这些值
  onChange: (instance) => setValues(instance.sortedValues),
})
```

## 刻度标记

```tsx
function SliderWithTicks() {
  const rangerInstance = useRanger({
    getRangerElement: () => rangerRef.current,
    values,
    min: 0,
    max: 100,
    stepSize: 10,
    ticks: [0, 25, 50, 75, 100],
    onChange: (instance) => setValues(instance.sortedValues),
  })

  return (
    <div>
      <div ref={rangerRef} className="slider-track">
        {/* 滑块 */}
      </div>
      <div className="tick-container">
        {rangerInstance.getTicks().map((tick, i) => (
          <div
            key={i}
            style={{ left: `${tick.percentage}%` }}
            className="tick"
          >
            <span className="tick-label">{tick.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 对数刻度

```tsx
import { logarithmicInterpolator } from '@tanstack/react-ranger'

const rangerInstance = useRanger({
  getRangerElement: () => rangerRef.current,
  values,
  min: 1,
  max: 1000,
  interpolator: logarithmicInterpolator,
  onChange: (instance) => setValues(instance.sortedValues),
})
```

## 可访问性

TanStack Ranger 提供了内置的可访问性：

- 滑块上使用 `role="slider"`
- `aria-valuemin`、`aria-valuemax`、`aria-valuenow` 属性
- 键盘导航（箭头键、Home、End、Page Up/Down）
- 聚焦管理

```tsx
// 为屏幕阅读器添加 aria-label
<button
  {...handle.getHandleProps()}
  aria-label={`值：${handle.getValue()}`}
/>
```

## 受控与不受控

```tsx
// 受控（推荐）
const [values, setValues] = useState([50])
const ranger = useRanger({
  values,
  onChange: (instance) => setValues(instance.sortedValues),
  // ...
})

// 带验证
const handleChange = (instance) => {
  const [min, max] = instance.sortedValues
  // 确保最小间隔为 10
  if (max - min >= 10) {
    setValues(instance.sortedValues)
  }
}
```

## 样式技巧

```css
/* 轨道 */
.slider-track {
  position: relative;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  width: 100%;
}

/* 活动段 */
.segment.active {
  background: #3b82f6;
}

/* 滑块 */
.slider-thumb {
  position: absolute;
  transform: translateX(-50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  cursor: grab;
}

.slider-thumb:active {
  cursor: grabbing;
}

.slider-thumb:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}
```

## 框架适配器

| 框架 | 包名 | 状态 |
|------|------|------|
| React | `@tanstack/react-ranger` | 稳定 |
| Vue | `@tanstack/vue-ranger` | 稳定 |
| Solid | `@tanstack/solid-ranger` | 稳定 |
| Svelte | `@tanstack/svelte-ranger` | 稳定 |
| Angular | `@tanstack/angular-ranger` | 稳定 |
| 核心 | `@tanstack/ranger-core` | 稳定 |

## 最佳实践

1. **始终使用 `onChange` 中的 `sortedValues`** - 滑块在拖动时可能会交叉
2. **缓存 `getRangerElement` 回调** - 防止不必要的重新渲染
3. **使用语义 HTML** - 将滑块渲染为 `<button>` 元素以实现可访问性
4. **添加 `aria-label`** - 描述每个滑块的目的
5. **使用 CSS 转换 (`translateX`)** - 而不是 `left` 以获得更好的性能
6. **在 `onChange` 中验证** - 强制约束（最小间隔、最大范围等）
7. **使用 `onDrag`** - 在拖动操作期间提供实时反馈
8. **考虑触摸目标** - 在移动设备上使滑块至少为 44x44px

## 常见陷阱

- 忘记在轨道容器上设置 `position: relative`
- 使用 `values` 而不是 `sortedValues`（滑块可能会交换位置）
- 未提供 `getRangerElement` 作为回调
- 使用 `left` 而不是 `transform: translateX()` 设置滑块位置
- 忘记处理键盘导航（通过 `getHandleProps` 内置）
- 未考虑滑块宽度时计算位置
