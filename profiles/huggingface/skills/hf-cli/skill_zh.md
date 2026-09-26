安装：`curl -LsSf https://hf.co/cli/install.sh | bash -s`。

Hugging Face Hub CLI 工具 `hf` 已可用。重要提示：`hf` 命令已取代已弃用的 `huggingface-cli` 命令。

使用 `hf --help` 查看可用功能。请注意，认证命令现在都在 `hf auth` 下，例如 `hf auth whoami`。

使用 `huggingface_hub v1.33.0` 生成。运行 `hf skills add --force` 重新生成。

## 命令

- `hf cp SRC` — 在本地路径、存储库和存储桶之间复制文件 `[--format [auto|human|agent|json|quiet]]`
- `hf download REPO_ID` — 从 Hub 下载文件 `[--type [model|dataset|space|kernel] --revision TEXT --include TEXT --exclude TEXT --cache-dir TEXT --local-dir TEXT --force-download --dry-run --max-workers INTEGER --format [auto|human|agent|json|quiet]]`
- `hf env` — 打印环境信息 `[--format [auto|human|agent|json|quiet]]`
- `hf sync` — 在本地目录和存储桶之间同步文件 `[--delete --ignore-times --ignore-sizes --plan TEXT --apply TEXT --dry-run --include TEXT --exclude TEXT --filter-from TEXT --existing --ignore-existing --verbose --format [auto|human|agent|json|quiet]]`
- `hf update` — 将 `hf` CLI 更新到最新版本 `[--format [auto|human|agent|json|quiet]]`
- `hf upload REPO_ID` — 将文件或文件夹上传到 Hub。推荐用于单提交上传 `[--type [model|dataset|space|kernel] --revision TEXT --private --include TEXT --exclude TEXT --delete TEXT --commit-message TEXT --commit-description TEXT --create-pr --every FLOAT --format [auto|human|agent|json|quiet]]`
- `hf upload-large-folder REPO_ID LOCAL_PATH` — [已弃用] 将大文件夹上传到 Hub。请使用 `hf upload` 代替 `[--type [model|dataset|space|kernel] --revision TEXT --private --include TEXT --exclude TEXT --num-workers INTEGER --no-report --no-bars --format [auto|human|agent|json|quiet]]`
- `hf version` — 打印有关 hf 版本的信息 `[--format [auto|human|agent|json|quiet]]`

### `hf auth` — 管理认证（登录、登出等）。

- `hf auth list` — 列出所有存储的访问令牌 `[--format [auto|human|agent|json|quiet]]`
- `hf auth login` — 从浏览器登录，或使用来自 huggingface.co/settings/tokens 的令牌 `[--add-to-git-credential --force --format [auto|human|agent|json|quiet]]`
- `hf auth logout` — 从特定令牌登出 `[--token-name TEXT --format [auto|human|agent|json|quiet]]`
- `hf auth switch` — 在访问令牌之间切换 `[--token-name TEXT --add-to-git-credential --format [auto|human|agent|json|quiet]]`
- `hf auth token` — 将当前访问令牌打印到标准输出 `[--format [auto|human|agent|json|quiet]]`
- `hf auth whoami` — 查找您登录的 huggingface.co 账户 `[--format [auto|human|agent|json|quiet]]`

### `hf buckets` — 与存储桶交互的命令。

