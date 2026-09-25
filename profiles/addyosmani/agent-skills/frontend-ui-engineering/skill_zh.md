# 前端 UI 工程

## 概述

构建可访问性良好、性能优异且视觉精美的生产级用户界面。目标是看起来像是由顶尖公司中具有设计意识的工程师构建的 UI，而不是由 AI 生成的。这意味着要严格遵守设计系统、确保可访问性、设计周到的交互模式，并避免通用的“AI 风格”。

## 使用场景

- 构建新的 UI 组件或页面
- 修改现有的用户界面
- 实现响应式布局
- 添加交互性或状态管理
- 修复视觉或 UX 问题

## 组件架构

### 文件结构

将组件相关的所有内容集中放置：

```
src/components/
  TaskList/
    TaskList.tsx          # 组件实现
    TaskList.test.tsx     # 测试
    TaskList.stories.tsx  # Storybook 故事（如果使用）
    use-task-list.ts      # 自定义钩子（如果状态复杂）
    types.ts              # 组件特定类型（如果需要）
```

### 组件模式

**优先使用组合而非配置：**

```tsx
// 良好：可组合
<Card>
  <CardHeader>
    <CardTitle>Tasks</CardTitle>
  </CardHeader>
  <CardBody>
    <TaskList tasks={tasks} />
  </CardBody>
</Card>

// 避免：过度配置
<Card
  title="Tasks"
  headerVariant="large"
  bodyPadding="md"
  content={<TaskList tasks={tasks} />}
/>
```

**保持组件专注：**

```tsx
// 良好：做一件事情
export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className="flex items-center gap-3 p-3">
      <Checkbox checked={task.done} onChange={() => onToggle(task.id)} />
      <span className={task.done ? 'line-through text-muted' : ''}>{task.title}</span>
      <Button variant="ghost" size="sm" onClick={() => onDelete(task.id)}>
        <TrashIcon />
      </Button>
    </li>
  );
}
```

**将数据获取与展示分离：**

```tsx
// 容器：处理数据
export function TaskListContainer() {
  const { tasks, isLoading, error } = useTasks();

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="Failed to load tasks" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="No tasks yet" />;

  return <TaskList tasks={tasks} />;
}

// 展示：处理渲染
export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul role="list" className="divide-y">
      {tasks.map(task => <TaskItem key={task.id} task={task} />)}
    </ul>
  );
}
```

## 状态管理

**选择最简单有效的方法：**

```
本地状态 (useState)           → 组件特定 UI 状态
提升状态                     → 在 2-3 个兄弟组件之间共享
上下文                          → 主题、认证、区域（读取密集型，写入稀疏型）
URL 状态 (searchParams)         → 过滤器、分页、可分享的 UI 状态
服务器状态 (React Query, SWR)  → 带缓存远程数据
全局存储 (Zustand, Redux)    → 全局共享的复杂客户端状态
```

**避免超过 3 层的 prop 钻探。** 如果你通过不使用它们的组件传递 props，请引入上下文或重构组件树。

## 设计系统遵循

### 基于参考的 UI 质量

当产品需要独特的视觉方向时，在选择布局之前收集证据：

1. 搜索可信的参考目录或使用产品团队提供的参考。
2. 研究 2-3 个相关屏幕。记录关于层级、密度、导航、控件、响应式行为和交互状态的决策。
3. 在实现之前，将那些决策转化为一个简短的设计合同。命名屏幕的工作、主要操作、所需状态、响应式规则和要拒绝的模式。
4. 在产品的组件、令牌、内容和视觉语言中重建有用的结构。永远不要复制其他产品的品牌、专有文本、图像或精确布局。

将参考作为证据，而不是模板。如果参考不可用，请记录假设并验证结果是否符合产品的现有设计系统。

### 避免AI美学

AI 生成的 UI 有可识别的模式。避免所有这些模式：

| AI 默认 | 问题原因 | 生产级质量 |
|---|---|---|
| 紫色/靛蓝色所有内容 | 模型默认使用视觉“安全”的调色板，使每个应用看起来都一样 | 使用项目的实际调色板 |
| 过度使用渐变 | 渐加视觉噪音并与大多数设计系统冲突 | 扁平或与设计系统匹配的微妙渐变 |
| 所有内容都圆角（rounded-2xl） | 最大圆角表示“友好”，但忽略了真实设计中角落半径的层级 | 从设计系统一致的 border-radius |
| 通用英雄区域 | 模板驱动布局与实际内容或用户需求没有联系 | 内容优先布局 |
| 洛伦兹文本样式 | 占位符文本隐藏了真实内容揭示的布局问题（长度、换行、溢出） | 真实的占位符内容 |
| 处处使用过大的填充 | 相等的填充量破坏了视觉层级并浪费屏幕空间 | 一致的间距比例 |
| 库卡片网格 | 统一网格是布局捷径，忽略了信息优先级和扫描模式 | 目标驱动布局 |
| 阴影过多的设计 | 层叠阴影增加了与内容竞争的深度，并在低端设备上减慢渲染速度 | 微妙或无阴影，除非设计系统指定 |

### 间距和布局

使用一致的间距比例。不要凭空创造值：

