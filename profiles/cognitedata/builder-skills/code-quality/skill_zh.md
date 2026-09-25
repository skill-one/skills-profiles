# 代码质量审查

审查 **$ARGUMENTS**（如果没有提供参数，则审查整个应用程序）中的代码质量问题。按照以下步骤逐一处理，并列出所有发现的问题，包括文件路径和行号。

---

## 第 1 步 — 首先运行 linter

在手动阅读任何代码之前，先从自动化工具获取一个基准：

```bash
pnpm run lint
```

列出所有错误和警告。在继续之前修复所有错误——linter 错误是不可协商的。警告应该被审查和解决，除非有文档记录的例外情况。

此外，在严格模式下运行 TypeScript 编译器以暴露任何隐藏的类型问题：

```bash
pnpm exec tsc --noEmit
```

列出所有类型错误。这些问题必须被修复。

---

## 第 2 步 — TypeScript 类型安全

### 2a — 消除 `any` 类型

在整个代码库中搜索 `any` 的使用情况：

```bash
grep -rn --include="*.ts" --include="*.tsx" -E ": any|as any|<any>" src/
```

对于每个匹配项，用正确的类型替换。常见的替换方式：

| 替换为 | 使用 |
|------------|-----|
| 用于未知外部数据的 `any` | `unknown` + 类型守卫或 Zod 解析 |
| 用于事件处理器的 `any` | `React.ChangeEvent<HTMLInputElement>`、`React.MouseEvent` 等 |
| 用于 CDF 响应的 `any` | SDK 自身的响应类型（从 `@cognite/sdk` 导入） |
| 用于数组的 `any[]` | `T[]` 并带有正确的泛型 |
| `as any` 转换 | 正确的类型缩小或显式的重载函数签名 |

目标是 `src/` 中没有 `any`。如果第三方库强制使用 `any`，请将调用包装在类型化的适配器函数中，以防止 `any` 泄漏到应用程序中。

### 2b — 使不可能的状态无法表示

使用类型系统使无效状态在编译时失败。可到达的状态越少，代码越容易阅读和修改。

**标记类型** — 标记原始类型，以便它们不会混淆。在边界处验证一次；下游代码信任该类型。

```ts
type PhoneNumber = string & { __brand: "PhoneNumber" };

function parsePhone(input: string): PhoneNumber {
  if (!/^\+?\d{10,15}$/.test(input)) throw new Error(`Invalid: ${input}`);
  return input as PhoneNumber;
}
```

如果项目使用具有原生标记类型支持的库（例如 Effect），请使用它们的原始类型，而不是自己编写。

**区分联合类型胜过标志包** — 用排他性联合类型替换布尔值/可选组合：

```ts
// 不要 — 无效的组合可以表示
type State = { loading: boolean; user?: User; error?: string };

// 要 — 只有有效的状态存在
type State =
  | { status: "loading" }
  | { status: "success"; user: User }
  | { status: "error"; error: string };
```

搜索标志包模式：

```bash
grep -rn --include="*.ts" --include="*.tsx" -E "loading\?|isLoading.*isError|isSuccess.*isError" src/
```

标记所有组合布尔标志的类型，其中只有某些组合是有效的。这些应该是区分联合类型。

### 2c — 让类型端到端流动

DB 模式 → 服务器 → 客户端应共享类型而无需手动重复。不要重新声明你可以派生的类型——在编写新接口之前，先使用 `Pick`、`Omit`、`Parameters`、`ReturnType`、`Awaited`、`typeof`。

```ts
// 不要 — 重复形状，当行变化时会漂移
type UserSummary = { id: string; email: Email };
function renderUser(u: UserSummary) { /* ... */ }

// 要 — 从源头派生
type User = Awaited<ReturnType<typeof db.query.users.findFirst>>;
function renderUser(u: Pick<User, "id" | "email">) { /* ... */ }
```

```bash
# 查找手动重复的类型形状
grep -rn --include="*.ts" --include="*.tsx" -E "^(export )?type \w+Summary|^(export )?interface \w+DTO" src/
```

标记手动重新声明已在 SDK 或 DB 类型上存在的字段的接口——这些应该使用 `Pick`/`Omit`。

### 2d — 传递对象，而不是位置参数

具有两个或多个相同原始类型参数的函数应接收命名字段对象，以便调用者不能无声地交换参数。

