# /printing-press-amend

将一个 dogfood 会话转换为一个公共图书馆中打印的 CLI 的 PR。

```bash
/printing-press-amend                 # 自动检测会话中的目标 CLI
/printing-press-amend superhuman      # 显式短名称
/printing-press-amend superhuman-pp-cli
/printing-press-amend "$PRESS_LIBRARY/superhuman"
```

这项技能存在于这个仓库（这台机器）中，并作用于公共图书馆中的打印 CLI。它是 `/printing-press-publish`（添加新的 CLI）、`/printing-press-polish`（发布前改进 CLI）和 `/printing-press-retro`（反思这台机器本身）的兄弟技能。这些都不涵盖发布后由真实会话摩擦驱动的 CLI 修订。

这项技能产生的工件在语义上是一个“补丁”（在 git/PR 的意义上），由公共图书馆的 `.printing-press-patches/` 目录跟踪（每个补丁一个文件）。内联 `// PATCH(...)` 源代码注释是可选的导航辅助工具，当它们使定制站点更容易进行 grep 时。斜杠技能名称为 `amend`，以区分现有的 `cli-printing-press patch` 二进制子命令（它通过 AST 注入预定义功能——不同的机制，不同的意图）。

## 设置

在其他任何操作之前：

<!-- PRESS_SETUP_CONTRACT_START -->
```bash
# min-binary-version: 4.0.0

# 首先推导范围——需要用于本地构建检测
_scope_dir="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
_scope_dir="$(cd "$_scope_dir" && pwd -P)"

# 当从 printing-press 仓库内部运行时，优先使用本地构建。
_press_repo=false
if [ -x "$_scope_dir/cli-printing-press" ] && [ -d "$_scope_dir/cmd/cli-printing-press" ]; then
  _press_repo=true
  export PATH="$_scope_dir:$PATH"
  echo "使用本地构建: $_scope_dir/cli-printing-press"
elif ! command -v cli-printing-press >/dev/null 2>&1; then
  if [ -x "$HOME/go/bin/cli-printing-press" ]; then
    echo "cli-printing-press 位于 ~/go/bin/cli-printing-press，但不在 PATH 上。"
    echo "将 GOPATH/bin 添加到您的 PATH:  export PATH=\"\$HOME/go/bin:\$PATH\""
  else
    echo "未找到 cli-printing-press 二进制。"
    echo "使用:  go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest"
  fi
  return 1 2>/dev/null || exit 1
fi

# 解析并输出代理必须用于每个后续 `cli-printing-press` 调用的绝对路径。`export PATH` 上的命令仅影响此单个 Bash 工具调用；后续调用会打开一个新的 shell，并针对用户的默认 PATH 解析裸 `cli-printing-press`，其中陈旧的全局版本可能会无声地遮蔽本地构建。代理捕获此标记并将绝对路径替换到每个后续调用中。
if [ "$_press_repo" = "true" ]; then
  PRINTING_PRESS_BIN="$_scope_dir/cli-printing-press"
else
  PRINTING_PRESS_BIN="$(command -v cli-printing-press 2>/dev/null || true)"
fi
if ! command -v go >/dev/null 2>&1; then
  echo ""
  echo "[setup-error] 未找到 Go 工具链。"
  echo ""
  echo "此 Printing Press 流程运行基于 Go 的构建或验证命令。"
  echo "从 https://go.dev/dl/ 安装 Go 1.26.6 或更高版本，然后使用以下命令验证："
  echo "  go version"
  echo "然后重新运行此技能。"
  echo ""
  return 1 2>/dev/null || exit 1
fi
echo "PRINTING_PRESS_BIN=$PRINTING_PRESS_BIN"

_pp_semver_lt() {
  if [ -z "${PP_SEMVER_A:-}" ] || [ -z "${PP_SEMVER_B:-}" ]; then
    echo "[setup-error] semver 比较输入缺失。" >&2
    return 2
  fi
  awk -v a="${PP_SEMVER_A:-}" -v b="${PP_SEMVER_B:-}" 'BEGIN {
    split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) {
      if ((x[i] + 0) < (y[i] + 0)) exit 0
      if ((x[i] + 0) > (y[i] + 0)) exit 1
    }
    exit 1
  }'
}

_pp_go_version_norm() {
  printf '%s\n' "${PP_GO_VERSION_INPUT:-}" | sed -nE 's/.*go([0-9]+)\.([0-9]+)(\.([0-9]+))?.*/\1.\2.\4/p' | sed -E 's/\.$/.0/'
}

_pp_check_go_currency() {
  _pp_go_installed="$(PP_GO_VERSION_INPUT="$(go env GOVERSION 2>/dev/null)" _pp_go_version_norm)"
  _pp_go_required="$(PP_GO_VERSION_INPUT="$(go version "$PRINTING_PRESS_BIN" 2>/dev/null)" _pp_go_version_norm)"
  PP_SEMVER_A="$_pp_go_installed"
  PP_SEMVER_B="$_pp_go_required"
  if [ -z "$_pp_go_installed" ] || [ -z "$_pp_go_required" ] || ! _pp_semver_lt; then
    return 0
  fi

  echo ""
  if [ "${GOTOOLCHAIN:-auto}" = "local" ]; then
    echo "[setup-error] 此 cli-printing-press 二进制需要 Go $_pp_go_required 或更高版本（已安装: $_pp_go_installed）。"
    echo "GOTOOLCHAIN=local 禁用自动工具链下载，因此后续的 Go 质量门禁会失败。"
    echo "从 https://go.dev/dl/ 安装 Go $_pp_go_required 或更高版本，或取消设置 GOTOOLCHAIN。"
    echo ""
    return 1
  fi

  echo "[go-toolchain-old] 此 cli-printing-press 二进制需要 Go $_pp_go_required 或更高版本（已安装: $_pp_go_installed）。"
  echo "默认的 GOTOOLCHAIN 行为可能会在 Go 命令期间下载所需的工具链。"
  echo ""
  return 0
}
_pp_check_go_currency || { return 1 2>/dev/null || exit 1; }

PRESS_BASE="$(basename "$_scope_dir" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]/-/g; s/^-+//; s/-+$//')"
if [ -z "$PRESS_BASE" ]; then
  PRESS_BASE="workspace"
fi

PRESS_SCOPE="$PRESS_BASE-$(printf '%s' "$_scope_dir" | shasum -a 256 | cut -c1-8)"
PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
PRESS_RUNSTATE="$PRESS_HOME/.runstate/$PRESS_SCOPE"
PRESS_LIBRARY="$PRESS_HOME/library"
PRESS_MANUSCRIPTS="$PRESS_HOME/manuscripts"
PRESS_CURRENT="$PRESS_RUNSTATE/current"

_pp_check_disk_space() {
  _pp_disk_warn_kb="${PRINTING_PRESS_DISK_WARN_KB:-3145728}"
  _pp_disk_fail_kb="${PRINTING_PRESS_DISK_FAIL_KB:-524288}"
  case "$_pp_disk_warn_kb$_pp_disk_fail_kb" in
    ""|*[!0-9]*) return 0 ;;
  esac

  _pp_disk_path="$PRESS_HOME"
  while [ ! -e "$_pp_disk_path" ] && [ "$_pp_disk_path" != "/" ]; do
    _pp_disk_path="$(dirname "$_pp_disk_path")"
  done

  _pp_disk_avail_kb="$(df -Pk "$_pp_disk_path" 2>/dev/null | awk 'BEGIN {
    if ((getline header) <= 0 || (getline record) <= 0) exit
    field_count = split(record, fields)
    if (field_count >= 4) print fields[4]
  }')"
  case "$_pp_disk_avail_kb" in
    ""|*[!0-9]*) return 0 ;;
  esac

  if [ "$_pp_disk_avail_kb" -lt "$_pp_disk_fail_kb" ]; then
    echo ""
    echo "[setup-error] Printing Press 工作空间卷上的磁盘空间严重不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_FAIL_KB=$_pp_disk_fail_kb"
    echo "释放磁盘空间或将 PRINTING_PRESS_HOME 设置为具有更多空间的卷，然后重新运行此技能。"
    echo ""
    return 1
  fi

  if [ "$_pp_disk_avail_kb" -lt "$_pp_disk_warn_kb" ]; then
    echo ""
    echo "[low-disk] Printing Press 工作空间卷上的可用空间不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_WARN_KB=$_pp_disk_warn_kb"
    echo "此流程可能需要几 GiB 用于生成的文件、Go 构建缓存、模块下载或仓库克隆。"
    echo ""
  fi
}
_pp_check_disk_space || { return 1 2>/dev/null || exit 1; }

mkdir -p "$PRESS_RUNSTATE" "$PRESS_LIBRARY" "$PRESS_MANUSCRIPTS" "$PRESS_CURRENT"

# --- 货币底线检查（独立、失败打开）---
# 对低于发布支持的底线的二进制进行硬停止，以便 amend 不会重新生成存在已知问题的 CLI。仓库检出从源代码构建并豁免。底线被钳制在 <= 最新，因此一个坏值不会使每个安装都损坏。每次运行时都重新获取，而不是重用 printing-press 预检的 TTL 缓存：amend 是低频操作，因此有界的 curl + go-list 成本不值得在这里为其创建自己的缓存。
if [ "$_press_repo" != "true" ] && command -v curl >/dev/null 2>&1; then
  _semver_lt() {
    if [ -z "${PP_SEMVER_A:-}" ] || [ -z "${PP_SEMVER_B:-}" ]; then
      echo "[setup-error] semver 比较输入缺失。" >&2
      return 2
    fi
    awk -v a="${PP_SEMVER_A:-}" -v b="${PP_SEMVER_B:-}" 'BEGIN {
      split(a, x, "."); split(b, y, ".")
      for (i = 1; i <= 3; i++) {
        if ((x[i] + 0) < (y[i] + 0)) exit 0
        if ((x[i] + 0) > (y[i] + 0)) exit 1
      }
      exit 1
    }'
  }
  _floor_installed=$("$PRINTING_PRESS_BIN" version --json 2>/dev/null | sed -nE 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p')
  _floor_doc=$(curl -fsSL --max-time 5 \
    https://raw.githubusercontent.com/mvanhorn/cli-printing-press/main/supported-versions.txt 2>/dev/null || true)
  _floor_min=$(printf '%s\n' "$_floor_doc" | sed -nE 's/^min_supported=//p' | head -n 1)
  _floor_reason=$(printf '%s\n' "$_floor_doc" | sed -nE 's/^reason=//p' | head -n 1)
  _floor_latest=""
  if command -v go >/dev/null 2>&1; then
    _floor_latest=$(go list -m -json github.com/mvanhorn/cli-printing-press/v4@latest 2>/dev/null | sed -nE 's/^[[:space:]]*"Version":[[:space:]]*"v?([^"]+)".*/\1/p' | head -n 1)
  fi
  if [ -n "$_floor_min" ] && [ -n "$_floor_installed" ] && [ -n "$_floor_latest" ] &&
     PP_SEMVER_A="$_floor_installed" PP_SEMVER_B="$_floor_min" _semver_lt &&
     ! PP_SEMVER_A="$_floor_latest" PP_SEMVER_B="$_floor_min" _semver_lt; then
    echo ""
    echo "[upgrade-required] printing-press v$_floor_min 是最低支持版本（您有 v$_floor_installed）"
    echo "PRESS_REQUIRED_MIN=$_floor_min"
    echo "PRESS_REQUIRED_INSTALLED=$_floor_installed"
    echo "PRESS_REQUIRED_REASON=$_floor_reason"
    echo ""
  fi
fi
```
<!-- PRESS_SETUP_CONTRACT_END -->

