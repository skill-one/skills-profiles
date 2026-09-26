# AWS 安全代理 — 代码扫描

此技能处理完整仓库扫描。设置（代理空间、角色、存储桶）由 **`setup-security-agent`** 技能处理 — 如果缺少 `.security-agent/config.json`，扫描工作流将自动先执行设置。

---

## 动作映射

| 用户意图 | 工作流 |
|-------------|----------|
| 直接扫描请求（"扫描我的代码"、"查找漏洞"） | 完整扫描 |
| 扫描状态检查（"扫描状态如何"、"进度"） | 状态工作流 |
| 查看结果（"发现了什么"、"显示结果"） | 结果工作流 |
| 列出扫描（"最近扫描"、"显示我的扫描"） | 读取 `.security-agent/scans.json` |
| 停止扫描 | `aws securityagent stop-code-review-job` |

### 主动建议的规则

- 运行前始终询问 — 永不自动触发扫描
- 单行建议，不是多段文字的推销
- 如果用户拒绝，则在同一会话中不再提出

---

## 本地状态

读取 `.security-agent/config.json` 获取 `agent_space_id` 和 `region`。如果 `config.json` 缺失，向用户显示一行 — "此工作区首次扫描 — 首先运行设置。" — 并在工作流中直接运行 **`setup-security-agent`** 工作流（步骤来自该技能的 SKILL.md），然后继续。首次扫描应"即插即用"。

在 `.security-agent/scans.json` 中跟踪扫描（保留最后 50 条记录）。每个工作区的 CodeReview ID 存储在 `config.json → code_reviews[<abs_path>]` 中，以便后续扫描重用相同的 CodeReview。

### 解决所需值

以下 CLI 示例使用占位符。在每次扫描开始时解决它们：

| 占位符 | 如何解决 |
|-------------|----------------|
| `<id>`（代理空间） | `config.agent_space_id` |
| `<region>` | `config.region` (默认 `us-east-1`) |
| `<account>` | `aws sts get-caller-identity --query Account --output text` (缓存到当前回合剩余部分) |
| `<role-arn>` | `arn:aws:iam::<account>:role/SecurityAgentScanRole` |
| `<bucket>` | `security-agent-scans-<account>-<region>` |
| `<cr-id>` | `code_review_id` 来自 `config.json → code_reviews[<abs_path>]` |
| `<job_id>` | `codeReviewJobId` 由 `start-code-review-job` 返回 |
| `<WORKSPACE_ID>` | `printf '%s' "$(pwd)" \| md5sum \| cut -c1-12` |

这些是派生而非存储在配置中，因此它们永远不会与现实脱节。

---

## 扫描前检查

1. **读取 `config.json`。** 如果缺失 → 首先在工作流中运行 `setup-security-agent` 工作流，然后继续。
2. **验证代理空间仍然存在:**

   ```bash
   aws securityagent batch-get-agent-spaces --agent-space-ids <id>
   ```

   如果响应显示它不存在，清除 `agent_space_id` 并再次运行 `setup-security-agent`。
3. **从上面的表中解决账户、角色 ARN 和存储桶名称。**
4. **生成工作区 ID:**

   ```bash
   WORKSPACE_ID=$(printf '%s' "$(pwd)" | md5sum | cut -c1-12)
   ```

---

## 工作流：完整扫描 (~45 分钟)

仅扫描更改的代码，请使用 `diff-scanning-with-aws-security-agent` 技能。对于威胁建模规范，请使用 `threat-modeling-with-aws-security-agent`。

1. 运行上述预扫描检查。
2. **压缩工作区。** 排除常见的构建/缓存目录。尊重 `.gitignore`。如果压缩文件大于 2 GB，则中止。

   ```bash
   cd <绝对工作区路径>
   zip -r /tmp/source.zip . \
     -x ".git/*" \
     -x ".security-agent/*" \
     -x "node_modules/*" \
     -x "__pycache__/*" \
     -x ".venv/*" -x "venv/*" \
     -x "dist/*" -x "build/*" -x "target/*" \
     -x ".mypy_cache/*" -x ".pytest_cache/*" -x ".tox/*" \
     -x ".next/*" -x "cdk.out/*" \
     -x ".DS_Store" -x "Thumbs.db" \
     -x "*.pyc" -x "*.pyo"
   ZIP_BYTES=$(stat -f%z /tmp/source.zip 2>/dev/null || stat -c%s /tmp/source.zip)
   if [ "$ZIP_BYTES" -gt 2147483648 ]; then echo "Zip too large (>2GB)"; exit 1; fi
   ```

