---
name: hf-cli
description: Hugging Face Hub 命令行界面 (`hf`) 用于在 Hugging Face Hub 上下载、上传和管理模型、数据集、空间、存储桶、仓库、论文、任务等。使用场景包括：处理身份验证；管理本地缓存；管理 Hugging Face 存储桶；在 Hugging Face 基础设施上运行或调度任务；管理 Hugging Face 仓库；进行讨论和拉取请求；浏览模型、数据集和空间；阅读、搜索或浏览学术论文；管理集合；查询数据集；配置空间；设置 Webhook；部署和管理 HF 推理端点。当用户提到 'hf'、'huggingface'、'Hugging Face'、'huggingface-cli' 或 'hugging face cli'，或希望进行与 Hugging Face 生态系统以及 AI 和 ML 相关的任何操作时，请确保使用此技能。也适用于云存储需求，如训练检查点、数据管道或代理跟踪。即使用户没有明确要求 CLI 命令，也请使用。替代已弃用的 `huggingface-cli`。
---

安装：`curl -LsSf https://hf.co/cli/install.sh | bash -s`。

Hugging Face Hub CLI 工具 `hf` 已可用。重要提示：`hf` 命令已取代已弃用的 `huggingface-cli` 命令。

使用 `hf --help` 查看可用功能。请注意，认证命令现在都在 `hf auth` 下，例如 `hf auth whoami`。

使用 `huggingface_hub v2.0.0` 生成。运行 `hf skills add --force` 以重新生成。

## 命令

- `hf cp SRC` — 在本地路径、存储库和存储桶之间复制文件。[`--format [auto|human|agent|json|quiet]`]
- `hf download REPO_ID` — 从 Hub 下载文件。[`--type [model|dataset|space|kernel] --revision TEXT --include TEXT --exclude TEXT --cache-dir TEXT --local-dir TEXT --force-download --dry-run --max-workers INTEGER --format [auto|human|agent|json|quiet]`]
- `hf env` — 打印环境信息。[`--format [auto|human|agent|json|quiet]`]
- `hf sync` — 在本地目录和存储桶之间同步文件。[`--delete --ignore-times --ignore-sizes --plan TEXT --apply TEXT --dry-run --include TEXT --exclude TEXT --filter-from TEXT --existing --ignore-existing --verbose --format [auto|human|agent|json|quiet]`]
- `hf update` — 将 `hf` CLI 更新到最新版本。[`--format [auto|human|agent|json|quiet]`]
- `hf upload REPO_ID` — 将文件或文件夹上传到 Hub。推荐用于单提交上传。[`--type [model|dataset|space|kernel] --revision TEXT --private --include TEXT --exclude TEXT --delete TEXT --commit-message TEXT --commit-description TEXT --create-pr --every FLOAT --format [auto|human|agent|json|quiet]`]
- `hf version` — 打印有关 hf 版本的信息。[`--format [auto|human|agent|json|quiet]`]

### `hf auth` — 管理认证（登录、登出等）。

- `hf auth list` — 列出所有存储的访问令牌。[`--format [auto|human|agent|json|quiet]`]
- `hf auth login` — 通过浏览器登录，或使用来自 huggingface.co/settings/tokens 的令牌。[`--add-to-git-credential --force --format [auto|human|agent|json|quiet]`]
- `hf auth logout` — 从特定令牌登出。[`--token-name TEXT --format [auto|human|agent|json|quiet]`]
- `hf auth switch` — 在访问令牌之间切换。[`--token-name TEXT --add-to-git-credential --format [auto|human|agent|json|quiet]`]
- `hf auth token` — 将当前访问令牌打印到标准输出。[`--format [auto|human|agent|json|quiet]`]
- `hf auth whoami` — 查找您登录的 huggingface.co 账户。[`--format [auto|human|agent|json|quiet]`]

### `hf buckets` — 与存储桶交互的命令。

