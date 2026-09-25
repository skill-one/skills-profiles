# 测试覆盖率修复

修复 **$ARGUMENTS**（如果没有提供参数，则修复整个应用程序）的测试覆盖率。此技能通过查找和修复覆盖率差距来强制执行 Flows 应用程序批准所需的 **80% 行覆盖率硬性门槛**。请按顺序处理每个步骤。

---

## 第 1 步 — 验证测试框架和覆盖率工具

检查项目是否具有配置了覆盖率的可工作的测试框架：

```bash
# 检查 package.json 中是否有 vitest 或 jest
grep -E "(vitest|jest)" package.json

# 检查覆盖率配置
cat vitest.config.ts 2>/dev/null || cat vitest.config.js 2>/dev/null || cat jest.config.ts 2>/dev/null || cat jest.config.js 2>/dev/null
```

验证：
- 已安装并配置了测试框架（Vitest 或 Jest）
- 配置文件具有 `coverage` 部分（例如 vitest.config.ts 中的 `coverage: { provider: 'v8', ... }`）
- 已配置覆盖率报告器（至少 `text` 和 `lcov` 或 `json-summary`）

**如果覆盖率工具未配置，请立即修复：**

1. 安装覆盖率提供程序：
```bash
pnpm add -D @vitest/coverage-v8
```

2. 将覆盖率配置添加到 `vitest.config.ts`。阅读现有的配置文件，然后在 `test` 内部添加 `coverage` 部分：

```typescript
// vitest.config.ts — 添加的最低覆盖率配置
test: {
  coverage: {
    provider: 'v8',
    reporter: ['text', 'text-summary', 'lcov'],
    include: ['src/**/*.{ts,tsx}'],
    exclude: [
      'src/**/*.test.{ts,tsx}',
      'src/**/*.spec.{ts,tsx}',
      'src/**/vite-env.d.ts',
      'src/main.tsx',
    ],
  },
}
```

写入更新后的配置文件。如果根本不存在 vitest.config.ts，请使用完整的 `defineConfig` 包装器创建一个。

---

## 第 2 步 — 验证覆盖率范围

80% 阈值适用于 `src/` 下所有 `.ts` 和 `.tsx` 文件，排除以下内容：
- 测试文件（`*.test.ts`，`*.test.tsx`，`*.spec.ts`，`*.spec.tsx`）
- 类型声明文件（`vite-env.d.ts`）
- 入口点（`main.tsx`）

应用程序**不得**将页面、组件、钩子或其他生产代码排除在覆盖率测量之外。

```bash
# 检查配置中排除了哪些文件覆盖率
grep -A 20 "exclude" vitest.config.ts 2>/dev/null || grep -A 20 "exclude" vitest.config.js 2>/dev/null

# 检查 jest 配置中的 coveragePathIgnorePatterns 或 collectCoverageFrom
grep -A 10 "coveragePathIgnorePatterns\|collectCoverageFrom" jest.config.ts 2>/dev/null
```

**如果配置排除了生产文件，请立即修复：**

删除任何隐藏生产代码的覆盖率测量的排除项。仅测试文件、类型声明和入口点应被排除。重写 `exclude` 数组，仅包含：

```typescript
exclude: [
  'src/**/*.test.{ts,tsx}',
  'src/**/*.spec.{ts,tsx}',
  'src/**/vite-env.d.ts',
  'src/main.tsx',
],
```

特别删除以下排除项：
- `src/pages/` 或 `src/components/` 或 `src/hooks/` — **不允许**
- 特定的功能文件 — **不允许**，除非它们是生成代码
- `src/**/*.tsx`（所有组件）— **不允许**，这会隐藏应用程序的大部分内容

写入修正后的配置文件。

---

## 第 3 步 — 运行测试并收集覆盖率

```bash
# 尝试基于项目设置的常见覆盖率命令
npx vitest run --coverage 2>/dev/null || npx jest --coverage 2>/dev/null || npm test -- --coverage 2>/dev/null
```

记录覆盖率摘要：
- **语句：** X%
- **分支：** X%
- **函数：** X%
- **行：** X%

**硬性门槛：** 总行覆盖率必须**至少为 80%**。低于此阈值的应用程序被列为**必须修复**。

**如果测试无法运行，请立即修复：**

常见修复方法：
- **缺少导入：** 阅读失败的测试文件，添加缺少的导入语句，写入修正后的文件。
- **损坏的模拟：** 阅读测试以了解正在模拟的内容。修复模拟以匹配模拟模块的当前 API。
- **过时的快照：** 运行 `npx vitest run --update` 更新快照，然后审查差异以确保正确性。
- **缺少依赖项：** 运行 `pnpm add -D <missing-package>` 为任何尚未安装的测试实用程序。
- **配置错误：** 阅读配置文件，修复语法或选项错误，写入修正后的文件。

每次修复后重新运行测试，直到所有测试通过。然后记录覆盖率摘要。

---

## 第 4 步 — 查找并编写缺失的测试文件

对于 `src/` 下每个非平凡的 `.ts`/`.tsx` 文件，检查是否存在相应的测试文件：

