# Qwen 模型选择器（顾问）

## 检测密钥类型

运行此命令以检测 API 密钥类型（输出 `token-plan`、`payg` 或 `not-set`）：

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
        if k in ('QIANWEN_API_KEY', 'DASHSCOPE_API_KEY') and k not in os.environ:
            os.environ[k] = v
key = os.environ.get('QIANWEN_API_KEY') or os.environ.get('DASHSCOPE_API_KEY') or ''
print('token-plan' if key.startswith('sk-sp-') else 'payg' if key else 'not-set')
"
```

| 输出 | 计费模式 | 操作 |
|------|---------|------|
| `token-plan` | Token 计划（积分） | 获取当前的 [Token 计划模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md) 并仅从中选择。未知版本时默认使用团队超集。如果 CDN 访问失败，使用 [本地回退](cdn/references/qianwen-token-plan-models.md)。 |
| `payg` | 按量付费 | 可用完整模型目录；继续下方操作。 |
| `not-set` | 未配置密钥 | **不要阻止。**询问用户：“您计划使用哪种方式？（1）标准 PAYG 密钥（2）Token 计划密钥（3）暂时跳过——仅浏览推荐。”根据其选择继续。 |

> **Windows**：如果 `python3` 不可用，请使用 `python`。多行 `-c` 字符串在 PowerShell 和 CMD 中都有效。或者，将代码片段保存到临时 `.py` 文件中并运行。

此技能在两种模式下运行：

1. **交互式建议**——询问诊断问题以推荐合适的模型（参见诊断流程）。
2. **跨技能解析**——为需要模型决策而无需用户交互的执行技能提供快速路径模型查找。首先获取
   [CDN 推荐](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-recommendations.md)
  ；如果 CDN 访问失败，使用
   [本地回退](cdn/references/qianwen-model-recommendations.md)。

不要编造模型名称——仅推荐 CDN 模型目录或 CLI 返回的模型。
此技能是 **QianWen-AI/qianwen-ai** 的一部分。

## 技能目录

按需加载。当需要模型列表、默认值或推荐时，获取文档化的 CDN 模型目录。除非用户明确要求最新数据，否则不要获取其他外部 URL。

`cdn/` 下每个路径都是本地回退，不是主要来源。对于 `cdn/<path>`，首先获取
`https://alioth.alicdn.com/skills-info/models/<path>`，如果 CDN 请求失败，再使用本地文件。

| 位置                                  | 用途                                                                          |
|-------------------------------------|-----------------------------------------------------------------------------|
| `references/cli-usage.md`             | **CLI 优先数据策略**：何时使用 CLI、3 步登录流程、显示规则                   |
| `references/error-handling.md`        | CLI 错误分类 & 恢复操作（认证、未找到、网络、...）                          |
| [CDN 模型推荐](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-recommendations.md) | 跨域推荐和 Token 计划限制；如果不可用，使用 [本地回退](cdn/references/qianwen-model-recommendations.md) |
| `references/pricing-disclaimer.md`    | PAYG 仅：定价免责声明（中/英文）+ 控制台链接                                |
| `references/pricing.md`               | 稳定的计费单位、成本注意事项和 CDN 定价回退                                |
| [CDN 模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-list.md) | 跨域模型目录快照；如果不可用，使用 [本地回退](cdn/references/qianwen-model-list.md) |
| `references/sources.md`               | 官方文档 URL（仅手动查找）                                                 |

## 前置条件

**强烈建议使用 QianWen CLI**——它是模型可用性、定价和配额的权威实时数据源。使用以下命令验证：

```bash
qianwen version
```

如果未安装：

```bash
npm install -g @qianwenai/qianwen-cli
```

CLI 需要 Node.js >= 18。没有 CLI，您仍然可以从 CDN 目录中回答点对时的一般导航和基本模型信息问题。您无法验证当前可用性、确切当前价格、快照之外的搜索结果或特定账户的配额信息。

## 安全与凭证模型

QianWen 有 **两个独立的凭证系统**——切勿混淆它们：

