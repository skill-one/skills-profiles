# React 19 开发模式

## 概述

适用于 Next.js App Router、服务器操作、乐观 UI 和并发特性的 React 19 模式。查看快速参考以获取 API 摘要，查看示例以复制粘贴模式。

## 使用场景

- 使用 Next.js App Router 构建 React 19 应用程序
- 使用 `useOptimistic` 或 `useTransition` 实现乐观 UI
- 创建带表单验证的服务器操作
- 从类组件迁移到钩子
- 使用 React 编译器优化并发渲染
- 使用 `useReducer` 或自定义钩子管理复杂状态
- 将异步操作包裹在 Suspense 边界中

## 快速参考

| 模式 | 钩子 / API | 用例 |
|------|-----------|------|
| 本地状态 | `useState` | 简单组件状态 |
| 复杂状态 | `useReducer` | 多动作状态机 |
| 副作用 | `useEffect` | 订阅、数据获取 |
| 共享状态 | `useContext` / `createContext` | 跨组件数据 |
| DOM 访问 | `useRef` | 聚焦、测量、计时器 |
| 性能优化 | `useMemo` / `useCallback` | 昂贵计算 |
| 非紧急更新 | `useTransition` | 大型列表的搜索/筛选 |
| 推迟昂贵 UI | `useDeferredValue` | 过期更新 |
| 读取资源 | `use()` (React 19) | 渲染中的 Promise 和上下文 |
| 乐观 UI | `useOptimistic` (React 19) | 变更的即时反馈 |
| 表单状态 | `useFormStatus` (React 19) | 子组件中的挂起状态 |
| 表单结果 | `useActionState` (React 19) | 服务器操作结果 |
| 自动记忆化 | React 编译器 | 消除手动记忆化/回调 |

## 使用说明

1. **识别组件类型**：确定是否需要服务器组件或客户端组件
2. **选择钩子**：使用适当的状态管理和副作用钩子
3. **类型化属性**：为所有组件属性定义 TypeScript 接口
4. **处理异步**：将数据获取组件包裹在 Suspense 边界中
5. **优化**：使用 React 编译器或手动记忆化处理昂贵渲染
6. **处理错误**：添加 ErrorBoundary 以实现优雅的错误处理
7. **验证服务器操作**：定义 Zod/模式验证，然后测试：
   - 提交无效输入 → 验证拒绝
   - 提交有效输入 → 验证成功

## 示例

### 带客户端交互的服务器组件

```tsx
// 服务器组件（默认）— 异步，获取数据
async function ProductPage({ id }: { id: string }) {
  const product = await db.product.findUnique({ where: { id } });

  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} />
    </div>
  );
}

// 客户端组件 — 处理交互
'use client';
function AddToCartButton({ productId }: { productId: string }) {
  const [isPending, startTransition] = useTransition();

  const handleAdd = () => {
    startTransition(async () => {
      await addToCart(productId);
    });
  };

  return (
    <button onClick={handleAdd} disabled={isPending}>
      {isPending ? '添加中...' : '加入购物车'}
    </button>
  );
}
```

### 使用 useOptimistic 实现即时反馈

```tsx
'use client';
import { useOptimistic } from 'react';

function TodoList({ todos, addTodo }: { todos: Todo[]; addTodo: (t: Todo) => Promise<void> }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, { ...newTodo, pending: true }]
  );

  const handleSubmit = async (formData: FormData) => {
    const newTodo = { id: Date.now(), text: formData.get('text') as string };
    addOptimisticTodo(newTodo);  // 立即更新 UI
    await addTodo(newTodo);      // 实际后端调用
  };

  return (
    <form action={handleSubmit}>
      {optimisticTodos.map(todo => (
        <div key={todo.id} style={{ opacity: todo.pending ? 0.5 : 1 }}>
          {todo.text}
        </div>
      ))}
      <input type="text" name="text" />
      <button type="submit">添加</button>
    </form>
  );
}
```

### 带表单的服务器操作