- `hf buckets cp SRC` — 在本地路径、存储库和存储桶之间复制文件。[`--format [auto|human|agent|json|quiet]`]
- `hf buckets create BUCKET_ID` — 创建新存储桶。[`--private --region [us|eu] --exist-ok --format [auto|human|agent|json|quiet]`]
- `hf buckets delete BUCKET_ID` — 删除存储桶。[`--yes --missing-ok --format [auto|human|agent|json|quiet]`]
- `hf buckets info BUCKET_ID` — 获取存储桶信息。[`--format [auto|human|agent|json|quiet]`]
- `hf buckets list` — 列出存储桶或存储桶中的文件。[`--human-readable --tree --recursive --search TEXT --format [auto|human|agent|json|quiet]`]
- `hf buckets move FROM_ID TO_ID` — 将存储桶移动（重命名）到新名称或命名空间。[`--format [auto|human|agent|json|quiet]`]
- `hf buckets remove ARGUMENT` — 从存储桶中删除文件。[`--recursive --yes --dry-run --include TEXT --exclude TEXT --format [auto|human|agent|json|quiet]`]
- `hf buckets settings BUCKET_ID` — 更新存储桶设置（可见性）。[`--private --public --format [auto|human|agent|json|quiet]`]
- `hf buckets sync` — 在本地目录和存储桶之间同步文件。[`--delete --ignore-times --ignore-sizes --plan TEXT --apply TEXT --dry-run --include TEXT --exclude TEXT --filter-from TEXT --existing --ignore-existing --verbose --format [auto|human|agent|json|quiet]`]

### `hf cache` — 管理本地缓存目录。

- `hf cache list` — 列出缓存的存储库或修订版本。[`--cache-dir TEXT --revisions --filter TEXT --sort [accessed|accessed:asc|accessed:desc|modified|modified:asc|modified:desc|name|name:asc|name:desc|size|size:asc|size:desc] --limit INTEGER --show-warnings --format [auto|human|agent|json|quiet]`]
- `hf cache prune` — 从缓存中删除分离的修订版本和不完整的下载。[`--cache-dir TEXT --yes --dry-run --format [auto|human|agent|json|quiet]`]
- `hf cache rm TARGETS` — 删除缓存的存储库、修订版本或文件。[`--cache-dir TEXT --yes --dry-run --format [auto|human|agent|json|quiet]`]
- `hf cache verify REPO_ID` — 验证缓存或本地目录中单个存储库修订版本的校验和。[`--type [model|dataset|space|kernel] --revision TEXT --cache-dir TEXT --local-dir TEXT --fail-on-missing-files --fail-on-extra-files --format [auto|human|agent|json|quiet]`]

### `hf collections` — 与 Hub 上的集合交互。

- `hf collections add-item COLLECTION_SLUG ITEM_ID ITEM_TYPE` — 将项目添加到集合。[`--note TEXT --exists-ok --format [auto|human|agent|json|quiet]`]
- `hf collections create TITLE` — 在 Hub 上创建新集合。[`--namespace TEXT --description TEXT --private --exists-ok --format [auto|human|agent|json|quiet]`]
- `hf collections delete COLLECTION_SLUG` — 从 Hub 删除集合。[`--missing-ok --format [auto|human|agent|json|quiet]`]
- `hf collections delete-item COLLECTION_SLUG ITEM_OBJECT_ID` — 从集合中删除项目。[`--missing-ok --format [auto|human|agent|json|quiet]`]
- `hf collections info COLLECTION_SLUG` — 获取 Hub 上集合的信息。[`--format [auto|human|agent|json|quiet]`]
- `hf collections list` — 列出 Hub 上的集合。[`--owner TEXT --item TEXT --sort [lastModified|trending|upvotes] --limit INTEGER --format [auto|human|agent|json|quiet]`]
- `hf collections update COLLECTION_SLUG` — 更新 Hub 上集合的元数据。[`--title TEXT --description TEXT --position INTEGER --private --theme TEXT --format [auto|human|agent|json|quiet]`]
- `hf collections update-item COLLECTION_SLUG ITEM_OBJECT_ID` — 更新集合中的项目。[`--note TEXT --position INTEGER --format [auto|human|agent|json|quiet]`]

### `hf datasets` — 与 Hub 上的数据集交互。

