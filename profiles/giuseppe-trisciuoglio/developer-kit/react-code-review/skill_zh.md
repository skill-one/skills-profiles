# React 代码审查

## 概述

这项技能为 React 应用程序提供结构化、全面的代码审查。它根据 React 19 最佳实践、组件架构模式、钩子使用、可访问性标准和生产就绪标准来评估代码。审查结果按严重程度（关键、警告、建议）分类，并提供具体的代码示例以供改进。

当通过代理系统调用时，这项技能会委托给 `react-software-architect-review` 代理进行深入的系统架构分析。

## 使用场景

- 合并前审查 React 组件、钩子和页面
- 验证组件组合和可重用性模式
- 检查钩子使用是否正确（useState、useEffect、useMemo、useCallback）
- 审查 React 19 模式（use、useOptimistic、useFormStatus、Actions）
- 评估状态管理方法（本地、上下文、外部存储）
- 评估性能优化（缓存、代码拆分、懒加载）
- 审查可访问性合规性（WCAG、语义 HTML、ARIA）
- 验证 props、状态和事件的 TypeScript 类型
- 检查 Tailwind CSS 和样式模式
- 实现新的 React 功能或重构组件架构后

## 指令

1. **确定范围**：确定要审查的 React 组件和钩子。使用 `glob` 发现 `.tsx`/`.jsx` 文件，并使用 `grep` 识别组件定义、钩子使用和上下文提供者。

2. **分析组件架构**：验证组件组合是否正确——检查单一职责、适当的大小和可重用性。查找过大的组件（>200 行）、props 过多的组件（>7 个）或混合关注点的组件。

3. **审查钩子使用**：验证钩子使用是否正确——检查 `useEffect`/`useMemo`/`useCallback` 中的依赖数组，验证 `useEffect` 中的清理函数，并识别因缺少或不正确的缓存而导致的无效重绘。

4. **评估状态管理**：评估状态的位置——检查适当的组合、不必要的提升以及上下文与外部存储的适当使用。验证服务器状态使用 TanStack Query、SWR 或类似库，而不是手动 `useEffect` + `useState` 模式。

5. **检查可访问性**：审查语义 HTML 的使用、ARIA 属性、键盘导航、焦点管理和屏幕阅读器兼容性。验证交互元素是否可访问，表单输入是否有适当的标签。

6. **评估性能**：查找无效的重绘、昂贵组件缺少 `React.memo`、`useCallback`/`useMemo` 使用不当、缺少代码拆分和大型包导入。

7. **审查 TypeScript 集成**：检查 props 类型定义、事件处理程序类型、泛型组件模式以及实用类型的正确使用。验证 `any` 是否在可能使用特定类型的地方被使用。

8. **生成审查报告**：生成一个结构化的报告，包含按严重程度分类的发现（关键、警告、建议）、积极观察和优先级建议，并提供代码示例。

## 示例

### 示例 1：钩子依赖问题

```tsx
// ❌ 错误：缺少依赖导致陈旧的闭包
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []); // 缺少 userId 在依赖数组中

  return <div>{user?.name}</div>;
}

// ✅ 正确：依赖正确，包含清理
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchUser(userId).then((data) => {
      if (!cancelled) setUser(data);
    });
    return () => { cancelled = true; };
  }, [userId]);

  return <div>{user?.name}</div>;
}

// ✅ 更好：使用 TanStack Query 处理服务器状态
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  if (isLoading) return <Skeleton />;
  return <div>{user?.name}</div>;
}
```

### 示例 2：组件组合

```tsx
// ❌ 错误：单体组件混合数据获取、过滤和渲染
function Dashboard() {
  const [users, setUsers] = useState([]);
  const [filter, setFilter] = useState('');
  useEffect(() => { /* 在一个中获取 + 过滤 + 排序所有内容 */ }, [filter]);
  return <div>{/* 200+ 行混合关注点 */}</div>;
}

// ✅ 正确：由专注组件和自定义钩子组合而成
function Dashboard() {
  return (
    <div>
      <UserFilters />
      <Suspense fallback={<TableSkeleton />}>
        <UserTable />
      </Suspense>
      <UserPagination />
    </div>
  );
}
```

### 示例 3：可访问性审查