```tsx
// app/actions.ts
'use server';
import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const schema = z.object({
  title: z.string().min(5),
  content: z.string().min(10),
});

export async function createPost(prevState: any, formData: FormData) {
  const parsed = schema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  });

  if (!parsed.success) {
    return { errors: parsed.error.flatten().fieldErrors };
  }

  await db.post.create({ data: parsed.data });
  revalidatePath('/posts');
  return { success: true };
}

// app/blog/new/page.tsx
'use client';
import { useActionState } from 'react';
import { createPost } from '../actions';

export default function NewPostPage() {
  const [state, formAction, pending] = useActionState(createPost, {});

  return (
    <form action={formAction}>
      <input name="title" placeholder="标题" />
      {state.errors?.title && <span>{state.errors.title[0]}</span>}
      <textarea name="content" placeholder="内容" />
      <button type="submit" disabled={pending}>
        {pending ? '发布中...' : '发布'}
      </button>
    </form>
  );
}
```

### 自定义钩子

```tsx
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    function handleOnline() { setIsOnline(true); }
    function handleOffline() { setIsOnline(false); }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

### 使用 useTransition 处理非紧急更新

```tsx
function SearchableList({ items }: { items: Item[] }) {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  const [filteredItems, setFilteredItems] = useState(items);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    startTransition(() => {
      setFilteredItems(items.filter(i => i.name.toLowerCase().includes(e.target.value.toLowerCase())));
    });
  };

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <span>筛选中...</span>}
      <ul>{filteredItems.map(i => <li key={i.id}>{i.name}</li>)}</ul>
    </div>
  );
}
```

## 最佳实践

### 服务器与客户端决策

- 从服务器组件开始（无需指令）
- 仅在以下情况添加 `'use client'`：钩子、浏览器 API、事件处理器

### 状态管理

- 保持状态最小 — 在渲染期间计算派生值，而不是在副作用中
- 使用 `useReducer` 管理具有多个相关动作的状态
- 将状态提升到最近的共同祖先

### 副作用

- 仅用于外部系统同步
- 始终指定正确的依赖数组
- 返回清理函数以处理订阅和计时器
- 始终创建新引用，切勿直接修改状态

### 性能优化

- 使用 React 编译器：避免手动 `useMemo`、`useCallback`、`memo`
- 不使用 React 编译器：使用 `useMemo` 处理昂贵计算，`useCallback` 处理稳定回调
- 使用 `useTransition` 处理低优先级状态更新
- 使用稳定 ID 作为列表键，而不是数组索引

### React 19 特定内容

- 将 `use(promise)` 组件包裹在 Suspense 边界中
- 使用 `useActionState` 集成表单-服务器操作
- 验证服务器操作输入 — 它们是公开端点
- 从服务器组件传递可序列化数据到客户端组件

## 限制和警告

- **服务器组件**：不能使用钩子、事件处理器或浏览器 API
- **use() 钩子**：只能在使用期间调用，不能在回调或副作用中调用
- **服务器操作**：必须包含 `'use server'` 指令；始终验证输入
- **状态变更**：切勿直接修改状态 — 始终创建新引用
- **副作用依赖**：在 `useEffect` 依赖数组中包含所有依赖
- **内存泄漏**：始终在 useEffect 返回值中清理订阅和事件监听器

## 参考

查阅以下文件以获取详细模式：

- **[references/hooks-patterns.md](references/hooks-patterns.md)** — useState、useEffect、useRef、useReducer、自定义钩子、常见陷阱
- **[references/component-patterns.md](references/component-patterns.md)** — 属性、组合、状态提升、上下文、复合组件、错误边界
- **[references/react19-features.md](references/react19-features.md)** — use()、useOptimistic、useFormStatus、useActionState、服务器操作、服务器组件、迁移指南
- **[references/performance-patterns.md](references/performance-patterns.md)** — React 编译器设置、useMemo、useCallback、useTransition、useDeferredValue、懒加载
- **[references/typescript-patterns.md](references/typescript-patterns.md)** — 带类型属性、泛型组件、事件处理器、区分联合、上下文类型化
- **[references/learn.md](references/learn.md)** — 从基础到高级 React 19 的渐进式学习指南
- **[references/reference.md](references/reference.md)** — 所有 React 钩子和组件 API 的完整 API 参考
