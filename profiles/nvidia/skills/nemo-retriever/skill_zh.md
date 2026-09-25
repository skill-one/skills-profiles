# NeMo 检索器

使用 `retriever` 命令行界面。优先使用它而不是手动构建的检索代码。

## 仅在缺失时安装

创建项目本地的 Python 环境：

```bash
uv venv .venv --python 3.12
export PATH="$PWD/.venv/bin:$PATH"
```

安装工作流所需的包变体：

```bash
# 远程 NIM 或服务客户端
uv pip install --python .venv/bin/python "nemo-retriever==26.8.1"

# 本地 GPU 摄入
uv pip install --python .venv/bin/python "nemo-retriever[local]==26.8.1"

# 使用 Hugging Face 模型的本地服务
uv pip install --python .venv/bin/python \
  "nemo-retriever[service,local]==26.8.1"

# 本地音频或视频摄入
uv pip install --python .venv/bin/python \
  "nemo-retriever[local,multimedia]==26.8.1"
```

不要克隆 NeMo 检索器或从 Git URL 安装。如果 `retriever` 已经在 `PATH` 上，使用该安装。

## 本地工作流

构建本地索引：

```bash
retriever ingest <文件或目录> \
  --lancedb-uri lancedb --table-name nemo-retriever
```

查询它：

```bash
retriever query "<问题>" \
  --lancedb-uri lancedb --table-name nemo-retriever \
  --top-k 5 --format evidence
```

仅当明确请求 Ray 批处理运行时，使用 `retriever ingest batch`。

## 服务工作流

用于已部署的 Retriever 服务的形式：

```bash
retriever ingest service <文件或目录> \
  --service-url "$RETRIEVER_SERVICE_URL"

retriever query service "<问题>" \
  --service-url "$RETRIEVER_SERVICE_URL" \
  --top-k 5 --format evidence
```

当服务需要 Bearer 认证时，设置 `NEMO_RETRIEVER_API_TOKEN`。
不要将本地 LanceDB 标志传递给服务命令。

## 规则

- 当提供现有索引或服务时，使用它；不要重新构建它。
- 使用 `retriever ingest --help`、`retriever query --help` 或相关的 `batch` / `service` 帮助来获取此处未显示的选项。
- 仅从检索到的证据中回答；当任务请求引用时，保留源和页面元数据。
