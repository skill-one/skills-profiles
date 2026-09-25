# 华为云 OBS 统计技能

## 概述

查询华为云 OBS（对象存储服务）统计信息：列出具有容量和对象计数的存储桶，查询外网/内网下载流量并进行月环比，查询总请求数并进行月环比。

## ⛔ 禁止操作（安全约束）

> **本技能严格禁止以下删除操作，无论用户请求如何：**

| 禁止操作 | API/命令 | 原因 |
|---------|---------|------|
| ❌ 删除存储桶 | `DeleteBucket` / `obsutil rm -bucket` | 不可逆；将删除整个存储桶及其所有对象 |
| ❌ 删除对象 | `DeleteObject` / `obsutil rm` | 不可逆；删除的对象无法恢复（除非已开启版本控制） |
| ❌ 批量删除对象 | `DeleteObjects` / `obsutil rm -r` | 不可逆；批量删除影响范围广 |
| ❌ 清空存储桶 | `obsutil rm -bucket -r` | 不可逆；删除存储桶中的所有对象 |

> **如果用户请求删除操作，你必须拒绝并告知：**
> "根据安全约束，本技能不允许删除操作（删除存储桶/对象/批量删除/清空存储桶）。请使用华为云 OBS 控制台或手动使用 obsutil。"

## 架构

```
华为云 OBS 统计
├── ListBucketsWithStats  (列出具有容量和对象计数的存储桶)
├── GetTraffic           (查询外网/内网下载流量并进行月环比)
└── GetRequests           (查询总请求数并进行月环比)
```

## 前置条件

> **前置条件检查：华为云 CLI (hcloud / KooCLI) >= 3.2.0 必须安装**
> 运行 `hcloud version` 以验证版本 >= 3.2.0。如果未安装或版本过低，
> 请参考 [references/cli-installation-guide.md](references/cli-installation-guide.md) 获取安装指南。

```bash
hcloud version
```

> **前置条件检查：obsutil >= 5.5.0 必须安装（用于 OBS 存储桶列表）**
> hcloud OBS 模块使用底层 obsutil。存储桶列表需要 obsutil 命令行工具。
> 运行 `obsutil version` 以验证版本 >= 5.5.0。如果未安装，
> 请参考 [references/cli-installation-guide.md](references/cli-installation-guide.md) 获取安装指南。

```bash
obsutil version
```

> **前置条件检查：obsutil 凭证配置必须完成**
>
> hcloud OBS 模块使用底层 obsutil，该模块需要单独的 AK/SK 和 Endpoint 配置。
> 在执行 OBS 操作之前，**你必须检查 obsutil 凭证是否已配置**：
>
> ```bash
> hcloud obs ls -limit=1
> ```
>
> **如果响应为 `Please set ak, sk and endpoint in the configuration file!` 或 `InvalidAccessKeyId`，则 obsutil 凭证未配置。**
>
> **解决方法：提供以下示例命令，并让用户在终端中配置（不要在对话中要求用户提供 AK/SK）：**
>
> ```
> obsutil 凭证未配置。请在终端中运行以下命令进行配置（AK/SK 可从华为云控制台 "我的凭证" 页面获取）：
>
>   hcloud obs config -i=<YourAK> -k=<YourSK> -e=obs.<Region>.myhuaweicloud.com
>
> 示例（广州区域）：
>   hcloud obs config -i=<YourAK> -k=<YourSK> -e=obs.cn-south-1.myhuaweicloud.com
>
> 常用 Endpoint：
>   cn-north-4  → obs.cn-north-4.myhuaweicloud.com
>   cn-east-3   → obs.cn-east-3.myhuaweicloud.com
>   cn-south-1  → obs.cn-south-1.myhuaweicloud.com
>   cn-southwest-2 → obs.cn-southwest-2.myhuaweicloud.com
>
> 配置完成后重新尝试。
> ```
>
> **禁止行为：**
> - ❌ 不要在对话中要求用户提供 AK/SK
> - ❌ 不要从 hcloud 配置文件中提取 AK/SK（凭证是加密的，不能直接使用）
> - ❌ 不要在执行 OBS 操作前跳过凭证检查

> **⚠️ hcloud 参数格式要求**
>
> hcloud (KooCLI) **所有参数必须使用 `--param=value` 格式**（使用等号连接）；空格分隔格式不受支持。
>
> ✅ 正确：`hcloud OBS ListBuckets --region=cn-south-1`
>
> ❌ 错误：`hcloud OBS ListBuckets --region cn-south-1`

**[条件] CLI User-Agent** — `hcloud` OBS 模块命令可能包含 User-Agent 头，但 **CES 模块不支持此参数**：
- ✅ OBS 模块：`hcloud obs ls`
- ❌ CES 模块：`hcloud CES ShowMetricData` **不支持** `--User-Agent`；添加它会导致 "Invalid parameter: User-Agent"

