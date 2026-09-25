# /understand-dashboard

启动 Understand Anything 仪表板以可视化当前项目的知识图谱。

## 操作说明

1. 确定项目目录和数据目录：
   - 如果 `$ARGUMENTS` 包含路径，则将其用作项目目录
   - 否则，使用当前工作目录
   - 优先使用存在的旧版 `.understand-anything/` 数据目录，否则使用 `.ua/`

   使用 Bash 工具解析：
   ```bash
   PROJECT_ARG="$ARGUMENTS"
   if [ -n "$PROJECT_ARG" ]; then
     PROJECT_DIR=$(cd "$PROJECT_ARG" 2>/dev/null && pwd -P)
   else
     PROJECT_DIR=$(pwd -P)
   fi

   if [ -z "$PROJECT_DIR" ] || [ ! -d "$PROJECT_DIR" ]; then
     echo "Error: Project directory not found: ${PROJECT_ARG:-$PWD}"
     exit 1
   fi

   if [ -d "$PROJECT_DIR/.understand-anything" ]; then
     UA_DIR="$PROJECT_DIR/.understand-anything"
   else
     UA_DIR="$PROJECT_DIR/.ua"
   fi
   ```

2. 检查项目目录中是否存在 `$UA_DIR/knowledge-graph.json`。如果不存在，提示用户：
   ```
   未找到知识图谱。请先运行 /understand 分析此项目。
   ```

   使用 Bash 工具检查：
   ```bash
   if [ ! -f "$UA_DIR/knowledge-graph.json" ]; then
     echo "未找到知识图谱。请先运行 /understand 分析此项目。"
     exit 1
   fi
   ```

3. 查找仪表板代码。仪表板位于插件根目录的 `packages/dashboard/` 相对路径下。按顺序检查这些路径并使用第一个存在的：
   - `${CLAUDE_PLUGIN_ROOT}/packages/dashboard/`（Claude 代码运行时根目录，最高优先级）
   - `~/.understand-anything-plugin/packages/dashboard/`（通用符号链接，所有安装）
   - 从 `~/.agents/skills/understand-dashboard` 真实路径向上两级（自相对回退）
   - 从 `~/.copilot/skills/understand-dashboard` 真实路径向上两级（Copilot 个人技能回退）
   - 常见的基于克隆的安装根目录：
     - `~/.codex/understand-anything/understand-anything-plugin/packages/dashboard/`
     - `~/.opencode/understand-anything/understand-anything-plugin/packages/dashboard/`
     - `~/.pi/understand-anything/understand-anything-plugin/packages/dashboard/`
     - `~/understand-anything/understand-anything-plugin/packages/dashboard/`

   使用 Bash 工具解析：
   ```bash
   SKILL_REAL=$(realpath ~/.agents/skills/understand-dashboard 2>/dev/null || readlink -f ~/.agents/skills/understand-dashboard 2>/dev/null || echo "")
   SELF_RELATIVE=$([ -n "$SKILL_REAL" ] && cd "$SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
   COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-dashboard 2>/dev/null || readlink -f ~/.copilot/skills/understand-dashboard 2>/dev/null || echo "")
   COPILOT_SELF_RELATIVE=$([ -n "$COPILOT_SKILL_REAL" ] && cd "$COPILOT_SKILL_REAL/../.." 2>/dev/null && pwd || echo "")

   PLUGIN_ROOT=""
   for candidate in \
     "${CLAUDE_PLUGIN_ROOT}" \
     "$HOME/.understand-anything-plugin" \
     "$SELF_RELATIVE" \
     "$COPILOT_SELF_RELATIVE" \
     "$HOME/.codex/understand-anything/understand-anything-plugin" \
     "$HOME/.opencode/understand-anything/understand-anything-plugin" \
     "$HOME/.pi/understand-anything/understand-anything-plugin" \
     "$HOME/understand-anything/understand-anything-plugin"; do
     if [ -n "$candidate" ] && [ -d "$candidate/packages/dashboard" ]; then
       PLUGIN_ROOT="$candidate"; break
     fi
   done

   if [ -z "$PLUGIN_ROOT" ]; then
     echo "Error: Cannot find the understand-anything plugin root."
     echo "Checked:"
     echo "  - ${CLAUDE_PLUGIN_ROOT:-<unset CLAUDE_PLUGIN_ROOT>}"
     echo "  - $HOME/.understand-anything-plugin"
     echo "  - ${SELF_RELATIVE:-<unresolved path derived from ~/.agents/skills/understand-dashboard>}"
     echo "  - ${COPILOT_SELF_RELATIVE:-<unresolved path derived from ~/.copilot/skills/understand-dashboard>}"
     echo "  - $HOME/.codex/understand-anything/understand-anything-plugin"
     echo "  - $HOME/.opencode/understand-anything/understand-anything-plugin"
     echo "  - $HOME/.pi/understand-anything/understand-anything-plugin"
     echo "  - $HOME/understand-anything/understand-anything-plugin"
     echo "请确保您遵循了平台的安装说明。"
     exit 1
   fi

   DASHBOARD_DIR="$PLUGIN_ROOT/packages/dashboard"
   ```

