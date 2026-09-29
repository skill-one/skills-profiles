---
name: printing-press-publish
description: 将生成的 CLI 发布到 printing-press-library 仓库
---

# /printing-press publish

将本地生成的 CLI 发布到 [printing-press-library](https://github.com/mvanhorn/printing-press-library) 仓库作为拉取请求。

```bash
/printing-press publish notion-pp-cli
/printing-press publish notion
/printing-press publish notion --from-polish
/printing-press publish notion --skip-live-test=auth-unavailable
/printing-press publish notion --blocked-api-journal notion
/printing-press publish
```

## PR 形状保护

此功能仅打开生成的 CLI 发布拉取请求，或使用 `--blocked-api-journal` 打开 `blocked-apis.json` 日志拉取请求。它永远不会以未准备发布的 CLI 替代形式打开文档、计划、提案或规范拉取请求。如果生成、验证或实时测试被阻止，请报告确切的阻止原因并停止。

## 直接用户调用要求

发布可以分叉 `mvanhorn/printing-press-library`，推送分支并打开或更新拉取请求。在设置或验证之前，检查调用上下文。如果此功能是从 `printing-press-polish` 的发布提议链式调用中触发的，包括 `AskUserQuestion` 答案或自动解析的优化建议，请立即停止并告诉用户在新鲜消息中发送 `/printing-press-publish <cli-name> --from-polish`。一个明确要求发布的全新用户发起请求就足够了；不要在直接发布请求之上添加另一个确认提示。

如果新鲜用户发起的请求包含 `--from-polish`，请为终端状态步骤记录 `POLISH_HANDOFF=true`，并在解析 CLI 名称时忽略该标记。该标记不是第二次确认，也不会传递给 `cli-printing-press`；它仅保留独立优化发布后的旧发布后回退提议，在新鲜轮发布完成后。

如果请求包含 `--blocked-api-journal`，则进入下方的 **阻止 API 日志模式**，而不是正常的打印 CLI 发布流程。此模式可以在用户明确选择“添加到阻止 API 日志”后从 `/printing-press` 的挂起路径菜单中调用；该父菜单选择足以授权对公共库日志的写入。不要要求对此日志模式进行第二次新鲜轮调用。

如果新鲜用户发起的请求包含 `--skip-live-test=<reason>`，请记录确切的非空原因作为 `SKIP_LIVE_TEST_REASON`，并在解析 CLI 名称前移除该标志。这是发布时实时测试门禁的唯一支持的逃生通道。仅用于 auth-unavailable、已知的上游中断、LAN 不可达的硬件 API 或类似具体的操作员批准的情况；永远不要从普通的延迟或存在较旧的 Phase 5 标记中推断跳过。

公共库将 `library/<category>/<api-slug>/.printing-press.json` 和 `manifest.json` 视为注册显示字段的来源。不要在发布拉取请求中编辑 `registry.json`、README 目录单元格或 `cli-skills/pp-<api-slug>/SKILL.md`；这三个都会在合并后由库自己的工作流程自动重新生成。库在 `verify-library-conventions.yml` 中的 `Fail on changes to generated artifacts` 检查会阻止任何与基础差异触及 `registry.json` 或 `cli-skills/pp-*/SKILL.md` 的分叉或同一仓库的 PR，因此包含其中任一内容的发布会被在审查前预先拒绝。

公共库还拥有每个 CLI 的发布会计。不要手动更新发布 PR 中的 `CHANGELOG.md`、`.printing-press-release.json` 或运行时 `var version = ...`。新鲜打印的 CLI 可能包含空的发布账本骨架；库的合并后工作流程会分配最终的 `YYYY.M.N` 发布并标记运行时版本。当替换现有的公共库 CLI 时，请保留其现有的发布账本文件，以便在重新打印 PR 中不会丢失更改日志历史。

`blocked-apis.json` 不同：它是一个手动的公共库日志，而不是生成的注册表面。仅日志的 PR 可以编辑 `blocked-apis.json`，并且必须不暂存 `library/`、`registry.json`、README 目录单元格或 `cli-skills/`。

## 阻止 API 日志模式

仅在调用包含 `--blocked-api-journal` 时使用此模式。它记录了一个挂起的 `/printing-press` 尝试，其阻止原因可能会重复出现，直到机器或上游问题发生变化。

调用者必须提供的字段：

- `slug`：规范 API slug，不是 CLI 二进制名称。
- `attempted_at`：`YYYY-MM-DD`。
- `verdict`：`hold`。
- `reason`：简洁的阻止原因，不包含秘密、本地路径、cookie、令牌或特定账户详细信息。
- `blocking_issue`：如果知道，则为 Printing Press 问题编号，否则为 `null`。
- `permanent`：布尔值。

如果调用者没有提供其中这些字段之一，请仅从当前运行上下文中推断安全值。如果 `reason` 缺失或模糊，请停止并要求一个具体的阻止句子；不要写一个无用的日志条目。

运行正常的设置、配置、作用域克隆清理和 GitHub 认证检查，然后像正常发布流程一样准备公共库克隆：如果需要，则分叉，确保 `upstream` 指向 `mvanhorn/printing-press-library`，获取 `upstream`，并将克隆重置为 `upstream/main`，然后再进行编辑。

然后仅更新 `$PUBLISH_REPO_DIR/blocked-apis.json`：

```bash
cd "$PUBLISH_REPO_DIR"
if [ ! -f blocked-apis.json ]; then
  printf '[]\n' > blocked-apis.json
fi
jq --arg slug "<api-slug>" \
   --arg attempted_at "<YYYY-MM-DD>" \
   --arg verdict "hold" \
   --arg reason "<reason>" \
   --argjson blocking_issue '<number-or-null>' \
   --argjson permanent '<true-or-false>' '
  (if type == "array" then . else [] end)
  | map(select(.slug != $slug))
  + [{
      slug: $slug,
      attempted_at: $attempted_at,
      verdict: $verdict,
      reason: $reason,
      blocking_issue: $blocking_issue,
      permanent: $permanent
    }]
  | sort_by(.slug)
' blocked-apis.json > blocked-apis.json.tmp || {
  rm -f blocked-apis.json.tmp
  echo "Error: jq failed to update blocked-apis.json"
  exit 1
}
if ! jq empty blocked-apis.json.tmp; then
  rm -f blocked-apis.json.tmp
  echo "Error: blocked-apis.json update produced invalid JSON"
  exit 1
fi
mv blocked-apis.json.tmp blocked-apis.json
```

创建一个日志分支并提交 PR：

```bash
git checkout -B chore/blocked-api-<api-slug>
git add blocked-apis.json
git commit -m "chore(<api-slug>): journal blocked API"
git push --force-with-lease -u origin chore/blocked-api-<api-slug>
```

创建一个针对 `mvanhorn/printing-press-library` 的 PR，其正文包含：

- 挂起的 API slug 和原因
- 阻止是否永久或与 `blocking_issue` 关联
- 预期的 Phase 0 行为：未来的 `/printing-press <api-slug>` 运行在重复尝试前发出警告

PR 打开后，报告 URL 并停止。不要继续进入正常的打印 CLI 打包、实时测试、注册或技能镜像步骤。

## 设置

在执行任何其他操作之前：

<!-- PRESS_SETUP_CONTRACT_START -->
```bash
# min-binary-version: 4.0.0

# 首先推导作用域 — 需要用于本地构建检测
_scope_dir="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
_scope_dir="$(cd "$_scope_dir" && pwd -P)"

# 从 printing-press 仓库内部运行时优先本地构建。
_press_repo=false
if [ -x "$_scope_dir/cli-printing-press" ] && [ -d "$_scope_dir/cmd/cli-printing-press" ]; then
  _press_repo=true
  export PATH="$_scope_dir:$PATH"
  echo "使用本地构建: $_scope_dir/cli-printing-press"
elif ! command -v cli-printing-press >/dev/null 2>&1; then
  if [ -x "$HOME/go/bin/cli-printing-press" ]; then
    echo "cli-printing-press 在 ~/go/bin/cli-printing-press 中找到，但不在 PATH 上。"
    echo "将 GOPATH/bin 添加到您的 PATH:  export PATH=\"\$HOME/go/bin:\$PATH\""
  else
    echo "未找到 cli-printing-press 二进制文件。"
    echo "使用以下命令安装:  go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest"
  fi
  return 1 2>/dev/null || exit 1
fi

# 解析并输出代理必须用于每个后续 `cli-printing-press` 调用的绝对路径。`export PATH` 上的内容仅影响此 Bash 工具调用；后续调用会打开一个新的 shell 并针对用户默认 PATH 解析 `cli-printing-press`，其中可能存在陈旧的全球变量而遮蔽本地构建。代理会捕获此标记并将绝对路径替换到后续每个调用中。
if [ "$_press_repo" = "true" ]; then
  PRINTING_PRESS_BIN="$_scope_dir/cli-printing-press"
else
  PRINTING_PRESS_BIN="$(command -v cli-printing-press 2>/dev/null || true)"
fi
if ! command -v go >/dev/null 2>&1; then
  echo ""
  echo "[setup-error] Go 工具链未找到。"
  echo ""
  echo "此 Printing Press 流程运行基于 Go 的构建或验证命令。"
  echo "从 https://go.dev/dl/ 安装 Go 1.26.6 或更高版本，然后使用以下命令验证:"
  echo "  go version"
  echo "然后重新运行此功能。"
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
    echo "[setup-error] 此 cli-printing-press 二进制需要 Go $_pp_go_required 或更高版本 (已安装: $_pp_go_installed)。"
    echo "GOTOOLCHAIN=local 禁用自动工具链下载，因此后续的 Go 质量门禁会失败。"
    echo "从 https://go.dev/dl/ 安装 Go $_pp_go_required 或更高版本，或取消设置 GOTOOLCHAIN。"
    echo ""
    return 1
  fi

  echo "[go-toolchain-old] 此 cli-printing-press 二进制需要 Go $_pp_go_required 或更高版本 (已安装: $_pp_go_installed)。"
  echo "默认 GOTOOLCHAIN 行为可能会在 Go 命令期间下载所需的工具链。"
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
    echo "[setup-error] Printing Press 工作区卷上的磁盘空间严重不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_FAIL_KB=$_pp_disk_fail_kb"
    echo "释放磁盘空间或将 PRINTING_PRESS_HOME 设置为具有更多空间的卷，然后重新运行此功能。"
    echo ""
    return 1
  fi

  if [ "$_pp_disk_avail_kb" -lt "$_pp_disk_warn_kb" ]; then
    echo ""
    echo "[low-disk] Printing Press 工作区卷上的可用磁盘空间不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_WARN_KB=$_pp_disk_warn_kb"
    echo "此流程可能需要几 GiB 用于生成的文件、Go 构建缓存、模块下载或仓库克隆。"
    echo ""
  fi
}
_pp_check_disk_space || { return 1 2>/dev/null || exit 1; }

mkdir -p "$PRESS_RUNSTATE" "$PRESS_LIBRARY" "$PRESS_MANUSCRIPTS" "$PRESS_CURRENT"
```
<!-- PRESS_SETUP_CONTRACT_END -->

运行设置合约后，从标准输出中捕获 `PRINTING_PRESS_BIN=<abs-path>` 行。**在此技能中的每个后续 `cli-printing-press ...` 调用都必须使用该绝对路径**（替换值，而不是 `$PRINTING_PRESS_BIN` 字面量标记）—— `export PATH` 上的内容仅影响它运行的单一 Bash 工具调用，因此后续调用会打开一个新的 shell，其中 `cli-printing-press` 会针对用户的默认 `PATH` 解析，而陈旧的全球变量可能会遮蔽本地构建。

如果设置输出了 `[go-toolchain-old]` 或 `[low-disk]`，请向用户显示建议，除非设置也输出了 `[setup-error]`。`[go-toolchain-old]` 意味着后续的 Go 命令可能会下载所需的工具链或在下载被阻止时失败；`[low-disk]` 意味着此运行可能需要几 GiB 用于生成的文件、Go 构建缓存、模块下载或仓库克隆。

捕获二进制路径后，检查二进制版本兼容性。从此技能的 YAML 前置读取 `min-binary-version` 字段。运行 `<PRINTING_PRESS_BIN> version --json` 并从输出中解析版本。使用 semver 规则将其与 `min-binary-version` 进行比较。如果安装的二进制文件比最小版本旧，请立即停止并告诉用户：“cli-printing-press 二进制文件 vX.Y.Z 比最小要求的 vA.B.C 旧。运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 更新。”

```bash
find "$PRESS_HOME" -maxdepth 1 -name '.publish-config-*.json' -type f | while read -r cfg; do
  [ "$cfg" = "$PUBLISH_CONFIG" ] && continue
  managed_by=$(jq -r '.managed_by // empty' "$cfg" 2>/dev/null || true)
  scope_dir=$(jq -r '.scope_dir // empty' "$cfg" 2>/dev/null || true)
  clone_path=$(jq -r '.clone_path // empty' "$cfg" 2>/dev/null || true)
  [ "$managed_by" = "printing-press-publish" ] || continue
  [ -z "$scope_dir" ] && continue
  [ -e "$scope_dir" ] && continue
  [ -d "$clone_path/.git" ] || continue
  case "$clone_path" in "$PRESS_HOME"/.publish-repo-*) ;; *) continue ;; esac
  origin=$(git -C "$clone_path" remote get-url origin 2>/dev/null || true)
  case "$origin" in *mvanhorn/printing-press-library*|*/*/printing-press-library*) ;; *) continue ;; esac
  [ -z "$(git -C "$clone_path" status --porcelain)" ] || continue
  [ "$(git -C "$clone_path" rev-parse --abbrev-ref HEAD 2>/dev/null || true)" = "main" ] || continue
  rm -rf "$clone_path" "$cfg"
done
```

## 第 1 步：前提条件

验证 `gh` 是否已认证：

```bash
gh auth status
```

如果此步骤失败，停止并告知用户：“GitHub CLI 未认证。请先运行 `gh auth login`。”

## 第 2 步：解析 API Slug

运行：

```bash
cli-printing-press library list --json
```

将 JSON 输出解析为 CLI 列表。该库现在以 API slug（目录名）为键，而非 CLI 名称。

**名称解析顺序**（为保持一致性，匹配 score skill 的逻辑）：

1. **精确匹配：** 如果参数与目录名（API slug）完全匹配，则使用它
2. **CLI 名称匹配：** 如果没有精确匹配，尝试与 `cli_name` 字段匹配，然后从清单的 `api_name` 字段推导 API slug
3. **后缀匹配：** 如果仍未匹配，尝试用 `<argument>-pp-cli` 去匹配 `cli_name` 字段
4. **通配符匹配：** 如果仍无匹配，搜索 `cli_name` 或 `api_name` 包含该参数作为子串的条目。限制为最近的 5 个匹配。如果存在多个匹配，通过 AskUserQuestion 呈现它们并让用户选择
5. **无匹配：** 列出所有可用的 CLI，并要求用户选择或重新输入
6. **无参数：** 如果调用时未提供名称，按修改时间排序列出所有 CLI，让用户选择

解析完成后，读取清单的 `api_name` 字段以获取 API slug。在所有下游操作（分支名、注册表条目、冲突检测、路径构造）中使用此 slug。清单中的 `cli_name` 仅用于二进制级别的操作。

呈现匹配结果时，以用户友好的格式显示 API slug 和修改时间（例如，“2 小时前”，“3 天前”）。

## 第 3 步：确定分类

从已解析的 CLI 目录读取 `.printing-press.json`。

**分类解析顺序：**

1. 如果清单中有 `category` 字段，将其呈现给用户确认：
   > “正在作为 **<category>** 发布。确定吗？”
   提供修改选项

2. 如果清单未提供分类，通过 AskUserQuestion 呈现完整列表：
   - developer-tools, monitoring, cloud, project-management
   - productivity, social-and-messaging, sales-and-crm, marketing
   - payments, auth, commerce, ai, food-and-dining, health, maps, media-and-entertainment, devices, other
   - travel

## 第 3.5 步：Greptile 审查契约 — 在打开 PR 之前阅读

进入公共库的每个 PR 都会获得自动化的 Greptile 审查以及 `Greptile policy gate` CI 任务。标准契约位于库的 [`AGENTS.md → "Automated code review with Greptile"`](https://github.com/mvanhorn/printing-press-library/blob/main/AGENTS.md#automated-code-review-with-greptile)；要点如下：

- **标准是在合并前解决所有 Greptile 发现项——0-5 的分数是置信度信号，而非门禁。** 解决了所有问题项的 4/5 分表示就绪；存在未解决的 P1 项的 5/5 分则未就绪。将所有 P0 和 P1 视为阻塞项；P2 项需要修复或具体的延期回复。
- **审查是增量的**：每次推送都会重新触发一次新的审查，可能会暴露新的发现项。将 PR 推进到*稳定*的绿色状态——绝不在第一轮后宣布完成。
- **阅读最新的 `greptile-apps` 顶层摘要，而不仅仅是内联线程。** 即使线程列表为空，摘要也可能包含可操作的 `Comments Outside Diff` 块。在宣布就绪之前运行仓库的审查状态辅助脚本：
  ```bash
  python3 .github/scripts/pr-review-state/greptile_feedback.py <PR_NUMBER>
  ```
- **超时恢复**：如果策略门禁因 `Timed out waiting for Greptile Review to complete` 而失败（常见触发因素是大型新 CLI 差异），门禁会在约 3 分钟后自动发布 `@greptileai review`；如果仍未恢复，请自行发布 `@greptileai review` 并等待。
- **分数门禁**：策略门禁要求当前 head SHA 上的最新 Greptile 评论包含 `Confidence Score: ≥ 4/5`。新推送会重新运行它——确保在最终 head 上分数仍满足阈值。

## 第 4 步：验证

运行：

```bash
cli-printing-press publish validate --dir <cli-dir> --json
```

此步骤中的 `govulncheck` 特意限定为仅针对 `<cli-dir>`。它使用默认的 `govulncheck ./...` 模式，因此可到达的符号发现项会阻塞发布，而仅是必需的易受攻击模块但没有调用路径的则不会成为发布阻塞项。不要将此替换为完整的公共库扫描或 `govulncheck -show verbose`。

解析 JSON 结果。向用户显示每个检查项的结果：

```
Validating <api-slug>...
  manifest        PASS
  phase5          PASS
  go mod tidy     PASS
  govulncheck     PASS
  go vet          PASS
  go build        PASS
  --help          PASS
  --version       PASS
  manuscripts     WARN (no manuscripts found)
```

如果 `"passed": false`，报告失败的检查项并**停止**。不要创建部分 PR。
`manifest` 检查项对于公共库的来源契约具有权威性：当前的 `schema_version`、`run_id`、`printing_press_version`、`printer`、`printer_name`，以及在宣传 MCP 时的 MCP 元数据文件。如果它失败，告知用户在打开库 PR 之前，使用当前的 Printing Press 元数据重新打印或重新打包。

保存结果中的 `help_output` 字段——它将用于 PR 描述中。

## 第 4.5 步：实时端到端门禁

在触及托管发布克隆之前，针对即将发布的 CLI 重新运行实时行为门禁。第 4 步证明源码可以构建并在结构上通过验证；此步骤证明当前的编辑后树状结构仍然对真实的上游 API 正常工作。不要依赖生成或打磨阶段遗留的旧 `phase5-acceptance.json`，因为自该标记写入后 CLI 可能已被手动编辑。

**标记失效与同步。** 验收标记携带源指纹；在其写入后对任何 `.go` 文件的编辑都会导致 `publish package` 以 “phase5 marker source fingerprint does not match” 失败。在每次源码变更后重新运行此实时门禁，并将标记写入**两个**副本：嵌入式的 `$CLI_DIR/.manuscripts/<run>/proofs/` 和归档的 `$PRESS_MANUSCRIPTS/<api>/<run>/proofs/`（手稿查找优先归档；证明查找优先嵌入式——任一位置的过期副本都会阻塞打包）。

从 CLI 清单解析 Phase 5 证明目录：

```bash
MANIFEST="$CLI_DIR/.printing-press.json"
API_SLUG=$(jq -r '.api_name // empty' "$MANIFEST")
CLI_NAME=$(jq -r '.cli_name // empty' "$MANIFEST")
RUN_ID=$(jq -r '.run_id // empty' "$MANIFEST")
AUTH_TYPE=$(jq -r '.auth_type // "none"' "$MANIFEST")
AUTH_ENV=$(jq -r '.auth_env_vars[0] // empty' "$MANIFEST")

if [ -z "$API_SLUG" ] || [ -z "$RUN_ID" ]; then
  echo "ERROR: manifest is missing api_name or run_id; cannot run publish live gate."
  exit 1
fi

PROOFS_DIR="$CLI_DIR/.manuscripts/$RUN_ID/proofs"
if [ ! -d "$PROOFS_DIR" ] && [ -n "$API_SLUG" ] && [ -d "$PRESS_MANUSCRIPTS/$API_SLUG/$RUN_ID/proofs" ]; then
  PROOFS_DIR="$PRESS_MANUSCRIPTS/$API_SLUG/$RUN_ID/proofs"
elif [ ! -d "$PROOFS_DIR" ] && [ -n "$CLI_NAME" ] && [ -d "$PRESS_MANUSCRIPTS/$CLI_NAME/$RUN_ID/proofs" ]; then
  PROOFS_DIR="$PRESS_MANUSCRIPTS/$CLI_NAME/$RUN_ID/proofs"
fi
mkdir -p "$PROOFS_DIR"

RESEARCH_DIR="$(dirname "$PROOFS_DIR")/research"
if [ ! -f "$RESEARCH_DIR/research.json" ] && [ -f "$(dirname "$PROOFS_DIR")/research.json" ]; then
  RESEARCH_DIR="$(dirname "$PROOFS_DIR")"
fi
if [ ! -f "$RESEARCH_DIR/research.json" ]; then
  echo "ERROR: publish live gate requires the run research.json at $RESEARCH_DIR." >&2
  exit 1
fi
```

Phase 5 标记绑定到被执行的源树。实时 dogfood 写入器自动记录 `source_fingerprint` 和逐文件哈希。发布验证会从当前 CLI 目录重新计算指纹，并拒绝来自漂移树的标记，当标记包含它们时会指明变更的源文件。仅涉及 README 的编辑在此指纹之外，不会使门禁失效。

如果未设置 `SKIP_LIVE_TEST_REASON`，运行完整的实时 dogfood，并将新的验收标记写入该证明目录。将原始的 `--json` 转录输出发送到所有手稿树之外的私有临时目录。它包含 API 响应体和绝对主机路径。`mktemp -d` 创建的该目录权限为 `0700`；转录文件权限为 `0600`。门禁结束后，删除该目录：在失败时，先打印失败的命令，然后删除它；在成功时，在继续之前删除它。`publish package` 强制实施相同的边界：它省略 `publish-live-gate*.json`、`*-publish-live-gate.json`、dogfood 结果转储（`dogfood-results*.json`、`*-dogfood-results.json`）以及 `pipeline/` 树，包括早先 dogfood 运行已保存在证明下的副本。它仍会复制 `phase5-acceptance.json` 和 `phase5-skip.json`。

```bash
LIVE_GATE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/printing-press-publish.XXXXXX")
chmod 700 "$LIVE_GATE_DIR"
LIVE_GATE_JSON="$LIVE_GATE_DIR/${API_SLUG}-${RUN_ID}-publish-live-gate.json"
LIVE_GATE_ARGS=(
  dogfood
  --dir "$CLI_DIR"
  --live
  --level full
  --timeout 120s
  --research-dir "$RESEARCH_DIR"
  --write-acceptance "$PROOFS_DIR/phase5-acceptance.json"
  --json
)
if [ -n "$AUTH_ENV" ]; then
  LIVE_GATE_ARGS+=(--auth-env "$AUTH_ENV")
fi

rm -f "$PROOFS_DIR/phase5-skip.json"
if ! (
  umask 077
  set +e
  "$PRINTING_PRESS_BIN" "${LIVE_GATE_ARGS[@]}" >"$LIVE_GATE_JSON"
  live_gate_status=$?
  chmod 600 "$LIVE_GATE_JSON" 2>/dev/null || true
  exit "$live_gate_status"
); then
  echo "Publish live gate failed. See $PROOFS_DIR/phase5-acceptance.json."
  jq -r '.tests[]? | select(.status == "fail") | "- \(.command) [\(.kind)]: \(.reason // "failed")"' "$LIVE_GATE_JSON" 2>/dev/null || true
  rm -rf "$LIVE_GATE_DIR"
  exit 1
fi
rm -rf "$LIVE_GATE_DIR"
```

如果失败，停止方式与第 4 步的 `passed: false` 完全相同：无托管克隆、无分支、无包、无 PR。报告失败的命令、存在时的退出码、stderr 或原因片段，以及新证明文件的路径，以便操作员可以重新运行 dogfood 并修复 CLI。

如果从 `--skip-live-test=<reason>` 设置了 `SKIP_LIVE_TEST_REASON`，则不运行 dogfood，而是写入一个新的跳过标记：

```bash
SKIP_REASON_LOWER=$(printf '%s' "$SKIP_LIVE_TEST_REASON" | tr '[:upper:]' '[:lower:]')
case "$AUTH_TYPE" in
  api_key|bearer_token|oauth2)
    ;;
  none)
    case "$SKIP_REASON_LOWER" in
      *upstream*outage*|lan-unreachable-from-generation-host)
        ;;
      *)
        echo "ERROR: --skip-live-test is only valid for auth_type=none during a known upstream outage or LAN-unreachable hardware case."
        exit 1
        ;;
    esac
    ;;
  *)
    echo "ERROR: --skip-live-test is not valid for auth_type=$AUTH_TYPE. Run the live gate instead."
    exit 1
    ;;
esac

API_KEY_AVAILABLE=false
if [ -n "$AUTH_ENV" ] && [ -n "${!AUTH_ENV:-}" ]; then
  API_KEY_AVAILABLE=true
fi

SOURCE_FILES=$(find "$CLI_DIR" \( -type d \( -name '.git' -o -name '.manuscripts' -o -name '.printing-press' \) -prune \) -o -type f \( -name '*.go' -o -name 'go.mod' -o -name 'go.sum' -o -name 'spec.json' -o -name 'spec.yaml' -o -name 'spec.yml' \) -print | LC_ALL=C sort)
SOURCE_FINGERPRINT=$(
  while IFS= read -r SOURCE_FILE; do
    [ -z "$SOURCE_FILE" ] && continue
    SOURCE_REL="${SOURCE_FILE#"$CLI_DIR"/}"
    SOURCE_HASH=$(shasum -a 256 "$SOURCE_FILE" | sed 's/[[:space:]].*//')
    printf '%s\0%s\n' "$SOURCE_REL" "$SOURCE_HASH"
  done <<EOF | shasum -a 256 | sed 's/[[:space:]].*//'
$SOURCE_FILES
EOF
)
if [ -z "$SOURCE_FINGERPRINT" ]; then
  echo "ERROR: unable to fingerprint CLI source before writing the Phase 5 skip marker."
  exit 1
fi

rm -f "$PROOFS_DIR/phase5-acceptance.json"
jq -n \
  --arg api "$API_SLUG" \
  --arg run "$RUN_ID" \
  --arg reason "$SKIP_LIVE_TEST_REASON" \
  --arg auth "$AUTH_TYPE" \
  --arg source_fingerprint "$SOURCE_FINGERPRINT" \
  --argjson api_key_available "$API_KEY_AVAILABLE" \
  --argjson browser_session_available false \
  '{
    schema_version: 1,
    api_name: $api,
    run_id: $run,
    status: "skip",
    level: "none",
    source_fingerprint: $source_fingerprint,
    skip_reason: $reason,
    auth_context: {
      type: $auth,
      api_key_available: $api_key_available,
      browser_session_available: $browser_session_available
    }
  }' > "$PROOFS_DIR/phase5-skip.json"
if [ "$SKIP_REASON_LOWER" = "lan-unreachable-from-generation-host" ]; then
  tmp_marker=$(mktemp "${TMPDIR:-/tmp}/phase5-skip.XXXXXX")
  jq '.auth_context.local_network_only = true' "$PROOFS_DIR/phase5-skip.json" > "$tmp_marker" &&
    mv "$tmp_marker" "$PROOFS_DIR/phase5-skip.json"
fi
LIVE_GATE_JSON=""
```

然后重新运行第 4 步的验证：

```bash
"$PRINTING_PRESS_BIN" publish validate --dir "$CLI_DIR" --json
```

这第二次验证证明新的验收或跳过标记满足打包和发布所依赖的同一 Phase 5 契约。如果失败，在第 5 步之前停止。

## 第 5 步：托管克隆

发布技能在 `$PUBLISH_REPO_DIR` 管理其自身的库仓库克隆。

### 首次设置

如果 `$PUBLISH_REPO_DIR` 不存在：

1. **检测推送权限：**
   ```bash
   GH_USER=$(gh api user --jq '.login')
   HAS_PUSH=$(gh api repos/mvanhorn/printing-press-library --jq '.permissions.push' 2>/dev/null || echo "false")
   ```

2. **检测 git 协议：**
   ```bash
   USE_SSH=false
   if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
     USE_SSH=true
   fi
   ```

3. **根据权限克隆：**

   **推送权限**（`HAS_PUSH` 为 `true`）：
   ```bash
   # 直接克隆 — origin 即上游
   if [ "$USE_SSH" = "true" ]; then
     REPO_URL="git@github.com:mvanhorn/printing-press-library.git"
   else
     REPO_URL="https://github.com/mvanhorn/printing-press-library.git"
   fi
   # 轻量级克隆：blobless + shallow + sparse。发布流程仅触及
   # 目标 CLI 自身的目录 — 它不再重新生成
   # cli-skills/registry 镜像（参见第 6 步） — 因此将其他
   # CLI 的源物化是浪费带宽和磁盘空间（完整克隆为多 GB；
   # 此方法仅需几十 MB）。该锥体保留 `tools`、`cli-skills` 和目标
   # `library/<category>`，以便下方的同类别 find/rm/copy 操作
   # 在真实的工作树上进行。跨类别冲突检查使用 `git ls-tree`
   # （从 blobless 克隆读取完整树）而非 `ls`。
   git clone --filter=blob:none --depth 1 --sparse "$REPO_URL" "$PUBLISH_REPO_DIR"
   # 技能管理的克隆由此流程拥有；强制 LF 检出行为，以便
   # Windows core.autocrlf 默认值不会创建仅 CRLF 的镜像差异。
   git -C "$PUBLISH_REPO_DIR" config core.autocrlf false
   git -C "$PUBLISH_REPO_DIR" sparse-checkout set tools cli-skills library/<category>
   ```

**无推送访问权限** (`HAS_PUSH` 为 `false`)：
```bash
# 首先创建分支 — 如果创建分支被阻止则明确失败
if ! gh repo fork mvanhorn/printing-press-library --clone=false 2>&1; then
  echo "ERROR: 无法创建 mvanhorn/printing-press-library 分支。"
  echo "仓库可能限制创建分支，或者您可能已经有一个不同名称的分支。"
  echo "手动创建分支：https://github.com/mvanhorn/printing-press-library/fork"
  exit 1
fi
FORK="$GH_USER/printing-press-library"

# 根据协议偏好构建 URL
if [ "$USE_SSH" = "true" ]; then
  FORK_URL="git@github.com:$FORK.git"
  UPSTREAM_URL="git@github.com:mvanhorn/printing-press-library.git"
else
  FORK_URL="https://github.com/$FORK.git"
  UPSTREAM_URL="https://github.com/mvanhorn/printing-press-library.git"
fi

# 轻量级克隆（无 blob + 浅层 + 稀疏） — 请参考上文的 push-access 分支了解原因和 cone 内容。
git clone --filter=blob:none --depth 1 --sparse "$FORK_URL" "$PUBLISH_REPO_DIR"
# 由技能管理的克隆由此流程拥有；强制 LF 检出行为，以便 Windows core.autocrlf 默认值不会创建仅 CRLF 的镜像差异。
git -C "$PUBLISH_REPO_DIR" config core.autocrlf false
cd "$PUBLISH_REPO_DIR"
git sparse-checkout set tools cli-skills library/<category>
git remote add upstream "$UPSTREAM_URL"
git fetch --filter=blob:none --depth 1 upstream
```

4. **缓存配置**：
```json
{
  "managed_by": "printing-press-publish",
  "repo_url": "https://github.com/mvanhorn/printing-press-library",
  "access": "推送或创建分支",
  "gh_user": "<gh 用户名>",
  "protocol": "ssh 或 https",
  "clone_path": "<展开的 $PUBLISH_REPO_DIR>",
  "scope_dir": "<绝对源工作树路径>",
  "module_path_base": "github.com/mvanhorn/printing-press-library/library"
}
```
写入 `$PUBLISH_CONFIG`。`access` 字段决定后续所有步骤的流程。`gh_user` 字段用于跨仓库 PR 头。`module_path_base` 始终引用上游仓库（PR 将提交到该仓库）。

### 后续发布

读取 `$PUBLISH_CONFIG`，然后重新检查访问权限（以防权限变更，例如用户被授予推送权限或权限被撤销）：

```bash
CURRENT_ACCESS=$(gh api repos/mvanhorn/printing-press-library --jq '.permissions.push' 2>/dev/null || echo "false")
CACHED_ACCESS=$(jq -r .access "$PUBLISH_CONFIG")

if [ "$CURRENT_ACCESS" = "true" ] && [ "$CACHED_ACCESS" = "创建分支" ]; then
  echo "访问权限升级为推送。重新配置克隆..."
  rm -rf "$PUBLISH_REPO_DIR"
  # 使用推送权限重新运行首次设置
fi
if [ "$CURRENT_ACCESS" = "false" ] && [ "$CACHED_ACCESS" = "推送" ]; then
  echo "推送权限被撤销。重新配置克隆为创建分支..."
  rm -rf "$PUBLISH_REPO_DIR"
  # 使用创建分支权限重新运行首次设置
fi
```

如果由于访问权限变更而删除了克隆，请重新运行上述首次设置。否则，更新克隆以匹配标准上游：

```bash
cd "$PUBLISH_REPO_DIR"
git config core.autocrlf false

if [ "$(jq -r .access $PUBLISH_CONFIG)" = "推送" ]; then
  # 推送权限：origin 即为上游
  git fetch --filter=blob:none --depth 1 origin
  git checkout main
  git reset --hard origin/main
  # 在复制此 CLI 之前，删除先前的发布分支中遗留的库片段。被分支本地 .gitignore 隐藏的忽略文件在检出后可能成为普通未跟踪文件，而后续的库添加不应将另一个 CLI 的残留内容扫入此 PR。
  git clean -fdq library/
else
  # 创建分支：origin 是创建分支，上游是标准版本
  git fetch --filter=blob:none --depth 1 upstream
  git checkout main
  git reset --hard upstream/main
  # 在复制此 CLI 之前，删除先前的发布分支中遗留的库片段。被分支本地 .gitignore 隐藏的忽略文件在检出后可能成为普通未跟踪文件，而后续的库添加不应将另一个 CLI 的残留内容扫入此 PR。
  git clean -fdq library/
  # 同步 origin（创建分支）以便 git push 正常工作
  git push origin main --force-with-lease 2>/dev/null || true
fi

# 现有的管理克隆可能已经为不同的发布类别设置了稀疏。在步骤 6 使用基于文件系统的删除和复制操作之前，刷新当前目标类别的 cone。
if git -C "$PUBLISH_REPO_DIR" config --bool core.sparseCheckout | grep -qx true; then
  git -C "$PUBLISH_REPO_DIR" sparse-checkout set tools cli-skills library/<category>
fi
```

验证克隆是否健康：

```bash
git rev-parse --is-inside-work-tree
test "$(git rev-parse --abbrev-ref HEAD)" = "main"
```

如果失败，克隆已损坏。删除 `$PUBLISH_REPO_DIR` 并重新运行首次设置。

### 中断状态恢复

在创建新分支之前，检查是否有未提交的更改：

```bash
cd "$PUBLISH_REPO_DIR"
git status --porcelain
```

如果有未提交的更改，通过 AskUserQuestion 询问用户：
- "重置并重新开始"
- "使用现有更改继续"

如果重置，运行 `git checkout -- . && git clean -fd`。

### 预打包发布状态快照

在步骤 6 修改管理克隆之前，记录此 API 短语是否已存在于公共库树中。步骤 6 删除并替换 `library/*/<api-slug>`，因此任何冲突或打包后的发布路径决策都必须使用此预打包快照，而不是新鲜的 `ls`。

```bash
# 从 git 树读取，而不是工作目录：稀疏检出仅实现目标类别，但短语可能在任何类别中冲突。
PREEXISTING_MERGED_PATHS=$(git -C "$PUBLISH_REPO_DIR" ls-tree -r --name-only HEAD \
  | sed -n 's#^\(library/[^/]*/<api-slug>\)/.*#\1#p' | sort -u || true)
PREEXISTING_MERGED_COLLISION=false
if [ -n "$PREEXISTING_MERGED_PATHS" ]; then
  PREEXISTING_MERGED_COLLISION=true
  # 如果这是一个类别更改重新打印，在步骤 6 运行基于文件系统的账本保留和删除之前，实现现有类别路径。
  if git -C "$PUBLISH_REPO_DIR" config --bool core.sparseCheckout | grep -qx true; then
    while IFS= read -r EXISTING_MERGED_PATH; do
      [ -n "$EXISTING_MERGED_PATH" ] || continue
      if [ "$EXISTING_MERGED_PATH" != "library/<category>/<api-slug>" ]; then
        git -C "$PUBLISH_REPO_DIR" sparse-checkout add "$EXISTING_MERGED_PATH"
      fi
    done <<EOF
$PREEXISTING_MERGED_PATHS
EOF
  fi
fi
```

## 步骤 6：打包

读取 `$PUBLISH_CONFIG` 获取 `module_path_base`。使用 API 短语（而不是 CLI 名称）构建完整模块路径：

```
MODULE_PATH="<module_path_base>/<category>/<api-slug>"
```

例如：`github.com/mvanhorn/printing-press-library/library/productivity/notion`

**`--module-path` 在 `--dest` 模式下是必需的。** 使用 `--dest` 打包时，始终传递 `--module-path "$MODULE_PATH"`。省略它将静默跳过 go.mod/import 重写（`RewriteModulePath` 由该标志控制），因此打包的 CLI 保持 `module <cli-name>`，而库 CI 将因模块路径不匹配而拒绝 PR。`publish package` 在重写后验证已暂存树的模块路径：使用 `--module-path`，已暂存的 `go.mod` 必须声明确切的该路径（裸 CLI 名称模块仍然失败）；不使用 `--module-path`，则必须使用标准 `github.com/mvanhorn/printing-press-library/library/` 前缀。在源树上的独立 `publish validate` 会将该检查显示为警告 — 在重写前，预期存在裸模块名称；权威失败是在打包步骤。

使用 `--target` 运行 `publish package` 将 CLI 暂存到唯一的临时目录，然后复制到发布仓库：

```bash
PUBLISH_STAGING_ROOT="/tmp/printing-press/publish"
mkdir -p "$PUBLISH_STAGING_ROOT"
STAGING_PARENT="$(mktemp -d "$PUBLISH_STAGING_ROOT/<api-slug>-XXXXXX")"
STAGING_DIR="$STAGING_PARENT/package"

# 重新打印传递现有公共库条目，因此 package 将其运行时版本声明布局标记而不是留下 0.0.0-dev。
BASE_CLI_DIR="$(find "$PUBLISH_REPO_DIR/library" -mindepth 2 -maxdepth 2 -type d -name "<api-slug>" -print -quit)"
PACKAGE_BASE_ARGS=()
if [ -n "$BASE_CLI_DIR" ]; then
  PACKAGE_BASE_ARGS=(--base-dir "$BASE_CLI_DIR")
fi

cli-printing-press publish package \
  --dir <cli-dir> \
  --category <category> \
  --target "$STAGING_DIR" \
  --module-path "$MODULE_PATH" \
  "${PACKAGE_BASE_ARGS[@]}" \
  --json
```

解析 JSON 结果。注意 `staged_dir`、`module_path`、`manuscripts_included` 和 `run_id`。`module_path` 字段确认了打包 CLI 的 `go.mod` 和导入路径中设置的 Go 模块路径。

`publish package` 在返回成功之前对暂存的 CLI 执行强制 vendor 前缀秘密扫描，包括复制的 manuscripts。如果它报告 `vendor-prefix tokens detected`，停止并删除或修改报告的文件：行位置，然后重试。这是一个硬性限制，不依赖于 `gitleaks`、`trufflehog` 或目标仓库的推送保护。

然后复制暂存的 CLI 到发布仓库，替换任何现有版本，同时保留公共库的发布账本文件（如果是重新打印）：

```bash
STAGED_CLI_DIR="$STAGING_DIR/library/<category>/<api-slug>"
DEST_CATEGORY_DIR="$PUBLISH_REPO_DIR/library/<category>"
DEST_CLI_DIR="$DEST_CATEGORY_DIR/<api-slug>"

if [ ! -d "$STAGED_CLI_DIR" ]; then
  echo "missing staged CLI directory: $STAGED_CLI_DIR" >&2
  exit 1
fi
mkdir -p "$DEST_CATEGORY_DIR"

# 保留发布账本文件和现有 shipcheck 报告，然后删除当前公共库条目。新的 CLI 在发布前不包含 .printing-press-release.json，直到库的 post-merge 工作流将其标记为真实发布；重新打印保留现有的变更日志历史记录和发布元数据，直到该工作流标记下一个发布。
# 新鲜打印会从暂存树中删除 dogfood-results.json 和 workflow-verify-report.json；重新打印必须将这些目录文件复制回来，以便覆盖不会删除它们。
RELEASE_LEDGER_TMP="$(mktemp -d)"
PUBLISH_SWAP_DIR="$(mktemp -d "$DEST_CATEGORY_DIR/.<api-slug>.XXXXXX")"
trap 'rm -rf "$RELEASE_LEDGER_TMP" "$PUBLISH_SWAP_DIR"' EXIT
for LEDGER_FILE in CHANGELOG.md .printing-press-release.json dogfood-results.json workflow-verify-report.json; do
  EXISTING_LEDGER="$(find "$PUBLISH_REPO_DIR/library" -mindepth 3 -maxdepth 3 -path "*/<api-slug>/$LEDGER_FILE" -print -quit)"
  if [ -n "$EXISTING_LEDGER" ]; then
    cp "$EXISTING_LEDGER" "$RELEASE_LEDGER_TMP/$LEDGER_FILE"
  fi
done

# 在删除当前公共库条目前，将暂存的 CLI 复制到同一类别的交换目录。这可以防止失败的复制在发布仓库中删除旧 CLI。
cp -R "$STAGED_CLI_DIR/." "$PUBLISH_SWAP_DIR/"

for LEDGER_FILE in CHANGELOG.md .printing-press-release.json dogfood-results.json workflow-verify-report.json; do
  if [ -f "$RELEASE_LEDGER_TMP/$LEDGER_FILE" ]; then
    cp "$RELEASE_LEDGER_TMP/$LEDGER_FILE" "$PUBLISH_SWAP_DIR/$LEDGER_FILE"
  fi
done

# 删除现有版本（处理类别更改），然后原子性地在目标类别中安装准备好的替换版本。
rm -rf "$PUBLISH_REPO_DIR/library"/*/"<api-slug>"
mv "$PUBLISH_SWAP_DIR" "$DEST_CLI_DIR"
rm -rf "$RELEASE_LEDGER_TMP"
trap - EXIT

# 重新打印必须保留基础 CLI 的运行时版本声明布局及其账本文件。新鲜打印可以移动 `var version = ...` 在文件之间，但公共库的发布账本守卫在正常发布 PR 中会拒绝这些移动，因为 post-merge 发布工作流拥有版本标记。
cd "$PUBLISH_REPO_DIR"
VERSION_DECL_BASE_REF=upstream/main
if ! git rev-parse --verify --quiet "$VERSION_DECL_BASE_REF" >/dev/null; then
  VERSION_DECL_BASE_REF=origin/main
fi
VERSION_DECL_DIFF="$(git diff --unified=0 "$VERSION_DECL_BASE_REF" -- \
  "library/*/<api-slug>/internal/cli/root.go" \
  "library/*/<api-slug>/internal/cli/version.go" \
  "library/*/<api-slug>/cmd/<api-slug>-pp-mcp/main.go")" || {
  echo "failed to compare runtime version declarations with ${VERSION_DECL_BASE_REF}" >&2
  exit 1
}
printf '%s\n' "$VERSION_DECL_DIFF" \
  | grep -E '^[+-][[:space:]]*var version[[:space:]]*=' || true

# 如果命令打印更改，停止。不要手动编辑版本声明。
# publish package --base-dir 应该已经将替换与基础树协调：
# - root.go 声明保留在 root.go 中，使用确切的标记值；删除 version.go 中的重复声明并保留其命令代码。
# - version.go 声明保留在 version.go 中，使用确切的标记值；删除内部 CLI 包中添加的任何新鲜声明。
# - MCP main 声明保留在 MCP main 中，使用确切的标记值。如果基础 MCP main 硬编码版本，则保留该表达式。
# - 如果基础在这些运行时表面中没有声明，则保留没有声明的布局及其现有的字面量/引用形式。不要引入新鲜打印的 0.0.0-dev 声明。
# 重新运行 publish package，将 --base-dir 指向现有的库条目，然后重复此 diff。不要继续，直到命令打印没有匹配的行。

# 删除根级二进制文件（不应提交）。publish package 已经在复制前删除这些；这个 rm -f 是为了代理路径的保险措施。覆盖本地构建路径可能丢弃的名称：裸短语、CLI 二进制文件、live-dogfood 探测二进制文件和 MCP 对等。
rm -f "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/<api-slug>" \
      "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/<cli-name>" \
      "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/<cli-name>-dogfood" \
      "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/<api-slug>-pp-mcp"

# 多重防御：在 README 和注册表表面之前验证打印机归属。
PRINTER=$(jq -r '.printer // ""' "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/.printing-press.json")
PRINTER_NAME=$(jq -r '.printer_name // ""' "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/.printing-press.json")
if [ -z "$PRINTER" ]; then
  echo "ERROR: manifest .printer 为空。设置 'git config --global github.user <your-handle>' 并在发布前重新打印。"
  exit 1
fi
if [ "$PRINTER" = "USER" ] || [ "$PRINTER" = "user" ]; then
  echo "ERROR: manifest .printer 是字面量哨兵 \"$PRINTER\"（在打印时未设置 git config github.user）。设置它并在发布前重新打印。"
  exit 1
fi
if [ -z "$PRINTER_NAME" ]; then
  echo "ERROR: manifest .printer_name 为空。设置 'git config --global user.name <your display name>' 并在发布前重新打印。"
  exit 1
fi

# 在这里不要重新生成或提交 `cli-skills/pp-<api-slug>/SKILL.md` 或 `registry.json`。两者都是由库的 `generate-skills.yml` 和 `generate-registry.yml` 工作流通过 `[skip ci]` 机器人提交重新生成的。库在 `verify-library-conventions.yml` 中的 `Fail on changes to generated artifacts` 检查会硬失败任何 diff 与基础冲突的 PR，无论创建分支还是同一仓库 origin。库不再有 PR 中的自动修复路径；不要在这里重新引入镜像或注册表重新生成。此外，也不要手动更新 CHANGELOG.md、.printing-press-release.json 或运行时版本字符串以进行发布会计；库发布账本工作流在合并后拥有这些。

# 验证此更改/新 CLI 在发布仓库中构建且没有可访问的 Go 漏洞
cd "$PUBLISH_REPO_DIR/library/<category>/<api-slug>" \
  && go build ./... \
  && go run golang.org/x/vuln/cmd/govulncheck@v1.3.0 ./...
```

在发布 PR 中将漏洞验证范围限制为 `library/<category>/<api-slug>`。公共库是一个历史收藏，无法在每次无关的 PR 上保持完全最新；全库 govulncheck 扫描属于计划/报告工作流，而阻塞 CI 应仅扫描添加或更改的 CLI 模块。

在发布仓库复制和构建验证完成后，删除预发布目录：

```bash
rm -rf "$STAGING_PARENT"
```

注意：`staged_dir` 通过 API slugs（例如 `espn`）进行索引，与发布仓库的目录布局匹配。复制步骤是同名复制，不是重命名。

## 第 6.5 步：记录自定义内容

在碰撞检测或分支创建之前，检查打包的 CLI 的自定义内容索引：

索引以两种形状之一提供：每个补丁目录 `.printing-press-patches/`（当前）或旧的单个数组 `.printing-press-patches.json`（较旧的打印，尚未规范化）。验证存在的任何形状：

```bash
PATCHES_DIR="$PUBLISH_REPO_DIR/library/<category>/<api-slug>/.printing-press-patches"
PATCHES_INDEX="$PUBLISH_REPO_DIR/library/<category>/<api-slug>/.printing-press-patches.json"
if [ -d "$PATCHES_DIR" ]; then
  # 每个补丁目录：每个 `<id>.json` 必须是一个包含与旧的单个数组文件在顶层（现在每个文件）保持相同来源的 JSON 对象，因此验证与旧分支下的验证相同。_meta.json（CLI 全局列表）和 .gitkeep 免责。
  for f in "$PATCHES_DIR"/*.json; do
    [ -e "$f" ] || continue
    [ "$(basename "$f")" = "_meta.json" ] && continue
    if ! jq -e '
      (type == "object") and
      (.schema_version | type == "number") and
      (.id | type == "string" and length > 0) and
      (.applied_at | type == "string" and length > 0) and
      (.base_run_id | type == "string" and length > 0) and
      (.base_printing_press_version | type == "string" and length > 0)
    ' "$f" >/dev/null; then
      echo "ERROR: 打包的 CLI 包含格式错误的补丁文件 $f。在发布前使用当前的 cli-printing-press 二进制重新打印。"
      exit 1
    fi
  done
elif [ -f "$PATCHES_INDEX" ]; then
  if ! jq -e '
    (.schema_version | type == "number") and
    (.applied_at | type == "string" and length > 0) and
    (.base_run_id | type == "string" and length > 0) and
    (.base_printing_press_version | type == "string" and length > 0) and
    (.patches | type == "array")
  ' "$PATCHES_INDEX" >/dev/null; then
    echo "ERROR: 打包的 CLI 包含格式错误的 .printing-press-patches.json。在发布前使用当前的 cli-printing-press 二进制重新打印。"
    exit 1
  fi
else
  echo "ERROR: 打包的 CLI 缺少其补丁索引 (.printing-press-patches/ 或 .printing-press-patches.json)。在发布前使用当前的 cli-printing-press 二进制重新打印。"
  exit 1
fi
```

当前 `cli-printing-press generate` 生成的全新打印包括 `.printing-press-patches/` 目录，其中仅包含 `.gitkeep`；如果没有在生成后进行手动自定义，则保持不变。如果两种形状都不存在，CLI 由旧二进制生成；使用当前的 `cli-printing-press` 构建重新打印，而不是手动合成确定性来源字段。

## 第 6.6 步：记录贡献者归属

当运行发布操作的人**不是** CLI 的原始创建者时，将他们记录为贡献者，以便他们在 README 签名、NOTICE 和公共注册表中获得认可。命令是幂等的——它跳过创建者和任何已列出的人——因此它对每个发布运行都是安全的：

```bash
"$PRINTING_PRESS_BIN" contributors add \
  --dir "$PUBLISH_REPO_DIR/library/<category>/<api-slug>" \
  || echo "note: 这个二进制文件早于 'contributors add'；跳过贡献者记录"
```

此步骤尽力而为：`contributors add` 是一个附加命令，因此早于它的二进制文件仅跳过记录而不是阻止发布（`min-binary-version` 地板仅跟踪主版本）。当此发布是重新打印（从头开始重新生成）时，请传递 `--front`，以便重新打印者首先列在贡献者中。永远不要手动编辑 `contributors[]` 或 `creator` 块——创建者是永久的，命令拥有该列表（与“以清单为权威”规则匹配）。

如果在打印或发布会话期间更改了生成的 CLI 文件，请在打开库 PR 之前记录每个自定义内容的简洁条目——每个补丁一个 `.printing-press-patches/<id>.json` 文件（目录取代了旧的 `patches[]` 数组，因此并发 PR 从不冲突）。这些条目是告诉未来代理和再生工具必须保留生成器输出之外的持久手动编辑合同。

使用此形状（一个文件，`.printing-press-patches/<id>.json`）：

```json
{
  "schema_version": 2,
  "id": "<api-slug>-<简短功能名称>",
  "applied_at": "<YYYY-MM-DD>",
  "base_run_id": "<从 .printing-press.json 复制>",
  "base_printing_press_version": "<从 .printing-press.json 复制>",
  "summary": "发生了什么（一句话）。",
  "reason": "为什么生成的输出需要这个自定义内容。",
  "files": ["internal/cli/example.go"],
  "validated_outcome": "可选：证明自定义内容的集中检查。",
  "upstream_issue": "可选：https://github.com/mvanhorn/cli-printing-press/issues/<n>"
}
```

规则：

- 文件名是补丁 `id`。使用连字符分隔的 ID，以 API slugs 开头，以便在整个公共库中通过 grep 查找。
- 保持 `summary` 和 `reason` 简短。每个条目是一个索引，不是 git diff 的副本。
- 当非 Go 支持文件是同一代码级别自定义的一部分时，在 `files` 中包含它们。仅对 README/SKILL.md 的润色不需要补丁清单条目。`publish validate` 读取记录，如果记录的 `files[]` 路径丢失、每个补丁记录省略 `schema_version` 或声明不支持的一个，或者声明的 `call_sites` / `markers` / `marker` 字符串不在记录的文件中，则失败。`files[]` 对每个 `call_sites` / `markers` / `marker` 针对是必需的，以便其他地方遗留的子字符串不能掩盖被丢弃的自定义内容。针仅在这些记录的文件中检查。
- 内联 `// PATCH(...)` 源代码注释是可选的导航辅助工具。公共库验证器需要一个补丁索引（目录或旧文件）和格式良好的条目；它不需要标记/注释配对。
- 如果一个条目仅存在以解决一个不再适用的旧验证器或管道错误，请删除过时的修复文件，而不是继续携带它。

有关权威的公共库编写合同，请阅读 `mvanhorn/printing-press-library` 的 `AGENTS.md` 部分中的 “`.printing-press-patches/` 记录库侧自定义”。

## 第 7 步：碰撞检测与解决

在管理的克隆更新后，在创建分支或 PR 之前检查名称冲突。这取代了以前的“检查现有 PR”步骤。

### 检测

按顺序运行这些检查：

**1. 检查管理的克隆中的合并 CLI：**

```bash
MERGED_COLLISION="$PREEXISTING_MERGED_COLLISION"
MERGED_PATHS="$PREEXISTING_MERGED_PATHS"
```

使用步骤 5 的预打包快照。在此处不要重新运行 `ls "$PUBLISH_REPO_DIR/library"/*/"<api-slug>"`：步骤 6 已经将新包复制到该路径，因此一个新鲜的 `ls` 会使每个新打印看起来像合并冲突。如果 `MERGED_COLLISION=true`，请从 `MERGED_PATHS` 记录类别路径。

**2. 检查所有打开的 PR（任何作者）：**

```bash
gh pr list --repo mvanhorn/printing-press-library --head "feat/<api-slug>" --state open --json number,title,url,author
```

如果列表非空，记录 `PR_COLLISION=true`。对于每个 PR，记录 PR 编号、URL 和作者登录。

**3. 确定自己的 PR：**

通过 `--author @me` 过滤步骤 2 中的 PR 列表：

对于基于分叉的 PR，头部包括用户名前缀：

```bash
ACCESS=$(jq -r .access "$PUBLISH_CONFIG")
GH_USER=$(jq -r .gh_user "$PUBLISH_CONFIG")

if [ "$ACCESS" = "fork" ]; then
  HEAD_REF="$GH_USER:feat/<api-slug>"
else
  HEAD_REF="feat/<api-slug>"
fi

gh pr list --repo mvanhorn/printing-press-library --head "$HEAD_REF" --state open --author @me --json number,title,url
```

如果找到，记录 `OWN_PR=true`，存储 `EXISTING_PR_NUMBER` 和 `EXISTING_PR_URL`。

**如果没有找到打开的 PR**，也检查同一分支上是否存在先前合并的 PR——任何作者，而不仅仅是你的：

```bash
MERGED_PR=$(gh pr list --repo mvanhorn/printing-press-library --head "$HEAD_REF" --state merged --json number --jq '.[0].number' 2>/dev/null)
```

如果 `MERGED_PR` 非空，分支名称已经使用并合并。设置 `BRANCH_MERGED=true`，以便步骤 8 创建一个新分支名称（例如 `feat/<api-slug>-YYYYMMDD`），而不是重用合并的分支。不要强制推送到一个已合并的分支——`gh pr edit` 会静默更新一个无人关注的已关闭 PR。

非作者查找也捕获**挤压僵尸分支**：GitHub 挤压合并将源分支保留在远程上，具有挤压前的提交引用，看起来“领先于 main”，但内容等同于挤压提交。如果没有此检查，技能将僵尸分类为全新发布，然后 `git push -u` 失败，因为远程分支已经存在。时间戳可以完全避免这个问题。

### 无碰撞

如果不存在合并的 CLI 且没有与你的匹配的打开 PR，从自己的 PR 检查设置 `EXISTING_PR_NUMBER`（如果没有则为空），然后正常进行到步骤 8。

如果找到你自己的一个打开 PR，通知用户：
> "找到你的打开 PR #N 对于 `<api-slug>`。将使用新版本更新它。"

### 检测到碰撞——显示信息

向用户显示找到的内容：

```
⚠️  名称冲突检测到对于 <api-slug>

  已合并：<category>/<api-slug> 存在于库中
  打开的 PR：#<number> 由 <author> — <url>
```

显示所有适用的行。如果 `OWN_PR=true`，请将 PR 标记为 "(你的)"。

### 解决路径

通过 AskUserQuestion 提供三个选项：

**如果 `OWN_PR=true`（你自己的打开 PR 存在）：**
- **更新** — 使用新版本更新你的现有 PR（默认，保留当前行为）
- **旁边** — 用限定符重命名你的，与现有的发布相邻
- **放弃** — 取消发布

**如果 PR 冲突是另一个用户，或者仅存在合并冲突：**
- **替换** — 故意覆盖现有的 CLI
- **旁边** — 用限定符重命名你的，与现有的发布相邻
- **放弃** — 取消发布并查看现有的 CLI/PR

#### 更新路径（自己的 PR）

这是现有的更新流程，带有分歧保护。从检测步骤设置 `EXISTING_PR_NUMBER` 并进行到步骤 8，它获取当前 PR 分支头部，检查新包会撤销的分支仅修复，然后才处理强制推送和 PR 描述更新。

#### 替换路径

**对于合并的 CLI 或你的 PR：** 标准确认：
> "这将替换现有的 `<api-slug>`。继续？"

**对于另一个用户的 PR：** 更强的确认，命名其他作者：
> "⚠️  这将替换 `<author>` 的 `<api-slug>` (PR #N)。确定？"

如果确认：
- PR 描述必须包括：`⚠️ **替换现有的 \`<api-slug>\`** — <用户提供的理由或“新版本”>`
- 设置 `EXISTING_PR_NUMBER=""`（创建一个新 PR，不要更新他们的）
- 正常进行到步骤 8

#### 旁边路径（重命名）

**1. 从清单的 `api_name` 字段提取原始 API slugs：**

```bash
# 从发布仓库的打包 CLI 中的 .printing-press.json 读取
ORIGINAL_API_SLUG=$(cat "$PUBLISH_REPO_DIR/library/<category>/<api-slug>/.printing-press.json" | jq -r '.api_name')
```

**2. 生成重命名建议** 使用 slugs 格式。根据用户选择的 slugs 推导新的 CLI 名称：

- 数字：`<api-slug>-2`（如果冲突，尝试 `-3`，`-4` 等）
- 非数字：`<api-slug>-alt`
- 自定义：提示用户输入限定词

用户选择 slugs 后，计算：

```bash
NEW_API_SLUG="<选择的-slug>"
NEW_CLI_NAME="${NEW_API_SLUG}-pp-cli"
```

向用户显示格式：
> "重命名格式：`<api-slug>-<限定符>`。选择一个限定符："
>
> 1. `2` → `<api-slug>-2`
> 2. `alt` → `<api-slug>-alt`
> 3. 输入自定义限定符

**3. 在显示之前验证每个建议不冲突：**

```bash
# 检查合并（读取 git 树，而不是稀疏工作目录）
git -C "$PUBLISH_REPO_DIR" ls-tree -r --name-only HEAD \
  | sed -n 's#^\(library/[^/]*/<建议>\)/.*#\1#p' | sort -u
# 检查打开的 PRs
gh pr list --repo mvanhorn/printing-press-library --head "feat/<建议>" --state open --json number
```

如果建议冲突，跳过它或增加数字后缀。

**4. 在发布仓库中重命名 CLI：**

由于步骤 6 将打包的 CLI 复制到 `$PUBLISH_REPO_DIR`，因此重命名操作在该目录上执行。注意：`--old-name`/`--new-name` 仍然使用 CLI 名称格式（例如 `dub-pp-cli`），因为 `RenameCLI` 执行内容替换——裸 slugs 会造成附带损害。`--dir` 路径使用 slugs 键控目录。重命名还会重写 `go.mod`、遗留的模块路径 slugs、安装器 slugs、环境前缀和 `research.json` 的 `api_name`（包括在 `.manuscripts/` 下）。成功重命名后不要手动修复这些。

```bash
cli-printing-press publish rename \
  --dir "$PUBLISH_REPO_DIR/library/<category>/<api-slug>" \
  --old-name <旧-cli-name> \
  --new-name "$NEW_CLI_NAME" \
  --json
```

解析 JSON 结果。验证 `"success": true`。注意 `new_dir` 现在应该是 `$PUBLISH_REPO_DIR/library/<category>/$NEW_API_SLUG`。

**5. 更新所有下游引用以进行步骤 8：**

- 分支名称：`feat/$NEW_API_SLUG`（不是旧 slugs）
- PR 标题：`feat($NEW_API_SLUG): add $NEW_API_SLUG`
- 提交消息：`feat($NEW_API_SLUG): add $NEW_API_SLUG`
- Registry.json 条目：`name` → `$NEW_API_SLUG`
- 设置 `EXISTING_PR_NUMBER=""`（重命名的 CLI 总是创建一个新 PR）

使用新名称进行步骤 8。

#### 放弃路径

显示存在的链接：
- 如果合并："现有 CLI 在 `library/<category>/<api-slug>/`"
- 如果打开 PR："打开 PR: <url>"

退出发布流程。如果步骤 6 已经将文件写入 `$PUBLISH_REPO_DIR`，请在管理的克隆中用 `git checkout -- . && git clean -fd` 进行清理。

## 第 8 步：分支、提交和 PR

### 创建分支

**如果 `EXISTING_PR_NUMBER` 设置**（更新现有的 PR）：

在替换它之前获取并检查当前 PR 分支。最新的 `origin/main` 加上新打包的 `library/<category>/<api-slug>/` 树是建议的更新。远程 PR 分支还可能包含来自驱动至绿色循环的已接受的审查修复。这些分支仅编辑必须不会被默默删除。

```bash
UPDATE_BRANCH="feat/<api-slug>"
UPDATE_BASE_REF="refs/printing-press-update-base/<api-slug>"

git fetch origin "+main:refs/remotes/origin/main" "+$UPDATE_BRANCH:$UPDATE_BASE_REF"

# 显示从当前 PR 头到新打包工作树的限定范围变更。这对于干净的更新是信息性的，对于挂起是强制性的上下文。
git diff --stat "$UPDATE_BASE_REF" -- "library/<category>/<api-slug>/"

# 仅分支路径是存在于当前 PR 分支但新打包工作树中缺失的文件。这些总是挂起，因为强制推送会删除它们。
WORKTREE_PATHS=$(find "library/<category>/<api-slug>" -type f -print 2>/dev/null | sort)
BRANCH_ONLY_PATHS=$(comm -23 \
  <(git ls-tree -r --name-only "$UPDATE_BASE_REF" -- "library/<category>/<api-slug>/" | sort) \
  <([ -n "$WORKTREE_PATHS" ] && printf '%s\n' "$WORKTREE_PATHS" || true))

# 修改路径仅在相对于 origin/main 的分支补丁不在新打包工作树中时需要人工审核。严格的超集通过：如果分支补丁可以从工作树反向应用，即使文件也有新鲜生成的变更，修复仍然存在。
BRANCH_ONLY_EDITS=$(git diff --name-only origin/main "$UPDATE_BASE_REF" -- "library/<category>/<api-slug>/" | while read -r path; do
  [ -n "$path" ] || continue
  if git diff origin/main "$UPDATE_BASE_REF" -- "$path" | git apply --check --reverse >/dev/null 2>&1; then
    continue
  else
    printf '%s\n' "$path"
  fi
done | sort -u)

if [ -n "$BRANCH_ONLY_PATHS$BRANCH_ONLY_EDITS" ]; then
  echo "HOLD: 更新 PR #$EXISTING_PR_NUMBER 会覆盖分支仅有的变更。"
  if [ -n "$BRANCH_ONLY_PATHS" ]; then
    echo "存在于 PR 分支但新包中缺失的文件："
    printf '%s\n' "$BRANCH_ONLY_PATHS" | sed 's/^/- /'
  fi
  if [ -n "$BRANCH_ONLY_EDITS" ]; then
    echo "在 PR 分支上编辑并在新包中再次更改的文件："
    printf '%s\n' "$BRANCH_ONLY_EDITS" | sed 's/^/- /'
  fi
  echo "不要推送。通过将分支仅有的修复恢复到新树上来协调，或者在使用上述路径后请求用户明确覆盖确认。"
  exit 1
fi
```

如果守卫退出，通过 `AskUserQuestion` 向用户提供两个选择：

- **先协调** — 将命名的分支仅有的文件或编辑恢复到新打包树，保留或添加匹配的 `.printing-press-patches/<id>.json` 记录以进行代码级修复，然后重新运行步骤 6 验证，最后重新运行此分歧守卫。
- **故意覆盖** — 仅在用户确认列出的路径已过时后继续，并包含 PR 正文笔记命名被覆盖的分支仅有的路径。

如果守卫未发现分支仅有的路径或编辑，覆盖本地分支：

```bash
git checkout -B feat/<api-slug>
```

**如果 `EXISTING_PR_NUMBER` 为空且 `BRANCH_MERGED` 为真**（之前的 PR 已合并）：

自动创建一个带时间戳的分支 — 不要重用已合并的分支名称：

```bash
git checkout -b feat/<api-slug>-$(date +%Y%m%d)
```

**如果 `EXISTING_PR_NUMBER` 为空且 `BRANCH_MERGED` 未设置**（没有开放的或已合并的 PR）：

检查过时的分支和竞争的 PR：

```bash
# 检查本地和远程分支
LOCAL_BRANCH=$(git branch --list "feat/<api-slug>" | head -1)
REMOTE_BRANCH=$(git ls-remote --heads origin "feat/<api-slug>" 2>/dev/null | head -1)

# 如果远程分支存在，检查谁拥有它
if [ -n "$REMOTE_BRANCH" ]; then
  # 检查此分支上的任何开放的 PR（不限于我们自己的）
  OTHER_PR=$(gh pr list --repo mvanhorn/printing-press-library --head "feat/<api-slug>" --state open --json number,author --jq '.[0]' 2>/dev/null)
fi
```

**如果另一个用户的开放 PR 存在于此分支**（`OTHER_PR` 非空且作者不是 `@me`）：
> "有人在 `<api-slug>` 上有一个开放的 PR（PR #N 由 @author 创建）。创建一个带时间戳的分支以避免冲突。"

自动创建一个带时间戳的分支：`feat/<api-slug>-YYYYMMDD`。不要提供覆盖选项 — 那会覆盖他们的工作。

**如果分支存在但没有竞争的 PR**（来自之前已关闭/合并的 PR 的过时分支）：

通过 AskUserQuestion 询问：
> "找到一个过时的分支 `feat/<api-slug>`（可能来自之前的发布）。要覆盖它吗？"

- "覆盖现有分支" — 重用分支名称
- "创建带时间戳的变体 (feat/<api-slug>-YYYYMMDD)"

**如果不存在分支**：正常创建。

```bash
# 新分支：
git checkout -b feat/<api-slug>

# 覆盖现有：
git checkout -B feat/<api-slug>
```

### 提交和推送

```bash
cd "$PUBLISH_REPO_DIR"
git add -A library/
# 已打包的包已经删除了本地二进制文件并通过了强制性的机密/PII 扫描，因此它是此发布的来源真相。
# 强制添加整个 CLI 目录：目标仓库或包本地 .gitignore 规则，如 `*-pp-cli`、`*-pp-mcp`、`/.manuscripts/` 或报告文件名不得静默抑制 cmd/、.manuscripts/ 或元数据文件下的必需发布工件。
git add -f "library/<category>/<api-slug>/"

# 预提交范围守卫：仅此 CLI 的替换加上任何预存在的相同 slug 的合并路径可以暂存。这会捕获来自先前发布分支的过时未跟踪片段，以防止它们泄漏到错误的 PR 中。
EXPECTED_STAGE_PREFIXES=$(printf '%s\n' "library/<category>/<api-slug>/" "$PREEXISTING_MERGED_PATHS" | sed '/^$/d; s#/*$#/#' | sort -u)
UNEXPECTED_STAGED=$(git diff --cached --name-only | awk -v prefixes="$EXPECTED_STAGE_PREFIXES" '
BEGIN {
  n = split(prefixes, p, "\n")
  while ((getline line) > 0) {
    matched = 0
    for (i = 1; i <= n; i++) {
      if (p[i] != "" && (line == p[i] || index(line, p[i]) == 1)) {
        matched = 1
        break
      }
    }
    if (!matched) print line
  }
}')
if [ -n "$UNEXPECTED_STAGED" ]; then
  echo "ERROR: 发布暂存路径超出预期的 CLI 范围：" >&2
  printf '%s\n' "$UNEXPECTED_STAGED" | sed 's/^/- /' >&2
  echo "重置管理的克隆并重新运行发布包，然后提交。" >&2
  exit 1
fi
git commit -m "feat(<api-slug>): add <api-slug>"
```

推送到 origin（对于非推送用户是 fork，对于推送用户是上游）：

**如果更新现有的 PR** (`EXISTING_PR_NUMBER` 设置）：

```bash
# 仅在上述更新路径分歧守卫通过后运行，或用户明确确认了故意覆盖命名的分支仅有的路径后运行。
git push --force-with-lease -u origin feat/<api-slug>
```

**如果创建新的 PR** 并且之前选择了“覆盖现有分支”：

```bash
git push --force-with-lease -u origin feat/<api-slug>
```

**否则**（新分支，无冲突）：

```bash
git push -u origin feat/<api-slug>
```

### 捕获推送的提交 SHA

推送后，捕获头提交 SHA。这用于在 PR 正文（见“构建 PR 描述”下文）中构建持久的文稿链接。

```bash
HEAD_SHA=$(git rev-parse HEAD)
```

SHA 在 `mvanhorn/printing-press-library` 上保持可解析，直到 PR 的生命周期结束（GitHub 将 fork-PR 头提交镜像到上游的 `refs/pull/<N>/head`），并且在 PR 合并和分支删除后仍然有效。此技能的每次调用在其推送后捕获新的 `HEAD_SHA` 并重写正文，因此链接在技能执行的更新中保持最新。如果分支在技能外部强制推送，重新运行 `/printing-press-publish` 以刷新正文 — 之前的链接仍然可解析，但它们将指向合并前和出 band 推送之前的文稿内容。

### 创建或更新 PR

从 `$PUBLISH_CONFIG` 读取 `access` 和 `gh_user`。这些决定了如何调用 `gh pr create`。

**对于基于 fork 的 PR** (`access` 是 `fork`)：使用 `--head <gh_user>:feat/<api-slug>`，以便 GitHub 从 fork 创建跨仓库 PR 到上游。如果没有 `--head`，`gh pr create` 会尝试在上游仓库上查找分支（用户无法推送），并失败。

**对于推送访问权限** (`access` 是 `push`)：使用 `--head feat/<api-slug>`，以便 GitHub 从此流程刚刚推送的分支创建 PR，即使管理的克隆或 shell 会话中检查了其他分支。

从以下内容构建 PR 描述：
- 宣言（`description`、`api_name`、`category`、`printing_press_version`、`spec_url`）
- 宣言的 `novel_features` 数组来自步骤 6 后打包的 CLI
- 步骤 4 捕获的 `help_output`
- CLI 的 README（前 2-3 段，或注明 README 缺失）
- 每个位于 `.manuscripts/<run-id>/research/` 和 `.manuscripts/<run-id>/proofs/` 下的文件的链接。每个链接必须是完整的 `https://github.com/mvanhorn/printing-press-library/blob/<HEAD_SHA>/library/<category>/<api-slug>/.manuscripts/<run-id>/<subdir>/<filename>` URL — 绝不能是相对路径（GitHub 会将它们解析为 `…/pull/`，产生损坏的 `…/pull/library/…` URL）和绝不能是目录（blob 视图需要文件）。枚举实际文件；不要编造或跳过它们。
- 步骤 4 的验证结果
- 步骤 4.5 的发布实时门结果，包括任何显式的 `--skip-live-test` 原因
- 缺失部分，列出任何缺失的宣言字段

从打包后的 `$PUBLISH_REPO_DIR/library/<category>/<api-slug>/.printing-press.json` 中读取 `novel_features`。保留宣言顺序。不要从 README 评论文本、技能评论文本、根帮助或运行记忆中派生此部分：这些表面可能被总结或手动编辑，而打包的宣言是发布时的来源真相。对于每个条目，包括命令、名称和描述。如果数组为空，则写 `在 .printing-press.json 中未记录新的命令。` 并将缺失的字段包含在 **缺失部分** 中；不要省略此部分。

还包含一个发布路径行，以便新的打印、再打印、PR 更新和冲突重命名可以区分：
- `新打印` — 没有合并的 CLI 且没有现有的 PR 匹配此 slug。
- `更新现有 PR #<N>` — 此发布刷新了一个开放的 PR。
- `再打印/替换` — 在此发布之前存在合并的库 CLI，并且选定的路径替换了它。这必须基于 `PREEXISTING_MERGED_COLLISION=true`，而不是基于打包后的树。
- `伴随打印` — 此发布重命名了 API slug 以避免冲突；包括原始 slug。
如果 `/printing-press-reprint` 交出了没有先前公共库来源的降级再打印，使用 `新打印` 并仅在可以从交出上下文中获取该上下文时添加降级再打印注释。

**强制要求：在构建 PR 正文之前，清理所有工作区 PII。** 库仓库是公开的。扫描任何实时测试结果、验收数据或文稿摘录，查找组织名称、团队成员姓名和电子邮件地址。替换为通用描述（“工作区”、“5 名团队成员”、“12 名用户”）。团队密钥（例如，“ESP”）可以，但组织名称（例如，“Acme Corp”）不可以。有关完整策略，请参阅 printing-press 技能中的 `references/secret-protection.md`。

将构建的 PR 正文写入临时 Markdown 文件并通过 `--body-file` 传递。对 PR 创建和 PR 更新都这样做。不要在 shell 参数中内联正文；大的 fenced 帮助输出、Markdown 表格和反引号太容易损坏。

**PR 描述模板：**

```markdown
## <api-slug>

<如果这是替换路径，则添加： "⚠️ **替换现有的 `<api-slug>`** — <用户的原因>">

<来自宣言的描述，或 "没有描述可用">

**API:** <api_name> | **分类:** <category> | **Press 版本:** <printing_press_version>
**规范:** <spec_url 或 "未指定">`

### 发布路径

<新打印 | 更新现有 PR #N | 再打印/替换 | 伴随打印来自 <original-api-slug>>

### CLI 形状

\`\`\`bash
$ <cli-name> --help
<来自验证的帮助输出>
\`\`\`

### 新命令

| 命令 | 名称 | 描述 |
|------|------|------|
| `<command>` | <name> | <description> |

### 此 CLI 做什么

<CLI 目录中 README.md 的前 2-3 段，或 "README 未找到">

### 文稿

<!-- 每个文件一个项目符号，不是每个目录一个。重复 research/ 行中的每个文件，以及 proofs/ 行中的每个文件。使用与文件匹配的人类标签（例如 `研究摘要`、`吸收宣言`、`新功能头脑风暴`、`阶段 5 验收`）。用推送后捕获的值替换 `<HEAD_SHA>`。不要使用相对路径。 -->

- [<label>](https://github.com/mvanhorn/printing-press-library/blob/<HEAD_SHA>/library/<category>/<api-slug>/.manuscripts/<run-id>/research/<filename>)
- [<label>](https://github.com/mvanhorn/printing-press-library/blob/<HEAD_SHA>/library/<category>/<api-slug>/.manuscripts/<run-id>/research/<filename>)
- … (每个 `.manuscripts/<run-id>/research/` 中的剩余文件一个项目符号)
- [<label>](https://github.com/mvanhorn/printing-press-library/blob/<HEAD_SHA>/library/<category>/<api-slug>/.manuscripts/<run-id>/proofs/<filename>)
- [<label>](https://github.com/mvanhorn/printing-press-library/blob/<HEAD_SHA>/library/<category>/<api-slug>/.manuscripts/<run-id>/proofs/<filename>)
- … (每个 `.manuscripts/<run-id>/proofs/` 中的剩余文件一个项目符号)

### 验证结果

| 检查 | 结果 |
|------|------|
| 宣言 | 通过/失败 |
| 阶段 5 | 通过/失败 |
| go mod tidy | 通过/失败 |
| govulncheck（仅此 CLI，可到达的发现） | 通过/失败 |
| go vet | 通过/失败 |
| go build | 通过/失败 |
| --help | 通过/失败 |
| --version | 通过/失败 |
| 文稿 | 存在/缺失 |

### 发布实时门

<如果步骤 4.5 运行了 dogfood： "在发布时完整运行了实时 dogfood 并通过。证明：`<proof path or manuscript link>`">
<如果步骤 4.5 被跳过： "跳过，原因：`<SKIP_LIVE_TEST_REASON>`">

### 缺失部分

<列出任何缺失的宣言字段，或如果所有内容都存在则省略此部分>
```

**如果更新现有的 PR** (`EXISTING_PR_NUMBER` 设置）：

```bash
cd "$PUBLISH_REPO_DIR"
PR_BODY_FILE="$(mktemp)"
# 将构建的 PR 正文 Markdown 写入 "$PR_BODY_FILE"。
gh pr edit "$EXISTING_PR_NUMBER" \
  --repo mvanhorn/printing-press-library \
  --body-file "$PR_BODY_FILE"
rm -f "$PR_BODY_FILE"
```

显示完整的 PR URL："更新 PR: <EXISTING_PR_URL>"（使用完整的 `https://` URL，而不是简称）。

**如果创建新的 PR**：

```bash
cd "$PUBLISH_REPO_DIR"

# 从配置中读取访问模式
ACCESS=$(jq -r .access "$PUBLISH_CONFIG")
GH_USER=$(jq -r .gh_user "$PUBLISH_CONFIG")

if [ "$ACCESS" = "fork" ]; then
  PR_HEAD_REF="$GH_USER:feat/<api-slug>"
else
  PR_HEAD_REF="feat/<api-slug>"
fi

PR_BODY_FILE="$(mktemp)"
# 将构建的 PR 正文 Markdown 写入 "$PR_BODY_FILE"。

gh pr create \
  --repo mvanhorn/printing-press-library \
  --head "$PR_HEAD_REF" \
  --base main \
  --title "feat(<api-slug>): add <api-slug>" \
  --body-file "$PR_BODY_FILE"

rm -f "$PR_BODY_FILE"
```

显示完整的 PR URL（例如，`https://github.com/mvanhorn/printing-press-library/pull/10`），而不是简称 `org/repo#N` 格式。完整 URL 在所有终端和上下文中都可点击。

## PR 打开后

一旦 PR 打开，它进入公共库仓库的审查合同。该合同由 [`mvanhorn/printing-press-library` AGENTS.md → "使用 Greptile 的自动代码审查"](
https://github.com/mvanhorn/printing-press-library/blob/main/AGENTS.md#automated-code-review-with-greptile) 拥有；阅读它以获取规范版本。从 `cli-printing-press` 调用此技能的代理不会加载库的 AGENTS.md，因此义务总结如下。

Greptile **增量审查**：你每次推送都会触发一次新的审查，这可能会暴露上一轮未发现的新问题。这是一个循环，不是单次通过 — 驱动 PR 到 *稳定的绿色*，并且在第一轮后不要宣布完成。

### 驱动 PR 到稳定绿色

迭代，直到**所有**以下条件都得到满足，并由最近的修复提交触发的审查确认：

- **所有 Greptile 检测项均已解决。** 0-5 分是一个置信度信号，不是门禁——标准是解决所有检测项。4/5 且所有项都解决即可；5/5 但仍有开放的 P1 不行。对于每个 P0/P1/P2 线程，要么提交一个修复，要么回复一个具体的理由说明为什么不应该触发——不是“不会修复”，而是 *为什么* 代码写法正确或 *为什么* 延迟是合理的。政策门禁还要求当前头 SHA 的最新分数 ≥ 4/5，所以保持最终头会议达到该阈值。
- **所有 CI 检查通过。** `verify-library-conventions`、`Govulncheck` 以及 PR 上的任何其他工作流。

从两个表面读取检测项——它们不重叠：

- `gh pr view <PR> --repo <owner>/<repo> --comments` 返回顶级问题对话（Greptile 的摘要评论、分数、CI 机器人）。
- `gh api repos/<owner>/<repo>/pulls/<PR>/comments` 返回内联差异锚定的评审评论——Greptile 在这里发布每个 P0/P1/P2 检测项，**并且这些不包含在 `--comments` 中**。跳过这个调用是代理无声地声明“所有检测项已解决”，而每个内联线程仍然打开。

**监控是 harness 的工作，不是你手写的忙循环。** 使用你的环境提供的任何 PR 活动监控——按收到评审/CI 事件进行反应，或者如果它不推送事件，则按间隔重新检查。每次修复推送后，等待重新触发的评审落地后再判断完成；新的一轮可以重新打开门禁。

**不要手动编辑 `registry.json` 或 `cli-skills/pp-<api-slug>/SKILL.md` 来满足一个检测项**——两者都是由 `[skip ci]` 提交后重新生成的，并且库的 `Fail on changes to generated artifacts` 检查会预先拒绝任何修改它们的 PR。

### 终端状态——然后交回

一旦 PR 稳定变绿，技能的工作就完成了。**不要合并它并且不要轮询等待它合并**——合并到公共库是维护者的手动评审，不是这个技能的，并且（对于分支贡献者）也不是用户的。

读取 `$PUBLISH_CONFIG` 中的 `access` (`jq -r .access "$PUBLISH_CONFIG"`) 来决定下一步做什么：

- **如果 `access` 是 `push`**（维护者/管理员具有推送权限）：应用 `awaiting-maintainer` 标签以指示 PR 已准备好进行手动评审：
  ```bash
  gh pr edit <PR> --repo mvanhorn/printing-press-library --add-label awaiting-maintainer
  ```
- **如果 `access` 是 `fork`**（社区贡献者）：你不能合并或标记上游 PR。一旦变绿，就没有更多要做了。

然后 **报告终端状态并将控制权交还给调用者。** 默认情况下，不要从这个技能提供回退或任何后续菜单——这个决定属于调用发布的人。`printing-press` 管道将其自己的发布后尾作为回退提供；没有 `--from-polish` 的直接人工调用在这里就结束了。

如果 `POLISH_HANDOFF=true`，在 PR 变绿后提供回退作为软尾。这保留了独立的打磨 -> 发布工作流，同时不允许打磨的同一轮 `AskUserQuestion` 回答创建或更新公共库 PR。

通过 `AskUserQuestion` 呈现：

> "PR 已打开：<PR_URL>。运行回退？它将此会话的系统差距（生成器遗漏、评分器错误、技能文档漂移）作为 GitHub 问题呈现给 Printing Press 维护者。每个提交的回退都会为下一个 CLI 提升底线，并且你当前的会话上下文是最新的。"
>
> 1. **不，我完成了**（默认）
> 2. **是，现在运行回退**

如果用户选择是，调用 `/printing-press-retro`。

## 密钥和 PII 保护

在创建 PR 之前，验证没有密钥泄漏到打包的 CLI 中。

**这很重要，因为库仓库是公开的。** PR 中的泄漏 API 密钥是一个安全事件——任何人都可以看到它，即使 PR 后来被关闭了。

### Printing Press 检查的内容（确定性）

生成技能（`/printing-press`）在 Phase 5.6 运行一个精确值扫描，如果用户提供了 API 密钥。在发布运行时，Printing Press 自己的错误应该已经被捕获。但用户可能在生成和发布之间编辑了文件。

### 发布检查的内容

1. **强制二进制扫描：** `cli-printing-press publish package` 扫描已发布的 CLI 和手稿，查找看起来像活着的供应商前缀标记（`sk-or-v1-*`、`sk_live_*`、`ghp_*`、`ghs_*`、`xoxb-*`、`AKIA*` 和类似的）。如果它因检测到供应商前缀标记而失败，则将包视为不可发布。在复制、提交、推送或打开 PR 之前，直到报告的文件：行发现被移除或删除。

2. **如果用户的确切 API 密钥值已知**，在创建 PR 之前扫描打包的树。这捕获了 `/printing-press` Phase 5.6 之后添加的编辑或手稿：
   ```bash
   if [ -n "$API_KEY_VALUE" ] && [ ${#API_KEY_VALUE} -ge 16 ]; then
     if grep -rF "$API_KEY_VALUE" "$PUBLISH_REPO_DIR/library/<category>/<api-slug>" 2>/dev/null; then
       echo "BLOCKING: API key value found in staged publish tree."
       exit 1
     fi
   fi
   ```

3. **如果安装了 `gitleaks` 或 `trufflehog`**，将其作为增强传递在已发布目录上运行：
   ```bash
   if command -v gitleaks >/dev/null 2>&1; then
     gitleaks detect --source "<staging-dir>/library" --no-git --verbose 2>&1
   elif command -v trufflehog >/dev/null 2>&1; then
     trufflehog filesystem "<staging-dir>/library" 2>&1
   fi
   ```
   这些工具使用特定于供应商的模式（Steam 密钥、Stripe 密钥、GitHub 标记），具有低误报率。它们的发现增加了检测器范围，超越了强制底线。在继续之前审查任何发现。

4. **始终执行轻量级结构检查：**
   - 验证已发布目录中不存在 `.env` 文件、`session-state.json` 或带有真实凭据的 `config.toml`
   - 检查 README 示例使用 `"your-key-here"` 占位符，而不是真实值
   - 检查（如果包含）手稿不包含认证标头或 cookie 值

5. **永远不要包含** 在已发布目录中：
   - `.env` 文件
   - `session-state.json`
   - 带有真实凭据的配置文件
   - 未剥离认证标头的 HAR 捕获

如果强制二进制扫描或精确值扫描发现问题，停止。对于外部工具或轻量级结构发现，警告用户并询问是否继续。用户对那些非强制发现做出最终决定。

### PII 模式扫描（强制）

除了上述密钥扫描之外，运行 `printing-press` 技能中定义的 `references/secret-protection.md` 中的 **PII 模式扫描** 步骤。它包含 Tier 1 模式集和扫描循环。这捕获了在实时 dogfood 中捕获的 PII，这些 PII 被散文指南遗漏——电子邮件、真实参会者姓名、账户标识符——在它们发送到公共库仓库之前。

扫描有两个级别：
- **Tier 1（自动静默删除）：** 供应商前缀锚定的载体标记（`Bearer cal_live_*`、`Bearer sk_live_*`、`Bearer ghp_*`、`xoxp-*` 等）。误报率接近零。
- **Tier 2（警告、批量用户提示）：** 通用电子邮件、通用载体标记、首字母大写的姓名模式。自动抑制抑制派生自 API 词汇的“事件类型”、“预订链接”等。

一个预先清理的已发布目录副本保存在 `<staging>.pre-pii-scrub/`，以便用户可以从错误的删除中恢复。

在扫描存在之前，已有两个 PII 泄漏发送到公共库。扫描是散文指南单独无法提供的机械防御层。

## 错误处理

- **`gh` 未认证：** 在步骤 1 中检测，告诉用户运行 `gh auth login`
- **CLI 未找到：** 在步骤 2 中显示可用 CLI，让用户选择
- **验证失败：** 在步骤 4 中显示每个检查结果，停止
- **仓库无法访问：** 在步骤 5 中清晰报告
- **分支创建失败：** `gh repo fork` 可能会因为用户已经有一个不同名称的分支而失败，或者如果组织限制分支。报告错误并建议用户通过 GitHub 网页 UI 手动分支。
- **冲突检查失败：** 如果 `gh pr list` 或 `ls` 命令失败（网络、认证），警告但不要阻止——按不存在冲突继续
- **重命名失败：** 显示 `publish rename --json` 的错误。提供使用不同的限定符重试或放弃。如果发布仓库处于部分状态，使用 `git checkout -- . && git clean -fd` 在重试之前重置
- **分支冲突（没有现有的 PR）：** 在步骤 8 中询问用户（覆盖或时间戳）
- **推送失败：** 对于分支用户，确保他们正在推送他们的分支（origin），而不是上游。报告错误，建议检查 `gh auth status` 和 `git remote -v`
- **跨仓库 PR 创建失败：** 如果 `gh pr create --head user:branch` 因“head not found”而失败，则分支没有被推送到分支。使用 `git ls-remote origin feat/<api-slug>` 进行验证