- `hf datasets card DATASET_ID` — 获取 Hub 上数据集的数据集卡片（README）。[`--metadata --text --format [auto|human|agent|json|quiet]`]
- `hf datasets info DATASET_ID` — 获取 Hub 上数据集的信息。[`--revision TEXT --expand TEXT --format [auto|human|agent|json|quiet]`]
- `hf datasets leaderboard DATASET_ID` — 列出数据集排行榜中的模型分数。此命令有助于找到最佳模型或通过基准分数比较模型。使用 'hf datasets ls --filter benchmark:official' 列出可用排行榜。[`--limit INTEGER --format [auto|human|agent|json|quiet]`]
- `hf datasets list` — 列出 Hub 上的数据集，或数据集存储库中的文件。[`--search TEXT --author TEXT --filter TEXT --sort [created_at|downloads|last_modified|likes|trending_score] --limit INTEGER --expand TEXT --human-readable --tree --recursive --revision TEXT --format [auto|human|agent|json|quiet]`]
- `hf datasets parquet DATASET_ID` — 列出数据集可用的 parquet 文件 URL。[`--subset TEXT --split TEXT --format [auto|human|agent|json|quiet]`]
- `hf datasets sql SQL` — 使用 DuckDB 对数据集 parquet URL 执行原始 SQL 查询。[`--format [auto|human|agent|json|quiet]`]

### `hf discussions` — 管理 Hub 上的讨论和拉取请求。