4. **快速路径 — 首先尝试预构建的查看器（无需安装，无需构建）。** 每个发布版本都附带一个自包含的查看器 tarball；将其绑定到已安装的插件版本运行：
   ```bash
   : "${PLUGIN_ROOT:?Run step 3 first so PLUGIN_ROOT is set}"
   : "${PROJECT_DIR:?Run step 1 first so PROJECT_DIR is set}"
   PLUGIN_VERSION=$(node -p "require('$PLUGIN_ROOT/package.json').version")
   VIEWER_URL="https://github.com/Egonex-AI/Understand-Anything/releases/download/v${PLUGIN_VERSION}/understand-anything-viewer.tgz"
   npx --yes "$VIEWER_URL" "$PROJECT_DIR"
   ```
   在后台运行。它打印与开发服务器相同的 `🔑  Dashboard URL` 行：
   - 如果出现该行，**跳过步骤 5-6** 并继续步骤 7。
   - 如果进程退出且未打印该行（此版本没有发布资源，或无网络），则回退到步骤 5-6。

5. 回退：如果需要，安装依赖项并构建：
   ```bash
   : "${PLUGIN_ROOT:?Run step 3 first so PLUGIN_ROOT is set}"
   DASHBOARD_DIR="${DASHBOARD_DIR:-$PLUGIN_ROOT/packages/dashboard}"
   cd "$DASHBOARD_DIR" && (pnpm install --frozen-lockfile 2>/dev/null || pnpm install)
   ```
   然后确保核心包已构建（仪表板依赖于它）：
   ```bash
   : "${PLUGIN_ROOT:?Run step 3 first so PLUGIN_ROOT is set}"
   cd "$PLUGIN_ROOT" && pnpm --filter @understand-anything/core build
   ```

6. 回退：启动指向项目知识图谱的 Vite 开发服务器：
   ```bash
   : "${PROJECT_DIR:?Run step 1 first so PROJECT_DIR is set}"
   : "${DASHBOARD_DIR:?Run step 5 first so DASHBOARD_DIR is set}"
   cd "$DASHBOARD_DIR" && GRAPH_DIR="$PROJECT_DIR" npx vite --host 127.0.0.1
   ```
   在后台运行，以便用户可以继续工作。

7. **从服务器输出中捕获访问令牌 URL。** 服务器（查看器或 Vite）打印类似以下内容的行：
   ```
   🔑  Dashboard URL: http://127.0.0.1:<PORT>?token=<TOKEN>
   ```
   提取包括 `?token=` 参数的完整 URL。令牌是访问知识图谱数据所需的 — 没有它，仪表板将显示“需要访问令牌”的网关。

8. 向用户报告，包括完整的令牌化 URL：
   ```
   Dashboard started at http://127.0.0.1:<PORT>?token=<TOKEN>
   Viewing: $UA_DIR/knowledge-graph.json

   仪表板在后台运行。在终端中按 Ctrl+C 停止它。
   ```
   **重要：** 始终在您分享的 URL 中包含 `?token=` 参数。如果您遗漏它，用户将被令牌网关阻止，并必须手动在终端输出中查找令牌。

## 注意事项

- 快速路径（步骤 4）从 GitHub 发布下载版本绑定的自包含查看器 — 插件目录中未安装任何内容，且不运行构建
- 仪表板自动在默认浏览器中打开（查看器和 Vite 的 `--open`）
- 如果端口 5173 已被占用，则选择下一个可用端口（两种路径）
- 在回退中，`GRAPH_DIR` 环境变量告诉开发服务器在哪里查找知识图谱
