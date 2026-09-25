# Shannon：用于 Web 应用和 API 的自主式 AI 渗透测试工具

> **权限概述**：此技能协调运行基于 Docker 的渗透测试工具 Shannon，该工具会主动对目标应用程序执行攻击。它会本地克隆/更新 Shannon 仓库，运行 Docker 容器，并读取渗透测试报告。**Shannon 执行真实的漏洞利用——仅对您拥有所有权或已获得明确书面授权进行测试的应用程序运行。**切勿在生产系统上运行。

Shannon 分析您的源代码，识别攻击向量，并执行真实的漏洞利用，以在漏洞到达生产环境之前证明其存在性。在 XBOW 安全基准测试中，96.15% 的漏洞利用成功率。涵盖 OWASP Top 10：注入、XSS、SSRF、损坏的身份验证、损坏的身份验证授权，以及更多内容。

---

## 关键：安全检查（始终首先运行）

在执行任何操作之前，您必须确认：

1. **授权**：询问用户——“您是否有明确授权对目标进行渗透测试？”如果他们回答没有或不确定，请停止并解释他们需要获得系统所有者的书面许可。
2. **环境**：确认目标是本地、测试或沙盒环境——**绝不能是生产环境**。
3. **范围**：明确他们想要测试的内容（全面渗透测试还是特定类别）。

```
⚠️  Shannon 执行真实的攻击，具有改变性的效果。
├─ 仅在您拥有或已获得书面授权进行测试的系统上运行
├─ 切勿针对生产环境
├─ 结果需要人工审核——LLM 输出可能包含幻觉
└─ 您需要遵守所有适用的法律
```

在每次渗透测试运行之前显示此警告。如果用户在本会话中已经确认了授权，则只需简要提醒即可。

---

## 解析用户意图

从用户的输入中提取：

1. **TARGET_URL**：渗透测试的 URL（例如，`http://localhost:3000`，`http://staging.example.com`）
2. **REPO_NAME**：源代码文件夹名称（放置在 Shannon 内部的 `./repos/` 中）
3. **SCOPE**：全面渗透测试（默认）或特定类别（注入、xss、ssrf、auth、authz）
4. **WORKSPACE**：用于恢复功能的命名工作区（可选）
5. **CONFIG**：自定义 YAML 配置路径（可选，用于身份验证流程、聚焦/忽略规则）

常见的调用模式：
- `/shannon http://localhost:3000 myapp` → 本地应用的全面渗透测试
- `/shannon --workspace=audit1 http://staging.example.com backend-api` → 用于恢复的命名工作区
- `/shannon --scope=xss,injection http://localhost:8080 frontend` → 目标类别
- `/shannon status` → 检查正在运行的渗透测试
- `/shannon results` → 显示最新报告
- `/shannon stop` → 停止正在运行的渗透测试

显示解析的意图：
```
🔐 Shannon 渗透测试
├─ 目标：{TARGET_URL}
├─ 源代码：repos/{REPO_NAME}
├─ 范围：{SCOPE 或 "全面（所有 5 个 OWASP 类别）"}
├─ 工作区：{WORKSPACE 或 "自动生成"}
└─ 配置：{CONFIG 或 "默认"}

预计运行时间：1–1.5 小时 │ 预计成本：~$50 (Claude Sonnet)
```

---

## 第 0 步：确保已安装 Shannon

检查是否已本地克隆 Shannon：

```bash
SHANNON_HOME="${SHANNON_HOME:-$HOME/shannon}"

if [ -d "$SHANNON_HOME" ] && [ -f "$SHANNON_HOME/shannon" ]; then
  echo "Shannon 位于 $SHANNON_HOME"
  cd "$SHANNON_HOME" && git pull --ff-only 2>/dev/null || true
else
  echo "未找到 Shannon。正在克隆..."
  git clone https://github.com/KeygraphHQ/shannon.git "$SHANNON_HOME"
fi

# 验证 Docker 是否可用
if command -v docker &>/dev/null; then
  echo "Docker: $(docker --version)"
else
  echo "错误：需要 Docker。安装 Docker Desktop：https://docker.com/products/docker-desktop"
  exit 1
fi
```