在运行设置合约后，从标准输出捕获 `PRINTING_PRESS_BIN=<abs-path>` 行。**此技能中后续的每个 `cli-printing-press ...` 调用都必须使用该绝对路径**（替换值，而不是 `$PRINTING_PRESS_BIN` 标记的文本）—— `export PATH` 上的命令仅影响它运行的单个 Bash 工具调用，因此后续调用会打开一个新的 shell，其中裸 `cli-printing-press` 会解析用户默认的 `PATH`，而陈旧的全球版本可能会遮蔽本地构建。

如果设置输出了 `[go-toolchain-old]` 或 `[low-disk]`，向用户显示建议，除非设置也输出了 `[setup-error]`。`[go-toolchain-old]` 意味着后续的 Go 命令可能会下载所需的工具链或在下载被阻止时失败；`[low-disk]` 意味着此运行可能需要几 GiB 用于生成的文件、Go 构建缓存、模块下载或仓库克隆。

在捕获二进制路径后，检查二进制版本兼容性。从此技能的 YAML 前置读取 `min-binary-version` 字段。运行 `<PRINTING_PRESS_BIN> version --json` 并从输出中解析版本。使用 semver 规则将其与 `min-binary-version` 进行比较。如果安装的二进制版本比最低版本旧，请立即停止并告诉用户：“cli-printing-press 二进制 vX.Y.Z 比最低要求的 vA.B.C 旧。运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 更新。”

