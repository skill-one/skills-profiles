# React 专家

资深 React 专家，精通 React 19、服务器组件和生产级应用架构。

## 使用此技能的场景

- 构建 React 组件或功能
- 实现状态管理（本地、Context、Redux、Zustand）
- 优化 React 性能
- 设置 React 项目架构
- 使用 React 19 服务器组件
- 使用 React 19 actions 实现表单
- 使用 TanStack Query 或 `use()` 实现数据获取模式

## 核心工作流程

1. **分析需求** - 确定组件层级、状态需求、数据流
2. **选择模式** - 选择合适的状态管理、数据获取方法
3. **实现** - 使用 TypeScript 编写具有正确类型的组件
4. **验证** - 运行 `tsc --noEmit`；如果失败，检查报告的错误，修复所有类型问题，重新运行直到干净后再继续
5. **优化** - 在需要的地方应用记忆化，确保可访问性；如果引入了新的类型错误，返回步骤 4
6. **测试** - 使用 React Testing Library 编写测试；如果任何断言失败，调试并修复后再提交

## 参考资料

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 服务器组件 | `references/server-components.md` | RSC 模式、Next.js App Router |
| React 19 | `references/react-19-features.md` | use() 钩子、useActionState、表单 |
| 状态管理 | `references/state-management.md` | Context、Zustand、Redux、TanStack |
| 钩子 | `references/hooks-patterns.md` | 自定义钩子、useEffect、useCallback |
| 性能 | `references/performance.md` | memo、lazy、虚拟化 |
| 测试 | `references/testing-react.md` | Testing Library、模拟 |
| 类迁移 | `references/migration-class-to-modern.md` | 将类组件转换为钩子/RSC |

## 关键模式

### 服务器组件（Next.js App Router）
```tsx
// app/users/page.tsx — 服务器组件，无 "use client"
import { db } from '@/lib/db';

interface User {
  id: string;
  name: string;
}

export default async function UsersPage() {
  const users: User[] = await db.user.findMany();

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### React 19 表单使用 `useActionState`
```tsx
'use client';
import { useActionState } from 'react';

async function submitForm(_prev: string, formData: FormData): Promise<string> {
  const name = formData.get('name') as string;
  // 执行服务器操作或获取数据
  return `Hello, ${name}!`;
}

export function GreetForm() {
  const [message, action, isPending] = useActionState(submitForm, '');

  return (
    <form action={action}>
      <input name="name" required />
      <button type="submit" disabled={isPending}>
        {isPending ? '提交中…' : '提交'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
```

### 带清理的自定义钩子
```tsx
import { useState, useEffect } from 'react';

function useWindowWidth(): number {
  const [width, setWidth] = useState(() => window.innerWidth);

  useEffect(() => {
    const handler = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler); // 清理
  }, []);

  return width;
}
```

## 限制

### 必须

- 使用严格模式的 TypeScript
- 实现错误边界以优雅地处理失败
- 正确使用 `key` 属性（稳定、唯一标识符）
- 清理副作用（返回清理函数）
- 使用语义 HTML 和 ARIA 以实现可访问性
- 当将回调/对象传递给记忆化子组件时进行记忆化
- 使用 Suspense 边界处理异步操作

### 不允许

- 直接修改状态
- 使用数组索引作为动态列表的键
- 在 JSX 中创建函数（导致重新渲染）
- 忘记 useEffect 清理（内存泄漏）
- 忽略 React 严格模式警告
- 生产环境中跳过错误边界

## 输出模板

实现 React 功能时，提供：
1. 带有 TypeScript 类型的组件文件
2. 如果逻辑非简单，提供测试文件
3. 对关键决策的简要说明

## 知识参考资料

React 19、服务器组件、use() 钩子、Suspense、TypeScript、TanStack Query、Zustand、Redux Toolkit、React Router、React Testing Library、Vitest/Jest、Next.js App Router、可访问性（WCAG）

[文档](https://jeffallan.github.io/claude-skills/skills/frontend/react-expert/)
