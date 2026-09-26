# AWS 安全代理 — 设置

此技能处理一件事情：确保工作区有一个可用的代理空间、IAM 服务角色和 S3 存储桶关联在一起。扫描和渗透测试在单独的技能中执行，并假定这些工作已完成。

---

## 本地状态约定

所有安全代理技能共享工作区本地状态在 `.security-agent/`：

- `config.json` — `{ "agent_space_id": "as-...", "region": "us-east-1", "code_reviews": { "<abs_path>": "cr-..." } }`。账户 ID、角色 ARN 和存储桶名称按约定推导。`code_reviews` 映射允许扫描重用工作区的相同 CodeReview。
- `scans.json` — `{ scan_id, code_review_id, job_id, agent_space_id, scan_type, title, started_at, status, path }`（保留最后 50 条）
- `pentests.json` — 相同结构，用于渗透测试任务
- `.gitignore` — 内容为 `*`，使此目录保持未被跟踪
- `findings-{scan_id}.md` — 扫描技能在每次扫描完成后写入

此技能的工作是填充 `config.json` 并创建 `.gitignore`。

### 推导值（约定优于配置）

其他技能在每个调用时计算这些值，而不是从 `config.json` 中读取：

| 值 | 约定 |
|---|---|
| `ACCOUNT` | `aws sts get-caller-identity --query Account --output text` |
| `REGION` | `config.region`（默认 `us-east-1`） |
| `service_role_arn` | `arn:aws:iam::${ACCOUNT}:role/SecurityAgentScanRole` |
| `s3_bucket` | `security-agent-scans-${ACCOUNT}-${REGION}` |

为什么配置最小化：角色名称和存储桶名称是确定的，因此存储它们会增加漂移风险（用户手动重新创建角色将静默使用过时的路径）。只存储 `agent_space_id`，因为用户可能有多个代理空间，并且我们不想在每个会话中都询问是哪一个。

---

## 工作流程

1. **检查现有状态**：如果存在，读取 `.security-agent/config.json`。
2. **调用者身份 + 区域**：

   ```bash
   export ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
   export REGION="${AWS_REGION:-us-east-1}"
   ```

3. **代理空间**：
   - 如果 `config.agent_space_id` 已设置，使用以下命令验证：

     ```bash
     aws securityagent batch-get-agent-spaces --agent-space-ids <id>
     ```

     如果响应显示不存在，则视为缺失。
   - 如果缺失，列出现有：

     ```bash
     aws securityagent list-agent-spaces
     ```

     - 如果存在任何代理空间 → **向用户显示它们**，包括名称 + ID，并询问："您想重用其中一个，还是让我创建一个新的？" 等待答案。**不要自动选择。**
     - 如果用户选择一个，使用该 `agentSpaceId`。
     - 如果用户想要新的，或者不存在：

       ```bash
       aws securityagent create-agent-space --name security-scans
       ```

       捕获返回的 `agentSpaceId`。