如果设置合约输出了 `[upgrade-required]` 块，则安装的二进制版本低于发布的**货币底线**（`PRESS_REQUIRED_MIN`）——旧版本会重新生成存在已知问题的 CLI（`PRESS_REQUIRED_REASON`）。这是一个硬性门槛，与 `min-binary-version` 不同：不要在那种二进制上 amend 或重新生成。通过 `AskUserQuestion` 提供一键升级——**是——立即升级**（运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest`，重新捕获 `PRINTING_PRESS_BIN`，然后继续）或**取消**（停止运行）。没有跳过并继续；低于底线，唯一的路径是升级或中止。如果升级命令失败，请显示并停止。

## 阶段 0 — 输入模式检测

此技能接受两种输入来源为后续修补提供查找列表：Claude 代码会话转录本（dogfood 模式，当前行为）和用户在斜杠命令提示符中提供的询问（直接输入模式，v0.2 中添加）。这两种模式仅在阶段 1 中分歧；阶段 2 及以后是模式无关的，并消耗具有相同形状的已打类型查找列表，无论来源如何。

在阶段 1 运行之前决定模式。

### 检测标准

读取斜杠命令提示符正文和对话上下文中的立即调用轮次。将其分类为以下四个分支之一：

- **`MODE=direct`** — 提示符包含具体的 CLI 名称，并且至少有一个直接输入信号：
  - 针对 CLI 的动作动词：`rename`、`add`、`remove`、`fix`、`sniff`、`discover`
  - 用户希望添加的明确 URL（例如，`https://example.com/feed/x`）
  - 枚举的 Feeds、命令、端点或功能列表
  - 类似于“这些想法”、“这些功能”、“具有以下”的措辞
- **`MODE=dogfood`** — 提示符为空，或命名一个没有询问的 CLI（“修订 superhuman CLI”），或明确引用会话（“我刚刚 dogfooded”、“这次会话的摩擦”、“来自我今天的会话”）
- **`MODE=both`** — 提示符清楚地引用两者：会话和特定的询问（“我 dogfooded 这次会话，还希望添加功能 X”、“除了我遇到的摩擦之外，请添加命令 Y”）
- **模糊** — 只有一个信号存在（命名 CLI 但没有动词，或动词没有目标 CLI，或询问措辞使其可能是摩擦报告或新的询问）。通过 `AskUserQuestion` 向用户询问：

  > “有两种方式为这次 amend 源查找。哪种适用？
  >   1. 矿掘当前会话转录本（dogfood 模式）
  >   2. 使用我刚刚输入的询问（直接输入模式）
  >   3. 两者——将转录本摩擦与我的询问结合”

当完全没有斜杠命令提示符时：`MODE=dogfood`。这保留了规范的用户体验——`/printing-press-amend` 后面什么都没有仍然按 v0.1 的方式工作。

### 持久化模式

将解析的模式写入 `$PRESS_RUNSTATE/current/mode.txt`，以便后续阶段（和恢复的运行）可以读取它：

```bash
echo "$MODE" > "$PRESS_RUNSTATE/current/mode.txt"
```

### 输出

阶段 0 向阶段 1 发出一行：

```yaml
mode: <dogfood|direct|both>
```

阶段 1 根据此值分支——dogfood 查找流经 `### 1a`，直接输入查找流经 `### 1b`，组合运行按顺序执行这两个子部分。阶段 2 及以后完全忽略模式——查找列表是合同。

当 `MODE=dogfood` 时，仅运行 `### 1a`。当 `MODE=direct` 时，仅运行 `### 1b`。当 `MODE=both` 时，首先运行 `### 1a`，然后运行 `### 1b`，并将两个查找列表合并（ID 不冲突的合并，1b 从 1a 停止的地方继续编号）。

### 1a. Dogfood 模式（MODE=dogfood）

阅读 `references/transcript-parsing.md` 获取完整流程。本节子部分执行的摘要：

1. **解析活动会话转录本文件** — 从当前工作目录推导 `<project-dir-slug>`，按 mtime 列出 `~/.claude/projects/<slug>/*.jsonl`，选择最近修改的。始终通过 `AskUserQuestion` 在读取前与用户确认解析的路径——错误文件选择会摄入来自错误会话的摩擦。

2. **遍历转录本并提取摩擦信号** — 非零退出代码、错误消息、手写的 API 负载（例如，应该是 CLI 命令的直接 `curl` POST）、重试失败模式、代理评论（如“X 不存在” / “X 返回 400”）、缺少标志引用、静默空返回、身份验证混乱。每个信号都携带时间戳 + 类别 + 逐字证据 + 它参考的 `<slug>-pp-cli`。

3. **将每个信号分类为 Bug 或功能**，用一行理由。Bug = CLI 行为不正确；功能 = CLI 行为缺失。分类是代理的最佳理解；用户在 U4 范围检查点确认或覆盖。

4. **自动检测目标 CLI** — 统计 signals 中每个 `<slug>-pp-cli` 的出现次数，提议最常被使用的 CLI 作为默认值。使用 `AskUserQuestion` 进行确认（单个 CLI：简单是/否；多个接近：从列表中选择）。当用户传递了显式的 `<cli-name-or-path>` 参数时，跳过自动检测。

5. **解析目标路径和发布状态** — 接受简称、全名或绝对路径（根据 R4）。将输入规范化为裸 CLI slugs，然后通过在公共库中查找该 slugs 来解析发布状态（当本地克隆存在时为 `~/printing-press-library/library/*/<slug>`，否则通过 `gh api` 使用相同路径）。不要从本地工作副本的 git 远程中推断发布状态，也不要将缺少的 `$PRESS_LIBRARY/<slug>` 工作副本视为未发布。如果 slugs 在公共库中找到，记录 `target_category`、`published_status: published`，并将运行路由到受管理的克隆上游 PR 路径。仅在 slugs 缺失于公共库时使用 `published_status: local-only`。类别由 U7 的 PR 打开阶段需要，在此处捕获，以避免重新推导。

由 1a 发出的每个发现都带有 `provenance: transcript`。输出流到 Phase 2，作为 `references/transcript-parsing.md` 中记录的结构化发现列表。

### 1b. 直接输入模式（MODE=direct）

阅读 `references/direct-input-parsing.md` 了解完整流程（引入于 v0.2）。本小节总结其功能：

1. **读取斜杠命令提示正文** 以及触发技能的即时代理消息轮次 — 这些包含用户的逐字询问（例如，“将 Digg 1000 重命名为 Digg，添加这些四个源：...，探测新端点”）。没有 transcript 确认；跳过 1a 运行的 U1 transcript-path 模态。

2. **解析目标 CLI** — 与 1a 步骤 4-5 相同的名称解析规则（根据 R4），但 CLI 通常已经在提示中命名。通过正则表达式提取（`<slug>-pp-cli` 或 "the <slug> CLI"）；如果缺失，则询问用户。

3. **使用 `references/direct-input-parsing.md` 中的标准将询问解析为结构化发现**。每个询问映射到一个带有类型 `kind` 字段的发现：
   - `rename` — "rename X to Y" / "call it X instead of Y" → `classification: feature`
   - `add-command` — "add command X" / "add subcommand X" → `classification: feature`
   - `add-feed` — "add feed <url>" / 用户希望添加的枚举 URL（每个 URL 一个发现）→ `classification: feature`
   - `add-endpoint` — "add endpoint <url>" / 明确的 API 路径 → `classification: feature`
   - `fix-bug` — "fix X" / "X is broken" / "X returns null" → `classification: bug`
   - `sniff` — "sniff for new APIs" / "find new endpoints" / "discover more" → 路由到 `### 1b.i` 中的 sniff 子程序