如果未安装 Shannon，请克隆它并通知用户。如果缺少 Docker，请停止并告诉他们安装它。

**SHANNON_HOME** 默认为 `~/shannon`。用户可以使用 `SHANNON_HOME` 环境变量覆盖。

---

## 第 1 步：准备源代码

Shannon 需要目标的源代码在 `$SHANNON_HOME/repos/{REPO_NAME}/`。

询问用户他们的源代码位置：

```bash
# 如果用户提供本地路径
REPO_PATH="/path/to/their/source"
REPO_NAME="myapp"

# 创建符号链接或复制到 Shannon 的 repos 目录
mkdir -p "$SHANNON_HOME/repos"
if [ ! -d "$SHANNON_HOME/repos/$REPO_NAME" ]; then
  ln -s "$(realpath "$REPO_PATH")" "$SHANNON_HOME/repos/$REPO_NAME"
  echo "链接 $REPO_PATH → repos/$REPO_NAME"
fi
```

如果用户提供 GitHub URL：
```bash
cd "$SHANNON_HOME/repos"
git clone "$GITHUB_URL" "$REPO_NAME"
```

---

## 第 2 步：配置身份验证（如果需要）

如果目标需要登录，请帮助用户创建 YAML 配置：

```yaml
# $SHANNON_HOME/configs/target-config.yaml
authentication:
  type: form            # "form" 或 "sso"
  login_url: "http://localhost:3000/login"
  credentials:
    username: "admin"
    password: "password123"
  flow: "导航到登录页面，输入用户名和密码，点击 Sign In"
  success_condition:
    url_contains: "/dashboard"

rules:
  avoid:
    - "/logout"
    - "/admin/delete"
  focus:
    - "/api/"
    - "/auth/"

pipeline:
  max_concurrent_pipelines: 5  # 1-5，默认为 5
```

**仅在目标需要身份验证或具有特定范围规则时创建配置。**对于开放/未身份验证的目标，不需要配置。

---

## 第 3 步：验证 API 凭据

检查 AI 提供商凭据是否可用：

```bash
cd "$SHANNON_HOME"

# 检查 Anthropic API 密钥（主要）
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "✅ ANTHROPIC_API_KEY 已设置"
elif [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
  echo "✅ CLAUDE_CODE_OAUTH_TOKEN 已设置"
elif [ "${CLAUDE_CODE_USE_BEDROCK:-}" = "1" ]; then
  echo "✅ 启用 AWS Bedrock 模式"
elif [ "${CLAUDE_CODE_USE_VERTEX:-}" = "1" ]; then
  echo "✅ 启用 Google Vertex AI 模式"
else
  echo "❌ 未找到 AI 凭据。"
  echo "设置其中一个：ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN，或启用 Bedrock/Vertex"
  exit 1
fi
```

如果未找到凭据，请解释选项：
- **直接 API**（推荐）：`export ANTHROPIC_API_KEY=sk-ant-...`
- **OAuth**：`export CLAUDE_CODE_OAUTH_TOKEN=...`
- **AWS Bedrock**：`export CLAUDE_CODE_USE_BEDROCK=1` + AWS 凭据
- **Google Vertex**：`export CLAUDE_CODE_USE_VERTEX=1` + 在 `./credentials/` 中的服务账户

还建议：`export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000`

---

## 第 4 步：启动渗透测试

**关键：在启动前与用户确认。**显示完整命令并等待批准。

```bash
cd "$SHANNON_HOME"

# 构建命令
CMD="./shannon start URL={TARGET_URL} REPO={REPO_NAME}"

# 添加可选标志
# CONFIG=configs/target-config.yaml  （如果存在身份验证配置）
# WORKSPACE={WORKSPACE}              （如果用户指定）
# OUTPUT=./audit-logs/               （默认）

echo "准备启动："
echo "  $CMD"
echo ""
echo "这将启动 Docker 容器并开始渗透测试。"
echo "运行时间：~1-1.5 小时 │ 成本：~$50 (Claude Sonnet)"
```

