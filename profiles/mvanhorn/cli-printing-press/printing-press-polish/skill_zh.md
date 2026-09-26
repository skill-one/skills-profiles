# /printing-press-polish

对生成的 CLI 进行打磨，使其通过验证并准备好发布。

复古改进了 Printing Press。打磨改进了生成的 CLI。这项技能在分叉的上下文中运行（`context: fork`），因此其诊断和修复循环不会污染调用者——诊断垃圾、修复迭代和重新诊断噪音都保持在打磨会话的作用范围内，调用者接收一个干净的摘要。

```bash
/printing-press-polish redfin
/printing-press-polish redfin-pp-cli
/printing-press-polish "$PRESS_LIBRARY/redfin"
```

## 运行时机

在 `/printing-press` 生成之后，尤其是在以下情况时：
- shipcheck 的判断结果是 `ship-with-gaps`
- 验证通过率低于 80%
- 得分低于 85
- 你希望 CLI 一次通过即可发布

也可以在 `$PRESS_LIBRARY/` 中的任何 CLI 上单独运行。

## 设置

```bash
# min-binary-version: 4.0.0

PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
PRESS_LIBRARY="$PRESS_HOME/library"

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
    echo "[setup-error] Printing Press 工作区卷的磁盘空间严重不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_FAIL_KB=$_pp_disk_fail_kb"
    echo "释放磁盘空间或将 PRINTING_PRESS_HOME 设置为具有更多空间的卷，然后重新运行此技能。"
    echo ""
    return 1
  fi

  if [ "$_pp_disk_avail_kb" -lt "$_pp_disk_warn_kb" ]; then
    echo ""
    echo "[low-disk] Printing Press 工作区卷的可用空间不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_WARN_KB=$_pp_disk_warn_kb"
    echo "此流程可能需要几个 GiB 用于生成文件、Go 构建缓存、模块下载或仓库克隆。"
    echo ""
  fi
}
_pp_check_disk_space || { return 1 2>/dev/null || exit 1; }

# 中间流程的调用者可以在 args bundle 中传递 printing_press_bin: <abs-path>
# 倾向于使用它，以便分叉的打磨运行时保持使用父技能预先选择的二进制文件，而不是重新通过 PATH 解析。
PRINTING_PRESS_BIN="${PRINTING_PRESS_BIN:-}"
if [ -z "$PRINTING_PRESS_BIN" ] && [ -n "${ARGUMENTS:-}" ]; then
  PRINTING_PRESS_BIN="$(printf '%s\n' "$ARGUMENTS" | sed -nE 's/^[[:space:]]*printing_press_bin:[[:space:]]*(.+)$/\1/p' | head -1)"
fi
if [ -z "$PRINTING_PRESS_BIN" ]; then
  PRINTING_PRESS_BIN="$(command -v cli-printing-press 2>/dev/null || true)"
fi

if [ -z "$PRINTING_PRESS_BIN" ]; then
  echo "cli-printing-press 二进制文件未找到。"
  echo "使用以下命令安装：  go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest"
  return 1 2>/dev/null || exit 1
fi
if ! command -v go >/dev/null 2>&1; then
  echo ""
  echo "[setup-error] Go 工具链未找到。"
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
    echo "[setup-error] cli-printing-press 二进制文件需要 Go $_pp_go_required 或更高版本 (已安装: $_pp_go_installed)。"
    echo "GOTOOLCHAIN=local 禁用自动工具链下载，因此后续的 Go 质量门禁会失败。"
    echo "从 https://go.dev/dl/ 安装 Go $_pp_go_required 或更高版本，或取消设置 GOTOOLCHAIN。"
    echo ""
    return 1
  fi

  echo "[go-toolchain-old] cli-printing-press 二进制文件需要 Go $_pp_go_required 或更高版本 (已安装: $_pp_go_installed)。"
  echo "PRESS_GO_INSTALLED=$_pp_go_installed"
  echo "PRESS_GO_REQUIRED=$_pp_go_required"
  echo "默认 GOTOOLCHAIN 行为会在 Go 命令期间下载所需的工具链。"
  echo ""
  return 0
}
_pp_check_go_currency || { return 1 2>/dev/null || exit 1; }
```

设置完成后，捕获 `PRINTING_PRESS_BIN=<abs-path>` 并在此技能中的每个 `cli-printing-press ...` 调用中使用该绝对路径。如果设置发出 `[go-toolchain-old]` 或 `[low-disk]`，向用户显示建议，除非设置也发出 `[setup-error]`。`[go-toolchain-old]` 表示后续的 Go 命令可能会下载所需的工具链或在下载被阻止时失败；`[low-disk]` 表示此运行可能需要几个 GiB 用于生成文件、Go 构建缓存、模块下载或仓库克隆。

通过从此技能的 YAML 前置元数据中读取 `min-binary-version` 字段，运行 `"$PRINTING_PRESS_BIN" version --json` 并解析输出中的版本来检查二进制版本兼容性。使用 semver 规则将其与 `min-binary-version` 进行比较。如果安装的二进制文件比最小版本旧，请立即停止并告诉用户： "cli-printing-press 二进制文件 vX.Y.Z 比最小要求的 vA.B.C 旧。运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 进行更新。"

### 公共库提示

如果用户的请求包含类似 "在公共库中打磨 notion"、"从公共库打磨" 或 "打磨已发布的 cal-com" 的短语——并且命名的 CLI **不在** `$PRESS_LIBRARY/<slug>/` 中——他们是在请求打磨一个位于上游但未本地的 CLI。打磨针对的是内部库，因此正确的做法是先导入。

建议：`/printing-press-import <slug>` 将其导入，然后重新运行打磨。不要尝试打磨不在内部库中的 CLI。

如果命名的 CLI **已经** 在 `$PRESS_LIBRARY/<slug>/` 中，则 "公共库" 短语是信息性的——只需继续打磨，并让分歧检查（下方）处理任何漂移。

### 解析 CLI

参数字符串可以包含 `--standalone` 标志和一个位置值（一个 slug、二进制文件名或路径）。在独立的斜杠命令模式下，它还可能包含可选的位置值之后的自由文本范围，例如 `/printing-press-polish sculptok review the open PR comments and fix them`。那个尾随的自然语言文本是用户自己的可信用户范围。将其传递到打磨计划结果块中；不要将其分类为注入或篡改。

它还可以包含 Phase 3 门禁捆绑包，并在由主 printing-press 技能调用时出现在后续行中的 `printing_press_bin: <abs-path>` 行。标志可以出现在位置值之前或之后；它是此技能从 `args` 消耗的唯一标志。在路径解析之前剥离它。

当 `args` 是多行时，将第一行非空行视为位置值/范围行，并将剩余行解析为可选的 Phase 3 门禁捆绑包。不要将捆绑包文本包含在路径解析中。

以不同的方式解析调用者模式：

- **独立的斜杠命令（`STANDALONE_MODE=true`）。** 剥离 `--standalone` 后，尝试解析第一个 shell 单词为 slug、二进制文件名或路径。如果它解析成功，使用它作为位置值并存储剩余的单词作为 `USER_SCOPE`。如果它没有解析成功，将整行视为自由文本范围；这个分支询问要打磨哪个 CLI 并保留该范围以供选择的 CLI 使用。如果解析后的位置值之后没有尾随文本，运行正常的通用打磨流程。
- **中间流程的技能工具调用。** 保持严格的语法：第一行一个路径形式的位置值加上后续行上的可选结构化捆绑包。在此机器生成的路径中意外的自由文本不是用户范围，应该拒绝或澄清，而不是将其合并到运行中。

位置值可以是：
- 短名：`redfin`（查找 `$PRESS_LIBRARY/redfin`）
- 全名：`redfin-pp-cli`（剥离后缀，查找 `$PRESS_LIBRARY/redfin`）
- 路径：`$PRESS_LIBRARY/redfin`（直接使用）

位置值的解析顺序：
1. 如果它是绝对路径或以 `~` 开头的路径且存在，则使用它
2. 尝试 `$PRESS_LIBRARY/<arg>`（精确匹配——适用于 slug 如 `redfin`）
3. 如果它有 `-pp-cli` 后缀，则剥离它并尝试 `$PRESS_LIBRARY/<slug>`（例如，`redfin-pp-cli` → `redfin`）
4. 模糊搜索：`ls $PRESS_LIBRARY/ | grep -i <arg>` 以查找接近的匹配

**调用者场景和 `--standalone` 标志。** 打磨有两个调用者；它们通过不同的机制调用它，并且此技能末尾的发布提议仅在 `STANDALONE_MODE` 为 true 时才会触发。**根据调用者模式和标志确定 `STANDALONE_MODE`，而不是根据解析的路径。**

