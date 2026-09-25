# Vitest 设置

检测项目类型，生成正确的 Vitest 配置，并创建可用的测试基础设施。这不是一份参考卡——这项技能会创建文件。

## 工作流程

1. **检测** — 扫描项目以确定类型和现有设置
2. **配置** — 生成针对环境的 vitest.config.ts
3. **搭建** — 创建测试设置、工具和一个示例测试
4. **连接** — 添加 package.json 脚本和 TypeScript 配置

## 第 1 步：检测项目类型

读取以下文件以确定项目：

```
package.json          → 依赖项、脚本、type 字段
tsconfig.json         → 路径、编译器选项
wrangler.toml         → Cloudflare Workers 项目
vite.config.ts        → 现有的 Vite 设置（扩展，不要替换）
vitest.config.ts      → 已经配置？只需填充空白
jest.config.*         → 迁移候选
src/                  → 源代码结构
```

将其分类为以下之一：

| 类型 | 信号 | 环境 |
|------|---------|-------------|
| **Cloudflare Workers** | wrangler.toml, @cloudflare/workers-types, cloudflare vite 插件 | `node` 与 Workers 特定设置 |
| **React (Vite)** | @vitejs/plugin-react, react-dom | `jsdom` 或 `happy-dom` |
| **React (SSR/TanStack Start)** | @tanstack/start, vinxi | 分割：`node` 用于服务器，`jsdom` 用于客户端 |
| **Node/Hono API** | hono, express, 没有 react-dom | `node` |
| **库** | exports 字段、没有框架依赖项 | `node` |

如果已经存在 `vite.config.ts`，则扩展它而不是创建单独的 vitest.config.ts — Vitest 本地读取 Vite 配置。

## 第 2 步：安装依赖项

根据检测到的类型生成安装命令：

```bash
# 基本（始终）
pnpm add -D vitest

# React 项目 — 添加 jsdom 和 Testing Library
pnpm add -D @vitest/coverage-v8 jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event

# Workers 项目 — 添加 Cloudflare 测试工具
pnpm add -D @vitest/coverage-v8 @cloudflare/vitest-pool-workers

# Node/Hono 项目
pnpm add -D @vitest/coverage-v8

# 如果从 Jest 迁移，还删除：
pnpm remove jest ts-jest @types/jest jest-environment-jsdom babel-jest
```

使用项目的包管理器（检查 pnpm-lock.yaml、yarn.lock、bun.lockb 或 package-lock.json）。

## 第 3 步：生成 vitest.config.ts

### Cloudflare Workers

```typescript
import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    globals: true,
    poolOptions: {
      workers: {
        wrangler: { configPath: "./wrangler.toml" },
      },
    },
  },
});
```

如果项目使用 Cloudflare Vite 插件（`@cloudflare/vite-plugin`），则将其集成到现有的 vite.config.ts 中：

```typescript
/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import { cloudflare } from "@cloudflare/vite-plugin";

export default defineConfig({
  plugins: [cloudflare()],
  test: {
    globals: true,
  },
});
```

### React (Vite)

```typescript
/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true,
  },
});
```

如果已经存在 vite.config.ts，则将其添加到 `test` 块中，而不是创建新文件。

### Node / Hono API

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
  },
});
```

### 带有覆盖率（添加到任何配置）

```typescript
  test: {
    // ... 现有配置
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      exclude: [
        "node_modules/",
        "**/*.config.*",
        "**/*.d.ts",
        "**/test/**",
      ],
    },
  },
```

## 第 4 步：生成测试设置文件

创建 `src/test/setup.ts`（仅限 React 项目）：

```typescript
import "@testing-library/jest-dom/vitest";
```

此单个导入添加了所有自定义匹配器（toBeInTheDocument、toHaveTextContent 等），并自动注册了 Vitest 的 `expect.extend`。

## 第 5 步：添加 TypeScript 配置

将 `tsconfig.json` 中的 compilerOptions 添加到：

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

对于具有多个 tsconfig 文件的项目（例如 tsconfig.app.json + tsconfig.node.json），将其添加到覆盖测试文件的 tsconfig 文件中——通常是根 tsconfig.json 或创建一个扩展它的 tsconfig.test.json。

## 第 6 步：添加 Package.json 脚本

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

不要覆盖现有脚本——与现有的合并。

## 第 7 步：生成示例测试

编写一个测试文件，展示此特定项目的正确模式。将其放在真实的源代码旁边，而不是在单独的 `__tests__` 目录中。

### 对于一个 Hono API 路由（例如 `src/routes/health.ts`）：

```typescript
import { describe, it, expect } from "vitest";
import { app } from "../index";

describe("GET /health", () => {
  it("returns 200 with status ok", async () => {
    const res = await app.request("/health");
    expect(res.status).toBe(200);

    const body = await res.json();
    expect(body).toEqual({ status: "ok" });
  });
});
```

### 对于一个 React 组件（例如 `src/components/Button.tsx`）：

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "./Button";

describe("Button", () => {
  it("renders with label", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: /click me/i })).toBeInTheDocument();
  });

  it("calls onClick when clicked", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await user.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### 对于一个工具函数（例如 `src/utils/format.ts`）：

```typescript
import { describe, it, expect } from "vitest";
import { formatCurrency } from "./format";

