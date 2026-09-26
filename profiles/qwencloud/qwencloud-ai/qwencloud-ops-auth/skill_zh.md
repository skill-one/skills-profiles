# QwenCloud 认证设置

配置和验证 QwenCloud API 的认证。
这项技能是 **qwencloud/qwencloud-ai** 的一部分。

## 技能目录

使用此技能的内部文件进行学习。仅在用户需要控制台或文档链接时加载引用。

| 位置 | 目的 |
|------|------|
| `references/tokenplan.md` | 令牌计划与编码计划与 PAYG；CDN 模型目录、端点映射、定价、User-Agent |
| `references/codingplan.md` | 编码计划与标准密钥：模型列表、端点映射、错误代码、成本风险 |
| `references/custom-oss.md` | 生产文件上传的自定义 OSS 存储桶设置（替换 48 小时临时存储） |
| `references/sources.md` | 控制台 URL、认证指南（仅手动查找） |

## 安全

**绝对不要输出任何明文的 API 密钥、OSS 凭证。**
这同样适用于 `DASHSCOPE_API_KEY` 和自定义 OSS AccessKey 对。在此技能中对凭证的任何检查或检测必须**非明文**：仅报告状态（例如 "已设置" / "未设置"、"有效" / "无效"、"HTTP 状态码"），绝不能输出密钥值。

## API 密钥处理（强制要求）

当 API 密钥未配置或脚本报告缺少凭证时：

1. **绝对不要直接要求用户提供他们的 API 密钥。** 不要提示 "请粘贴您的 API 密钥" 或类似内容。不要以任何形式请求密钥值。
2. **帮助创建一个 `.env` 文件**，然后指导用户填写自己的密钥：
   - 运行：`echo 'DASHSCOPE_API_KEY=sk-your-key-here' >> .env`
   - 告诉用户："请将 `sk-your-key-here` 替换为您从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 获取的实际 API 密钥。"
3. **或者** 解释如何配置环境变量：`export DASHSCOPE_API_KEY='sk-...'` + 提供控制台 URL。
4. **仅**在用户**明确坚持**让代理为他们完成时，将实际密钥值写入 `.env`。

## 凭证优先级链

凭证按以下顺序加载（第一个匹配的胜出）：

1. **环境变量** — `DASHSCOPE_API_KEY`（或 `QWEN_API_KEY` 别名）
2. **`.env` 文件** — 在当前工作目录，然后是代码库根目录（通过 `.git` 或 `skills/` 目录检测）。现有的环境变量不会被覆盖。

### 环境变量

| 变量名            | 目的                                                                                                                                   |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `DASHSCOPE_API_KEY` | API 密钥（必需）                                                                                                                        |
| `QWEN_API_KEY`      | `DASHSCOPE_API_KEY` 的别名。如果两者都设置，`QWEN_API_KEY` 优先级更高。                                                            |
| `QWEN_BASE_URL`     | 覆盖默认端点（可选；用于自定义部署）                                                                              |
| `QWEN_TMP_OSS_BUCKET` | 文件上传的自定义 OSS 存储桶（替换 48 小时临时存储）。参见 [custom-oss.md](references/custom-oss.md)。                         |
| `QWEN_TMP_OSS_REGION` | OSS 区域（当 `QWEN_TMP_OSS_BUCKET` 设置时必需）。                                                                              |
| `QWEN_TMP_OSS_AK_ID` / `AK_SECRET` | OSS 凭证（使用权限最低的 RAM 用户：`oss:PutObject` + `oss:GetObject`）。如果未设置，则回退到 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET`。 |

## API 密钥类型

QwenCloud 有三种互斥的密钥/计划类型：

| 密钥类型 | 格式 | 目的 | 端点 |
|----------|------|------|------|
| **标准（按量付费）** | `sk-xxxxx` | 脚本、应用程序和工具的 API 调用 | `dashscope-intl.aliyuncs.com` |
| **令牌计划** | `sk-sp-xxxxx` | 带有 User-Agent 标头的交互式 AI 工具 | `token-plan.ap-southeast-1.maas.aliyuncs.com` |
| **编码计划** | `sk-sp-xxxxx` | 仅限交互式 AI 编码工具（Cursor、Claude Code、Qwen Code） | `coding-intl.dashscope.aliyuncs.com` |

所有 qwencloud/qwencloud-ai 脚本都需要一个**标准**密钥 (`sk-`)。编码计划密钥 (`sk-sp-`) 在标准端点上会返回 `401 invalid_api_key`。令牌计划密钥 (`sk-sp-`) 会被脚本自动路由到令牌计划端点。在令牌计划请求之前，获取并阅读当前的 [令牌计划模型目录](https://alioth-intl.alicdn.com/skills-info/models/references/qwencloud-token-plan-models.md)，并传递精确列出的模型；如果 CDN 访问失败，请使用 [本地回退](cdn/references/qwencloud-token-plan-models.md)。编码计划的详细信息保留在 [codingplan.md](references/codingplan.md) 中。

如果用户的密钥以 `sk-sp-` 开头，首先检查 [tokenplan.md](references/tokenplan.md) 中的令牌计划详细信息，然后检查上述 CDN 目录中的模型覆盖范围，然后 [codingplan.md](references/codingplan.md) 中的编码计划详细信息。如果需要模型且不在其计划范围内，请指导他们从以下控制台获取标准密钥。

### 查看账单

使用 **qwencloud-usage** 技能直接查询使用情况、免费套餐配额和账单。或者，账单详情可在 QwenCloud 控制台中获取：

| 密钥类型 | 账单页面 |
|----------|----------|
| 标准（按量付费） | [按量付费账单](https://home.qwencloud.com/billing/pay-as-you-go) |
| 令牌计划个人 | [个人账单](https://home.qwencloud.com/analytics/token-plan/individual) |
| 令牌计划团队 | [团队账单](https://home.qwencloud.com/analytics/token-plan/team) |
| 编码计划 | [编码计划账单](https://home.qwencloud.com/billing/coding-plan) |
| 使用分析（两者） | [使用分析](https://home.qwencloud.com/analytics) |

> **绝对不要虚构、猜测或构造使用/账单/控制台 URL。** 仅提供本技能中列出的确切链接。如果此处未列出 URL，请不要编造。

## 获取 API 密钥

1. 打开 [QwenCloud 控制台](https://home.qwencloud.com/api-keys)
2. 使用您的 QwenCloud 账户登录
3. 从 API 密钥管理部分创建或复制 API 密钥
4. 标准密钥以 `sk-` 开头（不是 `sk-sp-`，后者仅用于编码计划）

## 安全最佳实践

- **不要在源代码或提交到版本控制的配置文件中硬编码 API 密钥**
- **使用环境变量** 或 `.env` 文件（并将 `.env` 添加到 `.gitignore`）
- **定期轮换密钥**，立即撤销泄露的密钥
- **使用最小权限** — 当可能时，为特定应用程序创建专用密钥**

### 设置 `.env`

在您的项目根目录或当前工作目录中创建一个 `.env` 文件：

```bash
echo 'DASHSCOPE_API_KEY=sk-your-key-here' >> .env
```

脚本会自动从当前工作目录和项目根目录加载 `.env`（通过 `.git` 或 `skills/` 目录检测）。`.env` 值**不会**覆盖现有的环境变量。

### 示例 `.gitignore` 条目

```
.env
.env.local
*.env
```

## 验证

除非另有说明，否则本技能中提到的任何脚本或任务都在**前台**运行——等待标准输出；不要作为后台任务运行。

**按量付费仅限**：使用简单的 curl 请求测试认证。**令牌计划**：不要使用 curl；使用目标技能捆绑的 Python 脚本进行验证。

```bash
curl -sS -X POST "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"Hi"}]}'
```

成功响应将返回包含 `choices` 和 `message.content` 的 JSON。

## 认证错误处理

QwenCloud API 密钥针对 QwenCloud 控制台进行范围限制。无效或匹配错误的密钥将产生 `401 Unauthorized`。

### 触发时机

当**任何**子技能收到 `401` 响应，并且非明文检查显示密钥已设置（例如 `[ -n "$DASHSCOPE_API_KEY" ]`；不要输出密钥值）时。

### 探测命令

对于按量付费，发送一个轻量级请求以验证认证。在令牌计划模式下，不要使用 curl；运行目标技能捆绑的 Python 脚本。

```bash
curl -sS -o /dev/null -w "%{http_code}" \
  -X POST "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"hi"}]}'