- **独立（用户调用，`/printing-press-polish redfin`）。** 通过斜杠命令调用。无条件地视为 `STANDALONE_MODE=true`——斜杠命令形式是发布意图的表面，即使用户省略了标志。参数是一个 slug 或二进制文件名；解析结果落在 `$PRESS_LIBRARY/<slug>/`。这是发布的副本，也是正确的目标。
- **中间流程（主 printing-press 技能 Phase 5.5，hold-path "重试打磨"）。** 通过技能工具调用，参数是 `"$CLI_WORK_DIR"`。参数是到 `~/printing-press/.runstate/.../runs/.../working/<api>-pp-cli/` 的绝对路径；解析必须命中规则 1。`STANDALONE_MODE=false` 默认——主技能拥有此路径的发布流程，因此打磨会推迟。**不要将参数改写为 slug**——Phase 5.5 在工作 CLI 被提升之前触发，因此 `$PRESS_LIBRARY/<slug>/` 要么不存在，要么包含 *先前* 运行的陈旧 CLI。
- **技能工具独立覆盖。** 一个非斜杠调用者如果确实希望打磨以发布，必须显式通过在 `args` 中包含 `--standalone`（例如，`args: "--standalone $PRESS_LIBRARY/redfin"`）来选择。没有这个标记，从技能工具调用中打磨永远不会发布——即使解析的路径恰好位于 `$PRESS_LIBRARY/` 下。标志是合同；路径不是。

这个调用者模式驱动的门禁取代了旧的路径子字符串启发式（`*.runstate/*`）。启发式在主技能的 Phase 5.5/5.6 顺序反转时失效，或者当从非 `.runstate` 的临时布局调用打磨时：打磨会看到 `$PRESS_LIBRARY/<slug>/` 路径，得出 "独立" 的结论，并在中间流程运行中触发其发布提议（分叉、全局 git 配置、公共 PR）。标志是明确的，更安全的默认值是不发布。

### Phase 3 门禁捆绑包

中间流程的调用者在 `args` 中的 CLI 路径之后传递这些字段：

```yaml
phase3_transcendence_rows_planned: <planned>
phase3_transcendence_rows_built: <built>
phase3_transcendence_rows_missing:
  - <manifest row name or command>
prior_sub60_reprint: <true|false>
partial_transcendence_override: <none or build-log note path>
```

在诊断之前解析捆绑包，并保留值以供船逻辑使用。缺失的捆绑包字段表示 "没有强制 Phase 3 持有"；它们不会阻止独立的打磨。如果 `prior_sub60_reprint: true`、`phase3_transcendence_rows_missing` 包含任何行，并且 `partial_transcendence_override` 为空或 `none`，打磨必须发出 `ship_recommendation: hold`，即使本地诊断 otherwise 清洁。将缺失的行添加到 `remaining_issues`，以便父技能可以显示阻止提升的特定门禁。

下一个代码块中的锁状态检查是中间流程场景的安全网：如果为该 CLI（无论哪种名称形式）持有构建锁，打磨将拒绝运行。`cli-printing-press lock` 在内部规范化 slug ↔ 二进制文件名，因此检查无论基名以哪种形式生成，都能正常工作。

如果没有匹配或多个匹配，通过 `AskUserQuestion` 显示。最多显示 4 个匹配项，按修改时间排序（最新的在前），并使用人类友好的相对时间戳（例如，"生成 2 小时前"）。

```bash
CLI_DIR="<resolved path>"
CLI_NAME="$(basename "$CLI_DIR")"
STANDALONE_MODE="<true|false>"  # true iff slash-command invocation or --standalone in args; default false for Skill-tool invocations

# 检查是否有活动的构建锁——打磨编辑将被运行中的构建覆盖，当构建提升到库时。
_lock_json=$("$PRINTING_PRESS_BIN" lock status --cli "$CLI_NAME" --json 2>/dev/null)
if echo "$_lock_json" | grep -q '"held".*true'; then
  if echo "$_lock_json" | grep -q '"stale".*true'; then
    echo "警告：存在 $CLI_NAME 的陈旧锁（构建可能已崩溃）。"
    echo "继续打磨。运行 '$PRINTING_PRESS_BIN lock release --cli $CLI_NAME' 清除。"
  else
    echo "正在进行 $CLI_NAME 的构建。"
    echo "打磨编辑将在构建提升时被覆盖。"
    echo "等待构建完成，然后运行打磨。"
    exit 1
  fi
fi

# 验证它是一个有效的 Go CLI
if [ ! -f "$CLI_DIR/go.mod" ]; then
  echo "不是有效的 CLI 目录：$CLI_DIR"
  exit 1
fi

echo "正在打磨：$CLI_NAME"
echo "位置：$CLI_DIR"
```

### 查找 spec 和研究目录

```bash
API_SLUG="${CLI_NAME%-pp-cli}"
SPEC_PATH=""
for f in "$PRESS_HOME/manuscripts/$API_SLUG"/*/research/*.yaml "$PRESS_HOME/manuscripts/$API_SLUG"/*/research/*.json "$PRESS_HOME/manuscripts/$CLI_NAME"/*/research/*.yaml "$PRESS_HOME/manuscripts/$CLI_NAME"/*/research/*.json; do
  if [ -f "$f" ]; then
    SPEC_PATH="$f"
    break
  fi
done

# Build the spec flag once. Empty when no spec was found — diagnostic
# commands accept a missing --spec and degrade gracefully.
SPEC_FLAG=""
if [ -n "$SPEC_PATH" ]; then
  SPEC_FLAG="--spec $SPEC_PATH"
fi

# Locate the research dir. dogfood's --research-dir triggers
# checkNovelFeatures, which writes novel_features_built back into
# research.json AND syncs the verified list into .printing-press.json.
# Without this flag, legacy CLIs whose manifest predates the
# novel_features schema fail publish-validate's transcendence gate.
#
# Two layouts to handle, keyed on $CLI_DIR path structure (NOT on the
# absence of a manuscripts entry — re-generating a previously-published
# API leaves stale manuscript entries from prior runs that would point
# scorecard at the wrong research.json):
#  1. Mid-pipeline polish (invoked from the main printing-press flow
#     before promote): $CLI_DIR is under $PRESS_RUNSTATE/.../runs/<id>/working/<cli>
#     (i.e. the path contains `.runstate/`), and research.json lives at
#     $PRESS_RUNSTATE/.../runs/<id>/research.json — $CLI_DIR's grandparent.
#  2. Post-promote (standalone polish): research.json lives at
#     manuscripts/<api>/<run-id>/research.json.
RESEARCH_DIR=""
MANIFEST_RUN_ID=""
if [ -f "$CLI_DIR/.printing-press.json" ]; then
  if command -v jq >/dev/null 2>&1; then
    MANIFEST_RUN_ID="$(jq -r '.run_id // empty' "$CLI_DIR/.printing-press.json" 2>/dev/null || true)"
  fi
  if [ -z "$MANIFEST_RUN_ID" ]; then
    MANIFEST_RUN_ID="$(sed -nE 's/.*"run_id"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' "$CLI_DIR/.printing-press.json" | head -1)"
  fi
fi
case "$CLI_DIR" in
  *.runstate/*)
    _grandparent="$(dirname "$(dirname "$CLI_DIR")")"
    if [ -f "$_grandparent/research.json" ]; then
      RESEARCH_DIR="$_grandparent"
    fi
    ;;
  *)
    if [ -n "$MANIFEST_RUN_ID" ]; then
      for base in "$PRESS_HOME/manuscripts/$API_SLUG" "$PRESS_HOME/manuscripts/$CLI_NAME"; do
        if [ -f "$base/$MANIFEST_RUN_ID/research.json" ]; then
          RESEARCH_DIR="$base/$MANIFEST_RUN_ID"
          break
        fi
      done
    fi
    # Match publish package's fallback: API slug first, then CLI name, each
    # using the lexicographically latest run id when the manifest has none.
    if [ -z "$RESEARCH_DIR" ]; then
      for base in "$PRESS_HOME/manuscripts/$API_SLUG" "$PRESS_HOME/manuscripts/$CLI_NAME"; do
        if [ -d "$base" ]; then
          _latest="$(find "$base" -mindepth 2 -maxdepth 2 -name research.json -type f 2>/dev/null | sort | tail -1)"
          if [ -n "$_latest" ]; then
            RESEARCH_DIR="$(dirname "$_latest")"
            break
          fi
        fi
      done
    fi
    ;;
esac

# Use a bash array so the flag survives paths with spaces (e.g. when
# $HOME or $PRESS_RUNSTATE resolves through a path containing spaces).
RESEARCH_ARGS=()
if [ -n "$RESEARCH_DIR" ]; then
  RESEARCH_ARGS=(--research-dir "$RESEARCH_DIR")
fi

# pii-audit runs against the CLI dir, but publish package later copies the
# same run archive under .manuscripts/<run-id> before enforcing the PII gate.
# Pass the run dir here so polish sees the narrative manuscript files with
# the same relative paths publish will scan.
PII_ARGS=()
if [ -n "$RESEARCH_DIR" ]; then
  PII_ARGS=(--manuscripts-dir "$RESEARCH_DIR")
fi
```

### Divergence check

**Stop and run this step before Phase 1. Do not skip it. Do not proceed to diagnostics until you have completed the check and resolved any divergence.**

