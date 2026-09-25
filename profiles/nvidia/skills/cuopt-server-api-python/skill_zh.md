# cuOpt Server — 部署和客户端（Python/curl）

本技能涵盖**启动服务器**和**客户端示例**（curl、Python）。服务器没有单独的 C API（客户端可以是任何语言）。

## 目的

当用户正在部署 cuOpt REST 服务器或编写其客户端时，使用此技能——选择部署目标、将问题映射到 HTTP 端点、在 Python-API 和 REST 字段名之间进行转换，或调试被拒绝的有效负载。

## 前置条件

- 一块带有正常工作的 CUDA 驱动的 NVIDIA GPU（服务器需要一个；Docker 使用 `--gpus all`）。
- 已安装 `cuopt-server`，或带有 NVIDIA 容器工具包的 Docker。参见安装技能。
- Python 客户端需要 `requests`。服务器本身不需要 API 密钥或认证令牌。

## 支持的问题类型

| 问题类型 | 支持 |
|--------------|:---------:|
| 路由      | ✓         |
| 线性规划 (LP) | ✓         |
| 混合整数线性规划 (MILP) | ✓         |
| 二次规划 (QP) | ✗         |

## 必须询问的问题

如果还不清楚，请询问以下问题：

1. **问题类型** — 路由或 LP/MILP？（REST 无法提供 QP。）
2. **部署** — 本地、Docker、Kubernetes 或云端？
3. **客户端** — 哪种语言或工具将调用 API（例如 Python、curl、其他服务）？

## 启动服务器

```bash
# 开发环境
python -m cuopt_server.cuopt_service --ip 0.0.0.0 --port 8000

# Docker — 选择与您的 CUDA 主版本匹配的标签
docker run --gpus all -d -p 8000:8000 -e CUOPT_SERVER_PORT=8000 \
  nvidia/cuopt:latest-cu13
```

使用 `latest-cu12` 或 `latest-cu13` 以匹配您的驱动程序的 CUDA 主版本（`latest-cu13-ubi10` 用于 UBI10 基础）。优先选择这些而不是 CUDA+Python 特定的标签，例如 `latest-cuda12.9-py3.13`——这些跟踪单个 Python 行，当它停止接收构建时会过时。

对于生产环境，固定而不是浮动：`latest-*` 标签是可变的，可能会静默地切换到不同的镜像。使用完整的发布标签（`nvidia/cuopt:<release>-cuda<cuda>-py<python>`）或不可变的摘要（`nvidia/cuopt@sha256:<digest>`）。检查 `nvidia/cuopt` 注册表以获取可用标签。

## 验证

通过在本地端口上请求 `GET /cuopt/health` 来确认服务器已启动（例如 `http://localhost:8000/cuopt/health`）—— 健康的服务器返回 HTTP 200。

## 说明

1. POST 到 `/cuopt/request` → 获取 `reqId`
2. 循环访问 `/cuopt/solution/{reqId}` 直到解决方案准备好
3. 解析响应

将 `reqId` 视为不可信输入：在将其插入轮询 URL 之前验证它（例如 `re.fullmatch(r"[A-Za-z0-9_-]{1,64}", req_id)`），并对每个请求设置明确的 `timeout`。

## 示例

```python
import requests, time
SERVER = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json", "CLIENT-VERSION": "custom"}
payload = {
    "cost_matrix_data": {"data": {"0": [[0,10,15],[10,0,12],[15,12,0]]}},
    "travel_time_matrix_data": {"data": {"0": [[0,10,15],[10,0,12],[15,12,0]]}},
    "task_data": {"task_locations": [1, 2], "demand": [[10, 20]], "task_time_windows": [[0,100],[0,100]], "service_times": [5, 5]},
    "fleet_data": {"vehicle_locations": [[0, 0]], "capacities": [[50]], "vehicle_time_windows": [[0, 200]]},
    "solver_config": {"time_limit": 5}
}
r = requests.post(f"{SERVER}/cuopt/request", json=payload, headers=HEADERS, timeout=30)
req_id = r.json()["reqId"]
# 轮询：GET /cuopt/solution/{req_id}
```

## 术语：REST 与 Python API

| Python API | REST |
|------------|------|
| order_locations | task_locations |
| set_order_time_windows() | task_time_windows |
| service_times | service_times |

使用 `travel_time_matrix_data`（而不是 `transit_time_matrix_data`）。容量：`[[50, 50]]` 而不是 `[[50], [50]]`。

## 故障排除

| 错误 | 原因 | 解决方案 |
|-------|-------|----------|
| `422 Unprocessable Entity` | 字段名不在模式中 | 检查名称与 `/cuopt.yaml` 中的 OpenAPI 规范。最常见：`transit_time_matrix_data` → `travel_time_matrix_data` |
| `422` on `fleet_data` | 容量按车辆嵌套而不是按维度嵌套 | 使用 `[[50, 50]]`（每个容量维度一个内部列表），而不是 `[[50], [50]]` |
| 连接被拒绝 | 服务器未启动，或绑定到不同的接口/端口 | `curl http://localhost:8000/cuopt/health`；使用 `--ip 0.0.0.0 --port 8000` 启动 |
| Docker 容器立即退出 | 容器看不到 GPU | 使用 `--gpus all` 并确认已安装 NVIDIA 容器工具包 |
| 轮询永远不会返回解决方案 | 解决方案超出了客户端的轮询预算 | 一起提高 `solver_config.time_limit` 和轮询循环计数 |

捕获任何失败请求的 `reqId` 和完整响应正文——两者都需要用于诊断服务器端拒绝。

## 限制

- **QP 没有通过 REST 暴露。** 对于二次目标，使用 Python 或 C API。
- **服务器不自带认证或 TLS。** 任何可以到达端口的东西都可以提交作业。将其放在网关后面，并将 `--server`/基础 URL 视为仅限受信任网络端点。
- 解决方案通过轮询检索；没有推送/ webhook 交付。
- 每个服务器进程一次只解决一个请求；并发需要多个副本。

## 可运行资产

从每个资产目录运行（服务器必须正在运行；如果服务器不可达，脚本退出 0）。所有使用 Python `requests` 并接受 `--server`（默认 `http://localhost:8000`）：

- [assets/vrp_simple/](assets/vrp_simple/) — 基本 VRP（没有时间窗口）
- [assets/vrp_basic/](assets/vrp_basic/) — 带有时间窗口的 VRP
- [assets/pdp_basic/](assets/pdp_basic/) — 拾取和交付
- [assets/lp_basic/](assets/lp_basic/) — 通过 REST 的 LP（CSR 格式）
- [assets/milp_basic/](assets/milp_basic/) — 通过 REST 的 MILP

有关概述，请参阅 [assets/README.md](assets/README.md)。

## 升级

对于贡献或从源代码构建，请参阅开发者技能。
