# Qwen 模型选择器 (顾问)

此技能以两种模式运行：

1. **交互式顾问** — 询问诊断问题以推荐合适的模型（参见诊断流程）。
2. **跨技能解析** — 为需要模型决策而无需用户交互的执行技能提供快速路径模型查找。首先获取
   [CDN 推荐内容](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-recommendations.md)
   如果 CDN 访问失败，则使用
   [本地回退](cdn/references/qwencloud-model-recommendations.md)。

不要编造模型名称 — 仅推荐 CDN 目录中列出的模型或 CLI 返回的模型。
此技能是 **qwencloud/qwencloud-ai** 的一部分。

> **🚫 关键 — 永远不要覆盖用户指定的模型。** 如果用户（或请求执行的技能）已经明确指定了模型，则此技能对该请求的工作已完成：使用**指定的模型**。不要用“更适合的”或更新模型来替代它，也不要添加用户没有要求的自定义模式（如思考模式、风格提示）参数。下方的推荐和诊断流程仅适用于**未指定模型**的情况。您可以验证可用性，如果模型不可用/受限，则通知用户并建议替代方案 — 但最终决定权在用户手中。

## 技能目录

按需加载。当需要模型列表、默认值或推荐时，获取文档化的 CDN 模型目录。除非用户明确要求最新数据，否则不要获取其他外部 URL。

`cdn/` 下面的每个路径都是本地回退，不是主要来源。对于 `cdn/<路径>`，首先获取
`https://alioth-intl.alicdn.com/skills-info/models/<路径>`，如果该请求失败，再使用本地文件。

| 位置                                  | 目的                                                                          |
|-------------------------------------------|----------------------------------------------------------------------------------|
| `references/cli-usage.md`                 | **CLI 优先数据策略**：何时使用 CLI、3 步登录流程、显示规则                   |
| `references/error-handling.md`            | CLI 错误分类 & 恢复操作 (认证、未找到、网络、 ...)                          |
| [CDN 模型推荐](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-recommendations.md) | 跨技能推荐、Token 计划限制和思考默认值；如果不可用，使用 [本地回退](cdn/references/qwencloud-model-recommendations.md) |
| `references/pricing-disclaimer.md`        | 定价指南 + **强制**成本估算免责声明 (CN/EN) + 控制台链接                 |
| `references/pricing.md`                   | 稳定计费指南和 CDN 定价回退                                                |
| [CDN 模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-list.md) | 跨域模型目录快照；如果不可用，使用 [本地回退](cdn/references/qwencloud-model-list.md) |
| `references/sources.md`                   | 官方文档 URL (仅手动查找)                                                 |

## 前置条件

**强烈推荐 QwenCloud CLI** — 它是模型可用性、定价和配额的权威实时数据源。使用以下命令验证：

```bash
qwencloud version
```

如果未安装：

```bash
npm install -g @qwencloud/qwencloud-cli
```

需要 Node.js >= 18。如果没有 CLI，您仍然可以从 CDN 目录回答点对时导航和模型问题
，但**您无法验证当前可用性、确切当前价格或账户配额**。

## 安全与凭证模型

QwenCloud 有 **两个独立的凭证系统** — 永远不要混淆它们：

| 凭证        | 目的        | 如何提供    |
|------------|------------|-------------|
| **API 密钥** (`sk-...` / `sk-sp-...`) | 在代码中调用模型 API | `$DASHSCOPE_API_KEY` / `$QWEN_API_KEY` 环境变量 |
| **CLI 会话** | 授权 `qwencloud` CLI 子命令 | `qwencloud auth login` (浏览器设备流程) |

**红线（两者都适用）**：

- **永远不要明文输出任何凭证值。** 使用变量引用；仅报告状态
  (“已设置” / “未设置”，“有效” / “无效”)。永远不要显示 `.env` 或配置文件内容。
