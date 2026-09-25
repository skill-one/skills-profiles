# OpenViking 嵌入模型切换

## 概述

将 OpenViking 使用的嵌入模型切换到本地 llama-server 或任何 OpenAI 兼容的端点，并执行适当的 vectordb 索引重建和沙盒安全重启。

> **⚠️ 单用途技能** — 所有操作都通过 job-env-manager REST API (`http://127.0.0.1:8090`) 进行。切勿在主机上直接运行 `openviking-server`。

OpenViking 是一个使用向量嵌入进行语义搜索的 AI 上下文数据库。其嵌入模型配置在 `ov.conf` 的 `embedding.dense` 部分。当切换到不同的嵌入模型（尤其是向量维度不同时），必须删除并重建现有的 vectordb 索引 — 否则 OpenViking 在启动时会抛出 `EmbeddingRebuildRequiredError`。

## 架构

```
OpenViking 嵌入模型切换
├── 检测当前配置     (读取 ov.conf embedding.dense 部分)
├── 验证端点         (检查 llama-server /v1/embeddings)
├── 修改 ov.conf     (更新 provider、model、api_base、dimension)
├── 删除 vectordb 索引 (如果 dimension 改变: rm -rf vectordb/context)
├── 重启服务器       (Kill + exec, NOT stop/start)
└── 验证             (Health + PID + dimension + log check)
```

```
┌─────────────────────────────────────────────────────┐
│                    主机                              │
│                                                      │
│  ┌─────────────┐    REST API   ┌──────────────────┐ │
│  │  Agent       │─────────────▶│  job-env-manager  │ │
│  │  (此技能)    │              │  :8090            │ │
│  └─────────────┘              └────────┬─────────┘ │
│                                        │            │
│         ┌──────────────────────────────┼──────┐    │
│         │  bwrap 沙盒 (openviking)   │      │    │
│         │                               ▼      │    │
│         │  ┌────────────────────────────────┐  │    │
│         │  │  openviking-server :1933       │  │    │
│         │  │  ├── ov.conf (嵌入配置)        │  │    │
│         │  │  ├── vectordb/context/         │  │    │
│         │  │  └── viking/ (元数据)        │  │    │
│         │  └────────────────────────────────┘  │    │
│         └──────────────────────────────────────┘    │
│                                                      │
│         ┌──────────────────────────────────────┐    │
│         │  bwrap 沙盒 (llama)                    │    │
│         │  ┌────────────────────────────────┐  │    │
│         │  │  llama-server :18200           │  │    │
│         │  │  --embeddings --model bge-...  │  │    │
│         │  └────────────────────────────────┘  │    │
│         └──────────────────────────────────────┘    │
│                                                      │
│  两个沙盒都使用 --share-net，因此 127.0.0.1        │
│  端点可以互相访问。                                 │
└─────────────────────────────────────────────────────┘
```

## 前置条件

> **前置条件检查: job-env-manager 正在运行**
> ```bash
> curl -s http://127.0.0.1:8090/api/v1/envs/openviking | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])"
> ```

- **job-env-manager** 在 `http://127.0.0.1:8090` 上运行
- **OpenViking 环境** 已部署并运行（状态 = `running`）
- **llama-server** 在 `127.0.0.1:{port}` 上运行并带有 `--embeddings` 标志
- 主机上可用 **curl** 和 **python3**
- 无需 AK/SK 或华为云凭证

## IAM 权限策略

此技能通过 job-env-manager REST API 在本地 bwrap 沙盒上操作，不访问华为云服务 — 无需华为云 IAM 策略。等效的访问控制列表在 [references/iam-policies.md](references/iam-policies.md) 中列出。

## 核心命令 (核心工作流)

### 任务 1: 检测当前配置

```bash
SANDBOX_DIR=$(curl -s http://127.0.0.1:8090/api/v1/envs/openviking \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['cwd'])")
```

读取沙盒目录下的 `ov.conf`，获取当前的 `embedding.dense` 部分（provider、model、dimension）。

### 任务 2: 验证目标嵌入端点

```bash
curl -s http://127.0.0.1:${LLAMA_PORT}/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"${MODEL_NAME}","input":"test"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['data'][0]['embedding']))"
```

如果无法访问，**停止**。脚本会自动修正 dimension，如果指定的值与实际端点输出不匹配。

### 任务 3: 修改 ov.conf

在修改前将 `ov.conf` 备份到 `ov.conf.bak`。更新 `embedding.dense` 部分：

| Field | Description |
|-------|-------------|
| `provider` | 嵌入提供者名称 |
| `model` | 模型名称（例如，`bge-small-zh-v1.5`） |
| `api_key` | 端点的 API 密钥（本地为空） |
| `api_base` | 端点 URL（例如，`http://127.0.0.1:18200/v1`） |
| `dimension` | 向量维度（从端点自动修正） |

### 任务 4: 删除不兼容的 vectordb 索引

> **⚠️ 关键:** 如果 dimension 不同，需要 `rm -rf vectordb/context`。否则启动时会抛出 `EmbeddingRebuildRequiredError`。