4. **每个发现记录用户的逐字措辞** 在 `evidence` 中，以便 U4 范围确认模态显示用户实际写了什么。

5. **边缘情况** — 多 CLI 询问拆分为两个单独运行（v0.2 范围外；询问用户选择一个）。歧义动词（没有具体说明的 `update X`）触发 `AskUserQuestion` 澄清而不是猜测。

由 1b 发出的每个发现都带有 `provenance: user-ask`（或 `provenance: sniff` 对于由 sniff 子程序产生的发现）。输出流到 Phase 2，作为与 1a 使用的相同结构化发现列表形状。

### 1b.i. Sniff 发现子程序

当解析标准将任何 1b 询问标记为 `kind: sniff`（如 "sniff for new APIs"、"find new endpoints"、"discover more endpoints in <site>"）时触发。Sniff 是按运行可选的 — 除非用户命名它，否则永远不会调用。当没有 sniff 发现时，完全跳过此子程序。

**步骤 1 — 解析目标源 URL。** 读取目标 CLI 的发布 manifest（`~/printing-press-library/library/<category>/<slug>/.printing-press.json`）并提取 `source_url`（或作为后备的 `spec_url`）。类别在 1b 步骤 2 中解析。

如果这两个字段都没有设置，则内联询问用户：

> "Sniff 需要一个目标 URL — 粘贴您希望探测的源站点，或跳过此运行的 sniff 发现？"

如果用户跳过，则从活动列表中删除 sniff 发现并继续处理其他 1b 发现。如果用户粘贴了 URL，则用于步骤 2-3。

**步骤 2 — 首先运行 crowd-sniff（快速，无需浏览器）。** 替换 `<PRINTING_PRESS_BIN>` 为设置时捕获的绝对路径：

```bash
<PRINTING_PRESS_BIN> crowd-sniff --site "$SOURCE_URL" --json > /tmp/amend-sniff-crowd.json
crowd_exit=$?
```

`crowd-sniff` 查询 npm SDKs 和 GitHub 代码搜索以发现候选端点 — 无需浏览器。典型运行时间不到一分钟。

**步骤 3 — 可选的浏览器 sniff（仅当用户选择更深入的探测时）。** 当用户的询问明确命名基于浏览器的探测（"sniff with browser"、"do a deep sniff"）AND 已经有捕获的 HAR 时，运行：

```bash
<PRINTING_PRESS_BIN> browser-sniff --har "$HAR_PATH" --json > /tmp/amend-sniff-browser.json
browser_exit=$?
```

此技能在 v0.2 中本身不协调 HAR 捕获 — 捕获由用户驱动（用户在 Chrome 中打开源站点，导出 HAR，并将技能指向它）或跳过深度 sniff 并附带说明。v0.3 可能扩展技能通过 claude-in-chrome MCP 驱动捕获；v0.2 范围外。

**步骤 4 — 将发现转换为发现。** 对于 sniff 输出中的每个候选端点，将一个发现追加到 1b 发现列表：

- `id: F<n>`（解析询问后的下一个可用编号）
- `kind: add-endpoint`
- `classification: feature`
- `evidence: "discovered via crowd-sniff: <endpoint-path>"`（适用时为 `browser-sniff`）
- `target_cli: <slug>-pp-cli`
- `rationale: <sniff 输出中的一行摘要（如果可用），否则 "sniff 候选，用户确认">`
- `provenance: sniff`

默认情况下在 Phase 3 将其归类为 Tier 3（精炼/架构）— 用户可以审查并将单个条目提升为 Tier 2（如果它们是高优先级）。

**步骤 5 — 降级路径。**

| 条件 | 行为 |
|------|------|
| `.printing-press.json` 缺少 `source_url` AND 用户在询问时跳过 | 删除 sniff 发现；继续处理其他 1b 发现；记录 "sniff 跳过 — 无源 URL"。 |
| `crowd-sniff` 退出非零 | 记录错误；跳过 sniff 发现；继续处理其他 1b 发现。不要中止 amend 运行。 |
| `crowd-sniff` 返回零候选端点 | 而不是添加什么，发出一个条目到延迟发现列表（"sniff 运行，未发现新端点"）— 为用户提供记录。 |
| 浏览器 sniff 请求但无 HAR 可用 | 记录；回退到 crowd-sniff 结果。 |

**步骤 6 — 向用户展示来源。** 在 Phase 3 范围确认模态中，sniff 源的发现按 `(sniff)` 来源标签分组，以便用户决定是否作为一个组保留，例如：

```
Tier 3 — 精炼 / 架构 (5)
  F8  add-endpoint /v1/feeds/stars (sniff)
  F9  add-endpoint /v1/feeds/new (sniff)
  F10 add-endpoint /v1/feeds/activity (sniff)
  ...
```

## Phase 2 — 预检查点守卫

在用户看到范围菜单之前运行两个守卫。任何一个都可以抑制发现或中止运行。

### 2a. PR 交叉引用（抑制重复提议）

对于 Phase 1 的每个发现，搜索 `mvanhorn/printing-press-library` 中的开放 + 最近合并的 PRs 以查找匹配项。重复检测标准（按优先级顺序）：(1) 目标 CLI 的目录路径与 PR 的更改文件列表重叠，(2) 发现的类别 + 理由中的关键词与 PR 标题或正文匹配。

```bash
# 替换 <PRINTING_PRESS_BIN> 使用为设置时捕获的绝对路径。
# 此阶段使用 gh，而不是 press 二进制文件。

# 触发此 CLI 的 Open PRs
gh pr list --repo mvanhorn/printing-press-library \
  --search "in:title,body <slug>" --state open --limit 20 \
  --json number,title,state,headRefName,files

# 最近合并的 PRs（最后 90 天）触发此 CLI。
# 可移植地计算 "90 天前" — `date -v-90d` 仅限 BSD/macOS，`date -d`
# 仅限 GNU/Linux。首先尝试 GNU，回退到 BSD，然后到 python3。如果
# 所有形式都失败，则明确报错而不是让 dedup 守卫无声地退出并带有空的 `merged:>` 限定符。
ninety_days_ago=$(date -u -d '90 days ago' +%Y-%m-%d 2>/dev/null \
  || date -u -v-90d +%Y-%m-%d 2>/dev/null \
  || python3 -c 'import datetime; print((datetime.datetime.now(datetime.UTC).date() - datetime.timedelta(days=90)).isoformat())' 2>/dev/null)
if [ -z "$ninety_days_ago" ]; then
  echo "ERROR: 无法计算 90 天前的日期 — 无 GNU date、BSD date 或 python3。"
  exit 1
fi

gh pr list --repo mvanhorn/printing-press-library \
  --search "in:title,body <slug> merged:>$ninety_days_ago" \
  --state merged --limit 20 \
  --json number,title,state,mergedAt,headRefName,files
```

对于每个具有可能重复匹配的发现，内联显示：

> "发现 `F<n>` (`<category>`) 可能已由 PR #<num> 解决 — `<title>` (<state>, <date>)。跳过此发现？"

