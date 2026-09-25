<!-- adk-managed-skill -->

# 预览 LWC 运行时 — 本地开发 + DOM 检查

指导代理完成两个通常一起运行的顺序任务：

1. **使用 Salesforce CLI 启动 Lightning 预览会话**，以便 LWC 应用或组件在本地开发环境中渲染。
2. **导航到该预览 URL 并提取运行时 DOM 子树**，以便代理（或用户）可以推断实际渲染了什么内容。

预览是 DOM 检查的前提条件。请保持此顺序。

## 何时使用此技能

- 用户希望在部署之前（`sf lightning dev app` / `sf lightning dev component`）在本地预览 LWC 应用或组件。
- 用户需要特定组件在运行时的渲染 HTML 子树——用于差异比较、截图管道或推断阴影 DOM。
- 用户询问为什么模板内容“不在 DOM 中”——这几乎总是与阴影 DOM 相关的误解，在步骤 2 中处理。

## 前提条件

- 已安装 Salesforce CLI (`sf`)。使用 `sf version` 进行检查。
- 已安装 `@salesforce/plugin-lightning-dev`。使用 `sf plugins` 进行检查。
- 已认证的组织（`sf org list` 显示至少有一个连接的组织）。
- 对于 DOM 提取：代理框架中可用浏览器自动化（Playwright、Puppeteer、Chrome DevTools Protocol——无论已配置什么）。

---

## 步骤 1 — 启动 Lightning 预览

询问用户（或从请求中推断）范围是 **应用** 还是 **组件**。

### 1a. 验证工具链

询问用户（或从请求中推断）预览应针对的组织别名。使用该别名运行捆绑的验证脚本，并显示其发出的任何错误——不要在文本中重新调用 `sf version` / `sf plugins` / `sf org display`。该脚本检查 CLI 的存在、`@salesforce/plugin-lightning-dev` 的安装，以及特定目标别名是否已认证和连接，并在失败时以可操作的错误消息退出非零：

```bash
"<skill_dir>/scripts/verify-toolchain.sh" <orgAlias>
```