```tsx
// ❌ 错误：交互元素不可访问
function Menu({ items }: { items: MenuItem[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <div onClick={() => setOpen(!open)}>菜单</div>
      {open && (
        <div>
          {items.map(item => (
            <div key={item.id} onClick={() => navigate(item.path)}>
              {item.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ✅ 正确：使用适当的语义和键盘支持
function Menu({ items }: { items: MenuItem[] }) {
  const [open, setOpen] = useState(false);
  return (
    <nav aria-label="主导航">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-controls="menu-list"
      >
        菜单
      </button>
      {open && (
        <ul id="menu-list" role="menu">
          {items.map(item => (
            <li key={item.id} role="menuitem">
              <a href={item.path}>{item.label}</a>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}
```

### 示例 4：性能优化

```tsx
// ❌ 错误：不稳定的回调每次渲染都会重新创建，导致子组件重绘
{filtered.map(product => (
  <ProductCard
    key={product.id}
    product={product}
    onSelect={() => console.log(product.id)} // 每次渲染新函数
  />
))}

// ✅ 正确：稳定的回调 + 缓存的子组件
const handleSelect = useCallback((id: string) => {
  console.log(id);
}, []);

const filtered = useMemo(
  () => products.filter(p => p.name.toLowerCase().includes(search.toLowerCase())),
  [products, search]
);

{filtered.map(product => (
  <ProductCard key={product.id} product={product} onSelect={handleSelect} />
))}

const ProductCard = memo(function ProductCard({ product, onSelect }: Props) {
  return <div onClick={() => onSelect(product.id)}>{product.name}</div>;
});
```

### 示例 5：TypeScript Props 审查

```tsx
// ❌ 错误：松散类型和缺少 props 定义
function Card({ data, onClick, children, ...rest }: any) {
  return (
    <div onClick={onClick} {...rest}>
      <h2>{data.title}</h2>
      {children}
    </div>
  );
}

// ✅ 正确：严格的类型和适当的接口
interface CardProps extends React.ComponentPropsWithoutRef<'article'> {
  title: string;
  description?: string;
  variant?: 'default' | 'outlined' | 'elevated';
  onAction?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

function Card({
  title,
  description,
  variant = 'default',
  onAction,
  children,
  className,
  ...rest
}: CardProps) {
  return (
    <article className={cn('card', `card--${variant}`, className)} {...rest}>
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {children}
      {onAction && <button onClick={onAction}>操作</button>}
    </article>
  );
}
```

## 审查输出格式

按照以下结构组织所有代码审查发现：

### 1. 摘要
简要概述，包括整体质量评分（1-10）和关键观察。

### 2. 关键问题（必须修复）
导致错误、安全漏洞或功能中断的问题。

### 3. 警告（建议修复）
违反最佳实践、导致性能问题或降低可维护性的问题。

### 4. 建议（考虑改进）
代码组织、可访问性或开发者体验的改进建议。

### 5. 积极观察
良好实现的模式和良好实践，值得认可。

### 6. 建议
按优先级排列的下一步行动，并提供代码示例以进行最有影响力的改进。

## 最佳实践

- 保持组件专注——单一职责，少于 200 行
- 将状态与使用它的组件组合在一起
- 使用自定义钩子从组件中提取可重用逻辑
- 仅当测量到的重绘成本合理时才使用 `React.memo`
- 使用 TanStack Query 或 SWR 处理服务器状态，而不是 `useEffect` + `useState`
- 在订阅外部资源时，始终在 `useEffect` 中包含清理函数
- 首先编写语义 HTML，仅在原生语义不足时添加 ARIA
- 使用 TypeScript 严格模式，组件 props 避免使用 `any`
- 实现错误边界以优雅地处理失败
- 优先考虑组合而不是条件渲染的复杂性

## 限制和警告

- 尊重项目的 React 版本——避免为旧版本建议 React 19 功能
- 除非项目已标准化使用某个库，否则不要强制执行特定的状态管理库
- 缓存并不总是有益的——仅在可衡量的重绘影响时建议
- 可访问性建议应遵循 WCAG 2.1 AA 作为基线
- 专注于高置信度的问题——避免对主观样式选择产生误报
- 不要建议重写正常工作的组件，除非有明确、可衡量的收益

## 参考

有关详细的审查清单和模式文档，请参阅 `references/` 目录：
- `references/hooks-patterns.md` — React 钩子最佳实践和常见错误
- `references/component-architecture.md` — 组件组合和设计模式
- `references/accessibility.md` — 可访问性清单和 React 的 ARIA 模式