3. **上传** 到每个工作区的稳定密钥（覆盖任何先前的上传）:

   ```bash
   aws s3 cp /tmp/source.zip s3://<bucket>/security-scans/source/<WORKSPACE_ID>/source.zip --expected-bucket-owner <account>
   ```

4. **获取或创建每个工作区的 CodeReview。** 查找 `config.json → code_reviews[<abs_path>]`。
   - 如果存在，使用该 `code_review_id`。
   - 如果不存在，创建:

     ```bash
     aws securityagent create-code-review --agent-space-id <id> --title <title> \
       --service-role <role-arn> \
       --assets sourceCode=[{s3Location=s3://<bucket>/security-scans/source/<WORKSPACE_ID>/source.zip}]
     ```

     捕获 `codeReviewId` 并持久化到 `config.json → code_reviews[<abs_path>]`。
   - 标题默认：`pre-cr-<git-branch>`（使用 `git rev-parse --abbrev-ref HEAD`）。将任何空格替换为连字符。
5. **启动工作:**

   ```bash
   aws securityagent start-code-review-job --agent-space-id <id> --code-review-id <cr-id>
   ```

   - **如果响应是 `ResourceNotFoundException`**：CodeReview 被外部删除。重新创建它（步骤 4）并重试。
6. 捕获 `codeReviewJobId`。生成本地 `scan_id` 如 `scan-<8-hex>`。追加到 `scans.json`:

   ```json
   {
     "scan_id": "scan-...",
     "code_review_id": "cr-...",
     "job_id": "cj-...",
     "agent_space_id": "as-...",
     "scan_type": "FULL",
     "title": "pre-cr-main",
     "path": "/abs/path",
     "started_at": "2026-06-01T20:00:00Z",
     "status": "IN_PROGRESS"
   }
   ```

7. 告诉用户："完整扫描已启动（scan_id: {id}）。耗时约 45 分钟。我将每 5 分钟检查一次 — 说 '停止轮询' 以退出。"
8. 运行下面的 **轮询循环**，检查之间使用 `sleep 300`。

---

## 轮询循环

启动扫描后：

1. `sleep 300`（5 分钟）。不要比这更快地轮询。
2. 调用状态：

   ```bash
   aws securityagent batch-get-code-review-jobs --agent-space-id <id> --code-review-job-ids <job_id>
   ```

3. 比较 `status` 与上次看到的状态。仅在状态变化（例如，`IN_PROGRESS` → `COMPLETED`）或终端状态（`COMPLETED`、`FAILED`、`STOPPED`）时向用户响应。
4. 不要多次报告"仍在进行中" — 那是噪音。
5. 如果用户说"停止轮询"或"稍后检查" → 停止循环并告诉他们： "随时说 '扫描状态' 或 '显示结果'。"
6. 在 `COMPLETED` → 运行 **结果** 工作流。
7. 在 `FAILED` → 获取工作错误信息（如果存在 `statusReason`），告诉用户，将简要失败记录写入 `.security-agent/findings-{scan_id}.md`。

---

## 工作流：状态检查（临时）

用户说"扫描状态" / "扫描如何":

1. 如果用户指定 `scan_id`，使用它。否则使用 `scans.json` 中最新的条目。
2. 调用一次 `batch-get-code-review-jobs`。
3. 更新 `scans.json` 状态字段。
4. 报告：状态 + 已用时间 + 当前步骤（如果有）。

---

## 工作流：结果

扫描完成后（或用户请求）:

### 1. 获取结果（分页）

```bash
aws securityagent list-findings --agent-space-id <id> --code-review-job-id <job-id>
```

如果返回 `nextToken`，再次使用 `--next-token <token>` 调用，直到用尽。

### 2. 使用完整详细信息丰富