用户选项：跳过（转到延迟）、保留，或 "显示 PR #<num>"（打开 `gh pr view <num> --repo mvanhorn/printing-press-library --web`）。对于明显合并的匹配，默认为 "跳过"；对于开放 PR，默认为 "保留"（用户可能希望添加到正在进行的 PR 而不是打开新的）。

此守卫捕获了 2026-05-15 dogfood 的典型失败模式：当兄弟 CLI 几小时前已经发布了一个类似的 PR 时，提议自动刷新 Printing Press CLI。跳过的成本很低（用户可以通过自定义选择在 U4 重新添加）；重复检测的假阴性成本是拒绝的 PR + 审查者时间。

### 2b. 陈旧二进制检查（如果 dogfooded 二进制落后于发布则中止）

读取公共库的目标 CLI 的 `.printing-press.json` 以找到发布版本。与本地打印的 CLI 二进制报告进行比较。

```bash
# 读取发布版本（如果可用，则为受管理的克隆，否则通过 gh api）
if [ -f "$HOME/printing-press-library/library/<category>/<slug>/.printing-press.json" ]; then
  published=$(jq -r '.version // empty' "$HOME/printing-press-library/library/<category>/<slug>/.printing-press.json")
else
  published=$(gh api repos/mvanhorn/printing-press-library/contents/library/<category>/<slug>/.printing-press.json \
    --jq '.content' | base64 -d | jq -r '.version // empty')
fi

# 读取本地二进制版本（如果安装；用户使用此二进制 dogfooded）
local_ver=$(<slug>-pp-cli version --json 2>/dev/null | jq -r '.version // empty' || echo "")
```

如果 `local_ver` 比较于 `published`（语义版本比较）更旧，则干净地中止：

> "您 dogfooded 的 `<slug>-pp-cli` 版本为 v`<local_ver>`，但发布库版本为 v`<published>`。您遇到的摩擦可能已在发布版本中修复。运行：
>
>     go install github.com/mvanhorn/<slug>-pp-cli@latest
>
> ...然后重新运行 `/printing-press-amend` 后重新 dogfooded。中止此运行。"

边缘情况：如果 `.printing-press.json` 缺失或没有 `version` 字段，则跳过陈旧检查并附带说明。如果 CLI 仅限本地（尚未发布），则跳过检查。

### 输出

Phase 2 将（可能修剪的）发现列表输出到 Phase 3：

```yaml
findings_kept:
  - <Phase 1 的发现>
findings_suppressed:
  - id: F3
    reason: "重复 PR #571 (合并于 2026-05-13)"
target_binary_check: { local: "1.0.0", published: "1.0.0", status: "current" }
published_status: published
```

## Phase 3 — 范围确认检查点（用户参与 #1）

这是两个用户检查点中的第一个。到目前为止，所有内容都是只读发现；此检查点提交范围。

### 将幸存的发现分层

将发现分为三个层级：

- **Tier 1 — Bug** — 每个带有 `classification: bug` 的发现。CLI 行为不正确；修复恢复正确性。
- **Tier 2 — 解决即时会话痛苦的缺失功能** — `classification: feature` 发现与用户在会话中实际构建的手动解决方法相关联（即用户显然现在需要，而不是理论上）。
- **Tier 3 — 精炼 / 架构** — 剩余的 `classification: feature` 发现，这些是可取的或架构改进，而会话中没有立即的解决方法。

在问题之前内联显示分层列表：

```
为 <slug>-pp-cli 发现摩擦（12 个信号，2 个作为重复被抑制）：

Tier 1 — Bug (4)
  F1  草稿列表静默返回 400
  F4  消息查询返回数据：null
  F7  刷新令牌过期未在错误中显示
  F11 ai --query 返回代码 500

Tier 2 — 解决会话痛苦的缺失功能 (4)
  F2  没有 `drafts new` 命令（用户手动编写 writeMessage 负载）
  F5  没有 `--type sent` 用于线程列表（用户用消息查询解决）
  F8  没有 `--remind-in <duration>` 标志用于发送（用户手动重新标记草稿）
  F10 没有 `bootstrap` 到本地 SQLite（用户进行了 50+ 个线程 API 调用）

Tier 3 — 精炼 / 架构 (2)
  F12 `auth status` 在刷新过期时不链接到 `auth login`
  F13 doctor 未显示陈旧二进制警告与发布版本对比
```

### 通过 AskUserQuestion 选择范围

```
此补丁应覆盖哪个范围？
  1. 仅 Bug (Tier 1) — 4 个发现
  2. Bug + 即时功能 (Tier 1 + Tier 2) — 8 个发现
  3. 所有层级 (Tier 1 + Tier 2 + Tier 3) — 10 个发现
  4. 自定义选择 — 选择单个发现
```

`AskUserQuestion` 选项必须自包含（每个标签必须传达其作用，而无需依赖描述文本 — 一些 harness 隐藏描述）。

对于 **自定义选择** 路径：显示一个多选，包含每个发现的 id + 类别 + 一行理由；在继续之前确认用户选择的子集。

### 持久化排除的发现

对于每个不在确认范围内的发现，追加到在以下路径的延迟列表 markdown 文件：

```
$PRESS_MANUSCRIPTS/<api-slug>/<run-id>/proofs/<timestamp>-amend-<cli-name>-deferred.md
```

`<run-id>` 是此 amend 运行的全新时间戳 id（例如 `amend-2026-05-15T1432`）。将延迟文件格式化为 YAML 前置符 + 每个发现为一段 markdown 正文，以便未来在相同 CLI 上的 `/printing-press-amend` 运行可以重新显示项目。

```yaml
---
date: 2026-05-15
target_cli: superhuman-pp-cli
amend_run_id: amend-2026-05-15T1432
deferred_count: 2
---
```

然后每个延迟发现一段，包含：id、类别、分类、理由、证据、排除理由（例如 "用户仅选择 Tier 1"），以及 `still_relevant: unknown`。

在后续的 `/printing-press-amend` 运行中，Phase 3 应在 `$PRESS_MANUSCRIPTS/<api-slug>/` 中查找最新的 `*-deferred.md` 并为用户提供选项，以在此次运行的范围中包含任何仍然相关的项目。（实现说明：此重新显示逻辑在 v0.1 中提供；不要无声地重新添加 — 始终呈现并确认。）

### 边缘情况：无事可做

如果 Phase 2 抑制了所有发现（所有内容都是重复），Phase 3 清晰报告并退出，不打开菜单：

> "此会话的所有发现都已由现有 PR 解决。未发现新补丁。"

### 输出

Phase 3 输出到 Phase 4：

```yaml
published_status: published
scope_tier: bugs+features            # 或 bugs|all|custom
findings_active: [...]               # 用户确认的子集
findings_deferred_path: <路径>       # 延迟文件落地的位置
```

## Phase 4 — 计划 + 执行 + 验证（自主）