The internal copy at `$CLI_DIR` can drift from the public library (`mvanhorn/printing-press-library`) copy if anyone edited the public repo directly after this CLI was last published. Polishing a stale internal copy and re-publishing later silently overwrites those public-only fixes — a real failure mode that shipped CLIs hit.

**You must:**

1. **Locate the public library clone.** Honor `$PRINTING_PRESS_LIBRARY_PUBLIC` if set; otherwise scan the user's filesystem however fits this platform. Validate every candidate by checking the git remote points at `mvanhorn/printing-press-library` — other directories may share the name (forks, accidental name collisions). If multiple valid clones exist, prefer the most recently modified; ask the user to disambiguate only if still unclear.
2. **Locate this CLI inside the clone.** `find <clone>/library -type d -name "<api>-pp-cli"` or equivalent.
3. **Run `diff -r <public-cli-dir> $CLI_DIR`** with these exclusions, all of which are expected to diverge after publish:
   - `.printing-press-tools-polish.json` (local ledger, not published)
   - `.printing-press-pii-polish.json` (local ledger, not published)
   - `go.mod` and `go.sum` — publish rewrites the module path from `<api>-pp-cli` to `github.com/mvanhorn/printing-press-library/library/<category>/<api>`
   - All `.go` files where the only difference is the rewritten import path (the publish step propagates the new module path through every internal import). When inspecting `.go` diffs, scan for substantive changes — anything beyond the module-path prefix swap is real divergence.

   Concretely: `diff -r --exclude=go.mod --exclude=go.sum --exclude=.printing-press-tools-polish.json --exclude=.printing-press-pii-polish.json <public-cli-dir> $CLI_DIR`.

   Don't pass `--exclude='<api>-pp-cli'` or `--exclude='<api>-pp-mcp'` — those names match both the root-level binary files **and** the `cmd/<api>-pp-cli/` and `cmd/<api>-pp-mcp/` source directories. Excluding by binary name silently skips the entire `cmd/` subtree, hiding real divergence in `main.go`. The "Only in $CLI_DIR: <api>-pp-cli" line for the built binary is one row of expected output, not noise worth filtering at the cost of completeness.
4. **Surface the result** before continuing.

Outcomes:

- **No clone found** → user doesn't have public locally. State this explicitly ("public library not found locally; proceeding on internal as canonical") and continue.
- **Clone found but doesn't contain this CLI** → never published or under a different name. State this and continue.
- **Found and diff is empty** → in sync. State this and continue.
- **Found and divergent** → **stop**. Do not run Phase 1 diagnostics yet. List the divergent files for the user. Ask via AskUserQuestion: **sync public→internal**, or **proceed without syncing**. If the user picks sync, copy public's version of the divergent files into internal, then continue polish on the synced internal copy.

Before showing the sync prompt, check whether internal has files modified after its `.printing-press.json` timestamp (the user has been polishing locally without publishing). If yes, hedge the prompt explicitly: syncing will overwrite their pending local work. Let them decide whether to keep their local edits or pull public's.

After sync (or explicit skip), the rest of polish operates on `$CLI_DIR` as canonical. The eventual `/printing-press-publish` step pushes internal back to public; no second divergence check is needed there.

**The check has run only when one of the four outcomes above is explicitly stated in your response.** Silent omission counts as not having run it.

## Phase 1: Baseline diagnostics

```bash
cd "$CLI_DIR"

# Build
go build -o "$CLI_NAME" ./cmd/"$CLI_NAME" 2>&1

# Diagnostics. SPEC_FLAG and RESEARCH_ARGS are set in the "Find spec
# and research dir" step above. RESEARCH_ARGS enables dogfood to
# verify novel features and sync them into .printing-press.json
# (required for publish-validate's transcendence gate).
"$PRINTING_PRESS_BIN" dogfood --dir "$CLI_DIR" $SPEC_FLAG "${RESEARCH_ARGS[@]}" 2>&1
"$PRINTING_PRESS_BIN" verify --dir "$CLI_DIR" $SPEC_FLAG --json 2>&1
"$PRINTING_PRESS_BIN" workflow-verify --dir "$CLI_DIR" --json > /tmp/polish-workflow-verify.json 2>&1 || true
"$PRINTING_PRESS_BIN" verify-skill --dir "$CLI_DIR" --json > /tmp/polish-verify-skill.json 2>&1 || true
# publish-validate is a publish-readiness gate, not a CLI-readiness gate.
# Mid-pipeline polish runs before the main SKILL's promote step and before
# the publish skill packages tools-manifest.json, so its prerequisites
# (manifest.printer from git config github.user, packaged tools manifest,
# phase5 acceptance proof relocated under $CLI_DIR/.manuscripts/<run>/proofs/)
# are not yet satisfied. Running publish-validate here would cascade
# parent-pipeline-owned failures into the polish ship_recommendation,
# which the main SKILL's Phase 5.5 verdict-override then turns into a
# CLI-level hold. Only run publish-validate when polish is the publish
# entry point (slash-command invocation or explicit --standalone).
if [ "$STANDALONE_MODE" = "true" ]; then
  "$PRINTING_PRESS_BIN" publish validate --dir "$CLI_DIR" --json > /tmp/polish-publish-validate.json 2>&1 || true
fi
# --live-check samples novel-feature outputs and populates
# live_check.features[].warnings (Wave B entity detection) — required for
# the "Output entity warnings" row below to have data to read.
# RESEARCH_ARGS points scorecard at the run's research.json when the
# CLI lives under $PRESS_RUNSTATE/runs/<id>/working/<cli> (mid-pipeline
# polish). Without it, scorecard looks adjacent to the binary, doesn't
# find research.json, and reports `unable: true`.
"$PRINTING_PRESS_BIN" scorecard --dir "$CLI_DIR" $SPEC_FLAG "${RESEARCH_ARGS[@]}" --live-check --json > /tmp/polish-scorecard.json 2>&1 || true
"$PRINTING_PRESS_BIN" scorecard --dir "$CLI_DIR" $SPEC_FLAG 2>&1
"$PRINTING_PRESS_BIN" tools-audit "$CLI_DIR" --json > /tmp/polish-tools-audit-before.json 2>&1 || true
"$PRINTING_PRESS_BIN" pii-audit "$CLI_DIR" "${PII_ARGS[@]}" --json > /tmp/polish-pii-audit-before.json 2>&1 || true
go vet ./... 2>&1
if command -v gosec >/dev/null 2>&1; then
  gosec -fmt=json -out=/tmp/polish-gosec-before.json ./... 2>&1 || true
else
  go run github.com/securego/gosec/v2/cmd/gosec@v2.26.1 -fmt=json -out=/tmp/polish-gosec-before.json ./... 2>&1 || true
fi
```

verify-skill and workflow-verify run alongside dogfood/verify/scorecard so polish catches the same class of failures the public-library CI catches. `publish-validate` runs only when `STANDALONE_MODE=true` (slash-command or `--standalone` Skill-tool invocation). The publish-validate leg is a hard ship-gate **for standalone polish**: in that mode polish cannot recommend `ship` or `ship-with-gaps` while `"$PRINTING_PRESS_BIN" publish validate` reports `passed: false`. Mid-pipeline polish (`STANDALONE_MODE=false`) skips publish-validate entirely — its prerequisites (manifest.printer from `git config github.user`, packaged `tools-manifest.json`, phase5 acceptance proof relocated under `$CLI_DIR/.manuscripts/<run>/proofs/`) are not yet satisfied at this point; the main SKILL's Phase 6 publish flow gates on publish-validate at the correct time. See "Ship logic" below for how this affects ship_recommendation.

**Live matrix qualifier.** After each `scorecard --live-check --json` run, read `/tmp/polish-scorecard.json` and record whether `live_check` actually exercised live samples. Treat it as `exercised` only when `live_check.unable` is false and at least one feature was evaluated (`passed + failed > 0`, or equivalent feature statuses). Treat `live_check.unable: true`, no `live_check`, no evaluated features, or missing credentials/token as `not_exercised`. A clean mock dogfood/verify run is still useful, but it is **not** a live matrix pass.

`gosec` runs as the off-the-shelf security static-analysis leg for hand-written Go. Prefer an installed `gosec` binary when present; otherwise use the pinned `go run github.com/securego/gosec/v2/cmd/gosec@v2.26.1` fallback so a clean machine still gets a reproducible check without a separate setup step. Read `/tmp/polish-gosec-before.json` for the baseline finding count and issue details. If the command fails before writing JSON, treat the missing scan as a polish failure: add it to `remaining_issues`, set `ship_recommendation: hold`, and include the stderr summary so the next run can distinguish network/tooling failure from CLI defects. Prioritize findings in hand-authored files: whole files under `internal/cli/`, `internal/syncer/`, and `internal/store/` whose first 20 lines lack the `Generated by CLI Printing Press` header are polish-owned novel-feature code. Findings in generator-emitted files are Printing Press retro candidates unless they can be fixed durably by changing the spec and regenerating; do not hand-edit generated files just to silence gosec.