```ts
// 不要 — 交换两个参数，仍然可以编译
sendEmail("Welcome!", "Hi there");

// 要 — 无顺序，自文档化
sendEmail({ to: "alice@x.com", subject: "Welcome!", body: "Hi there" });
```

```bash
# 查找具有多个字符串/数字参数的函数（潜在的交换错误）
grep -rn --include="*.ts" --include="*.tsx" -E "^\s*(export\s+)?(function|const)\s+\w+\s*\([^)]*string[^)]*string" src/
```

---

## 第 3 步 — 检查组件大小和单一职责

列出所有 `.tsx` 文件及其行数：

```bash
node -e "const fs=require('fs'),path=require('path');function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>{const p=path.join(d,e.name);return e.isDirectory()?walk(p):p.endsWith('.tsx')?[p]:[]})}walk('src').map(p=>({p,l:fs.readFileSync(p,'utf8').split('\n').length})).sort((a,b)=>b.l-a.l).forEach(({l,p})=>console.log(l,p))"
```

标记每个超过 **150 行**的组件文件。对于每个文件，阅读并检查：

- 它是否做不止一件事？（获取数据 AND 渲染 UI AND 处理表单状态）
- 获取逻辑是否可以移动到自定义钩子（`useAssetData`）？
- 子部分是否可以提取为命名的子组件？

仅在它创建真正更清晰的分离时应用拆分——不要仅因为行数而拆分。一个命名良好的 200 行组件比三个命名不良的 60 行组件更好。

---

## 第 4 步 — 查找并删除重复逻辑（DRY）

在钩子、工具和组件中搜索复制粘贴的模式：

```bash
# 查找重复的获取模式
grep -rn --include="*.ts" --include="*.tsx" -E "sdk\.(assets|timeseries|events|files)\.(list|retrieve)" src/

# 查找重复的格式化函数
grep -rn --include="*.ts" --include="*.tsx" -E "toLocaleDateString|toLocaleString|new Date\(" src/

# 查找超过 40 个字符的重复 className 字符串
grep -rn --include="*.tsx" -E 'className="[^"]{40,}"' src/
```

对于每个重复集：
- 如果它是纯函数，则提取到 `src/utils/`
- 如果它包含 React 状态或效果，则提取到 `src/hooks/`
- 如果它是 JSX，则提取到共享组件

---

## 第 5 步 — 强制外部调用的依赖注入

组件和钩子不得直接导入 CDF 客户端。SDK 客户端必须从上下文（通过 `useCogniteClient()` 或属性）获取，以便组件可以独立测试。

```bash
grep -rn --include="*.ts" --include="*.tsx" -E "new CogniteClient|createCogniteClient" src/
```

标记应用程序的引导/身份验证设置文件之外任何直接的客户端构造。模式应始终为：

```ts
// 好 — 客户端来自上下文
export function useMyData() {
  const sdk = useCogniteClient(); // 从 Flows 身份验证上下文
  // ...
}

// 坏 — 在钩子或组件内直接构造
const sdk = new CogniteClient({ project: "my-project", ... });
```

类似地，Atlas 工具应通过 `execute` 的钩子提供的 ref 闭包接收它们的依赖项，而不是通过导入全局单例。

---

## 第 6 步 — 验证编码模式和可测试性

检查代码库是否遵循 Flows 应用程序审查过程所需的三个核心模式。这些模式使代码可测试、可维护和一致。

### 6a — 通过 React 上下文进行依赖注入

钩子必须通过上下文类型声明它们的依赖项，并通过 `useContext` 消费它们，而不是直接导入它们。这使无模块级模拟即可进行测试成为可能。

```bash
# 查找直接导入其他钩子/服务的钩子（潜在的 DI 违规）
grep -rn --include="*.ts" --include="*.tsx" -E "^import.*from\s+['\"]\.\./" src/hooks/

# 查找使用 useContext 进行依赖注入的钩子（好模式）
grep -rn --include="*.ts" --include="*.tsx" "useContext" src/hooks/
```

首选模式：

```typescript
// 好 — 可通过上下文注入
const defaultDependencies = { useDataSource, useAnalytics };
export type UseMyHookContextType = typeof defaultDependencies;
export const UseMyHookContext = createContext<UseMyHookContextType>(defaultDependencies);
export function useMyHook() {
  const { useDataSource } = useContext(UseMyHookContext);
}

// 坏 — 硬编码导入，需要 vi.mock 进行测试
import { useDataSource } from '../data/useDataSource';
export function useMyHook() { const data = useDataSource(); }
```

