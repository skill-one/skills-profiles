# AWS 安全代理 — 威胁模型审查

通过 STRIDE 方法论对比规范文档（`requirements.md`、`design.md`）与源代码，以识别安全态势变化。无需预先扫描。

## 本地状态

读取 `.security-agent/config.json` 获取 `agent_space_id` 和 `region`。若缺失，则先执行内联的 `setup-security-agent` 工作流。

### 解析所需值

| 占位符 | 解析方法 |
|-------|---------|
| `<id>` (代理空间) | `config.agent_space_id` |
| `<region>` | `config.region` (默认 `us-east-1`) |
| `<account>` | `aws sts get-caller-identity --query Account --output text` |
| `<role-arn>` | `arn:aws:iam::<account>:role/SecurityAgentScanRole` |
| `<bucket>` | `security-agent-scans-<account>-<region>` |

---

## 工作流

1. **预检查**。读取配置，验证代理空间，解析值。

2. **收集规范文件**。识别用户正在处理的 `requirements.md` 和/或 `design.md`。使用绝对路径。若不确定需审查的文件，则询问。

3. **压缩工作区**（与代码扫描相同的排除项）：

   ```bash
   cd <绝对工作区路径>
   zip -r /tmp/source.zip . \
     -x ".git/*" -x ".security-agent/*" -x "node_modules/*" \
     -x "__pycache__/*" -x ".venv/*" -x "venv/*" \
     -x "dist/*" -x "build/*" -x "target/*" \
     -x ".mypy_cache/*" -x ".pytest_cache/*" -x ".tox/*" \
     -x ".next/*" -x "cdk.out/*" -x ".DS_Store" -x "*.pyc"
   ```

4. **上传源码压缩包**：

   ```bash
   SCAN_ID="tm-$(date +%s)-$(openssl rand -hex 3)"
   WORKSPACE_ID=$(printf '%s' "$(pwd)" | md5sum | cut -c1-12)
   aws s3 cp /tmp/source.zip s3://<bucket>/security-scans/source/${WORKSPACE_ID}/source.zip --expected-bucket-owner <account>
   ```

5. **上传规范文件**：

   ```bash
   aws s3 cp /path/to/requirements.md s3://<bucket>/security-scans/threat-models/${SCAN_ID}/specs/requirements.md --expected-bucket-owner <account>
   aws s3 cp /path/to/design.md s3://<bucket>/security-scans/threat-models/${SCAN_ID}/specs/design.md --expected-bucket-owner <account>
   ```

6. **创建威胁模型**：

   ```bash
   aws securityagent create-threat-model --agent-space-id <id> --title <title> \
     --service-role <role-arn> \
     --assets sourceCode=[{s3Location=s3://<bucket>/security-scans/source/${WORKSPACE_ID}/source.zip}] \
     --scope-docs '[{"s3Location":"s3://<bucket>/security-scans/threat-models/'${SCAN_ID}'/specs/requirements.md"},{"s3Location":"s3://<bucket>/security-scans/threat-models/'${SCAN_ID}'/specs/design.md"}]'
   ```

   捕获 `threatModelId`。

7. **启动威胁模型任务**：

   ```bash
   aws securityagent start-threat-model-job --agent-space-id <id> --threat-model-id <tm-id>
   ```

   捕获 `threatJobId`。

8. 将结果持久化到 `scans.json`，`scan_type: "THREAT_MODEL"`。

9. 告知用户："威胁模型审查已启动。运行时间随工作区大小变化。我将每 2 分钟检查一次——说 '停止轮询' 可退出。"

10. **每 2 分钟轮询**：

    ```bash
    aws securityagent batch-get-threat-model-jobs --agent-space-id <id> --threat-model-job-ids <tj-id>
    ```

    仅在状态变化时响应。

11. **在 COMPLETED 状态时** → 获取威胁：

    ```bash
    aws securityagent list-threats --agent-space-id <id> --threat-job-id <tj-id>
    ```

    若存在 `nextToken`，则使用 `--next-token` 分页。

## 发现结果展示

每个威胁包含：`statement`、`severity`、`stride` 类别、`threatImpact`、`recommendation`、`impactedAssets`。

```
🟣 严重：{statement}
   STRIDE：{stride}
   影响：{threatImpact}
   受影响资产：{impactedAssets}
   建议：{recommendation}

🔴 高：{statement}
   ...
```

将完整报告写入 `.security-agent/findings-{scan_id}.md`。指出任何与先前设计相比表示回归的威胁。

---

## 规则

- 威胁模型审查是独立的——无需预先扫描
- 每 2 分钟轮询，不能更快
- 至少需要一个规范文件
- 工作区和规范文件使用绝对路径
- 标题：`threat-model-<feature-name>`（无空格）