用户确认后，在后台运行：
```bash
cd "$SHANNON_HOME" && ./shannon start URL={TARGET_URL} REPO={REPO_NAME} {EXTRA_FLAGS}
```

使用 `run_in_background: true` 和 600000ms（10 分钟）的超时进行初始设置。渗透测试本身在 Docker 中运行，并将独立继续。

---

## 第 5 步：监控进度

在渗透测试运行期间，用户可以检查状态：

```bash
cd "$SHANNON_HOME"

# 列出活动工作区
./shannon workspaces

# 查看特定工作流的日志
./shannon logs ID={workflow-id}
```

解释 5 阶段管道：
```
Shannon 管道（5 阶段，尽可能并行）：
├─ 阶段 1：预侦察——源代码分析 + 外部扫描（Nmap、Subfinder、WhatWeb）
├─ 阶段 2：侦察——通过浏览器自动化映射实时攻击面
├─ 阶段 3：漏洞分析——5 个并行代理（注入、XSS、SSRF、Auth、AuthZ）
├─ 阶段 4：漏洞利用——专用代理执行真实攻击以验证发现
└─ 阶段 5：报告——包含可重复的 PoC 的执行摘要
```

---

## 第 6 步：阅读和解释结果

报告保存在 `$SHANNON_HOME/audit-logs/{hostname}_{sessionId}/`。

```bash
cd "$SHANNON_HOME"

# 查找最新报告
LATEST=$(ls -td audit-logs/*/ 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  echo "最新报告：$LATEST"
  # 查找主报告文件
  find "$LATEST" -name "*.md" -type f | head -5
fi
```

阅读报告并呈现摘要：

```
🔐 Shannon 渗透测试报告：{TARGET}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 严重：{N} 个漏洞
🟠 高：{N} 个漏洞
🟡 中：{N} 个漏洞
🔵 低：{N} 个漏洞

主要发现：
1. [严重] {Vuln type} — {location} — PoC: {brief description}
2. [高] {Vuln type} — {location} — PoC: {brief description}
3. ...

每个发现都包含可重复的 PoC 漏洞利用。
```

**重要提示：Shannon 的“无漏洞，无报告”策略意味着每个发现都有一个可工作的 PoC。**但请提醒用户，LLM 生成的內容需要人工审核。

---

## 实用命令

### 检查状态
```bash
cd "$SHANNON_HOME" && ./shannon workspaces
```

### 查看日志
```bash
cd "$SHANNON_HOME" && ./shannon logs ID={workflow-id}
```

### 停止渗透测试
```bash
cd "$SHANNON_HOME" && ./shannon stop
```

### 停止并清理所有数据
```bash
# 破坏性操作——首先与用户确认
cd "$SHANNON_HOME" && ./shannon stop CLEAN=true
```

### 恢复先前工作区
```bash
cd "$SHANNON_HOME" && ./shannon start URL={URL} REPO={REPO} WORKSPACE={name}
```

---

## 针对本地应用

如果用户的应用在 localhost 上运行，请解释：
```
Shannon 在 Docker 内部运行。要访问您的本地应用：
├─ 使用 http://host.docker.internal:{PORT} 而不是 http://localhost:{PORT}
├─ macOS/Windows：Docker Desktop 自动工作
└─ Linux：在 docker run 中添加 --add-host=host.docker.internal:host-gateway
```

自动将命令中的 `localhost` URL 转换为 `host.docker.internal`。

---

## 配置参考

### 环境变量
| 变量 | 必需 | 描述 |
|------|------|------|
| `ANTHROPIC_API_KEY` | 其中之一 | 直接 Anthropic API 密钥 |
| `CLAUDE_CODE_OAUTH_TOKEN` | 必需 | Anthropic OAuth 令牌 |
| `CLAUDE_CODE_USE_BEDROCK` | | 设置为 `1` 以启用 AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | | 设置为 `1` 以启用 Google Vertex AI |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 推荐 | 设置为 `64000` |
| `SHANNON_HOME` | 可选 | Shannon 安装目录（默认：`~/shannon`） |

