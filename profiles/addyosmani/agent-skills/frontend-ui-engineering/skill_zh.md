# 前端 UI 工程

## 概述

构建生产级别的用户界面，使其具备无障碍性、高性能和精良的视觉效果。目标是外观如同由顶尖公司中具备设计意识工程师所构建的界面——而非由 AI 生成的界面。这要求真正遵循设计系统、具备良好的无障碍性、体现深思熟虑的交互模式，并杜绝通用的“AI 美学”。

## 何时使用

- 构建新的 UI 组件或页面
- 修改现有的面向用户的界面
- 实现响应式布局
- 添加交互性或状态管理
- 修复视觉或 UX 问题

## 组件架构

### 文件结构

将与组件相关的所有内容归置在一起：

```
src/components/
  TaskList/
    TaskList.tsx          # Component implementation
    TaskList.test.tsx     # Tests
    TaskList.stories.tsx  # Storybook stories (if using)
    use-task-list.ts      # Custom hook (if complex state)
    types.ts              # Component-specific types (if needed)
```

### 组件模式

**优先采用组合而非配置：**

```tsx
// Good: Composable
<Card>
  <CardHeader>
    <CardTitle>Tasks</CardTitle>
  </CardHeader>
  <CardBody>
    <TaskList tasks={tasks} />
  </CardBody>
</Card>

// Avoid: Over-configured
<Card
  title="Tasks"
  headerVariant="large"
  bodyPadding="md"
  content={<TaskList tasks={tasks} />}
/>
```

**保持组件专注：**

```tsx
// Good: Does one thing
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
// Container: handles data
export function TaskListContainer() {
  const { tasks, isLoading, error } = useTasks();

  if (isLoading) return <TaskListSkeleton />;
  if (error) return <ErrorState message="Failed to load tasks" retry={refetch} />;
  if (tasks.length === 0) return <EmptyState message="No tasks yet" />;

  return <TaskList tasks={tasks} />;
}

// Presentation: handles rendering
export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul role="list" className="divide-y">
      {tasks.map(task => <TaskItem key={task.id} task={task} />)}
    </ul>
  );
}
```

## 状态管理

**选择最简可行方案：**

```
局部状态（useState）           → 组件特定的 UI 状态
提升状态                       → 在 2-3 个兄弟组件之间共享
Context                         → 主题、认证、语言（读取多、写入少）
URL 状态（searchParams）        → 过滤器、分页、可分享的 UI 状态
服务端状态（React Query, SWR）  → 带缓存的远程数据
全局状态库（Zustand, Redux）    → 全局共享的复杂客户端状态
```

**避免属性传递超过 3 层。如果需通过不使用这些属性的组件传递属性，则引入 Context 或重构组件树。**

## 设计系统遵循

### 以参考为导向的 UI 质量

当产品需要明确的视觉方向时，在选择布局前收集证据：

1. 搜索可信的参考目录，或使用产品团队提供的参考资料。
2. 研究两到三个相关的界面，记录关于层级、密度、导航、控件、响应式行为和交互状态的决定。
3. 在实现前，将这些决定转化为一份简短的设计契约，明确界面的功能、主要操作、必需状态、响应式规则以及需拒绝的交互模式。
4. 在产品自身的组件、设计令牌、内容和视觉语言中重建有用的结构。绝不复制其他产品的品牌、专有文本、图像或精确布局。

将参考资料作为证据，而非模板。若参考资料不可用，请记录假设，并对照产品现有的设计系统验证结果。

### 避免 AI 美学

AI 生成的 UI 具有可识别的模式，需规避所有此类模式：

| AI 默认模式 | 问题所在 | 生产级质量 |
|---|---|---|
| 全用紫/靛蓝 | 模型默认使用视觉上“安全”的配色，导致所有应用看起来都一模一样 | 使用项目的实际配色方案 |
| 过度使用渐变 | 渐变会增加视觉噪点，并与大多数设计系统冲突 | 与设计系统匹配的扁平或微妙渐变 |
| 所有元素都高度圆角（rounded-2xl） | 最大圆角虽传递出“友好”信号，但忽略了真实设计中圆角层级 | 来自设计系统的统一边框半径 |
| 通用的英雄区段 | 模板化布局，与实际内容和用户需求无关联 | 以内容为中心的布局 |
| Lorem ipsum 风格的文案 | 占位符文本会隐藏真实内容（长度、换行、溢出）暴露的布局问题 | 真实的占位内容 |
| 各处 padding 过大 | 等量且宽裕的 padding 会破坏视觉层级并浪费屏幕空间 | 一致的间距尺度 |
| 通用卡片网格 | 统一网格是忽略信息优先级和扫描模式的布局捷径 | 以目的驱动的布局 |
| 阴影过重的设计 | 层次阴影会增加深度，与内容竞争，并在低端设备上拖慢渲染 | 设计系统有明确要求时使用细微或无需阴影 |

### 间距与布局

使用一致的间距尺度，不要随意定义数值：