- **永远不要混淆这两个系统。** 当 CLI 返回 `Not authenticated` / `AUTH_REQUIRED` 时，运行
  3 步设备流程登录（参见 [cli-usage.md](references/cli-usage.md#authentication-3-step-login-flow)）。
  **不要**要求用户提供 API 密钥，并且**不要**尝试将 `$DASHSCOPE_API_KEY` 设置为修复 CLI 认证。

## 检测密钥类型

在推荐模型之前，从配置的 API 密钥检测计费模式
（输出 `token-plan`、`payg` 或 `not-set` — 永远不是密钥值本身）：

```bash
python3 -c "
import os
from pathlib import Path
env_file = Path('.env')
if not env_file.exists():
    for parent in [Path.cwd()] + list(Path.cwd().parents):
        if (parent / '.git').exists() or (parent / 'skills').is_dir():
            env_file = parent / '.env'
            break
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('\"').strip(\"'\")
        if k in ('QWEN_API_KEY', 'DASHSCOPE_API_KEY') and k not in os.environ:
            os.environ[k] = v
key = os.environ.get('QWEN_API_KEY') or os.environ.get('DASHSCOPE_API_KEY') or ''
print('token-plan' if key.startswith('sk-sp-') else 'payg' if key else 'not-set')
"
```

| 密钥类型 | 推荐范围    |
|----------|-------------|
| `token-plan` | 获取 [Token 计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md) 并仅从中选择；如果未知版本，则默认为团队超集。如果 CDN 访问失败，使用 [本地回退](cdn/references/qwencloud-token-plan-models.md)。 |
| `payg`   | 全模型目录  |
| `not-set` | **不要阻止** — 询问用户：“您计划使用哪种方法？ (1) 标准 PAYG 密钥 (2) Token 计划密钥 (3) 暂时不使用 — 仅浏览推荐。” 并根据他们的选择继续。 |

> **Windows**：如果 `python3` 不可用，请使用 `python`。或者，将代码片段保存到临时 `.py` 文件中并运行它。

## 数据解析顺序

将用户的问题与正确的数据源匹配。**不要在没有先尝试更高层级的恢复操作的情况下回退到较低层。**

| 问题类型                                                  | 主要来源                                          | 备注                                                |
|----------------------------------------------------------------|---------------------------------------------------------|------------------------------------------------------|
| 一般导航或点对时模型详情                                 | [CDN 推荐内容](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-recommendations.md) 和域目录 | 首先获取；如果不可用，使用匹配的本地回退并标识为快照 |
| **最新 / 精确 / 特定**（价格、模型详情、配额）             | **必须使用 CLI** — 参见 `cli-usage.md`               | 快照是过时的；永远不要编造数字                      |
| 按能力搜索 (“执行 X 的模型”)                           | `qwencloud models search "<X>" --format json`           | 快照关键字覆盖不完整                                |
| CLI 返回了错误                                          | `error-handling.md` 恢复操作，**然后重试**    | 认证失败 → 运行 3 步登录，不要跳转到快照 |
| CLI 完全不可用 AND 用户拒绝安装/登录                     | CDN 目录 + `pricing.md`                             | 仅回答快照支持的快照事实，并附带过时数据警告 |
| 以上全部无法回答 AND 用户确认在线查找                     | `sources.md` 中的 URL                              | 永远不要主动获取                              |

## 诊断流程（交互式顾问）

按顺序询问用户：

1. **内容类型？** — 文本 / 图像 / 视频 / 音频 / 视觉
2. **主要任务？** — 生成 / 理解 / 编程 / 推理 / 翻译
3. **优先级？** — 质量与速度与成本
4. **输入大小？** — 短 / 中 / 长上下文
5. **结构化输出？** — JSON / 函数调用需要?

## 默认推荐

在选择默认值或推荐模型之前，获取并阅读当前的
[CDN 推荐内容](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-recommendations.md)。
对于 Token 计划密钥，还阅读上面链接的 Token 计划目录，并将候选者限制为它。

- 如果用户明确指定了模型，请保留它，并仅报告真实的可用性冲突。
- 否则，首先匹配最强的任务信号，然后选择适当的质量、速度或成本层。
- 除非用户明确请求覆盖，否则保留所选模型的文档化思考默认值。
- 如果 CDN 访问失败，使用 [本地推荐](cdn/references/qwencloud-model-recommendations.md)。

> **降级**：如果此技能未加载，每个执行技能从 CDN 加载其默认值并回退到其捆绑配置。此协议纯粹是附加的，永远不会阻止执行。

## CLI 快速参考

> **需要认证。** 所有 `models` 和 `usage` 命令都需要一个活动的 **CLI 会话**（浏览器设备流程登录 — **不是** API 密钥）。如果命令返回 `Not authenticated` / `AUTH_REQUIRED`：
> 1. **运行 3 步设备流程登录** 在 [cli-usage.md](references/cli-usage.md#authentication-3-step-login-flow)
>    （使用操作系统适当的命令主动打开验证 URL，然后立即轮询）。
> 2. **在 `success` 后重试原始命令**。
> 3. **不要**要求用户提供 `$DASHSCOPE_API_KEY` / `$QWEN_API_KEY` — 这些是用于模型 API 调用，不是 CLI 会话。参见 [安全与凭证模型](#security--credential-model)。
> 4. **不要**无声地回退到快照。

| 需要                          | 命令                                                            |
|-------------------------------|--------------------------------------------------------------------|
| 全模型目录            | `qwencloud models list --all --format json`                        |
| 按模态过滤            | `qwencloud models list --input image --output text --format json`  |
| 单个模型详情          | `qwencloud models info <model-id> --format json`                   |
| 关键字搜索                | `qwencloud models search "<query>" --format json`                  |
| 免费层剩余           | `qwencloud usage free-tier --format json`                          |
| 认证状态                   | `qwencloud auth status --format json`                              |

**显示规则**：解析 `--format json` 输出并显示人类可读的摘要；永远不要直接输出原始 JSON。显示 `--format text` 输出原样，然后在 `---` 后添加分析。参见
[cli-usage.md](references/cli-usage.md#agent-display-rules-for-cli-output) 获取详细信息。

## CLI 错误处理 — 快速指南

当 CLI 失败时，**首先分类，然后恢复，再重试**。永远不要无声地回退到快照。

| 类别          | 恢复 (摘要)                                                             |
|-------------------|--------------------------------------------------------------------------------|
| `auth-failure`    | 运行 3 步登录 → **重试原始命令**。只有在用户拒绝时才回退。                 |
| `not-installed`   | 显示安装命令 → 询问用户安装 → 重试。不要无声地使用快照。                   |
| `model-not-found` | 运行 `qwencloud models search "<keyword>"` → 提出前 3 个 → 重试使用正确 ID。 |
| `network-timeout` | 重试一次（2 秒后）；只有在第二次失败后才询问是否回退。                    |
| `rate-limit`      | 显示 [速率限制控制台](https://home.qwencloud.com/settings/monitoring/rate-limit)；用户决定。 |
| `quota-exhausted` | 显示 [计费控制台](https://home.qwencloud.com/billing/pay-as-you-go)；不要使用快照。 |
| `version-mismatch`| 建议 `qwencloud version --check` 或更新检查技能 → 升级 → 重试。            |
| `other`           | 显示原始 stderr；链接到文档；只有在用户选择退出后，才回退。                  |

完整分类、信号和示例流程：[error-handling.md](references/error-handling.md)。

## 定价与成本估算

- **最新定价**：首先运行 `qwencloud models info <model> --format json`；仅将 `pricing.md` 链接的 CDN 定价参考作为回退。**永远不要编造价格。**
- **强制免责声明**：每个与成本相关的答案**必须**以 [pricing-disclaimer.md](references/pricing-disclaimer.md) 中的免责声明（中文或英文版本，匹配用户的响应语言）结束。省略免责声明是一个**关键错误**。
- **免费配额**：永远不要假设有免费配额可用 — 使用 `qwencloud usage free-tier` 来验证或
  指导用户到 [控制台](https://home.qwencloud.com/benefits)。
- **使用/计费查询**：将用户引导到适当控制台页面 — 参见 [pricing-disclaimer.md](references/pricing-disclaimer.md#usage--billing-console) 中的表格。

## 更新检查

当用户要求检查更新 (“检查更新”、“检查版本”、“是否有新版本”、“更新技能”)：

1. **查找 qwencloud-update-check**：在兄弟技能目录中查找 `qwencloud-update-check/SKILL.md`。
2. **如果找到** — 运行：`python3 <qwencloud-update-check-dir>/scripts/check_update.py --print-response`
   并报告结果。如果用户要求强制检查，请使用 `--force`。
3. **如果未找到** — 运行 `qwencloud version --check` 并报告结果。

## 反模式

- **永远不要覆盖用户指定的模型** — 如果用户明确选择了模型，则不要为该请求推荐其他模型；仅验证可用性。只有在用户要求建议或其选择确实不可用（并且用户仍然决定）时，才允许建议。
- **永远不要编造模型名称** — 仅推荐 CDN 目录中列出的模型或 CLI 返回的模型。
- **永远不要推荐用户计费范围之外的模型** — Token 计划密钥必须仅接收 Token 计划目录中链接的模型；PAYG
  密钥可以使用完整目录。违反此规定会导致用户出现严重错误。
- **永远不要编造或猜测任何价格数字** — 仅使用 CLI / `pricing.md` / 官方定价页面。编造价格是**关键错误**。
- **永远不要在 CLI 出错时无声地回退到快照** — 首先应用
  [error-handling.md](references/error-handling.md) 恢复操作。
- **永远不要假设免费配额可用** — 配额可能已被消耗、过期或移除。始终首先显示付费单位价格。
- **永远不要明文输出 API 密钥** — 参见安全部分。
- **永远不要混淆 CLI 会话与 API 密钥** — CLI 认证使用浏览器设备流程登录；永远不要将 `$DASHSCOPE_API_KEY` 或 `$QWEN_API_KEY` 作为修复 CLI `Not authenticated` / `AUTH_REQUIRED` 错误的方法。
- **永远不要主动获取任意 URL 或触发网络搜索。** 当需要模型数据时，获取文档化的 CDN 模型目录；仅在 CLI + CDN 目录无法回答 AND 用户确认时，访问其他在线源。
- **永远不要构造使用/计费/控制台 URL** — 仅使用此技能或其参考中列出的确切链接。如果 URL 未列出，不要编造一个。
- **对于任何与成本相关的答案，始终包含成本免责声明**（参见
  [pricing-disclaimer.md](references/pricing-disclaimer.md))。

## 参考

| 来源                                                       | 目的                                                          |
|--------------------------------------------------------------|------------------------------------------------------------------|
| [cli-usage.md](references/cli-usage.md)                      | CLI 优先策略、3 步登录、显示规则、模型详情 URL                 |
| [error-handling.md](references/error-handling.md)            | CLI 错误分类 & 恢复                                          |
| [qwencloud-model-recommendations.md (CDN)](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-recommendations.md) ([local fallback](cdn/references/qwencloud-model-recommendations.md)) | 跨技能推荐、Token 计划、思考模式                             |
| [pricing-disclaimer.md](references/pricing-disclaimer.md)    | 定价指南 + 强制免责声明 + 计费控制台链接                      |
| [pricing.md](references/pricing.md)                          | 稳定计费指南和 CDN 定价回退                                  |
| [qwencloud-model-list.md (CDN)](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-model-list.md) ([local fallback](cdn/references/qwencloud-model-list.md)) | 跨域模型目录快照                                              |
| [sources.md](references/sources.md)                          | 官方文档 URL                                                  |
| `qwencloud models list --format json`                        | 动态：完整模型目录，包括定价、功能、配额                     |
| `qwencloud models info <id> --format json`                   | 动态：单个模型详情（定价层、上下文、速率限制）                 |
| `qwencloud models search "<q>" --format json`                | 动态：基于关键字的模型发现                                     |
| `qwencloud usage free-tier --format json`                    | 动态：每个模型的剩余免费层配额                                 |
