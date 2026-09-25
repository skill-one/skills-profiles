# /printing-press-import

将公共库中的已发布CLI（来自 [`mvanhorn/printing-press-library`](https://github.com/mvanhorn/printing-press-library)）导入内部库 `$PRESS_LIBRARY/` 中，使其与生成器产生的形式相匹配。手稿文件将随同导入。

```bash
/printing-press-import notion
/printing-press-import cal.com
/printing-press-import allrecipes --from-clone ~/Code/printing-press-library
```

内部库是工作副本；公共库是持久的工件。导入后，CLI即可用于精炼、压印或重新发布——发布步骤将重新应用模块路径重写。

## 运行时机

- 公共库中存在本地没有的CLI
- 内部副本已损坏、丢失或不同步
- 在对已发布的CLI运行精炼之前需要干净的基线

如果用户请求精炼CLI并提到“在/来自公共库”或“来自仓库”，建议先运行此技能。

## 配置

```bash
PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
PRESS_LIBRARY="$PRESS_HOME/library"
PRESS_MANUSCRIPTS="$PRESS_HOME/manuscripts"
SCRIPTS_DIR="$(dirname "${BASH_SOURCE[0]:-.}")/references"

if ! command -v go >/dev/null 2>&1; then
  echo ""
  echo "[setup-error] 未找到Go工具链。"
  echo ""
  echo "此Printing Press流程运行基于Go的构建或验证命令。"
  echo "从 https://go.dev/dl/ 安装Go 1.26.6或更高版本，然后使用以下命令验证："
  echo "  go version"
  echo "然后重新运行此技能。"
  echo ""
  return 1 2>/dev/null || exit 1
fi

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
    echo "[setup-error] Printing Press工作区卷的磁盘空间严重不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_FAIL_KB=$_pp_disk_fail_kb"
    echo "释放磁盘空间或将PRINTING_PRESS_HOME设置为具有更多空间的卷，然后重新运行此技能。"
    echo ""
    return 1
  fi

  if [ "$_pp_disk_avail_kb" -lt "$_pp_disk_warn_kb" ]; then
    echo ""
    echo "[low-disk] Printing Press工作区卷的可用空间不足。"
    echo "PRESS_DISK_PATH=$_pp_disk_path"
    echo "PRESS_DISK_AVAIL_KB=$_pp_disk_avail_kb"
    echo "PRESS_DISK_WARN_KB=$_pp_disk_warn_kb"
    echo "此流程可能需要几个GiB的生成文件、Go构建缓存、模块下载或仓库克隆。"
    echo ""
  fi
}
_pp_check_disk_space || { return 1 2>/dev/null || exit 1; }
```

四个参考脚本位于此 `SKILL.md` 文件下的 `references/` 目录中：

- `import-fetch.sh <library-path> <staging> [--clone <path>]`
- `import-backup.sh <api-slug>`（在标准输出上打印zip路径）
- `import-rewrite.sh <staging> <api-slug>`
- `import-place.sh <staging> <api-slug>`

如果配置过程中输出 `[low-disk]`，向用户显示建议，除非同时输出 `[setup-error]`。`[low-disk]` 表示此运行可能需要几个GiB用于仓库克隆、暂存文件、备份、Go构建缓存或模块下载。

## 第一阶段 — 解析CLI

参数可以是任何自然形式：API缩写（`notion`）、品牌名称（`cal.com`）、旧的CLI名称（`notion-pp-cli`）或足够接近（`Allrecipes`）。通过公共库的 `registry.json` 进行解析——它包含每个条目的 `name`、`category`、`api`、`description` 和 `path`，只需一次获取即可。

```bash
REGISTRY=$(mktemp)
gh api -H "Accept: application/vnd.github.v3.raw" \
  repos/mvanhorn/printing-press-library/contents/registry.json \
  > "$REGISTRY"
```

按以下顺序匹配：

1. **精确 `name` 匹配** — `jq --arg q "$ARG" '.entries[] | select(.name == $q)' "$REGISTRY"`
2. **标准化精确** — 去除 `-pp-cli` 后缀，转换为小写，点→连字符，然后精确匹配
3. **在 `name` 或 `description` 上的子字符串** — 不区分大小写的包含

```bash
# 精确匹配：
jq --arg q "$ARG" '.entries[] | select(.name == $q)' "$REGISTRY"

# 标准化精确（在 $ARG2 = 转换为小写、点→连字符、后缀去除后）：
jq --arg q "$ARG2" '.entries[] | select(.name == $q)' "$REGISTRY"

# 模糊匹配（在 `name` 或 `description` 上的子字符串）：
jq --arg q "$ARG2" '.entries[]
  | select((.name | ascii_downcase | contains($q | ascii_downcase))
        or (.description | ascii_downcase | contains($q | ascii_downcase)))
' "$REGISTRY"
```

如果匹配到一个：使用它。如果有多个：通过 `AskUserQuestion` 向用户最多显示4个，显示每个候选的 `name` + `description`。如果为零：告诉用户公共库中没有该CLI。

匹配的条目会给你所有需要的信息：
- 从 `.path` 获取 `LIB_PATH`（例如，`library/productivity/cal-com`）
- 从 `.name` 获取 `API_SLUG`
- 从 `.category` 获取 `CATEGORY`

**不要加载整个文件** 在推理候选时。上述字段足够；如果你确实需要更多，CLI的每个手稿文件只是 `<LIB_PATH>/manifest.json`，描述信息可以通过相同的方式获取（`gh api -H "Accept: ... raw" .../manifest.json | jq -r '.description'`）。

## 第二阶段 — 决定是否覆盖

检查内部库是否已经存在此CLI：

```bash
LIB_TARGET="$PRESS_LIBRARY/$API_SLUG"
MAN_TARGET="$PRESS_MANUSCRIPTS/$API_SLUG"
```

**如果两者都不存在**：直接导入——继续到第三阶段。

**如果任一存在**：从双方读取来源信息以决定是否覆盖。不要读取整个 `.printing-press.json` 文件——只拉取相关的字段：

```bash
# 内部来源（如果存在）：
jq '{run_id, generated_at, printing_press_version, spec_checksum}' \
  "$LIB_TARGET/.printing-press.json" 2>/dev/null

# 公共来源（一次性通过原始方式）：
gh api -H "Accept: application/vnd.github.v3.raw" \
  repos/mvanhorn/printing-press-library/contents/$LIB_PATH/.printing-press.json \
  | jq '{run_id, generated_at, printing_press_version, spec_checksum}'
```

进行差异分析：

- **相同的 `run_id`** — 公共与内部是相同的版本。可能是无操作；在覆盖前询问。如果用户仍要导入（例如，从损坏的内部副本恢复），则继续。
- **公共 `generated_at` 更新** — 公共有内部没有的更改。导入是安全的；询问用户确认。
- **内部 `generated_at` 更新** — 内部有公共没有的工作（进行中的精炼、手动修复）。导入会覆盖这些。停止并显示给用户——他们可能需要先发布内部更改。
- **任一侧缺少 `.printing-press.json`** — 更旧或手动导入。询问用户。

当用户确认覆盖时，第三阶段的备份步骤会捕获当前的内部状态。

## 第三阶段 — 导入

```bash
STAGING=$(mktemp -d)

# 获取（远程，除非 --from-clone 被传递）
if [[ -n "${CLONE_PATH:-}" ]]; then
  bash "$SCRIPTS_DIR/import-fetch.sh" "$LIB_PATH" "$STAGING" --clone "$CLONE_PATH"
else
  bash "$SCRIPTS_DIR/import-fetch.sh" "$LIB_PATH" "$STAGING"
fi

# 备份如果任何内容将被覆盖。在标准输出上打印zip路径。
if [[ -d "$LIB_TARGET" || -d "$MAN_TARGET" ]]; then
  BACKUP_ZIP=$(bash "$SCRIPTS_DIR/import-backup.sh" "$API_SLUG")
  echo "已备份到: $BACKUP_ZIP"
fi

# 逆转发布步骤的模块路径重写。
bash "$SCRIPTS_DIR/import-rewrite.sh" "$STAGING" "$API_SLUG"

# 原子移动暂存到目标位置。
bash "$SCRIPTS_DIR/import-place.sh" "$STAGING" "$API_SLUG"
```

## 第四阶段 — 验证内部一致性

移动后，确认导入的CLI可以构建且结构完整。将任何失败视为实际问题——不要掩盖它。

```bash
cd "$LIB_TARGET"

# 模块路径是本地形式
grep -q "^module ${API_SLUG}-pp-cli\$" go.mod \
  || { echo "FAIL: go.mod 仍指向公共模块路径"; exit 1; }

# 没有公共模块路径泄漏到源代码
if grep -rq "github.com/mvanhorn/printing-press-library/library" \
   --include='*.go' --include='*.yaml' --include='*.yml' .; then
  echo "FAIL: 源代码仍引用公共模块路径"
  exit 1
fi

# 构建
go build ./... \
  || { echo "FAIL: go build"; exit 1; }

# Doctor（自检）
make doctor 2>/dev/null \
  || ./bin/${API_SLUG}-pp-cli doctor 2>/dev/null \
  || true   # 尽力而为；并非所有CLI都以相同方式配置 doctor
```

报告导入结果：

- 源路径（来自注册表：`<category>/<api-slug>`）
- 运行ID（来自 `.printing-press.json`）
- 放置的手稿运行ID（数量+名称）
- 备份zip路径（如果有）
- 构建状态

## 精炼侧提示

如果用户请求导入是由精炼请求触发的（例如，他们提到“在公共库中精炼 notion”），建议：

```
已导入 $API_SLUG。要精炼：/printing-press-polish $API_SLUG
```

精炼技能作用于内部库，因此导入后再精炼是从已发布CLI开始的正确流程。