**If Phase 1 baseline reveals the underlying CLI needs re-discovery** — broken HTML/SSR extraction, sparse capture (fewer than 5 unique endpoints in the source manuscript), wrong endpoint shapes, missing GraphQL operation hashes, or any signal that the CLI was generated from incomplete capture — polish does not normally do browser capture itself. When re-discovery is required, use the capture backends the runtime already exposes (Claude chrome-MCP `mcp__claude-in-chrome__*` and computer-use `mcp__computer-use__*`) rather than inventing a new capture flow. Re-discovery from polish is rare but real.

Parse findings into categories:

| Category | Source | What to look for |
|----------|--------|------------------|
| Verify failures | verify --json | Commands with score < 3 |
| SKILL static-check failures | verify-skill --json | Any `findings[]` with `severity=error` (flag-names, flag-commands, positional-args, unknown-command, canonical-sections). Hard ship-gate: ship cannot fire while these exist. |
| Workflow gaps | workflow-verify --json | Verdict `workflow-fail`. Soft gate: surface in `remaining_issues` and downgrade to `hold` when the workflow is the CLI's primary value. |
| Publish validation failures | publish validate --json | `passed: false`. **Standalone polish only** (runs only when `STANDALONE_MODE=true`); skipped in mid-pipeline polish where publish prerequisites aren't yet satisfied. When it runs, it's a hard ship-gate: ship cannot fire while publish validate fails. If the only failing check is missing phase5 acceptance, report `phase5 acceptance required` with the next-step command: authenticate, then run `"$PRINTING_PRESS_BIN" dogfood --dir "$CLI_DIR" $SPEC_FLAG --live --level quick --write-acceptance <proofs-dir>/phase5-acceptance.json`. Use the proofs directory from the validate error when present. |
| Security static-analysis failures | gosec JSON | Any `Issues[]` entry, especially G201/G202 SQL construction, G101 credential literals, or unsafe file/command execution. Hard ship-gate when the finding is in hand-authored novel-feature Go. |
| Dead code | dogfood | Dead functions, dead flags |
| Stale files | dogfood | Unregistered commands |
| Description issues | dogfood | Boilerplate root Short |
| README gaps | scorecard | README score < 8 |
| Example gaps | dogfood | Commands missing examples |
| Go vet issues | go vet | Any output |
| Output entity warnings | scorecard JSON | `live_check.features[].warnings` — raw HTML entities in human output |
| Output plausibility | Phase 4.85 | Findings from the agentic output review |
| MCP tool quality | tools-audit | Empty Short, thin Short, missing read-only annotations, thin MCP descriptions |
| Customer PII | pii-audit | Card last-4, email, phone, ZIP+4, postal-address shapes in high-risk files (manuscripts, fixtures, README) |

**Environmental failures vs. CLI defects.** Some Phase 1 outputs surface failures that aren't real CLI bugs and should not block ship:

- `scorecard --live-check` 报告 `SQLITE_BUSY`、网络超时、来自模拟或过期令牌的 `401`，或依赖于测试工作区权限/状态的 HTTP 错误——这些问题是测试环境问题，不是 CLI 缺陷。
- `verify` 模拟工具在具有二进制输出的命令（例如，`qr` 返回 PNG 而子字符串匹配器无法验证）或具有可选位置参数的命令（其中干运行输出确实不包含验证探测字符串）上出现错误。
- 学习循环命令：狗粮/verify 矩阵现在覆盖了默认开启的学习表面（`teach`、`recall`、`learnings`、`playbook`）。`teach` 和 `teach-playbook` 在被空调用时有意退出 2，通过 `pp:typed-exit-codes` 声明，因此 `verify` 评分将其视为通过，而 `dogfood --live` 将 `happy_path` 和 `json_fidelity` 检查记录为跳过，原因 `声明非零退出 2`；两者都不是缺陷，也不是“修复”退出代码的理由。跳过的 happy path 不计入 phase5 live 覆盖率，因此仅在其 happy path 上始终退出非零的新功能会报告为空而不是覆盖。`learnings stats` 在新的打印上确实报告零和空部分；这是一个空的本地存储，不是缺陷。

在 `skipped_findings` 中将这些分类为环境问题，并附上具体原因；不要在 Phase 2 周期内试图“修复”它们。抛光技能的发布逻辑已经排除了 live-check 失败，但代理仍然应该注释它们，以便审阅者可以看到它们被考虑并故意忽略。

### Phase 4.85 — 代理输出审查（Wave B）

在上述机械诊断完成后，通过技能工具调用 `printing-press-output-review` 子技能。子技能携带 `context: fork` 并拥有调度提示、门禁逻辑和已知盲点——与主 printing-press 技能共享的单一事实来源。

```
Skill(
  skill: "cli-printing-press:printing-press-output-review",
  args: "$CLI_DIR"
)
```

解析返回的 `---OUTPUT-REVIEW-RESULT---` 块。`status: WARN` 查找项流入上述诊断类别，因此 Phase 2 修复将解决基于规则和合理性问题。`status: SKIP` 是信息性的——记录但不要阻止。

Wave B 门禁适用：所有查找项都是警告，永远不会是阻止器。如果明显且便宜，则修复；如果推迟，则用简短注释记录。

记录基线分数：scorecard 总分、verify 通过率、狗粮判定、live 矩阵限定符（`exercised` / `not_exercised`）、go vet 问题数量、gosec 查找数量、输出审查查找数量。

## Phase 2：修复

按优先级顺序修复。每次修复完一个优先级级别后，更新锁心跳：

```bash
"$PRINTING_PRESS_BIN" lock update --cli "$CLI_NAME" --phase polish 2>/dev/null
```

### 运行时变体默认清单

如果抛光修复添加或更改了运行时模式、数据源选项、认证层、传输或其他用户可见默认值，请在选择默认值前记录此简短清单：

- **用户可见默认值**：用户无需额外标志或配置即可获得的行为。
- **兼容性风险**：现有命令、脚本、MCP 工具或存储配置是否改变行为。
- **验证命令**：证明默认值和非默认值逃生通道都起作用的精确命令。

将清单保存在抛光笔记或结果块中。对于普通错误修复，如果未更改运行时变体或默认值，则跳过它。

### 跨越 API 调用监控

当抛光构建必须观察每个出站 API 调用的功能类时，例如配额账本、请求日志或审计跟踪，在 `internal/client/client.go` 中监控生成的客户端中间件，而不是单独的命令处理程序。如果存在共享的预调度钩子，则优先使用它；否则覆盖 `do()` 和 `doRead()`。`do()` 路径处理标准端点镜像、同步迭代和使用生成客户端的新功能，而 `doRead()` 处理仅使用 POST 类似传输的只读操作，例如 GraphQL 查询、JSON-RPC 读取和标记 `mcp:read-only` 的基于 POST 的搜索。命令级钩子计数不足，因为它们只看到抛光触碰的命令。

### 新功能数据路由

当抛光添加或修复读取 API 响应数据到本地存储的新功能命令时，通过生成的类型化模式路由数据，而不是直接将原始响应 JSON 写入表：

1. 读取 `internal/types/<resource>.go` 和 `internal/store/<resource>.go` 以获取正在缓存的资源。如果这些文件存在，请使用它们发出的类型化插入/更新辅助程序。如果为生成的资源缺少辅助程序，请在编写任何持久化代码之前创建它们。
2. 在决定插入映射正确之前，检查响应形状与规范模式和真实样本响应。
3. 在持久化之前将 API 响应解码为类型化结构。除非表是手编写的迁移中声明的自定义抛光拥有的表，否则不要从未知的 `map[string]any` 或原始 `json.RawMessage` 值构建 `INSERT INTO ...` 语句。
4. 从资源类型而不是新功能命令碰巧开始查询的目标表验证。获取 `<child>` 记录的命令必须插入 `<child>` 行，而不是父行或方便的相邻表。
5. 在插入前规范化嵌套响应标识符。如果 API 将标量 ID 包装在还包含元数据的对象中，请提取标量 ID 字段并存储该值；永远不要将整个 ID 对象作为主键或外键引用存储。

仅自定义抛光拥有的表（在手动编写的迁移中声明）的原始 `database/sql` 写入是可接受的。在这种情况下，在 `internal/store/` 中保持表模式明确，记录为什么生成的资源辅助程序不适用，并在持久化前将嵌套标识符解码为标量。

### 优先级 0：MCP 表面迁移（遗留 CLIs）

如果 Phase 1 的 `dogfood` 报告 `MCP Surface: FAIL` 出现奇偶校验不匹配，CLI 在运行时 cobratree 行走器存在之前生成，并且仍然在静态 `internal/mcp/tools.go` 表面。修复是机械的：

```bash
"$PRINTING_PRESS_BIN" mcp-sync "$CLI_DIR"
```