如果 dimension 未改变，跳过此步骤。

### 任务 5: 在沙盒内重启 openviking-server

> **⚠️ 陷阱:** `POST /envs/openviking/stop` + `start` 会重新运行 `start.sh`，这会使用 TokenHub 凭证覆盖 `ov.conf`。**不要使用 stop/start。**

相反：

1. **从主机杀死旧进程**：`kill $PID`，然后轮询端口 1933 释放（最多 10 秒）。如果 SIGTERM 未能释放端口，升级到 `kill -9`。
2. **清理过期的锁文件**：`.openviking.pid` 和 vectordb 的 `LOCK` 文件。
3. **通过 `exec` API 以 `--max-time 15` 启动新服务器**：

```bash
curl -s --max-time 15 -X POST http://127.0.0.1:8090/api/v1/envs/openviking/exec \
  -H 'Content-Type: application/json' \
  -d '{"cmd":["bash","-c","nohup /root/runtime/openviking/venv/bin/openviking-server --config /workspace/process_dir/ov.conf > /workspace/process_dir/openviking-server.log 2>&1 & sleep 2 && echo started"]}'
```

### 任务 6: 验证

1. **带重试循环的健康检查**（最多 30 秒）：每秒轮询 `GET /health`，直到 `healthy=true` 或超时
2. **PID 变更检查**：验证新服务器的 PID 与旧的不同（检测端口冲突假阳性）
3. **集合 dimension 检查**：读取 `collection_meta.json` 并确认 `Dimension` 与目标匹配
4. **日志错误检查**：精确的 grep 查找 `Traceback|ERROR.*Application startup failed|EmbeddingRebuildRequiredError|DataDirectoryLocked`（避免因“重试”信息消息产生的假阳性）
5. **失败时回滚**：如果健康检查失败或 PID 未变更，则恢复 `ov.conf.bak` 并退出报错

## 参数确认

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `MODEL_NAME` | 是 | 嵌入模型名称 | `bge-small-zh-v1.5` |
| `LLAMA_PORT` | 是 | llama-server 端口 | `18200` |
| `TARGET_DIMENSION` | 是 | 向量维度（如果错误会自动修正） | `512` |

```bash
# 使用方法
bash scripts/switch-embedding-model.sh <model_name> <llama_port> <dimension>
```

## 常见嵌入模型维度

| Model | Dimension | Typical Use |
|-------|-----------|-------------|
| `bge-small-zh-v1.5` | 512 | 轻量级中文嵌入 |
| `bge-large-zh-v1.5` | 1024 | 高质量中文嵌入 |
| `bge-small-en-v1.5` | 384 | 轻量级英文嵌入 |
| `bge-base-en-v1.5` | 768 | 通用英文嵌入 |
| `Qwen3-Embedding-0.6B` | 1024 | Qwen3 嵌入（TokenHub 默认） |

## 验证

参考 [references/verification-method.md](references/verification-method.md) 了解分步检查和端到端验收标准。

**快速验证:**
```bash
# 1. 服务器健康
curl -s http://127.0.0.1:1933/health \
  | python3 -c "import sys,json; assert json.load(sys.stdin)['healthy']; print('OK')"

# 2. 集合 dimension 与目标匹配
python3 -c "import json; d=json.load(open('${SANDBOX_DIR}/data/vectordb/context/collection_meta.json')); assert d['Dimension']==${TARGET_DIMENSION}; print('OK')"

# 3. 日志中无错误（精确模式）
grep -ci "Traceback\|Application startup failed\|EmbeddingRebuildRequiredError\|DataDirectoryLocked" \
  "${SANDBOX_DIR}/process_dir/openviking-server.log"
# 预期: 0
```

## 安全机制

参考 [references/guardrails.md](references/guardrails.md) 了解完整规则。关键原则：

- **始终通过 job-env-manager 运行** — 切勿在主机上直接执行 `openviking-server`
- **切勿使用 stop/start 重启** — `start.sh` 会用 TokenHub 凭证覆盖 `ov.conf`
- **修改前验证** — 目标端点必须响应才能进行任何配置更改
- **失败时回滚** — 如果验证失败，会恢复 `ov.conf.bak` 并报错

## 参考

| Document | Description |
|----------|-------------|
| [config-reference.md](references/config-reference.md) | ov.conf 嵌入部分字段参考 |
| [guardrails.md](references/guardrails.md) | 安全规则：沙盒执行、重启顺序、回滚 |
| [iam-policies.md](references/iam-policies.md) | 等效访问控制（无需华为云 IAM） |
| [verification-method.md](references/verification-method.md) | 每个工作流的分步验证 |
| [related-commands.md](references/related-commands.md) | 常用 job-env-manager 和 curl 命令 |
| [acceptance-criteria.md](references/acceptance-criteria.md) | 切换成功的验收标准 |
| [troubleshooting.md](references/troubleshooting.md) | 常见失败场景的故障排除 |
| [dataflow-diagram.md](references/dataflow-diagram.md) | Mermaid 数据流图 |
| [demo/example-input.json](demo/example-input.json) | 切换工作流的示例输入 |
