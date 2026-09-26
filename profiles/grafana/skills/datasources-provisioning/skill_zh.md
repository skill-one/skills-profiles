## 工作流

### 1. 确定起点：从零开始，还是从现有数据源？

**在其他任何操作之前先问这个问题**（只有当用户已经明确说明时才跳过）：

- **从零开始** — 用户指定插件类型进行配置 → 继续步骤 2。
- **从现有数据源** 在运行中的实例中 → 跳转到 [转换现有数据源](#转换现有数据源)，然后返回步骤 6。

### 2. 解析完整的插件 ID

配置需要规范化的插件 ID (`<org>-<name>-datasource`)，而不是用户可能说的简称。

- 已经是规范化的（包含 `-datasource` 或 `-app`）？直接使用：`yesoreyeram-infinity-datasource`。
- 只有简称（例如 `infinity`、`clickhouse`）？使用 `filter=<keyword>` 搜索目录 API：
  ```bash
  curl -s "https://grafana.com/api/plugins?filter=infinity" \
    | jq -r '.items[] | "\(.slug)\t\(.name)"'
  # → yesoreyeram-infinity-datasource    Infinity
  ```
  多个匹配项 → 显示候选项并询问哪个。

下面的代码片段使用 Infinity (`yesoreyeram-infinity-datasource`) 作为示例 — 将在此处解析的 ID（以及步骤 3 中的版本）替换到每个命令和输出中。

### 3. 解析最新版本

```bash
curl -s "https://grafana.com/api/plugins/yesoreyeram-infinity-datasource" | jq -r '.version'
```

永远不要硬编码版本 — CDN 路径是版本绑定的，过时的版本会返回 404。

### 4. 获取设置模式（主要结构化来源）

```
https://plugins-cdn.grafana.net/<PLUGIN_ID>/<VERSION>/public/plugins/<PLUGIN_ID>/schema/dsconfig.json
```

```bash
ID=yesoreyeram-infinity-datasource
VER=$(curl -s "https://grafana.com/api/plugins/$ID" | jq -r '.version')
curl -sf "https://plugins-cdn.grafana.net/$ID/$VER/public/plugins/$ID/schema/dsconfig.json"
```

该文件符合 **dsconfig** 模式规范 — 解释它的权威来源。不要从记忆中重新推导字段语义（`valueType` 仅涵盖 `string`、`number`、`boolean`、`array`、`object`、`map`、`any`）；当字段不是纯标量时，请参考规范：

- 文本规范：https://raw.githubusercontent.com/grafana/dsconfig/refs/heads/main/dsconfig/schema.md
- 元规范（定义每个 `dsconfig.json` 的格式）：https://raw.githubusercontent.com/grafana/dsconfig/refs/heads/main/dsconfig/schema.json

从每个字段中获取配置所需的信息：`key`（配置键）、`valueType`、`target`（`root` | `jsonData` | `secureJsonData`）和 `validations`（尊重 `allowedValues` 以用于选择器如 `auth_method`）。方向示例（`schemaVersion: "v1"`）：

```json
{
  "pluginType": "yesoreyeram-infinity-datasource",
  "fields": [
    {
      "key": "auth_method",
      "valueType": "string",
      "target": "jsonData",
      "validations": [
        {
          "type": "allowedValues",
          "values": [
            "none",
            "basicAuth",
            "apiKey",
            "bearerToken",
            "oauth2",
            "aws",
            "azureBlob"
          ]
        }
      ]
    }
  ]
}
```

仅选择与用户请求相关的字段（选择的自定义方法 + 连接），而不是所有字段。每个字段的 `description` 告诉你它属于哪种自定义方法。

对于现成的示例配置，获取 `v0alpha1.json`：

```
https://plugins-cdn.grafana.net/<PLUGIN_ID>/<VERSION>/public/plugins/<PLUGIN_ID>/schema/v0alpha1.json
```

```bash
ID=yesoreyeram-infinity-datasource
VER=$(curl -s "https://grafana.com/api/plugins/$ID" | jq -r '.version')
curl -sf "https://plugins-cdn.grafana.net/$ID/$VER/public/plugins/$ID/schema/v0alpha1.json"
```

示例位于 `settingsExamples.examples` 下，按场景键（例如 `apiKey`、`oauth2ClientCredentials`）。每个条目都有一个 `summary`/`description`（场景）和一个 `value` 包含要直接复制到文件中的 `jsonData`/`secureJsonData` 负载：

```bash
# 列出场景，然后拉取一个负载
... | jq -r '.settingsExamples.examples | keys[]'
... | jq '.settingsExamples.examples.apiKey.value'
```

### 5. 未发布模式时的回退

如果 `schema/dsconfig.json` 返回 404（旧插件）：

- 最后手段：**grafana-oss** 技能中的通用结构（§ 数据源配置）也可以告诉用户字段名称是尽力而为的，而不是插件权威的。

> 注意：**grafana-oss** 技能在 `grafana-core` 插件中可用，并且也可以作为独立技能从 https://github.com/grafana/skills 仓库获取

### 6. 根据 `target` 映射每个字段

| `target`         | YAML                                                                  | Terraform (`grafana_data_source`)                                                    |
| ---------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `root`           | 数据源顶层键（`url`、`basicAuth`、`basicAuthUser`）                   | 顶层参数（`url`） / 在 `json_data_encoded` 内部                                      |
| `jsonData`       | 在 `jsonData:` 下                                                     | `json_data_encoded = jsonencode({ … })` 内部的键                                     |
| `secureJsonData` | 在 `secureJsonData:` 下作为 `${ENV_VAR}`                              | `secure_json_data_encoded = jsonencode({ … })` 通过一个 `sensitive` 变量内的键         |

使用每个字段的 `valueType` 作为标量（YAML 中的 `string` 引用，`boolean`→`true`/`false`，`number` 原始）。永远不要内联真实密钥。嵌套对象（`oauth2`、`aws`）和数组（`allowedHosts`、`scopes`）直接映射。

始终设置 `access`（`root` 目标）并将其默认设置为 `proxy` — 查询通过 Grafana 服务器路由（安全默认值）；只有当用户明确要求时才使用 `direct`（浏览器→数据源）。在 Terraform 中，参数是 `access_mode`。

### 7. 询问格式，然后生成文件

**现在问：YAML 还是 Terraform？** 相同字段，不同的输出文件和语法。不要假设："配置 X" 可能意味着任何一种；只有当用户已经指定了格式（"Terraform 用于 X"）时才跳过这个问题。YAML 文件配置是原生、零依赖的路径；Terraform 需要官方的 [`grafana/grafana`](https://registry.terraform.io/providers/grafana/grafana/latest) 提供者。

| 选择               | 生成                                     |
| -------------------- | -------------------------------------------- |
| **YAML 配置文件** | `provisioning/datasources/<name>.yaml`       |
| **Terraform**        | `<name>.tf` (`grafana_data_source` 资源) |

`<name>` 只是文件的 basenmae — 主要是装饰性的，因为两个加载器都会读取目录中的每个文件，而不管文件名如何。默认将其设置为插件名称。

**YAML** → `provisioning/datasources/<name>.yaml`:

```yaml
apiVersion: 1
datasources:
  - name: Infinity # 必须在整个实例中唯一 — 即使是不同的数据源类型也会冲突
    type: yesoreyeram-infinity-datasource # = schema 中的 pluginType
    access: proxy # 始终设置；默认代理（查询通过 Grafana 服务器路由）
    uid: infinity-ds # 也唯一且不可变，以便仪表板可以引用它
    jsonData:
      auth_method: apiKey # 来自 validations.allowedValues 的值
      apiKeyKey: X-API-Key
      apiKeyType: header
      allowedHosts:
        - https://api.example.com
    secureJsonData:
      apiKeyValue: ${API_KEY} # 环境变量引用，永远不会是字面量密钥
    editable: false
```

**Terraform** → `<name>.tf`:

```hcl
variable "api_key" {
  type      = string
  sensitive = true
}

resource "grafana_data_source" "infinity" {
  type        = "yesoreyeram-infinity-datasource"
  name        = "Infinity"
  uid         = "infinity-ds"
  access_mode = "proxy" # 始终设置；默认代理（查询通过 Grafana 服务器路由）

  json_data_encoded = jsonencode({
    auth_method  = "apiKey"
    apiKeyKey    = "X-API-Key"
    apiKeyType   = "header"
    allowedHosts = ["https://api.example.com"]
  })

  secure_json_data_encoded = jsonencode({
    apiKeyValue = var.api_key
  })
}
```

`grafana_data_source` 来自 [`grafana/grafana`](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/data_source) 提供者 — 参数名称的权威参考（`access_mode`、`json_data_encoded`、`secure_json_data_encoded`）。这个文件只是资源；用户需要提供 `required_providers` + `provider "grafana"` 块和凭证。

### 8. 将文件返回给用户

以单个代码块的形式向用户展示完整文件，以便他们复制并粘贴到他们的环境中 — 注意它应该放在哪里：

- **YAML** → `provisioning/datasources/<name>.yaml`（在 Grafana 启动或配置重新加载时应用）。
- **Terraform** → 他们的 Terraform 配置，使用 `terraform apply` 应用。

可选地，告诉他们如何确认应用后是否正常工作：

```bash
curl -s https://grafana.example.com/api/datasources/uid/<uid>/health \
  -H "Authorization: Bearer <token>"
# { "status": "OK" }    → 正常工作
# { "status": "ERROR" } → URL 不可达或认证配置错误
```

或者在 UI 中验证：访问 `<https://grafana.example.com>/connections/datasources/edit/<uid>` 并点击 **Test**。

## 转换现有数据源

要规范已在运行实例中配置的数据源，通过 **Grafana MCP 服务器** ([grafana/mcp-grafana](https://github.com/grafana/mcp-grafana)) 读取其配置。

**前提条件：** Grafana MCP 服务器已连接并启用其 **数据源** 工具集（它包含实例凭证）。**如果不可用，不支持此路径** — 永远不要要求用户在聊天中粘贴 Grafana 令牌。改用从零开始的 Workflow。

1. 使用 MCP 工具查找数据源 — `list_datasources` 浏览，然后 `get_datasource`（通过 `uid` 或 `name`）获取完整配置。
2. 结果直接携带每个**非密钥**字段：`type`、`uid`、`url`、`access`、`basicAuth`、`basicAuthUser` 和完整的 `jsonData` 对象。直接复制它们。
3. **密钥永远不会返回。** `secureJsonFields` 映射列出了设置的密钥名称（例如 `{"apiKeyValue": true}`），但没有它们的值。为每个报告 `true` 的密钥在 `secureJsonData` 中发出 `${ENV_VAR}` 占位符。
4. 与模式（步骤 4）交叉检查以确认密钥名称和 `target` 位置，然后像正常一样继续步骤 6（映射）和步骤 7（生成）。

## 相关

- [grafana-oss](../../grafana-core/grafana-oss/SKILL.md) — 通用数据源 / 仪表板配置结构和方法。
