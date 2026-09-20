# 模板验证 + 询价确认（步骤 9）

Agent 直接执行 CLI 命令进行模板验证和费用估算。

> **`$TEMPLATE_URL` 从哪来**：把步骤 7 生成的模板上传到 OSS，即
> `python3 scripts/upload_artifacts.py --template-file <生成的模板.yaml> ...`，
> 该命令输出签名 URL；将其导出为 `TEMPLATE_URL` 后再执行下面的命令。验证与询价只看资源结构与价格，
> 用占位 UserData 即可，不涉及产物（产物在步骤 10 上传）。
> （ROS 必须用 `--TemplateURL`，`--TemplateBody` 会被 WAF 拦截。）

---

## 模板验证

```bash
aliyun ros ValidateTemplate --RegionId "$REGION" --TemplateURL "$TEMPLATE_URL"
```

非 0 退出码 → 读 `Code` + `Message`，修模板后重试。

---

## 费用估算

> 询价需要 `Password` 参数但不会真正创建资源。用环境变量注入一次性口令，
> 避免形似密钥的字面量落入 shell 历史：
> `export PRICING_PWD="$(openssl rand -base64 12)!aA1"`。

```bash
aliyun ros GetTemplateEstimateCost \
  --RegionId "$REGION" \
  --TemplateURL "$TEMPLATE_URL" \
  --Parameters.1.ParameterKey AppName        --Parameters.1.ParameterValue "$APP_NAME" \
  --Parameters.2.ParameterKey InstanceType   --Parameters.2.ParameterValue "$INSTANCE_TYPE" \
  --Parameters.3.ParameterKey Password       --Parameters.3.ParameterValue "$PRICING_PWD" \
  --Parameters.4.ParameterKey SystemDiskSize --Parameters.4.ParameterValue "40" \
  --Parameters.5.ParameterKey AppPort    --Parameters.5.ParameterValue "8080" \
  --Parameters.6.ParameterKey ZoneId         --Parameters.6.ParameterValue "$ZONE_ID" \
  --Parameters.7.ParameterKey UserDataScript --Parameters.7.ParameterValue "#!/bin/bash"
```

> 含 RDS 时不传 UserDataScript，改传 RDS 参数：
> `DbInstanceClass`（= 步骤 5 的 `DB_INSTANCE_CLASS`）、`DbInstanceStorage`（GiB）、`DbName`、
> `DbAccount`、`DbPassword`。`DbInstanceClass`/`DbInstanceStorage` 须与用户在步骤 5 的选择一致，
> 询价才能反映真实 RDS 规格。

---

## 解析结果

返回 `Resources.<LogicalId>.Result.Order.OriginalAmount`（每个资源的**每小时**金额）。
求和得到总小时单价。币种始终为**人民币（¥）**。

---

## 确认展示

AskUserQuestion 汇总确认时展示：
- 小时单价（¥）
- 本次将创建的全部计费资源清单
- 不含公网流量、快照、OSS 存储等动态费用的提示