对于非 React 代码（工具、服务），使用 **具有部分依赖项覆盖的工厂函数**：

```typescript
type Deps = { serviceFactory: () => SomeService };
const defaultDeps: Deps = { serviceFactory: () => new SomeServiceImpl() };
export const doSomething = async (props: Props, depOverrides?: Partial<Deps>) => {
  const deps = { ...defaultDeps, ...depOverrides };
  const service = deps.serviceFactory();
};
```

标记每个直接导入依赖项而不是通过上下文接收的钩子。即使今天存在测试，这些也是可测试性问题。

### 6b — 基于接口的服务

服务类必须实现显式的 TypeScript 接口。这使生产代码可替换且类型安全。

```bash
# 查找服务/类定义并检查接口实现
grep -rn --include="*.ts" --include="*.tsx" -E "class\s+\w+(Service|Client|Repository|Manager)" src/

# 查找生产代码和测试代码中的不安全转换
grep -rn --include="*.ts" --include="*.tsx" "as unknown as" src/
```

标记：
- 未实现显式接口的服务类
- 生产或测试代码中的 `as unknown as T` 转换——这表明接口设计不佳

### 6c — ViewModel 模式

页面级钩子（`useSomethingViewModel`）必须将业务逻辑与表示分离。UI 组件仅接收数据和回调；它们不包含数据获取、副作用逻辑或直接的 SDK 调用。

```bash
# 查找页面/视图组件
grep -rn --include="*.tsx" --include="*.ts" -l "useQuery\|useMutation\|sdk\.\|client\." src/pages/ src/views/ 2>/dev/null

# 查找 ViewModel 钩子
grep -rn --include="*.ts" --include="*.tsx" -l "ViewModel" src/hooks/ 2>/dev/null
```

标记：
- 包含 `useQuery`、`useMutation` 或直接 SDK 调用的页面组件——这些逻辑应在 ViewModel 钩子中
- 非平凡数据逻辑的页面缺少 ViewModel 钩子

### 6d — 测试模拟质量

```bash
# 查找 vi.mock 使用——每个都应该有解释为什么没有使用上下文注入的注释
grep -rn --include="*.ts" --include="*.tsx" "vi\.mock" src/

# 查找不安全的测试转换
grep -rn --include="*.ts" --include="*.tsx" "as unknown as" src/ | grep -E "\.test\.|\.spec\."
```

标记：
- 没有解释为什么没有使用上下文注入的注释的 `vi.mock` 使用
- 测试文件中的 `as unknown as T` 转换——表明生产代码中的接口设计不佳

---

## 第 7 步 — 检查命名约定

阅读一组有代表性的文件并验证：

| 资产 | 约定 | 示例 |
|----------|-----------|---------|
| 文件和目录 | `kebab-case` | `asset-panel.tsx`, `use-asset-data.ts` |
| React 组件 | `PascalCase` | `AssetPanel`, `NavigationBar` |
| 变量、函数、钩子 | `camelCase` | `isLoading`, `fetchAssets`, `useAssetData` |
| 常量（模块级） | `SCREAMING_SNAKE_CASE` | `MAX_ITEMS`, `AGENT_EXTERNAL_ID` |
| TypeScript 类型 & 接口 | `PascalCase` | `AssetNode`, `ChartConfig` |
| 布尔变量 | 辅助动词前缀 | `isLoading`, `hasError`, `canEdit` |

搜索常见的违规行为：

```bash
# TSX 组件不在 PascalCase（文件名以小写字母开头）
node -e "const fs=require('fs'),path=require('path');function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>{const p=path.join(d,e.name);return e.isDirectory()?walk(p):p.endsWith('.tsx')?[p]:[]})}walk('src').filter(p=>/^[a-z]/.test(path.basename(p))).forEach(p=>console.log(p))"

# 钩子文件不以 "use" 开头
node -e "const fs=require('fs');fs.readdirSync('src/hooks').filter(f=>f.endsWith('.ts')&&!f.startsWith('use')).forEach(f=>console.log('src/hooks/'+f))"
```

---

## 第 8 步 — 删除死代码