### YAML 配置选项
| 部分 | 字段 | 描述 |
|------|------|------|
| `authentication.type` | `form` / `sso` | 登录方法 |
| `authentication.login_url` | URL | 登录页面 |
| `authentication.credentials` | 对象 | username, password, totp_secret |
| `authentication.flow` | 字符串 | 自然语言登录说明 |
| `authentication.success_condition` | 对象 | `url_contains` 或 `element_present` |
| `rules.avoid` | 列表 | 跳过路径/子域名 |
| `rules.focus` | 列表 | 优先处理路径/子域名 |
| `pipeline.retry_preset` | `subscription` | 扩展退避（用于速率限制计划） |
| `pipeline.max_concurrent_pipelines` | 1-5 | 并行代理数量（默认：5） |

---

## 漏洞覆盖范围

Shannon 测试 50 多个特定案例，涵盖 5 个 OWASP 类别：

| 类别 | 示例 |
|------|------|
| **注入** | SQL 注入、命令注入、SSTI、NoSQL 注入 |
| **XSS** | 反射型、存储型、DOM-based、通过文件上传 |
| **SSRF** | 内部服务访问、云元数据、协议走私 |
| **损坏的身份验证** | 默认凭据、JWT 缺陷、会话固定、MFA 绕过、CSRF |
| **损坏的身份验证授权** | IDOR、权限提升、路径遍历、强制浏览 |

---

## 集成安全工具（Docker 内捆绑）

- **Nmap** — 端口扫描和服务检测
- **Subfinder** — 子域名枚举
- **WhatWeb** — 网络技术指纹识别
- **Schemathesis** — 基于 API 模板的模糊测试
- **Chromium** — 无头浏览器，用于自动化漏洞利用（Playwright）

---

## 上下文记忆

对于此对话的其余部分，请记住：
- **SHANNON_HOME**：Shannon 安装路径
- **TARGET_URL**：正在测试的 URL
- **REPO_NAME**：源代码文件夹名称
- **WORKSPACE**：工作区名称（如果有）
- **PENTEST_STATUS**：运行中 / 已完成 / 已停止

当用户提出后续问题时：
- 检查渗透测试状态并报告进度
- 阅读并解释来自 audit-logs 的新发现
- 帮助修复发现的漏洞
- 解释 PoC 漏洞利用及其影响

---

## 安全与权限

**此技能的功能：**
- 从 GitHub 克隆/更新 Shannon 仓库到 `~/shannon`（或 `$SHANNON_HOME`）
- 从用户的源代码创建符号链接到 `~/shannon/repos/`
- 通过 `./shannon` CLI 启动 Docker 容器（Temporal 服务器、工作器、可选路由器）
- 从 `~/shannon/audit-logs/` 读取渗透测试报告
- 可选地创建 YAML 配置文件在 `~/shannon/configs/`

**Shannon 在 Docker 内的功能：**
- 对目标 URL 执行真实漏洞利用（SQL 注入、XSS、SSRF 等）
- 使用 Nmap、Subfinder、WhatWeb、Schemathesis 进行扫描
- 通过无头 Chromium 自动化浏览器交互
- 向 Anthropic API（或 Bedrock/Vertex）发送提示以进行推理
- 将报告写入 `audit-logs/` 目录

**此技能不会执行的操作：**
- 未经用户确认不会针对任何系统
- 不会存储或传输 API 密钥（除非配置的提供者）
- 不会修改用户的源代码
- 除非明确指示，否则不会访问生产系统（它会警告不要这样做）
- 没有 Docker 就不会运行——所有攻击工具都是容器化的

**在首次使用前审查 Shannon 源代码：** https://github.com/KeygraphHQ/shannon
