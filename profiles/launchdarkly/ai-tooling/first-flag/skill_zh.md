# 创建第一个功能标志

SDK 已连接。现在帮助用户创建他们的第一个功能标志并端到端查看其工作情况。

这项技能嵌套在 [LaunchDarkly 入门](../SKILL.md) 之下；父级 **步骤 6** 是 **第一个标志**。**优先级：** [应用代码更改](../sdk-install/apply/SKILL.md)。

**可选 -- 标志创建技能已安装：** 如果会话中可用 [github.com/launchdarkly/ai-tooling](https://github.com/launchdarkly/ai-tooling) 的 **`launchdarkly-flag-create`** 技能（使用 `npx skills add launchdarkly/ai-tooling --skill launchdarkly-flag-create -y --agent <agent>` 安装），您可以使用它来 **创建标志** 并 **选择与仓库匹配的评估代码**。您仍然必须完成 **默认关闭 -> 验证关闭 -> 切换开启 -> 验证开启**（以下步骤 3-5）。**不要** 要求该技能：当它缺失时，此页面将作为完整的回退，或者 MCP 流程与用户的设置冲突时。

## 安全：凭证处理

**永远不要将字面量令牌值直接替换到命令中。** 使用环境变量引用：

- Shell 命令：`$LAUNCHDARKLY_ACCESS_TOKEN`（由 Shell 扩展，不在 `ps` 输出中可见）
- 在您的会话中设置变量：`export LAUNCHDARKLY_ACCESS_TOKEN=<your-token>`

这可以防止令牌出现在进程列表、Shell 历史记录和屏幕录制中。

## 步骤 0：参考 SDK 标志键指南

在创建标志或连接评估代码之前，请检查下表中的 [SDK 的标志键行为](#flag-key-behavior-by-sdk)。某些 SDK 在在应用程序代码中暴露标志键之前会转换标志键（例如 React SDK 将 kebab-case 键 camelCases 为 `my-first-flag` → `myFirstFlag`）。在 LaunchDarkly 中创建的标志键、SDK/框架配置以及代码中引用的键必须一致。

- **如果 SDK 转换键**（例如 React `useFlags()` camelCases `my-first-flag` → `myFirstFlag`）：使用 **转换后的** 键生成评估代码。LaunchDarkly 中的标志键保持不变（kebab-case 是惯例）。
- **如果 SDK 保留键原样**（大多数服务器端 SDK）：在代码中使用 LaunchDarkly 标志键的精确字符串。
- **如果 SDK 支持两种模式**（例如 React 允许通过提供程序选项禁用 camelCase）：确定项目使用哪种模式（检查现有代码或提供程序配置），然后生成匹配的代码。

### SDK 的标志键行为

| SDK | 键转换 | `my-first-flag` 的代码键 | 备注 |
|-----|--------|--------------------------|------|
| React Web (`useFlags()`) | 默认 camelCase | `myFirstFlag` | `reactOptions: { useCamelCaseFlagKeys: false }` 在提供程序上禁用此功能 |
| React Native (`useFlags()`) | 默认 camelCase | `myFirstFlag` | 同样的 `reactOptions` 覆盖可用 |
| Vue (`useLDFlag()`) | 无（传递原始键） | `'my-first-flag'` | |
| JavaScript 浏览器 | 无 | `'my-first-flag'` | |
| Node.js 服务器 | 无 | `'my-first-flag'` | |
| Python 服务器 | 无 | `'my-first-flag'` | |
| Go 服务器 | 无 | `"my-first-flag"` | |
| Java 服务器 | 无 | `"my-first-flag"` | |
| .NET 服务器 | 无 | `"my-first-flag"` | |
| Ruby 服务器 | 无 | `'my-first-flag'` | |
| Swift/iOS | 无 | `"my-first-flag"` | |
| Android | 无 | `"my-first-flag"` | |
| Flutter | 无 | `'my-first-flag'` | |

在以下步骤 2 中连接评估代码时，如果 SDK 应用转换，请使用 **代码键** 列的值，而不是原始 LaunchDarkly 键。

## 步骤 1：创建标志

**REST / curl 认证：** 将 `$LAUNCHDARKLY_ACCESS_TOKEN` 作为 `Authorization` 头的值（LaunchDarkly 使用原始令牌，没有 `Bearer` 前缀）。Shell 扩展该变量，但不会记录它。

### 通过 MCP（推荐）

如果 LaunchDarkly MCP 服务器可用，请使用 `create-feature-flag`（或您的服务器提供的等效标志创建工具）：

- **键**：`my-first-flag`（或与用户项目相关的名称）
- **名称**："我的第一个标志"
- **类型**：`boolean`
- **变体**：`true` / `false`
- **临时**：`true`

### 通过 LaunchDarkly API

```bash
curl -s -X POST \
  "https://app.launchdarkly.com/api/v2/flags/PROJECT_KEY" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Flag",
    "key": "my-first-flag",
    "kind": "boolean",
    "variations": [
      {"value": true},
      {"value": false}
    ],
    "temporary": true
  }'
```

### 通过 ldcli

```bash
ldcli flags create \
  --access-token "$LAUNCHDARKLY_ACCESS_TOKEN" \
  --project PROJECT_KEY \
  --data '{"name": "My First Flag", "key": "my-first-flag", "kind": "boolean", "temporary": true}'
```

创建后，标志将开始 **目标定位关闭**，向所有人提供关闭变体（`false`）。当项目键已知时，将用户链接到标志的仪表板页面：**`https://app.launchdarkly.com/projects/{projectKey}/flags/my-first-flag`**（替换为实际的项目键）。

## 步骤 2：添加标志评估代码

在应用程序中添加代码来评估标志。将此代码放置在用户功能合适的位置。

### 服务器端示例

```javascript
// Node.js (@launchdarkly/node-server-sdk) -- ldClient 是初始化服务器客户端后 waitForInitialization 的
const context = { kind: 'user', key: 'example-user-key', name: 'Example User' };
const showFeature = await ldClient.boolVariation('my-first-flag', context, false);

if (showFeature) {
  console.log('Feature is ON');
} else {
  console.log('Feature is OFF');
}
```

```python
# Python (launchdarkly-server-sdk) -- client 是 set_config 后的 ldclient.get()
from ldclient import Context

context = Context.builder("example-user-key").name("Example User").build()
show_feature = client.variation("my-first-flag", context, False)

if show_feature:
    print("Feature is ON")
else:
    print("Feature is OFF")
```

```go
// Go
context := ldcontext.NewBuilder("example-user-key").Name("Example User").Build()
showFeature, _ := ldClient.BoolVariation("my-first-flag", context, false)

if showFeature {
    fmt.Println("Feature is ON")
} else {
    fmt.Println("Feature is OFF")
}
```

### 客户端端示例

```tsx
// React — useFlags() camelCases 键："my-first-flag" → myFirstFlag（见步骤 0 表格）
import { useFlags } from 'launchdarkly-react-client-sdk';

function MyComponent() {
  const { myFirstFlag } = useFlags();

  return (
    <div>
      {myFirstFlag ? <p>Feature is ON</p> : <p>Feature is OFF</p>}
    </div>
  );
}
```

React SDK 的 `useFlags()` 钩子默认将 kebab-case 键 camelCases（例如 `my-first-flag` 变为 `myFirstFlag`）。如果项目通过在提供程序上设置 `reactOptions: { useCamelCaseFlagKeys: false }` 禁用此功能，请使用原始键字符串。在选择使用哪种形式之前，始终检查项目的提供程序配置——请参阅上表中的 [标志键行为表](#flag-key-behavior-by-sdk)。

## 步骤 3：验证默认值

在目标定位关闭的情况下，标志应评估为 `false`。运行应用程序并确认：

```
Feature is OFF
```

## 步骤 4：切换标志开启

### 通过 MCP

LaunchDarkly MCP 服务器公开 **`update-feature-flag`**（JSON 补丁），而不是名为 `toggle-flag` 的工具——使用您的 MCP 服务器列出的工具名称。

**最简单的路径：** 当您只需要开启标志一次时，请优先使用 **ldcli** 或以下 LaunchDarkly API 块。

**如果使用 `update-feature-flag`：** 使用 `projectKey`、`featureFlagKey` 和 `PatchWithComment.patch` 作为 JSON 补丁数组调用它。通常使用对环境 `on` 字段的 `replace` 操作来将标志 **开启**（如果需要，请从您的帐户的 `get-feature-flag` 确认确切路径）：

```json
{
  "projectKey": "PROJECT_KEY",
  "featureFlagKey": "my-first-flag",
  "PatchWithComment": {
    "patch": [
      {
        "op": "replace",
        "path": "/environments/ENVIRONMENT_KEY/on",
        "value": true
      }
    ],
    "comment": "Onboarding: turn on my-first-flag"
  }
}
```

将 `ENVIRONMENT_KEY` 替换为您要定位的环境的键（例如 `test`、`production`）。

### 通过 LaunchDarkly API

```bash
curl -s -X PATCH \
  "https://app.launchdarkly.com/api/v2/flags/PROJECT_KEY/my-first-flag" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
  -H "Content-Type: application/json; domain-model=launchdarkly.semanticpatch" \
  -d '{
    "environmentKey": "ENVIRONMENT_KEY",
    "instructions": [
      {"kind": "turnFlagOn"}
    ]
  }'
```

### 通过 ldcli

```bash
ldcli flags toggle-on \
  --access-token "$LAUNCHDARKLY_ACCESS_TOKEN" \
  --project PROJECT_KEY \
  --environment ENVIRONMENT_KEY \
  --flag my-first-flag
```

## 步骤 5：验证切换

切换标志开启后，应用程序现在应显示：

```
Feature is ON
```

对于使用流式传输（默认）的服务器端 SDK，更改应在几秒钟内反映出来。对于客户端端 SDK，更改将在下次页面加载或 SDK 轮询更新时出现。

## 步骤 6：添加交互式演示

现在标志可以工作了，添加一个 **可见的、可交互的元素**，以便用户可以看到标志的实际效果——而不仅仅是控制台日志。这会创造一个“哇”的时刻，并给用户一个他们可以向他人展示的具体证明点。

**根据您检测到的内容选择合适的演示：**

| 应用类型 | 添加什么 | 用户体验 |
|----------|----------|----------|
| **前端（React、Vue、SPA）** | 一个横幅、徽章或按钮，由标志控制 | 在仪表板中切换标志 → 刷新页面 → 元素出现/消失 |
| **后端 API（Node、Python、Go 等）** | 一个 `/launchdarkly-demo` 端点，返回标志状态作为 JSON | `curl` 端点 → 切换标志 → 再次 `curl` → 响应更改 |
| **全栈（Next.js SSR、Rails 等）** | 两者：一个 API 端点 + 一个显示标志状态的 UI 元素 | 切换标志 → API 和 UI 都反映更改 |
| **CLI / 脚本** | 一个 `--feature-demo` 标志或不同的输出模式 | 运行脚本 → 切换标志 → 再次运行 → 输出更改 |

### 前端演示示例（React）

添加一个在标志开启时明显可见的组件或元素：

```tsx
// 添加到现有页面组件
import { useFlags } from 'launchdarkly-react-client-sdk';

function FeatureFlagDemo() {
  const { myFirstFlag } = useFlags();

  if (!myFirstFlag) return null;

  return (
    <div style={{
      padding: '12px 20px',
      backgroundColor: '#405BFF',
      color: 'white',
      borderRadius: '8px',
      margin: '16px 0',
      fontWeight: 500
    }}>
      LaunchDarkly 正在运行——此横幅受功能标志控制
    </div>
  );
}
```

将其放置在显眼的位置（例如，在主页面顶部或仪表板/标题区域）。

### 后端演示示例（Node.js/Express）

添加一个返回标志状态的端点：

```javascript
// 添加到您的 Express 应用（或等效其他框架）
app.get('/launchdarkly-demo', async (req, res) => {
  const context = { kind: 'user', key: 'demo-user' };
  const flagValue = await ldClient.boolVariation('my-first-flag', context, false);
  
  res.json({
    flag: 'my-first-flag',
    enabled: flagValue,
    message: flagValue 
      ? 'LaunchDarkly 正在运行——标志是 ON'
      : 'LaunchDarkly 正在运行——标志是 OFF'
  });
});
```

告诉用户使用：`curl http://localhost:PORT/launchdarkly-demo`

### 后端演示示例（Python/Flask）

```python
@app.route('/launchdarkly-demo')
def launchdarkly_demo():
    context = Context.builder("demo-user").build()
    flag_value = ld_client.variation("my-first-flag", context, False)
    
    return jsonify({
        "flag": "my-first-flag",
        "enabled": flag_value,
        "message": "LaunchDarkly 正在运行——标志是 ON" if flag_value 
                   else "LaunchDarkly 正在运行——标志是 OFF"
    })
```

### 全栈演示

对于同时具有服务器和客户端的应用（例如 Next.js、Remix、Rails 等）：

1. 添加 API 端点（上述后端示例）
2. 添加一个 UI 组件，它要么调用端点，要么直接使用客户端 SDK
3. 用户可以验证两者都起作用

### 指导方针

1. **匹配现有模式**——使用与应用程序其余部分相同的路由样式、组件约定和代码样式
2. **使其明显**——使用颜色、位置或文本明确指示这是 LaunchDarkly 演示
3. **保持可移除**——添加类似 `// LaunchDarkly 演示 - 可以安全删除` 的简短注释，以便用户知道他们可以稍后删除它（或将其作为模板保留）
4. **不要过度设计**——这是一个演示，不是生产功能；几行代码就足够理想

### 引导用户完成

添加演示元素后：

1. 告诉用户您添加了什么以及如何查看它（URL、页面位置、命令）
2. 让他们验证它显示当前的标志状态
3. 让他们切换仪表板中的标志（提供深度链接：`https://app.launchdarkly.com/projects/{projectKey}/flags/my-first-flag`）
4. 让他们刷新/重新运行以查看更改
5. 庆祝成功的集成

## 恭喜

用户已成功：

1. 安装 LaunchDarkly SDK
2. 将其连接到 LaunchDarkly
3. 创建功能标志
4. 在代码中评估它
5. 切换它并看到结果
6. 添加一个他们可以向他人展示的交互式演示

这是“证明点”时刻——用户有一个可以实时切换的功能标志。演示元素使其具体化和可分享。

**鼓励下一个技能：** 建议他们安装或启用 [github.com/launchdarkly/ai-tooling](https://github.com/launchdarkly/ai-tooling) 的 **`launchdarkly-flag-create`** 技能（使用 `npx skills add launchdarkly/ai-tooling --skill launchdarkly-flag-create -y --agent <agent>` 安装），以便未来的工作——创建与仓库约定匹配的标志、包装功能以及验证接线——有一个专门的剧本。如果他们不确定如何添加，请提供帮助。

## 错误处理

### 认证错误

如果任何步骤返回 **401** 或 **403**：

**D9 -- 阻塞性：** 现在调用您的结构化问题工具。
- 问题："我收到一个认证错误（[具体状态码和消息]）。这需要您的操作来解决——我不能自动重试。"
- 选项：
  - "我将重新认证——运行 ldcli login 或刷新我的令牌"
  - "让我检查我的访问令牌并重试"
  - "我没有帐户——帮助我注册"
  - "项目或环境不存在——帮助我创建一个"
- 停止。不要将问题作为文本写入。不要自动重试认证错误——它们始终需要用户操作。不要继续，直到用户选择一个选项。

### 其他错误

对于非认证错误（标志创建失败、SDK 键不匹配、标志返回回退值等），使用错误输出、应用程序日志和对项目的理解来诊断问题。

**建议下一步：**

- **安装** **`launchdarkly-flag-create`** 从 [github.com/launchdarkly/ai-tooling](https://github.com/launchdarkly/ai-tooling) 如果它尚未可用——此入门流程仅涵盖第一个布尔标志；该技能指导与现有代码模式对齐的真实世界标志创建（需要 LaunchDarkly MCP，如该技能的先决条件所述）。
- 使用 **`launchdarkly-flag-targeting`** 从同一分发版设置百分比发布和定位规则
- 阅读 [LaunchDarkly 文档](https://docs.launchdarkly.com) 了解高级主题，如上下文、实验和指标

---

**完成后，继续：** [入门摘要](../references/1.8-summary.md) 和 [编辑器规则和技能](../references/1.9-editor-rules.md)（默认在父入门技能中继续——**不是** MCP 设置，而是步骤 4）。对于 MCP 安装或故障排除，使用 [mcp-configure](../mcp-configure/SKILL.md) 和 [MCP 配置模板](../mcp-configure/references/mcp-config-templates.md)。
