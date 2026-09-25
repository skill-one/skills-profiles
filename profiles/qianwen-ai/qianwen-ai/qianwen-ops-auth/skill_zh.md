# 千文认证设置

配置和验证千文API的认证。
这项技能是 **QianWen-AI/qianwen-ai** 的一部分。

## 技能目录

使用此技能的内部文件进行学习。仅在用户需要控制台或文档链接时加载引用。

| 位置 | 用途 |
|------|------|
| `references/tokenplan.md` | 令牌计划与标准密钥的对比；指向支持模型的CDN目录，并保留积分、策略和错误指导 |
| `references/custom-oss.md` | 生产文件上传的自定义OSS桶设置（替换48小时临时存储） |
| `references/sources.md` | 控制台URL，认证指南（仅手动查找） |

## 安全

**绝对不要以明文形式输出任何API密钥、OSS凭证。**
这同样适用于 `DASHSCOPE_API_KEY` 和自定义OSS AccessKey对。在此技能中对凭证的任何检查或检测必须**非明文**：仅报告状态（例如 "已设置" / "未设置"、"有效" / "无效"、HTTP状态码），绝不能输出密钥值。

## API密钥处理（强制要求）

当API密钥未配置或脚本报告缺少凭证时：

1. **绝对不要直接要求用户提供他们的API密钥。** 不要提示 "请粘贴您的API密钥" 或类似内容。不要以任何形式请求密钥值。
2. **帮助创建一个 `.env` 文件** 并提供占位符，然后指导用户填写自己的密钥：
   - 运行：`echo 'DASHSCOPE_API_KEY=sk-your-key-here' >> .env`
   - 告诉用户："请将 `sk-your-key-here` 替换为您从 [千文控制台](https://platform.qianwenai.com/home/api-keys) 获取的实际API密钥。"
3. **或者** 解释如何配置环境变量：`export DASHSCOPE_API_KEY='sk-...'` + 提供控制台URL。
4. **仅** 在用户**明确坚持**要求代理替他们完成时，才将实际密钥值写入 `.env`。

## 凭证优先级链

凭证按以下顺序加载（第一个匹配的优先）：

1. **环境变量** — `DASHSCOPE_API_KEY`（或 `QIANWEN_API_KEY` 别名）
2. **`.env` 文件** — 在当前工作目录，然后是代码库根目录（通过 `.git` 或 `skills/` 目录检测）。现有的环境变量不会被覆盖。

### 环境变量

| 变量名            | 用途                                                                                                                                   |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| `DASHSCOPE_API_KEY` | API密钥（必需）                                                                                                                        |
| `QIANWEN_API_KEY`      | `DASHSCOPE_API_KEY` 的别名。如果两者都设置，`QIANWEN_API_KEY` 优先级更高。                                                            |
| `QWEN_BASE_URL`     | 覆盖端点（可选；用于自定义部署或特定计划的Base URL）                                                        |
| `QWEN_TMP_OSS_BUCKET` | 文件上传的自定义OSS桶（替换48小时临时存储）。参见 [custom-oss.md](references/custom-oss.md)。                         |
| `QWEN_TMP_OSS_REGION` | OSS区域（当 `QWEN_TMP_OSS_BUCKET` 设置时必需）。                                                                              |
| `QWEN_TMP_OSS_AK_ID` / `AK_SECRET` | OSS凭证（使用权限最低的RAM用户：`oss:PutObject` + `oss:GetObject`）。如果未设置，则回退到 `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET`。 |

## API密钥类型

千文有两种互斥的密钥类型：

| 密钥类型 | 格式 | 用途 |
|----------|------|------|
| **标准（按量付费）** | `sk-ws-xxxxx`（旧版 `sk-xxxxx`） | 脚本、应用程序和工具的API调用 |
| **令牌计划** | `sk-sp-xxxxx` | 交互式AI工具及其调用的技能/代理扩展（针对当前用户） |