```

### 遇到 401：强制交互式解决

如果按量付费探测返回 401，请按以下顺序执行这些步骤：

**步骤 1 — 确认密钥来源：**

```
您的 API 密钥认证失败。

请确认：
1. 您的密钥是在 home.qwencloud.com（QwenCloud 控制台）创建的 → 重新验证密钥
2. 我的密钥可能无效 → 在 home.qwencloud.com/api-keys 创建一个新的
```

**步骤 2 — 应用用户的选项：**

| 用户说                         | 操作                                                              |
|--------------------------------|---------------------------------------------------------------------|
| 密钥来自 QwenCloud 控制台 | 重新运行验证以确认密钥是否有效                                    |
| 密钥可能无效                | 指导用户在 `home.qwencloud.com/api-keys` 创建一个新的密钥 |

**步骤 3 — 重新运行验证。**

**步骤 4 — 如果仍然 401**，密钥本身无效——指导用户从 [QwenCloud 控制台](https://home.qwencloud.com/api-keys) 创建一个新的。

## 验证

对于按量付费，运行上述 curl 验证。对于令牌计划，运行目标技能捆绑的 Python 脚本。

通过标准：HTTP 200 且输出有效。将证据保存到 `output/qwencloud-ops-auth/`。

## 输出和证据

- 将验证结果和任何诊断输出保存到 `output/qwencloud-ops-auth/`。
- 保留成功认证测试的记录以供故障排除。

## 输出位置

优先选择**当前工作目录**。默认子目录：`./output/qwencloud-ops-auth/`。

**写入禁止**：绝对不要将输出文件写入此技能的安装目录或任何 `skills/` 层次结构。所有生成的内容必须位于当前工作目录下的 `output/` 或用户指定路径。

## 更新检查（执行后强制要求）

当用户要求检查更新（例如 "检查更新"、"检查版本"、"是否有新版本"、"更新技能"）时：

1. **查找 qwencloud-update-check**：在兄弟技能目录中查找 `qwencloud-update-check/SKILL.md`。
2. **如果找到** — 运行：`python3 <qwencloud-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。如果用户要求强制检查，请使用 `--force`。
3. **如果未找到** — 您**必须**提供以下选项并**等待用户的响应**：

> 更新检查技能未安装。它让您了解 qwencloud/qwencloud-ai 的新功能和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何事情
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QwenCloud/qwencloud-ai --skill qwencloud-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

## 参考文献

- [tokenplan.md](references/tokenplan.md) — 令牌计划与标准密钥；CDN 模型目录指针、积分账单和端点指南
- [codingplan.md](references/codingplan.md) — 编码计划兼容性和错误指南
- [custom-oss.md](references/custom-oss.md) — 生产文件上传的自定义 OSS 存储桶设置
- [sources.md](references/sources.md) — 官方文档 URL（控制台、认证指南）