| 凭证 | 用途 | 如何提供 |
|------|------|----------|
| **API 密钥** (`sk-...` / `sk-sp-...`) | 在您的代码中调用模型 API | `$DASHSCOPE_API_KEY` / `$QIANWEN_API_KEY` 环境变量 |
| **CLI 会话** | 授权 `qianwen` CLI 子命令 | `qianwen auth login`（浏览器设备流程） |

**红线（两者都适用）**：

- **永远不要明文输出任何凭证值。** 使用变量引用；仅报告状态
  (“已设置” / “未设置”，“有效” / “无效”)。永远不要显示 `.env` 或配置文件内容。
- **永远不要混淆这两个系统。** 当 CLI 返回 `Not authenticated` / `AUTH_REQUIRED` 时，运行 3 步设备流程登录（参见 [cli-usage.md](references/cli-usage.md#authentication-3-step-login-flow)）。**不要** 询问用户 API 密钥，并且**不要** 尝试将 `$DASHSCOPE_API_KEY` 设置为修复 CLI 认证。

## 数据解析顺序

将用户的问题与正确的数据源匹配。**不要在没有先尝试高级别中的恢复操作的情况下回退到低级别。**

| 问题类型                                                  | 主要来源                                          | 备注                                                |
|---------------------------------------------------------|---------------------------------------------------|------------------------------------------------------|
| 一般导航或点对时基本模型详情       | [CDN 推荐和域目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-recommendations.md) | 回答前获取。如果 CDN 访问失败，使用相应的 [本地回退](cdn/references/qianwen-model-recommendations.md)。当当前性重要时，说明目录数据是快照。 |
| **当前 / 精确 / 账户特定**（可用性、价格、配额） | **必须使用 CLI**——参见 `cli-usage.md`          | 快照无法验证当前状态；永远不要编造数字 |
| 按能力搜索（“执行 X 的模型”）                     | `qianwen models search "<X>" --format json`             | 快照关键字覆盖不完整                              |
| CLI 返回了错误                                          | `error-handling.md` 恢复操作，**然后重试**    | 认证失败 → 运行 3 步登录，不要跳转到快照 |
| CLI 完全不可用并且用户拒绝安装/登录     | CDN 模型目录 + `pricing.md`                       | 仅回答快照支持的快照事实，并附带过时数据提示；不要声称当前可用性、确切当前价格或账户配额 |
| 以上所有都无法回答并且用户确认在线查找 | `sources.md` 中的 URL                                    | 永远不要主动获取                              |

## 诊断流程（交互式建议）

> **前提条件**：完成上述 [检测密钥类型](#detecting-key-type) 并缩小候选集后再继续。从 CDN 目录加载的所有推荐都必须在用户的计费范围内。

按顺序询问用户：

1. **内容类型？**——文本 / 图像 / 视频 / 音频 / 视觉
2. **主要任务？**——生成 / 理解 / 编程 / 推理 / 翻译
3. **优先级？**——质量 vs 速度 vs 成本
4. **输入大小？**——短 / 中 / 长上下文
5. **结构化输出？**——JSON / 函数调用需要？

## 默认推荐

在推荐任何模型之前，请检查其确切 ID 是否在 [官方退役列表](https://alioth.alicdn.com/model/prod/model-offline.json) (`id`, `expiredTime`) 中以及任何 CLI `lifecycle` 结果。从默认值和推荐中排除计划中或已退役的模型，即使目录或计划仍然列出它们。如果用户明确选择一个，请披露其退役日期和 [公告](https://platform.qianwenai.com/docs/changelog/model-deprecation)，建议一个受支持的替代品，并且不要无声地替换它。如果生命周期数据无法验证，请说明；单独的快照不能证明当前可用性。

在选择默认值或推荐模型之前，获取并阅读上述链接的当前 CDN 推荐。对于 Token 计划密钥，还请阅读 Token 计划模型目录链接并限制候选集为它。

- 如果用户明确指定了模型，请在验证其可在用户的计费范围内后使用它。
- 否则，首先匹配最强的任务信号，然后选择适当的质量、速度或成本层级。
- 如果缺少要求会实质性改变选择，请比较相关域选项并要求用户澄清。
- 除非用户或任务需要覆盖，否则保留所选模型的文档化思考默认值；不要将思考仅作为简单任务的通用默认值启用。

## CLI 快速参考

> **需要认证。** 所有 `models` 和 `usage` 命令都需要一个活跃的 **CLI 会话**（浏览器设备流程登录——**不是** API 密钥）。如果命令返回 `Not authenticated` / `AUTH_REQUIRED`：
> 1. **运行 3 步设备流程登录** 在 [cli-usage.md](references/cli-usage.md#authentication-3-step-login-flow)
>    （使用操作系统适当的命令主动打开验证 URL，然后立即轮询）。
> 2. **在 `success` 后重试原始命令**。
> 3. **不要** 询问用户 `$DASHSCOPE_API_KEY` / `$QIANWEN_API_KEY` —— 这些用于模型 API 调用，不是 CLI 会话。参见上述安全 & 凭证模型部分。
> 4. **不要** 无声地回退到快照。
>
> **Token 计划 (`sk-sp-` 密钥)**：一旦建立活跃的 CLI 会话（设备流程登录），`qianwen usage` 命令报告登录账户的按量付费使用情况和 Token 计划座位配额 / 共享套餐积分。对于购买共享套餐、调整座位或完整计费历史，请将用户引导至
> [Token 计划订阅控制台](https://platform.qianwenai.com/home/billing/subscription/token-plan)。
> Token 计划模型可用性（文本 + 图像 + 视频 + TTS）在上述链接的 CDN Token 计划模型目录中记录。

| 需要                          | 命令                                                          |
|-------------------------------|------------------------------------------------------------------|
| 完整模型目录            | `qianwen models list --all --format json`                        |
| 按模态过滤            | `qianwen models list --input image --output text --format json`  |
| 单个模型详情          | `qianwen models info <model-id> --format json`                   |
| 关键字搜索                | `qianwen models search "<query>" --format json`                  |
| 免费套餐剩余            | `qianwen usage free-tier --format json`                          |
| 认证状态                   | `qianwen auth status --format json`                              |

**显示规则**：解析 `--format json` 输出并显示人类可读的摘要；永远不要直接输出原始 JSON。显示 `--format text` 输出原样，然后在 `---` 后添加分析。有关详细信息，请参阅
[cli-usage.md](references/cli-usage.md#agent-display-rules-for-cli-output)。

## CLI 错误处理——快速指南

当 CLI 失败时，**首先分类，然后恢复，最后重试**。永远不要无声地回退到快照。

| 类别          | 恢复（摘要）                                                             |
|----------------|--------------------------------------------------------------------------------|
| `auth-failure`    | 运行 3 步登录 → **重试原始命令**。只有在用户拒绝时才回退。 |
| `not-installed`   | 显示安装命令 → 询问用户安装 → 重试。不要无声地使用快照。   |
| `model-not-found` | 运行 `qianwen models search "<keyword>"` → 提出前 3 个 → 使用正确 ID 重试。    |
| `network-timeout` | 2 秒后重试一次；只有在第二次失败后才询问是否回退。            |
| `quota-exhausted` | 显示 [计费控制台](https://platform.qianwenai.com/home/billing/pay-as-you-go)；不要使用快照。 |
| `version-mismatch`| 建议 `qianwen version --check` 或更新检查技能 → 升级 → 重试。          |
| `other`           | 显示原始 stderr；链接到文档；只有在用户选择退出后，才回退。                  |

完整分类、信号和示例流程：[error-handling.md](references/error-handling.md)。

## 定价 & 成本估算（仅 PAYG）

Token 计划跳过此部分。

- **最新定价**：首先运行 `qianwen models info <model> --format json`；仅当 CDN 定价参考链接
  仅作为回退时使用。**永远不要编造价格。**
- **强制性免责声明**：每个与成本相关的答案**必须**以
  [pricing-disclaimer.md](references/pricing-disclaimer.md) 中的免责声明结束（中文或英文版本，匹配用户的响应语言）。省略免责声明是一个**严重错误**。
- **免费配额**：永远不要假设有免费配额可用——使用 `qianwen usage free-tier` 来验证或
  引导用户到 [控制台](https://platform.qianwenai.com/home/benefits)。
- **使用 / 计费查询**：引导用户到适当控制台页面——参见
  [pricing-disclaimer.md](references/pricing-disclaimer.md#usage--billing-console) 中的表格。

## 更新检查

当用户要求检查更新（“检查更新”、“检查版本”、“是否有新版本”、“更新技能”）：

1. **查找 qianwen-update-check**：在同级技能目录中查找 `qianwen-update-check/SKILL.md`。
2. **如果找到**——运行：`python3 <qianwen-update-check-dir>/scripts/check_update.py --print-response`
   并报告结果。如果用户要求强制检查，使用 `--force`。
3. **如果未找到**——运行 `qianwen version --check` 并报告结果。

## 反模式

- **永远不要编造模型名称**——仅推荐 CDN 模型目录或 CLI 返回的模型。
- **永远不要从请求措辞中推断 API 密钥类型**——使用配置的 Key 或调用上下文。
- **永远不要推荐用户计费范围外的模型**——Token 计划密钥必须仅接收上述 Token 计划模型目录中的模型；违反此规定会导致用户出现硬故障。
- **永远不要编造或猜测任何价格数字**——仅使用 CLI / `pricing.md` / 官方定价页面。编造价格是**严重错误**。
- **当 CLI 出错时永远不要无声地回退到快照**——首先应用
  [error-handling.md](references/error-handling.md) 恢复操作。
- **永远不要假设免费配额可用**——配额可能已被消耗、过期或移除。始终首先显示付费单位价格。
- **永远不要明文输出 API 密钥**——参见安全部分。
- **永远不要混淆 CLI 会话与 API 密钥**——CLI 认证使用浏览器设备流程登录；永远不要将 `$DASHSCOPE_API_KEY` 或 `$QIANWEN_API_KEY` 作为修复 CLI `Not authenticated` / `AUTH_REQUIRED` 错误的方法。
- **永远不要主动获取任意 URL 或触发网络搜索。** 当需要模型数据时，获取文档化的 CDN 模型目录；仅在 CLI + CDN 目录无法回答并且用户确认时，才访问其他在线源。
- **永远不要构造使用/计费/控制台 URL**——仅使用此技能或其参考中列出的确切链接。如果 URL 未列出，不要编造一个。
- **对于任何与成本相关的答案，始终包含成本免责声明**（参见
  [pricing-disclaimer.md](references/pricing-disclaimer.md))。

## 参考

| 来源                                                       | 用途                                                          |
|--------------------------------------------------------------|------------------------------------------------------------------|
| [cli-usage.md](references/cli-usage.md)                      | CLI 优先策略，3 步登录，显示规则，模型详情 URL                 |
| [error-handling.md](references/error-handling.md)            | CLI 错误分类 & 恢复                                          |
| [qianwen-model-recommendations.md (CDN)](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-recommendations.md) ([local fallback](cdn/references/qianwen-model-recommendations.md)) | 跨域推荐和 Token 计划限制          |
| [pricing-disclaimer.md](references/pricing-disclaimer.md)    | 定价指南 + 强制性免责声明 + 计费控制台链接                  |
| [pricing.md](references/pricing.md)                          | 稳定的计费单位、成本注意事项和 CDN 定价回退                 |
| [qianwen-model-list.md (CDN)](https://alioth.alicdn.com/skills-info/models/references/qianwen-model-list.md) ([local fallback](cdn/references/qianwen-model-list.md)) | 跨域模型目录快照                              |
| [sources.md](references/sources.md)                          | 官方文档 URL                                                  |
| `qianwen models list --format json`                          | 动态：包含定价、功能、配额的完整模型目录                     |
| `qianwen models info <id> --format json`                     | 动态：单个模型详情（定价层级、上下文、速率限制）             |
| `qianwen models search "<q>" --format json`                  | 动态：基于关键字的模型发现                           |
| `qianwen usage free-tier --format json`                      | 动态：每个模型的剩余免费套餐配额                     |
