# SEO漂移监控器（2026年4月）

Git为您的SEO服务。捕获基准点，检测回归，跟踪随时间变化。

---

## 命令

| 命令 | 目的 |
|------|------|
| `/seo drift baseline <url>` | 将当前SEO状态捕获为“已知良好”的快照 |
| `/seo drift compare <url>` | 将当前页面状态与存储的基准点进行比较 |
| `/seo drift history <url>` | 显示变更历史记录和过去的比较 |

---

## 捕获内容

每个基准点记录以下SEO关键元素：

| 元素 | 字段 | 来源 |
|------|------|------|
| 标题标签 | `title` | `parse_html.py` |
| 元描述 | `meta_description` | `parse_html.py` |
| 原始URL | `canonical` | `parse_html.py` |
| 机器人指令 | `meta_robots` | `parse_html.py` |
| H1标题 | `h1`（数组） | `parse_html.py` |
| H2标题 | `h2`（数组） | `parse_html.py` |
| H3标题 | `h3`（数组） | `parse_html.py` |
| JSON-LD模式 | `schema`（数组） | `parse_html.py` |
| Open Graph标签 | `open_graph`（字典） | `parse_html.py` |
| 核心网络指标 | `cwv`（字典） | `pagespeed_check.py` |
| HTTP状态码 | `status_code` | `fetch_page.py` |
| HTML内容哈希 | `html_hash`（SHA-256） | 计算得出 |
| 模式内容哈希 | `schema_hash`（SHA-256） | 计算得出 |

---

## 比较工作原理

比较引擎应用**17条规则，跨越3个严重程度级别**。加载
`references/comparison-rules.md`获取完整的规则集，包括阈值、推荐操作和跨技能参考。

### 严重程度级别

| 级别 | 含义 | 响应时间 |
|------|------|----------|
| **严重** | SEO破坏性变更，可能导致流量损失 | 立即 |
| **警告** | 潜在影响，需要调查 | 1周内 |
| **信息** | 仅需知晓，可能是故意变更 | 随时审查 |

---

## 存储

所有数据本地存储在SQLite中：

```
~/.cache/claude-seo/drift/baselines.db
```

### 表格

- **baselines**：捕获的包含所有SEO元素的快照
- **comparisons**：触发规则和严重程度的差异结果

URL规范化确保一致匹配：小写方案/主机，移除默认端口（80/443），排序查询参数，移除UTM参数，移除尾随斜杠。

---

## 命令：`baseline`

捕获页面当前状态并存储。

**步骤：**
1. 验证URL（通过`google_auth.validate_url()`实现SSRF保护）
2. 通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run fetch_page.py <URL>`获取页面
3. 通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run parse_html.py <URL>`解析HTML
4. 可选地通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run pagespeed_check.py <URL>`获取CWV（使用`--skip-cwv`跳过）
5. 哈希HTML主体和模式内容（SHA-256）
6. 将快照存储在SQLite中

**执行：**
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_baseline.py <url>
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_baseline.py <url> --skip-cwv
```

**输出：** 包含基准点ID、时间戳、URL和捕获元素摘要的JSON。

---

## 命令：`compare`

获取当前页面状态并与最新基准点进行比较。

**步骤：**
1. 验证URL
2. 从SQLite加载最新基准点（或指定`--baseline-id`）
3. 获取并解析当前页面状态
4. 运行所有17条比较规则
5. 按严重程度分类结果
6. 存储比较结果
7. 输出JSON差异报告

**执行：**
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_compare.py <url>
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_compare.py <url> --baseline-id 5
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_compare.py <url> --skip-cwv
```

**输出：** 包含所有触发的规则、旧/新值、严重程度和操作的JSON。

比较后，提供生成HTML报告的选项：
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_report.py <comparison_json_file> --output drift-report.html
```

---

## 命令：`history`

显示URL的所有基准点和比较。

**执行：**
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_history.py <url>
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_history.py <url> --limit 10
```

**输出：** 包含时间戳和比较摘要的基准点JSON数组（最新优先）。

---

## 跨技能集成

检测到漂移时，推荐适当的专用技能：

| 发现 | 推荐 |
|------|------|
| 模式被移除或修改 | 运行`/seo schema <url>`进行完整验证 |
| CWV回归 | 运行`/seo technical <url>`进行性能审计 |
| 标题或元描述变更 | 运行`/seo page <url>`进行内容分析 |
| 原始URL变更或移除 | 运行`/seo technical <url>`进行可索引性检查 |
| 添加了noindex | 运行`/seo technical <url>`进行可爬取性审计 |
| H1/标题结构变更 | 运行`/seo content <url>`进行E-E-A-T审查 |
| OG标签移除 | 运行`/seo page <url>`进行社交分享分析 |
| 状态码变为错误 | 运行`/seo technical <url>`进行完整诊断 |

---

## 错误处理

| 场景 | 操作 |
|------|------|
| URL无法访问 | 报告`fetch_page.py`的错误。不要猜测状态。建议用户验证URL。 |
| URL不存在基准点 | 通知用户并建议先运行`baseline`。 |
| SSRF被阻止（私有IP） | 报告`validate_url()`拒绝。永不绕过。 |
| SQLite数据库缺失 | 首次使用时自动创建。无错误。 |
| CWV获取失败（无API密钥） | CWV字段存储为`null`。比较时跳过CWV规则。 |
| 页面返回4xx/5xx | 仍捕获为基准点（状态码是跟踪字段）。 |
| 存在多个基准点 | 使用最新基准点，除非指定`--baseline-id`。 |

---

## 安全

- **所有URL获取**通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run fetch_page.py`，该命令执行SSRF保护
  （阻止私有IP、回环、保留范围、GCP元数据端点）
- **无curl，无子进程HTTP调用** -- 仅使用项目的验证获取管道
- **所有SQLite查询**使用参数化占位符（`?`），绝不使用字符串插值
- **始终验证TLS** -- 管道中任何地方都不使用`verify=False`

---

## 典型工作流程

### 部署前/后检查
```
/seo drift baseline https://example.com     # 部署前
# ... 部署发生 ...
/seo drift compare https://example.com      # 部署后
```

### 持续监控
```
/seo drift baseline https://example.com     # 初始捕获
# ... 几周后 ...
/seo drift compare https://example.com      # 检查漂移
/seo drift history https://example.com      # 审查所有变更
```

### 调查流量下降
```
/seo drift compare https://example.com      # 发生了什么变更？
/seo drift history https://example.com      # 变更何时发生？
```
