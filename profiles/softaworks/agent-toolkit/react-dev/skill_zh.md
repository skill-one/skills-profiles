# React TypeScript

类型安全的 React = 编译时保证 = 自信的重构。

<when_to_use>

- 构建带类型的 React 组件
- 实现泛型组件
- 类型化事件处理器、表单、ref
- 使用 React 19 功能（动作、服务器组件、use()）
- 路由集成（TanStack Router、React Router）
- 带正确类型的自定义钩子

不适用于：非 React TypeScript、纯 JavaScript React

</when_to_use>

<react_19_changes>

React 19 的破坏性变更需要迁移。关键模式：

**ref 作为 prop** - forwardRef 已弃用：

```typescript
// React 19 - ref 作为普通 prop
type ButtonProps = {
  ref?: React.Ref<HTMLButtonElement>;
} & React.ComponentPropsWithoutRef<'button'>;

function Button({ ref, children, ...props }: ButtonProps) {
  return <button ref={ref} {...props}>{children}</button>;
}
```

**useActionState** - 替换 useFormState：

```typescript
import { useActionState } from 'react';

type FormState = { errors?: string[]; success?: boolean };

function Form() {
  const [state, formAction, isPending] = useActionState(submitAction, {});
  return <form action={formAction}>...</form>;
}
```

**use()** - 解包 promise/上下文：

```typescript
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // 挂起直到解析
  return <div>{user.name}</div>;
}
```

参见 [react-19-patterns.md](references/react-19-patterns.md) 了解 useOptimistic、useTransition、迁移清单。

</react_19_changes>

<component_patterns>

**Props** - 扩展原生元素：

```typescript
type ButtonProps = {
  variant: 'primary' | 'secondary';
} & React.ComponentPropsWithoutRef<'button'>;

function Button({ variant, children, ...props }: ButtonProps) {
  return <button className={variant} {...props}>{children}</button>;
}
```

**子元素类型化**：

```typescript
type Props = {
  children: React.ReactNode;          // 任何可渲染内容
  icon: React.ReactElement;           // 单个元素
  render: (data: T) => React.ReactNode;  // 渲染属性
};
```

**区分联合类型** 用于变体 props：

```typescript
type ButtonProps =
  | { variant: 'link'; href: string }
  | { variant: 'button'; onClick: () => void };

function Button(props: ButtonProps) {
  if (props.variant === 'link') {
    return <a href={props.href}>Link</a>;
  }
  return <button onClick={props.onClick}>Button</button>;
}
```

</component_patterns>

<event_handlers>

使用特定的事件类型以实现精确的目标类型化：

```typescript
// 鼠标
function handleClick(e: React.MouseEvent<HTMLButtonElement>) {
  e.currentTarget.disabled = true;
}

// 表单
function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
}

// 输入
function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  console.log(e.target.value);
}

// 键盘
function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
  if (e.key === 'Enter') e.currentTarget.blur();
}
```

参见 [event-handlers.md](references/event-handlers.md) 了解 focus、拖拽、剪贴板、触摸、滚轮事件。

</event_handlers>

<hooks_typing>

**useState** - 对联合/空显式声明：

```typescript
const [user, setUser] = useState<User | null>(null);
const [status, setStatus] = useState<'idle' | 'loading'>('idle');
```

**useRef** - DOM 为空，可变值为值：

```typescript
const inputRef = useRef<HTMLInputElement>(null);  // DOM - 使用 ?.
const countRef = useRef<number>(0);               // 可变 - 直接访问
```

**useReducer** - 对动作使用区分联合类型：

```typescript
type Action =
  | { type: 'increment' }
  | { type: 'set'; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'set': return { ...state, count: action.payload };
    default: return state;
  }
}
```

**自定义钩子** - 元组返回带 as const：

```typescript
function useToggle(initial = false) {
  const [value, setValue] = useState(initial);
  const toggle = () => setValue(v => !v);
  return [value, toggle] as const;
}
```

**useContext** - 空值保护模式：

```typescript
const UserContext = createContext<User | null>(null);

function useUser() {
  const user = useContext(UserContext);
  if (!user) throw new Error('useUser outside UserProvider');
  return user;
}
```

参见 [hooks.md](references/hooks.md) 了解 useCallback、useMemo、useImperativeHandle、useSyncExternalStore。

</hooks_typing>

<generic_components>

泛型组件从 props 推断类型 - 调用点无需手动注解。

**模式** - keyof T 用于列键，渲染属性用于自定义渲染：