捆绑执行的技能接受两种密钥类型，并将 `sk-sp-` 请求路由到令牌计划端点。
在进行令牌计划请求之前，获取并读取当前的 [令牌计划模型目录](https://alioth.alicdn.com/skills-info/models/references/qianwen-token-plan-models.md)，并传递一个精确支持的模型。不要探测模型或自动回退。如果CDN访问失败，请使用 [本地回退](cdn/references/qianwen-token-plan-models.md)。

### 检测密钥类型（非明文）

要从API密钥确定调用模式而不完全暴露它，请检查前缀（前6个字符）：

```bash
echo ${DASHSCOPE_API_KEY:0:6}
```

| 前缀输出 | 密钥类型 | 计费模式 |
|----------|----------|-------------------|
| `sk-sp-` | 令牌计划 | 积分计费；有限模型目录 |
| `sk-ws-` 或其他 `sk-...` | 标准（按量付费） | 按token计费；完整模型目录 |

如果无法访问shell，请询问用户他们的密钥是否以 `sk-sp-` 开头。

### 查看账单

使用 **qianwen-usage** 技能直接查询使用情况、免费套餐配额和账单。或者，账单详情可在千文控制台中获取：

| 密钥类型 | 账单页面 |
|----------|----------|
| 标准（按量付费） | [按量付费账单](https://platform.qianwenai.com/home/billing/pay-as-you-go) |
| 令牌计划 | [令牌计划订阅](https://platform.qianwenai.com/home/billing/subscription/token-plan) |
| 使用分析（按量付费） | [使用分析](https://platform.qianwenai.com/home/analytics) |

> **绝对不要编造、猜测或构造使用/账单/控制台URL。** 仅提供本技能中列出的确切链接。如果此处未列出URL，请不要编造。

## 获取API密钥

1. 打开 [千文控制台](https://platform.qianwenai.com/home/api-keys)
2. 使用您的千文账户登录
3. 从API密钥管理部分创建或复制API密钥
4. 按量付费密钥以 `sk-ws-` 开头（旧版 `sk-`）；令牌计划密钥以 `sk-sp-` 开头

## 安全最佳实践

- **不要在源代码或提交到版本控制的配置文件中硬编码API密钥**
- **使用环境变量** 或 `.env` 文件（并将 `.env` 添加到 `.gitignore`）
- **定期轮换密钥** 并立即撤销泄露的密钥
- **使用最小权限** — 尽可能为特定应用程序创建专用密钥

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

使用简单的curl请求测试认证：

```bash
curl -sS -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"Hi"}]}'
```

成功响应将返回包含 `choices` 和 `message.content` 的JSON。

## 认证错误处理

千文API密钥仅限于千文控制台。无效或匹配错误的密钥将产生 `401 Unauthorized`。

### 触发条件

当**任何**子技能收到 `401` 响应，并且非明文检查显示密钥已设置（例如 `[ -n "$DASHSCOPE_API_KEY" ]`；不要输出密钥值）时。

### 探测命令

发送轻量级请求以验证认证：

```bash
curl -sS -o /dev/null -w "%{http_code}" \
  -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"hi"}]}'
```

### 收到401：强制交互式解决

如果探测返回401，请按以下顺序执行这些步骤：

**步骤1 — 确认密钥来源：**

```
您的API密钥认证失败。

请确认：
1. 您的密钥是在 platform.qianwenai.com/home 创建的（千文控制台）→ 重新验证密钥
2. 我的密钥可能无效 → 在 platform.qianwenai.com/home/api-keys 创建一个新的
```

**步骤2 — 应用用户的选择：**

| 用户说                         | 操作                                                              |
|--------------------------------|---------------------------------------------------------------------|
| 密钥来自千文控制台 | 重新运行验证以确认密钥是否有效                                    |
| 密钥可能无效                | 指导用户在 `platform.qianwenai.com/home/api-keys` 创建新密钥 |

**步骤3 — 重新运行验证。**

**步骤4 — 如果仍然401**，密钥本身无效——指导用户从 [千文控制台](https://platform.qianwenai.com/home/api-keys) 创建一个新的。

## 验证

运行上述curl验证命令。通过标准：HTTP 200响应，包含有效的JSON，其中包含 `choices` 和 `message.content`。将输出保存到 `output/qianwen-ops-auth/` 以供证据。

## 输出和证据

- 将验证结果和任何诊断输出保存到 `output/qianwen-ops-auth/`。
- 保留成功的认证测试记录以供故障排除。

## 输出位置

优先选择**当前工作目录**。默认子目录：`./output/qianwen-ops-auth/`。

**写入禁止**：绝对不要将输出文件写入此技能的安装目录或任何 `skills/` 层级。所有生成的内容必须位于当前工作目录下的 `output/` 或用户指定路径。

## 更新检查（执行后强制要求）

当用户要求检查更新（例如 "检查更新"、"检查版本"、"是否有新版本"、"更新技能"）时：

1. **查找 qianwen-update-check**：在兄弟技能目录中查找 `qianwen-update-check/SKILL.md`。
2. **如果找到** — 运行：`python3 <qianwen-update-check-dir>/scripts/check_update.py --print-response` 并报告结果。如果用户要求强制检查，请使用 `--force`。
3. **如果未找到** — 您**必须**提供以下选项并**等待用户的响应**：

> 更新检查技能未安装。它可以帮助您了解新的 QianWen-AI/qianwen-ai 功能和错误修复。
>
> 1) **立即安装** — 我将为您运行安装命令
> 2) **暂时跳过** — 这次不做任何操作
> 3) **不再提醒我** — 永久抑制此提示

用户响应后：
- 用户选择 **1** → 运行：`npx skills add QianWen-AI/qianwen-ai --skill qianwen-update-check -y`，然后运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`
- 用户选择 **2** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --dismiss`，然后正常继续
- 用户选择 **3** → 运行：`python3 <this-skill-scripts-dir>/gossamer.py --never-install`，然后正常继续

## 参考文献

- [tokenplan.md](references/tokenplan.md) — 令牌计划与标准密钥的对比；CDN模型目录指针，积分计费，禁止使用，错误代码
- [custom-oss.md](references/custom-oss.md) — 生产文件上传的自定义OSS桶设置
- [sources.md](references/sources.md) — 官方文档URL（控制台，认证指南）
