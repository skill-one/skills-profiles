# /understand

分析当前代码库并生成一个 `knowledge-graph.json` 文件，该文件将放置在项目的数据目录（`.ua/`，如果已存在则为传统的 `.understand-anything/`）。该文件为交互式仪表板提供支持，用于探索项目的架构。

## 选项

- `$ARGUMENTS` 可能包含：
  - `--full` — 强制进行完整重建，忽略任何现有的图
  - `--auto-update` — 启用自动图更新（将 `autoUpdate: true` 写入 `$UA_DIR/config.json`）
  - `--no-auto-update` — 禁用自动图更新（将 `autoUpdate: false` 写入 `$UA_DIR/config.json`）
  - `--review` — 运行完整的 LLM 图审阅器而不是内联确定性验证
  - `--language <lang>` — 在指定语言中生成所有文本内容（摘要、描述、标签、标题、languageNotes、languageLesson）。接受 ISO 639-1 代码（`zh`、`ja`、`ko`、`en`、`es`、`fr`、`de` 等）或友好名称（`chinese`、`japanese`、`korean`、`english`、`spanish` 等）。支持区域变体：`zh-TW`、`zh-HK` 等。默认为 `en`（英语）。将首选项存储在 `$UA_DIR/config.json` 中，以便在增量更新中保持一致性。
  - `--exclude <patterns>` — 用于排除分析额外文件/目录的逗号分隔的 glob 模式（例如，`--exclude "tests/*,docs/*"`）。这些模式比内置默认值和 `.understandignore` 规则具有更高的优先级。支持 gitignore 语法，包括 `!` 否定。
  - 目录路径（例如 `/path/to/repo` 或 `../other-project`） — 分析给定的目录而不是当前工作目录

---

## 进度报告

在执行过程中，在每个阶段转换时以及在进行批量处理时向用户报告进度。这使用户能够在分析可能需要很长时间的大型代码库时保持知情。

- **阶段转换**：在每个阶段的开始打印状态行：
  > `[Phase N/7] <phase name>...`
  >
  > 示例：`[Phase 2/7] Analyzing files (12 batches)...`

- **批量进度**：在阶段 2 中，报告每个批次的索引和总数：
  > `Analyzing batch X/N (files: foo.ts, bar.ts, ...)`（最多列出 3 个文件名，如果更多则省略 `...`）

- **阶段完成**：当阶段完成时，简要确认：
  > `Phase N complete. <结果的一行摘要>`
  >
  > 示例：`Phase 1 complete. 在 3 种语言中找到 247 个文件。`

---

## 阶段 0 — 预飞行

确定是运行完整分析还是增量更新。

