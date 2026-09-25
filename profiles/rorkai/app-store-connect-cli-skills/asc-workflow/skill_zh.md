# asc 工作流

当您需要在 CLI 中使用行式自动化时，请使用以下命令：

- `asc workflow validate`
- `asc workflow list`
- `asc workflow run`

工作流是存储在仓库本地的自动化文件。它们运行受信任的 shell 命令，将步骤输出流到 stderr，并将 stdout 保留为机器可读的 JSON 格式。

## 命令发现

始终使用以下命令验证标志：

```bash
asc workflow --help
asc workflow validate --help
asc workflow list --help
asc workflow run --help
```

## 端到端流程

1.  编写 `.asc/workflow.json` 文件。
2.  验证结构和引用：

```bash
asc workflow validate
```

3.  发现公共工作流：

```bash
asc workflow list
asc workflow list --all
```

4.  预览执行：

```bash
asc workflow run --dry-run beta BUILD_ID:123456789 GROUP_ID:abcdef
```

5.  执行：

```bash
asc workflow run beta BUILD_ID:123456789 GROUP_ID:abcdef
```

6.  如果可恢复的运行失败，请使用 JSON 结果中的运行 ID 继续执行：

```bash
asc workflow run release --resume "release-20260312T120000Z-deadbeef"
```

不要使用 `--resume` 传递额外的 `KEY:VALUE` 参数；保存的工作流文件、参数和持久化输出将被重复使用。

## 文件位置和格式

- 默认路径：`.asc/workflow.json`
- 覆盖路径：`asc workflow run --file ./path/to/workflow.json <name>`
- 支持 JSONC 注释。
- 顶层钩子：`before_all`、`after_all`、`error`
- 工作流键：`description`、`private`、`env`、`steps`
- 步骤形式：
  - 字符串简写：`"echo hello"`
  - `run` shell 命令
  - `workflow` 子工作流调用
  - `name` 标签
  - `if` 条件变量名
  - `with` 工作流调用步骤的环境覆盖
  - `outputs` 映射，用于从命名运行步骤中提取 JSON stdout
  - `retry` 固定延迟重试策略，用于 `run` 步骤
  - `timeout` 每个 `run` 步骤的正向尝试持续时间

## 输出

运行步骤可以声明输出。命令必须在 stdout 上发出 JSON，因此对于产生输出的 `asc` 命令，请传递 `--output json`。

输出引用使用：

```text
${steps.step_name.OUTPUT_NAME}
```

规则：

- 声明 `outputs` 的步骤必须具有参考安全的 `name`。
- 输出允许在 `run` 步骤上，不允许在工作流调用步骤上。
- 产生输出的名称必须在可以一起在同一运行图中执行的工作流中唯一。
- 持久化输出存储在工作流运行状态中，因此不要将密钥映射到输出。

## 有界重试和超时

仅对您已确定可以重复的命令添加重试。运行器不会自行分类命令或重试变更。

```json
{
  "name": "resolve_build",
  "run": "asc builds info --app $APP_ID --latest --platform IOS --output json",
  "retry": {
    "max_attempts": 3,
    "delay": "5s"
  },
  "timeout": "2m"
}
```

`retry.max_attempts` 计数第一次尝试，必须介于 2 和 100 之间。重试延迟和超时必须为正持续时间，且不超过 24 小时。这两个字段仅适用于 `run` 步骤，不适用于工作流调用或生命周期钩子。

没有重试的超时是终结性的，因为命令可能已远程完成。配对重试和超时是明确表示可以安全尝试的信号。继续需要成功的检查点或启用了重试的失败步骤；输出提取失败无法继续。

## 运行时参数

`asc workflow run <name> [KEY:VALUE ...]` 支持两种分隔符：

```bash
asc workflow run beta VERSION:2.1.0
asc workflow run beta VERSION=2.1.0
```

重复的键以最后写入者胜出。在 shell 命令中，通过 shell 扩展引用参数，如 `$VERSION`。

## 环境优先级

主工作流运行：

```text
definition.env < workflow.env < CLI 参数
```

使用 `with` 的子工作流调用：

```text
sub-workflow 环境变量 < 调用者环境变量和参数 < 步骤 with
```

## 条件语句

向步骤添加 `"if": "VAR_NAME"`。真值是 `1`、`true`、`yes`、`y` 和 `on`，不区分大小写。查找首先检查合并的工作流环境/参数，然后处理环境。

## 示例工作流

```json
{
  "env": {
    "APP_ID": "123456789",
    "VERSION": "1.0.0",
    "GROUP_ID": ""
  },
  "before_all": "asc auth status",
  "after_all": "echo workflow_done",
  "error": "echo workflow_failed",
  "workflows": {
    "beta": {
      "description": "解析最新构建并将其分发到 TestFlight",
      "steps": [
        {
          "name": "resolve_build",
          "run": "asc builds info --app $APP_ID --latest --platform IOS --output json",
          "outputs": {
            "BUILD_ID": "$.data.id"
          }
        },
        {
          "name": "list_groups",
          "run": "asc testflight groups list --app $APP_ID --limit 20 --output json"
        },
        {
          "name": "add_build_to_group",
          "if": "GROUP_ID",
          "run": "asc builds add-groups --build-id ${steps.resolve_build.BUILD_ID} --group $GROUP_ID"
        }
      ]
    },
    "release": {
      "description": "验证、准备和提交 App Store 版本",
      "steps": [
        {
          "name": "validate",
          "run": "asc validate --app $APP_ID --version $VERSION --platform IOS --output json"
        },
        {
          "name": "stage",
          "run": "asc release stage --app $APP_ID --version $VERSION --build-id $BUILD_ID --metadata-dir ./metadata/version/$VERSION --confirm --output json"
        },
        {
          "name": "submit",
          "if": "SUBMIT_FOR_REVIEW",
          "run": "asc review submit --app $APP_ID --version $VERSION --build-id $BUILD_ID --confirm --output json"
        }
      ]
    },
    "publish-appstore": {
      "description": "高级上传和 App Store 审核提交",
      "steps": [
        {
          "name": "publish",
          "run": "asc publish appstore --app $APP_ID --ipa ./build/MyApp.ipa --version $VERSION --wait --submit --confirm --output json"
        }
      ]
    }
  }
}
```

## 有用的调用

```bash
asc workflow validate | jq -e '.valid == true'
asc workflow list --pretty
asc workflow list --all --pretty
asc workflow run --dry-run beta BUILD_ID:123 GROUP_ID:grp_abc
asc workflow run beta BUILD_ID:123 GROUP_ID:grp_abc | jq -e '.status == "ok"'
asc workflow run release BUILD_ID:123 SUBMIT_FOR_REVIEW:true
asc workflow run release --resume "release-20260312T120000Z-deadbeef"
```

## 安全规则

- 将 `.asc/workflow.json` 像代码一样对待；仅运行受信任的工作流文件。
- 避免从包含密钥的不受信任的 PR 中运行工作流。
- 将工作流文件存储在版本控制中。
- 首先验证，然后预览，最后运行。
- 对可变步骤使用显式 ID 和 `--confirm`。
- 使用 `asc validate`、`asc release stage`、`asc review submit` 和 `asc publish appstore`；不要使用已移除的提交命令。
