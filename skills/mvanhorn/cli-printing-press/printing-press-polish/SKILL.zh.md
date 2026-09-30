---
name: printing-press-polish
description: 将生成的 CLI 打磨至通过验证，使其达到可发布状态。执行诊断（dogfood、verify、scorecard、go vet、gosec），自动修复所有问题（验证失败、静态分析发现、死代码、描述、README、MCP 工具质量），报告修复前后的差异，并提议发布。在每次运行 /printing-press 之后，或在 $PRESS_LIBRARY/ 中的任何 CLI 上使用。触发短语："polish"（打磨）、"improve the CLI"（改进该 CLI）、"fix verify"（修复验证）、"make it publish-ready"（使其可发布）、"clean up the CLI"（清理该 CLI）、"get this ready to ship"（使其具备发货条件）。
---

# /printing-press-polish

对生成的 CLI 进行打磨，使其通过验证并准备好发布。

复古改进了 Printing Press。打磨改进了生成的 CLI。这项技能在分叉的上下文中运行（`context: fork`），因此其诊断和修复循环不会污染调用者——诊断垃圾、修复迭代和重新诊断噪音都局限于打磨会话，调用者接收到的是一个干净的摘要。

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
- 您希望 CLI 一次性通过发布

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

# 中间流程的调用者可以在参数包中传递 printing_press_bin: <绝对路径>。优先使用它，以便分叉的打磨会话继续使用父技能预先选择的二进制文件，而不是通过 PATH 重新解析。
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
    echo "[setup-error] cli-printing-press 二进制文件需要 Go $_pp_go_required 或更高版本 (已安装: $_pp_go_installed)。"
    echo "GOTOOLCHAIN=local 禁用自动工具链下载，因此后续的 Go 质量门禁会失败。"
    echo "从 https://go.dev/dl/ 安装 Go $_pp_go_required 或更高版本，或取消设置 GOTOOLCHAIN。"
    echo ""
    return 1
  fi

  echo "[go-toolchain-old] cli-printing-press 二进制文件需要 Go $_pp_go_required 或更高版本 (已安装: $_pp_go_installed)。"
  echo "PRESS_GO_INSTALLED=$_pp_go_installed"
  echo "PRESS_GO_REQUIRED=$_pp_go_required"
  echo "默认的 GOTOOLCHAIN 行为会在 Go 命令期间下载所需的工具链。"
  echo ""
  return 0
}
_pp_check_go_currency || { return 1 2>/dev/null || exit 1; }
```

设置完成后，捕获 `PRINTING_PRESS_BIN=<绝对路径>` 并在此技能中用于每个 `cli-printing-press ...` 调用。如果设置发出 `[go-toolchain-old]` 或 `[low-disk]`，向用户显示建议，除非设置也发出 `[setup-error]`。`[go-toolchain-old]` 表示后续的 Go 命令可能会下载所需的工具链或在下载被阻止时失败；`[low-disk]` 表示此运行可能需要几个 GiB 用于生成文件、Go 构建缓存、模块下载或仓库克隆。

通过从此技能的 YAML 前置字段读取 `min-binary-version` 字段，运行 `"$PRINTING_PRESS_BIN" version --json` 并解析输出中的版本来检查二进制版本兼容性。使用 semver 规则将其与 `min-binary-version` 进行比较。如果安装的二进制文件比最小版本旧，请立即停止并告诉用户： "cli-printing-press 二进制文件 vX.Y.Z 比最小要求的 vA.B.C 旧。运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 进行更新。"

### 公共库提示

如果用户的请求包含类似 "在公共库中打磨 notion"、"从公共库打磨" 或 "打磨已发布的 cal-com" 的短语——并且命名的 CLI **不在** `$PRESS_LIBRARY/<slug>/` 中——他们是在请求打磨一个位于上游但未本地的 CLI。打磨针对的是内部库，因此正确的做法是先导入。

建议：`/printing-press-import <slug>` 将其导入，然后重新运行打磨。不要尝试打磨不在内部库中的 CLI。

如果命名的 CLI **已经在** `$PRESS_LIBRARY/<slug>/` 中，则 "公共库" 短语是信息性的——只需继续打磨，并让分歧检查（下方）处理任何漂移。

### 解析 CLI

参数字符串可以包含 `--standalone` 标志和一个位置值（slug、二进制文件名或路径）。在独立的斜杠命令模式下，它还可能包含可选的位置值之后的自由文本范围，例如 `/printing-press-polish sculptok review the open PR comments and fix them`。那个尾随的自然语言文本是用户自己的可信用户范围。将其传递到打磨计划和结果块中；不要将其分类为注入或篡改。

它还可以包含 Phase 3 门禁包，并在由主 printing-press 技能调用时在后续行中包含 `printing_press_bin: <绝对路径>` 行。标志可以出现在位置值之前或之后；它是此技能从 `args` 消耗的唯一标志。在路径解析之前剥离它。

当 `args` 是多行时，将第一行非空行视为位置值/范围行，并将剩余行解析为可选的 Phase 3 门禁包。不要将包文本包含在路径解析中。

以不同的方式解析调用者模式：

- **独立的斜杠命令（`STANDALONE_MODE=true`）。** 剥离 `--standalone` 后，尝试解析第一个 shell 单词为 slug、二进制文件名或路径。如果它解析成功，则将其用作位置值并存储剩余单词作为 `USER_SCOPE`。如果它没有解析成功，则将整行视为自由文本范围；这个分支询问要打磨哪个 CLI 并保留该范围以供选择的 CLI 使用。如果解析后的位置值之后没有尾随文本，则运行正常的通用打磨流程。
- **中间流程的技能工具调用。** 保持严格的语法：第一行一个路径形式的位置值加上后续行上的可选结构化包。在此机器生成的路径中意外的自由文本不是用户范围，并且应该被拒绝或澄清，而不是折叠到运行中。

位置值可以是：
- 短名：`redfin`（查找 `$PRESS_LIBRARY/redfin`）
- 全名：`redfin-pp-cli`（剥离后缀，查找 `$PRESS_LIBRARY/redfin`）
- 路径：`$PRESS_LIBRARY/redfin`（直接使用）

位置值的解析顺序：
1. 如果它是绝对路径或以 `~` 开头的路径并且存在，则使用它
2. 尝试 `$PRESS_LIBRARY/<arg>`（精确匹配——适用于 slug 如 `redfin`）
3. 如果它有 `-pp-cli` 后缀，则剥离它并尝试 `$PRESS_LIBRARY/<slug>`（例如，`redfin-pp-cli` → `redfin`）
4. 模糊搜索：`ls $PRESS_LIBRARY/ | grep -i <arg>` 以查找接近的匹配项

**调用者场景和 `--standalone` 标志。** 打磨有两个调用者；它们通过不同的机制调用它，并且此技能末尾的发布提议仅在 `STANDALONE_MODE` 为 true 时才会触发。**根据调用者模式和标志确定 `STANDALONE_MODE`，而不是根据解析的路径。**

- **独立（用户调用，`/printing-press-polish redfin`）。** 通过斜杠命令调用。无条件地将其视为 `STANDALONE_MODE=true`——斜杠命令形式是发布意图的表面，即使用户省略了标志。参数是一个 slug 或二进制文件名；解析结果落在 `$PRESS_LIBRARY/<slug>/`。这是发布的副本，也是正确的目标。
- **中间流程（主 printing-press 技能 Phase 5.5，hold-path "打磨以重试"）。** 通过技能工具调用，`args: "$CLI_WORK_DIR"`。参数是到 `~/printing-press/.runstate/.../runs/.../working/<api>-pp-cli/` 的绝对路径；解析必须命中规则 1。`STANDALONE_MODE=false` 默认——主技能对此路径拥有发布流程，因此打磨会推迟。**不要将参数改写为 slug**——Phase 5.5 在工作 CLI 被提升之前触发，因此 `$PRESS_LIBRARY/<slug>/` 要么不存在，要么包含 *先前运行* 的过时 CLI。
- **技能工具独立覆盖。** 一个非斜杠调用者如果真心希望打磨以发布，必须通过在 `args` 中包含 `--standalone`（例如，`args: "--standalone $PRESS_LIBRARY/redfin"`）显式选择。没有这个标记，从技能工具调用中打磨永远不会发布——即使解析的路径恰好位于 `$PRESS_LIBRARY/` 下。标志是合同；路径不是。

这个调用者模式驱动的门禁取代了旧的路径子字符串启发式（`*.runstate/*`）。启发式在主技能的 Phase 5.5/5.6 顺序反转时失效，或者当从非 `.runstate` 的临时布局调用打磨时：打磨会看到 `$PRESS_LIBRARY/<slug>/` 路径，得出 "独立" 的结论，并在中间流程运行中触发其发布提议（分叉、全局 git 配置、公共 PR）。标志是明确的，更安全的默认值是不发布。

### Phase 3 门禁包

中间流程的调用者在 `args` 中 CLI 路径之后传递这些字段：

```yaml
phase3_transcendence_rows_planned: <计划>
phase3_transcendence_rows_built: <构建>
phase3_transcendence_rows_missing:
  - <清单行名或命令>
prior_sub60_reprint: <true|false>
partial_transcendence_override: <无或构建日志备注路径>
```

在诊断之前解析包并保留值以供发货逻辑使用。缺失的包字段表示 "没有强制 Phase 3 持有"；它们不会阻止独立的打磨。如果 `prior_sub60_reprint: true`、`phase3_transcendence_rows_missing` 包含任何行，并且 `partial_transcendence_override` 为空或 `none`，则打磨必须发出 `ship_recommendation: hold`，即使本地诊断其他方面干净。将缺失的行添加到 `remaining_issues`，以便父技能可以显示阻止提升的特定门禁。

下一个代码块中的锁状态检查是中间流程场景的安全网：如果为该 CLI 持有构建锁（无论哪种名称形式），打磨将拒绝运行。`cli-printing-press lock` 在内部规范化 slug ↔ 二进制文件名，因此无论基名产生哪种形式，检查都有效。

如果没有匹配项或多个匹配项，通过 `AskUserQuestion` 显示。最多显示 4 个匹配项，按修改时间排序（最新的在前），并使用人类友好的相对时间戳（例如，"生成 2 小时前"）。

```bash
CLI_DIR="<解析路径>"
CLI_NAME="$(basename "$CLI_DIR")"
STANDALONE_MODE="<true|false>"  # true 如果是斜杠命令调用或在 args 中包含 --standalone；Skill-tool 调用默认为 false

# 检查是否存在活动的构建锁——打磨编辑将被运行中的构建覆盖，当构建提升到库时。
_lock_json=$("$PRINTING_PRESS_BIN" lock status --cli "$CLI_NAME" --json 2>/dev/null)
if echo "$_lock_json" | grep -q '"held".*true'; then
  if echo "$_lock_json" | grep -q '"stale".*true'; then
    echo "警告：存在 $CLI_NAME 的过时锁（构建可能已崩溃）。"
    echo "继续打磨。运行 '$PRINTING_PRESS_BIN lock release --cli $CLI_NAME' 清除。"
  else
    echo "正在进行 $CLI_NAME 的构建。"
    echo "打磨编辑将被构建覆盖。"
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

### 查找规范和研究目录

```bash
API_SLUG="${CLI_NAME%-pp-cli}"
SPEC_PATH=""
for f in "$PRESS_HOME/manuscripts/$API_SLUG"/*/research/*.yaml "$PRESS_HOME/manuscripts/$API_SLUG"/*/research/*.json "$PRESS_HOME/manuscripts/$CLI_NAME"/*/research/*.yaml "$PRESS_HOME/manuscripts/$CLI_NAME"/*/research/*.json; do
  if [ -f "$f" ]; then
    SPEC_PATH="$f"
    break
  fi
done

# 构建spec标志一次。如果没有找到spec则为空——诊断命令接受缺失的 --spec 并优雅地降级。
SPEC_FLAG=""
if [ -n "$SPEC_PATH" ]; then
  SPEC_FLAG="--spec $SPEC_PATH"
fi

# 定位研究目录。dogfood的 --research-dir 触发 checkNovelFeatures，该函数将 novel_features_built 写回 research.json 并将验证的列表同步到 .printing-press.json 中。
# 没有这个标志，预日期 novel_features schema 的旧版CLI将无法通过 publish-validate 的超越关卡。
#
# 处理两种布局，根据 $CLI_DIR 路径结构键值对（不是 manuscripts 条目的缺失——重新生成先前发布的API会留下旧的manuscripts条目，这些条目将指向错误的 research.json）：
# 1. 中间管道抛光（从主 printing-press 流程在 promote 之前调用）：$CLI_DIR 位于 $PRESS_RUNSTATE/.../runs/<id>/working/<cli>（即路径包含 .runstate/），research.json 位于 $PRESS_RUNSTATE/.../runs/<id>/research.json — $CLI_DIR 的祖父。
# 2. promote 之后（独立抛光）：research.json 位于 manuscripts/<api>/<run-id>/research.json。
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
    # 匹配 publish 包的回退：API slugs 优先，然后是 CLI 名称，每个使用字典序最新的 run id 当 manifest 没有指定时。
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

# 使用 bash 数组，以便标志在包含空格的路径中幸存（例如，当 $HOME 或 $PRESS_RUNSTATE 通过包含空格的路径解析时）。
RESEARCH_ARGS=()
if [ -n "$RESEARCH_DIR" ]; then
  RESEARCH_ARGS=(--research-dir "$RESEARCH_DIR")
fi

# pii-audit 对 CLI 目录运行，但 publish 包稍后会将相同的运行存档复制到 .manuscripts/<run-id> 之前强制执行 PII 关卡。
# 将运行目录传递给抛光，以便抛光看到与 publish 将扫描的相同相对路径的叙事性 manuscript 文件。
PII_ARGS=()
if [ -n "$RESEARCH_DIR" ]; then
  PII_ARGS=(--manuscripts-dir "$RESEARCH_DIR")
fi
```

### 分歧检查

**在第一阶段之前停止并运行此步骤。不要跳过它。在完成检查并解决任何分歧之前，不要继续进行诊断。**

内部副本在 `$CLI_DIR` 可能与公共库 (`mvanhorn/printing-press-library`) 副本脱节，如果有人直接在 CLI 最后发布后编辑了公共存储库。抛光过时的内部副本然后重新发布会无声地覆盖那些仅公开的修复——这是一个实际的问题，已发布的 CLI 已经遇到。

**你必须：**

1. **定位公共库克隆。** 如果设置了 `$PRINTING_PRESS_LIBRARY_PUBLIC`，请尊重它；否则扫描用户文件系统，以适合此平台的方式。通过检查 git 远程指向 `mvanhorn/printing-press-library` 来验证每个候选者——其他目录可能共享名称（分支，意外的名称冲突）。如果存在多个有效的克隆，请优先选择最近修改的；如果仍然不清楚，请要求用户消除歧义。
2. **在克隆中定位此 CLI。** `find <clone>/library -type d -name "<api>-pp-cli"` 或等效。
3. **运行 `diff -r <public-cli-dir> $CLI_DIR`** 带有这些排除项，所有这些在发布后都预期会分歧：
   - `.printing-press-tools-polish.json`（本地账本，未发布）
   - `.printing-press-pii-polish.json`（本地账本，未发布）
   - `go.mod` 和 `go.sum` — 发布会重写模块路径从 `<api>-pp-cli` 到 `github.com/mvanhorn/printing-press-library/library/<category>/<api>`
   - 所有 `.go` 文件，其中唯一差异是重写的导入路径（发布步骤通过每个内部导入传播新的模块路径）。在检查 `.go` 差异时，扫描实质性更改——任何超出模块路径前缀交换的内容都是真正的分歧。

   具体来说：`diff -r --exclude=go.mod --exclude=go.sum --exclude=.printing-press-tools-polish.json --exclude=.printing-press-pii-polish.json <public-cli-dir> $CLI_DIR`。

   不要传递 `--exclude='<api>-pp-cli'` 或 `--exclude='<api>-pp-mcp'` — 这些名称匹配根级别的二进制文件**和** `cmd/<api>-pp-cli/` 和 `cmd/<api>-pp-mcp/` 源目录。按二进制名称排除会无声地跳过整个 `cmd/` 子树，隐藏 `main.go` 中的真实分歧。"Only in $CLI_DIR: <api>-pp-cli" 行对于构建的二进制文件是预期输出的一行，不值得以牺牲完整性为代价进行过滤。
4. **在继续之前显示结果。**

结果：

- **未找到克隆** → 用户没有本地公共库。明确说明（“本地未找到公共库；继续使用内部作为规范”）并继续。
- **找到克隆但其中不包含此 CLI** → 从未发布或使用不同名称发布。说明并继续。
- **找到且 diff 为空** → 同步。说明并继续。
- **找到且分歧** → **停止**。不要运行第一阶段诊断。列出分歧文件供用户查看。通过 AskUserQuestion 询问：**同步公共→内部** 或 **不同步继续**。如果用户选择同步，将公共的分歧文件副本复制到内部，然后在同步的内部副本上继续抛光。

在显示同步提示之前，检查内部是否有文件在 `.printing-press.json` 时间戳之后被修改（用户在没有发布的情况下本地抛光）。如果是，明确提示提示：同步将覆盖他们的本地工作。让他们决定是否保留本地编辑或拉取公共的。

同步后（或明确跳过），其余的抛光操作都在 `$CLI_DIR` 上作为规范。最终的 `/printing-press-publish` 步骤将内部推回公共；在那里不需要第二次分歧检查。

**只有在明确声明了上述四种结果之一时，检查才会运行。** 静默遗漏视为未运行。

## 第一阶段：基线诊断

```bash
cd "$CLI_DIR"

# 构建
go build -o "$CLI_NAME" ./cmd/"$CLI_NAME" 2>&1

# 诊断。SPEC_FLAG 和 RESEARCH_ARGS 在上面的“查找 spec 和研究目录”步骤中设置。RESEARCH_ARGS 启用 dogfood 验证新颖功能并将它们同步到 .printing-press.json（发布验证的超越关卡所必需）。
"$PRINTING_PRESS_BIN" dogfood --dir "$CLI_DIR" $SPEC_FLAG "${RESEARCH_ARGS[@]}" 2>&1
"$PRINTING_PRESS_BIN" verify --dir "$CLI_DIR" $SPEC_FLAG --json 2>&1
"$PRINTING_PRESS_BIN" workflow-verify --dir "$CLI_DIR" --json > /tmp/polish-workflow-verify.json 2>&1 || true
"$PRINTING_PRESS_BIN" verify-skill --dir "$CLI_DIR" --json > /tmp/polish-verify-skill.json 2>&1 || true
# publish-validate 是发布就绪关卡，不是 CLI 就绪关卡。
# 中间管道抛光在主 SKILL 的 promote 步骤之前运行，在发布技能包工具-manifest.json 之前运行，所以其先决条件（manifest.printer 来自 git config github.user，打包的工具 manifest，phase5 接受证明移至 $CLI_DIR/.manuscripts/<run>/proofs/）
# 在此时尚未满足。在此处运行 publish-validate 会导致父管道拥有的失败级联到抛光的 ship_recommendation，主 SKILL 的 Phase 5.5 裁决将此转换为 CLI 级别的 hold。仅在抛光是发布入口点时（命令行调用或显式 --standalone）运行 publish-validate。
if [ "$STANDALONE_MODE" = "true" ]; then
  "$PRINTING_PRESS_BIN" publish validate --dir "$CLI_DIR" --json > /tmp/polish-publish-validate.json 2>&1 || true
fi
# --live-check 采样新颖功能输出并填充 live_check.features[].warnings（Wave B 实体检测）——就绪于“输出实体警告”行下有数据可读。
# RESEARCH_ARGS 指向运行的研究.json，当 CLI 位于 $PRESS_RUNSTATE/runs/<id>/working/<cli>（中间管道抛光）时。没有它，scorecard 查找二进制文件相邻，找不到 research.json，并报告 `unable: true`。
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

verify-skill 和 workflow-verify 与 dogfood/verify/scorecard 一起运行，以便抛光捕获公共库 CI 捕获的同一类失败。`publish-validate` 仅在 `STANDALONE_MODE=true`（命令行或 `--standalone` Skill 工具调用）时运行。publish-validate 分支是独立抛光的硬 ship-gate：在该模式下抛光不能推荐 `ship` 或 `ship-with-gaps`，而 `"$PRINTING_PRESS_BIN" publish validate` 报告 `passed: false`。中间管道抛光 (`STANDALONE_MODE=false`) 完全跳过 publish-validate —— 其先决条件（manifest.printer 来自 `git config github.user`，打包的 `tools-manifest.json`，phase5 接受证明移至 `$CLI_DIR/.manuscripts/<run>/proofs/`）是父管道拥有的，在此时尚未满足；主 SKILL 的 Phase 6 发布流程在正确的时间运行 publish-validate。有关此如何影响 ship_recommendation，请参阅“发布逻辑”下方。

**实时矩阵限定符。** 在每次 `scorecard --live-check --json` 运行后，读取 `/tmp/polish-scorecard.json` 并记录 `live_check` 是否实际执行了实时样本。仅当 `live_check.unable` 为 false 且至少评估了一个功能（`passed + failed > 0`，或等效功能状态）时，将其视为 `exercised`。将 `live_check.unable: true`，没有 `live_check`，没有评估的功能，或缺失凭证/令牌视为 `not_exercised`。干净的模拟 dogfood/verify 运行仍然有用，但它**不是** 实时矩阵通过。

`gosec` 作为手写 Go 的离线安全静态分析分支运行。当存在安装的 `gosec` 二进制文件时，请优先使用它；否则使用固定的 `go run github.com/securego/gosec/v2/cmd/gosec@v2.26.1` 回退，以便干净的机器在没有单独设置步骤的情况下仍能获得可重复的检查。读取 `/tmp/polish-gosec-before.json` 获取基线发现计数和问题详情。如果命令在写入 JSON 之前失败，将缺失的扫描视为抛光失败：将其添加到 `remaining_issues`，设置 `ship_recommendation: hold`，并包括 stderr 摘要，以便下次运行可以区分网络/工具失败与 CLI 缺陷。优先考虑手写文件中的发现：位于 `internal/cli/`，`internal/syncer/` 和 `internal/store/` 下且前 20 行缺少 `Generated by CLI Printing Press` 标头的整个文件是抛光拥有的新颖功能代码。生成器发出的文件中的发现是 Printing Press 逆向候选，除非它们可以通过更改规范并重新生成来永久修复；不要手动编辑生成的文件以静默 gosec。

**如果第一阶段基线显示底层 CLI 需要重新发现**——损坏的 HTML/SSR 提取，稀疏捕获（源 manuscript 中少于 5 个唯一端点），错误的端点形状，缺少 GraphQL 操作哈希，或任何表明 CLI 是从不完整的捕获生成的信号——抛光通常不会自己进行浏览器捕获。当需要重新发现时，使用运行时已经暴露的捕获后端（Claude chrome-MCP `mcp__claude-in-chrome__*` 和 computer-use `mcp__computer-use__*`）而不是发明新的捕获流程。从抛光重新发现是罕见的但真实的。

将发现分类到以下类别：

| 类别 | 来源 | 查找内容 |
|------|------|----------|
| verify 失败 | verify --json | 分数低于 3 的命令 |
| SKILL 静态检查失败 | verify-skill --json | 任何 `findings[]` 具有 `severity=error`（flag-names，flag-commands，positional-args，unknown-command，canonical-sections）。硬 ship-gate：ship 存在时不能发射。 |
| 工作流差距 | workflow-verify --json | Verdict `workflow-fail`。软关卡：在 `remaining_issues` 中显示，并在工作流是 CLI 主要价值时降级为 `hold`。 |
| 发布验证失败 | publish validate --json | `passed: false`。**仅独立抛光**（仅在 `STANDALONE_MODE=true` 时运行）；在中间管道抛光中跳过，因为发布先决条件在此时尚未满足。当它运行时，它是硬 ship-gate：ship 在 publish validate 失败时不能发射。如果唯一失败的检查是缺少 phase5 接受，报告 `phase5 acceptance required` 并使用下一步命令：认证，然后运行 `"$PRINTING_PRESS_BIN" dogfood --dir "$CLI_DIR" $SPEC_FLAG --live --level quick --write-acceptance <proofs-dir>/phase5-acceptance.json`。使用验证错误中出现的证明目录。 |
| 安全静态分析失败 | gosec JSON | 任何 `Issues[]` 条目，尤其是 G201/G202 SQL 构造，G101 凭证字面量或危险文件/命令执行。当发现位于手写的 novel-feature Go 中时，硬 ship-gate。 |
| 死代码 | dogfood | 死函数，死标志 |
| 过期文件 | dogfood | 未注册的命令 |
| 描述问题 | dogfood | 样板根 Short |
| README 差距 | scorecard | README 分数 < 8 |
| 示例差距 | dogfood | 缺少示例的命令 |
| Go vet 问题 | go vet | 任何输出 |
| 输出实体警告 | scorecard JSON | `live_check.features[].warnings` — 人类输出中的原始 HTML 实体 |
| 输出可信度 | Phase 4.85 | 来自 agentic 输出审查的发现 |
| MCP 工具质量 | tools-audit | 空的 Short，薄的 Short，缺少只读注释，薄的 MCP 描述 |
| 客户 PII | pii-audit | 高风险文件（manuscripts，fixtures，README）中的卡号后四位，电子邮件，电话，ZIP+4，邮政地址形状 |

**环境失败与 CLI 缺陷。** 一些第一阶段输出显示的失败不是真正的 CLI 错误，也不应阻止发布：

- `scorecard --live-check` 报告 `SQLITE_BUSY`、网络超时、来自模拟或过期令牌的 `401`，或依赖于测试工作区权限/状态的 HTTP 错误——这些问题是测试环境问题，不是 CLI 缺陷。
- `verify` 模拟工具在具有二进制输出的命令（例如，`qr` 返回 PNG 而子字符串匹配器无法验证）或具有可选位置参数的命令（其中干运行输出确实不包含验证探测字符串）上出现错误。
- 学习循环命令：狗粮/verify 矩阵现在覆盖了默认开启的学习表面（`teach`、`recall`、`learnings`、`playbook`）。`teach` 和 `teach-playbook` 在被空调用时故意退出 2，通过 `pp:typed-exit-codes` 声明，因此 `verify` 评分将其作为通过，而 `dogfood --live` 将 `happy_path` 和 `json_fidelity` 检查记录为跳过，原因 `声明非零退出 2`；两者都不是缺陷，也不是“修复”退出代码的理由。跳过的 happy path 不计入 phase5 live 覆盖率，因此仅在其 happy path 上始终退出非零的新功能会报告为空而不是覆盖。`learnings stats` 在新鲜打印时确实报告零和空部分；这是一个空的本地存储，不是缺陷。

在 `skipped_findings` 中将这些分类为环境问题，并注明具体原因；不要在 Phase 2 周期内试图“修复”它们。抛光技能的发布逻辑已经排除了 live-check 失败，但代理仍然应该标注它们，以便审阅者可以看到它们被考虑并故意忽略。

### Phase 4.85 — 代理输出审阅（Wave B）

在上述机械诊断完成后，通过技能工具调用 `printing-press-output-review` 子技能。子技能携带 `context: fork` 并拥有调度提示、门禁逻辑和已知盲点——这是与主 printing-press 技能共享的单一事实来源。

```
Skill(
  skill: "cli-printing-press:printing-press-output-review",
  args: "$CLI_DIR"
)
```

解析返回的 `---OUTPUT-REVIEW-RESULT---` 块。`status: WARN` 查找项流入上述诊断类别，因此 Phase 2 修复将解决基于规则和合理性问题。`status: SKIP` 是信息性的——记录但不要阻塞。

Wave B 门禁适用：所有查找项都是警告，永远不会是阻塞项。如果明显且便宜，则修复；如果推迟，则用简短注释记录。

记录基线分数：scorecard 总分、verify 通过率、狗粮判定、live 矩阵限定符（`exercised` / `not_exercised`）、go vet 问题数量、gosec 查找数量、输出审阅查找数量。

## Phase 2：修复

按优先级顺序修复。每次修复完一个优先级级别后，更新锁心跳：

```bash
"$PRINTING_PRESS_BIN" lock update --cli "$CLI_NAME" --phase polish 2>/dev/null
```

### 运行时变体默认清单

如果抛光修复添加或更改了运行时模式、数据源选项、认证层、传输或其他用户可见默认值，请在选择默认值前记录此简短清单：

- **用户可见默认值**：用户无需额外标志或配置即可获得的行为。
- **兼容性风险**：现有命令、脚本、MCP 工具或存储配置是否改变行为。
- **验证命令**：证明默认值和非默认值逃生通道都有效的确切命令。

将清单保存在抛光笔记或结果块中。对于普通错误修复，如果未更改运行时变体或默认值，则跳过它。

### 跨越 API 调用探测

当抛光构建必须观察每个出站 API 调用的功能类时，例如配额账本、请求日志或审计跟踪，在 `internal/client/client.go` 中探测生成的客户端中间件，而不是单独的命令处理程序。如果存在共享的预调度钩子，则优先使用它；否则覆盖 `do()` 和 `doRead()`。`do()` 路径处理标准端点镜像、同步迭代和新使用生成客户端的功能，而 `doRead()` 处理仅使用 POST 类似传输的只读操作，例如 GraphQL 查询、JSON-RPC 读取和标记 `mcp:read-only` 的基于 POST 的搜索。命令级钩子计数不足，因为它们只看到抛光触碰的命令。

### 新功能数据路由

当抛光添加或修复读取 API 响应数据到本地存储的新命令时，通过生成的类型化模式路由数据，而不是直接将原始响应 JSON 写入表：

1. 读取 `internal/types/<resource>.go` 和 `internal/store/<resource>.go` 以获取正在缓存的资源。如果存在这些文件发出的类型化插入/更新辅助程序，请随时使用它们。如果为生成资源缺少辅助程序，请在编写任何持久化代码之前创建它们。
2. 在决定插入映射正确之前，检查响应形状与规范模式和真实样本响应。
3. 在持久化之前将 API 响应解码为类型化结构。除非表是手编写的迁移中声明的自定义抛光拥有的表，否则不要从未类型化的 `map[string]any` 或原始 `json.RawMessage` 值构建 `INSERT INTO ...` 语句。
4. 从资源类型而不是新命令碰巧开始查询的目标表验证。获取 `<child>` 记录的命令必须插入 `<child>` 行，而不是父行或方便的相邻表。
5. 在插入前规范化嵌套响应标识符。如果 API 将标量 ID 包装在还包含元数据的对象中，请提取标量 ID 字段并存储该值；永远不要将整个 ID 对象作为主键或外键引用存储。

仅自定义抛光拥有的表（在手动编写的迁移中声明）的原始 `database/sql` 写入是可接受的。在这种情况下，在 `internal/store/` 中保持表模式明确，记录为什么生成的资源辅助程序不适用，并在持久化前将嵌套标识符解码为标量。

### 优先级 0：MCP 表面迁移（遗留 CLIs）

如果 Phase 1 的 `dogfood` 报告 `MCP Surface: FAIL` 出现奇偶校验不匹配，CLI 在运行时 cobratree 行走器存在之前生成，并且仍然在静态 `internal/mcp/tools.go` 表面。修复是机械的：

```bash
"$PRINTING_PRESS_BIN" mcp-sync "$CLI_DIR"
```

这将迁移 MCP 表面到运行时行走器，重新生成 `tools-manifest.json` 和 `internal/mcp/tools.go`，并应用任何 `mcp-descriptions.json` 覆盖。如果它退出并报告 `mcp-sync refused` 并需要重新打印，停止此抛光运行并转交给 `/printing-press-reprint`；目标 CLI 生成的客户端对于当前的 MCP 处理器太旧，因此单独重写 `tools.go` 会破坏其构建。在转交时，请说明重新打印流程必须对其重新生成的 CLI 运行正常的 dogfood 门禁，并确认 `MCP Surface: PASS` 才能发布。不要对过时的 `$CLI_DIR` 重新运行 dogfood。成功 `mcp-sync` 后，在此处重新运行 `dogfood`；奇偶校验门禁应切换到 PASS。在兼容的 CLI 已经使用运行时行走器时运行 `mcp-sync` 是无操作刷新。

在 dogfood 的 MCP 门禁已经通过的 CLI 上跳过此优先级。

### 优先级 1：安全静态分析失败

对于 `/tmp/polish-gosec-before.json` 中的每个 gosec 查找项：

1. 读取引用的文件并确认它是否是手编写的。在 `internal/cli/`、`internal/syncer/` 或 `internal/store/` 下，如果前 20 行缺少 `Generated by CLI Printing Press`，则是抛光拥有的新功能代码。
2. 如果查找项在手编写的代码中，请在处理较低优先级抛光项之前在源代码中修复根本原因。示例：用参数化查询替换 SQL 字符串组装，避免使用不受信任的参数调用 shell，并将看起来像凭证的常量移到配置/环境管道。
3. 如果 gosec 标记生成代码，不要手动编辑生成的文件。要么修复上游规范并重新生成，要么添加一个 `skipped_findings` 条目，将其命名为生成器回退候选，并包含规则 ID 和文件路径。
4. 如果 gosec 报告误报，请保持抑制范围狭窄并解释它。仅在代码实际上安全且理由持久时，才优先使用本地 `// #nosec G### -- reason`；否则修复代码。

手编写的新功能 Go 中的未解决的 gosec 查找项是硬阻塞项：它们必须出现在 `remaining_issues` 中，强制 `ship_recommendation: hold`，并在修复可能机械时设置 `further_polish_recommended: yes`。

### 优先级 2：Verify 失败

对于每个失败 verify 干运行或执行的命令：

1. 读取命令文件
2. 查找 `Args: cobra.ExactArgs(N)` 或类似约束
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
5. 删除过时文件（未在 root.go 中注册的升级命令）

### 优先级 4：CLI 描述和元数据

1. 读取 `internal/cli/root.go` 中的 root 命令 `Short`
2. 如果它包含样板（“逆向工程...”、原始 API 标题），重写：
   模式：`"<Product> CLI with <capability-1>, <capability-2>, and <capability-3>"`
3. 检查命令是否有缺失的 `Example` 字段。添加具有特定领域值的真实示例。

### 优先级 5：README

**基本规则：对您放入 README 的每个命令运行 `<cli> <cmd> --help>`。** 永远不要猜测标志名称、参数格式或有效值。如果您写 `--start-time` 但标志是 `--start`，则 README 是错误的，用户在第一次尝试时就会出错。

#### 渲染部分的源文件

在编辑 README.md、SKILL.md 或 `.printing-press.json` 之前，确定该部分是否从源文件渲染。狗粮和再生会覆盖这些渲染部分，因此直接编辑它们是临时的，并且仅用于检查当前输出。

| 渲染部分或字段 | 源文件::字段 | 抛光工作流 |
| --- | --- | --- |
| README `## Unique Features` | `research.json::novel_features_built[]` | 编辑底层的 `research.json` 功能描述/示例，然后使用 `--research-dir` 重新运行狗粮。 |
| SKILL `## Unique Capabilities` | `research.json::novel_features_built[]` | 编辑底层的 `research.json` 功能描述/示例，然后使用 `--research-dir` 重新运行狗粮。 |
| `internal/mcp/tools.go` `command_mirror_capabilities` | `research.json::novel_features_built[]` | 狗粮报告磁盘上的不同块并保留未修改。仅当传递 `--overwrite-command-mirror` 时才替换它从 `research.json`。 |
| README Quick Start | `research.json::narrative.quickstart[]` | 编辑 `research.json` 中的命令/注释，然后重新运行狗粮/渲染步骤。 |
| SKILL Recipes | `research.json::narrative.recipes[]` | 编辑 `research.json` 中的配方标题、命令或解释，然后重新运行狗粮/渲染步骤。 |
| README/SKILL Troubleshooting | `research.json::narrative.troubleshoots[]` | 编辑 `research.json` 中的症状/修复对，然后重新运行狗粮/渲染步骤。 |
| `.printing-press.json` `display_name`, `description`, `mcp_*` | `WriteManifestForGenerate`; 对于描述/显示名覆盖，编辑规范 (`info.title`, `info.x-display-name`, `info.description`) | 编辑规范或重新运行清单写入器。除非您正在进行临时诊断，否则不要手动编辑生成的清单元数据。 |

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

如果 `RESEARCH_JSON` 存在并且渲染部分有不良的措辞、示例或标志引用，请首先在该文件中修复相应字段。对于新功能，狗粮验证 `research.json::novel_features[]`，将剩余集写入 `research.json::novel_features_built[]`，并从该验证集同步 README `## Unique Features`、SKILL `## Unique Capabilities`、`.printing-press.json` `novel_features` 和 root 帮助高亮。`internal/mcp/tools.go` 中不同的 `command_mirror_capabilities` 块被保留未修改，除非传递 `--overwrite-command-mirror`。

#### 必须存在的部分（必须存在且正确）

1. **标题**：`# <Product Name> CLI` — 使用产品真实名称，正确的大小写/标点（例如，"Cal.com" 而不是 "Cal Com"）
2. **副标题**：一句描述 CLI 对用户的作用的句子，匹配 root `Short` 字段。不是 API 描述。
3. **安装**：正确的安装命令。使用 printing-press-library 仓库 URL，而不是不存在于每个 CLI 的特定仓库。
4. **认证**：如何设置 `<API>_API_KEY` 环境变量，在哪里获取密钥（链接到提供者的设置页面），如果支持，自托管 URL 覆盖。读取 `config.go` 以找到所有环境变量。
5. **快速入门**：3-5 个有人会首先运行的命令。选择既**最有用**（您每天会运行的）又**展示 CLI 价值**（为什么安装这个而不是 curl）的命令。通常：
   `doctor` → `sync` → 超越命令（`today`、`health`）→ `search`。避免原始列表命令——它们只是倾倒数据，而没有展示 CLI 存在的原因。
6. **命令**：分类表。按领域功能（调度、分析、账户、工具）分组，而不是按实现结构。
7. **输出格式**：显示 `--json`、`--select`、`--csv`、`--compact`、`--dry-run`、`--agent`。使用真实命令，而不是占位符。
8. **代理使用**：代理原生属性和退出代码。
9. **食谱**：8-15 个使用 `--help` 中**验证标志名称**的食谱。展示 CLI 的独特能力：超越命令、过滤器、SQL 查询、管道。至少包含一个变异示例。
10. **健康检查**：显示实际的 `doctor` 输出，而不是占位符。
11. **配置**：列出 `config.go` 中的所有环境变量并描述。包括配置文件路径。
12. **故障排除**：常见错误映射到退出代码并附带修复。

#### 可选部分（根据需要添加）

- **速率限制**：如果 API 有文档记录的限制
- **自托管**：如果 CLI 支持 `--api-url` 或 `BASE_URL` 覆盖
- **分页**：如果 API 有显著的分页行为
- **来源和灵感**：社区项目的信用（由机器生成，如果存在则保留）

### 优先级 5.5：SKILL 静态检查失败（verify-skill）

读取 `/tmp/polish-verify-skill.json` 获取完整查找列表。每个查找项都有一个 `check`（`flag-names`、`flag-commands`、`positional-args`、`unknown-command` 或 `canonical-sections`）、一个 `command`（SKILL 声称的路径）和一个 `detail` 描述不匹配。常见形状和修复：

- **`flag-names`** — 技能（SKILL）引用了 `<cli> ...` 调用中的 `--foo`，但在 `internal/cli/*.go` 中没有命令声明它。要么示例是错误的（修复技能或删除配方），要么标志已被删除（决定是否应恢复）。**超出范围**：在其他工具调用行上使用的标志（例如 `npx -y @mvanhorn/printing-press install <api> --cli-only`、`gh pr create --base ...`、`go install ...`）。配方范围的 flag-names 检查按设计忽略了这些——永远不要剥离外部工具标志以使 verify-skill 退出 0，也永远不要用虚构的斜杠命令替换安装说明。如果发现是外部工具标志触发的，那是 verify-skill 的错误，不是技能（SKILL）的错误；请报告而不是编辑技能（SKILL）。
- **`flag-commands`** — `--foo 在其他地方声明，但在 <cmd>` 上没有。标志存在于某个地方，但在技能（SKILL）调用了它的命令上不存在。两种修复方法：
  1. 如果标志是通过共享辅助工具（如 `addXxxFlags(cmd, ...)`）添加的，请将 `cmd.Flags().StringVar(...)` 声明直接内联到受影响的命令的源文件中。verify-skill 的 grep 无法跟踪函数调用间接引用。
  2. 如果技能（SKILL）示例确实错误，请修复示例以使用命令声明的标志。
- **`positional-args`** — `got N positional args; Use: "<cmd> <arg>" expects M-M`。技能（SKILL）配方传递了 N 个位置参数，但命令的 `Use:` 声明了 M 个必需的。两种修复方法：
  1. 如果命令也通过 `--flag` 接收值，请将 `Use: "cmd <arg>"` 改为 `Use: "cmd [arg]"`（方括号 = 可选）。verify-skill 正确接受 `--flag`-only 调用针对可选位置参数。
  2. 如果技能（SKILL）示例缺少必需的位置参数，请修复示例。
- **`canonical-sections`** — `install section drift: hand-edit detected in a generator-owned section`。`## Prerequisites: Install the CLI` 块已被编辑，与今天生成器会为该 CLI 发出的内容不同。**不要手动编辑安装部分**。它从 `internal/generator/templates/skill.md.tmpl` 模板化，参数化为 `(api_name, category, uses_browser_http_transport)`；任何漂移都意味着自动化步骤或人员修改了机器拥有的文本。通过重新生成打印的 CLI 解决（运行 `printing-press regen` 对此目录，或对于发布的 CLI，从规范重新生成并重新发布）。如果规范文本本身是错误的（例如，需要安装说明的实际更改），请修复模板，而不是打印的 CLI。

在编辑其他部分的 SKILL.md 时，首先阅读受影响的章节，编辑后再重新阅读。`Edit` 替换字面字符串；如果周围上下文已漂移，单个 `Edit` 可能会在第一个块上嫁接第二个副本，而不是替换它。

修复后，重新运行 `"$PRINTING_PRESS_BIN" verify-skill --dir "$CLI_DIR"` 并在继续之前确认退出 0。

### 优先级 6：剩余的 dogfood 问题

- 路径有效性不匹配
- 认证协议不匹配
- 示例漂移（引用错误命令的示例）
- 数据管道完整性问题

### 优先级 7：MCP 工具质量

**您现在需要确保此 CLI 暴露的每个 MCP 工具都带有代理级描述和正确的读写分类。** 工具描述和分类是代理发现和决定是否调用工具的方式——瘦描述和缺失注释会直接降低代理用户体验，并且 Phase 1 的机械门（verify、dogfood）不会捕获此类问题。

停止并：

1. 运行 `"$PRINTING_PRESS_BIN" tools-audit "$CLI_DIR" --json` 以暴露机械发现（空的 Short、瘦的 Short、读取形状的命令名称上缺少 `mcp:read-only`）。
2. 您必须阅读 `references/tools-polish.md` 并遵循其说明来解决发现问题，并对每个命令进行判断传递——无论审计是否标记了它。审计捕获机械问题；描述质量和边界分类（只读与本地写入）始终需要代理推理。您必须不跳过这一点。
3. **接受 MCP 描述发现附带更严格的合同。** `thin-mcp-description` 和 `empty-mcp-description` 接受要求每个发现填充三个预决策字段（`spec_source_material`、`target_description`、`gap_analysis`）。二进制文件拒绝批量接受（>5 个发现共享一个理由）并运行该“完成”而不提升 MCPDescriptionQuality。通过覆盖或生成器改进修复是预期路径；接受是罕见的。有关完整合同，请参阅 `references/tools-polish.md` “Marking a finding accepted”。

仅当审计的摘要行读取 `no pending findings` 且没有 `incomplete:` 块时，才继续到“所有修复后”。

### 优先级 8：客户-PII 门

**您现在需要清除 PII 账户，以便 promote 和 publish 门通过。** PII 门是防止真实客户值到达发布库内容的确定性底线。它捕获高风险文件中的卡末尾 4 位、电子邮件、美国电话、ZIP+4 和邮政地址形状。

停止并：

1. 运行 `"$PRINTING_PRESS_BIN" pii-audit "$CLI_DIR" "${PII_ARGS[@]}"` 以暴露待处理发现（或从 Phase 1 的基线读取 `/tmp/polish-pii-audit-before.json`）。当 `RESEARCH_DIR` 存在时，这包括该运行的 `research.json` 和 `research/*.md`（`.manuscripts/<run-id>/...` 路径），因此接受会传递到 `publish package`。
2. 您必须阅读 `references/pii-polish.md` 并遵循每个发现的决策树——用不匹配的占位符修复源中的真实值，或使用 `category` + `evidence_context` 预决策字段接受。
3. **接受 PII 发现附带严格的合同。** 缺少字段、6+ 个接受共享一个理由，或未经源修复就批量接受 ≥10 个发现都会失败门。请参阅 `references/pii-polish.md` “The accept contract” 和 “Forbidden accept patterns” 以获取完整规则。

仅当 `pii-audit` 读取 `no pending findings` 且没有 `incomplete:` 块时，才继续到“所有修复后”。

### 所有修复后

```bash
go build -o "$CLI_NAME" ./cmd/"$CLI_NAME"
gofmt -w .
```

## Phase 3：重新诊断

对修复的 CLI 重新运行诊断扫描：

```bash
# RESEARCH_ARGS 必须在此 dogfood 中传递——没有它，
# checkNovelFeatures 不会在 Phase 2 编辑后重新同步 novel_features_built，
# 并且 publish-validate 的 transcendence 门会从 Phase 1 的传递中读取陈旧状态
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

记录后的分数，包括来自最终 `scorecard --live-check --json` 输出的实时矩阵限定符。如果 gosec 命令在写入 `/tmp/polish-gosec-after.json` 之前失败，将缺失的修复后扫描视为修复失败：将其添加到 `remaining_issues`，设置 `ship_recommendation: hold`，并包含 stderr 摘要。如果 verify-skill 仍然有 `severity=error` 发现，workflow-verify 仍然报告 `workflow-fail`（仅当 `STANDALONE_MODE` 为真时——中间管道修复不会运行此检查），gosec 仍然在手写的 novel-feature Go 中报告未解决的发现，pii-audit 仍然有待处理发现或门失败，或者最终实时矩阵限定符是 `not_exercised`，则 ship 不能触发（见 ship 逻辑下方）。对于未执行的实时矩阵，添加类似 `live matrix not exercised (mock-only/no live token); run the live gate before publish` 的 `remaining_issues` 项。

## Ship 逻辑

计算 ship 推荐意见：

- **`ship`**：verify ≥ 80%，scorecard ≥ 75，无关键失败，**并且** verify-skill 退出 0（无技能/CLI 不匹配），**并且** workflow-verify 不是 `workflow-fail`，**并且**（当 `STANDALONE_MODE=true`）publish-validate 报告 `passed: true`，**并且** gosec 在手写的 novel-feature Go 中没有未解决的发现，**并且** tools-audit 显示零待处理发现（每个发现已修复或带有理由明确接受），**并且** pii-audit 显示零待处理发现和零门失败（每个 PII 发现已在源中修复或使用有效预决策字段接受）。技能/工作流/发布/gosec/PII 门是硬性要求：一个带有关于其技能（SKILL）的错误报告（verify-skill 发现）的 CLI 会给代理提供损坏的指令；一个主要工作流失败验证的 CLI 实际上尚未发布；一个被 publish-validate 拒绝的 CLI 无法发布；一个在手写 novel-feature 代码中仍有未解决静态分析安全发现的 CLI 仍然是评审人的诱饵；一个在 promote/publish 门失败时 PII-audit 失败的 CLI 将阻止发货。publish-validate 门仅当修复运行时适用（独立模式）；中间管道修复将发布就绪推迟到主技能（SKILL）的 Phase 6。
- **`ship-with-gaps`**：verify ≥ 65%，scorecard ≥ 65，非关键差距仍然存在，**并且** 上述技能/工作流/gosec/PII 门得到满足，**并且**（当 `STANDALONE_MODE=true`）publish-validate 门得到满足，**并且** README 有一个 `## Known Gaps` 块，列出了用户界面上的差距。保留在重构或外部依赖项阻止干净修复的罕见情况下使用。

  **README Known Gaps 是 ship-with-gaps 的强制性要求。** 发布的库副本是下游用户看到的；如果裁决声称存在差距，但 README 隐藏了它们，下游用户会遇到一个行为不当且未披露的 CLI。在发出 `ship_recommendation: ship-with-gaps` 之前：

  1. 阅读 CLI 的 `README.md`。如果 `## Known Gaps` 部分已经存在（例如，主技能（SKILL）Phase 4 在修复运行之前写了它），请确认它涵盖了 `remaining_issues` 中的用户界面项。为任何新发现的用户界面差距修复添加要点。
  2. 如果 `## Known Gaps` 缺失，请编写它——放置在 `## Quick Start`（或 `## Usage` 之前）以镜像 `## Unique Features` 的放置惯例。`remaining_issues` 中的每个用户界面项一个要点。从用户的角度出发：什么命令行为不当，什么替代方案。示例：

     ```markdown
     ## Known Gaps

     - **`analytics export --csv`** 在具有 >10k 事件的 workspaces 上返回截断的行。使用 `--json` 并将输出重定向到 `jq`，直到底层的导出端点分页。
     ```

  3. 在填充部分时过滤 `remaining_issues` 以获取用户界面条目。内部项（对已弃用标志的 verify 漂移、MCP 描述调整、修复内部注释）不应出现在公共 Known Gaps 中。如果代理无法从 `remaining_issues` 识别任何用户界面差距，裁决是 `ship`，而不是 `ship-with-gaps`。
  4. 在 `fixes_applied` 中列出每个 Known Gaps 写/更新，以便调用者可以表明这发生了。

  如果修复无法负责任地从可用证据中填充 Known Gaps（例如，`remaining_issues` 全是内部术语，没有用户界面可读性），则将裁决降级为 `hold`，而不是在没有披露的情况下发货。
- **`hold`**：verify < 65% 或 scorecard < 65 或关键失败，**或者** verify-skill 有未解决发现，**或者** workflow-verify 报告 `workflow-fail` 且工作流是 CLI 的主要价值，**或者**（当 `STANDALONE_MODE=true`）publish-validate 报告 `passed: false`，**或者** gosec 仍然在手写的 novel-feature Go 中报告未解决的发现，**或者** pii-audit 仍然有待处理发现或门失败，**或者** Phase 3 门捆绑包表示这是先前的 sub-60 重印且缺少 transcendence 行且没有接受的 `partial_transcendence_override`。中间管道修复永远不会因为 publish-validate 达到 `hold`——该检查在此模式下不运行，并且 `publish_validate_*` 作为 `skipped (mid-pipeline)` 发出。

### 不玩游戏地推更高

ship 门是底线，不是上限。通过后，查看 scorecard 维度仍然低于最大值，并询问每个差距是真实的还是结构的：

1. **找到根本缺陷，而不是分数。** Scorecard 是质量的代理，不是目标本身。一个评分 8/10 的 README 可能缺少 Cookbook 部分或过时的命令——这是一个真实且可修复的差距。一个在 200 端点 API 上评分 2/10 的 `mcp_surface_strategy` 可能表示表面主要是端点镜像——也可能可以修复。
2. **如果有真实、代理级改进可用，就去做。** 更好的描述、缺失的标志文档、薄弱的 README 部分、一个不反映实际使用的示例。CLI 会变得更好，分数会随之提高。
3. **如果缺陷是结构的，记录并接受。** 某些维度假设 CLI 的领域没有的功能（只读 API 对写工作流维度评分，没有认证的 CLI 对认证维度评分，小型 API 在 `surface_strategy` 阈值上受到惩罚，这些阈值针对大型 API 校准）。在 `skipped_findings` 中记录原因并继续。
4. **永远不要添加脚手架来满足评分者。** 假命令、假测试、假标志或纯粹为推动数字而编写的样板文本——这些会降低 CLI 的质量以满足代理。评分器设计不完美（AGENTS.md 中的“评分可能不完美”免责声明适用）。相信基本判断，而不是数字。

#### MCP scorecard 维度映射到规范字段，而不是生成器代码

当 `mcp_token_efficiency`、`mcp_tool_design`、`mcp_remote_transport` 或 `mcp_surface_strategy` 低于最大值时，修复几乎总是规范编辑 + 重新生成（或从新鲜生成的树 `regen-merge`），**不是** 生成器模板更改。修复可以解决这些问题——不要将它们归类为“生成器拥有的文件的功能添加，逆向候选”。Cobratree shell-out 工具已经从 Short（不是操作员 Long 帮助）中目录化，因此剩余的 `mcp_token_efficiency` 压力是类型端点描述，而不是框架 `--help`。

| 弱维度 | 修复它的规范字段 | 要添加到 `spec.yaml` 的 `mcp:` 块中的内容 |
|---|---|---|
| `mcp_remote_transport` | `mcp.transport` | `transport: [stdio, http]`（小型 API 在或低于 `spec.DefaultRemoteTransportEndpointThreshold` 的类型端点默认获得此；覆盖仅在规范选择了一个较窄的列表或 API 高于阈值但仍然需要远程访问时需要） |
| `mcp_token_efficiency`、`mcp_surface_strategy` | `mcp.endpoint_tools`、`mcp.orchestration` | `endpoint_tools: hidden` + `orchestration: code`（Cloudflare 模式：~70 原始端点工具折叠为 `<api>_search` + `<api>_execute`；所有端点仍然可以通过 execute 访问） |
| `mcp_tool_design` | `mcp.intents` | 为 API 支持的工作流定义多步骤意图组合 |
| `mcp_description_quality` | `mcp-descriptions.json`（CLI 根目录处的覆盖文件） | 每个工具描述覆盖；瘦规范派生描述无需规范编辑即可获得更丰富的文本 |

推荐阈值：当手动输入的端点数超过50个时，默认推荐全部四个（`transport`、`endpoint_tools=hidden`、`orchestration=code`、`intents`用于标题工作流）。小型API（<= `spec.DefaultRemoteTransportEndpointThreshold`）默认已获得http传输，因此`mcp_remote_transport`在无需修改规范的情况下即可达到10/10——只有当规范明确缩小了列表时才需要指出。完整参考是`docs/SPEC-EXTENSIONS.md`。

编辑规范后，重新生成（或将更改合并到已发布的库中），以便新的`mcp:`块能够到达模板。CobraTree遍历的新命令无论如何都会作为MCP工具出现；它们不需要规范更改。

经验法则：如果你的修复即使没有计分卡仍然有价值，那就去做。如果唯一的动机是“推动计分”，那就不要。

## 显示差异并发出结果块

向用户显示差异，然后发出结构化的`---POLISH-RESULT---`块。该块允许调用技能（例如，主要印刷机Phase 5.5）可靠地解析推荐和分数；上面的人类可读表格是给用户的。

```
<CLI_NAME>的精炼结果：

                    之前    之后    差异
  计分卡：        XX/100    XX/100    +N
  验证：           XX%       XX%       +N%
  活矩阵：      练习/未练习 -> 练习/未练习
  工具审计：      XX        XX        -N待处理的发现

已应用的修复：
  - 每个修复的简短描述

跳过的发现：
  - <发现>：你选择不修复的原因

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
tools_audit_before: <N pending>
tools_audit_after: <N pending>
publish_validate_before: <PASS|FAIL|跳过（中管道）>
publish_validate_after: <PASS|FAIL|跳过（中管道）>
fixes_applied:
- <每个修复的简短描述>
skipped_findings:
- <发现>：你选择不修复的原因
remaining_issues:
- <每个你试图修复但无法解决的问题的简短描述>
ship_recommendation: <发布|发布带缺口|暂停>
further_polish_recommended: <是|否>
further_polish_reasoning: <解释调用的一句话>
---END-POLISH-RESULT---
```

这三个列表有不同的用途：
- **fixes_applied**：发生了什么变化——调用者显示这些
- **skipped_findings**：你发现的问题但故意不修复，并附有理由（例如，“验证将`stale`分类为读取——计分器错误，不是CLI问题”，“`version`接受为薄短——准确且简短）。调用者显示这些，以便用户可以决定是否手动处理。
- **remaining_issues**：你试图修复但无法解决的问题。

**`publish_validate_*`值。** 当精炼运行了publish-validate（独立模式）时发出`PASS`或`FAIL`。当精炼跳过了它（中管道调用，`STANDALONE_MODE=false`）时发出字面字符串`跳过（中管道）`。跳过值仅用于信息：调用者在决定是否将精炼的`ship_recommendation`级联到CLI级别的暂停时，不应将其视为失败。

**`dogfood_live_matrix_*`值。** 仅当live-check评估了至少一个真实样本时才发出`练习`。对于模拟-only/无令牌/无研究/未评估样本的运行发出`未练习`。当`dogfood_after: PASS`但`dogfood_live_matrix_after: 未练习`时，人类摘要必须说`dogfood PASS（模拟仅用；活矩阵未练习——在发布前运行活门）`，并且`ship_recommendation`必须为`暂停`，除非父调用者明确拥有后续的活门。

**`gosec_*`值。** 发出生成文件筛选后仍然与打印的CLI相关的gosec发现的计分卡数。这些值有意不是来自`/tmp/polish-gosec-*.json`的原始`Issues[]`长度：不要计算被路由到`skipped_findings`作为逆向候选的生成器发出的发现，但要计算迫使`暂停`的手动编写的未解决发现。

### 选择`further_polish_recommended`

由你的判断，而不是`remaining_issues`的数量决定。当另一个精炼调用有实际机会解决剩余问题时，设置`是`：

- `remaining_issues`包括你因时间不足而未能运行的验证或dogfood失败，而一个有更多关注每个失败的全新通过可能有可能解决。
- 你已经落地的修复可能解除了你这次无法触及的依赖问题。
- SKILL/CLI不匹配需要在这次通过更改源树后进行第二次检查。

设置`否`当另一个调用会重新走过同样的地面：

- `remaining_issues`是用户才能做出的决定（重命名旗舰命令，选择默认行为，接受结构权衡）。
- 你已经尝试了两种不同的修复方式，并且都以相同的原因失败。
- 阻塞因素是外部的（API改变了形状，速率限制，缺少凭证），而一个全新的精炼运行看不到不同的地方。
- `remaining_issues`为空并且`skipped_findings`都是环境或结构性的——精炼没有剩下的事情可做。

`further_polish_reasoning`是一句调用者逐字显示的句子。使其具体（“`analytics export`和`report show`的验证失败看起来可以解决，但我太早放弃了”）而不是通用（“更多的精炼可能会有帮助”）。调用者使用这个信号来决定是否在他们的下一个提示中提供“再次精炼”；一个模糊的理由会使他们的提示模糊。

## 发布提议

**除非`STANDALONE_MODE`为真，否则跳过整个这一节。** `STANDALONE_MODE`在上述“解决CLI”块中根据调用者模式设置：对于斜杠命令调用（`/printing-press-polish ...`）或传递`--standalone`到`args`的技能工具调用为真；否则为假。当为假时，精炼是从主要SKILL Phase 5.5或暂停路径“精炼以重试”中调用的，工作CLI尚未提升到库。`/printing-press-publish <slug>`将解析到`$PRESS_LIBRARY/<slug>/`，这要么是空的，要么包含陈旧的先前的运行——在这里调用发布要么无法解析，要么会发布错误的副本。父技能在该路径上拥有发布流程；只需发出结果块并返回。

应用发布回合边界规则：`AskUserQuestion`的答案可能仅授权传递消息，而不是同回合发布。发布会打开或更新公共库PR，因此它需要在精炼完成后需要一个新的用户编写的消息。有关理由，请参阅`references/publish-turn-boundary.md`。

一个简单的检查：

```bash
if [ "$STANDALONE_MODE" != "true" ]; then
  echo "非独立调用者；跳过发布提议"
  return
fi
```

门是调用者模式标志，**不是**解析的路径。没有`--standalone`的技能工具调用即使路径位于`$PRESS_LIBRARY/<slug>/`下也会延迟发布；这是更安全的默认值，并且是唯一能够捕获倒置的Phase 5.5/5.6失败模式（中管道运行触发公共分支+PR）在精炼边界的方式。之前的路径子字符串启发式（`*.runstate/*`）在这里不再承担负载——它已经在上述研究目录解析块中保留，因为那个块是在选择两个真实的磁盘布局，这与其他发布门控的担忧不同。

对于独立调用，继续执行下面的提议。

如果`ship`或`ship-with-gaps`：

从结果块构建提示。形状是数据驱动的，因此用户永远不会被要求权衡“再次精炼”与“发布”，当精炼本身决定另一个通过不会有所帮助时。

### 建议

从精炼结果中选择建议的行动：

- `ship` + `remaining_issues`为空 → 建议发布。
- `ship` + `remaining_issues`非空 + `further_polish_recommended: 是` → 建议再次精炼。
- `ship` + `remaining_issues`非空 + `further_polish_recommended: 否` → 如果剩余问题不触及CLI的标题命令，则建议发布；否则显示权衡，并让用户在发布（如原样；README不会自动更新`ship`裁决）和完成之间决定。
- `ship-with-gaps` + `further_polish_recommended: 是` → 建议再次精炼。
- `ship-with-gaps` + `further_polish_recommended: 否` → 建议发布（缺口已经在README的`## 已知缺口`中，因为精炼的ship逻辑强制为`ship-with-gaps`——见上面的“ship逻辑”）或如果缺口是发布阻塞的——代理判断。

### 菜单

当`further_polish_recommended: 否`时完全抑制“再次精炼”选项。始终保留“发布”和“完成”。

当精炼选择不推荐另一个通过时，显示`further_polish_reasoning`作为上下文——用户应该看到为什么精炼完成了。

通过`AskUserQuestion`呈现。两个示例形状：

**精炼收敛干净**（`remaining_issues`为空，`further_polish_recommended: 否`）：

> "<CLI_NAME>精炼：计分卡XX/100，验证XX%。精炼运行干净——没有更多需要修复。
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
> 建议：发布前再次精炼。
>
> 1. **再次精炼**（推荐）——解决剩余的<N>个问题
> 2. **单独发布**——显示下一个用户消息的发布命令以如原样发布
> 3. **暂时完成**——CLI位于$PRESS_LIBRARY/<cli-name>"

推荐的选项领先，带有`(推荐)`标签，并且领先的`Recommendation:`行明确声明了代理的调用。三个加强渠道，以便用户不必从顺序中推断。

### 如果“单独发布”

不要从这个相同的回合中调用`/printing-press-publish <cli-name>`，并且在这里不要检查或创建公共库PR。打印一个需要明确的新用户编写的消息的传递：

> "发布需要单独的用户确认，因为它可以分支`mvanhorn/printing-press-library`，推送一个分支，并打开或更新PR。
>
> 要发布，将以下内容作为您的下一个消息发送：
>
> `/printing-press-publish <cli-name> --from-polish`"

打印传递后停止。如果用户在稍后的消息中发送命令，发布技能将拥有验证、打包、公共库PR创建或更新，以及发布后的`--from-polish`逆向提议。

（当`STANDALONE_MODE`为假时，这一整节是不可达的——本节顶部的发布提议守卫会提前返回——因此在这里不需要额外的检查。）

### 如果“再次精炼”

使用相同的CLI重新运行Phase 1 → Phase 2 → Phase 3。最多2次额外的精炼通过（包括第一次总共3次）。

### 如果“暂时完成”

正常结束。

## 规则

- 修复所有问题。在修复前不要请求批准——精炼是自主的。
- 如实报告结果。显示哪些有所改善，哪些没有。
- 不要添加新功能。精炼修复质量问题，而不是功能差距。
- 不要重新运行研究或生成。精炼在CLI如原样工作时工作。
- 不要修改印刷机生成器。那是`/printing-press-retro`。
- 不要修改任何位于`$CLI_DIR`外的文件。
- 如果精炼添加或重命名了Cobra命令，MCP表面通过生成的`internal/mcp/cobratree`运行时镜像自动更新。仅在README/SKILL突出显示或注册表显示应更改时更新`novel_features`；使用`cmd.Annotations["mcp:hidden"] = "true"`用于调试仅用的命令。
- 每次精炼调用最多1次修复和重新诊断通过。`Polish again`路径运行额外的调用（总共最多3次）。
- 优先考虑机械修复而不是创造性决策。当需要创造性决策时（例如CLI描述），如果可用，使用手稿的研究简报。