```bash
# 列出所有生产文件并检查测试对应文件
for file in $(find src -name "*.ts" -o -name "*.tsx" | grep -v ".test." | grep -v ".spec." | grep -v "node_modules" | grep -v "vite-env" | sort); do
  base="${file%.*}"
  ext="${file##*.}"
  dir=$(dirname "$file")
  filename=$(basename "$base")

  # 检查同一目录或 __tests__ 目录中的测试文件
  test_exists="false"
  for pattern in "${base}.test.${ext}" "${base}.spec.${ext}" "${base}.test.ts" "${base}.spec.ts" "${dir}/__tests__/${filename}.test.${ext}" "${dir}/__tests__/${filename}.spec.${ext}"; do
    if [ -f "$pattern" ]; then
      test_exists="true"
      break
    fi
  done

  if [ "$test_exists" = "false" ]; then
    echo "NO TEST: $file"
  fi
done
```

对每个没有测试的文件进行分类：
- **服务、钩子、实用程序、上下文、ViewModel 钩子** — **立即编写测试文件**（见下文）
- **无逻辑的纯展示组件** — 标记为 **N/A**（无需测试）
- **导出器**（仅重新导出的 `index.ts`）— 标记为 **N/A**
- **仅类型文件**（`.d.ts`，仅包含类型/接口导出的文件）— 标记为 **N/A**

**对于每个缺失测试的文件，创建一个全面的测试文件。** 在生产代码支持的情况下使用上下文注入进行依赖项模拟。如果生产代码使用硬编码的导入，请将其记录为可测试性问题，但仍使用 `vi.mock` 并附上说明性评论。按此流程处理每个：

1. **阅读源文件**以了解其导出、依赖项和逻辑。
2. **在同一目录下创建一个 `.test.ts` 或 `.test.tsx` 文件**。
3. **编写测试覆盖以下内容**：成功路径、错误路径、空状态和边缘情况。

为每种文件类型使用正确的测试模式：

**对于钩子：**
- 使用 `@testing-library/react` 的 `renderHook` 进行测试
- 使用必要的提供程序（QueryClientProvider、自定义上下文提供程序等）进行包装
- 测试初始状态、加载状态、成功状态和错误状态
- 示例结构：
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// 导入钩子

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useMyHook', () => {
  it('returns data on success', async () => {
    const { result } = renderHook(() => useMyHook(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.data).toBeDefined());
  });

  it('handles errors', async () => {
    // 设置错误条件
    const { result } = renderHook(() => useMyHook(), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.error).toBeDefined());
  });
});
```

**对于服务/实用程序：**
- 使用直接函数调用进行测试
- 在需要时模拟 CDF SDK 响应
- 测试返回值、副作用和抛出的错误
- 示例结构：
```typescript
import { describe, it, expect, vi } from 'vitest';
// 导入服务/实用程序函数

describe('myService', () => {
  it('returns expected result for valid input', () => {
    const result = myFunction(validInput);
    expect(result).toEqual(expectedOutput);
  });

  it('throws on invalid input', () => {
    expect(() => myFunction(invalidInput)).toThrow();
  });
});
```

**对于具有逻辑的组件：**
- 使用 `@testing-library/react` 的 `render` 进行测试
- 验证加载、错误和数据状态
- 测试触发状态变化的用户交互
- 示例结构：
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// 导入组件和提供程序

describe('MyComponent', () => {
  it('shows loading state initially', () => {
    render(<MyComponent />, { wrapper: createWrapper() });
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders data after loading', async () => {
    render(<MyComponent />, { wrapper: createWrapper() });
    await waitFor(() => {
      expect(screen.getByText('expected content')).toBeInTheDocument();
    });
  });
});
```

**依赖项模拟指南：**
- 尽可能使用上下文注入（而不是 `vi.mock`）— 通过钩子的上下文提供测试依赖项。
- 如果生产代码使用硬编码的导入，阻止上下文注入，请使用 `vi.mock` 并附上解释性评论（例如，`// vi.mock required: useDataSource uses direct import, not context injection`）。
- 确保模拟是类型安全的——没有 `as unknown as T` 强制转换。定义满足接口的适当模拟对象。

编写每个测试文件后，运行 `npx vitest run <test-file>` 以验证它通过。

---

## 第 5 步 — 修复低覆盖率文件

如果覆盖率工具生成每个文件的指标，列出低于 80% 行覆盖率的文件：

```bash
# 解析 lcov 或 text 输出以获取每个文件的覆盖率
cat coverage/coverage-summary.json 2>/dev/null | node -e "
  const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  Object.entries(data).forEach(([file, metrics]) => {
    if (file === 'total') return;
    const pct = metrics.lines?.pct ?? 0;
    if (pct < 80) console.log(pct.toFixed(1) + '% — ' + file);
  });
" 2>/dev/null
```

**对于每个低于 80% 覆盖率的文件，从覆盖率报告中阅读未覆盖的行，然后添加测试用例来执行这些特定代码路径：**