```typescript
type Column<T> = {
  key: keyof T;
  header: string;
  render?: (value: T[keyof T], item: T) => React.ReactNode;
};

type TableProps<T> = {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string | number;
};

function Table<T>({ data, columns, keyExtractor }: TableProps<T>) {
  return (
    <table>
      <thead>
        <tr>{columns.map(col => <th key={String(col.key)}>{col.header}</th>)}</tr>
      </thead>
      <tbody>
        {data.map(item => (
          <tr key={keyExtractor(item)}>
            {columns.map(col => (
              <td key={String(col.key)}>
                {col.render ? col.render(item[col.key], item) : String(item[col.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**约束泛型** 用于必需属性：

```typescript
type HasId = { id: string | number };

function List<T extends HasId>({ items }: { items: T[] }) {
  return <ul>{items.map(item => <li key={item.id}>...</li>)}</ul>;
}
```

参见 [generic-components.md](examples/generic-components.md) 了解 Select、List、Modal、FormField 模式。

</generic_components>

<server_components>

React 19 服务器组件在服务器上运行，可以是异步的。

**异步数据获取**：

```typescript
export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  return <div>{user.name}</div>;
}
```

**服务器动作** - 'use server' 用于变异：

```typescript
'use server';

export async function updateUser(userId: string, formData: FormData) {
  await db.user.update({ where: { id: userId }, data: { ... } });
  revalidatePath(`/users/${userId}`);
}
```

**客户端 + 服务器动作**：

```typescript
'use client';

import { useActionState } from 'react';
import { updateUser } from '@/actions/user';

function UserForm({ userId }: { userId: string }) {
  const [state, formAction, isPending] = useActionState(
    (prev, formData) => updateUser(userId, formData), {}
  );
  return <form action={formAction}>...</form>;
}
```

**use() 用于 promise 传递**：

```typescript
// 服务器：传递 promise 而无需 await
async function Page() {
  const userPromise = fetchUser('123');
  return <UserProfile userPromise={userPromise} />;
}

// 客户端：使用 use 解包
'use client';
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise);
  return <div>{user.name}</div>;
}
```

参见 [server-components.md](examples/server-components.md) 了解并行获取、流式传输、错误边界。

</server_components>

<routing>

TanStack Router 和 React Router v7 都提供类型安全的路由解决方案。

**TanStack Router** - 使用 Zod 验证实现编译时类型安全：

```typescript
import { createRoute } from '@tanstack/react-router';
import { z } from 'zod';

const userRoute = createRoute({
  path: '/users/$userId',
  component: UserPage,
  loader: async ({ params }) => ({ user: await fetchUser(params.userId) }),
  validateSearch: z.object({
    tab: z.enum(['profile', 'settings']).optional(),
    page: z.number().int().positive().default(1),
  }),
});

function UserPage() {
  const { user } = useLoaderData({ from: userRoute.id });
  const { tab, page } = useSearch({ from: userRoute.id });
  const { userId } = useParams({ from: userRoute.id });
}
```

**React Router v7** - 使用 Framework Mode 自动生成类型：

```typescript
import type { Route } from "./+types/user";

export async function loader({ params }: Route.LoaderArgs) {
  return { user: await fetchUser(params.userId) };
}

export default function UserPage({ loaderData }: Route.ComponentProps) {
  const { user } = loaderData; // 从 loader 类型化
  return <h1>{user.name}</h1>;
}
```

参见 [tanstack-router.md](references/tanstack-router.md) 了解 TanStack 模式，以及 [react-router.md](references/react-router.md) 了解 React Router 模式。

</routing>

<rules>

始终：
- 具体的事件类型（MouseEvent、ChangeEvent 等）
- 对联合/空显式 useState
- 使用 ComponentPropsWithoutRef 扩展原生元素
- 对变体 props 使用区分联合类型
- as const 用于元组返回
- React 19 中使用 ref 作为 prop（不使用 forwardRef）
- 使用 useActionState 处理表单动作
- 使用类型安全路由模式（参见路由部分）

绝不：
- 事件处理器中使用 any
- 使用 JSX.Element 作为子元素（使用 ReactNode）
- React 19+ 中使用 forwardRef
- 使用 useFormState（已弃用）
- 忘记处理 DOM ref 的空值
- 在同一文件中混合服务器/客户端组件
- 向 use() 传递时 await promise

</rules>

<references>

- [hooks.md](references/hooks.md) - useState、useRef、useReducer、useContext、自定义钩子
- [event-handlers.md](references/event-handlers.md) - 所有事件类型、通用处理器
- [react-19-patterns.md](references/react-19-patterns.md) - useActionState、use()、useOptimistic、迁移
- [generic-components.md](examples/generic-components.md) - Table、Select、List、Modal 模式
- [server-components.md](examples/server-components.md) - 异步组件、服务器动作、流式传输
- [tanstack-router.md](references/tanstack-router.md) - TanStack Router 类型化路由、搜索参数、导航
- [react-router.md](references/react-router.md) - React Router v7 加载器、动作、类型生成、表单

</references>