```css
/* 使用该尺度：以 0.25rem 为增量（或项目实际使用的值） */
/* 好 */  padding: 1rem;      /* 16px */
/* 好 */  gap: 0.75rem;       /* 12px */
/* 差 */   padding: 13px;      /* 不在任何尺度上 */
/* 差 */   margin-top: 2.3rem; /* 不在任何尺度上 */
```

### 排版

遵循类型层级：

```
h1 → 页面标题（每页一个）
h2 → 章节标题
h3 → 子章节标题
body → 默认文本
small → 次要/辅助文本
```

不要跳级标题层级，也不要使用标题样式来渲染非标题内容。

### 色彩

- 使用语义化颜色令牌： ` text-primary`, `bg-surface`, `border-default` —— 而非直接使用原始十六进制色值
- 确保对比度足够（常规文本为 4.5:1，大号文本为 3:1）
- 不要仅依赖色彩来传达信息（同时使用图标、文字或图案等）

## 无障碍访问（WCAG 2.1 AA）

每个组件都必须满足以下标准：

### 键盘导航

```tsx
// 每个交互元素都必须可通过键盘操作
<button onClick={handleClick}>点击我</button>        // ✓ 默认即可聚焦
<div onClick={handleClick}>点击我</div>               // ✗ 无法聚焦
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
// 为缺少可见文本的交互元素添加标签
<button aria-label="关闭对话框"><XIcon /></button>

// 为表单输入框添加标签
<label htmlFor="email">邮箱</label>
<input id="email" type="email" />

// 或在不存在的可见标签时使用 aria-label
<input aria-label="搜索任务" type="search" />
```

### 焦点管理

```tsx
// 内容变化时移动焦点
function Dialog({ isOpen, onClose }: DialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) closeRef.current?.focus();
  }, [isOpen]);

  // 打开时限制焦点在对话框内
  return (
    <dialog open={isOpen}>
      <button ref={closeRef} onClick={onClose}>关闭</button>
      {/* 对话框内容 */}
    </dialog>
  );
}
```

### 有意义的空状态与错误状态

```tsx
// 不要显示空白页面
function TaskList({ tasks }: { tasks: Task[] }) {
  if (tasks.length === 0) {
    return (
      <div role="status" className="text-center py-12">
        <TasksEmptyIcon className="mx-auto h-12 w-12 text-muted" />
        <h3 className="mt-2 text-sm font-medium">没有任务</h3>
        <p className="mt-1 text-sm text-muted">通过创建新任务开始吧。</p>
        <Button className="mt-4" onClick={onCreateTask}>创建任务</Button>
      </div>
    );
  }

  return <ul role="list">...</ul>;
}
```

## 响应式设计

采用移动端优先的思路，再向大屏扩展：

```tsx
// Tailwind: mobile-first 响应式
<div className="
  grid grid-cols-1      /* 移动端：单列 */
  sm:grid-cols-2        /* 小屏：2 列 */
  lg:grid-cols-3        /* 大屏：3 列 */
  gap-4
">
```

测试以下断点：320px、768px、1024px、1440px。

## 加载与过渡

```tsx
// 骨架屏加载（内容不使用旋转加载器）
function TaskListSkeleton() {
  return (
    <div className="space-y-3" aria-busy="true" aria-label="加载任务">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-12 bg-muted animate-pulse rounded" />
      ))}
    </div>
  );
}

// 使用乐观更新提升视觉速度
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

## 相关文档

有关详细无障碍要求与测试工具的说明，请参阅 `../../references/accessibility-checklist.md`。

## 常见辩解理由

| 辩解理由 | 实际情况 |
|---|---|
| “无障碍访问是锦上添花” | 在许多司法管辖区，这是一项法律要求，也是工程质量标准。 |
| “稍后做响应式设计” | 对响应式设计进行后期改造，比从零开始构建要难 3 倍。 |
| “设计还没定稿，所以不做样式” | 使用设计系统默认样式。未做样式的 UI 会给审核者留下破损的第一印象。 |
| “这只是个原型” | 原型最终会变成生产代码。从一开始就打好基础。 |
| “现在的 AI 美学也能接受” | 这传递出质量低下的信号。从一开始就使用项目的实际设计系统。 |

## 危险信号

- 组件代码超过 200 行（需拆分）
- 使用内联样式或任意像素值
- 缺少错误状态、加载状态或空状态
- 未进行键盘导航测试
- 仅以色彩（无文字或图标）来标识状态（红/绿）
- 通用的“AI 风格”（紫色渐变、过度放大的卡片、通用布局）

## 验证

构建 UI 后：

- [ ] 组件渲染无控制台报错
- [ ] 所有交互元素均支持键盘访问（可通过 Tab 键遍历页面）
- [ ] 屏幕阅读器能够传达页面内容及结构
- [ ] 响应式适配：在 320px、768px、1024px、1440px 下均可正常显示
- [ ] 在适用时，已处理加载、空、错误、成功及权限等状态
- [ ] 遵循项目设计系统（间距、色彩、排版）
- [ ] 渲染结果通过最终的 UI 专项验收审查
- [ ] 开发工具或 axe-core 中无无障碍警告