4. **服务角色**（`SecurityAgentScanRole`，ARN `arn:aws:iam::$ACCOUNT:role/SecurityAgentScanRole`）：
   - 探测：

     ```bash
     aws iam get-role --role-name SecurityAgentScanRole
     ```

   - 如果返回 `NoSuchEntity`，则创建角色。**幂等性注意**：`create-role` 如果角色已存在，将失败并返回 `EntityAlreadyExists`。如果发生这种情况，则继续到 `update-assume-role-policy` 以确保信任策略正确。

     ```bash
     # 信任策略 — 包括 aws:SourceAccount 混乱代理保护
     cat > /tmp/sa-trust.json <<EOF
     {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"securityagent.amazonaws.com"},"Action":"sts:AssumeRole","Condition":{"StringEquals":{"aws:SourceAccount":"${ACCOUNT}"}}}]}
     EOF
     # 权限策略（S3 + CloudWatch Logs）
     cat > /tmp/sa-perms.json <<EOF
     {"Version":"2012-10-17","Statement":[
       {"Effect":"Allow","Action":["s3:GetObject","s3:GetObjectVersion","s3:ListBucket"],"Resource":["arn:aws:s3:::security-agent-scans-${ACCOUNT}-${REGION}","arn:aws:s3:::security-agent-scans-${ACCOUNT}-${REGION}/*"]},
       {"Effect":"Allow","Action":["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],"Resource":"arn:aws:logs:*:${ACCOUNT}:log-group:/aws/securityagent/*"}
     ]}
     EOF

     aws iam create-role --role-name SecurityAgentScanRole --assume-role-policy-document file:///tmp/sa-trust.json
     # if EntityAlreadyExists:
     aws iam update-assume-role-policy --role-name SecurityAgentScanRole --policy-document file:///tmp/sa-trust.json
     # always (re)apply permissions:
     aws iam put-role-policy --role-name SecurityAgentScanRole --policy-name SecurityAgentCodeReviewAccess --policy-document file:///tmp/sa-perms.json
     ```

5. **S3 存储桶**（`security-agent-scans-$ACCOUNT-$REGION`）：

   > **存储桶所有权强制执行（必需）**。存储桶名称由调用者的 AWS 账户 ID 和区域派生 — 两者都是非秘密且可以从 ARNs / ECR URI 公开派生的 — 因此任何第三方都可以预先注册（"抢占"）他们在自己的账户中的可预测名称。对派生存储桶的每个 S3 调用都必须传递 `--expected-bucket-owner "$ACCOUNT"`，以便如果存储桶由其他人拥有，操作将失败。对已存在但由其他账户拥有的存储桶的 `403 Forbidden` 是**致命的** — 中止设置并永不上传。

   - 探测（断言所有权）：

     ```bash
     BUCKET="security-agent-scans-${ACCOUNT}-${REGION}"
     NEED_CREATE=0
     if aws s3api head-bucket --bucket "$BUCKET" --expected-bucket-owner "$ACCOUNT" 2>/tmp/sa-head.err; then
       : # 存储桶存在且由此账户拥有 — 安全可重用
     elif grep -q '404' /tmp/sa-head.err; then
       NEED_CREATE=1
     elif grep -Eq '403|Forbidden' /tmp/sa-head.err; then
       echo "FATAL: 存储桶 $BUCKET 存在但由其他账户拥有 (403)。可能是存储桶抢占 — 中止。未上传任何内容。" >&2
       exit 1
     else
       cat /tmp/sa-head.err >&2; exit 1
     fi
     ```

   - 如果未找到，则创建它。`BucketAlreadyExists` 错误表示另一个账户已经持有全局名称 — 将其视为**致命的**且与 `BucketAlreadyOwnedByYou`（这是一个安全的无操作）不同。创建后重新断言所有权，然后再进行任何进一步使用：

     ```bash
     if [ "$NEED_CREATE" = "1" ]; then
       if [ "$REGION" = "us-east-1" ]; then
         # us-east-1: 无 LocationConstraint
         aws s3api create-bucket --bucket "$BUCKET" 2>/tmp/sa-create.err || true
       else
         # 其他区域：
         aws s3api create-bucket --bucket "$BUCKET" \
           --create-bucket-configuration LocationConstraint="$REGION" 2>/tmp/sa-create.err || true
       fi
       if grep -q 'BucketAlreadyExists' /tmp/sa-create.err; then
         echo "FATAL: 存储桶名称 $BUCKET 已经被其他账户拥有 (BucketAlreadyExists)。可能是存储桶抢占 — 中止。" >&2
         exit 1
       elif [ -s /tmp/sa-create.err ] && ! grep -q 'BucketAlreadyOwnedByYou' /tmp/sa-create.err; then
         cat /tmp/sa-create.err >&2; exit 1
       fi
       # 在使用前确认新创建的存储桶的所有权。
       aws s3api head-bucket --bucket "$BUCKET" --expected-bucket-owner "$ACCOUNT"
     fi
     ```

   - 始终（重新）应用公共访问阻止 + 30 天生命周期：

     ```bash
     aws s3api put-public-access-block --bucket "$BUCKET" \
       --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

     cat > /tmp/sa-lifecycle.json <<'EOF'
     {"Rules":[{"ID":"AutoDeleteUploads","Status":"Enabled","Filter":{"Prefix":""},"Expiration":{"Days":30}}]}
     EOF
     aws s3api put-bucket-lifecycle-configuration --bucket "$BUCKET" --lifecycle-configuration file:///tmp/sa-lifecycle.json
     ```

