# Grafana Pyroscope

> **文档**: https://grafana.com/docs/pyroscope/latest/

持续分析 — CPU、内存、分配、互斥锁争用、goroutines 的火焰图。

## 前置条件

- Pyroscope 服务器 (开源版) 或 Grafana Cloud Profiles 端点
- 对于 Cloud: 数字 Pyroscope 用户 (堆栈 ID) + API 密钥
- 对于 eBPF 通过 Alloy: root + 主机 PID + Linux ≥ 5.8 且具有 BTF (或 RHEL 4.18+)

## 仪器路径

1. **Alloy eBPF** (推荐) — 自动仪器，无需代码更改
2. **SDK 直接推送** — 应用程序调用 Pyroscope API
3. **SDK → Alloy** — SDK 推送到 `pyroscope.receive_http`，Alloy 转发

## 常见工作流

### 1. 使用 SDK 仪器应用程序 (代表：Python)

```bash
pip install pyroscope-io==1.0.11
```

```python
import pyroscope, os
pyroscope.configure(
    application_name="my.python.app",
    server_address="http://pyroscope:4040",
    sample_rate=100, oncpu=True,
    tags={"region": os.getenv("REGION"), "env": "prod"},
)
# 动态标签用于热点路径
with pyroscope.tag_wrapper({"controller": "slow_controller"}):
    slow_code()
```

```bash
# 验证应用程序正在推送 — Pyroscope 在几秒钟内摄取样本
curl -s http://pyroscope:4040/ready                                    # → "ready"
curl -s http://pyroscope:4040/api/v1/labels | jq '.data | index("service_name")'  # → 不为空

# 验证服务在 Grafana 中显示 → 探索 → Profiles → 服务下拉菜单。
```

其他 SDKs (Java 代理、Node、Ruby、.NET、Rust) + Cloud 认证 + 可调环境变量: [`references/sdks.md`](references/sdks.md)。

### 2. 使用 Alloy 进行集群范围的 eBPF 仪器

```alloy
# config.alloy — references/ebpf-and-query.md 中的完整块
pyroscope.ebpf "local_pods" {
  forward_to       = [pyroscope.write.cloud.receiver]
  targets          = discovery.relabel.local_pods.output
  sample_rate      = 97
  collect_interval = "15s"
}
pyroscope.write "cloud" {
  endpoint {
    url = "https://profiles-prod-xxx.grafana.net"
    basic_auth { username = sys.env("PYROSCOPE_USER")
                 password = sys.env("GRAFANA_API_KEY") }
  }
}
```

```bash
# 1. 重新加载 Alloy
curl -X POST http://localhost:12345/-/reload

# 2. 验证 eBPF 组件是否健康
curl -s http://localhost:12345/api/v0/web/components \
  | jq '.[] | select(.id|contains("pyroscope.ebpf")) | {id,health:.health.state}'
# 预期：health.state == "healthy"

# 3. 验证样本到达 Pyroscope
#    Grafana → 探索 → Profiles 数据源 → 查询：
#      {namespace="default", __profile_type__="process_cpu:cpu:nanoseconds:cpu:nanoseconds"}
#    预期火焰图会显示来自目标 Pod 的帧。
```

### 3. 使用 ProfileQL 查询

```
{service_name="myapp", env="prod",
 __profile_type__="process_cpu:cpu:nanoseconds:cpu:nanoseconds"}
```

Profile-type 列表 + 完整 ProfileQL 语法: [`references/ebpf-and-query.md`](references/ebpf-and-query.md)。

## 故障排除

- SDK 启动但没有火焰图 → 检查应用程序是否实际调用了 `start()` / `configure()` (某些 SDK 是懒加载的)；检查 `server_address` 从容器内部可达
- Alloy eBPF 组件 `unhealthy` 并有 BPF 错误 → 内核 < 5.8 或缺少 BTF；`ls /sys/kernel/btf/vmlinux`
- Cloud 推送 401 → 错误的 `basic_auth_username` (必须是数字堆栈 ID，而不是别名)
- 火焰图显示但没有帧 → 对于 Java，设置 `PYROSCOPE_FORMAT=jfr`；对于 Alpine 上的 Python，确保 `procfs` 和 `glibc` 兼容性

## 资源

- [Pyroscope 文档](https://grafana.com/docs/pyroscope/latest/)
- [Grafana Cloud Profiles](https://grafana.com/docs/grafana-cloud/monitor-applications/profiles/)
- [`references/sdks.md`](references/sdks.md) — Java/Node/Ruby/.NET/Rust 安装 + 配置 + 环境变量表 + Profile-type 矩阵
- [`references/ebpf-and-query.md`](references/ebpf-and-query.md) — 完整 Alloy eBPF 管道 + ProfileQL
