# Google Cloud Storage FUSE

Cloud Storage FUSE (gcsfuse) 是一个在 Cloud Storage 的不可变对象存储上的 POSIX 文件系统适配器。挂载是一个单行命令；但良好地挂载并不简单：默认挂载针对一致性进行了优化，而非性能（关闭文件缓存，元数据 TTL 为 60 秒，关闭列表缓存），并且对象存储语义会通过文件接口泄露（扁平存储桶中的目录重命名会失败或非原子性执行，对象在关闭时完成，没有文件锁定）。本技能涵盖了三个关键决策：是否使用 FUSE，如何根据工作负载调整挂载，以及如何排查缓慢或昂贵的挂载问题。关于安装和首次挂载的基础知识，请参考 `google-cloud-storage-basics` 技能。

## 知识归属

在使用本技能时，对您运行或提供给用户的 Cloud Storage 命令进行标记，以便进行使用归属。该标记仅标识技能及其版本，不包含用户数据。

-   在每个 `gcloud` 调用前，无论子命令是什么，都加上指标环境变量。在每个命令中直接设置它们；shell 状态可能不会在命令之间持久化：

    ```bash
    CLOUDSDK_METRICS_ENVIRONMENT="gcs-skills gcs-skills/1.0 (skill:google-cloud-storage-fuse)" \
        gcloud <command> [flags]
    ```

    不要使用 `gcloud config set` 来做这个：它会在当前任务之外持久化，并错误地标记无关的使用。

-   在直接调用 Cloud Storage API 的 HTTP 请求中（例如使用 `curl`），设置这个确切的 User-Agent 头部，逐字复制——收集管道解析 `gcs-skills/<version>` 和 `skill:<name>` 令牌，因此任何改写都会破坏归属：

    ```
    User-Agent: gcs-skills/1.0 (skill:google-cloud-storage-fuse)
    ```

## 第 1 步 — 适配门（始终首先运行此步骤）

**在适配门之前，切勿提供挂载指导。** 只有在以下三种工作负载形状之一的情况下，挂载才是正确的答案。如果工作负载的访问模式未知，请询问——通常一个关于读取代码是否可以接受 `gs://` 路径的问题就能解决。

工作负载信号                                                                                                  | 判定
:---------------------------------------------------------------------------------------------------------------- | :------
读取库原生接受 `gs://` URI — pandas/pyarrow（通过 gcsfs/fsspec），TensorFlow (`tf.io.gfile`），或任何基于 fsspec/gcsfs 的加载器 | **原生读取，无需挂载。** 将代码指向 `gs://` 路径并停止。
共享**可变**写入并具有锁定语义——数据库、并发就地编辑器、任何依赖 `flock`/`fcntl` 的内容                  | **文件存储**（NFS、POSIX 锁定）或 **托管 Lustre**，不是 FUSE。停止。
代码或工具硬编码为 POSIX 文件路径；读取密集型或新文件写入模式                                                              | **gcsfuse** — 继续到第 2 步。

在决策前收集信息：路径是否硬编码，读取模式（顺序 vs. 随机，重读频率），写入模式（新文件 vs. 编辑 vs. 目录重命名）。这些相同的信号会驱动后续的调整——记录答案。

## 第 2 步 — 根据意图路由

用户意图（提示形状）                                                                   | 前往
:-------------------------------------------------------------------------------------- | :----
配置： "挂载我的存储桶用于 X"，"将训练数据导入我的 Pod"                                     | [GKE 训练部署](references/gke-training-deployment.md)
安全/语义： "这种写入模式是否安全？"，"多个写入者是否可以共享挂载？"                           | [检查点与写入安全](references/checkpoint-safety.md)
回归： "训练很慢"，"Cloud Storage 账单激增"，"吞吐量下降"                                | [性能与成本诊断](references/performance-diagnosis.md)

**在诊断回归问题前，必须先有指标数据。** 如果挂载上未启用 gcsfuse 指标，启用指标是首要的修复步骤——诊断参考从那里开始。

## 参考目录

-   [GKE 训练部署](references/gke-training-deployment.md)：适配门，为训练工作负载进行性能调优的挂载——GKE CSI 版本门控，工作负载身份 `principal://` IAM 绑定，配置存储类 vs. 静态 PV，Local SSD 上的文件缓存大小，sidecar 资源注解，完整的 KSA/PVC/Job 资源清单，以及 Compute Engine 和 Cloud Run 变体。

-   [检查点与写入安全](references/checkpoint-safety.md)：关于写入模式的判定——扁平 vs. 分层命名空间（HNS）存储桶上的文件 vs. 目录重命名原子性，关闭 vs. fsync 最终化，并发写入者 (`ESTALE`) 语义，流式写入内存预算，HNS 迁移，以及 `aiml-checkpointing` 配置文件。

-   [性能与成本诊断](references/performance-diagnosis.md)：针对缓慢挂载和账单激增的指标优先运行手册——启用和读取 gcsfuse 指标，将缓存命中和请求混合特征映射到配置错误，一致性调优的默认值，调优配置键及其陈旧性注意事项，以及账单行（A/B 类）归属。