这将迁移 MCP 表面到运行时行走器，重新生成 `tools-manifest.json` 和 `internal/mcp/tools.go`，并应用任何 `mcp-descriptions.json` 覆盖。如果它退出并显示 `mcp-sync refused` 和 `reprint required`，停止此抛光运行并转交给 `/printing-press-reprint`；目标 CLI 生成的客户端对当前的 MCP 处理器太旧，因此单独重写 `tools.go` 会破坏其构建。在转交中包括，重印流程必须对其重新生成的 CLI 运行正常的 dogfood 门禁，并确认 `MCP Surface: PASS` 才能发布。不要对过时的 `$CLI_DIR` 重新运行 dogfood。成功 `mcp-sync` 后，在此处重新运行 `dogfood`；奇偶校验门禁应切换到 PASS。在兼容的 CLI 已使用运行时行走器上运行 `mcp-sync` 是无操作刷新。

在 dogfood 的 MCP 门禁已经通过的 CLI 上跳过此优先级。

### 优先级 1：安全静态分析失败

对于 `/tmp/polish-gosec-before.json` 中的每个 gosec 查找项：

1. 读取引用的文件并确认它是否是手编写的。在 `internal/cli/`、`internal/syncer/` 或 `internal/store/` 下，如果前 20 行缺少 `Generated by CLI Printing Press`，则是抛光拥有的新功能代码。
2. 如果查找项在手编写的代码中，请在处理较低优先级抛光项之前在源代码中修复根本原因。示例：用参数化查询替换 SQL 字符串组装，避免使用不受信任的参数调用 shell，并将看起来像凭证的常量移动到配置/环境管道。
3. 如果 gosec 标记生成代码，不要手动编辑生成的文件。要么修复上游规范并重新生成，要么添加一个 `skipped_findings` 条目，将其命名为生成器候选，并附上规则 ID 和文件路径。
4. 如果 gosec 报告误报，请保持抑制范围狭窄并解释它。仅在代码实际上安全且理由持久时，才优先使用本地 `// #nosec G### -- reason`；否则修复代码。

手编写的 novel-feature Go 中未解决的 gosec 查找项是硬阻止器：它们必须出现在 `remaining_issues` 中，强制 `ship_recommendation: hold`，并在修复可能机械时设置 `further_polish_recommended: yes`。

### 优先级 2：Verify 失败

对于每个失败 verify 干运行或执行的命令：

1. 读取命令文件
2. 找到 `Args: cobra.ExactArgs(N)` 或类似约束
3. 删除 `Args:` 字段
4. 在 `RunE` 顶部添加：
   ```go
   if len(args) == 0 {
       return cmd.Help()
   }
   ```
5. 对于需要 2 个以上参数的命令，使用 `if len(args) < 2`
6. 检查干运行 nil 数据崩溃并添加保护：
   ```go
   if flags.dryRun {
       return nil
   }
   ```

### 优先级 3：死代码

1. 对于 dogfood 标记的每个死函数，grep 所有 `.go` 文件以验证它确实未使用（不仅仅是其定义与自身匹配）
2. 如果确实未使用：删除该函数
3. 如果由另一个辅助程序使用：保留它（误报）
4. 删除后，删除未使用的导入
5. 删除过时的文件（未在 root.go 中注册的推广命令）

### 优先级 4：CLI 描述和元数据

1. 读取 `internal/cli/root.go` 中的 root 命令 `Short`
2. 如果它包含样板（“逆向工程...”、原始 API 标题），重写：
   模式：`"<Product> CLI with <capability-1>, <capability-2>, and <capability-3>"`
3. 检查命令是否有缺失的 `Example` 字段。添加具有特定领域值的现实示例。

### 优先级 5：README

**基本规则：对您放入 README 的每个命令运行 `<cli> <cmd> --help`。** 永远不要猜测标志名称、参数格式或有效值。如果您写 `--start-time` 但标志是 `--start`，则 README 是错误的，用户在第一次尝试时会出现错误。

#### 渲染部分的源文件

在编辑 README.md、SKILL.md 或 `.printing-press.json` 之前，确定该部分是否从源文件渲染。狗粮和再生会覆盖这些渲染部分，因此直接编辑它们是临时的，并且仅用于检查当前输出。

| 渲染部分或字段 | 源文件::字段 | 抛光工作流 |
| --- | --- | --- |
| README `## Unique Features` | `research.json::novel_features_built[]` | 编辑底层的 `research.json` 功能描述/示例，然后使用 `--research-dir` 重新运行狗粮。 |
| SKILL `## Unique Capabilities` | `research.json::novel_features_built[]` | 编辑底层的 `research.json` 功能描述/示例，然后使用 `--research-dir` 重新运行狗粮。 |
| `internal/mcp/tools.go` `command_mirror_capabilities` | `research.json::novel_features_built[]` | 狗粮报告磁盘上的不同块并保留它未修改。仅当传递 `--overwrite-command-mirror` 时才替换它从 `research.json`。 |
| README Quick Start | `research.json::narrative.quickstart[]` | 编辑 `research.json` 中的命令/注释，然后重新运行狗粮/渲染步骤。 |
| SKILL Recipes | `research.json::narrative.recipes[]` | 编辑 `research.json` 中的配方标题、命令或解释，然后重新运行狗粮/渲染步骤。 |
| README/SKILL Troubleshooting | `research.json::narrative.troubleshoots[]` | 编辑 `research.json` 中的症状/修复对，然后重新运行狗粮/渲染步骤。 |
| `.printing-press.json` `display_name`, `description`, `mcp_*` | `WriteManifestForGenerate`；对于描述/显示名覆盖，编辑规范 (`info.title`, `info.x-display-name`, `info.description`) | 编辑规范或重新运行清单编写器。除非您正在进行临时诊断，否则不要手动编辑生成的清单元数据。 |

这些渲染部分的推荐循环：编辑源字段，使用 `--research-dir "$RESEARCH_DIR"` 重新运行狗粮或按适当方式重新生成 CLI，然后运行第二遍以确认渲染的 README/SKILL 文本保持固定。如果您直接在其中一个部分中编辑 README.md 或 SKILL.md，预期下一次狗粮同步或再生会覆盖更改。

要找到手稿源：

```bash
PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
API_SLUG="${CLI_NAME%-pp-cli}"
RESEARCH_JSON=""
for f in "$PRESS_HOME/manuscripts/$CLI_NAME"/*/research.json \
         "$PRESS_HOME/manuscripts/$API_SLUG"/*/research.json; do
  if [ -f "$f" ]; then RESEARCH_JSON="$f"; break; fi
done
```

如果 `RESEARCH_JSON` 存在且渲染部分有不良的措辞、示例或标志引用，请首先在该文件中修复相应字段。对于新功能，狗粮验证 `research.json::novel_features[]`，将剩余集写入 `research.json::novel_features_built[]`，并从该验证集同步 README `## Unique Features`、SKILL `## Unique Capabilities`、`.printing-press.json` `novel_features` 和 root 帮助高亮。`command_mirror_capabilities` 块在 `internal/mcp/tools.go` 中不同步时将保留未修改，除非传递 `--overwrite-command-mirror`。

#### 必须存在的部分（必须正确存在）

1. **标题**：`# <Product Name> CLI` — 使用产品的真实名称，正确的大小写/标点（例如，"Cal.com" 而不是 "Cal Com"）
2. **副标题**：一句描述 CLI 对用户的作用的句子，匹配 root `Short` 字段。不是 API 的描述。
3. **安装**：正确的安装命令。使用 printing-press-library 仓库 URL，而不是不存在于每个 CLI 的特定仓库。
4. **认证**：如何设置 `<API>_API_KEY` 环境变量，在哪里获取密钥（链接到提供者的设置页面），如果支持自托管 URL 覆盖。读取 `config.go` 以找到所有环境变量。
5. **快速入门**：3-5 个有人会首先运行的命令。选择既 **最有用**（您每天会运行的）又 **展示 CLI 价值**（为什么安装这个而不是 curl）的命令。通常：
   `doctor` → `sync` → 超越命令（`today`、`health`）→ `search`。避免原始列表命令——它们只是倾倒数据，而没有展示 CLI 存在的原因。
6. **命令**：分类表。按领域功能（调度、分析、账户、实用工具）分组，而不是按实现结构。
7. **输出格式**：显示 `--json`、`--select`、`--csv`、`--compact`、`--dry-run`、`--agent`。使用真实命令，而不是占位符。
8. **代理使用**：代理原生属性和退出代码。
9. **食谱**：8-15 个使用 `--help` 中 **验证标志名称** 的食谱。展示 CLI 的独特能力：超越命令、过滤器、SQL 查询、管道。至少包含一个变异示例。
10. **健康检查**：显示实际的 `doctor` 输出，而不是占位符。
11. **配置**：列出来自 config.go 的所有环境变量及其描述。包括配置文件路径。
12. **故障排除**：常见错误映射到退出代码及其修复。

#### 可选部分（根据需要添加）

- **速率限制**：如果 API 有文档记录的限制
- **自托管**：如果 CLI 支持 `--api-url` 或 `BASE_URL` 覆盖
- **分页**：如果 API 有显著的分页行为
- **来源和灵感**：社区项目的信用（由机器生成，如果存在则保留）

