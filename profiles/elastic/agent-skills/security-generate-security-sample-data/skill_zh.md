# 生成安全样本数据

生成符合 ECS 标准的安全事件、多步骤攻击场景和合成警报文档，用于填充 Elastic Security 仪表板、警报选项卡和攻击发现。

## 快速入门

为了获得无缝体验并生成所有内容并打开 Kibana：

```bash
node skills/security/generate-security-sample-data/scripts/demo-walkthrough.js
```

## 工作流程

```text
- [ ] 第 1 步：设置环境变量
- [ ] 第 2 步：生成样本数据
- [ ] 第 3 步：在 Kibana 中探索
- [ ] 第 4 步：完成时清理
```

### 第 1 步：设置环境变量

```bash
export ELASTICSEARCH_URL="https://your-project.es.region.aws.elastic.cloud"
export ELASTICSEARCH_USERNAME="admin"
export ELASTICSEARCH_PASSWORD="your-password"
export KIBANA_URL="https://your-project.kb.region.aws.elastic.cloud"
```

### 第 2 步：生成样本数据

#### 一次性生成所有内容

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js \
  system endpoint okta aws windows --scenarios --alerts
```

#### 仅生成事件

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js \
  system endpoint --count 100
```

#### 仅生成攻击场景

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js --scenarios
```

#### 仅生成合成警报

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js --alerts
```

### 第 3 步：在 Kibana 中探索

生成数据后，引导用户访问以下页面：

- **安全 > 警报** — 带有 MITRE ATT&CK 映射的合成警报
- **安全 > 攻击发现** — 需要使用 LLM 连接器分析警报
- **安全 > 主机** — 样本事件中的主机活动
- **安全 > 概览** — 所有安全数据的摘要
- **发现** — 所有数据流中的原始事件

### 第 4 步：完成时清理

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js --cleanup
```

## 生成的数据内容

样本数据涵盖 5 个包（系统、端点、windows、aws、okta）和 4 个专注的攻击场景，覆盖最常见的演示主题：Windows 凭据窃取、AWS 云权限提升、Okta 身份劫持以及完整的勒索软件杀伤链。合成警报文档被索引到 `.alerts-security.alerts-default`，包含 MITRE ATT&CK 映射、严重级别和风险评分。

所有事件使用 RFC 5737 / RFC 2606 安全地址。有关包、场景和警报的完整表格，请参阅 [references/sample-data-reference.md](references/sample-data-reference.md)。

## 持续模式

将事件流式传输以模拟实时环境：

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js \
  --continuous --interval 15
```

每 5 批次中包含一个攻击场景；每 10 批次添加合成警报。按 Ctrl+C 停止。

## 工具参考

### sample-data.js

| 标志              | 描述                                      |
| ----------------- | ----------------------------------------- |
| `--count`, `-n`   | 每个包的事件数（默认：50）                 |
| `--scenarios`     | 运行所有攻击模拟场景                      |
| `--scenario NAME` | 运行特定场景                              |
| `--alerts`        | 生成合成警报文档                          |
| `--cleanup`       | 删除所有样本数据和警报                    |
| `--continuous`    | 流式传输实时事件（Ctrl+C 停止）            |
| `--interval N`    | 连续批次之间的秒数（默认：30）             |
| `--json`, `-j`    | 将结果输出为 JSON                        |
| `--yes`, `-y`     | 跳过确认提示                              |

### demo-walkthrough.js

生成所有内容并打开 Kibana 的零摩擦运行器。

| 标志           | 描述                                     |
| -------------- | ---------------------------------------- |
| `--cleanup`    | 删除所有样本数据、警报、案例             |
| `--continuous` | 生成然后流式传输实时事件                |
| `--count N`    | 每个包的事件数（默认：50）                |
| `--interval N` | 批次之间的秒数（默认：30）                |

## 示例

### 针对利益相关者的快速演示

> "设置一个演示环境，以便我可以向我的副总裁展示攻击发现。"

```bash
node skills/security/generate-security-sample-data/scripts/demo-walkthrough.js
```

### 针对特定场景的测试

> "仅生成勒索软件攻击链以测试我们的检测规则。"

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js \
  --scenario ransomwareChain --alerts
```

### 模拟实时 SOC

> "持续生成事件，以便在演示期间保持仪表板活跃。"

```bash
node skills/security/generate-security-sample-data/scripts/demo-walkthrough.js --continuous
```

### 演示后的清理

> "删除我的项目中的所有样本数据。"

```bash
node skills/security/generate-security-sample-data/scripts/sample-data.js --cleanup
```

## 指南

- 所有生成的文档都标记为 `tags: ["elastic-security-sample-data"]` 以便安全清理。清理命令仅删除带有此标记的文档。
- 如果标记字段未在数据流中索引，清理将回退到扫描 `_source.tags` 以查找过去 14 天内的匹配样本文档。
- 合成警报直接索引到 `.alerts-security.alerts-default` — 它们不需要安装或启用检测规则。
- 攻击发现需要一个 LLM 连接器（OpenAI、Anthropic、Google Gemini 或类似）在 Kibana 下配置在堆栈管理 > 连接器中。 "完整" 项目层解锁该功能，但连接器必须单独设置。
- 使用 `case-management` 技能从警报创建调查案例。

## 生产环境使用

- **不要在生产集群上运行**，除非您打算在真实警报旁边注入合成数据。样本事件和警报被标记以供清理，但它们会与真实数据一起出现在仪表板、警报选项卡和攻击发现中。
- 所有写操作（`generate`、`--cleanup`、`--continuous`）都会提示确认。当由代理调用时，传递 `--yes` 或 `-y` 以跳过。
- `--cleanup` 跨所有样本数据索引运行 `deleteByQuery` — 在运行之前验证环境变量指向预期的集群。
- `--continuous` 模式无限期索引事件，直到手动使用 Ctrl+C 停止。

## 环境变量

| 变量                 | 是否必需 | 描述                                  |
| ------------------- | -------- | ------------------------------------- |
| `ELASTICSEARCH_URL`  | 是       | Elasticsearch URL                      |
| `ELASTICSEARCH_API_KEY` | 是\*     | Elasticsearch API 密钥                |
| `ELASTICSEARCH_USERNAME` | 是\*     | Elasticsearch 用户名（替代方案）       |
| `ELASTICSEARCH_PASSWORD` | 是\*     | Elasticsearch 密码（替代方案）       |
| `KIBANA_URL`         | 否       | Kibana URL（用于案例创建和链接）       |
| `KIBANA_USERNAME`    | 否       | Kibana 用户名（如果使用 Kibana 功能） |
| `KIBANA_PASSWORD`    | 否       | Kibana 密码（如果使用 Kibana 功能）   |

\*Elasticsearch 需要 API 密钥或用户名/密码中的任意一项。