如果它报告目标别名未认证或未连接，请指导用户到
[启用本地开发](https://developer.salesforce.com/docs/platform/lwc/guide/get-started-test-components.html#enable-local-dev)
并让他们运行 `sf org login web --alias <orgAlias>`，然后在继续之前重新运行验证脚本。

### 1b. 读取子命令的标志

```bash
# 对于应用范围
sf lightning dev app --help

# 对于组件范围
sf lightning dev component --help
```

注意必需标志与可选标志。如果必需标志不明确，请在运行之前询问用户。

### 1c. 启动预览

为每个预览命令添加前缀 `OPEN_BROWSER=false`——CLI 默认会打开浏览器窗口，而我们**不**希望代理驱动时这样做。（此环境变量在 `--help` 中未记录；除非用户明确要求浏览器窗口，否则依赖它。）

| 范围       | 命令                                                                               |
|-------------|---------------------------------------------------------------------------------------|
| `app`       | `OPEN_BROWSER=false sf lightning dev app -o <orgAlias> -n <appName> -t desktop`       |
| `component` | `OPEN_BROWSER=false sf lightning dev component -o <orgAlias> -n <componentName>`      |

预览启动后，捕获 URL 并以完全相同的格式记录：

```text
Lightning 预览在 URL: <URL> 上运行
```

如果任何子步骤失败，请停止并将错误显示给用户——不要试图掩盖认证或插件安装问题。

---

## 步骤 2 — 提取运行时 DOM

仅在步骤 1 生成实时预览 URL 后运行此步骤。

### 2a. 获取认证的前端门 URL —— **不向代理上下文显示令牌**

`sf org open --url-only --json` 返回的前端门 URL 包含一个短寿命的 OTP，用于认证会话。**绝对不要直接运行 `sf org open`——其输出将出现在代理工具输出流中，并将认证令牌泄漏到记录中，违反了代理安全标准 S1。** 捆绑的辅助脚本是与获取 URL 的唯一支持方式：它内部运行 `sf org open` 并将 stdout 重定向到 `chmod 600` 临时文件，并抑制 stderr，因此 URL 片段或令牌子字符串永远不会到达代理上下文。

相反，使用捆绑的辅助脚本，它将 URL 写入 `chmod 600` 临时文件，并仅打印 `export` 分配（不包含令牌内容）。首先捕获辅助脚本输出，以便非零退出状态终止调用者——`eval "$(...)"` 单独会掩盖失败，让代理继续进行未设置的 `$FRONTDOOR_URL_FILE`：

```bash
frontdoor_env="$("<skill_dir>/scripts/open-frontdoor.sh" <orgAlias> <previewUrl>)" || exit 1
eval "$frontdoor_env"
```

辅助脚本抑制了 `sf` 和 `python3` 的 stderr 以及 stdout，因此部分 URL 和进度噪音永远不会到达代理记录。

浏览器驱动程序必须：
1. 从 `$FRONTDOOR_URL_FILE` 读取 URL。
2. 导航到它以建立会话。
3. 使用后立即删除临时文件。
4. **绝对不要 `cat` 或以其他方式输出文件内容。**

**OTP 令牌很快过期。** 首先启动浏览器驱动程序，然后在导航之前立即调用辅助脚本——否则令牌会过期。

### 2b. 导航并等待

1. 在自动化浏览器中打开步骤 1 的预览 URL。
2. 等待网络空闲并初始渲染完成。
3. 如果预期元素不存在，请短暂后退并重试，然后再宣布失败——本地开发页面有时会分两个阶段进行水合。

### 2c. 提取子树

两个确定性字符串操作——将组件名称转换为其 `c-<kebab>` 选择器，并将提取的 HTML 用确切的 `DOM_OUTPUT_START` / `DOM_OUTPUT_END` 标记包裹——由 `<skill_dir>/scripts/extract-dom.sh` 处理。不要在文本中重新推导选择器或组合标记；调用脚本。

实际的 DOM 遍历必须由浏览器自动化驱动程序（Playwright / Puppeteer / CDP）运行；脚本不驱动浏览器。

#### 如果范围是 `component`

确定性地计算选择器：

```bash
selector="$("<skill_dir>/scripts/extract-dom.sh" selector <componentName>)"
```

然后，使用驱动程序，刺穿 `lwr_dev-preview-container` 阴影根，定位第一个匹配 `$selector` 的可见元素，并读取其子树 HTML（通过 `element.shadowRoot.innerHTML`）。将 HTML 管道到包装步骤：

```bash
printf '%s' "$html_subtree" \
  | "<skill_dir>/scripts/extract-dom.sh" wrap component <componentName>
```

#### 如果范围是 `app`

使用驱动程序，识别主要应用根（优先选择 `document.body` 或主应用容器——不是 `document.documentElement`），排除 `<head>` 和未渲染的节点，并读取子树 HTML。将其管道到包装步骤：

```bash
printf '%s' "$html_subtree" \
  | "<skill_dir>/scripts/extract-dom.sh" wrap app
```

将脚本的 stdout 原样输出作为 DOM 输出。

### 2d. 关于 LWC 阴影 DOM（第一个常见错误）

Lightning Web Components 使用阴影 DOM。模板内容**不**可以直接在主机元素上查询：

| 访问模式                | 你会得到                         |
|-------------------------------|--------------------------------------|
| `element.innerHTML`           | 空的，或只有插槽 light-DOM 内容 |
| `element.outerHTML`           | 仅主机标签，无子元素              |
| `element.shadowRoot.innerHTML`| 真实的渲染模板内容               |

如果浏览器驱动程序的 DOM 查询默认不穿透阴影根，请显式遍历 `shadowRoot`。大多数现代自动化驱动程序都有一个穿透阴影查询的辅助函数——使用它。

---

## 示例

对于端到端示例（预览组件、安全捕获前端门 URL 并提取其 DOM），加载
[`examples/component-preview-and-dom.md`](examples/component-preview-and-dom.md)。

---

## 验证清单

- [ ] `<skill_dir>/scripts/verify-toolchain.sh <orgAlias>` 对于目标别名退出零。
- [ ] 预览命令使用 `OPEN_BROWSER=false` 运行。
- [ ] 预览 URL 以 `Lightning 预览在 URL: <URL>` 格式记录。
- [ ] 通过 `<skill_dir>/scripts/open-frontdoor.sh` 获取前端门 URL（绝对不要直接运行 `sf org open`）。
- [ ] DOM 提取使用了 `shadowRoot` 遍历（主机上的 `innerHTML`）。
- [ ] DOM 输出由 `<skill_dir>/scripts/extract-dom.sh wrap …` 产生（脚本拥有标记）。

---

## 故障排除

- **`verify-toolchain.sh` 报告“目标组织别名未认证或未连接”**——
  运行 `sf org login web --alias <orgAlias>`（别名必须与传递给 `verify-toolchain.sh` 的值和预览命令使用的 `-o` 值匹配）。
- **`verify-toolchain.sh` 报告插件缺失**——使用
  `sf plugins install @salesforce/plugin-lightning-dev` 安装它。
- **预览打开浏览器窗口**——你忘了 `OPEN_BROWSER=false`。
- **提取时 DOM 为空**——你正在查看主机上的 `innerHTML`。使用
  `element.shadowRoot.innerHTML`。还请验证你是否穿透了 `lwr_dev-preview-container` 阴影根。
- **前端门令牌失败**——它已过期。重新调用
  `<skill_dir>/scripts/open-frontdoor.sh` 并在 ~60 秒内导航。