---

## 身份验证

> **前置条件检查：华为云凭证必须完成**

> **安全规则（必须遵守）：**
> - **禁止**读取、回显或打印 AK/SK 值
> - **禁止**在对话中要求用户直接输入 AK/SK
> - **禁止**使用 `hcloud configure set` 传递明文凭证值
> - **禁止**直接接受对话中用户提供的 AK/SK
> - **仅允许**从环境变量或配置的 CLI 配置文件中读取凭证
>
> **⚠️ 重要：处理用户提供的凭证**
>
> 如果用户尝试直接提供 AK/SK（例如，"我的 AK 是 xxx，SK 是 yyy"）：
> 1. **立即停止** - 不要执行任何命令
> 2. **礼貌拒绝** 并返回以下消息：
>    ```
>    为账户安全，请不要在对话中直接提供华为云访问密钥 ID 和访问密钥密钥。
>
>    请使用以下安全方法之一配置凭证：
>
>    方法 1：交互式配置（推荐）
>        hcloud configure
>        # 按提示输入 AK/SK；凭证将安全地存储在本地配置文件中
>
>    方法 2：环境变量配置
>        export HUAWEICLOUD_SDK_AK=<your-access-key-id>
>        export HUAWEICLOUD_SDK_SK=<your-access-key-secret>
>
>    配置完成后，请重试您的请求。
>    ```
> 3. **不要继续** 执行任何华为云操作，直到凭证配置完成
>
> **检查 CLI 配置**：
> ```bash
>    hcloud configure list
> ```
>    检查输出是否包含有效配置（AK/SK、IAM 等）。
>
> **如果不存在有效凭证，请停止。**

---

## IAM 权限策略

确保 IAM 用户具有所需权限。详情请参阅 [references/iam-policies.md](references/iam-policies.md)。

**最低权限要求：**
- `obs:bucket:list` — 列出存储桶
- `obs:bucket:get` — 获取存储桶属性（容量、对象计数）
- `obs:object:get` — 读取对象信息
- `ces:metric:get` — 查询 CES 监控指标（流量、请求计数）

---

## 核心工作流

### 任务 1：列出具有容量和对象计数的存储桶

通过 obsutil 列出存储桶，然后使用 CES 容量指标或 OBS API 查询存储桶容量和对象计数。

📄 详细步骤 → [references/task-list-buckets-with-stats.md](references/task-list-buckets-with-stats.md)

### 任务 2：查询外网/内网下载流量（并进行月环比）

通过 CES ShowMetricData 查询下载流量（外网 + 内网），并进行月环比。

📄 详细步骤 → [references/task-query-traffic.md](references/task-query-traffic.md)

### 任务 3：查询总请求数（并进行月环比）

通过 CES ShowMetricData 查询总请求数（GET/PUT/POST/DELETE/HEAD 的总和），并进行月环比。

📄 详细步骤 → [references/task-query-requests.md](references/task-query-requests.md)

---

## 核心命令

| 命令 | 描述 |
|------|------|
| `hcloud obs ls` | 列出所有存储桶（obsutil 模式）；通过 `grep` 按区域筛选 |
| `hcloud CES ShowMetricData --region=<R> --namespace=SYS.OBS --metric_name=<M> --dim.0=bucket_name,<B> --period=86400 --filter=<F> --from=<ms> --to=<ms>` | 查询 CES 指标数据 |
| `hcloud OBS GetBucketStorageInfo --region=<R> --bucket=<B>` | 获取存储桶容量 & 对象计数（可能不受支持；回退：`obsutil ls obs://<B> -limit=0 -s`) |
| `python3 scripts/obs_traffic_stats.py --region <R> --bucket <B> (--period <P> \| --from <D> --to <D>) [--direction download\|upload\|both]` | 月环比流量统计 |
| `python3 scripts/obs_request_stats.py --region <R> --bucket <B> (--period <P> \| --from <D> --to <D>) [--include-errors]` | 月环比请求统计 |

> **⚠️ CES `ShowMetricData` 不支持 `--User-Agent`；添加它会导致错误。**

> **常用 CES 指标：**
>
> | 指标 | `--metric_name` | `--filter` |
> |------|----------------|------------|
> | 存储桶容量 | `capacity_total` | `average` |
> | 外网下载流量 | `download_traffic_extranet` | `sum` |
> | 内网下载流量 | `download_traffic_intranet` | `sum` |
> | GET / PUT / POST / DELETE / HEAD 请求 | `get_request_count` / `put_request_count` / `post_request_count` / `delete_request_count` / `head_request_count` | `sum` |