### 优先级 5.5：SKILL 静态检查失败（verify-skill）

读取 `/tmp/polish-verify-skill.json` 获取完整查找列表。每个查找项都有一个 `check`（`flag-names`、`flag-commands`、`positional-args`、`unknown-command` 或 `canonical-sections`）、一个 `command`（SKILL 声称的路径）和一个 `detail` 描述不匹配。常见形状和修复：

- **`flag-names`** — SKILL 在 `<cli> ...` 调用中引用了 `--foo`，但 `internal/cli/*.go` 中没有任何命令声明了该标志。要么示例有误（修正 SKILL 或删除该 recipe），要么该标志已被删除（判断是否应恢复）。**不在检查范围内：** 调用其他工具的行上的标志（例如 `npx -y @mvanhorn/printing-press install <api> --cli-only`、`gh pr create --base ...`、`go install ...`）。recipe 范围的 flag-names 检查按设计会忽略这些外部工具标志——切勿为了让 verify-skill 返回 0 而剥离外部工具标志，也切勿用虚构的斜杠命令替代安装说明。如果该发现仍然触发了外部工具标志上的检查，那是 verify-skill 的 bug，而非 SKILL 的 bug；应报告该问题，而非编辑 SKILL。
- **`flag-commands`** — `--foo 在其他位置有声明，但未在 <cmd> 上声明`。该标志存在于某处，但 SKILL 调用它的命令上并未声明。两种修复方式：
  1. 如果该标志是通过共享辅助函数（如 `addXxxFlags(cmd, ...)`）添加的，直接在受影响的命令源文件中内联 `cmd.Flags().StringVar(...)` 声明。verify-skill 的 grep 无法跟踪函数调用间接引用。
  2. 如果 SKILL 示例确实有误，将示例修改为该命令实际声明的标志。
- **`positional-args`** — `得到 N 个位置参数；Use: "<cmd> <arg>" 期望 M-M`。SKILL recipe 传递了 N 个位置参数，但命令的 `Use:` 声明需要 M 个。两种修复方式：
  1. 如果该命令也通过 `--flag` 接受该值，将 `Use: "cmd <arg>"` 改为 `Use: "cmd [arg]"`（方括号 = 可选）。verify-skill 正确地将仅使用 `--flag` 的调用视为可选位置参数的有效调用。
  2. 如果 SKILL 示例缺少必需的位置参数，修正示例。
- **`canonical-sections`** — `install section drift: hand-edit detected in a generator-owned section`。`## Prerequisites: Install the CLI` 区块已被手动编辑，偏离了生成器当前为该 CLI 输出的内容。**不要手动编辑安装区块。** 它由 `internal/generator/templates/skill.md.tmpl` 模板生成，参数为 `(api_name, category, uses_browser_http_transport)`；任何偏差都意味着自动化步骤或人员修改了机器拥有的文本。解决方法是重新生成该打印 CLI（在此目录上运行 `printing-press regen`，或对于已发布的 CLI，从 spec 重新生成并重新发布）。如果规范文本本身有误（例如安装说明确实需要变更），修改模板，而非打印的 CLI。

在编辑 SKILL.md 其他部分时，先 Read 受影响的区块，编辑完成后再次 Read。`Edit` 替换的是字面字符串；如果周围上下文已漂移，一次 Edit 可能将第二份区块嫁接到第一份上，而非替换它。

修复完成后，重新运行 `"$PRINTING_PRESS_BIN" verify-skill --dir "$CLI_DIR"` 并确认退出码为 0，然后再继续。

### 优先级 6：剩余的 dogfood 问题

- 路径有效性不匹配
- 认证协议不匹配
- 示例漂移（示例引用了错误的命令）
- 数据管道完整性问题

### 优先级 7：MCP 工具质量

**你现在的目标是确保此 CLI 暴露的每个 MCP 工具都具有 agent 级别的描述和正确的读/写分类。** 工具描述和分类是 agent 发现和决定是否调用工具的方式——描述薄弱且缺少注释会直接降低 agent 体验，而 Phase 1 的机械门禁（verify、dogfood）无法捕获此类问题。

停下来执行：

1. 运行 `"$PRINTING_PRESS_BIN" tools-audit "$CLI_DIR" --json` 以暴露机械发现（空的 Short、薄弱的 Short、读取型命令名称缺少 `mcp:read-only`）。
2. 你必须阅读 `references/tools-polish.md` 并按照其说明处理所有发现，**并且**对每个命令进行判断审查——无论审计是否标记了它。审计捕获的是机械问题；描述质量和边界分类（只读 vs. 本地写入）始终需要 agent 推理。不得跳过此步骤。
3. **接受 MCP 描述发现有更严格的契约要求。** `thin-mcp-description` 和 `empty-mcp-description` 的接受操作需要按发现填写三个预决策字段（`spec_source_material`、`target_description`、`gap_analysis`）。二进制文件会拒绝批量接受（>5 个发现共享同一理由），并且不会提升 MCPDescriptionQuality 就标记为"完成"。通过 override 或生成器改进来修复是预期路径；接受操作是罕见的。完整契约参见 `references/tools-polish.md` 的 "Marking a finding accepted" 章节。

仅当审计摘要行显示 `no pending findings` 且没有 `incomplete:` 块时（所有门禁——预决策字段、重复理由、记分卡增量——均通过），才继续进入 "After all fixes"。

### 优先级 8：客户 PII 门禁

**你现在的目标是清除 PII 台账，使 promote 和 publish 门禁通过。** PII 门禁是阻止真实客户值进入已发布库内容的确定性底线。它捕获高风险文件中的卡号末四位、邮箱、美国电话、ZIP+4 和邮政地址格式。

停下来执行：

1. 运行 `"$PRINTING_PRESS_BIN" pii-audit "$CLI_DIR" "${PII_ARGS[@]}"` 以暴露待处理发现（或从 Phase 1 基线读取 `/tmp/polish-pii-audit-before.json`）。当 `RESEARCH_DIR` 存在时，这包括该运行的 `research.json` 和 `research/*.md`，带有 `.manuscripts/<run-id>/...` 路径，以便接受操作能传递到 `publish package`。
2. 你必须阅读 `references/pii-polish.md` 并按照其逐项决策树处理——在源文件中用不匹配的占位符替换真实值，或使用 `category` + `evidence_context` 预决策字段接受。
3. **接受 PII 发现有严格契约要求。** 缺少字段、6 个以上接受操作共享同一理由、或在无源文件修复的情况下整体接受 ≥10 个发现，都会导致门禁失败。完整规则参见 `references/pii-polish.md` 的 "The accept contract" 和 "Forbidden accept patterns"。

仅当 `pii-audit` 显示 `no pending findings` 且没有 `incomplete:` 块时，才继续进入 "After all fixes"。

### 所有修复完成后

```bash
go build -o "$CLI_NAME" ./cmd/"$CLI_NAME"
gofmt -w .
```

## Phase 3：重新诊断

在修复后的 CLI 上重新运行诊断扫描：

```bash
# RESEARCH_ARGS 在此处也必须随 dogfood 一起传递——否则，
# checkNovelFeatures 在 Phase 2 编辑后不会重新同步 novel_features_built，
# 而 publish-validate 的 transcendence 门禁会读取 Phase 1 通过时的过期状态。
"$PRINTING_PRESS_BIN" dogfood --dir "$CLI_DIR" $SPEC_FLAG "${RESEARCH_ARGS[@]}" 2>&1
"$PRINTING_PRESS_BIN" verify --dir "$CLI_DIR" $SPEC_FLAG --json 2>&1
"$PRINTING_PRESS_BIN" workflow-verify --dir "$CLI_DIR" --json 2>&1
"$PRINTING_PRESS_BIN" verify-skill --dir "$CLI_DIR" --json 2>&1
if [ "$STANDALONE_MODE" = "true" ]; then
  "$PRINTING_PRESS_BIN" publish validate --dir "$CLI_DIR" --json 2>&1
fi
"$PRINTING_PRESS_BIN" scorecard --dir "$CLI_DIR" $SPEC_FLAG 2>&1
"$PRINTING_PRESS_BIN" tools-audit "$CLI_DIR" 2>&1
"$PRINTING_PRESS_BIN" pii-audit "$CLI_DIR" "${PII_ARGS[@]}" 2>&1
go vet ./... 2>&1
if command -v gosec >/dev/null 2>&1; then
  gosec -fmt=json -out=/tmp/polish-gosec-after.json ./... 2>&1 || true
else
  go run github.com/securego/gosec/v2/cmd/gosec@v2.26.1 -fmt=json -out=/tmp/polish-gosec-after.json ./... 2>&1 || true
fi
```

