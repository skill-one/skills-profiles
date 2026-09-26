# Brev — TAO执行粘合剂

> **独立安装？** 如果此会话不是由TAO技能库插件初始化的，请先运行`tao-setup`技能（主机预检、凭证、跨技能发现）。

NVIDIA Brev提供按需GPU实例（预装NVIDIA驱动程序、CUDA、Docker和NVIDIA容器工具包）。Brev是**基于实例的**：您创建一个实例，通过`brev exec`在其上运行命令，完成后删除它。

这个技能是故意设计得比较薄的。**实例的创建和管理——创建、按GPU/价格搜索、启动/停止、删除、登录——由NVIDIA Brev自己的代理技能负责，这里不重复。** 这个技能只涵盖TAO特定的部分：通过**四动词docker合约**在达到的实例上运行TAO容器，将容器如何通过`tao-run-on-docker`委托给`brev exec`。

## 创建实例：使用官方Brev技能或MCP

NVIDIA Brev发布一个管理实例的代理技能，使用自然语言（“创建一个A100实例”、“搜索价格低于3美元/小时的GPU”、“停止所有我的实例”）。安装一次——它会自我注册到您的代理技能目录中，并在运行时被发现的：

```bash
curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/scripts/install-agent-skill.sh | bash
# 安装到 ~/.claude/skills/brev-cli/ , ~/.codex/skills/brev-cli/ , ~/.agents/skills/brev-cli/
```

或者连接**Brev MCP服务器**（`https://docs.nvidia.com/brev/_mcp/server`）。两者都负责登录/认证的细节、放置ID、GPU搜索和拆除标志。它**不包括**在实例上执行容器——那是这个技能。

**此技能的预检**：`brev` CLI在`PATH`上并且已经登录（无头：`brev login --token "$BREV_API_TOKEN"`在任何其他调用之前），并且您可以到达目标实例——用**两个词**的命令轮询，直到它成功后再发出实际工作（新实例在sshd启动之前报告`RUNNING`）：

```bash
for i in $(seq 1 60); do brev exec <instance> "echo ok" 2>/dev/null | grep -qx ok && break; sleep 5; done
brev exec <instance> "echo ok" 2>/dev/null | grep -qx ok || { echo "实例未准备好执行"; exit 1; }
```

探测必须是**两个词，作为单个参数引用**。单个令牌的探测（`brev exec <instance> -- true`）即使所有实际命令都损坏也会通过，因为`brev exec [instance...] <command>`只将最后一个位置参数视为命令——所以一个孤独的`true`偶然地落在了正确的位置，而`docker run ...`则没有。见下文*`brev exec`参数形式*。

允许**≥ 600秒**用于新实例上的第一个`brev exec`（SSH启动+第一个容器拉取）；60-120秒的包装超时会截断启动，看起来像是一个意外的`exec failed`。

## 存储

没有共享的NFS/Lustre——存储层**B/C**通过`tao-data-io`：将输入从S3阶段到实例的本地磁盘（或在容器内获取），并在删除实例**之前**将结果上传到S3。实例本地`~/`在停止/启动之间持久化，但在删除/创建之间**不**持久化，所以结果上传必须先于拆除。

## 执行——四动词（Docker的组合）

Brev是一个**组合消费者**：`submit`到达一个实例，然后**将容器如何委托给四动词docker**（`tao-run-on-docker`）在`brev exec`上运行。它不是一个对称的伙伴——拆除必须额外删除实例以停止计费。`$BANK` = `${TAO_SKILL_BANK_PATH}`。

