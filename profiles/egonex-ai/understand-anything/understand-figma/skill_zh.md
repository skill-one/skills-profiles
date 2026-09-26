# /understand-figma

分析 Figma 文件并在现有仪表板中生成交互式设计知识图谱。

## 前置条件

- **`FIGMA_TOKEN` 环境变量** — Figma 个人访问令牌（在 https://www.figma.com/settings 创建）。如果缺失，停止并提示用户：
  > 首先设置 Figma 令牌：在 figma.com/settings 创建一个，然后 `export FIGMA_TOKEN=<token>`。
- Node ≥ 22，pnpm ≥ 10。

> **安全提示：** 令牌仅从环境读取，仅在 `X-Figma-Token` 请求头中传输。切勿将其写入图谱、`meta.json`、日志或中间文件。此技能会向 `api.figma.com` 发起出站调用——与 `/understand` 不同，它并非完全离线。告知用户这一点一次。

## 阶段 0 — 预检查

1. 解析 `$ARGUMENTS` 获取 Figma URL 或纯文件键（非标志令牌），以及可选的 `--language <lang>`。
2. 将 `PROJECT_ROOT` 解析为当前工作目录。**一次性解析数据目录 `$UA_DIR` 并在每次读写中复用**：`UA_DIR="$PROJECT_ROOT/$([ -d "$PROJECT_ROOT/.understand-anything" ] && echo .understand-anything || echo .ua)"`——如果已存在 `.understand-anything/`，则使用它，否则使用新的 `.ua/`。由于每个阶段可能在一个新 shell 中运行，需像 `$PROJECT_ROOT` 一样传递 `$UA_DIR`，并在后续命令块需要时用相同行重新解析它。
3. 解析 `PLUGIN_ROOT` 并确保核心已构建（与 `/understand` 阶段 0.1.5 相同逻辑）。如果 `packages/core/dist/figma/index.js` 缺失，运行：
   ```bash
   cd "$PLUGIN_ROOT" && (pnpm install --frozen-lockfile 2>/dev/null || pnpm install) && pnpm --filter @understand-anything/core build
   ```
4. `mkdir -p $UA_DIR/intermediate`。

## 阶段 1 — 获取与解析（确定性）

运行捆绑的扫描脚本（`<SKILL_DIR>` 是此技能的目录）：

```bash
FIGMA_TOKEN="$FIGMA_TOKEN" node <SKILL_DIR>/figma-scan.mjs "$PROJECT_ROOT" "<url-or-key>"
```

它会写入 `$UA_DIR/intermediate/scan-manifest.json` 并打印节点计数。将计数传递给用户。如果它以非零状态退出，传递 stderr 并停止。

> 如果扫描打印 `UP_TO_DATE`，报告 "设计图谱对于此 Figma 文件版本已是最新" 并停止。要强制完全重建，请在环境中设置 `UNDERSTAND_FIGMA_FORCE=1` 重新运行。

## 阶段 2 — 分析（LLM 增强）

1. 读取 `scan-manifest.json`。将节点分组为约 15 个一批，尽可能按页面分组。
2. 对于每一批，使用 `design-analyzer` 代理定义（`agents/design-analyzer.md`）派生子代理。传递：
   - 节点批（`id`、`type`、`name`、`figmaMeta`、子名称、令牌使用情况），
   - 现有节点 ID 的完整列表，
   - `$INTERMEDIATE_DIR = $UA_DIR/intermediate`，
   - 批次编号用于输出命名。
   代理会写入 `analysis-batch-<N>.json`。
   如果提供了 `--language`，则附加 `$LANGUAGE_DIRECTIVE`（复用 `/understand` 的指令文本）。
3. **最多并发运行 5 批次**。如果一批失败，记录警告并继续——清单是一个坚实的基础。

## 阶段 3 — 合并

```bash
node <SKILL_DIR>/figma-merge.mjs "$PROJECT_ROOT"
```

它会合并 `scan-manifest.json` + `analysis-batch-*.json`，运行 `mergeDesignGraph`（验证、重新附加 `kind:"design"`），并写入 `knowledge-graph.json` + `meta.json`。传递打印的统计信息和任何非 `auto-corrected` 的问题。

## 阶段 4 — 保存与启动

1. 清理中间文件**除** `scan-manifest.json`：
   ```bash
   INTER="$UA_DIR/intermediate"
   find "$INTER" -mindepth 1 -maxdepth 1 -not -name 'scan-manifest.json' -exec rm -rf {} +
   ```
2. 报告摘要：项目名称、按节点类型的计数、按类型的边、图层、游览步骤，以及路径 `$UA_DIR/knowledge-graph.json`。
3. 自动启动仪表板，通过调用 `/understand-dashboard` 技能。