此阶段在检查点 1 和 2 之间运行，无需用户干预。用户不会看到逐个修复的细节；他们会在 Phase 6 PR-draft 检查点审查最终 diff。

### 步骤 1 — 设置受管理的克隆

根据计划中的 Pre-Implementation Decision：此技能直接在 `mvanhorn/printing-press-library` 的受管理克隆上操作，而不是在 `$PRESS_LIBRARY/<slug>/`。受管理的克隆位于：

```
$PRESS_HOME/.publish-repo-$PRESS_SCOPE
```

这是 `/printing-press-publish` 技能使用的相同克隆（该技能步骤 5）。重用它：

```bash
PUBLISH_REPO_DIR="$PRESS_HOME/.publish-repo-$PRESS_SCOPE"
PUBLISH_CONFIG="$PRESS_HOME/.publish-config-$PRESS_SCOPE.json"

if [ ! -d "$PUBLISH_REPO_DIR/.git" ]; then
  # 首次设置：有关完整检测的详细信息，请参阅 references/library-pr-plumbing.md（通过 gh api .../permissions.push 的推送与分支访问检测、SSH 与 HTTPS 协议检测、作用域克隆清理循环）。
  echo "未找到管理的克隆 — 正在初始化..."
  # ...（请参阅 library-pr-plumbing.md）
else
  # 从上游刷新。-f 在检出时将丢弃先前运行中遗留下来的任何本地编辑（在 Phase 4 的编辑和 Phase 7 的提交之间中止的运行），如果没有 -f，这些未提交的更改将阻止检出，并且后续的 reset --hard 不会运行。
  cd "$PUBLISH_REPO_DIR"
  git fetch upstream main
  git checkout -f main
  git reset --hard upstream/main
fi
```

CLI 在管理的克隆中的目录是 `$PUBLISH_REPO_DIR/library/<category>/<slug>/`。类别在 Phase 1 中已解析（或使用 `find "$PUBLISH_REPO_DIR/library" -maxdepth 2 -name "<slug>" -type d` 进行查找）。

```bash
CLI_DIR="$PUBLISH_REPO_DIR/library/<category>/<slug>"
```

本阶段的所有编辑都在 `$CLI_DIR` 内进行。切勿触碰 `$PRESS_LIBRARY/<slug>/` — 那是另一个工作副本，编辑它不会反映到 PR 中。

### 第 2 步 — 编写每次运行的计划文档

在编辑代码之前，在以下位置创建一个计划 Markdown 文件：

```
$PRESS_MANUSCRIPTS/<slug>/<run-id>/proofs/<timestamp>-amend-<cli-name>.md
```

镜像到 `/tmp/printing-press/amend/` 以便快速参考。计划文档包含：

- 前置内容：`date`、`target_cli`、`amend_run_id`、`scope_tier`、`findings_count`
- 每个活动发现一个部分：id、类别、分类、理由、目标文件（`$CLI_DIR/...` 路径）、预期行为变化、针对此发现的测试场景
- 风险和发现之间的依赖关系（如果有）

计划是决策形状，不是执行形状 — 实现者时间的排序在 Step 3 中进行。

### 第 3 步 — 执行计划（使用补丁合同）

对于依赖顺序中的每个发现：

1. 编辑 `$CLI_DIR` 下的目标文件。遵守 AGENTS.md 反重构规则（不手动编写响应构建器；新命令必须调用真实端点或通过 `// pp:client-call` / `// pp:novel-static-reference` 选项仅在真正有理由时从本地存储读取）。

2. 可选：在更改位置添加 `// PATCH(<简短原因>)` 源注释，当它有助于未来代理快速找到定制时。格式示例：

   ```go
   // PATCH(amend-2026-05-15: 将刷新令牌过期暴露给用户) — 之前在静默重试
   func (c *Client) Refresh(ctx context.Context) error {
       ...
   }
   ```

3. 创建一个补丁文件 `$CLI_DIR/.printing-press-patches/<id>.json`（文件名 = 补丁 `id`）。每个文件是一个自包含的补丁对象 — 每个补丁一个文件，因此同一 CLI 的并发 amend PR 不会在补丁元数据上冲突：

   ```json
   {
     "schema_version": 2,
     "id": "<api-slug>-refresh-token-expiry",
     "applied_at": "<YYYY-MM-DD>",
     "base_run_id": "<从 .printing-press.json 复制>",
     "base_printing_press_version": "<从 .printing-press.json 复制>",
     "summary": "fix(superhuman): 暴露刷新令牌过期；添加草稿新 + --type sent",
     "reason": "生成的 CLI 隐藏了过期的刷新令牌，并省略了实时 API 需要的工作流标志。",
     "files": [
       "internal/auth/refresh.go",
       "internal/cli/drafts.go",
       "internal/cli/threads.go"
     ],
     "call_sites": ["printRefreshTokenExpiry("],
     "validated_outcome": "publish validate passed; 专注草稿和刷新令牌检查通过",
     "findings_addressed": ["F1", "F2", "F5", "F7"]
   }
   ```

   如果 CLI 仍然发送传统的 `.printing-press-patches.json`（旧版打印，尚未规范化），仍然将您的条目作为新的 `.printing-press-patches/<id>.json` 文件写入 — 公共库的 normalize-patches 工作流在合并后合并这两种。不要追加到旧数组。

   如果您添加了 `// PATCH(...)` 注释，您也可以包括一个 `patch_count` 字段以方便审阅者。当没有添加源注释时，不要添加 `patch_count`。

   对于具有未来替代路径的临时补丁，在相同的补丁条目中包括上游交接字段：

   ```json
   {
     "deferred_to_upstream": [
       {
         "feature": "此打印 CLI 补丁应最终替代的生成器或上游 API 功能",
         "reason": "本地补丁为何有意为临时或特定 API."
       }
     ],
     "upstream_issue": "https://github.com/mvanhorn/cli-printing-press/issues/<n>"
   }
   ```

   `.printing-press-patches/<id>.json` 补丁文件是代码级定制强制性的。内联 `// PATCH(...)` 源注释是可选的导航辅助；公共库验证器不再强制执行标记/注释配对。有关权威规范，请参阅 `~/printing-press-library/AGENTS.md`。当定制的关键调用可以在文件仍然存在时消失时，请在 `call_sites` 或 `markers`（或 `marker`）中声明它，并保持这些针头在 `files[]` 中，以便 regen 和 `publish validate` 在它消失时失败。`files[]` 对每个针头都是必需的；那些文件之外的剩余匹配不计入。

   仅在补丁有意留下未来替代路径时使用 `deferred_to_upstream`：今天缺少公共 API 端点、命令依赖于非官方主机或备用身份源、实时响应形状从生成器假设中漂移，或者一旦打印机学习模式，修复将变得不必要。在这些情况下，首先搜索 `mvanhorn/cli-printing-press` 问题；重用匹配的问题或在使用库 PR 之前打开一个，然后将 `upstream_issue` 设置为该 URL。不要仅在 PR 正文留下机器级或 API 发布依赖。