describe("formatCurrency", () => {
  it("formats whole numbers", () => {
    expect(formatCurrency(1000)).toBe("$1,000.00");
  });

  it("formats decimals", () => {
    expect(formatCurrency(49.9)).toBe("$49.90");
  });

  it("handles zero", () => {
    expect(formatCurrency(0)).toBe("$0.00");
  });
});
```

从项目中选择一个真实的文件进行测试。不要编造一个假的模块——示例测试应在设置后立即运行。

## 第 8 步：验证

运行测试以确认一切正常：

```bash
pnpm test:run
```

如果失败，诊断并修复。常见问题：

| 错误 | 修复 |
|-------|-----|
| `Cannot find module 'vitest'` | 检查安装完成，检查 `node_modules/.vitest` 是否存在 |
| `ReferenceError: describe is not defined` | 将 `globals: true` 添加到配置中，或添加 `types: ["vitest/globals"]` 到 tsconfig |
| `document is not defined` | 错误的环境——为 React 测试设置 `environment: "jsdom"` |
| `Cannot use import.meta` | 确保vitest.config使用 `.ts` 扩展名，项目具有 `"type": "module"` 或 Vite 处理转换 |
| Workers 绑定未定义 | 使用 `@cloudflare/vitest-pool-workers` 而不是普通的 vitest，检查 wrangler.toml 路径 |

---

## 模拟参考

这些模式是在设置完成后编写测试的。如果用户要求模拟示例，请将它们包含在示例测试中或 `src/test/examples.test.ts` 中。

### 模块模拟（vi.mock）

```typescript
import { vi, describe, it, expect } from "vitest";
import { getUser } from "./api";

vi.mock("./api", () => ({
  getUser: vi.fn(),
}));

it("mocks a module function", async () => {
  vi.mocked(getUser).mockResolvedValue({ id: 1, name: "Test" });
  const user = await getUser(1);
  expect(user.name).toBe("Test");
  expect(getUser).toHaveBeenCalledWith(1);
});
```

### 监控方法（vi.spyOn）

```typescript
it("spies on console.warn", () => {
  const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
  doSomethingThatWarns();
  expect(spy).toHaveBeenCalledOnce();
  spy.mockRestore();
});
```

### 假计时器

```typescript
import { vi, beforeEach, afterEach, it, expect } from "vitest";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-01-15T10:00:00Z"));
});

afterEach(() => {
  vi.useRealTimers();
});

it("uses controlled time", () => {
  expect(new Date().toISOString()).toBe("2026-01-15T10:00:00.000Z");
});
```

### 全局桩

```typescript
it("stubs fetch", async () => {
  const mockFetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ data: "test" }),
  });
  vi.stubGlobal("fetch", mockFetch);

  const res = await fetch("/api/data");
  expect(mockFetch).toHaveBeenCalledWith("/api/data");

  vi.unstubAllGlobals();
});
```

### 快照测试

```typescript
it("matches snapshot", () => {
  const result = generateConfig({ debug: true });
  expect(result).toMatchSnapshot();
});

it("matches inline snapshot", () => {
  expect({ status: "ok", count: 3 }).toMatchInlineSnapshot(`
    {
      "count": 3,
      "status": "ok",
    }
  `);
});
```

### 参数化测试

```typescript
describe.each([
  { input: "hello", expected: "HELLO" },
  { input: "world", expected: "WORLD" },
  { input: "", expected: "" },
])("toUpperCase($input)", ({ input, expected }) => {
  it(`returns ${expected}`, () => {
    expect(input.toUpperCase()).toBe(expected);
  });
});
```

---

## Jest 迁移

当检测到的项目具有 Jest（`jest.config.*`、`@types/jest`、`ts-jest` 在依赖项中）：

1. **生成 vitest.config.ts** 使用上述步骤
2. **更新现有测试文件中的导入**：

```typescript
// 之前
import { jest } from "@jest/globals";
jest.mock("./api");
jest.fn();
jest.spyOn(obj, "method");

// 之后
import { vi } from "vitest";
vi.mock("./api");
vi.fn();
vi.spyOn(obj, "method");
```

3. **删除 Jest 包**：
```bash
pnpm remove jest ts-jest @types/jest jest-environment-jsdom babel-jest @jest/globals
```

4. **更新 tsconfig** — 将 `"types": ["jest"]` 替换为 `"types": ["vitest/globals"]`

5. **运行测试** 并修复任何剩余问题

关键替换：

| Jest | Vitest |
|------|--------|
| `jest.fn()` | `vi.fn()` |
| `jest.mock()` | `vi.mock()` |
| `jest.spyOn()` | `vi.spyOn()` |
| `jest.useFakeTimers()` | `vi.useFakeTimers()` |
| `jest.clearAllMocks()` | `vi.clearAllMocks()` |
| `jest.requireActual()` | `vi.importActual()` |
| `@jest/globals` | `vitest` |
| `jest.config.js` | `vitest.config.ts` |

---

## 工作区设置（Monorepos）

对于具有多个包的 monorepo 项目：

```typescript
// vitest.workspace.ts
import { defineWorkspace } from "vitest/config";

export default defineWorkspace([
  "packages/*/vitest.config.ts",
]);
```

每个包都有自己的配置。工作区文件只是指向它们。

---

## 这项技能生成的内容

运行后，项目应具有：

- `vitest.config.ts`（或添加到现有 vite.config.ts 的测试块）
- `src/test/setup.ts`（仅限 React 项目）
- 更新的 `tsconfig.json` 带有 vitest/globals 类型
- 更新的 `package.json` 带有测试脚本
- 至少一个针对真实源代码的通过示例测试
- 安装的依赖项

测试应在第一次运行时通过。如果它们没有通过，请在完成之前修复它们。