- `hf discussions close REPO_ID NUM` — 关闭讨论或拉取请求。[`--comment TEXT --yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions comment REPO_ID NUM` — 在讨论或拉取请求上评论。[`--body TEXT --body-file PATH --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions create REPO_ID --title TEXT` — 在存储库上创建新的讨论或拉取请求。[`--body TEXT --body-file PATH --pull-request --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions diff REPO_ID NUM` — 显示拉取请求的差异。[`--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions edit REPO_ID NUM COMMENT_ID` — 编辑讨论或拉取请求上的现有评论。[`--body TEXT --body-file PATH --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions info REPO_ID NUM` — 获取讨论或拉取请求的信息。[`--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions list REPO_ID` — 列出存储库上的讨论和拉取请求。[`--status [open|closed|merged|draft|all] --kind [all|discussion|pull_request] --author TEXT --limit INTEGER --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions merge REPO_ID NUM` — 合并拉取请求。[`--comment TEXT --yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions rename REPO_ID NUM NEW_TITLE` — 重命名讨论或拉取请求。[`--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]
- `hf discussions reopen REPO_ID NUM` — 重新打开已关闭的讨论或拉取请求。[`--comment TEXT --yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]`]

### `hf endpoints` — 管理 Hugging Face 推理端点。

- `hf endpoints catalog deploy --repo TEXT` — 从模型目录部署推理端点。[`--name TEXT --accelerator TEXT --namespace TEXT --format [auto|human|agent|json|quiet]`]
- `hf endpoints catalog list` — 列出可用目录模型。[`--format [auto|human|agent|json|quiet]`]
- `hf endpoints delete NAME` — 永久删除推理端点。[`--namespace TEXT --yes --format [auto|human|agent|json|quiet]`]
- `hf endpoints deploy NAME --repo TEXT --framework TEXT --accelerator TEXT --instance-size TEXT --instance-type TEXT --region TEXT --vendor TEXT` — 从 Hub 存储库部署推理端点。[`--namespace TEXT --task TEXT --min-replica INTEGER --max-replica INTEGER --scale-to-zero-timeout INTEGER --scaling-metric [pendingRequests|hardwareUsage] --scaling-threshold FLOAT --revision TEXT --custom-image TEXT --engine [custom|hf-serve|llamacpp|sglang|tei|tgi|tgi-neuron|vllm|vllm-neuron] --health-route TEXT --port INTEGER --container-registry-username TEXT --container-registry-password TEXT --tensor-parallel-size INTEGER --data-parallel-size INTEGER --container-command TEXT --container-args TEXT --env TEXT --env-file TEXT --secrets TEXT --secrets-file TEXT --type [public|authenticated|private] --format [auto|human|agent|json|quiet]`]
- `hf endpoints describe NAME` — 获取现有端点的信息。[`--namespace TEXT --format [auto|human|agent|json|quiet]`]
- `hf endpoints hardware` — 列出可用于部署推理端点的硬件。[`--namespace TEXT --vendor TEXT --region TEXT --accelerator TEXT --instance-type TEXT --all --format [auto|human|agent|json|quiet]`]
- `hf endpoints list` — 列出给定命名空间的所有推理端点。[`--namespace TEXT --format [auto|human|agent|json|quiet]`]
- `hf endpoints pause NAME` — 暂停推理端点。[`--namespace TEXT --format [auto|human|agent|json|quiet]`]
- `hf endpoints resume NAME` — 恢复推理端点。[`--namespace TEXT --fail-if-already-running --format [auto|human|agent|json|quiet]`]
- `hf endpoints scale-to-zero NAME` — 将推理端点缩放到零。[`--namespace TEXT --format [auto|human|agent|json|quiet]`]
- `hf endpoints update NAME` — 更新现有端点。[`--namespace TEXT --repo TEXT --accelerator TEXT --instance-size TEXT --instance-type TEXT --framework TEXT --revision TEXT --task TEXT --custom-image TEXT --engine [custom|hf-serve|llamacpp|sglang|tei|tgi|tgi-neuron|vllm|vllm-neuron] --health-route TEXT --port INTEGER --tensor-parallel-size INTEGER --data-parallel-size INTEGER --container-command TEXT --container-args TEXT --min-replica INTEGER --max-replica INTEGER --scale-to-zero-timeout INTEGER --scaling-metric [pendingRequests|hardwareUsage] --scaling-threshold FLOAT --format [auto|human|agent|json|quiet]`]

### `hf extensions` — 管理 hf CLI 扩展。

- `hf extensions exec NAME` — 执行已安装的扩展。
- `hf extensions install REPO_ID` — 从公共 GitHub 存储库安装扩展。[`--force --format [auto|human|agent|json|quiet]`]
- `hf extensions list` — 列出已安装的扩展命令。[`--format [auto|human|agent|json|quiet]`]
- `hf extensions remove NAME` — 删除已安装的扩展。[`--format [auto|human|agent|json|quiet]`]
- `hf extensions search` — 搜索 GitHub 上可用的扩展（标记为 'hf-extension' 主题）。[`--format [auto|human|agent|json|quiet]`]
- `hf extensions update` — 将已安装的扩展更新到最新版本。[`--format [auto|human|agent|json|quiet]`]

### `hf jobs` — 在 Hub 上运行和管理 Jobs。

- `hf jobs cancel JOB_ID` — 取消作业 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs hardware` — 列出作业的可用硬件选项 `[--format [自动|人类|代理|JSON|安静]]`
- `hf jobs inspect JOB_IDS` — 显示一个或多个作业的详细信息 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs labels JOB_ID` — 更新作业上的标签。传递 --label 会替换所有现有标签；单独传递 --name 会保留它们 `[--name 文本 --label 文本 --clear --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs list` — 列出作业 `[--all --status [已完成|已取消|错误|已删除|调度中|运行中] --label 文本 --name 文本 --limit 整数 --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs logs JOB_ID` — 获取作业的日志 `[--follow --tail 整数 --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs run IMAGE COMMAND` — 运行作业 `[--env 文本 --secrets 文本 --name 文本 --label 文本 --volume 文本 --env-file 文本 --secrets-file 文本 --flavor [cpu-基础版|cpu-升级版|cpu-性能版|cpu-xl|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --timeout 文本 --detach --dry-run --expose 整数 --ssh --network-group 文本 --network-别名 文本 --resource-group-id 文本 --namespace 文本 --format [代理|自动|人类|JSON|安静] --json --quiet]`
- `hf jobs scheduled delete SCHEDULED_JOB_ID` — 删除计划作业 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled inspect SCHEDULED_JOB_IDS` — 显示一个或多个计划作业的详细信息 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled labels SCHEDULED_JOB_ID` — 更新计划作业上的标签。传递 --label 会替换所有现有标签；单独传递 --name 会保留它们 `[--name 文本 --label 文本 --clear --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled list` — 列出计划作业 `[--all --status [活跃|暂停] --label 文本 --name 文本 --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled resume SCHEDULED_JOB_ID` — 恢复（暂停）计划作业 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled run SCHEDULE IMAGE COMMAND` — 安排作业 `[--suspend --concurrency --env 文本 --secrets 文本 --name 文本 --label 文本 --volume 文本 --env-file 文本 --secrets-file 文本 --flavor [cpu-基础版|cpu-升级版|cpu-性能版|cpu-xl|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --timeout 文本 --dry-run --expose 整数 --resource-group-id 文本 --namespace 文本 --format [代理|自动|人类|JSON|安静] --json --quiet]`
- `hf jobs scheduled suspend SCHEDULED_JOB_ID` — 暂停（暂停）计划作业 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled trigger SCHEDULED_JOB_ID` — 触发计划作业立即运行（不会更改计划）。 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs scheduled uv run SCHEDULE SCRIPT` — 在 HF 基础设施上运行 UV 脚本（本地文件或 URL） `[--suspend --concurrency --image 文本 --flavor [cpu-基础版|cpu-升级版|cpu-性能版|cpu-xl|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --env 文本 --secrets 文本 --name 文本 --label 文本 --volume 文本 --env-file 文本 --secrets-file 文本 --timeout 文本 --dry-run --expose 整数 --resource-group-id 文本 --namespace 文本 --with 文本 --python 文本 --format [代理|自动|人类|JSON|安静] --json --quiet]`
- `hf jobs ssh JOB_ID` — SSH 到正在运行的作业 `[--identity-file 路径 --dry-run --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs stats` — 获取作业的资源使用统计和指标 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf jobs uv run SCRIPT` — 在 HF 基础设施上运行 UV 脚本（本地文件或 URL） `[--image 文本 --flavor [cpu-基础版|cpu-升级版|cpu-性能版|cpu-xl|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --env 文本 --secrets 文本 --name 文本 --label 文本 --volume 文本 --env-file 文本 --secrets-file 文本 --timeout 文本 --detach --dry-run --expose 整数 --ssh --network-group 文本 --network-别名 文本 --resource-group-id 文本 --namespace 文本 --with 文本 --python 文本 --format [代理|自动|人类|JSON|安静] --json --quiet]`
- `hf jobs wait JOB_IDS` — 等待一个或多个作业达到终端状态 `[--timeout 文本 --namespace 文本 --format [自动|人类|代理|JSON|安静]]`

### `hf models` — 与 Hub 上的模型交互。

- `hf models card MODEL_ID` — 获取 Hub 上模型的模型卡（README）。 `[--metadata --text --format [自动|人类|代理|JSON|安静]]`
- `hf models info MODEL_ID` — 获取 Hub 上模型的信息。 `[--revision 文本 --expand 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf models list` — 列出 Hub 上的模型，或模型存储库中的文件。 `[--search 文本 --author 文本 --filter 文本 --pipeline-tag 文本 --gated --apps 文本 --num-parameters 文本 --inference-provider [baseten|cerebras|cohere|deepinfra|fal-ai|featherless-ai|fireworks-ai|groq|hf-inference|novita|nscale|openai|ovhcloud|publicai|replicate|scaleway|together|wavespeed|zai-org] --warm --sort [创建时间|下载量|最后修改时间|点赞|trending_score] --limit 整数 --expand 文本 --human-readable --tree --递归 --revision 文本 --format [自动|人类|代理|JSON|安静]]`

### `hf papers` — 与 Hub 上的论文交互。

- `hf papers info PAPER_ID` — 获取 Hub 上论文的信息。 `[--format [自动|人类|代理|JSON|安静]]`
- `hf papers list` — 列出 Hub 上的每日论文。 `[--date 文本 --week 文本 --month 文本 --submitter 文本 --sort [publishedAt|trending] --limit 整数 --format [自动|人类|代理|JSON|安静]]`
- `hf papers read PAPER_ID` — 以 markdown 格式阅读论文。 `[--format [自动|人类|代理|JSON|安静]]`
- `hf papers search QUERY` — 在 Hub 上搜索论文。 `[--limit 整数 --format [自动|人类|代理|JSON|安静]]`

### `hf repos` — 管理 Hub 上的存储库。

- `hf repos branch create REPO_ID BRANCH` — 在 Hub 上为存储库创建一个新分支。 `[--revision 文本 --type [模型|数据集|空间|内核] --exist-ok --format [自动|人类|代理|JSON|安静]]`
- `hf repos branch delete REPO_ID BRANCH` — 从 Hub 上的存储库删除一个分支。 `[--type [模型|数据集|空间|内核] --format [自动|人类|代理|JSON|安静]]`
- `hf repos cp SRC` — 在本地路径、存储库和存储桶之间复制文件。 `[--format [自动|人类|代理|JSON|安静]]`
- `hf repos create REPO_ID` — 在 Hub 上创建一个新存储库。 `[--type [模型|数据集|空间|内核] --sdk 文本 --template 文本 --private --public --protected --exist-ok --resource-group-id 文本 --region [us|eu] --flavor [cpu-基础版|cpu-升级版|zero-a10g|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8] --sleep-time 整数 --secrets 文本 --secrets-file 文本 --env 文本 --env-file 文本 --volume 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf repos delete REPO_ID` — 从 Hub 删除存储库。这是一个不可逆的操作。 `[--type [模型|数据集|空间|内核] --missing-ok --yes --format [自动|人类|代理|JSON|安静]]`
- `hf repos delete-files REPO_ID PATTERNS` — 从 Hub 上的存储库删除文件。 `[--type [模型|数据集|空间|内核] --revision 文本 --commit-message 文本 --commit-description 文本 --create-pr --format [自动|人类|代理|JSON|安静]]`
- `hf repos duplicate FROM_ID` — 在 Hub 上复制存储库（模型、数据集或 Space）。 `[--type [模型|数据集|空间|内核] --private --public --protected --exist-ok --flavor [cpu-基础版|cpu-升级版|zero-a10g|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8] --sleep-time 整数 --secrets 文本 --secrets-file 文本 --env 文本 --env-file 文本 --volume 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf repos list` — 列出所有存储库（模型、数据集、空间、存储桶）并显示存储信息。 `[--namespace 文本 --type [模型|数据集|空间|存储桶] --search 文本 --limit 整数 --explore --format [自动|人类|代理|JSON|安静]]`
- `hf repos move FROM_ID TO_ID` — 将存储库从一个命名空间移动到另一个命名空间。 `[--type [模型|数据集|空间|内核] --format [自动|人类|代理|JSON|安静]]`
- `hf repos settings REPO_ID` — 更新存储库的设置。 `[--gated [自动|手动|false] --private --public --protected --type [模型|数据集|空间|内核] --format [自动|人类|代理|JSON|安静]]`
- `hf repos tag create REPO_ID TAG` — 为存储库创建一个标签。 `[--message 文本 --revision 文本 --type [模型|数据集|空间|内核] --format [自动|人类|代理|JSON|安静]]`
- `hf repos tag delete REPO_ID TAG` — 删除存储库的标签。 `[--yes --type [模型|数据集|空间|内核] --format [自动|人类|代理|JSON|安静]]`
- `hf repos tag list REPO_ID` — 列出存储库的标签。 `[--type [模型|数据集|空间|内核] --format [自动|人类|代理|JSON|安静]]`

### `hf sandbox` — 在 Hugging Face Jobs 上运行和管理实验性沙盒。

- `hf sandbox cp SRC DST` — 在本地机器和沙盒之间复制文件（docker 风格）。 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox create` — 创建沙盒：默认情况下是专用虚拟机，或使用 `--pool` 创建一个廉价的共享沙盒。 `[--pool 文本 --flavor [cpu-基础版|cpu-升级版|cpu-性能版|cpu-xl|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --idle-timeout 文本 --env 文本 --secrets 文本 --label 文本 --env-file 文本 --secrets-file 文本 --volume 文本 --namespace 文本 --forward-hf-token --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox exec SANDBOX_ID COMMAND` — 在沙盒中运行命令并流式传输输出。使用命令的退出代码退出。 `[--workdir 文本 --env 文本 --env-file 文本 --timeout 浮点数 --namespace 文本]`
- `hf sandbox kill` — 终止沙盒、整个共享主机或所有内容（--all）。 `[--all --yes --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox pool create` — 加热池：立即启动一个主机虚拟机，并标记它以便稍后通过其池 ID 找到。 `[--flavor [cpu-基础版|cpu-升级版|cpu-性能版|cpu-xl|t4-小|t4-中|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-小|a10g-大|a10g-大x2|a10g-大x4|a100-大|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --per-host 整数 范围 --max-hosts 整数 范围 --idle-timeout 文本 --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox pool delete POOL_ID` — 终止池中的每个主机虚拟机（因此所有其沙盒）。 `[--yes --namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox pool ls` — 列出正在运行的沙盒池（按其主机虚拟机分组）。 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox process kill SANDBOX_ID PID` — 停止沙盒中运行的背景进程。 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox process ls SANDBOX_ID` — 列出沙盒中运行的背景进程（使用 `hf sandbox spawn` 启动）。 `[--namespace 文本 --format [自动|人类|代理|JSON|安静]]`
- `hf sandbox spawn SANDBOX_ID COMMAND` — 在后台启动一个长时间运行的命令并返回其 pid（不等待）。 `[--workdir 文本 --env 文本 --env-file 文本 --namespace 文本]`

### `hf skills` — 管理人工智能助手的技能。

- `hf skills add` — 为人工智能助手安装 Hugging Face 技能。 `[--global --dest 路径 --force --format [自动|人类|代理|JSON|安静]]`
- `hf skills list` — 列出 Hugging Face 市场上的可用技能。 `[--format [自动|人类|代理|JSON|安静]]`
- `hf skills preview` — 将生成的 `hf-cli` SKILL.md 打印到标准输出。 `[--format [自动|人类|代理|JSON|安静]]`
- `hf skills update` — 更新已安装的 Hugging Face 市场技能。 `[--global --dest 路径 --format [自动|人类|代理|JSON|安静]]`

### `hf spaces` — 与 Hub 上的空间交互。

- `hf spaces card SPACE_ID` — 获取 Hub 上某个 Space 的 Space 卡（README）。`[--metadata --text --format [auto|human|agent|json|quiet]]`
- `hf spaces dev-mode SPACE_ID` — 启用或禁用 Space 上的开发模式。`[--stop --format [auto|human|agent|json|quiet]]`
- `hf spaces hardware` — 列出 Spaces 的可用硬件选项。`[--format [auto|human|agent|json|quiet]]`
- `hf spaces hot-reload SPACE_ID` — 无需完整重建+重启，热重载 Space 的任何 Python 文件。`[--local-file PATH --skip-checks --skip-summary --format [auto|human|agent|json|quiet]]`
- `hf spaces info SPACE_ID` — 获取 Hub 上某个 Space 的信息。`[--revision TEXT --expand TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces list` — 列出 Hub 上的 Spaces，或 Space 仓库中的文件。`[--search TEXT --author TEXT --filter TEXT --sort [created_at|last_modified|likes|trending_score] --limit INTEGER --expand TEXT --human-readable --tree --recursive --revision TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces logs SPACE_ID` — 获取 Space 的运行或构建日志。`[--build --follow --tail INTEGER --format [auto|human|agent|json|quiet]]`
- `hf spaces pause SPACE_ID` — 暂停一个 Space。`[--format [auto|human|agent|json|quiet]]`
- `hf spaces restart SPACE_ID` — 重新启动一个 Space。`[--factory-reboot --format [auto|human|agent|json|quiet]]`
- `hf spaces search QUERY` — 使用语义搜索在 Hub 上搜索 Spaces。`[--filter TEXT --sdk TEXT --include-non-running --description --limit INTEGER --format [auto|human|agent|json|quiet]]`
- `hf spaces secrets add SPACE_ID` — 为 Space 添加或更新密钥。`[--secrets TEXT --secrets-file TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces secrets delete SPACE_ID KEY` — 从 Space 中删除一个密钥。`[--yes --format [auto|human|agent|json|quiet]]`
- `hf spaces secrets list SPACE_ID` — 列出 Space 的密钥。密钥值是只写且不返回。`[--format [auto|human|agent|json|quiet]]`
- `hf spaces settings SPACE_ID` — 更新 Space 的设置。`[--sleep-time INTEGER --hardware [cpu-basic|cpu-upgrade|zero-a10g|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8] --format [auto|human|agent|json|quiet]]`
- `hf spaces ssh SPACE_ID` — 进入 Space 的开发模式容器。`[--identity-file PATH --dry-run --auto --format [auto|human|agent|json|quiet]]`
- `hf spaces templates` — 列出可用的 Space 模板。`[--format [auto|human|agent|json|quiet]]`
- `hf spaces variables add SPACE_ID` — 为 Space 添加或更新环境变量。`[--env TEXT --env-file TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces variables delete SPACE_ID KEY` — 从 Space 中删除一个环境变量。`[--yes --format [auto|human|agent|json|quiet]]`
- `hf spaces variables list SPACE_ID` — 列出 Space 的环境变量。`[--format [auto|human|agent|json|quiet]]`
- `hf spaces volumes delete SPACE_ID` — 从 Space 中删除所有卷。`[--yes --format [auto|human|agent|json|quiet]]`
- `hf spaces volumes list SPACE_ID` — 列出 Space 中挂载的卷。`[--format [auto|human|agent|json|quiet]]`
- `hf spaces volumes set SPACE_ID` — 为 Space 设置（替换）卷。`[--volume TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces wait SPACE_ID` — 等待 Space 完成构建/启动。`[--timeout TEXT --format [auto|human|agent|json|quiet]]`

### `hf webhooks` — 管理 Hub 上的 webhooks。

- `hf webhooks create --watch TEXT` — 创建一个新的 webhook。`[--url TEXT --job-id TEXT --domain [repo|discussions] --secret TEXT --format [auto|human|agent|json|quiet]]`
- `hf webhooks delete WEBHOOK_ID` — 永久删除一个 webhook。`[--yes --format [auto|human|agent|json|quiet]]`
- `hf webhooks disable WEBHOOK_ID` — 禁用一个活动的 webhook。`[--format [auto|human|agent|json|quiet]]`
- `hf webhooks enable WEBHOOK_ID` — 启用一个被禁用的 webhook。`[--format [auto|human|agent|json|quiet]]`
- `hf webhooks info WEBHOOK_ID` — 显示单个 webhook 的详细信息。`[--format [auto|human|agent|json|quiet]]`
- `hf webhooks list` — 列出当前用户的所有 webhook。`[--format [auto|human|agent|json|quiet]]`
- `hf webhooks update WEBHOOK_ID` — 更新一个现有的 webhook。仅更改提供的选项。`[--url TEXT --watch TEXT --domain [repo|discussions] --secret TEXT --format [auto|human|agent|json|quiet]]`

## 常用选项

- `--format` — 输出格式：`--format json`（或 `--json`）或 `--format table`（默认）。
- `-q / --quiet` — 安静输出（每行一个 ID）。等同于 `--format quiet`。
- `--revision` — Git 修订版本 ID，可以是分支名、标签或提交哈希。
- `--token` — 使用用户访问令牌。优先设置 `HF_TOKEN` 环境变量，而不是传递 `--token`。
- `--type` — 仓库类型（模型、数据集、Space 或内核）。

## 将仓库挂载为本地文件系统

要将 Hub 仓库或存储桶挂载为本地文件系统——无需下载、无需复制、无需等待——请使用 `hf-mount`。文件按需获取。GitHub: https://github.com/huggingface/hf-mount

安装：`brew install hf-mount`，或从 https://github.com/huggingface/hf-mount/releases 下载二进制文件

一些命令示例：
- `hf-mount start repo openai-community/gpt2 /tmp/gpt2` — 挂载一个仓库（只读）
- `hf-mount start --hf-token $HF_TOKEN bucket myuser/my-bucket /tmp/data` — 挂载一个存储桶（读写）
- `hf-mount status` / `hf-mount stop /tmp/data` — 列出或卸载

## 小贴士

- 使用 `hf <command> --help` 获取完整选项、描述、用法和实际示例
- 使用 `HF_TOKEN` 环境变量（推荐）或 `--token` 进行身份验证
- 使用 `hf update` 更新 CLI（使用检测到的安装方法的正确命令）
