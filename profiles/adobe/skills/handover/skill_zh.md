# 项目交接文档

为 Edge Delivery Services 项目生成全面的交接文档。协调为不同受众创建指南。

## 可用文档类型

| 指南 | 受众 | 技能 |
|------|------|------|
| **内容创作指南** | 内容作者和内容管理员 | `handover-author` |
| **开发者指南** | 开发者和技术团队 | `handover-developer` |
| **管理员指南** | 网站管理员和运维人员 | `handover-admin` |

---

## 执行流程

### 第 0 步：导航至项目根目录（必填）

```bash
cd "$(git rev-parse --show-toplevel)"
ls scripts/aem.js
```

如果不存在 `scripts/aem.js`，则告知用户此技能需要 AEM Edge Delivery Services 项目并停止。

所有后续步骤均从项目根目录执行。指南创建在 `project-guides/` 目录下。

---

### 第 0.5 步：清理过期配置

```bash
rm -f .claude-plugin/project-config.json
```

---

### 第 1 步：询问用户所需文档类型

使用 `AskUserQuestion` 并使用以下四个选项：

```json
AskUserQuestion({
  "questions": [{
    "question": "您希望我生成哪种类型的交接文档？",
    "header": "指南类型",
    "options": [
      {"label": "全部（推荐）", "description": "生成全部三个指南：内容创作、开发和管理员"},
      {"label": "内容创作指南", "description": "面向内容作者和管理员 - 模块、模板、发布"},
      {"label": "开发者指南", "description": "面向开发者 - 代码库、实现、设计令牌"},
      {"label": "管理员指南", "description": "面向网站管理员 - 权限、API 操作、缓存"}
    ],
    "multiSelect": false
  }]
})
```

### 第 1.5 步：获取组织名称

在用户选择指南类型后，确保在调用任何子技能前获取组织名称。

#### 1.5.1 检查已保存的组织

```bash
cat .claude-plugin/project-config.json 2>/dev/null | node -e "
  const d = require('fs').readFileSync(0,'utf8');
  try { const o = JSON.parse(d).org; if(o) console.log('org: ' + o); } catch(e) {}
"
```

#### 1.5.2 从 Git 获取站点名称

```bash
SITE=$(basename -s .git $(git remote get-url origin 2>/dev/null) 2>/dev/null)
echo "site=${SITE:-NOT SET}"
```

#### 1.5.3 提示输入组织名称（若未保存）

如果未保存组织名称，则询问用户：

> "您的 Config Service 组织名称是什么？这是您 Edge Delivery Services URL 中的 `{org}` 部分（例如，`https://main--site--{org}.aem.page`）。组织名称可能与您的 GitHub 组织不同。
>
> 您可以提供组织名称或预览/生产 URL。"

以纯文本问题形式询问，不要使用 `AskUserQuestion` 带选项。组织名称是必填项。

如果用户提供 URL，则从中解析组织名称：

```bash
URL="$USER_INPUT"
if echo "$URL" | grep -q '\.aem\.page\|\.aem\.live'; then
  HOST_PART=$(echo "$URL" | cut -d'/' -f3 | cut -d'.' -f1)
  ORG=$(echo "$HOST_PART" | awk -F'--' '{print $NF}')
  echo "从 URL 解析：org=$ORG"
fi
```

#### 1.5.4 保存组织名称

```bash
mkdir -p .claude-plugin
grep -qxF '.claude-plugin/' .gitignore 2>/dev/null || echo '.claude-plugin/' >> .gitignore

# 仅当选择“全部（推荐）”时才包含 allGuides 标志
echo '{"org": "{ORG_NAME}"}' > .claude-plugin/project-config.json
# 或对于“全部（推荐）”：
echo '{"org": "{ORG_NAME}", "allGuides": true}' > .claude-plugin/project-config.json
```

将 `{ORG_NAME}` 替换为实际组织名称。仅当用户选择“全部（推荐）”时才包含 `"allGuides": true` — 这将指示子技能跳过步骤 0 验证。

### 第 1.6 步：认证

检查有效的认证令牌：

```bash
AUTH_TOKEN=$(node -e "
  const fs = require('fs');
  try {
    const t = JSON.parse(fs.readFileSync(process.env.HOME + '/.aem/ims-token.json', 'utf8'));
    if (t.authToken && t.authTokenExpiry > Math.floor(Date.now()/1000) + 60) {
      process.stdout.write(t.authToken);
    }
  } catch (e) {}
")

if [ -n "$AUTH_TOKEN" ]; then
  echo "令牌有效"
else
  echo "令牌缺失或过期。"
fi
```

如果没有有效令牌，则调用认证技能：

```
Skill({ skill: "aem-project-management:auth" })
```

在此处认证意味着所有并行运行的子技能都可以使用保存的令牌，而无需分别提示登录。

### 第 1.7 步：验证组织名称

认证后，验证组织名称：

```bash
AUTH_TOKEN=$(node -e "
  const fs = require('fs');
  try {
    const t = JSON.parse(fs.readFileSync(process.env.HOME + '/.aem/ims-token.json', 'utf8'));
    process.stdout.write(t.authToken || '');
  } catch (e) {}
")
ORG=$(cat .claude-plugin/project-config.json | node -e "
  const d = require('fs').readFileSync(0,'utf8');
  process.stdout.write(JSON.parse(d).org || '');
")
curl -s -w "\nHTTP: %{http_code}" -H "x-auth-token: ${AUTH_TOKEN}" \
  "https://admin.hlx.page/config/${ORG}/sites.json"
```

