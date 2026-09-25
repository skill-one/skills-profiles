# 获取代码库知识

在 `docs/codebase/` 目录下生成七个已填充的文档，涵盖有效参与项目所需的所有内容。仅记录可从文件或终端输出生成的信息——绝不推断或假设。

## 输出契约（必需）

完成前，所有以下内容必须为真：

1. `docs/codebase/` 目录下仅存在这些文件：`STACK.md`、`STRUCTURE.md`、`ARCHITECTURE.md`、`CONVENTIONS.md`、`INTEGRATIONS.md`、`TESTING.md`、`CONCERNS.md`。
2. 每个声明均可追溯到源文件、配置或终端输出。
3. 未知项标记为 `[TODO]`；依赖团队意图的决策标记为 `[ASK USER]`。
4. 每个文档包含一个简短的“证据”列表，包含具体文件路径。
5. 最终响应包含编号的 `[ASK USER]` 问题以及意图与现实之间的差异。

## 工作流程

复制并跟踪此清单：

```
- [ ] 第一阶段：运行扫描，阅读意图文档
- [ ] 第二阶段：调查每个文档区域
- [ ] 第三阶段：在 `docs/codebase/` 中填充所有七个文档
- [ ] 第四阶段：验证文档，展示发现，解决所有 `[ASK USER]` 项
```

## 聚焦区域模式

如果用户提供聚焦区域（例如：“仅架构”或“测试与关注”）：

1. 始终完整运行第一阶段。
2. 首先完整完成聚焦区域文档。
3. 对于尚未分析的、非聚焦文档，保留必需部分并标记未知项为 `[TODO]`。
4. 仍然对所有七个文档运行第四阶段验证循环，然后输出最终结果。

### 第一阶段：扫描和阅读意图

1. 从目标项目根目录运行扫描脚本：
   ```bash
   python3 "$SKILL_ROOT/scripts/scan.py" --output docs/codebase/.codebase-scan.txt
   ```
   其中 `$SKILL_ROOT` 是技能文件夹的绝对路径。适用于 Windows、macOS 和 Linux。

   **快速启动：** 如果你有路径内联：
   ```bash
   python3 /绝对路径/to/skills/acquire-codebase-knowledge/scripts/scan.py --output docs/codebase/.codebase-scan.txt
   ```

2. 搜索 `PRD`、`TRD`、`README`、`ROADMAP`、`SPEC`、`DESIGN` 文件并阅读它们。
3. 在阅读任何源代码之前，总结声明中的项目意图。

### 第二阶段：调查

使用扫描输出为每个七个模板回答问题。加载 [`references/inquiry-checkpoints.md`](references/inquiry-checkpoints.md) 获取每个模板的完整问题列表。

如果栈不明确（多个清单文件、不熟悉的文件类型、没有 `package.json`），加载 [`references/stack-detection.md`](references/stack-detection.md)。

### 第三阶段：填充模板

从 `assets/templates/` 复制每个模板到 `docs/codebase/`。按此顺序填充：

1. [STACK.md](assets/templates/STACK.md) — 语言、运行时、框架、所有依赖项
2. [STRUCTURE.md](assets/templates/STRUCTURE.md) — 目录布局、入口点、关键文件
3. [ARCHITECTURE.md](assets/templates/ARCHITECTURE.md) — 层级、模式、数据流
4. [CONVENTIONS.md](assets/templates/CONVENTIONS.md) — 命名、格式化、错误处理、导入
5. [INTEGRATIONS.md](assets/templates/INTEGRATIONS.md) — 外部 API、数据库、认证、监控
6. [TESTING.md](assets/templates/TESTING.md) — 框架、文件组织、模拟策略
7. [CONCERNS.md](assets/templates/CONCERNS.md) — 技术债务、错误、安全风险、性能瓶颈

对于无法从代码中确定的任何内容使用 `[TODO]`。当正确答案需要团队意图时使用 `[ASK USER]`。

### 第四阶段：验证、修复、确认

在最终确定前运行此强制验证循环：

1. 根据 `references/inquiry-checkpoints.md` 验证每个文档。
2. 对于每个非平凡的声明，确认至少存在一个证据参考。
3. 如果任何必需部分缺失或不支持：
   - 修复文档。
   - 重新运行验证。
4. 重复直到所有七个文档通过。

然后展示所有七个文档的摘要，将每个 `[ASK USER]` 项作为编号问题列出，并突出第一阶段中意图与现实之间的差异。

验证通过标准：

