# NVIDIA RAG 蓝图

## 目的

使用此技能进行 NVIDIA RAG 蓝图操作：部署、配置、故障排除、关闭和功能管理，涵盖 Docker、Helm 和库部署。

## 说明

1. 将用户请求与下方的意图路由表进行匹配。
2. 在进行更改之前，请阅读引用的剧本。
3. 以仓库文档和部署配置文件为事实来源。
4. 更改后验证受影响的服务或工作流。

## 前置条件

- 检出 NVIDIA RAG 蓝图仓库。
- 使用 Docker/Compose 或 Kubernetes/Helm 进行部署。
- 使用库工作流时需要 Python 3.11+。
- 对于自托管 NIM 服务，需要 NVIDIA GPU 工具。

## 自主原则

- 自动检测所有内容：GPU、VRAM、驱动程序、Docker、CUDA、磁盘、操作系统、端口、现有服务、NGC 密钥、仓库状态。
- 如果可以用命令检查，就用命令检查，不要询问用户。
- 仅在需要用户操作时询问：提供 API 密钥、确认数据删除或在不同等价选项之间进行选择。
- 分析完成后，路由到正确的工作流并执行。

## 意图检测

确定用户的意图并立即路由：

| 用户意图 | 操作 |
|---------|------|
| 部署、安装、设置、启动 RAG | 阅读 `references/deploy.md` |
| 配置、启用、更改、切换功能 | 使用下方的配置部分 |
| 故障排除、调试、修复、错误、不健康 | 阅读 `references/troubleshoot.md` |
| 停止、关闭、拆除、清理 | 阅读 `references/shutdown.md` |

如果意图不明确，根据上下文推断（例如，“RAG 无法工作”→ 故障排除；“让 RAG 运行”→ 部署）。只有当确实不清楚时才询问。

---

## 配置

需要运行中的 RAG 部署。如果服务未运行，请先通过 `references/deploy.md` 进行部署。

将用户的请求与参考文件匹配，然后阅读并遵循它：

| 功能关键词 | 参考 |
|-----------|------|
| VLM、VLM 嵌入、图像描述 | `references/configure/vlm.md` |
| NeMo Guardrails | `references/configure/guardrails.md` |
| 智能体 RAG、规划/执行代理、智能体流式传输、阶段事件 | `references/configure/agentic-rag.md` |
| 查询重写、分解、多轮 | `references/configure/query-and-conversation.md` |
|摄取（仅文本、音频、Nemotron Parse、OCR、批量 CLI、NV-Ingest、卷挂载、性能） | `references/configure/ingestion.md` |
| 搜索、检索、混合搜索、多集合、元数据、过滤器、Elasticsearch 过滤器、重新排序器、topK、准确率/性能 | `references/configure/search-and-retrieval.md` |
| LLM/嵌入/排序模型更改、向量数据库、Milvus/Elasticsearch 认证、服务密钥、模型配置文件、端口/GPU | `references/configure/models-and-infrastructure.md` |
| 推理、思考模式、`reasoning_content`、自我反思、提示、生成参数（令牌、温度、引用）、按请求 LLM 参数 | `references/configure/reasoning-and-generation.md` |
| 摘要 | `references/configure/summarization.md` |
| 可观察性（跟踪、Zipkin、Grafana、Prometheus） | `references/configure/observability.md` |
| 多模态查询（图像 + 文本） | `references/configure/multimodal-query.md` |
| 数据目录（集合/文档元数据） | `references/configure/data-catalog.md` |
| 用户界面（UI 设置、推理面板、元数据过滤器） | `references/configure/user-interface.md` |
| API 参考（端点、模式） | `references/configure/api-reference.md` |
| 评估（RAGAS 指标） | `references/configure/evaluation.md`（以及技能 `rag-eval`） |
| MCP 服务器 & 客户端、代理工具包 | `references/configure/mcp.md` |
| 迁移（版本升级） | `references/configure/migration.md` |
| 笔记本（设置和目录） | `references/configure/notebooks.md` |

### 配置流程

1. 将用户的请求与上表中的参考文件匹配。

2. 检测正在运行的内容：
   ```bash
   echo "=== NIM ===" && docker ps --format '{{.Names}}' 2>/dev/null | grep -iE '(nim-llm|nemotron-(vlm-)?embedding|nemotron-ranking|nemotron-vlm|nemotron-3-nano-omni|page-elements|graphic-elements|table-structure|nemotron-ocr)' || echo "NO_LOCAL_NIMS"; echo "=== RAG ===" && docker ps --format '{{.Names}}' 2>/dev/null | grep -iE '(rag-server|ingestor-server|elasticsearch|milvus|seaweedfs|lancedb)' || echo "NO_DOCKER_RAG"; echo "=== K8S ===" && kubectl get pods -n rag 2>/dev/null | head -5 || echo "NO_K8S"; echo "=== LIBRARY ===" && ps aux 2>/dev/null | grep -E '(nvidia_rag|uvicorn.*rag)' | grep -v grep || echo "NO_LIBRARY"
   ```

