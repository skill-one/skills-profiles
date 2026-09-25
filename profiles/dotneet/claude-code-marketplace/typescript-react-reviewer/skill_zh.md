# TypeScript + React 19 代码审查专家

精通 React 19 新特性、TypeScript 最佳实践、状态管理模式和常见反模式的代码审查专家。

## 审查优先级等级

### 🚫 严重（阻止合并）

这些问题会导致 Bug、内存泄漏或架构问题：

| 问题 | 为什么严重 |
|-------|------------|
| `useEffect` 用于派生状态 | 额外渲染周期、同步 Bug |
| `useEffect` 缺少清理 | 内存泄漏 |
| 直接状态修改（`.push()`、`.splice()`） | 静默更新失败 |
| 条件钩子调用 | 破坏钩子规则 |
| 动态列表中的 `key={index}` | 重新排序时状态损坏 |
| 无理由的 `any` 类型 | 绕过类型安全 |
| 同一组件中 `useFormStatus` 和 `<form>` | 总是返回 false（React 19 Bug） |
| 在渲染中创建 `use()` 的 Promise | 无限循环 |

### ⚠️ 高优先级

| 问题 | 影响 |
|-------|------|
| 不完整的依赖数组 | 陈旧的闭包、缺少更新 |
| 将 Props 类型指定为 `any` | 运行时错误 |
| 无理由的 `useMemo`/`useCallback` | 不必要的复杂性 |
| 缺少错误边界 | 糟糕的错误用户体验 |
| 控制输入初始化为 `undefined` | React 警告 |

### 📝 架构/风格

| 问题 | 建议 |
|-------|------|
| 组件超过 300 行 | 拆分为更小的组件 |
| Prop 钻孔超过 2-3 层 | 使用组合或上下文 |
| 状态远离使用位置 | 同位状态 |
| 没有 `use` 前缀的自定义钩子 | 遵循命名约定 |

## 快速检测模式

### useEffect 滥用（最常见的反模式）

```typescript
// ❌ 错误：派生状态在 useEffect 中
const [firstName, setFirstName] = useState('');
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// ✅ 正确：在渲染期间计算
const fullName = firstName + ' ' + lastName;
```

```typescript
// ❌ 错误：事件逻辑在 useEffect 中
useEffect(() => {
  if (product.isInCart) showNotification('Added!');
}, [product]);

// ✅ 正确：逻辑在事件处理程序中
function handleAddToCart() {
  addToCart(product);
  showNotification('Added!');
}
```

### React 19 钩子错误

```typescript
// ❌ 错误：在表单组件中使用 useFormStatus（总是返回 false）
function Form() {
  const { pending } = useFormStatus();
  return <form action={submit}><button disabled={pending}>Send</button></form>;
}

// ✅ 正确：在子组件中使用 useFormStatus
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button type="submit" disabled={pending}>Send</button>;
}
function Form() {
  return <form action={submit}><SubmitButton /></form>;
}
```

```typescript
// ❌ 错误：在渲染中创建 Promise（无限循环）
function Component() {
  const data = use(fetch('/api/data')); // 每次渲染都创建新的 Promise!
}

// ✅ 正确：从 Props 或状态中获取 Promise
function Component({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise);
}
```

### 状态修改检测

```typescript
// ❌ 错误：修改（无重新渲染）
items.push(newItem);
setItems(items);

arr[i] = newValue;
setArr(arr);

// ✅ 正确：不可变更新
setItems([...items, newItem]);
setArr(arr.map((x, idx) => idx === i ? newValue : x));
```

### TypeScript 警报

```typescript
// ❌ 需要捕获的警报
const data: any = response;           // 不安全的 any
const items = arr[10];                // 缺少 undefined 检查
const App: React.FC<Props> = () => {}; // 不推荐的模式

// ✅ 推荐模式
const data: ResponseType = response;
const items = arr[10]; // with noUncheckedIndexedAccess
const App = ({ prop }: Props) => {};  // 明确的 Props
```

## 审查工作流程

1. **首先扫描严重问题** - 检查“严重（阻止合并）”部分中的模式
2. **检查 React 19 使用情况** - 查看 [react19-patterns.md](references/react19-patterns.md) 了解新的 API 模式
3. **评估状态管理** - 状态是否同位？服务器状态与客户端状态分离？
4. **评估 TypeScript 安全性** - 泛型组件、区分联合类型、严格配置
5. **审查可维护性** - 组件大小、钩子设计、文件夹结构

## 参考文档

有关详细模式和示例：

- **[react19-patterns.md](references/react19-patterns.md)** - React 19 新钩子（useActionState、useOptimistic、use）、服务器/客户端组件边界
- **[antipatterns.md](references/antipatterns.md)** - 包含修复的全面反模式目录
- **[checklist.md](references/checklist.md)** - 用于彻底审查的完整代码审查清单

## 状态管理快速指南

| 数据类型 | 解决方案 |
|---------|---------|
| 服务器/异步数据 | TanStack Query（永远不要复制到本地状态） |
| 简单全局 UI 状态 | Zustand (~1KB, 无 Provider) |
| 精细粒度派生状态 | Jotai (~2.4KB) |
| 组件本地状态 | useState/useReducer |
| 表单状态 | React 19 useActionState |

### TanStack Query 反模式

```typescript
// ❌ 永远不要将服务器数据复制到本地状态
const { data } = useQuery({ queryKey: ['todos'], queryFn: fetchTodos });
const [todos, setTodos] = useState([]);
useEffect(() => setTodos(data), [data]);

// ✅ 查询就是真相
const { data: todos } = useQuery({ queryKey: ['todos'], queryFn: fetchTodos });
```

## TypeScript 配置建议

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true
  }
}
```

`noUncheckedIndexedAccess` 至关重要 - 它可以捕获 `arr[i]` 返回 undefined 的情况。

## 立即警报

审查时立即标记这些内容：

| 模式 | 问题 | 修复 |
|------|------|------|
| `eslint-disable react-hooks/exhaustive-deps` | 隐藏陈旧闭包 Bug | 重构逻辑 |
| 组件定义在组件内部 | 每次渲染都会重新挂载 | 移到外部 |
| `useState(undefined)` 用于输入 | 无受控警告 | 使用空字符串 |
| `React.FC` 带有泛型 | 泛型推断失败 | 使用明确的 Props |
| 应用代码中的包文件（`index.ts`） | 打包膨胀、循环依赖 | 直接导入 |