- 没有不受支持的声明。
- 没有空的必需部分。
- 未知项使用 `[TODO]` 而非假设。
- 团队意图差距明确标记为 `[ASK USER]`。

---

## 注意事项

**单体仓库：** 根 `package.json` 可能没有源代码——检查 `workspaces`、`packages/` 或 `apps/` 目录。每个工作区可能有独立的依赖项和约定。分别映射每个子包。

**过时的 README：** README 通常描述的是预期架构，而非当前架构。在将任何 README 声明视为事实之前，先与实际文件结构进行交叉引用。

**TypeScript 路径别名：** `tsconfig.json` `paths` 配置意味着像 `@/foo` 这样的导入不会直接映射到文件系统。在记录结构之前将别名映射到实际路径。

**生成/编译输出：** 从 `dist/`、`build/`、`generated/`、`.next/`、`out/` 或 `__pycache__/` 中记录模式。这些都是产物——仅记录源代码约定。

**`.env.example` 揭示必需的配置：** 密码从不提交。读取 `.env.example`、`.env.template` 或 `.env.sample` 以发现必需的环境变量。

**`devDependencies` ≠ 生产栈：** 仅 `dependencies`（或等效项，例如 `[tool.poetry.dependencies]`）在生产中运行。将 linters、formatters 和测试框架作为开发工具单独记录。

**测试 TODOs ≠ 生产债务：** `test/`、`tests/`、`__tests__/` 或 `spec/` 中的 TODO 是覆盖率差距，不是生产技术债务。在 `CONCERNS.md` 中将它们分开。

**高变更文件 = 易碎区域：** 最近 git 历史中频繁出现的文件具有最高的修改率，可能隐藏着复杂性。始终在 `CONCERNS.md` 中注明它们。

---

## 反模式

| ❌ 不要 | ✅ 而是这样做 |
|---------|--------------|
| "使用 Clean Architecture，包含 Domain/Data 层。"（当没有这样的目录时） | 仅陈述实际显示的目录结构。 |
| "这是一个 Next.js 项目。"（未经检查 `package.json`） | 首先检查 `dependencies`。陈述实际存在的内容。 |
| 从变量名如 `dbUrl` 推测数据库 | 检查清单中的 `pg`、`mysql2`、`mongoose`、`prisma` 等。 |
| 记录 `dist/` 或 `build/` 的命名模式作为约定 | 仅源文件。 |

---

## 增强扫描输出部分

`scan.py` 脚本现在除了原始输出外，还会生成以下部分：

- **代码指标** — 总文件数、按语言统计的代码行数、最大文件（复杂性信号）
- **CI/CD 管道** — 检测到的 GitHub Actions、GitLab CI、Jenkins、CircleCI 等
- **容器与编排** — Docker、Docker Compose、Kubernetes、Vagrant 配置
- **安全与合规** — Snyk、Dependabot、SECURITY.md、SBOM、安全策略
- **性能与测试** — 基准配置、性能分析标记、负载测试工具

在第二阶段使用这些部分来指导调查问题，并识别特定于工具的模式。

---

## 随附资源

| 资源 | 加载时机 |
|-------|-------------|
| [`scripts/scan.py`](scripts/scan.py) | 第一阶段 — 首先运行，在阅读任何代码之前（需要 Python 3.8+） |
| [`references/inquiry-checkpoints.md`](references/inquiry-checkpoints.md) | 第二阶段 — 加载用于每个模板的调查问题 |
| [`references/stack-detection.md`](references/stack-detection.md) | 第二阶段 — 仅当栈不明确时 |
| [`assets/templates/STACK.md`](assets/templates/STACK.md) | 第三阶段步骤 1 |
| [`assets/templates/STRUCTURE.md`](assets/templates/STRUCTURE.md) | 第三阶段步骤 2 |
| [`assets/templates/ARCHITECTURE.md`](assets/templates/ARCHITECTURE.md) | 第三阶段步骤 3 |
| [`assets/templates/CONVENTIONS.md`](assets/templates/CONVENTIONS.md) | 第三阶段步骤 4 |
| [`assets/templates/INTEGRATIONS.md`](assets/templates/INTEGRATIONS.md) | 第三阶段步骤 5 |
| [`assets/templates/TESTING.md`](assets/templates/TESTING.md) | 第三阶段步骤 6 |
| [`assets/templates/CONCERNS.md`](assets/templates/CONCERNS.md) | 第三阶段步骤 7 |

模板使用模式：

- 默认模式：仅完成每个模板中的“核心部分（必需）”。
- 扩展模式：仅在仓库复杂性证明需要时添加可选部分。