3. 使用此表确定平台、部署类型以及配置位置：

   | 本地 NIM 正在运行？ | RAG 服务正在运行？ | 部署类型 | 配置位置 |
   |---------------------|-----------------------|-----------------|-----------------|
   | 是（Docker） | 任何 | 自托管 | `deploy/compose/.env` |
   | 否 | 是（Docker） | NVIDIA 托管 | `deploy/compose/nvdev.env` |
   | 是（K8s pod） | 任何 | 自托管 | `values.yaml`（NIM 部分） |
   | 否 | 是（K8s pod） | NVIDIA 托管 | `values.yaml`（envVars） |
   | — | 库进程 | 库模式 | `notebooks/config.yaml` |
   | 否 | 否 | 未运行 | 通过 `references/deploy.md` 部署 |

   告知用户检测到的内容并请求确认。示例：“我看到本地 NIM 容器正在运行（nim-llm-ms、nemotron-vlm-embedding-ms）——这是一个自托管部署。配置文件是 `deploy/compose/.env`。正确吗？”

4. 在更改任何内容之前检查当前功能状态——从步骤 3 读取配置位置，然后交叉检查实时服务：
   - Docker: `docker exec rag-server env 2>/dev/null | grep -E "<VAR_NAME>"`
   - Helm: `kubectl get pod -n rag -l app=rag-server -o jsonpath='{.items[0].spec.containers[0].env}' 2>/dev/null`

   如果配置文件和实时服务不一致，告诉用户服务有陈旧的配置，需要重启。

5. 如果功能需要额外的 GPU，请根据硬件限制检查可用性（见下文）：
   ```bash
   nvidia-smi --query-gpu=index,name,memory.total,memory.used --format=csv,noheader 2>/dev/null || echo "NO_GPU"
   ```

6. 阅读 reference 文件并应用更改：
   - Docker: 编辑 env 文件（取消注释以启用，重新注释以禁用——env 文件是事实来源）。然后重启受影响的服务：
     ```
     source <env-file> && docker compose -f deploy/compose/<compose-file> up -d
     ```
     | 服务 | Compose 文件 |
     |---------|-------------|
     | rag-server | `docker-compose-rag-server.yaml` |
     | ingestor-server | `docker-compose-ingestor-server.yaml` |
     | Elasticsearch、Milvus、etcd、SeaweedFS | `vectordb.yaml` |
     | NIM 容器（LLM、嵌入、排序、VLM、OCR、解析、音频、提取） | `nims.yaml` |
     | guardrails | `docker-compose-nemo-guardrails.yaml` |
     | 可观察性（Grafana、Prometheus、Zipkin） | `observability.yaml` |
   - Helm: 编辑 `values.yaml`，然后升级：`helm upgrade rag <chart> -n rag -f values.yaml`
   - 库：编辑 `notebooks/config.yaml`，然后重启 Python 进程

7. 验证：
   - Docker: `docker ps --format "table {{.Names}}\t{{.Status}}" | head -20; curl -s http://localhost:8081/v1/health?check_dependencies=true 2>/dev/null | head -1`
   - Helm: `kubectl get pods -n rag; kubectl rollout status deployment/rag-server -n rag --timeout=120s`
   - 库：`curl -s http://localhost:8081/v1/health 2>/dev/null | head -1`

8. 如果重启失败，请阅读 `references/troubleshoot.md`。如果请求了多个功能，请对每个功能重复从步骤 1 开始。

## 示例

- "部署 RAG" → 路由到 `references/deploy.md`。
- "启用 VLM" → 路由到 `references/configure/vlm.md`。
- "RAG 不健康" → 路由到 `references/troubleshoot.md`。
- "停止 RAG" → 路由到 `references/shutdown.md`。

## 限制

- 操作指南仅适用于此 RAG 蓝图仓库。
- 实时部署更改需要运行中的 Docker、Helm 或库目标。
- 密钥（如 `NGC_API_KEY`）必须由用户环境提供。

## 故障排除

| 错误/信号 | 应该怎么办 |
|----------------|------------|
| 服务未运行 | 在配置功能之前遵循 `references/deploy.md`。 |
| 重启或健康检查失败 | 遵循 `references/troubleshoot.md`。 |
| 用户请求拆除 | 遵循 `references/shutdown.md` 并确认破坏性清理。 |

### 当用户说“配置”但没有具体说明时

运行上述步骤 2–3，然后读取已识别的配置文件以列出当前启用的内容：
```bash
grep -E "^(export )?(ENABLE_|APP_)" <config-file> 2>/dev/null | sort
```
总结正在运行和启用的内容，然后询问要更改哪个功能。

---

## 硬件限制

阅读 `docs/support-matrix.md` 了解当前每个部署模式的 GPU 要求。
阅读 `docs/service-port-gpu-reference.md` 了解端口映射和 GPU 分配。

| GPU | 功能限制 |
|-----|---------------------|
| B200 | 不能有 VLM、不能有 Guardrails、不能有 Nemotron Parse。可能需要多 GPU LLM (`LLM_MS_GPU_ID`)。 |
| RTX PRO 6000 | 不能有 Nemotron Parse。Helm 上不能有音频。 |