记录修复后的分数，包括最终 `scorecard --live-check --json` 输出中的 live matrix 限定条件。如果 gosec 命令在写入 `/tmp/polish-gosec-after.json` 之前失败，将缺少修复后扫描视为 polish 失败：将其添加到 `remaining_issues`，设置 `ship_recommendation: hold`，并包含 stderr 摘要。如果 verify-skill 仍有任何 `severity=error` 发现、workflow-verify 仍报告 `workflow-fail`、publish-validate 仍报告 `passed: false`（仅限 standalone 模式——管道中间 polish 不运行此检查）、gosec 仍报告手工编写的 novel-feature Go 中未解决的发现、pii-audit 仍有待处理发现或门禁失败、或最终 live matrix 限定条件为 `not_exercised`，则无法触发 ship（参见下方的 ship 逻辑）。对于未执行的 live matrix，在 `remaining_issues` 中添加一项，例如 `live matrix not exercised (mock-only/no live token); run the live gate before publish`。

## Ship 逻辑

计算 ship 建议：

- **`ship`**：verify ≥ 80%，scorecard ≥ 75，无关键失败，**且** verify-skill 退出码为 0（无 SKILL/CLI 不匹配），**且** workflow-verify 不是 `workflow-fail`，**且**（当 `STANDALONE_MODE=true` 时）publish-validate 报告 `passed: true`，**且** gosec 在手写 novel-feature Go 中零未解决发现，**且** tools-audit 显示零待处理发现（所有发现已修复或附带理由明确接受），**且** pii-audit 显示零待处理发现且零门禁失败（所有 PII 发现已在源文件中修复或附带有效预决策字段接受）。SKILL/workflow/publish/gosec/PII 门禁是硬性要求：携带一个对自身撒谎的 SKILL 的 CLI 发布（verify-skill 发现）会给 agent 错误的指令；主要工作流未通过验证的 CLI 实际上并未发布；publish-validate 拒绝的 CLI 不可发布；手写 novel-feature 代码中存在未解决安全静态分析发现的 CLI 仍然是审查者的靶子；在 promote/publish 门禁处 pii-audit 失败的 CLI 无论如何都会停止发布。publish-validate 门禁仅在 polish 运行了它时适用（standalone 模式）；管道中间 polish 将发布就绪性推迟到主 SKILL 的 Phase 6。
- **`ship-with-gaps`**：verify ≥ 65%，scorecard ≥ 65，存在非关键差距，**且** 上述 SKILL/workflow/gosec/PII 门禁均满足，**且**（当 `STANDALONE_MODE=true` 时）publish-validate 门禁满足，**且** README 包含 `## Known Gaps` 区块，列出面向用户的差距。仅保留给极少数重构或外部依赖阻塞导致无法干净修复的情况。

  **ship-with-gaps 必须附带 README Known Gaps。** 已发布的库副本是下游用户看到的内容；如果判定声称存在差距但 README 隐藏了它们，下游用户将遇到一个行为异常且无披露的 CLI。在发出 `ship_recommendation: ship-with-gaps` 之前：

  1. 阅读 CLI 的 `README.md`。如果 `## Known Gaps` 区块已存在（例如主 SKILL Phase 4 在 polish 运行前已写入），确认其覆盖了 `remaining_issues` 中的面向用户条目。为 polish 新发现的面向用户差距添加条目。
  2. 如果缺少 `## Known Gaps`，则写入它——放置在 `## Quick Start` 之后（或 `## Usage` 之前），以镜像 `## Unique Features` 的放置惯例。每个面向用户的 `remaining_issues` 条目一个项目符号。从用户视角表述：哪个命令行为异常，替代方案是什么。示例：

     ```markdown
     ## Known Gaps

     - **`analytics export --csv`** 在超过 10k 事件的工作区上返回截断行。作为临时替代方案，使用 `--json` 并通过管道传给 `jq`，直到底层导出端点支持分页。
     ```

  3. 填充该区块时，从 `remaining_issues` 中筛选面向用户的条目。内部条目（已弃用标志上的 verify 漂移、MCP 描述调优、polish 内部备注）不属于公开的 Known Gaps。如果 agent 无法从 `remaining_issues` 中识别出任何面向用户的差距，判定为 `ship`，而非 `ship-with-gaps`。
  4. 在 `fixes_applied` 中列出每次 Known Gaps 的写入/更新，以便调用方可以展示此操作的发生。

  如果 polish 无法根据现有证据合理填充 Known Gaps（例如 `remaining_issues` 全部是内部术语，无面向用户的解读），将判定降级为 `hold`，而非在无披露的情况下发布。
- **`hold`**：verify < 65% 或 scorecard < 65 或存在关键失败，**或** verify-skill 有未解决发现，**或** workflow-verify 报告 `workflow-fail` 且该工作流是 CLI 的核心价值，**或**（当 `STANDALONE_MODE=true` 时）publish-validate 报告 `passed: false`，**或** gosec 仍报告手写 novel-feature Go 中未解决发现，**或** pii-audit 仍有待处理发现或门禁失败，**或** Phase 3 门禁束表明这是一个先前低于 60 分且缺少 transcendence 行的重新打印且无已接受的 `partial_transcendence_override`。管道中间 polish 永远不会因 publish-validate 而达到 `hold`——该检查在此模式下不运行，`publish_validate_*` 输出为 `skipped (mid-pipeline)`。

### 在不刷分的前提下提升

Ship 门禁是底线，而非上限。通过门禁后，检查记分卡中仍低于满分的维度，判断每个差距是真实的还是结构性的：

1. **找到根本缺陷，而非分数。** 记分卡是质量的代理指标，而非目标本身。README 得分 8/10 可能缺少 Cookbook 章节或有过期命令——这是真实且可修复的差距。一个 200 端点 API 的 `mcp_surface_strategy` 得分 2/10 可能标记的是表面大多是端点镜像——也可能可修复。
2. **如果存在真实的、agent 级别的改进空间，就执行它。** 更好的描述、缺失的标志文档、薄弱的 README 章节、不反映实际用法的示例。CLI 变得更好，分数随之提升。
3. **如果缺陷是结构性的，记录并接受。** 某些维度假设了 CLI 领域不具备的能力（只读 API 被写入工作流维度评分、无认证的 CLI 被认证维度评分、小型 API 被按大型 API 校准的 `surface_strategy` 阈值惩罚）。在 `skipped_findings` 中注明原因，然后继续。
4. **绝不添加脚手架来满足评分器。** 虚假命令、虚假测试、虚假标志，或纯粹为提升数字而写的样板文字——这些会让 CLI 降级以满足代理指标。评分器按设计就是不完善的（AGENTS.md 中"scoring may be imperfect"的免责声明适用）。信任底层判断，而非数字。

#### MCP 记分卡维度映射到 spec 字段，而非生成器代码

当 `mcp_token_efficiency`、`mcp_tool_design`、`mcp_remote_transport` 或 `mcp_surface_strategy` 低于满分时，修复几乎总是 spec 编辑 + 重新生成（或从新生成的树执行 `regen-merge`），**而非** 生成器模板变更。Polish 可以处理这些——不要将它们归类为"向生成器拥有的文件添加功能，候选回溯修复"。Cobratree 外部调用工具已经从 Short 编目（而非 operator Long help），因此残留的 `mcp_token_efficiency` 压力来自 typed 端点描述，而非框架 `--help`。

| 薄弱维度 | 修复它的 spec 字段 | 需添加到 `spec.yaml` 的 `mcp:` 区块的内容 |
|---|---|---|
| `mcp_remote_transport` | `mcp.transport` | `transport: [stdio, http]`（在 `spec.DefaultRemoteTransportEndpointThreshold` 及以下规模的 API 的 typed 端点已默认获得此配置；仅当 spec 选择了更窄的列表或 API 超过阈值但仍需远程访问时才需要覆盖） |
| `mcp_token_efficiency`、`mcp_surface_strategy` | `mcp.endpoint_tools`、`mcp.orchestration` | `endpoint_tools: hidden` + `orchestration: code`（Cloudflare 模式：约 70 个原始端点工具坍缩为 `<api>_search` + `<api>_execute`；所有端点仍可通过 execute 到达） |
| `mcp_tool_design` | `mcp.intents` | 为 API 支持的工作流定义多步 intent 组合 |
| `mcp_description_quality` | `mcp-descriptions.json`（CLI 根目录的覆盖文件） | 每工具描述覆盖；从 spec 派生的薄弱描述可获取更丰富文本而无需编辑 spec |

推荐阈值：当手动输入的端点数超过50个时，默认推荐全部四个（`transport`、`endpoint_tools=hidden`、`orchestration=code`、`intents`用于标题工作流）。小型API（<= `spec.DefaultRemoteTransportEndpointThreshold`）默认已获得http传输，因此`mcp_remote_transport`在无需修改规范的情况下即可达到10/10——只有当规范明确缩小列表时才需指出。完整参考是`docs/SPEC-EXTENSIONS.md`。

编辑规范后，重新生成（或将更改合并到已发布的库中），以便新的`mcp:`块能够到达模板。CobraTree遍历的新命令无论如何都会作为MCP工具出现；它们不需要规范更改。

经验法则：如果你的修复即使没有计分卡仍然有价值，那就去做。如果唯一的动机是“推动计分”，那就不要做。