1. **解析 `PROJECT_ROOT`**：
   - 解析 `$ARGUMENTS` 以查找非标志标记（任何不以 `--` 开头的参数）。如果找到，将其视为目标目录路径。
     - 如果路径是相对路径，则将其相对于当前工作目录解析。
     - 验证解析的路径是否存在并且是一个目录（运行 `test -d <path>`）。如果不存在或不是目录，则向用户报告错误并 **停止**。
     - 将 `PROJECT_ROOT` 设置为解析的绝对路径。
   - 如果未找到目录路径参数，则将 `PROJECT_ROOT` 设置为当前工作目录。
   - **工作树重定向**。如果 `PROJECT_ROOT` 位于 git 工作树内（不是主检出），则将输出重定向到主仓库。由 Claude Code 管理的工作树是暂时的——会话结束时，写入的数据目录（`.ua/` 或传统的 `.understand-anything/`）以及知识图谱都将被销毁（问题 #133）。通过比较 `git rev-parse --git-dir` 与 `git rev-parse --git-common-dir` 来检测工作树；在正常检出或子模块中，它们解析为相同的路径；在工作树中，它们不同，`--git-common-dir` 的父级是主仓库根目录。

     ```bash
     COMMON_DIR=$(git -C "$PROJECT_ROOT" rev-parse --git-common-dir 2>/dev/null)
     GIT_DIR=$(git -C "$PROJECT_ROOT" rev-parse --git-dir 2>/dev/null)
     if [ -n "$COMMON_DIR" ] && [ -n "$GIT_DIR" ]; then
       COMMON_ABS=$(cd "$PROJECT_ROOT" && cd "$COMMON_DIR" 2>/dev/null && pwd -P)
       GIT_ABS=$(cd "$PROJECT_ROOT" && cd "$GIT_DIR" 2>/dev/null && pwd -P)
       if [ -n "$COMMON_ABS" ] && [ "$COMMON_ABS" != "$GIT_ABS" ]; then
         MAIN_ROOT=$(dirname "$COMMON_ABS")
         if [ -d "$MAIN_ROOT" ] && [ "${UNDERSTAND_NO_WORKTREE_REDIRECT:-0}" != "1" ]; then
           echo "[understand] 在 $PROJECT_ROOT 检测到 git 工作树"
           echo "[understand] 重定向输出到主仓库根目录: $MAIN_ROOT"
           echo "[understand] (设置 UNDERSTAND_NO_WORKTREE_REDIRECT=1 以保持工作树中的 PROJECT_ROOT。) "
           PROJECT_ROOT="$MAIN_ROOT"
         fi
       fi
     fi
     ```

     如果您有意要为每个工作树生成独立的图（很少——大多数用户希望重定向），请设置 `UNDERSTAND_NO_WORKTREE_REDIRECT=1`。
- **确保插件已构建**。后续阶段将调用 Node 脚本，这些脚本导入 `@understand-anything/core`。在全新安装的情况下，`packages/core/dist/` 尚未存在——构建一次。

     **重要**：**不要**假设插件根目录仅仅是技能路径字符串上两级目录。在许多安装中，`~/.agents/skills/understand` 是指向真实插件检出的符号链接。优先使用运行时提供的插件根目录（对于 Claude），然后回退到通用符号链接、技能符号解析和常见的克隆安装路径。

     按如下方式解析插件根目录：

     ```bash
     SKILL_REAL=$(realpath ~/.agents/skills/understand 2>/dev/null || readlink -f ~/.agents/skills/understand 2>/dev/null || echo "")
     SELF_RELATIVE=$([ -n "$SKILL_REAL" ] && cd "$SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
     COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand 2>/dev/null || readlink -f ~/.copilot/skills/understand 2>/dev/null || echo "")
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
       if [ -n "$candidate" ] && [ -f "$candidate/package.json" ] && [ -f "$candidate/pnpm-workspace.yaml" ]; then
           PLUGIN_ROOT="$candidate"
           break
       fi
     done

     if [ -z "$PLUGIN_ROOT" ]; then
       echo "Error: 无法找到 understand-anything 插件根目录。"
       echo "检查:"
       echo "  - ${CLAUDE_PLUGIN_ROOT:-<unset CLAUDE_PLUGIN_ROOT>}"
       echo "  - $HOME/.understand-anything-plugin"
       echo "  - ${SELF_RELATIVE:-<从 ~/.agents/skills/understand 解析出的未解析路径>}"
       echo "  - ${COPILOT_SELF_RELATIVE:-<从 ~/.copilot/skills/understand 解析出的未解析路径>}"
       echo "  - $HOME/.codex/understand-anything/understand-anything-plugin"
       echo "  - $HOME/.opencode/understand-anything/understand-anything-plugin"
       echo "  - $HOME/.pi/understand-anything/understand-anything-plugin"
       echo "  - $HOME/understand-anything/understand-anything-plugin"
       echo "确保插件已正确安装。"
       exit 1
     fi

     if [ ! -f "$PLUGIN_ROOT/packages/core/dist/index.js" ]; then
       cd "$PLUGIN_ROOT" && (pnpm install --frozen-lockfile 2>/dev/null || pnpm install) && pnpm --filter @understand-anything/core build
     fi
     ```

     如果 `pnpm` 未安装，向用户报告："安装 Node.js ≥ 22 和 pnpm ≥ 10，然后重新运行 `/understand`。
