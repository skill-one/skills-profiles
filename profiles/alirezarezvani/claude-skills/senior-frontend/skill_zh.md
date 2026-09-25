# 高级前端

React/Next.js 应用的前端开发模式、性能优化和自动化工具。

## 目录

- [项目脚手架](#项目脚手架)
- [组件生成](#组件生成)
- [打包分析](#打包分析)
- [React 模式](#react-模式)
- [Next.js 优化](#nextjs-优化)
- [可访问性与测试](#可访问性与测试)

---

## 项目脚手架

使用 TypeScript、Tailwind CSS 和最佳实践配置生成新的 Next.js 或 React 项目。

### 工作流：创建新的前端项目

1. 使用项目名称和模板运行脚手架：
   ```bash
   python scripts/frontend_scaffolder.py my-app --template nextjs
   ```

2. 添加可选功能（认证、API、表单、测试、故事板）：
   ```bash
   python scripts/frontend_scaffolder.py dashboard --template nextjs --features auth,api
   ```

3. 导航到项目并安装依赖项：
   ```bash
   cd my-app && npm install
   ```

4. 启动开发服务器：
   ```bash
   npm run dev
   ```

### 脚手架选项

| 选项 | 描述 |
|------|------|
| `--template nextjs` | Next.js 14+，带 App Router 和服务器组件 |
| `--template react` | React + Vite，带 TypeScript |
| `--features auth` | 添加 NextAuth.js 认证 |
| `--features api` | 添加 React Query + API 客户端 |
| `--features forms` | 添加 React Hook Form + Zod 验证 |
| `--features testing` | 添加 Vitest + Testing Library |
| `--dry-run` | 预览文件而不创建它们 |

### 生成的结构（Next.js）

```
my-app/
├── app/
│   ├── layout.tsx        # 根布局，带字体
│   ├── page.tsx          # 首页
│   ├── globals.css       # Tailwind + CSS 变量
│   └── api/health/route.ts
├── components/
│   ├── ui/               # Button, Input, Card
│   └── layout/           # Header, Footer, Sidebar
├── hooks/                # useDebounce, useLocalStorage
├── lib/                  # utils (cn), constants
├── types/                # TypeScript 接口
├── tailwind.config.ts
├── next.config.js
└── package.json
```

---

## 组件生成

使用 TypeScript、测试和 Storybook 故事生成 React 组件。

### 工作流：创建新组件

1. 生成客户端组件：
   ```bash
   python scripts/component_generator.py Button --dir src/components/ui
   ```

2. 生成服务器组件：
   ```bash
   python scripts/component_generator.py ProductCard --type server
   ```

3. 生成带测试和故事文件的组件：
   ```bash
   python scripts/component_generator.py UserProfile --with-test --with-story
   ```

4. 生成自定义钩子：
   ```bash
   python scripts/component_generator.py FormValidation --type hook
   ```

### 生成器选项

| 选项 | 描述 |
|------|------|
| `--type client` | 客户端组件，带 'use client'（默认） |
| `--type server` | 异步服务器组件 |
| `--type hook` | 自定义 React 钩子 |
| `--with-test` | 包含测试文件 |
| `--with-story` | 包含 Storybook 故事 |
| `--flat` | 在输出目录中创建，不创建子目录 |
| `--dry-run` | 预览而不创建文件 |

### 生成的组件示例

```tsx
'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps {
  className?: string;
  children?: React.ReactNode;
}

export function Button({ className, children }: ButtonProps) {
  return (
    <div className={cn('', className)}>
      {children}
    </div>
  );
}
```

---

## 打包分析

分析 package.json 和项目结构，寻找打包优化的机会。

### 工作流：优化打包大小

1. 在你的项目上运行分析器：
   ```bash
   python scripts/bundle_analyzer.py /path/to/project
   ```

2. 查看健康评分和问题：
   ```
   打包健康评分：75/100 (C)

   依赖项过大：
     moment (290KB)
       替代方案：date-fns (12KB) 或 dayjs (2KB)

     lodash (71KB)
       替代方案：lodash-es + tree-shaking
   ```

3. 通过替换过大的依赖项应用推荐的修复。

4. 使用详细模式重新运行以检查导入模式：
   ```bash
   python scripts/bundle_analyzer.py . --verbose
   ```

### 打包评分解释

| 评分 | 等级 | 操作 |
|------|------|------|
| 90-100 | A | 打包优化良好 |
| 80-89 | B | 可能有小的优化 |
| 70-79 | C | 替换过大的依赖项 |
| 60-69 | D | 需要关注多个问题 |
| 0-59 | F | 打包大小存在严重问题 |

### 检测到的过大数据依赖项

分析器识别了这些常见的过大数据包：

| 包 | 大小 | 替代方案 |
|------|------|------|
| moment | 290KB | date-fns (12KB) 或 dayjs (2KB) |
| lodash | 71KB | lodash-es + tree-shaking |
| axios | 14KB | Native fetch 或 ky (3KB) |
| jquery | 87KB | Native DOM API |
| @mui/material | 大 | shadcn/ui 或 Radix UI |

---

## React 模式

参考：`references/react_patterns.md`

### 复合组件

在相关组件之间共享状态：

```tsx
const Tabs = ({ children }) => {
  const [active, setActive] = useState(0);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
};

Tabs.List = TabList;
Tabs.Panel = TabPanel;

// 使用
<Tabs>
  <Tabs.List>
    <Tabs.Tab>One</Tabs.Tab>
    <Tabs.Tab>Two</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel>内容 1</Tabs.Panel>
  <Tabs.Panel>内容 2</Tabs.Panel>
</Tabs>
```

### 自定义钩子

提取可重用逻辑：

```tsx
function useDebounce<T>(value: T, delay = 500): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// 使用
const debouncedSearch = useDebounce(searchTerm, 300);
```

### 渲染属性

共享渲染逻辑：

```tsx
function DataFetcher({ url, render }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(url).then(r => r.json()).then(setData).finally(() => setLoading(false));
  }, [url]);

  return render({ data, loading });
}

// 使用
<DataFetcher
  url="/api/users"
  render={({ data, loading }) =>
    loading ? <Spinner /> : <UserList users={data} />
  }
/>
```

---

## Next.js 优化

参考：`references/nextjs_optimization_guide.md`

### 服务器组件与客户端组件

默认使用服务器组件。仅在需要以下功能时添加 'use client'：
- 事件处理器（onClick, onChange）
- 状态（useState, useReducer）
- 效果（useEffect）
- 浏览器 API

```tsx
// 服务器组件（默认）- 无 'use client'
async function ProductPage({ params }) {
  const product = await getProduct(params.id);  // 服务器端获取

  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} />  {/* 客户端组件 */}
    </div>
  );
}

// 客户端组件
'use client';
function AddToCartButton({ productId }) {
  const [adding, setAdding] = useState(false);
  return <button onClick={() => addToCart(productId)}>添加</button>;
}
```

### 图片优化

```tsx
import Image from 'next/image';

// 立即加载
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority
/>

// 响应式填充图片
<div className="relative aspect-video">
  <Image
    src="/product.jpg"
    alt="产品"
    fill
    sizes="(max-width: 768px) 100vw, 50vw"
    className="object-cover"
  />
</div>
```

### 数据获取模式

```tsx
// 并行获取
async function Dashboard() {
  const [user, stats] = await Promise.all([
    getUser(),
    getStats()
  ]);
  return <div>...</div>;
}

// 流式传输与 Suspense
async function ProductPage({ params }) {
  return (
    <div>
      <ProductDetails id={params.id} />
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews productId={params.id} />
      </Suspense>
    </div>
  );
}
```

---

## 可访问性与测试

参考：`references/frontend_best_practices.md`

### 可访问性检查清单

1. **语义 HTML**：使用正确的元素（`<button>`, `<nav>`, `<main>`）
2. **键盘导航**：所有交互元素可聚焦
3. **ARIA 标签**：为图标和复杂组件提供标签
4. **颜色对比度**：普通文本最小 4.5:1
5. **焦点指示器**：可见的焦点状态

```tsx
// 可访问性按钮
<button
  type="button"
  aria-label="关闭对话框"
  onClick={onClose}
  className="focus-visible:ring-2 focus-visible:ring-blue-500"
>
  <XIcon aria-hidden="true" />
</button>

// 键盘用户跳过链接
<a href="#main-content" className="sr-only focus:not-sr-only">
  跳到主要内容
</a>
```

### 测试策略

```tsx
// React Testing Library 组件测试
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('按钮点击触发动作', async () => {
  const onClick = vi.fn();
  render(<Button onClick={onClick}>点击我</Button>);

  await userEvent.click(screen.getByRole('button'));
  expect(onClick).toHaveBeenCalledTimes(1);
});

// 测试可访问性
test('对话框可访问性', async () => {
  render(<Dialog open={true} title="确认" />);

  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby');
});
```

---

## 快速参考

### 常见 Next.js 配置

```js
// next.config.js
const nextConfig = {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: 'cdn.example.com' }],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
  },
};
```

### Tailwind CSS 工具

```tsx
// 使用 cn() 进行条件类名
import { cn } from '@/lib/utils';

<button className={cn(
  'px-4 py-2 rounded',
  variant === 'primary' && 'bg-blue-500 text-white',
  disabled && 'opacity-50 cursor-not-allowed'
)} />
```

### TypeScript 模式

```tsx
// 带有 children 的属性
interface CardProps {
  className?: string;
  children: React.ReactNode;
}

// 泛型组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}
```

---

## 资源

- React 模式：`references/react_patterns.md`
- Next.js 优化：`references/nextjs_optimization_guide.md`
- 最佳实践：`references/frontend_best_practices.md`
- 强制问题库（Matt Pocock grill）：`references/forcing_questions.md`
- 组合映射（哪个专家可以 fork）：`references/composition_map.md`

---

## 假设与可验证的成功标准（Karpathy 学科）

在脚手架组件、推荐框架或审核打包之前，必须暴露以下四个假设。

1. **主要用户设备和网络** — mobile-4G、desktop-fiber、low-end-Android 或 corporate-network。驱动所有性能决策。
2. **LCP 目标（毫秒）** — 一个数字，不是“快”。驱动打包预算和渲染选择。
3. **SEO 依赖 vs. 认证墙** — 驱动渲染（SSR/SSG/RSC vs. SPA）。
4. **WCAG 目标 + 命名的可访问性负责人** — AA、AAA 或尽力而为。驱动可访问性投资和 CI 门禁。

**可验证的成功标准**（Karpathy #4）— 每个推荐都必须包括：

- 核心网络指标目标（LCP、INP、CLS）在主要设备上的 p75
- 每个路由的 JS 打包预算（KB-gzip）
- Lighthouse 可访问性底线 + 性能底线

如果其中三个未说明，推荐不完整 — 返回强制问题库的 Q2。

`scripts/frontend_decision_engine.py` 工具编码了这些检查：它拒绝在没有四个假设输入的情况下推荐配置，并打印匹配配置的可验证阈值。

---

## 定制配置文件

`profiles/` 中有四个内置配置，校准每个推荐：

| 配置文件 | 选择时机 | LCP 目标（mobile-4G p75） | 打包预算 |
|---|---|---|---|
| `next-app-router` | SaaS 客户端面，SEO + 动态，RSC 首选 | 2000ms | 150 KB-gzip / 路由 |
| `remix-or-sveltekit` | mobile-4G 主要，低 JS 首选，渐进式增强 | 1500ms | 80 KB-gzip / 路由 |
| `vite-spa` | 认证墙应用，desktop/corporate 主要 | 2500ms | 200 KB 初始化 + 80 KB / 路由 |
| `astro-or-static` | 营销/文档/博客，零写入，SEO 关键 | 1200ms | 30 KB JS / 页面 |

通过以下方式选择配置文件：

```bash
python scripts/frontend_decision_engine.py \
  --primary-device mobile-4g --lcp-target-ms 2000 \
  --seo-dependent true --auth-walled false --team-size 5
```

工具返回最佳匹配配置文件、次优权衡（如果差距在 15% 以内）、堆栈选择、该配置文件应避免的反模式以及所需的 CI 门禁。

要添加自定义配置文件（例如，组织内部工具的默认值）：复制 `profiles/vite-spa.json` 到 `profiles/<your-org>.json` 并调整 `constraints` + `success_thresholds`。

---

## 组合映射

此技能不会重新实现由 POWERFUL 级专家拥有的范围。它会 fork 到他们那里。查看 `references/composition_map.md` 获取完整路由表。关键 fork：

| 关注点 | Fork 到 |
|---|---|
| WCAG 审计、对比度、屏幕阅读器 | `engineering-team/skills/a11y-audit/` |
| 打包分析 + 运行时性能 | `engineering/skills/performance-profiler/` |
| 电影/滚动故事叙述着陆页 | `engineering-team/skills/epic-design/` |
| Apple HIG（iOS / macOS / visionOS） | `product-team/skills/apple-hig-expert/` |
| 预提交 Karpathy 审查 | `engineering/karpathy-coder/` |
| 预飞行架构审查 | `engineering/grill-me/` |

`cs-frontend-engineer` 代理通过 `context: fork` 协调这些 fork。从另一个代理调用它，使用 `Agent({subagent_type: "cs-frontend-engineer", prompt: "..."})` 或通过 `/cs:frontend-review <your problem>` 调用。

---

## 强制问题库（Matt Pocock grill）

在锁定任何框架或渲染决策之前，按 `references/forcing_questions.md` 中的七个强制问题进行讨论。纪律：

1. 每次一个问题。不打包。
2. 总是引用权威文献推荐答案。
3. 在 `/tmp/frontend-grill-<date>.md` 中跟踪答案。
4. 如果触发淘汰标准，停止。不要围绕未解决的差距构建。
5. Q7 之后，运行 `frontend_decision_engine.py` 使用七个答案。

总结：

1. 主要设备和网络？
2. LCP 目标（毫秒）（和 INP, CLS）？
3. RSC / SPA / SSR / SSG — 选择并辩护？
4. 每个路由的 JS 打包预算？
5. SEO 依赖或认证墙？
6. 设计系统源真相？
7. WCAG 目标 + 命名的可访问性负责人？

---

## 从其他代理和技能的调用

三个表面：

1. **斜杠命令**：`/cs:frontend-review <prompt>` — 完整 grill + 决策引擎 + 组合路由。
2. **代理子代理**：`Agent({subagent_type: "cs-frontend-engineer", prompt: "..."})` — fork 上下文，返回 ≤ 200 字摘要。
3. **直接工具调用**：`python scripts/frontend_decision_engine.py ...` — 确定性配置匹配，当输入已知时。

查看 `agents/engineering/cs-frontend-engineer.md` 获取完整调用合同。