6. **在代理空间上注册角色 + 存储桶（幂等）**：
   - 读取现有资源：

     ```bash
     aws securityagent batch-get-agent-spaces --agent-space-ids <id>
     ```

     查看 `agentSpaces[0].awsResources.iamRoles` 和 `awsResources.s3Buckets`。
   - 如果角色 ARN 或存储桶名称不在这些列表中，则合并并更新：

     ```bash
     aws securityagent update-agent-space --agent-space-id <id> --name <existing-name> \
       --aws-resources iamRoles=[<arn1>,<arn2>...],s3Buckets=[<bucket1>,<bucket2>...]
     ```

7. **持久化**到 `.security-agent/config.json`（最小化 — 账户/角色/存储桶是推导的）：

   ```json
   {
     "agent_space_id": "as-xxxxx",
     "region": "us-east-1"
   }
   ```

8. **如果缺失，创建 gitignore**：

   ```bash
   mkdir -p .security-agent
   echo '*' > .security-agent/.gitignore
   ```

9. 向用户确认："设置完成。您现在可以运行安全扫描或渗透测试了。"

---

## 规则

- 当存在多个代理空间时，**不要自动选择** — 始终询问用户
- **不要禁用安全保护**（公共访问阻止保持开启）
- 对派生存储桶的每个 S3 调用都必须传递 `--expected-bucket-owner "$ACCOUNT"`。存储桶名称由非秘密账户 ID 派生，因此第三方可以预先注册它；在由其他账户拥有的存储桶上出现 `403`/`BucketAlreadyExists` 是致命的 — 中止并永不上传。
- 信任策略必须允许 `securityagent.amazonaws.com`（生产服务主体）并包括 `aws:SourceAccount` 混乱代理保护
- 如果用户提供自己的角色名称或存储桶名称（与约定默认值不同），请告知他们：此插件使用基于约定的默认值（`SecurityAgentScanRole` / `security-agent-scans-${ACCOUNT}-${REGION}`）。要么接受这些默认值，要么扩展技能 — 其他技能派生这些名称，而不是从配置中读取。
- 扫描和渗透测试技能可以在 `config.json` 缺失时内联调用此技能 — 首次用户不需要单独运行设置。

---

## 故障排除

- **调用 `iam:CreateRole` 时出现 `AccessDenied`** → 用户缺乏 IAM 权限。请他们使用自己的角色 ARN 运行设置，或者授予 `iam:CreateRole` + `iam:PutRolePolicy`。
- **对 `s3api create-bucket` 出现 `AccessDenied`** → 要么存储桶名称全局已被占用，要么用户缺乏 `s3:CreateBucket`。建议使用他们拥有的现有存储桶并显式传递。
- **派生存储桶上出现 `403 Forbidden` / `BucketAlreadyExists`** → 可预测的名称由一个 *不同* 的账户拥有（存储桶抢占）。按设计这是致命的 — 不要上传。让用户选择他们拥有的存储桶名称（或从预期的账户/区域运行设置）并重新运行设置。
- **角色存在但信任策略不正确** → `update-assume-role-policy`（步骤 4 回退）。如果他们不想更新该角色，请他们提供不同的角色 ARN。
- **代理空间存在但在不同区域** → 告知用户；建议使用正确的区域或在当前区域创建新的空间。