- `hf buckets cp SRC` — 在本地路径、存储库和存储桶之间复制文件 `[--format [auto|human|agent|json|quiet]]`
- `hf buckets create BUCKET_ID` — 创建一个新的存储桶 `[--private --region [us|eu] --exist-ok --format [auto|human|agent|json|quiet]]`
- `hf buckets delete BUCKET_ID` — 删除存储桶 `[--yes --missing-ok --format [auto|human|agent|json|quiet]]`
- `hf buckets info BUCKET_ID` — 获取存储桶信息 `[--format [auto|human|agent|json|quiet]]`
- `hf buckets list` — 列出存储桶或存储桶中的文件 `[--human-readable --tree --recursive --search TEXT --format [auto|human|agent|json|quiet]]`
- `hf buckets move FROM_ID TO_ID` — 将存储桶移动到新的名称或命名空间（重命名） `[--format [auto|human|agent|json|quiet]]`
- `hf buckets remove ARGUMENT` — 从存储桶中删除文件 `[--recursive --yes --dry-run --include TEXT --exclude TEXT --format [auto|human|agent|json|quiet]]`
- `hf buckets settings BUCKET_ID` — 更新存储桶设置（可见性） `[--private --public --format [auto|human|agent|json|quiet]]`
- `hf buckets sync` — 在本地目录和存储桶之间同步文件 `[--delete --ignore-times --ignore-sizes --plan TEXT --apply TEXT --dry-run --include TEXT --exclude TEXT --filter-from TEXT --existing --ignore-existing --verbose --format [auto|human|agent|json|quiet]]`

### `hf cache` — 管理本地缓存目录。

- `hf cache list` — 列出缓存的存储库或修订版本 `[--cache-dir TEXT --revisions --filter TEXT --sort [accessed|accessed:asc|accessed:desc|modified|modified:asc|modified:desc|name|name:asc|name:desc|size|size:asc|size:desc] --limit INTEGER --show-warnings --format [auto|human|agent|json|quiet]]`
- `hf cache prune` — 从缓存中删除分离的修订版本和不完整的下载 `[--cache-dir TEXT --yes --dry-run --format [auto|human|agent|json|quiet]]`
- `hf cache rm TARGETS` — 删除缓存的存储库、修订版本或文件 `[--cache-dir TEXT --yes --dry-run --format [auto|human|agent|json|quiet]]`
- `hf cache verify REPO_ID` — 验证来自缓存或本地目录的单个存储库修订版本的校验和 `[--type [model|dataset|space|kernel] --revision TEXT --cache-dir TEXT --local-dir TEXT --fail-on-missing-files --fail-on-extra-files --format [auto|human|agent|json|quiet]]`

### `hf collections` — 与 Hub 上的集合交互。

- `hf collections add-item COLLECTION_SLUG ITEM_ID ITEM_TYPE` — 将项目添加到集合 `[--note TEXT --exists-ok --format [auto|human|agent|json|quiet]]`
- `hf collections create TITLE` — 在 Hub 上创建一个新的集合 `[--namespace TEXT --description TEXT --private --exists-ok --format [auto|human|agent|json|quiet]]`
- `hf collections delete COLLECTION_SLUG` — 从 Hub 删除集合 `[--missing-ok --format [auto|human|agent|json|quiet]]`
- `hf collections delete-item COLLECTION_SLUG ITEM_OBJECT_ID` — 从集合中删除项目 `[--missing-ok --format [auto|human|agent|json|quiet]]`
- `hf collections info COLLECTION_SLUG` — 获取 Hub 上集合的信息 `[--format [auto|human|agent|json|quiet]]`
- `hf collections list` — 列出 Hub 上的集合 `[--owner TEXT --item TEXT --sort [lastModified|trending|upvotes] --limit INTEGER --format [auto|human|agent|json|quiet]]`
- `hf collections update COLLECTION_SLUG` — 更新集合的元数据 `[--title TEXT --description TEXT --position INTEGER --private --theme TEXT --format [auto|human|agent|json|quiet]]`
- `hf collections update-item COLLECTION_SLUG ITEM_OBJECT_ID` — 更新集合中的项目 `[--note TEXT --position INTEGER --format [auto|human|agent|json|quiet]]`

### `hf datasets` — 与 Hub 上的数据集交互。