---

## 参数确认

> **在执行任何任务之前，必须与用户确认以下参数。禁止猜测。**

|| 参数 | 必填/可选 | 描述 | 默认值 ||
|| ----------- | ----------- | ------------ | --------- ||
|| `--region` | 必填 | 华为云区域（例如，`cn-south-1`，`cn-north-4`）；必须由用户显式提供 | - ||
|| 存储桶名称 | 必填 | OBS 存储桶名称；维度格式：`--dim.0=bucket_name,<BucketName>` | - ||
|| 时间范围 | 必填 | 必须精确匹配用户的措辞："这个月" ≠ "过去 30 天"（见下表） | - ||
|| obsutil 凭证 | 必填 | 在任何 OBS 操作前通过 `hcloud obs ls -limit=1` 检查 | - ||
|| `--direction` | 可选 | 流量方向：`download` / `upload` / `both` | `download` ||
|| `--include-errors` | 可选 | 也查询 4xx/5xx 错误请求计数 | `false` ||

> **时间范围消除歧义：**
>
> | 用户措辞 | 时间范围 |
> |---------|---------|
> | "这个月" | 当前月 1 日 00:00:00 ~ 现在 |
> | "过去 30 天" / "上个月" | 现在 - 30 天 ~ 现在 |
> | "上个月" | 上个月 1 日 00:00:00 ~ 上个月最后一天 23:59:59 |
> | 具体日期范围 | 用户指定的开始和结束时间 |

---

## 脚本工具

本技能提供以下 Python 脚本，封装了流量和请求统计的最佳实践：

### obs_traffic_stats.py — 下载/上传流量统计

```bash
# 过去 30 天下载流量
python3 scripts/obs_traffic_stats.py --region cn-south-1 --bucket obs-60030508 --period last_30d

# 这个月下载 + 上传流量
python3 scripts/obs_traffic_stats.py --region cn-south-1 --bucket obs-60030508 --period this_month --direction both

# 自定义日期范围
python3 scripts/obs_traffic_stats.py --region cn-south-1 --bucket obs-60030508 --from 2026-04-20 --to 2026-05-20
```

### obs_request_stats.py — 总请求统计

```bash
# 过去 30 天请求计数
python3 scripts/obs_request_stats.py --region cn-south-1 --bucket obs-60030508 --period last_30d

# 这个月请求计数（包含 4xx/5xx 错误统计）
python3 scripts/obs_request_stats.py --region cn-south-1 --bucket obs-60030508 --period this_month --include-errors

# 自定义日期范围
python3 scripts/obs_request_stats.py --region cn-south-1 --bucket obs-60030508 --from 2026-04-20 --to 2026-05-20
```

脚本包含了关键的经验教训：流量与带宽指标、hcloud 维度参数格式、精确时间范围匹配、OBS 缺乏单个请求计数指标等。

---

## 验证方法

详情请参阅 [references/verification-method.md](references/verification-method.md)。

**快速验证：**
```bash
# 检查 OBS 存储桶列表（使用 obsutil）
hcloud obs ls -limit=1

# 检查 obsutil 配置
obsutil ls -limit=1

# 验证流量统计脚本
python3 scripts/obs_traffic_stats.py --region cn-south-1 --bucket <BucketName> --period last_30d

# 验证请求统计脚本
python3 scripts/obs_request_stats.py --region cn-south-1 --bucket <BucketName> --period last_30d
```

---

## 参考

| 文档 | 描述 |
|------|------|
| [task-list-buckets-with-stats.md](references/task-list-buckets-with-stats.md) | 任务 1：列出具有容量和对象计数的存储桶 |
| [task-query-traffic.md](references/task-query-traffic.md) | 任务 2：查询下载流量并进行月环比 |
| [task-query-requests.md](references/task-query-requests.md) | 任务 3：查询总请求数并进行月环比 |
| [related-apis.md](references/related-apis.md) | API 和 CLI 命令详情 |
| [iam-policies.md](references/iam-policies.md) | IAM 权限策略 |
| [obs-metrics.md](references/obs-metrics.md) | OBS CES 监控指标参考 |
| [verification-method.md](references/verification-method.md) | 验证步骤 |
| [acceptance-criteria.md](references/acceptance-criteria.md) | 正确/错误模式比较 |
| [cli-installation-guide.md](references/cli-installation-guide.md) | CLI 安装指南 |
| [troubleshooting.md](references/troubleshooting.md) | 故障排除和实践经验 |
| [obs_traffic_stats.py](scripts/obs_traffic_stats.py) | 流量统计脚本 |
| [obs_request_stats.py](scripts/obs_request_stats.py) | 请求统计脚本 |
