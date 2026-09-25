# Hugging Face API 工具构建器

你现在需要创建可重用的命令行脚本和工具，用于使用 Hugging Face API，允许链式调用、管道传输和在需要时进行中间处理。你可以直接访问 API，也可以使用 `hf` 命令行工具。模型和数据集卡片可以直接从存储库中访问。

## 脚本规则

确保遵循以下规则：
 - 脚本必须接受 `--help` 命令行参数来描述其输入和输出
 - 非破坏性脚本在交给用户之前应进行测试
 - 优先使用 Shell 脚本，但如果复杂性或用户需求需要，可以使用 Python 或 TSX。
 - 重要提示：使用 `HF_TOKEN` 环境变量作为授权头。例如：`curl -H "Authorization: Bearer ${HF_TOKEN}" https://huggingface.co/api/`。这提供了更高的速率限制和适当的数据访问授权。
 - 在提交最终设计之前，调查 API 结果的形状；在组合性有优势的地方使用管道和链式调用；尽可能选择简单的解决方案。
 - 完成后分享使用示例。

在需要问题或澄清时，务必确认用户偏好。

## 示例脚本

下面的路径相对于此技能目录。

参考示例：
- `references/hf_model_papers_auth.sh` — 自动使用 `HF_TOKEN`，并链式调用趋势 → 模型元数据 → 模型卡片解析（带回退）；它展示了多步 API 使用以及受保护/私有内容的授权规范。
- `references/find_models_by_paper.sh` — 通过 `--token` 可选使用 `HF_TOKEN`，一致的认证搜索，以及在 arXiv 前缀搜索过于狭窄时提供重试路径；它展示了弹性的查询策略和清晰的用户界面帮助。
- `references/hf_model_card_frontmatter.sh` — 使用 `hf` CLI 下载模型卡片，提取 YAML 前置信息，并发出 NDJSON 摘要（许可证、管道标签、标签、受保护提示标志）以便于过滤。

基准示例（超简单、最小逻辑、原始 JSON 输出带 `HF_TOKEN` 头）：
- `references/baseline_hf_api.sh` — bash
- `references/baseline_hf_api.py` — python
- `references/baseline_hf_api.tsx` — typescript 可执行文件

组合式工具（stdin → NDJSON）：
- `references/hf_enrich_models.sh` — 从 stdin 读取模型 ID，按 ID 获取元数据，为流式管道每行发出一个 JSON 对象。

通过管道实现的组合性（对 Shell 友好的 JSON 输出）：
- `references/baseline_hf_api.sh 25 | jq -r '.[].id' | references/hf_enrich_models.sh | jq -s 'sort_by(.downloads) | reverse | .[:10]'`
- `references/baseline_hf_api.sh 50 | jq '[.[] | {id, downloads}] | sort_by(.downloads) | reverse | .[:10]'`
- `printf '%s\n' openai/gpt-oss-120b meta-llama/Meta-Llama-3.1-8B | references/hf_model_card_frontmatter.sh | jq -s 'map({id, license, has_extra_gated_prompt})'`

## 高级端点

以下是在 `https://huggingface.co` 可用的主要 API 端点：

```
/api/datasets
/api/models
/api/spaces
/api/collections
/api/daily_papers
/api/notifications
/api/settings
/api/whoami-v2
/api/trending
/oauth/userinfo
```

## 访问 API

API 使用 OpenAPI 标准进行文档化，位于 `https://huggingface.co/.well-known/openapi.json`。

**重要提示：** 不要尝试直接读取 `https://huggingface.co/.well-known/openapi.json`，因为它太大而无法处理。

**重要** 使用 `jq` 查询和提取相关部分。例如，

获取所有 160 个端点的命令

```bash
curl -s "https://huggingface.co/.well-known/openapi.json" | jq '.paths | keys | sort'
```

模型搜索端点详细信息

```bash
curl -s "https://huggingface.co/.well-known/openapi.json" | jq '.paths["/api/models"]'
```

你也可以查询端点以查看数据的形状。在这样做时，将结果限制为低数字以使其易于处理，同时具有代表性。

## 使用 HF 命令行工具

`hf` 命令行工具为你提供了进一步访问 Hugging Face 存储库内容和基础设施的途径。

```bash
❯ hf --help
Usage: hf [OPTIONS] COMMAND [ARGS]...

  Hugging Face Hub CLI

Options:
  --help                Show this message and exit.

Commands:
  auth                 Manage authentication (login, logout, etc.).
  buckets              Commands to interact with buckets.
  cache                Manage local cache directory.
  collections          Interact with collections on the Hub.
  datasets             Interact with datasets on the Hub.
  discussions          Manage discussions and pull requests on the Hub.
  download             Download files from the Hub.
  endpoints            Manage Hugging Face Inference Endpoints.
  env                  Print information about the environment.
  extensions           Manage hf CLI extensions.
  jobs                 Run and manage Jobs on the Hub.
  models               Interact with models on the Hub.
  papers               Interact with papers on the Hub.
  repos                Manage repos on the Hub.
  skills               Manage skills for AI assistants.
  spaces               Interact with spaces on the Hub.
  sync                 Sync files between local directory and a bucket.
  upload               Upload a file or a folder to the Hub.
  upload-large-folder  Upload a large folder to the Hub.
  version              Print information about the hf version.
  webhooks             Manage webhooks on the Hub.
```

`hf` CLI 命令已取代现已弃用的 `huggingface-cli` 命令。