```bash
aws securityagent batch-get-findings --agent-space-id <id> --finding-ids <id1> <id2> ...
```

### 3. 过滤（可选）

如果用户要求最低严重性（例如，"高及以上"），过滤到该级别：

- 严重性顺序：CRITICAL > HIGH > MEDIUM > LOW > INFORMATIONAL.

### 4. 聊天中的简洁摘要

按严重性分组。每个文件路径 + 行号：

```
🟣 CRITICAL: {name}
   文件: {filePath}:{lineStart}
   {description}

🔴 HIGH: {name}
   文件: {filePath}:{lineStart}
   {description}

🟡 MEDIUM: {name}
   文件: {filePath}:{lineStart}
   {description}

🟢 LOW: {name}
   文件: {filePath}:{lineStart}
   {description}
```

### 5. 详细报告文件

写入 `.security-agent/findings-{scan_id}.md`。包括返回的每个字段（findingId、name、description、riskLevel、riskType、confidence、status、codeLocations with filePath/lineStart/lineEnd，如果存在 remediationCode 则包括它）。

```markdown
# 安全扫描报告 — {scan_id}

**扫描类型**: FULL
**标题**: {title}
**开始**: {started_at}
**总结果**: {count}

## 摘要
| 严重性 | 数量 |
|----------|-------|
| CRITICAL | N |
| HIGH | N |
| MEDIUM | N |
| LOW | N |

## 结果

### 🟣 CRITICAL: {name}
- **ID**: {findingId}
- **风险类型**: {riskType}
- **置信度**: {confidence}
- **状态**: {status}
- **位置**: `{filePath}:{lineStart}-{lineEnd}`

**描述**: {description}

**修复**:
{remediationCode 或来自描述的修复指导}

(repeat for every finding)
```

告诉用户： "完整详细信息写入到 `.security-agent/findings-{scan_id}.md`"

### 6. 跟进

询问：

- "您想先关注关键/高结果吗？"
- "我应该更详细地解释这些吗？"
- "想让我修复这些问题吗？"

对于修复：读取结果的描述和代码位置，然后合成并使用编辑工具应用修复。

---

## 工作流：停止扫描

用户说"停止扫描":

```bash
aws securityagent stop-code-review-job --agent-space-id <id> --code-review-job-id <job_id>
```

更新 `scans.json` 状态为 `STOPPED`。

---

## 工作流：列出最近扫描

用户询问"显示我的最近扫描" / "列出扫描":

读取 `.security-agent/scans.json`。以紧凑表格显示：

| scan_id | 类型 | 标题 | 状态 | 开始 |
|---------|------|-------|--------|---------|
| scan-abc | FULL | pre-cr-main | COMPLETED | 2h ago |
| scan-def | FULL | pre-cr-feature-x | FAILED | 1d ago |

---

## 规则

- 任何扫描前始终运行预扫描检查（配置存在 + 代理空间验证）
- 扫描 API 立即返回 — 每 5 分钟轮询状态
- 如果用户没有指定，使用 `scans.json` 中的最新扫描
- 标题不能包含空格 — 使用连字符。默认为 git 分支名。
- 不要直接转储 JSON — 使用严重性图标 + 文件位置格式化
- 从 `start-code-review-job` 获取 `ResourceNotFoundException`，重新创建 CodeReview 并重试一次

---

## 故障排除

- **"未配置" / `config.json` 缺失** → 首先运行 `setup-security-agent` 技能
- **`AccessDenied` on `s3 cp`** → 存储桶未在工作区注册，或信任策略错误。重新运行设置。
- **`403` / `ExpectedBucketOwner` 不匹配 on `s3 cp`** → 派生的存储桶由不同账户拥有（存储桶占用）。按设计拒绝上传 — 不要在没有保护的情况下重试。重新运行 `setup-security-agent`，它在外国拥有的存储桶上中止。
- **`ResourceNotFoundException` on agent space** → 它被删除了。重新运行设置。
- **扫描在 PREFLIGHT 挂起超过 10 分钟** → 后端问题，不是客户端。显示 `batch-get-code-review-jobs` 输出并告诉用户升级。
- **代码太大（zip > 2 GB）** → 在子目录上运行。
