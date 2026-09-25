# /understand-domain

从代码库中提取业务领域知识——领域、业务流程和流程步骤——并在仪表盘中生成交互式水平流程图。

## 工作原理

- 如果知识图谱已存在（`.ua/knowledge-graph.json`，或者当该目录存在时为遗留的 `.understand-anything/knowledge-graph.json`），则从中派生领域知识（快速，无需文件扫描）
- 如果知识图谱不存在，则执行轻量级扫描：文件树 + 入口点检测 + 抽样文件
- 使用 `--full` 标志强制即使存在知识图谱也要进行全新扫描

## 使用说明

### 阶段 0：解析 `PROJECT_ROOT`

将 `PROJECT_ROOT` 设置为当前工作目录。

**工作树重定向。** 如果 `PROJECT_ROOT` 位于 git 工作树中（非主分支检出），则将输出重定向到主仓库根目录。由 Claude Code 管理的工作树是暂时的——会话结束时，写入其中的数据目录（`.ua/`，或遗留的 `.understand-anything/`）将被销毁，领域图谱也随之消失（问题 #133）。通过比较 `git rev-parse --git-dir` 和 `git rev-parse --git-common-dir` 来检测工作树；在正常检出或子模块中它们解析为相同的路径，在工作树中它们不同，`--git-common-dir` 的父级是主仓库根目录。

```bash
COMMON_DIR=$(git -C "$PROJECT_ROOT" rev-parse --git-common-dir 2>/dev/null)
GIT_DIR=$(git -C "$PROJECT_ROOT" rev-parse --git-dir 2>/dev/null)
if [ -n "$COMMON_DIR" ] && [ -n "$GIT_DIR" ]; then
  COMMON_ABS=$(cd "$PROJECT_ROOT" && cd "$COMMON_DIR" 2>/dev/null && pwd -P)
  GIT_ABS=$(cd "$PROJECT_ROOT" && cd "$GIT_DIR" 2>/dev/null && pwd -P)
  if [ -n "$COMMON_ABS" ] && [ "$COMMON_ABS" != "$GIT_ABS" ]; then
    MAIN_ROOT=$(dirname "$COMMON_ABS")
    if [ -d "$MAIN_ROOT" ] && [ "${UNDERSTAND_NO_WORKTREE_REDIRECT:-0}" != "1" ]; then
      echo "[understand-domain] 检测到 git 工作树位于 $PROJECT_ROOT"
      echo "[understand-domain] 重定向输出到主仓库根目录：$MAIN_ROOT"
      echo "[understand-domain] (设置 UNDERSTAND_NO_WORKTREE_REDIRECT=1 以保持 PROJECT_ROOT 为工作树。) "
      PROJECT_ROOT="$MAIN_ROOT"
    fi
  fi
fi
```

使用 `$PROJECT_ROOT`（而非裸 CWD）来引用后续阶段中的“当前项目” / `<project-root>`。

**解析数据目录 `$UA_DIR`。** 所有 Understand-Anything 实物都存放在项目的数据目录中。在已知 `$PROJECT_ROOT` 的情况下，现在解析一次 `$UA_DIR`，并在后续阶段的读写中重用 `$UA_DIR`：
```bash
UA_DIR="$PROJECT_ROOT/$([ -d "$PROJECT_ROOT/.understand-anything" ] && echo .understand-anything || echo .ua)"
```
这会保留已存在的遗留 `.understand-anything/` 目录（现有项目无需迁移即可继续工作），否则使用新的 `.ua/`。由于每个阶段可能在一个新的 shell 中运行，像 `$PROJECT_ROOT` 一样传递 `$UA_DIR`，如果后续命令块需要它，则使用上述行重新解析它。

**重要：** 不要假设插件根目录仅仅是技能路径字符串上方的两个目录。在许多安装中 `~/.agents/skills/understand-domain` 是一个指向真实插件检出的符号链接。优先使用运行时提供的插件根目录（用于 Claude），然后回退到通用符号链接、技能符号链接解析和常见的基于克隆的安装路径。

像这样解析插件根目录：

```bash
SKILL_REAL=$(realpath ~/.agents/skills/understand-domain 2>/dev/null || readlink -f ~/.agents/skills/understand-domain 2>/dev/null || echo "")
SELF_RELATIVE=$([ -n "$SKILL_REAL" ] && cd "$SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-domain 2>/dev/null || readlink -f ~/.copilot/skills/understand-domain 2>/dev/null || echo "")
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
  echo "错误：无法找到 understand-anything 插件根目录。"
  echo "检查："
  echo "  - ${CLAUDE_PLUGIN_ROOT:-<未设置 CLAUDE_PLUGIN_ROOT>}"
  echo "  - $HOME/.understand-anything-plugin"
  echo "  - ${SELF_RELATIVE:-<从 ~/.agents/skills/understand-domain 派生的未解析路径>}"
  echo "  - ${COPILOT_SELF_RELATIVE:-<从 ~/.copilot/skills/understand-domain 派生的未解析路径>}"
  echo "  - $HOME/.codex/understand-anything/understand-anything-plugin"
  echo "  - $HOME/.opencode/understand-anything/understand-anything-plugin"
  echo "  - $HOME/.pi/understand-anything/understand-anything-plugin"
  echo "  - $HOME/understand-anything/understand-anything-plugin"
  echo "确保插件已正确安装。"
  exit 1
fi
```