- `hf datasets card DATASET_ID` — 获取 Hub 上数据集的卡（README） `[--metadata --text --format [auto|human|agent|json|quiet]]`
- `hf datasets info DATASET_ID` — 获取 Hub 上数据集的信息 `[--revision TEXT --expand TEXT --format [auto|human|agent|json|quiet]]`
- `hf datasets leaderboard DATASET_ID` — 列出数据集排行榜中的模型分数。此命令有助于找到执行任务的最佳模型，或通过基准分数比较模型。使用 'hf datasets ls --filter benchmark:official' 列出可用的排行榜 `[--limit INTEGER --format [auto|human|agent|json|quiet]]`
- `hf datasets list` — 列出 Hub 上的数据集，或数据集存储库中的文件 `[--search TEXT --author TEXT --filter TEXT --sort [created_at|downloads|last_modified|likes|trending_score] --limit INTEGER --expand TEXT --human-readable --tree --recursive --revision TEXT --format [auto|human|agent|json|quiet]]`
- `hf datasets parquet DATASET_ID` — 列出可用于数据集的 parquet 文件 URL `[--subset TEXT --split TEXT --format [auto|human|agent|json|quiet]]`
- `hf datasets sql SQL` — 使用 DuckDB 对数据集 parquet URL 执行原始 SQL 查询 `[--format [auto|human|agent|json|quiet]]`

### `hf discussions` — 管理 Hub 上的讨论和拉取请求。

- `hf discussions close REPO_ID NUM` — 关闭讨论或拉取请求 `[--comment TEXT --yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions comment REPO_ID NUM` — 在讨论或拉取请求中评论 `[--body TEXT --body-file PATH --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions create REPO_ID --title TEXT` — 在存储库上创建新的讨论或拉取请求 `[--body TEXT --body-file PATH --pull-request --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions diff REPO_ID NUM` — 显示拉取请求的差异 `[--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions edit REPO_ID NUM COMMENT_ID` — 编辑讨论或拉取请求中的现有评论 `[--body TEXT --body-file PATH --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions info REPO_ID NUM` — 获取讨论或拉取请求的信息 `[--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions list REPO_ID` — 列出存储库上的讨论和拉取请求 `[--status [open|closed|merged|draft|all] --kind [all|discussion|pull_request] --author TEXT --limit INTEGER --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions merge REPO_ID NUM` — 合并拉取请求 `[--comment TEXT --yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions rename REPO_ID NUM NEW_TITLE` — 重命名讨论或拉取请求 `[--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf discussions reopen REPO_ID NUM` — 重新打开已关闭的讨论或拉取请求 `[--comment TEXT --yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`

### `hf endpoints` — 管理 Hugging Face Inference Endpoints。

- `hf endpoints catalog deploy --repo TEXT` — 从模型目录部署 Inference Endpoint `[--name TEXT --accelerator TEXT --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf endpoints catalog list` — 列出可用的目录模型 `[--format [auto|human|agent|json|quiet]]`
- `hf endpoints delete NAME` — 永久删除 Inference Endpoint `[--namespace TEXT --yes --format [auto|human|agent|json|quiet]]`
- `hf endpoints deploy NAME --repo TEXT --framework TEXT --accelerator TEXT --instance-size TEXT --instance-type TEXT --region TEXT --vendor TEXT` — 从 Hub 存储库部署 Inference Endpoint `[--namespace TEXT --task TEXT --min-replica INTEGER --max-replica INTEGER --scale-to-zero-timeout INTEGER --scaling-metric [pendingRequests|hardwareUsage] --scaling-threshold FLOAT --revision TEXT --custom-image TEXT --engine [custom|hf-serve|llamacpp|sglang|tei|tgi|tgi-neuron|vllm|vllm-neuron] --health-route TEXT --port INTEGER --container-registry-username TEXT --container-registry-password TEXT --tensor-parallel-size INTEGER --data-parallel-size INTEGER --container-command TEXT --container-args TEXT --env TEXT --env-file TEXT --secrets TEXT --secrets-file TEXT --type [public|protected|authenticated|private] --format [auto|human|agent|json|quiet]]`
- `hf endpoints describe NAME` — 获取现有端点的信息 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf endpoints hardware` — 列出可用于部署 Inference Endpoint 的硬件 `[--namespace TEXT --vendor TEXT --region TEXT --accelerator TEXT --instance-type TEXT --all --format [auto|human|agent|json|quiet]]`
- `hf endpoints list` — 列出给定命名空间的所有 Inference Endpoint `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf endpoints pause NAME` — 暂停 Inference Endpoint `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf endpoints resume NAME` — 恢复 Inference Endpoint `[--namespace TEXT --fail-if-already-running --format [auto|human|agent|json|quiet]]`
- `hf endpoints scale-to-zero NAME` — 将 Inference Endpoint 缩放为零 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf endpoints update NAME` — 更新现有端点 `[--namespace TEXT --repo TEXT --accelerator TEXT --instance-size TEXT --instance-type TEXT --framework TEXT --revision TEXT --task TEXT --custom-image TEXT --engine [custom|hf-serve|llamacpp|sglang|tei|tgi|tgi-neuron|vllm|vllm-neuron] --health-route TEXT --port INTEGER --tensor-parallel-size INTEGER --data-parallel-size INTEGER --container-command TEXT --container-args TEXT --min-replica INTEGER --max-replica INTEGER --scale-to-zero-timeout INTEGER --scaling-metric [pendingRequests|hardwareUsage] --scaling-threshold FLOAT --format [auto|human|agent|json|quiet]]`

