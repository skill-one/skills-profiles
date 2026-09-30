---
name: dpm-finder
description: 找到驱动您 Grafana Cloud 账单的 Prometheus 指标。`dpm-finder` 是一个 Grafana 专业服务的 CLI 工具，它根据每分钟数据点数（DPM）对指标进行排序，并提供按标签集分解、可选的 `--cost-per-1000-series` 定价模式以及 Prometheus 导出器模式。在调查高 Grafana Cloud 支出、查找噪声/高基数指标、比较记录规则前后的基数，或将成本数据输入仪表板时使用——即使用户说“为什么我的 Mimir 账单这么高？”、“找到最大的指标”、“基数违规者”或“优化 Prometheus 成本”，而不提及 dpm-finder。
---

# dpm-finder

Grafana PS 工具，根据 DPM 对 Prometheus 指标进行排名，并按系列进行细分。来源：https://github.com/grafana-ps/dpm-finder

## 前置条件

- Python 3.9+
- Grafana Cloud Prometheus 端点 URL + 数字堆栈 ID + API 密钥 (`glc_…`, `metrics:read` 范围)

## 常见工作流程

### 单次分析（最常见）

```bash
# 1. 克隆 + venv + 安装
git clone https://github.com/grafana-ps/dpm-finder.git
cd dpm-finder
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. 配置凭证 — 复制 .env_example → .env 并填写：
#    PROMETHEUS_ENDPOINT  https://prometheus-<cluster_slug>.grafana.net  (.net 后面不能有任何内容)
#    PROMETHEUS_USERNAME  <数字堆栈 ID>
#    PROMETHEUS_API_KEY   glc_…

# 3. 扫描前验证凭证 — 应返回 >0 系列计数
curl -s -u "$PROMETHEUS_USERNAME:$PROMETHEUS_API_KEY" \
  "$PROMETHEUS_ENDPOINT/api/v1/label/__name__/values" | jq '.data | length'

# 4. 运行扫描（10 分钟回溯，2.0 DPM 最小值，输出顶部结果）
./dpm-finder.py -f json -m 2.0 -t 8 --timeout 120 -l 10

# 5. 阅读结果 — 按 DPM 排序的前 10 个指标
jq -r '.metrics | sort_by(-.dpm) | .[:10][] | "\(.dpm)\t\(.series_count)\t\(.metric_name)"' metric_rates.json
```

如果第 5 步为空，请降低 `-m` 或确认端点 URL 在 `.net` 后没有路径。

### 使用 `gcx` 发现堆栈详情

如果安装了 [gcx](https://github.com/grafana/gcx)，它可以推导出端点 + 用户名：

```bash
gcx config check          # 活跃堆栈上下文
gcx config list-contexts  # 所有配置的堆栈
gcx config view           # 完整配置，包括端点
```

Prometheus 端点模式是 `https://prometheus-{cluster_slug}.grafana.net`。用户名是数字堆栈 ID。

没有 gcx：在 Grafana Cloud 门户中查找，或在使用数据源上查询 `grafanacloud_instance_info{name=~"STACK_NAME.*"}`。

### 多堆栈运行

限制为 **最多 3 个并发** 运行以避免 GCloud 速率限制。分批处理堆栈，并在下一个批次之前等待每个批次完成。

## 解释结果

- **DPM** = 该指标的所有系列中每分钟最大数据点数
- **series_count** = 该指标的活跃时间序列计数
- **series_detail[]** (JSON / 仅文本) = 按标签组合的 DPM 分解 — 使用此功能来识别有问题的标签
- 按 DPM 降序排序 → 最嘈杂的指标；结合 `--cost-per-1000-series` 以按支出优先级排序

## 故障排除

- **401 / 403** — API 密钥无效或缺少 `metrics:read`；确认 `PROMETHEUS_USERNAME` 是数字堆栈 ID
- **超时** — 将 `--timeout` 提高到 120+ 以适用于具有数千个指标的堆栈
- **HTTP 422** — 指标具有聚合规则；工具会警告并自动跳过
- **空结果** — 降低 `-m`；验证端点没有尾随路径
- **连接错误** — 指数退避重试最多 10 次；持续失败通常 = 网络/防火墙

## 参考

- [`references/cli.md`](references/cli.md) — 完整标志参考，输出格式细节，导出模式，Docker 调用，自动排除规则，重试行为

## 资源

- [dpm-finder GitHub](https://github.com/grafana-ps/dpm-finder)
- [gcx](https://github.com/grafana/gcx)