使用 `$PLUGIN_ROOT` 来引用后续阶段中的代理定义。

### 阶段 1：检测现有图谱

1. 检查 `$UA_DIR/knowledge-graph.json` 是否存在
2. 如果它存在并且 `--full` 未传递，则在从中派生之前检查新鲜度：
   - 从图谱元数据中读取 `project.gitCommitHash` 作为 `GRAPH_COMMIT_RAW`。切换到 `$PROJECT_ROOT`，将其解析为提交，在 Git diff 中使用它之前，比较解析的提交与 `git rev-parse HEAD`，并检查项目范围的已提交和工作树更改：
     ```bash
     GRAPH_COMMIT=$(git rev-parse --verify --end-of-options "${GRAPH_COMMIT_RAW}^{commit}" 2>/dev/null)
     git rev-parse HEAD
     git diff --name-only "$GRAPH_COMMIT" HEAD -- .
     git diff --cached --name-only -- .
     git diff --name-only -- .
     git ls-files --others --exclude-standard -- .
     ```
   - `-- .` 路径规范是必需的：仅修改兄弟单仓库项目的提交不应使此图谱过时。当项目 diff 为空时，哈希不匹配本身不是过时。
   - 在每个命令的输出中忽略选定的数据目录（`.ua/` 或遗留的 `.understand-anything/`），因为它包含生成的图谱实物，而不是项目源代码漂移。
   - 如果已提交的 diff 或任何工作树命令报告项目文件，则警告领域提取可能忽略这些更改。建议：运行 `/understand` 刷新知识图谱。
   - 仅当 `GRAPH_COMMIT_RAW` 解析成功时才运行提交 diff。如果图谱提交或 Git 元数据丢失、无效或不可用，则给出简短的尽力而为警告并继续，而不是阻止。
3. 在此预检之后，继续阶段 3（从图谱派生）。
4. 否则，继续阶段 2（轻量级扫描）。当使用 `--full` 时，跳过此预检，因为命令执行全新扫描而不是消耗现有图谱。

### 阶段 2：轻量级扫描（路径 1）

预处理脚本不会生成领域图谱——它生成**原始材料**（文件树、入口点、导出/导入），以便领域分析代理可以专注于实际领域分析，而不是花费数十个工具调用探索代码库。将其视为一份作弊表：廉价的 Python 预处理 → 昂贵的 LLM 获得干净的小输入 → 以较低成本获得更好的结果。

1. 运行随此技能捆绑的预处理脚本，并将阶段 0 中的 `$PROJECT_ROOT` 传递给它：
   ```
   python ./extract-domain-context.py "$PROJECT_ROOT"
   ```
   这会输出 `$UA_DIR/intermediate/domain-context.json`，其中包含：
   - 文件树（尊重 `.gitignore`）
   - 检测到的入口点（HTTP 路由、CLI 命令、事件处理器、cron 作业、导出处理器）
   - 文件签名（每个文件的导出、导入）
   - 每个入口点的代码片段（签名 + 几行）
   - 项目元数据（package.json、README 等）
2. 将生成的 `domain-context.json` 作为阶段 4 的上下文读取
3. 继续阶段 4

### 阶段 3：从现有图谱派生（路径 2）

1. 读取 `$UA_DIR/knowledge-graph.json`
2. 将图谱数据格式化为结构化上下文：
   - 所有节点及其类型、名称、摘要和标签
   - 所有边及其类型（尤其是 `calls`、`imports`、`contains`）
   - 所有层及其描述
   - 如果可用，则游览步骤
3. 这是领域分析器的上下文——无需读取文件
4. 继续阶段 4

### 阶段 4：领域分析

1. 从 `$PLUGIN_ROOT/agents/domain-analyzer.md` 读取领域分析器代理提示
2. 使用领域分析器提示 + 阶段 2 或 3 的上下文派发一个子代理
3. 代理将其输出写入 `$UA_DIR/intermediate/domain-analysis.json`

### 阶段 5：验证和保存

1. 读取领域分析输出
2. 使用标准图谱验证流程进行验证（现在模式支持领域/流程/步骤类型）
3. 如果验证失败，则记录警告但保存有效的部分（错误容忍）
4. 保存到 `$UA_DIR/domain-graph.json`
5. 清理 `$UA_DIR/intermediate/domain-analysis.json` 和 `$UA_DIR/intermediate/domain-context.json`

### 阶段 6：启动仪表盘

1. 自动触发 `/understand-dashboard` 以可视化领域图谱
2. 仪表盘将检测 `domain-graph.json` 并默认显示领域视图