4. **机器与打印 CLI 判断**（根据 AGENTS.md）：当发现的修复可以泛化到每个打印的 CLI（例如，“生成器应为任何线程列表命令发出 `--type sent`”）时，将其作为边缘情况暴露：

   > "发现 F5 (`--type sent` 缺失) 看起来是机器级修复 — 生成器模板 `internal/generator/templates/threads.go.tmpl` 应为具有此端点形状的每个 CLI 发出它，而不仅仅是 `<slug>-pp-cli`。推迟到 `/printing-press-retro` 跟进，还是特定 CLI 进行？"

   当推迟时，进入延迟列表，分类为 `machine-level`。当因为打印 CLI 需要立即进行狭窄修复，并且补丁仍然携带未来替代路径时，在使用库 PR 之前创建或重用上游打印机问题，将问题 URL 添加到补丁的 `.printing-press-patches/<id>.json`，并添加一个 `deferred_to_upstream` 条目命名应替代本地补丁的机器级或上游 API 条件。

### 第 4 步 — 验证

所有编辑完成后，运行合并验证器（将 `<PRINTING_PRESS_BIN>` 替换为设置时捕获的绝对路径）：

```bash
<PRINTING_PRESS_BIN> publish validate --dir "$CLI_DIR" --json > /tmp/amend-validate.json
exit_code=$?
```

`publish validate` 运行 manifest、phase5、govulncheck（针对此 CLI 的模块范围）、`go vet`、`go build`、`--help`、`--version`。退出 0 = 清洁。

### 第 5 步 — 失败时重试（最多 3 次迭代）

如果 `publish validate` 报告失败，解析 JSON 中的错误类别，尝试有针对性的修复，重新运行验证。最多 3 次迭代。迭代 3 后：

```bash
# 将进行中的计划 + 差异保存到临时位置
HELD_PATH="$PRESS_MANUSCRIPTS/<slug>/<run-id>/proofs/<timestamp>-amend-<cli-name>-INCOMPLETE.md"
git -C "$PUBLISH_REPO_DIR" diff > "${HELD_PATH%.md}.diff"
cp "$PLAN_PATH" "$HELD_PATH"
```

将最终错误日志显示给用户，不要自动打开 PR，退出。用户可以通过重新调用技能（Phase 1 检测到保留的计划并提议恢复）来继续。

### 第 6 步 — 检查补丁清单

此 amend 运行必须记录至少一个补丁 — 在 `.printing-press-patches/` 下 `<id>.json`（目录布局），或仅对于尚未规范化的 CLI，在旧版 `.printing-press-patches.json` 中的非空 `patches[]`。

```bash
dir_count=0
if [ -d "$CLI_DIR/.printing-press-patches" ]; then
  dir_count=$(find "$CLI_DIR/.printing-press-patches" -maxdepth 1 -name '*.json' ! -name '_meta.json' | wc -l | tr -d ' ')
fi
legacy_count=0
if [ -f "$CLI_DIR/.printing-press-patches.json" ]; then
  legacy_count=$(jq '(.patches // []) | length' "$CLI_DIR/.printing-press-patches.json")
fi
if [ "$dir_count" -eq 0 ] && [ "$legacy_count" -eq 0 ]; then
  echo "ERROR: 此 amend 运行必须在 .printing-press-patches/ 下记录至少一个补丁（或旧版 .printing-press-patches.json）。"
  exit 1
fi
```

缺失或空的补丁清单 → 在继续之前本地修复。

### 第 6 步 — 文档更新检查点

在 Phase 4 可以发出通过之前，检查每个新重命名或更改的用户界面命令、标志、工作流、运行时模式或 MCP 可见操作的确认发现和最终差异。每个此类更改都必须在同一公共库 PR 中提供文档：

- 在 `SKILL.md` 和 `README.md` 中添加或更新一个食谱。
- 添加或更新匹配的 Unique Features / Unique Capabilities 条目，以便生成的文档和代理面朝总结命名更改的工作流。
- 保持示例真实：命令、标志、位置参数和输出片段必须与 `$CLI_DIR` 中现在存在的代码匹配。
- 从公共库检出时，从公共库检出时运行 `python3 .github/scripts/verify-skill/verify_skill.py --dir "$CLI_DIR"`；否则运行打包验证器等效程序并记录命令。

如果任何必需的文档编辑或验证器结果缺失，停止并使用阻塞检查清单。阻塞检查清单命名命令和缺失的 README/SKILL/Unique Features 组件。在清空检查清单之前不要移动到 PR-draft 检查点。如果 amend 仅修复内部且没有用户界面行为变化，请在 Phase 4 输出中记录 `documentation_checkpoint: no-user-facing-doc-change`。

### 输出

Phase 4 输出到 Phase 5：

```yaml
plan_doc_path: <path>
managed_clone_dir: <path>
cli_dir_in_clone: <path>
findings_addressed: [...]
build_status: PASS|FAIL
test_status: PASS|FAIL
dogfood_status: PASS|FAIL|N/A    # PASS|FAIL 当 MODE=dogfood（或“两者”）时；始终 N/A 当 MODE=direct
validate_iterations: <n>
patch_entry_count: <n>
documentation_checkpoint: PASS|no-user-facing-doc-change
```

**`dogfood_status` 按模式。** 当 `MODE=dogfood` 时，该值反映消耗转录发现结果的 dogfood 验证步骤的结果（如果运行产生了干净的修复则 PASS，如果它暴露了回归则 FAIL）。当 `MODE=direct` 时，没有转录可以 dogfood 对抗 — 设置 `dogfood_status=N/A`。当 `MODE=both` 时，dogfood 验证仍然针对转录发现的一半运行；相应地设置 PASS/FAIL。此默认值必须在 Phase 4 结束时设置，以便 Phase 7 的 PR 正文和 Phase 8 的 RESULT 块永远不会发出空值。

## Phase 5 — PII 清理

阅读 `references/pii-scrubbing.md` 以获取完整程序。摘要：

清理有三个层，每个层都在临时暂存副本上操作（不在用户的会话转录或进行中的源代码上）：

1. **凭据** — 重用 `skills/printing-press-retro/references/secret-scrubbing.md` 中的正则表达式模式（Stripe、GitHub PAT、载体令牌、AWS 密钥等）加上 amend 特定的添加，用于会话转录中引用的手动 API 负载中的 `Authorization`/`Cookie`/`X-API-Key` 标头。
2. **实体** — 公司、人员、电子邮件与用户维护的停用列表 `~/.printing-press/amend-config.yaml` 匹配。用保持形状的标记（`<company-1>`、`<person-1>`、`<email-1>`）替换，这些标记在工件集中保持身份，以便审阅者仍然可以解析意图。
3. **首次提及防御** — 遍历每个工件，查找看起来像专有名词的大写短语，并且不在停用列表中。在 Phase 6 PR-draft 显示之前向用户内联显示： "发现 `Esper Labs`（计划文档中 3 次，PR 正文中 1 次） — 添加到停用列表并清理，或接受？"