```powershell
# 查找注释掉的代码块（3+ 连续注释行）
Get-ChildItem -Recurse -Include "*.ts","*.tsx" src | ForEach-Object {
    $file = $_; $lines = Get-Content $file.FullName
    $count = 0; $startLine = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\s*//') {
            if ($count -eq 0) { $startLine = $i + 1 }
            $count++
        } else {
            if ($count -ge 3) { "$($file.FullName):$startLine — $count 连续注释行" }
            $count = 0
        }
    }
    if ($count -ge 3) { "$($file.FullName):$startLine — $count 连续注释行" }
}

# 查找 console.log/debug 语句
grep -rn --include="*.tsx" --include="*.ts" -E "console\.(log|debug|warn|error|info)" src/

# 查找 TODO/FIXME/HACK 评论
grep -rn --include="*.tsx" --include="*.ts" -E "(TODO|FIXME|HACK|XXX):" src/
```

搜索无法到达的页面（路由中定义但组件从未导入或渲染的页面）和完全未使用的文件：

```bash
# 查找所有 .ts/.tsx 文件并检查是否在任何地方导入
for file in $(find src -name "*.ts" -o -name "*.tsx" | grep -v ".test." | grep -v ".spec." | grep -v "node_modules"); do
  basename=$(basename "$file" | sed 's/\.[^.]*$//')
  imports=$(grep -rn --include="*.ts" --include="*.tsx" "$basename" src/ | grep -v "$file" | wc -l)
  if [ "$imports" -eq 0 ]; then
    echo "UNUSED: $file"
  fi
done

# 查找路由定义并验证它们的组件是否被导入
grep -rn --include="*.tsx" --include="*.ts" -E "path:\s*['\"]|<Route" src/
```

规则：
- `console.log` 和 `console.debug` 在发布前必须删除（使用适当的错误日志记录 `console.error`）。
- 注释掉的代码块必须删除——版本控制保留历史记录。
- 当前冲刺之前的 `TODO` 和 `FIXME` 评论应解决或转换为跟踪问题。
- 未使用的导入由 linter（第 1 步）捕获；确认它们已删除。

**硬门槛**：无法到达的页面、完全未使用的文件和重要的死代码块在批准前必须删除。这些是阻塞发现。

---

## 第 9 步 — 验证文件和导出结构

每个功能区域都应遵循一致的结构。检查应用程序的布局是否与此模式匹配：

```
src/
├── components/         # 共享的展示性组件
│   └── <name>/
│       ├── <name>.tsx
│       └── index.ts    # 重新导出公共 API
├── hooks/              # 自定义钩子（每个文件 = 一个钩子）
├── utils/              # 纯工具函数（无 React）
├── contexts/           # React 上下文提供者
├── pages/ or views/    # 路由级组件
└── types/              # 共享的 TypeScript 类型
```

标记：
- 直接位于页面组件中的业务逻辑（应在钩子中）
- 位于组件文件内的工具函数（应在 `utils/` 中）
- 在多个文件中使用时在组件文件中内联定义的类型（应在 `types/` 中）
- 组件目录缺少 `index.ts` 模块文件（使导入冗长）

---

## 第 10 步 — 报告发现

生成按类别分组的结构化报告：

| 类别 | 文件 | 行 | 问题 | 建议 |
|----------|------|------|-------|----------------|
| TypeScript | `src/hooks/useData.ts` | 18 | `response as any` 转换 | 从 `@cognite/sdk` 导入并使用 `NodeItem` 类型 |
| 大小 | `src/components/Dashboard.tsx` | — | 340 行，混合获取和渲染逻辑 | 提取 `useDashboardData` 钩子 (~120 行) |
| DRY | `src/components/A.tsx`, `src/components/B.tsx` | 45, 62 | 相同的日期格式化器 | 提取到 `src/utils/formatDate.ts` |
| 命名 | `src/hooks/data.ts` | — | 文件名不以 `use` 开头 | 重命名为 `useData.ts` |
| 死代码 | `src/App.tsx` | 88 | `console.log("debug response", data)` | 删除 |

如果在某个步骤中没有发现问题，请为该步骤声明“未发现问题”。不要无声地跳过步骤。

---

## 完成

总结按类别发现的总数，并列出首先需要解决的高影响项。任何 `any` 类型和 linter 错误都必须视为阻塞——单独列出。
