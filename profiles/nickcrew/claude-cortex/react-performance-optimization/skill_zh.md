# React 性能优化

通过记忆化、代码拆分、虚拟化和高效的渲染策略来优化 React 应用性能的专业指导。

## 何时使用此技能

- 优化渲染缓慢的 React 组件
- 减少包体积以加快初始加载时间
- 提升大数据列表或数据表格的响应性
- 防止复杂组件树中的不必要重新渲染
- 优化状态管理以减少渲染级联
- 通过代码拆分提升感知性能
- 使用 React DevTools Profiler 调试性能问题

## 核心概念

### React 渲染优化
当 props 或 state 发生变化时，React 会重新渲染组件。不必要的重新渲染会浪费 CPU 周期并降低用户体验。关键的优化技术包括：
- **记忆化**：缓存组件渲染和计算值
- **代码拆分**：按需加载代码以加快初始加载
- **虚拟化**：仅渲染可见的列表项
- **状态优化**：结构化状态以最小化渲染级联

### 何时进行优化
1. **先进行性能分析**：使用 React DevTools Profiler 识别实际瓶颈
2. **衡量影响**：验证优化是否提升了性能
3. **避免过早优化**：不要优化性能良好的组件

## 快速参考

按需加载详细模式和示例：

| 主题 | 参考文件 |
| --- | --- |
| React.memo、useMemo、useCallback 模式 | `skills/react-performance-optimization/references/memoization.md` |
| 使用 lazy/Suspense 进行代码拆分、包优化 | `skills/react-performance-optimization/references/code-splitting.md` |
| 大型列表的虚拟化（react-window） | `skills/react-performance-optimization/references/virtualization.md` |
| 状态管理策略、上下文拆分 | `skills/react-performance-optimization/references/state-management.md` |
| useTransition、useDeferredValue（React 18+） | `skills/react-performance-optimization/references/concurrent-features.md` |
| React DevTools Profiler、性能监控 | `skills/react-performance-optimization/references/profiling-debugging.md` |
| 常见陷阱和反模式 | `skills/react-performance-optimization/references/common-pitfalls.md` |

## 优化工作流程

### 1. 识别瓶颈
```bash
# 打开 React DevTools Profiler
# 记录交互 → 分析火焰图 → 找到缓慢的组件
```

**查找：**
- 黄色/红色条形的组件（渲染缓慢）
- 不必要的渲染（相同的 props/state）
- 每次渲染时进行昂贵计算

### 2. 应用针对性优化

**针对不必要重新渲染：**
- 用 `React.memo` 包裹组件
- 使用 `useCallback` 获取稳定的函数引用
- 检查 props 中的内联对象/数组

**针对昂贵计算：**
- 使用 `useMemo` 缓存结果
- 尽可能将计算移出渲染

**针对大型列表：**
- 使用 react-window 实现虚拟化
- 确保提供正确的唯一键（不是索引）

**针对缓慢初始加载：**
- 使用 `React.lazy` 添加代码拆分
- 使用 webpack-bundle-analyzer 分析包体积
- 对重型依赖使用动态导入

### 3. 验证改进
```bash
# 记录新的 Profiler 会话
# 比较 before/after 指标
# 确保优化确实有帮助
```

## 常见模式

### 记忆化昂贵组件
```jsx
import { memo } from 'react';

const ExpensiveList = memo(({ items, onItemClick }) => {
  return items.map(item => (
    <Item key={item.id} data={item} onClick={onItemClick} />
  ));
});
```

### 缓存计算值
```jsx
import { useMemo } from 'react';

function DataTable({ items, filters }) {
  const filteredItems = useMemo(() => {
    return items.filter(item => filters.includes(item.category));
  }, [items, filters]);

  return <Table data={filteredItems} />;
}
```

### 稳定函数引用
```jsx
import { useCallback } from 'react';

function Parent() {
  const handleClick = useCallback((id) => {
    console.log('Clicked:', id);
  }, []);

  return <MemoizedChild onClick={handleClick} />;
}
```

### 代码拆分路由
```jsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./Dashboard'));
const Reports = lazy(() => import('./Reports'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  );
}
```

### 虚拟化大型列表
```jsx
import { FixedSizeList } from 'react-window';

function VirtualList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  );
}
```

## 常见错误

1. **过度记忆化**：不要记忆化简单的快速组件（会增加开销）
2. **内联对象/数组**：新引用会破坏记忆化（`config={{ theme: 'dark' }}`）
3. **缺失依赖**：useCallback/useMemo 中的陈旧闭包
4. **使用索引作为键**：当列表顺序变化时会破坏重组
5. **单个大型上下文**：任何更新都会导致大规模重新渲染
6. **无性能分析**：未测量就优化会浪费时间

## 性能检查清单

优化前：
- [ ] 使用 React DevTools 进行性能分析以识别瓶颈
- [ ] 测量基线性能指标

优化目标：
- [ ] 对具有稳定 props 的昂贵组件进行记忆化
- [ ] 使用 useMemo 缓存实际昂贵的计算值
- [ ] 对传递给记忆化子组件的函数使用 useCallback
- [ ] 对路由和重型组件实现代码拆分
- [ ] 对超过 100 项的列表进行虚拟化
- [ ] 为列表项提供稳定的键（唯一 ID，不是索引）
- [ ] 按更新频率拆分状态
- [ ] 使用并发特性（useTransition、useDeferredValue）提升响应性

优化后：
- [ ] 再次进行性能分析以验证改进
- [ ] 检查包体积减少（如果适用）
- [ ] 确保没有功能回归

## 资源

- **React 文档 - 性能**：https://react.dev/learn/render-and-commit
- **React DevTools**：用于性能分析的浏览器扩展
- **react-window**：https://github.com/bvaughn/react-window
- **包分析器**：webpack-bundle-analyzer、rollup-plugin-visualizer
- **Lighthouse**：Chrome DevTools 性能审计