目标，按优先级顺序：PR 标题/正文草稿、每次运行的计划文档、延迟发现列表、任何新添加到 `$CLI_DIR` 的测试固定或示例输出。对于每个目标，在清理之前将其复制到 `<path>.pre-pii-scrub`，以便用户可以审计更改内容。

**纵深防御**：遍历 `$CLI_DIR` 中的每个 `*.go` 文件，查找停用列表匹配。如果找到任何匹配，将其视为 BLOCKING — 暂停并要求用户解决，然后再进行 Phase 6。代理不应将 PII 引入 Go 源代码；此检查用于捕获代理错误。

**停用列表创建**：如果 `~/.printing-press/amend-config.yaml` 不存在，技能会创建一个默认文件，其中包含一个起始列表和一个解释格式的注释。文件模式验证（对世界可写警告，对非所有者中止）。

清理报告写入到 `$PRESS_MANUSCRIPTS/<slug>/<run-id>/scrub-report.json`（不提交；供用户审计）。阶段末尾的用户界面摘要： "X 个标记在 Y 个工件中替换。"

## Phase 6 — PR 草稿审查检查点（用户参与 #2）

这是第二次也是最终的用户新增点。以下所有内容在执行任何 `gh` 命令之前向用户显示。
在此审查中包含 Phase 4 的文档检查点结果，以便未记录的用户界面更改不会滑入 PR。

### 组装草稿

在内存中组合 PR 标题、正文、标签和差异摘要。标题格式遵循公共库约定：

- `fix(<api-slug>): <一句话摘要>` 当范围仅限于错误时
- `feat(<api-slug>): <一句话摘要>` 当范围包括功能时
- `feat(<api-slug>): <一句话摘要>` 当混合时（功能胜出，因为它是一个更大的合同更改）

`<一句话摘要>` 由最重要的 1-3 个发现组成（例如 `surface refresh-token expiry; add drafts new + --type sent`）。

PR 正文部分（按 origin R27）：

1. **摘要** — 1-3 句话命名用户痛点和解修形状
2. **发现** — 包含 ID、类别、类型（错误/功能）、理由的表格
3. **更改** — `git diff --stat upstream/main..HEAD` 的输出
4. **验证** — Phase 4 的构建/测试/狗粮/验证状态，以及文档检查点结果
5. **证据** — 每次运行计划文档和 PR 的 HEAD SHA 处 `.printing-press-patches/` 目录的完整 GitHub URL（在推送后捕获，以防止链接 404）
6. **关闭 #N** 页脚，当在 `library-pr-plumbing.md` 的 Step 6 中找到问题匹配时

标签：始终提议 `comp:<api-slug>`；`priority:P1` 对于仅限错误范围，`priority:P2` 对于错误+功能，`priority:P3` 对于所有层级。在将标签应用于上游库 PR 之前，使用 `gh label list --repo mvanhorn/printing-press-library --json name --jq '.[].name'` 查询目标存储库，并仅应用其中存在的标签。如果提议的标签不存在，则跳过它并在 PR 正文或最终运行日志中记录跳过；不要让缺失的每个 CLI 或优先级标签失败 amend 流。

### 在 gh 发起之前显示

向用户显示标题、正文、标签列表和 `git diff --stat`。如果 Phase 5 暴露了用户接受的未识别的大写短语，现在重新显示这些短语及其所在的句子：

> "提醒：PR 正文引用 `<phrase>`（您在 Phase 5 接受为合法）。确认后再打开。"

### AskUserQuestion: 打开 / 编辑 / 挂起 / 中止

PR 草稿已就绪。接下来怎么办？

1. 按草稿直接提交 PR（推荐）
2. 编辑后提交 — 进入交互式的标题/正文审阅
3. 搁置 — 将计划和 diff 保存以供日后恢复；不推送任何内容
4. 中止 — 丢弃所有内容，不留任何记录

对于**编辑后提交**：将标题和正文作为独立的可编辑块展示，接受用户的修改，重新展示完整草稿，确认后再继续。

对于**搁置**：将计划和 diff 保存到 `$PRESS_MANUSCRIPTS/<slug>/<run-id>/proofs/<timestamp>-amend-<cli-name>-HELD.md` 以及 `${path%.md}.diff`。输出一个包含 `status: held` 和恢复路径的 RESULT 块。未来的 `/printing-press-amend` 运行可以检测已搁置的文件并提供恢复选项。

对于**中止**：输出简短的确认信息。U5 的计划文档保留（frontmatter 中写入 `status: aborted`），以便用户了解发现了哪些问题，但其他内容均不保留。托管克隆将在下次运行时重置。

## 阶段 7 — 提交 PR（自动执行）

如果用户选择了提交或编辑后提交，执行 `references/library-pr-plumbing.md` 中的步骤 5–7：

1. **步骤 5** — `git add "$CLI_DIR"` + 使用约定式提交信息提交（含发现列表）
2. **步骤 6** — 搜索与发现内容匹配的已有 issue；链接或新建；尽力自行指派
3. **步骤 7** — 推送分支（push 还是 fork 访问模式在步骤 1 中已确定），使用 `--body-file` 执行 `gh pr create`，记录 HEAD_SHA，应用标签

fork/访问检测、分支冲突处理和托管克隆刷新模式在 `references/library-pr-plumbing.md` 中有详细说明。请勿在此处内联这些模式 — 该参考文档是权威来源。

PR 提交后，在面向用户的摘要中展示 URL 和 Greptile 提示：

> "PR 已提交: <url>
>
> Greptile 将在约 2 分钟内完成审查。请查看内联评论：
>
>     gh api repos/mvanhorn/printing-press-library/pulls/<N>/comments
>
> P0/P1 级别的发现值得在请求人工审查之前处理。"

## 阶段 8 — 输出

完成时输出结构化的 `---PATCH-RESULT---` 块。格式如下：

```
---PATCH-RESULT---
pr_url: <url>
pr_number: <n>
branch_name: <name>
api_slug: <slug>
scope_tier: <bugs|bugs+features|all|custom>
files_changed:
- <file>
build_status: <PASS|FAIL>
test_status: <PASS|FAIL>
dogfood_status: <PASS|FAIL|N/A>
pii_scrub_summary: <N tokens replaced across M artifacts>
findings_addressed:
- <one-line-summary>
findings_deferred:
- <one-line-summary>
deferred_list_path: <path>
plan_doc_path: <path>
---END-PATCH-RESULT---
```

## 本技能自身的验证

本 SKILL.md 的静态 lint 检查通过以下方式运行：

```bash
<PRINTING_PRESS_BIN> verify-internal-skill --dir skills/printing-press-amend
```

（参见 `internal/cli/verify_internal_skill.go` 及其对应的测试文件。setup-contract 一致性检查作为 Go 测试在 `internal/pipeline/contracts_test.go` 中运行 — `TestSkillSetupBlocksMatchWorkspaceContract`。）