1. **从覆盖率报告中阅读未覆盖的行**。检查 `coverage/` 目录中的详细每个文件报告（lcov 或 html），以显示哪些行未覆盖。
2. **阅读源文件**以了解这些未覆盖的行做什么。
3. **添加测试用例**来执行这些特定代码路径：

- **未覆盖的错误路径：** 添加触发错误条件的测试（网络故障、无效输入、空值、权限错误）。通过提供不良输入或模拟依赖项抛出错误来强制错误。
- **未覆盖的分支：** 为每个条件分支添加测试。如果 `if/else` 只有 `true` 分支被测试，请编写一个触发 `false` 分支的测试。
- **未覆盖的函数：** 添加调用每个缺少覆盖的导出函数的测试。验证返回值和副作用。
- **未覆盖的 catch 块：** 模拟上游调用拒绝/抛出，验证 catch 块行为。

4. **添加测试后重新运行覆盖率**以验证文件现在满足 80%：
```bash
npx vitest run --coverage <test-file>
```

重复直到每个文件至少达到 80% 行覆盖率或您已覆盖所有可行路径。

---

## 第 6 步 — 修复可测试性模式

评估和修复代码库中的可测试性问题：

```bash
# 检查通过上下文进行依赖项注入
grep -rn --include="*.ts" --include="*.tsx" "useContext\|createContext" src/hooks/ src/contexts/

# 检查 vi.mock 使用（测试性红旗）
grep -rn --include="*.ts" --include="*.tsx" "vi\.mock" src/

# 检查测试中的不安全强制转换
grep -rn --include="*.ts" --include="*.tsx" "as unknown as" src/ | grep -E "\.test\.|\.spec\."

# 检查基于接口的服务
grep -rn --include="*.ts" --include="*.tsx" -E "implements\s+\w+" src/
```

**对于每个找到的可测试性问题，重构生产代码以支持更好的测试模式。然后更新相应的测试以使用改进的模式。**

| 问题 | 修复 |
|-------|-----|
| 钩子直接导入依赖项而不是使用上下文 | 添加一个包含默认依赖项的类型上下文。使用 `createContext` 创建上下文，提供使用真实实现的默认值。在钩子中，使用 `useContext` 获取依赖项。测试可以然后通过上下文提供程序提供模拟依赖项，而无需 `vi.mock`。 |
| 服务没有接口 | 提取一个描述服务公共 API 的 TypeScript 接口。让类/对象实现接口。测试模拟接口，而不是具体实现。 |
| 页面组件混合数据获取和渲染 | 将数据逻辑提取到 `use*ViewModel` 钩子中。页面组件调用 ViewModel 钩子并根据其返回值进行渲染。使用模拟的 ViewModel 分别测试 ViewModel 钩子，测试页面组件。 |
| 测试使用 `vi.mock` 对于可以使用上下文注入的模块 | 重构生产代码以使用上下文注入（如上所述），更新测试以通过上下文提供程序提供模拟依赖项。删除 `vi.mock` 调用。添加说明性评论。 |
| 测试使用 `as unknown as T` 强制转换模拟 | 定义一个满足所需接口的适当模拟类型或对象。用正确类型的模拟替换强制转换。如果接口很大，创建一个返回仅使用方法的局部模拟的辅助函数，并正确类型化。 |

对于每个重构的文件：
1. 阅读源文件及其测试文件。
2. 重构生产代码（添加上下文、提取接口、提取 ViewModel 钩子）。
3. 更新测试以使用改进的模式。
4. 运行 `npx vitest run <test-file>` 以验证测试仍然通过。

---

## 第 7 步 — 报告剩余差距

重新运行完整测试套件并带覆盖率以获取最终数字：

```bash
npx vitest run --coverage 2>/dev/null || npx jest --coverage 2>/dev/null
```

生成一个总结已完成的操作和剩余内容的摘要：

```markdown
### 测试覆盖率摘要（修复后）

| 指标 | 之前 | 之后 | 门槛 |
|------|------|------|------|
| 行 | X% | Y% | ≥80% 必须满足 |
| 分支 | X% | Y% | — |
| 函数 | X% | Y% | — |
| 语句 | X% | Y% | — |

### 覆盖率结果：通过 / 失败

### 已修复内容
- [ ] 覆盖率工具配置/修正
- [ ] 清理排除项（删除了 N 个生产文件排除项）
- [ ] 修复了 N 个失败的测试
- [ ] 编写了 N 个新的测试文件（列出它们）
- [ ] 扩展了 N 个现有测试文件以增加覆盖率
- [ ] 重构了 N 个文件以提高可测试性

### 剩余差距（需要人工审查）
仅列出无法自动修复的问题：
- 复杂的业务逻辑，正确的测试断言需要领域知识
- 需要真实 API 凭据或环境设置的集成测试
- 无法在不进行重大架构更改的情况下达到 80% 覆盖率的文件（解释原因）
```

---

## 完成

总结：
- 修复前后的总体覆盖率与 80% 门槛（通过或失败）
- 编写测试文件和添加的测试数量
- 重构以提高可测试性的文件数量
- 任何需要人工审查的剩余 **必须修复** 项目
