# /打印机目录

> **已弃用**：此技能已被主 `/printing-press` 技能取代，现在会自动检查内置目录。请使用 `/printing-press <API>`。浏览目录时，请在终端中使用 `cli-printing-press catalog list`。

浏览和安装针对流行 API 的预构建 Go CLI。

## 快速入门

```
/printing-press-catalog
/printing-press-catalog install stripe
/printing-press-catalog search auth
```

## 前置条件

- 已安装 Go 1.26.4 或更高版本
- `cli-printing-press` 二进制文件位于 PATH 上（使用 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 安装）

## 设置

在任何其他命令之前，运行设置合约以验证 `cli-printing-press` 二进制文件是否位于 PATH 上并初始化作用域变量：

<!-- PRESS_SETUP_CONTRACT_START -->
```bash
# min-binary-version: 4.0.0

# 首先推导作用域 — 需要用于本地构建检测
_scope_dir="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
_scope_dir="$(cd "$_scope_dir" && pwd -P)"

# 从 printing-press 仓库内部运行时优先使用本地构建。
_press_repo=false
if [ -x "$_scope_dir/cli-printing-press" ] && [ -d "$_scope_dir/cmd/cli-printing-press" ]; then
  _press_repo=true
  export PATH="$_scope_dir:$PATH"
  echo "使用本地构建: $_scope_dir/cli-printing-press"
elif ! command -v cli-printing-press >/dev/null 2>&1; then
  if [ -x "$HOME/go/bin/cli-printing-press" ]; then
    echo "cli-printing-press 位于 ~/go/bin/cli-printing-press 但不在 PATH 上。"
    echo "将 GOPATH/bin 添加到您的 PATH:  export PATH=\"\$HOME/go/bin:\$PATH\""
  else
    echo "未找到 cli-printing-press 二进制文件。"
    echo "使用以下命令安装:  go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest"
  fi
  return 1 2>/dev/null || exit 1
fi

# 解析并输出代理必须用于后续每个 `cli-printing-press` 调用的绝对路径。上面 `export PATH` 仅影响此单个 Bash 工具调用；后续调用会打开一个新的 shell 并解析 bare `cli-printing-press` 对用户默认 PATH 的解析，其中陈旧的全局路径可能会无声地遮蔽本地构建。代理捕获此标记并将绝对路径替换到后续每个调用中。
if [ "$_press_repo" = "true" ]; then
  PRINTING_PRESS_BIN="$_scope_dir/cli-printing-press"
else
  PRINTING_PRESS_BIN="$(command -v cli-printing-press 2>/dev/null || true)"
fi
echo "PRINTING_PRESS_BIN=$PRINTING_PRESS_BIN"

PRESS_BASE="$(basename "$_scope_dir" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]/-/g; s/^-+//; s/-+$//')"
if [ -z "$PRESS_BASE" ]; then
  PRESS_BASE="workspace"
fi

PRESS_SCOPE="$PRESS_BASE-$(printf '%s' "$_scope_dir" | shasum -a 256 | cut -c1-8)"
PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
PRESS_RUNSTATE="$PRESS_HOME/.runstate/$PRESS_SCOPE"
PRESS_LIBRARY="$PRESS_HOME/library"

mkdir -p "$PRESS_RUNSTATE" "$PRESS_LIBRARY"
```
<!-- PRESS_SETUP_CONTRACT_END -->

运行设置合约后，从标准输出捕获 `PRINTING_PRESS_BIN=<abs-path>` 行。**在此技能中的后续每个 `cli-printing-press ...` 调用都必须使用该绝对路径**（替换值，而不是 `$PRINTING_PRESS_BIN` 字面量标记）— 上面 `export PATH` 仅影响其运行的单个 Bash 工具调用，因此后续调用会打开一个新的 shell，其中 bare `cli-printing-press` 会解析用户默认的 `PATH`，而陈旧的全球路径可能会遮蔽本地构建。

捕获二进制路径后，检查二进制版本兼容性。从此技能的 YAML 前置字段中读取 `min-binary-version` 字段。运行 `<PRINTING_PRESS_BIN> version --json` 并从输出中解析版本。使用 semver 规则将其与 `min-binary-version` 进行比较。如果安装的二进制文件比最低版本旧，请立即停止并告知用户： "cli-printing-press 二进制文件 vX.Y.Z 比最低要求的 vA.B.C 旧。运行 `go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest` 更新。"

生成的 CLI 会发布到 `$PRESS_LIBRARY/` 中，而不是发布到仓库。

## 工作流

### 列出目录（无参数）

当调用时没有参数，将按类别列出所有可用的 CLI。

1. 使用 Glob + Read 读取 catalog/ 中的所有 YAML 文件
2. 解析每个文件的名字、display_name、description、category 字段
3. 按类别分组并显示：

```
可用的 CLI (12 条记录)：

支付：
  stripe - 支付处理和金融基础设施 API
  square - 支付处理和商业 API

认证：
  stytch - 认证和用户管理 API

电子邮件：
  sendgrid - 电子邮件发送和营销 API

通信：
  discord - 聊天和社区平台 API
  twilio - 用于 SMS、语音和消息的通信 API
  front - 客户通信平台 API

开发者工具：
  github - 软件开发平台 API
  digitalocean - 云基础设施和开发者平台 API

项目管理：
  asana - 工作管理和项目跟踪 API

CRM：
  hubspot - CRM 联系人 API

示例：
  petstore - 典型的 OpenAPI 示例

安装任何 CLI: /printing-press-catalog install <名称>
```

### 安装（install <名称>）

当调用时使用 `install <名称>`：

1. 读取 catalog/<名称>.yaml
2. 如果文件不存在，显示错误： "没有目录条目 '<名称>'。运行 /printing-press-catalog 查看可用 CLI。"
3. 从目录条目中提取 spec_url
4. 显示预览： "正在安装 <display_name> CLI 从 <spec_url>"
5. 下载规范并生成：
   ```bash
   CATALOG_TMP_DIR="/tmp/printing-press/catalog"
   mkdir -p "$CATALOG_TMP_DIR"
   SPEC_TMP="$(mktemp "$CATALOG_TMP_DIR/<名称>-spec-XXXXXX.yaml")"
   curl -sL -o "$SPEC_TMP" "<spec_url>"
   OUTPUT_BASE="$PRESS_LIBRARY/<名称>-pp-cli"
   OUTPUT_DIR="$OUTPUT_DIR"
   i=2
   while [ -e "$OUTPUT_DIR" ]; do
     OUTPUT_DIR="${OUTPUT_BASE}-$i"
     i=$((i + 1))
   done
   cli-printing-press generate \
     --spec "$SPEC_TMP" \
     --output "$OUTPUT_DIR" \
     --validate
   ```
7. 如果所有质量门都通过，显示结果：
   ```
   生成了 <名称>-pp-cli，包含 X 个资源。

   尝试：
     cd "$OUTPUT_DIR"
     go install ./cmd/<名称>-pp-cli
     <名称>-pp-cli --help
     <名称>-pp-cli doctor
   ```
8. 如果门未通过，显示错误并建议： "尝试 /printing-press <display_name> API 进行自定义生成，支持重试。"

### 搜索（search <查询>）

当调用时使用 `search <查询>`：

1. 读取 catalog/ 中的所有 YAML 文件
2. 搜索查询的名称、display_name、description 和 category（不区分大小写）
3. 显示匹配条目

## 限制

- 大型 API 规范（Stripe、Discord、GitHub）生成和编译需要 30-60 秒
- 生成的 CLI 每个资源最多 50 个资源 / 20 个端点
- 目录条目指向可能变化的外部 URL
