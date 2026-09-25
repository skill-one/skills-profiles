# LobeHub 测试指南

## 快速参考

**命令：**

```bash
# 运行特定测试文件
bunx vitest run --silent='passed-only' '[file-path]'

# 数据库包（client-db, PGlite — 默认，跳过 BM25/pg_search）
cd packages/database && bunx vitest run --silent='passed-only' '[file]'

# 数据库包（server-db, Postgres — BM25/pgvector 对比，CI 测量覆盖率的）
cd packages/database && TEST_SERVER_DB=1 bunx vitest run --silent='passed-only' '[file]'
```

**永远不要运行** `bun run test` — 它会运行所有 3000+ 测试（约 10 分钟）。

> **数据库模型/仓库：** `packages/database/src/models/**` 或 `src/repositories/**` 下每个新文件在同一个 PR 中都附带一个同名的 `__tests__/<name>.test.ts`。
> 使用 `getTestDB()`（集成风格）获取真实数据库，用 `describe.skipIf(!isServerDB)` 保护 BM25/全文搜索块，并始终测试用户隔离。有关设置、模式陷阱以及客户端与服务器数据库分区的信息，请参阅
> `references/db-model-test.md`。

## 测试类别

| 类别   | 位置                    | 配置                          |
| ------ | ----------------------- | ----------------------------- |
| Webapp | `src/**/*.test.ts(x)`       | `vitest.config.ts`              |
| 包     | `packages/*/**/*.test.ts`   | `packages/*/vitest.config.ts`   |
| 桌面端  | `apps/desktop/**/*.test.ts` | `apps/desktop/vitest.config.ts` |

## 核心原则

1. **优先使用 `vi.spyOn` 而不是 `vi.mock`** - 更具针对性，更易于维护。根 Vitest 配置不会自动恢复模拟；在测试清理时使用 `vi.restoreAllMocks()` 恢复监视器。
2. **测试行为而非实现细节**
   - 将原生 `node:test` CI 检查保留在 `.github/scripts/` 中，位于应用程序 Vitest 发现路径之外。当混合使用多个测试运行器时，在推送之前验证预期的运行器和拥有 Vitest 项目的文件发现。
3. **修复 Bug 的回归测试** - 包含一个在没有修复时失败而在修复后通过回归测试；当失败容易重现时，先编写失败的测试。**跳过**纯风格/CSS 修复（选择器、悬停、遮罩、间距、颜色），当唯一实际的断言是样式表中源字符串匹配时——这不是值得发布的回归测试。
4. **不添加新组件测试** - 仅更新现有的 React 组件测试。复杂逻辑应提取到钩子中进行测试。

## UI 库模拟 (@lobehub/ui/base-ui)

**默认：不要模拟 `@lobehub/ui/base-ui` — 渲染真实组件。**
`vitest.config.mts` 将库的内部 MotionProvider 重定向到静态桩 (`tests/mocks/lobehubUiMotionProvider.tsx`)，因此 base-ui 组件在测试中渲染而不需要应用级别的 ConfigProvider。`在测试中用 <ConfigProvider>（或 <MotionProvider>）包裹你的应用程序` 意味着重定向未生效（例如，本地 Vitest 配置）——不要手动模拟每个组件来修复它。

当测试确实需要简化的 DOM 时，通过真实模块组合规范桩而不是编写封闭工厂（封闭工厂在库迁移组件的导入路径时会被破坏）：

```typescript
vi.mock('@lobehub/ui/base-ui', async (importOriginal) => ({
  ...(await importOriginal<object>()),
  ...(await import('~base-ui-stubs')).baseUiStubs,
}));
```

`~base-ui-stubs` (`tests/mocks/baseUiStubs.tsx`) 覆盖 ActionIcon / Button / Text / Tag / Avatar / Alert / toast / confirmModal / createModal 的标准 aria 语义。当断言需要自定义的 testid 规范时，每个文件的工厂仍然可以——但保持它组合在 `importOriginal` 上，以便未知的导出永远不会丢失。

## 详细指南

有关特定测试场景，请参阅 `references/`：

- **数据库模型测试**：`references/db-model-test.md`
- **Electron IPC 测试**：`references/electron-ipc-test.md`
- **Zustand Store Action 测试**：`references/zustand-store-action-test.md`
- **Agent 运行时 E2E 测试**：`references/agent-runtime-e2e.md`
- **桌面端控制器测试**：`references/desktop-controller-test.md`

## 修复失败测试 — 优化还是删除？

当测试因实现变更（非 Bug）而失败时，在盲目修复之前进行评估：

### 保留并修复（更新测试数据/断言）

- **行为测试**：验证代码做什么的测试（输出、副作用、用户可见行为）。只需更新模拟数据格式或预期值。
  - 示例：工具数据结构从 `{ name }` 变更为 `{ function: { name } }` → 更新模拟数据
  - 示例：输出格式从 `Current date: YYYY-MM-DD` 变更为 `Current date: YYYY-MM-DD (TZ)` → 更新预期字符串

### 删除（过度指定，低价值）

- **参数转发测试**：断言精确内部函数调用参数的测试（例如，`expect(internalFn).toHaveBeenCalledWith(expect.objectContaining({ exact params }))`）——这些测试在每次重构时都会失败，并且重复了行为测试已经涵盖的内容。
- **实现耦合测试**：验证代码内部如何工作的测试，而不是它产生什么。如果更高层次的测试已经涵盖了相同的行为，低层次的测试会增加维护成本而没有覆盖增益。

### 决策检查清单

1. 测试是否验证**外部可观察的行为**（API 响应、数据库写入、渲染输出）？→ **保留**
2. 测试是否仅验证**内部连接**（哪个函数接收哪些参数）？→ 检查行为测试是否已经涵盖。如果是 → **删除**
3. 相同的行为是否已在**更高集成级别**进行测试？→ 删除低层次的重复
4. 测试是否会在**下一次常规重构**时再次失败？→ 考虑提升到集成级别或删除

### 编写新测试时

- 优先使用**集成级别断言**（验证最终输出）而不是**白盒断言**（验证内部调用）
- 仅对稳定、面向公共的契约使用 `expect.objectContaining` —— 不要用于随着重构而变化的内部参数形状
- 在边界（数据库、网络、外部服务）处模拟，而不是在内部模块之间模拟