```css
/* 使用比例：0.25rem 增量（或项目使用的任何值） */
/* 良好 */  padding: 1rem;      /* 16px */
/* 良好 */  gap: 0.75rem;       /* 12px */
/* 不好 */   padding: 13px;      /* 不在任何比例上 */
/* 不好 */   margin-top: 2.3rem; /* 不在任何比例上 */
```

### 字体排印

尊重类型层级：

```
h1 → 页面标题（每页一个）
h2 → 区分标题
h3 → 子区分标题
body → 默认文本
small → 次要/辅助文本
```

不要跳过标题级别。不要使用标题样式来表示非标题内容。

### 颜色

- 使用语义颜色令牌：`text-primary`, `bg-surface`, `border-default` — 而不是原始十六进制值
- 确保足够的对比度（正常文本 4.5:1，大文本 3:1）
- 不要仅依赖颜色来传达信息（使用图标、文本或模式）

## 可访问性（WCAG 2.1 AA）

每个组件都必须满足这些标准：

### 键盘导航

```tsx
// 每个交互元素都必须是键盘可访问的
<button onClick={handleClick}>Click me</button>        // ✓ 默认可聚焦
<div onClick={handleClick}>Click me</div>               // ✗ 不可聚焦
<div role="button" tabIndex={0} onClick={handleClick}    // ✓ 但优先使用 <button>
     onKeyDown={e => {
       if (e.key === 'Enter') handleClick();
       if (e.key === ' ') e.preventDefault();
     }}
     onKeyUp={e => {
       if (e.key === ' ') handleClick();
     }}>
  Click me
</div>
```

### ARIA 标签

```tsx
// 标记缺乏可见文本的交互元素
<button aria-label="Close dialog"><XIcon /></button>

// 标记表单输入
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// 或者在没有可见标签的情况下使用 aria-label
<input aria-label="Search tasks" type="search" />
```

### 聚焦管理

```tsx
// 当内容变化时移动聚焦
function Dialog({ isOpen, onClose }: DialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) closeRef.current?.focus();
  }, [isOpen]);

  // 打开时在对话框内捕获聚焦
  return (
    <dialog open={isOpen}>
      <button ref={closeRef} onClick={onClose}>Close</button>
      {/* 对话框内容 */}
    </dialog>
  );
}
```

### 有意义的空状态和错误状态

```tsx
// 不要显示空白屏幕
function TaskList({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return (
      <div role="status" className="text-center py-12">
        <TasksEmptyIcon className="mx-auto h-12 w-12 text-muted" />
        <h3 className="mt-2 text-sm font-medium">No tasks</h3>
        <p className="mt-1 text-sm text-muted">Get started by creating a new task.</p>
        <Button className="mt-4" onClick={onCreateTask}>Create Task</Button>
      </div>
    );
  }

  return <ul role="list">...</ul>;
}
```

## 响应式设计

先为移动端设计，然后扩展：

```tsx
// Tailwind：移动端优先的响应式
<div className="
  grid grid-cols-1      /* 移动端：单列 */
  sm:grid-cols-2        /* 小屏：2 列 */
  lg:grid-cols-3        /* 大屏：3 列 */
  gap-4
">
```

在以下断点测试：320px、768px、1024px、1440px。

## 加载和过渡

```tsx
// 骨架加载（不要使用内容旋转的加载动画）
function TaskListSkeleton() {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="Loading tasks">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-12 bg-muted animate-pulse rounded" />
      ))}
    </div>
  );
}

// 乐观更新以提高感知速度
function useToggleTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleTask,
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });
      const previous = queryClient.getQueryData(['tasks']);

      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(t => t.id === taskId ? { ...t, done: !t.done } : t)
      );

      return { previous };
    },
    onError: (_err, _taskId, context) => {
      queryClient.setQueryData(['tasks'], context?.previous);
    },
  });
}
```

## 参考文档

有关详细的可访问性要求和测试工具，请参阅 `../../references/accessibility-checklist.md`。

## 常见借口

| 借口 | 现实 |
|---|---|
| "可访问性是锦上添花" | 它是许多司法管辖区的法律要求，也是工程质量标准。 |
| "我们会稍后做响应式设计" | 重新设计响应式设计比从一开始就构建要困难 3 倍。 |
| "设计还没最终确定，所以我先跳过样式" | 使用设计系统默认值。未样式化的 UI 会在审查者中留下破败的第一印象。 |
| "这只是原型" | 原型会变成生产代码。从一开始就打好基础。 |
| "AI 美学现在还可以" | 它表明质量低。从一开始就使用项目的实际设计系统。 |

## 警示信号

- 超过 200 行的组件（将它们拆分）
- 内联样式或任意像素值
- 缺少错误状态、加载状态或空状态
- 没有关键盘导航测试
- 仅使用颜色作为状态指示器（红色/绿色，没有文本或图标）
- 通用“AI 外观”（紫色渐变、过大的卡片、库存布局）

## 验证

构建 UI 后：

- [ ] 组件无控制台错误
- [ ] 所有交互元素都是键盘可访问的（通过页面）
- [ ] 屏幕阅读器可以传达页面的内容和结构
- [ ] 响应式：在 320px、768px、1024px、1440px 上工作
- [ ] 处理适用的加载、空、错误、成功和权限状态
- [ ] 遵循项目的设计系统（间距、颜色、字体排印）
- [ ] 渲染结果通过最终 UI 专用完成门禁审查
- [ ] 开发工具或 axe-core 中没有可访问性警告
