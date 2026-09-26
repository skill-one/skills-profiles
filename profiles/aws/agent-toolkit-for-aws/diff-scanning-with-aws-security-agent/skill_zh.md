# AWS 安全代理 — 差异扫描

仅扫描自 git 引用以来变更的代码。比全量扫描更快 — 将发现结果聚焦于差异。无需先进行全量扫描。

## 本地状态

读取 `.security-agent/config.json` 获取 `agent_space_id` 和 `region`。若缺失，请先运行 `setup-security-agent` 工作流。

在 `.security-agent/scans.json` 中跟踪扫描记录。

### 解析所需值

| 占位符 | 解析方法 |
|-------|---------|
| `<id>` (代理空间) | `config.agent_space_id` |
| `<region>` | `config.region` (默认 `us-east-1`) |
| `<account>` | `aws sts get-caller-identity --query Account --output text` |
| `<role-arn>` | `arn:aws:iam::<account>:role/SecurityAgentScanRole` |
| `<bucket>` | `security-agent-scans-<account>-<region>` |
| `<WORKSPACE_ID>` | `printf '%s' "$(pwd)" \| md5sum \| cut -c1-12` |

---

## 工作流

1. **预扫描检查。** 与全量扫描相同 — 读取配置、验证代理空间、解析值、生成工作空间 ID。

2. **询问扫描目标：**
   - 未提交变更 → `BASE_REF=HEAD` (默认)
   - 分支与主分支对比 → `BASE_REF=main`
   - 自定义引用 → 用户提供

3. **生成差异 (若为空则快速失败)：**

   ```bash
   cd <绝对工作空间路径>
   if [ "$BASE_REF" = "HEAD" ]; then
     git diff HEAD > /tmp/diff.patch
   else
     git diff "$BASE_REF..HEAD" > /tmp/diff.patch
   fi
   [ -s /tmp/diff.patch ] || { echo "与 $BASE_REF 无变更"; exit 1; }
   ```

4. **压缩工作空间** (与全量扫描相同的排除项，2 GB 限制)：

   ```bash
   cd <绝对工作空间路径>
   zip -r /tmp/source.zip . \
     -x ".git/*" -x ".security-agent/*" -x "node_modules/*" \
     -x "__pycache__/*" -x ".venv/*" -x "venv/*" \
     -x "dist/*" -x "build/*" -x "target/*" \
     -x ".mypy_cache/*" -x ".pytest_cache/*" -x ".tox/*" \
     -x ".next/*" -x "cdk.out/*" -x ".DS_Store" -x "*.pyc"
   ```

5. **上传源码压缩包和差异补丁：**

   ```bash
   SCAN_ID="diff-$(date +%s)-$(openssl rand -hex 3)"
   aws s3 cp /tmp/source.zip s3://<bucket>/security-scans/source/<WORKSPACE_ID>/source.zip --expected-bucket-owner <account>
   aws s3 cp /tmp/diff.patch s3://<bucket>/security-scans/diffs/${SCAN_ID}/diff.patch --expected-bucket-owner <account>
   ```

6. **获取或创建每个工作空间的 CodeReview** (与全量扫描相同逻辑 — 查找 `config.json → code_reviews[<abs_path>]`，若不存在则创建)：

   ```bash
   aws securityagent create-code-review --agent-space-id <id> --title <title> \
     --service-role <role-arn> \
     --assets sourceCode=[{s3Location=s3://<bucket>/security-scans/source/<WORKSPACE_ID>/source.zip}]
   ```

7. **启动差异任务：**

   ```bash
   aws securityagent start-code-review-job --agent-space-id <id> --code-review-id <cr-id> \
     --diff-source s3Uri=s3://<bucket>/security-scans/diffs/${SCAN_ID}/diff.patch
   ```

   若 `ResourceNotFoundException`：重新创建 CodeReview 并重试。

8. 捕获 `codeReviewJobId`。持久化到 `scans.json`，记录 `scan_type: "DIFF"` 和 `base_ref`。

9. 告知用户："差异扫描已启动。需要几分钟。我将每 2 分钟检查一次 — 说 '停止轮询' 可退出。"

10. **每 2 分钟轮询：**

    ```bash
    aws securityagent batch-get-code-review-jobs --agent-space-id <id> --code-review-job-ids <job_id>
    ```

    仅在状态变更时响应。完成时 → 获取发现结果。

11. **发现结果：** 与全量扫描相同呈现 — 按严重程度分组，报告写入 `.security-agent/findings-{scan_id}.md`。

---

## 规则

- 差异扫描独立运行 — 无需先进行全量扫描
- 每 2 分钟轮询，不能更快
- 若用户未指定，默认 `BASE_REF=HEAD`
- 标题：`diff-<git-分支>-<时间戳>` (无空格)
- 若差异为空，告知用户并停止 — 不启动扫描