- **submit** — 到达一个实例（通过官方Brev技能或MCP创建/重用；通过`instance_id`重用现有实例；等待就绪，如上所述）。检查组装的命令，在启动**之前**打开记录以铸造`$JOB_ID`，然后在实例内部运行docker的`submit`动词并标记为RUNNING：

  ```bash
  redact_secrets.py lint <<<"$REMOTE_CMD"     # 没有内联密钥；凭证作为 -e VAR
  JOB_ID=$("$BANK/scripts/tao_job_record.py" open \
    --platform brev --image "$IMG" \
    --network-arch "$ARCH" --action "$ACTION" \
    --storage-tier "$TIER" --results-root "$RESULTS_ROOT")
  brev exec <instance> "docker inspect '$JOB_ID' >/dev/null 2>&1 && { echo '$JOB_ID已经提交'; exit 0; }; docker run -d --name '$JOB_ID' --label 'tao-job=$JOB_ID' ..."
  "$BANK/scripts/tao_job_record.py" mark "$JOB_ID" --state RUNNING \
    --backend-ref "<instance>/$JOB_ID"       # 实例是引用的一部分：没有它容器是不可达的
  ```
- **status / logs** — `brev exec <instance> "docker inspect $JOB_ID"` /
  `brev exec <instance> "docker logs $JOB_ID"`，与docker动词完全相同的词汇映射。从记录的`backend-ref`中恢复`<instance>`。
- **cancel / teardown** — 删除容器，然后对于临时实例删除它（停止计费），然后标记记录。永远不要让临时实例运行：

  ```bash
  brev exec <instance> "docker rm -f $JOB_ID"
  brev delete <instance>                      # 只有临时实例
  "$BANK/scripts/tao_job_record.py" mark "$JOB_ID" --state CANCELED --source agent
  ```

### `brev exec`参数形式

远程命令是**一个参数**。CLI签名是`brev exec [instance...] <command>`：除了最后一个位置参数之外，每个位置参数都是一个实例名称，`--`只结束标志解析——它不会组合它后面的单词。所以`brev exec <inst> -- docker inspect "$JOB_ID"`被读取为实例`<inst> docker inspect`加上命令`"$JOB_ID"`，并失败，显示`could not look up instance "docker"` / `ssh: illegal option -- -`（退出码255）——一个读起来像实例或SSH故障的错误，但实际上是一个语法错误。将每个远程命令引用为单个字符串，与`brev exec --help`显示的完全一样。

NGC认证一次每个实例——**永远不要在argv中放置`NGC_KEY`**（它会落在远程进程表中）；将其管道到`--password-stdin`：

```bash
IMG=nvcr.io/nvidia/tao/tao-toolkit:7.2.0-pyt  # 版本键：images.tao_toolkit.pyt

# NGC认证（每个实例一次）——值永远不会在argv中。
# 单引号本地使用，以便`$NGC_KEY`在实例的shell中展开；首先在那里导出它（或者从本地shell管道进去，如果实例没有副本）。
brev exec <instance> 'printf %s "$NGC_KEY" | docker login nvcr.io -u "$oauthtoken" --password-stdin'

# 验证认证而不读取~/.docker/config.json。在成功登录之前失败 = 未认证；成功登录之后失败 = 该密钥的组织没有授权。
brev exec <instance> "docker manifest inspect $IMG >/dev/null && echo AUTH_OK || echo AUTH_FAIL"

# 在GPU运行之前拉取。`docker run`会隐式拉取，但实例在启动时计费，所以一个GB级的首次TAO拉取会计费GPU空闲时间。
# 作为自己的步骤拉取也将拉取失败（认证/授权）与训练失败在日志中分离。
brev exec <instance> "docker image inspect $IMG >/dev/null 2>&1 || docker pull $IMG"

# 运行一个TAO作业（docker的`submit`动词，通过brev exec）
brev exec <instance> "docker inspect '$JOB_ID' >/dev/null 2>&1 && { echo '$JOB_ID已经提交'; exit 0; }; docker run -d --name '$JOB_ID' --label 'tao-job=$JOB_ID' --gpus all -v ~/data:/data -e NGC_KEY '$IMG' visual_changenet train -e /data/spec.yaml"
```

## 多GPU和多节点

**多节点在Brev上不受支持**——基于实例，没有跨实例协调。单个实例上的多GPU**支持**（最多8× H100 / A100 / L40S）；`torchrun --nproc-per-node=N`或PyTorch DDP在实例内部工作。