如果 HTTP 200：组织名称有效，继续执行步骤 2。

如果非 200：告知用户组织名称似乎不正确，并请求正确名称。更新 `.claude-plugin/project-config.json` 并重试，直到 HTTP 200。

### 第 2 步：调用相应技能

| 选择 | 操作 |
|------|------|
| **全部** | 并行调用三个技能（见步骤 3） |
| **内容创作指南** | `Skill({ skill: "aem-project-management:handover-author" })` |
| **开发者指南** | `Skill({ skill: "aem-project-management:handover-developer" })` |
| **管理员指南** | `Skill({ skill: "aem-project-management:handover-admin" })` |

对于单指南选择，直接从主对话调用技能（不通过 Agent），以便权限提示能到达用户。

### 第 3 步：对于“全部”选择 — 并行执行

提供立即反馈：

```
"开始并行生成全部 3 个交接指南：
  内容创作指南 - 分析模块、模板、配置...
  开发者指南 - 分析代码、模式、架构...
  管理员指南 - 分析部署、安全、运维..."
```

以**单条消息**（前台模式）同时启动所有三个代理。**不要**使用 `run_in_background: true`。告知每个代理读取子技能 SKILL.md 并直接遵循其指示 — **不要**告知代理调用 Skill 工具。

```javascript
Agent({
  description: "生成内容创作指南",
  prompt: "您正在为一个 AEM Edge Delivery Services 项目生成内容创作指南，项目根目录为 {PROJECT_ROOT}。读取技能说明文件 {PLUGIN_ROOT}/skills/handover-author/SKILL.md 并遵循其指示生成指南。项目配置在 .claude-plugin/project-config.json（组织、allGuides 已设置 — 跳过阶段 0 和认证）。认证令牌在 ~/.aem/ims-token.json。从阶段 1 开始。对于 PDF 转换，读取 {PLUGIN_ROOT}/skills/whitepaper/SKILL.md 并遵循其指示。**不要**使用 Skill 工具 — 直接使用 Bash、Read 和 Write 工具执行所有步骤。"
})

Agent({
  description: "生成开发者指南",
  prompt: "您正在为一个 AEM Edge Delivery Services 项目生成开发者指南，项目根目录为 {PROJECT_ROOT}。读取技能说明文件 {PLUGIN_ROOT}/skills/handover-developer/SKILL.md 并遵循其指示生成指南。项目配置在 .claude-plugin/project-config.json（组织、allGuides 已设置 — 跳过阶段 0 和认证）。认证令牌在 ~/.aem/ims-token.json。从阶段 1 开始。对于 PDF 转换，读取 {PLUGIN_ROOT}/skills/whitepaper/SKILL.md 并遵循其指示。**不要**使用 Skill 工具 — 直接使用 Bash、Read 和 Write 工具执行所有步骤。"
})

Agent({
  description: "生成管理员指南",
  prompt: "您正在为一个 AEM Edge Delivery Services 项目生成管理员指南，项目根目录为 {PROJECT_ROOT}。读取技能说明文件 {PLUGIN_ROOT}/skills/handover-admin/SKILL.md 并遵循其指示生成指南。项目配置在 .claude-plugin/project-config.json（组织、allGuides 已设置 — 跳过阶段 0 和认证）。认证令牌在 ~/.aem/ims-token.json。从阶段 1 开始。对于 PDF 转换，读取 {PLUGIN_ROOT}/skills/whitepaper/SKILL.md 并遵循其指示。**不要**使用 Skill 工具 — 直接使用 Bash、Read 和 Write 工具执行所有步骤。"
})
```

将 `{PROJECT_ROOT}` 替换为实际项目根路径（`git rev-parse --show-toplevel` 的输出）。

使用以下命令确定 `{PLUGIN_ROOT}`：

```bash
PLUGIN_ROOT=$([ -d ".claude/plugins/aem-project-management" ] && echo ".claude/plugins/aem-project-management" || echo "$CLAUDE_PLUGIN_ROOT")
```

当所有三个完成时，报告最终总结：

```
"交接文档生成完成：

project-guides/
├── AUTHOR-GUIDE.pdf
├── DEVELOPER-GUIDE.pdf
└── ADMIN-GUIDE.pdf

所有 PDF 已生成。源文件已清理。"
```

---

## 输出文件

| 选择 | 输出文件 |
|------|----------|
| 全部 | `project-guides/AUTHOR-GUIDE.pdf`, `project-guides/DEVELOPER-GUIDE.pdf`, `project-guides/ADMIN-GUIDE.pdf` |
| 内容创作指南 | `project-guides/AUTHOR-GUIDE.pdf` |
| 开发者指南 | `project-guides/DEVELOPER-GUIDE.pdf` |
| 管理员指南 | `project-guides/ADMIN-GUIDE.pdf` |

每个子技能在完成指南后立即生成 PDF。所有源文件（.md, .html, .plain.html）在生成 PDF 后被清理。

---

## 相关技能

- `aem-project-management:handover-author` — 内容创作/管理员的指南
- `aem-project-management:handover-developer` — 开发者技术指南
- `aem-project-management:handover-admin` — 管理员运维指南
- `aem-project-management:whitepaper` — PDF 生成（由每个子技能调用）