## 显示差异并发出结果块

向用户显示差异，然后发出结构化的`---POLISH-RESULT---`块。该块允许调用技能（例如，主印刷机Phase 5.5）可靠地解析推荐和分数；上面的人类可读表格是给用户的。

```
<CLI_NAME>的精炼结果：

                    之前    之后    差异
  计分卡：        XX/100    XX/100    +N
  验证：           XX%       XX%       +N%
  活矩阵：      练习/未练习 -> 练习/未练习
  工具审计：      XX        XX        -N待处理发现

已应用的修复：
  - 每个修复的简短描述

跳过的问题：
  - <问题>：你选择不修复的原因

剩余问题：
  - 你试图修复但无法解决的问题的简短描述

---POLISH-RESULT---
scorecard_before: <N>
scorecard_after: <N>
verify_before: <N>
verify_after: <N>
dogfood_before: <PASS|FAIL>
dogfood_after: <PASS|FAIL>
dogfood_live_matrix_before: <练习|未练习|未知>
dogfood_live_matrix_after: <练习|未练习|未知>
govet_before: <N>
govet_after: <N>
gosec_before: <N>
gosec_after: <N>
tools_audit_before: <N待处理>
tools_audit_after: <N待处理>
publish_validate_before: <PASS|FAIL|跳过（中管道）>
publish_validate_after: <PASS|FAIL|跳过（中管道）>
fixes_applied:
- 每个修复的简短描述
skipped_findings:
- <问题>：你选择不修复的原因
remaining_issues:
- 你试图修复但无法解决的问题的简短描述
ship_recommendation: <发布|发布带缺口|暂停>
further_polish_recommended: <是|否>
further_polish_reasoning: <解释调用的一句话>
---END-POLISH-RESULT---
```

这三个列表有不同的用途：
- **fixes_applied**：发生了什么变化——调用者显示这些
- **skipped_findings**：你发现但故意不修复的问题，附有理由（例如，“验证将`stale`分类为读取——评分器错误，不是CLI问题”，“`version`接受thin-short——准确且简短）。调用者显示这些，以便用户可以决定是否手动处理。
- **remaining_issues**：你试图修复但无法解决的问题。

**`publish_validate_*`值。** 当精炼运行了publish-validate（独立模式）时发出`PASS`或`FAIL`。当精炼跳过了它（中管道调用，`STANDALONE_MODE=false`）时发出字面字符串`跳过（中管道）`。跳过值仅用于信息：调用者在决定是否将精炼的`ship_recommendation`级联到CLI级别的暂停时，不应将其视为失败。

**`dogfood_live_matrix_*`值。** 仅当live-check评估了至少一个真实样本时才发出`练习`。对于模拟-only/无令牌/无研究/未评估样本运行发出`未练习`。当`dogfood_after: PASS`但`dogfood_live_matrix_after: 未练习`时，人类摘要必须说`dogfood PASS（模拟仅用；活矩阵未练习——在发布前运行活门）`，并且`ship_recommendation`必须为`暂停`，除非父调用者明确拥有后续的活门。

**`gosec_*`值。** 发出生成文件筛选后仍然与打印的CLI相关的gosec发现的数量。这些值有意不是来自`/tmp/polish-gosec-*.json`的原始`Issues[]`长度：不要计算被路由到`skipped_findings`作为逆向候选的生成器发出的发现，但要计算迫使`暂停`的手动编写的未解决发现。

### 选择`further_polish_recommended`

由你的判断，而不是`remaining_issues`的数量决定。当另一个精炼调用有实际机会解决剩余问题时，设置`是`：

- `remaining_issues`包括你因时间不足而未能运行的验证或dogfood失败，而一个带有更多关注每个失败的全新通过可能有可能解决。
- 你已经落地的修复可能解除了你这次无法触及的依赖问题。
- SKILL/CLI不匹配需要在这次通过更改源代码树后进行第二次检查。

设置`否`当另一个调用会重新踩同样的地面：

- `remaining_issues`是用户才能做出的决定（重命名旗舰命令、选择默认行为、接受结构权衡）。
- 你已经尝试了两种不同的修复方式，并且都以相同的原因失败。
- 阻塞因素是外部的（API改变了形状、速率限制、缺少凭证），而不是一个全新的精炼运行能看到的不同之处。
- `remaining_issues`为空并且`skipped_findings`都是环境或结构性的——精炼没有剩下什么可做的。

`further_polish_reasoning`是一句调用者逐字显示的句子。使其具体（“`analytics export`和`report show`的验证失败看起来可以解决，但我太早放弃了”）而不是通用（“更多的精炼可能会有帮助”）。调用者使用这个信号来决定是否在下次提示中提供“再次精炼”；一个模糊的理由会使他们的提示模糊。

## 发布提议

**除非`STANDALONE_MODE`为真，否则跳过整个这一节。** `STANDALONE_MODE`在上述“解决CLI”块中根据调用者模式设置：对于斜杠命令调用（`/printing-press-polish ...`）或传递`--standalone`到`args`的技能工具调用为真；否则为假。当为假时，精炼是从主SKILL Phase 5.5或暂停路径“精炼以重试”中调用的，工作CLI尚未提升到库。`/printing-press-publish <slug>`将解析到`$PRESS_LIBRARY/<slug>/`，它要么为空，要么包含陈旧的先前的运行——在这里调用发布要么无法解析，要么会发布错误的副本。父技能拥有该路径上的发布流程；只需发出结果块并返回。

应用发布回合边界规则：`AskUserQuestion`的答案可能仅授权传递消息，而不是同回合发布。发布会打开或更新公共库PR，因此它需要在精炼完成后需要一个新的用户编写的消息。有关理由，请参阅`references/publish-turn-boundary.md`。

一个简单的检查：

```bash
if [ "$STANDALONE_MODE" != "true" ]; then
  echo "非独立调用者；跳过发布提议"
  return
fi
```

门是调用者模式标志，**不是**解析的路径。没有`--standalone`的技能工具调用即使路径位于`$PRESS_LIBRARY/<slug>/`下也会推迟发布；这是更安全的默认值，并且是唯一能捕获倒置的Phase 5.5/5.6失败模式（中管道运行触发公共分支+PR）在精炼边界的方式。之前的路径子字符串启发式（`*.runstate/*`）在这里不再承担负载——它已保留在上述研究目录解析块中，因为该块是在选择两个真实的磁盘布局，这与其他发布门控的问题是不同的。

对于独立调用，继续执行下面的提议。

如果`ship`或`ship-with-gaps`：

从结果块构建提示。形状是数据驱动的，因此用户永远不会被要求权衡“再次精炼”与“发布”，当精炼本身决定另一个通过不会有帮助时。

### 建议

从精炼结果中选择推荐的操作：

- `ship` + `remaining_issues`为空 → 推荐**发布**。
- `ship` + `remaining_issues`非空 + `further_polish_recommended: 是` → 推荐**再次精炼**。
- `ship` + `remaining_issues`非空 + `further_polish_recommended: 否` → 如果剩余问题不触及CLI的标题命令，则推荐**发布**；否则显示权衡，并让用户在**发布**（如原样；README不会自动更新`ship`裁决）和**完成**之间决定。
- `ship-with-gaps` + `further_polish_recommended: 是` → 推荐**再次精炼**。
- `ship-with-gaps` + `further_polish_recommended: 否` → 推荐**发布**（缺口已经在README的`## 已知缺口`中，因为精炼的ship逻辑强制为`ship-with-gaps`——见上面的“ship逻辑”）或**完成**如果缺口是发布阻塞的——代理判断。

### 菜单

当`further_polish_recommended: 否`时完全抑制“再次精炼”选项。始终保留“发布”和“完成”。

当精炼选择不推荐另一个通过时，显示`further_polish_reasoning`作为上下文——用户应该看到为什么精炼完成了。

通过`AskUserQuestion`呈现。两个示例形状：

**精炼收敛干净**（`remaining_issues`为空，`further_polish_recommended: 否`）：

> "<CLI_NAME>精炼：计分卡XX/100，验证XX%。精炼运行干净——没有更多可修复的。
>
> 建议：发布。
>
> 1. **单独发布**（推荐）——显示下一个用户消息的发布命令
> 2. **暂时完成**——CLI位于$PRESS_LIBRARY/<cli-name>"

**精炼认为另一个通过会有帮助**（`remaining_issues`非空，`further_polish_recommended: 是`）：

> "<CLI_NAME>精炼：计分卡XX/100，验证XX%。剩余<N>个问题。
>
> 精炼备注：'<further_polish_reasoning>'
>
> 建议：在发布前再次精炼。
>
> 1. **再次精炼**（推荐）——关闭剩余的<N>个问题
> 2. **单独发布**——显示下一个用户消息的发布命令以原样发布
> 3. **暂时完成**——CLI位于$PRESS_LIBRARY/<cli-name>"

推荐的选项领先，带有`(推荐)`标签，并且领先的`建议:`行明确声明了代理的调用。三个加强渠道，以便用户不必从顺序中推断。