### `hf extensions` — 管理 hf CLI 扩展。

- `hf extensions exec NAME` — 执行已安装的扩展。
- `hf extensions install REPO_ID` — 从公共 GitHub 存储库安装扩展 `[--force --format [auto|human|agent|json|quiet]]`
- `hf extensions list` — 列出已安装的扩展命令 `[--format [auto|human|agent|json|quiet]]`
- `hf extensions remove NAME` — 删除已安装的扩展 `[--format [auto|human|agent|json|quiet]]`
- `hf extensions search` — 搜索 GitHub 上可用的扩展（标记为 'hf-extension' 主题） `[--format [auto|human|agent|json|quiet]]`
- `hf extensions update` — 将已安装的扩展更新到最新版本 `[--format [auto|human|agent|json|quiet]]`

### `hf jobs` — 在 Hub 上运行和管理 Jobs。

- `hf jobs cancel JOB_ID` — 取消 Job `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs hardware` — 列出 Jobs 可用的硬件选项 `[--format [auto|human|agent|json|quiet]]`
- `hf jobs inspect JOB_IDS` — 显示一个或多个 Jobs 的详细信息 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs labels JOB_ID` — 更新 Job 上的标签。传递 `--label` 将替换所有现有标签；仅传递 `--name` 将保留它们 `[--name TEXT --label TEXT --clear --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs list` — 列出 Jobs `[--all --status [COMPLETED|CANCELED|ERROR|DELETED|SCHEDULING|RUNNING] --label TEXT --name TEXT --limit INTEGER --namespace TEXT --filter TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs logs JOB_ID` — 获取 Job 的日志 `[--follow --tail INTEGER --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs run IMAGE COMMAND` — 运行 Job `[--env TEXT --secrets TEXT --name TEXT --label TEXT --volume TEXT --env-file TEXT --secrets-file TEXT --flavor [cpu-basic|cpu-upgrade|cpu-performance|cpu-xl|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --timeout TEXT --detach --dry-run --expose INTEGER --ssh --network-group TEXT --network-alias TEXT --resource-group-id TEXT --namespace TEXT --format [agent|auto|human|agent|json|quiet] --json --quiet]`
- `hf jobs scheduled delete SCHEDULED_JOB_ID` — 删除计划的 Job `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled inspect SCHEDULED_JOB_IDS` — 显示一个或多个计划 Jobs 的详细信息 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled labels SCHEDULED_JOB_ID` — 更新计划 Job 上的标签。传递 `--label` 将替换所有现有标签；仅传递 `--name` 将保留它们 `[--name TEXT --label TEXT --clear --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled list` — 列出计划 Jobs `[--all --status [active|suspended] --label TEXT --name TEXT --namespace TEXT --filter TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled resume SCHEDULED_JOB_ID` — 恢复（取消暂停）计划 Job `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled run SCHEDULE IMAGE COMMAND` — 安排 Job `[--suspend --concurrency --env TEXT --secrets TEXT --name TEXT --label TEXT --volume TEXT --env-file TEXT --secrets-file TEXT --timeout TEXT --dry-run --expose INTEGER --resource-group-id TEXT --namespace TEXT --format [agent|auto|human|agent|json|quiet] --json --quiet]`
- `hf jobs scheduled suspend SCHEDULED_JOB_ID` — 暂停（暂停）计划 Job `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled trigger SCHEDULED_JOB_ID` — 立即触发计划 Job 运行（不会更改计划） `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs scheduled uv run SCHEDULE SCRIPT` — 在 HF 基础设施上运行 UV 脚本（本地文件或 URL） `[--suspend --concurrency --image TEXT --flavor [cpu-basic|cpu-upgrade|cpu-performance|cpu-xl|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --env TEXT --secrets TEXT --name TEXT --label TEXT --volume TEXT --env-file TEXT --secrets-file TEXT --timeout TEXT --detach --dry-run --expose INTEGER --ssh --network-group TEXT --network-alias TEXT --resource-group-id TEXT --namespace TEXT --with TEXT --python TEXT --format [agent|auto|human|agent|json|quiet] --json --quiet]`
- `hf jobs ssh JOB_ID` — SSH 到正在运行的 Job 中 `[--identity-file PATH --dry-run --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs stats` — 获取 Jobs 的资源使用统计和指标 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf jobs uv run SCRIPT` — 在 HF 基础设施上运行 UV 脚本（本地文件或 URL） `[--image TEXT --flavor [cpu-basic|cpu-upgrade|cpu-performance|cpu-xl|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --env TEXT --secrets TEXT --name TEXT --label TEXT --volume TEXT --env-file TEXT --secrets-file TEXT --timeout TEXT --detach --dry-run --expose INTEGER --ssh --network-group TEXT --network-alias TEXT --resource-group-id TEXT --namespace TEXT --with TEXT --python TEXT --format [agent|auto|human|agent|json|quiet] --json --quiet]`
- `hf jobs wait JOB_IDS` — 等待一个或多个 Jobs 达到终端状态 `[--timeout TEXT --namespace TEXT --format [auto|human|agent|json|quiet]]`

### `hf models` — 与 Hub 上的模型交互。

- `hf models card MODEL_ID` — 获取 Hub 上模型的卡（README） `[--metadata --text --format [auto|human|agent|json|quiet]]`
- `hf models info MODEL_ID` — 获取 Hub 上模型的信息 `[--revision TEXT --expand TEXT --format [auto|human|agent|json|quiet]]`
- `hf models list` — 列出 Hub 上的模型，或模型存储库中的文件 `[--search TEXT --author TEXT --filter TEXT --pipeline-tag TEXT --gated --apps TEXT --num-parameters TEXT --inference-provider [baseten|cerebras|cohere|deepinfra|fal-ai|featherless-ai|fireworks-ai|groq|hf-inference|novita|nscale|openai|ovhcloud|publicai|replicate|scaleway|together|wavespeed|zai-org] --warm --sort [created_at|downloads|last_modified|likes|trending_score] --limit INTEGER --expand TEXT --human-readable --tree --recursive --revision TEXT --format [auto|human|agent|json|quiet]]`

### `hf papers` — 与 Hub 上的论文交互。

- `hf papers info PAPER_ID` — 获取 Hub 上论文的信息 `[--format [auto|human|agent|json|quiet]]`
- `hf papers list` — 列出 Hub 上的每日论文 `[--date TEXT --week TEXT --month TEXT --submitter TEXT --sort [publishedAt|trending] --limit INTEGER --format [auto|human|agent|json|quiet]]`
- `hf papers read PAPER_ID` — 以 markdown 格式阅读论文 `[--format [auto|human|agent|json|quiet]]`
- `hf papers search QUERY` — 在 Hub 上搜索论文 `[--limit INTEGER --format [auto|human|agent|json|quiet]]`

### `hf repos` — 管理 Hub 上的存储库。

- `hf repos branch create REPO_ID BRANCH` — 为存储库在 Hub 上创建一个新的分支 `[--revision TEXT --type [model|dataset|space|kernel] --exist-ok --format [auto|human|agent|json|quiet]]`
- `hf repos branch delete REPO_ID BRANCH` — 从 Hub 上删除分支 `[--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf repos cp SRC` — 在本地路径、存储库和存储桶之间复制文件 `[--format [auto|human|agent|json|quiet]]`
- `hf repos create REPO_ID` — 在 Hub 上创建一个新的存储库 `[--type [model|dataset|space|kernel] --sdk TEXT --template TEXT --private --public --protected --exist-ok --resource-group-id TEXT --region [us|eu] --flavor [cpu-basic|cpu-upgrade|zero-a10g|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8] --storage [small|medium|large] --sleep-time INTEGER --secrets TEXT --secrets-file TEXT --env TEXT --env-file TEXT --volume TEXT --format [auto|human|agent|json|quiet]]`
- `hf repos delete REPO_ID` — 从 Hub 上删除存储库。这是一个不可逆的操作。 `[--type [model|dataset|space|kernel] --missing-ok --yes --format [auto|human|agent|json|quiet]]`
- `hf repos delete-files REPO_ID PATTERNS` — 从 Hub 上删除存储库中的文件 `[--type [model|dataset|space|kernel] --revision TEXT --commit-message TEXT --commit-description TEXT --create-pr --format [auto|human|agent|json|quiet]]`
- `hf repos duplicate FROM_ID` — 在 Hub 上复制存储库（模型、数据集或 Space）。 `[--type [model|dataset|space|kernel] --private --public --protected --exist-ok --flavor [cpu-basic|cpu-upgrade|zero-a10g|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8] --storage [small|medium|large] --sleep-time INTEGER --secrets TEXT --secrets-file TEXT --env TEXT --env-file TEXT --volume TEXT --format [auto|human|agent|json|quiet]]`
- `hf repos list` — 列出所有存储库（模型、数据集、空间、存储桶）及其存储信息 `[--namespace TEXT --type [model|dataset|space|bucket] --search TEXT --limit INTEGER --explore --format [auto|human|agent|json|quiet]]`
- `hf repos move FROM_ID TO_ID` — 将存储库从一个命名空间移动到另一个命名空间 `[--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf repos settings REPO_ID` — 更新存储库的设置 `[--gated [auto|manual|false] --private --public --protected --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf repos tag create REPO_ID TAG` — 为存储库创建标签 `[--message TEXT --revision TEXT --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf repos tag delete REPO_ID TAG` — 删除存储库的标签 `[--yes --type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`
- `hf repos tag list REPO_ID` — 列出存储库的标签 `[--type [model|dataset|space|kernel] --format [auto|human|agent|json|quiet]]`

### `hf sandbox` — 在 Hugging Face Jobs 上运行和管理实验性沙盒。

- `hf sandbox cp SRC DST` — 在本地机器和沙盒（docker 风格）之间复制文件 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox create` — 创建沙盒：默认情况下为专用虚拟机，或使用 `--pool` 创建廉价的共享沙盒 `[--pool TEXT --flavor [cpu-basic|cpu-upgrade|cpu-performance|cpu-xl|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --idle-timeout TEXT --env TEXT --secrets TEXT --label TEXT --env-file TEXT --secrets-file TEXT --volume TEXT --namespace TEXT --forward-hf-token --format [auto|human|agent|json|quiet]]`
- `hf sandbox exec SANDBOX_ID COMMAND` — 在沙盒中运行命令，并流式传输输出。以命令的退出代码退出 `[--workdir TEXT --env TEXT --env-file TEXT --timeout FLOAT --namespace TEXT]`
- `hf sandbox kill` — 终止沙盒、整个共享主机或所有内容（`--all`）。 `[--all --yes --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox pool create` — 热身池：立即启动一个主机 VM，以便稍后通过其池 ID 找到 `[--flavor [cpu-basic|cpu-upgrade|cpu-performance|cpu-xl|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8|h200|h200x2|h200x4|h200x8|rtx-pro-6000|rtx-pro-6000x2|rtx-pro-6000x4|rtx-pro-6000x8] --per-host INTEGER RANGE --max-hosts INTEGER RANGE --idle-timeout TEXT --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox pool delete POOL_ID` — 终止池中的每个主机 VM（因此所有其沙盒）。 `[--yes --namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox pool ls` — 列出正在运行的沙盒池（按其主机 VM 分组）。 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox process kill SANDBOX_ID PID` — 停止沙盒中运行的背景进程。 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox process ls SANDBOX_ID` — 列出沙盒中运行的背景进程（使用 `hf sandbox spawn` 启动）。 `[--namespace TEXT --format [auto|human|agent|json|quiet]]`
- `hf sandbox spawn SANDBOX_ID COMMAND` — 在后台启动长时间运行的命令，并返回其 pid（不等待）。 `[--workdir TEXT --env TEXT --env-file TEXT --namespace TEXT]`

### `hf skills` — 管理 AI 助手技能。

- `hf skills add` — 为 AI 助手安装 Hugging Face 技能 `[--claude --global --dest PATH --force --format [auto|human|agent|json|quiet]]`
- `hf skills list` — 列出 Hugging Face 市场上的可用技能 `[--format [auto|human|agent|json|quiet]]`
- `hf skills preview` — 将生成的 `hf-cli` SKILL.md 打印到标准输出 `[--format [auto|human|agent|json|quiet]]`
- `hf skills update` — 更新已安装的 Hugging Face 市场技能 `[--claude --global --dest PATH --format [auto|human|agent|json|quiet]]`

### `hf spaces` — 与 Hub 上的空间交互。

- `hf spaces card SPACE_ID` — 获取 Hub 上空间的卡（README） `[--metadata --text --format [auto|human|agent|json|quiet]]`
- `hf spaces dev-mode SPACE_ID` — 启用或禁用空间上的 dev 模式 `[--stop --format [auto|human|agent|json|quiet]]`
- `hf spaces hardware` — 列出空间的可用硬件选项 `[--format [auto|human|agent|json|quiet]]`
- `hf spaces hot-reload SPACE_ID` — 无需完整重建和重启即可热重载空间的任何 Python 文件 `[--local-file PATH --skip-checks --skip-summary --format [auto|human|agent|json|quiet]]`
- `hf spaces info SPACE_ID` — 获取 Hub 上空间的信息 `[--revision TEXT --expand TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces list` — 列出 Hub 上的空间，或空间存储库中的文件 `[--search TEXT --author TEXT --filter TEXT --sort [created_at|last_modified|likes|trending_score] --limit INTEGER --expand TEXT --human-readable --tree --recursive --revision TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces logs SPACE_ID` — 获取空间的运行或构建日志 `[--build --follow --tail INTEGER --format [auto|human|agent|json|quiet]]`
- `hf spaces pause SPACE_ID` — 暂停空间 `[--format [auto|human|agent|json|quiet]]`
- `hf spaces restart SPACE_ID` — 重新启动空间 `[--factory-reboot --format [auto|human|agent|json|quiet]]`
- `hf spaces search QUERY` — 使用语义搜索在 Hub 上搜索空间 `[--filter TEXT --sdk TEXT --include-non-running --description --limit INTEGER --format [auto|human|agent|json|quiet]]`
- `hf spaces secrets add SPACE_ID` — 为空间添加或更新密钥 `[--secrets TEXT --secrets-file TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces secrets delete SPACE_ID KEY` — 从空间中删除密钥 `[--yes --format [auto|human|agent|json|quiet]]`
- `hf spaces secrets list SPACE_ID` — 列出空间的密钥。密钥值是只写入的，不会返回。 `[--format [auto|human|agent|json|quiet]]`
- `hf spaces settings SPACE_ID` — 更新空间的设置 `[--sleep-time INTEGER --hardware [cpu-basic|cpu-upgrade|zero-a10g|t4-small|t4-medium|l4x1|l4x4|l40sx1|l40sx4|l40sx8|a10g-small|a10g-large|a10g-largex2|a10g-largex4|a100-large|a100x4|a100x8] --format [auto|human|agent|json|quiet]]`
- `hf spaces ssh SPACE_ID` — SSH 到空间的 Dev 模式容器中 `[--identity-file PATH --dry-run --auto --format [auto|human|agent|json|quiet]]`
- `hf spaces templates` — 列出可用的空间模板 `[--format [auto|human|agent|json|quiet]]`
- `hf spaces variables add SPACE_ID` — 为空间添加或更新环境变量 `[--env TEXT --env-file TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces variables delete SPACE_ID KEY` — 从空间中删除环境变量 `[--yes --format [auto|human|agent|json|quiet]]`
- `hf spaces variables list SPACE_ID` — 列出空间的环境变量 `[--format [auto|human|agent|json|quiet]]`
- `hf spaces volumes delete SPACE_ID` — 从空间中删除所有卷 `[--yes --format [auto|human|agent|json|quiet]]`
- `hf spaces volumes list SPACE_ID` — 列出空间中挂载的卷 `[--format [auto|human|agent|json|quiet]]`
- `hf spaces volumes set SPACE_ID` — 为空间设置（替换）卷 `[--volume TEXT --format [auto|human|agent|json|quiet]]`
- `hf spaces wait SPACE_ID` — 等待空间完成构建/启动 `[--timeout TEXT --format [auto|human|agent|json|quiet]]`

### `hf webhooks` — 管理 Hub 上的 webhooks。

- `hf webhooks create --watch TEXT` — 创建新的 webhook。 `[--url TEXT --job-id TEXT --domain [repo|discussions] --secret TEXT --format [auto|human|agent|json|quiet]]`
- `hf webhooks delete WEBHOOK_ID` — 永久删除 webhook `[--yes --format [auto|human|agent|json|quiet]]`
- `hf webhooks disable WEBHOOK_ID` — 禁用活动的 webhook `[--format [auto|human|agent|json|quiet]]`
- `hf webhooks enable WEBHOOK_ID` — 启用已禁用的 webhook `[--format [auto|human|agent|json|quiet]]`
- `hf webhooks info WEBHOOK_ID` — 显示单个 webhook 的完整详细信息 `[--format [auto|human|agent|json|quiet]]`
- `hf webhooks list` — 列出当前用户的所有 webhooks `[--format [auto|human|agent|json|quiet]]`
- `hf webhooks update WEBHOOK_ID` — 更新现有的 webhook。仅更改提供的选项。 `[--url TEXT --watch TEXT --domain [repo|discussions] --secret TEXT --format [auto|human|agent|json|quiet]]`

## 常用选项

- `--format` — 输出格式：`--format json`（或 `--json`）或 `--format table`（默认）。
- `-q / --quiet` — 静默输出（每行一个 ID）。等同于 '--format quiet'。
- `--revision` — Git 修订 ID，可以是分支名、标签或提交哈希。
- `--token` — 使用用户访问令牌。建议设置 `HF_TOKEN` 环境变量而不是传递 `--token`。
- `--type` — 存储库的类型（模型、数据集、空间或内核）。

## 将存储库挂载为本地文件系统

要将 Hub 存储库或存储桶挂载为本地文件系统——无需下载、无需复制、无需等待——使用 `hf-mount`。文件按需获取。GitHub：https://github.com/huggingface/hf-mount

安装：`brew install hf-mount`，或从 https://github.com/huggingface/hf-mount/releases 下载二进制文件

一些命令示例：

- `hf-mount start repo openai-community/gpt2 /tmp/gpt2` — 挂载一个存储库（只读）
- `hf-mount start --hf-token $HF_TOKEN bucket myuser/my-bucket /tmp/data` — 挂载一个存储桶（读写）
- `hf-mount status` / `hf-mount stop /tmp/data` — 列出或卸载

## 小贴士

- 使用 `hf <command> --help` 获取完整选项、描述、用法和实际示例
- 使用 `HF_TOKEN` 环境变量进行认证（推荐）或使用 `--token`
- 使用 `hf update` 更新 CLI（使用检测到的安装方法正确的命令）
