---
name: huawei-cloud-obs-upload
description: '将本地文件或目录上传至华为云OBS（对象存储服务）存储桶，列出OBS存储桶的容量和对象数量，并通过crontab进行周期性上传调度。

  当用户需要执行以下操作时，请使用此技能：(1) 将本地文件或目录上传至OBS存储桶，(2) 列出OBS存储桶并检查其存储容量和对象数量，(3) 设置定时/周期性上传任务，自动将本地目录同步至OBS存储桶。

  触发条件包括：用户提及“OBS”、“对象存储”、“桶列表”、“桶容量”、“上传至OBS”、“上传文件”、“上传目录”、“定时上传”、“周期性上传”、“同步至桶”、“对象存储”、“桶列表”、“桶容量”、“上传文件”、“上传目录”、“定时上传”、“OBS管理”。'
---

# 华为云OBS上传技能

## 概述

将本地文件或目录上传到华为云OBS存储桶，列出具有容量和对象计数的OBS存储桶，并通过crontab进行周期性上传。**上传操作使用obsutil；存储桶列表/统计使用`hcloud obs ls` + CES指标。**

**工具分离原则：**
- **obsutil** — 文件/目录上传，计划上传同步 (**上传核心工具；hcloud CLI没有PutObject支持**)
- **hcloud CLI** — 通过`hcloud obs ls`（obsutil模式）列出存储桶，通过`hcloud CES ShowMetricData`进行存储桶容量/对象计数统计
- **crontab / 任务调度器** — 操作系统级计划任务，用于周期性上传（无守护进程依赖）

**安全架构：**
- AK/SK永远不会在对话中读取、回显或打印
- obsutil凭证由用户在其终端中配置（对话中从不询问）
- 删除操作严格禁止（不可逆）；超出范围的操作会被拒绝并提供引导替代方案
- 对于目录上传，是否保留目录结构（`-flat`）由客户的明确回答决定，从不假设

## ⛔ 禁止操作（安全约束）

> **此技能严格禁止以下操作，无论用户请求如何：**

| 禁止操作 | 原因 |
|--------|------|
| ❌ 删除存储桶 (`DeleteBucket` / `obsutil rm -bucket`) | 不可逆；会删除整个存储桶和所有对象 |
| ❌ 删除对象 (`DeleteObject` / `obsutil rm`) | 不可逆；删除的对象无法恢复（除非启用了版本控制） |
| ❌ 批量删除对象 (`DeleteObjects` / `obsutil rm -r`) | 不可逆；批量删除影响范围很广 |
| ❌ 清空存储桶 (`obsutil rm -bucket -r`) | 不可逆；删除存储桶中的所有对象 |
| ❌ 下载对象 (`GetObject` / `obsutil cp obs://... <本地路径>`) | 此技能仅支持上传；下载是单独的工作流 |
| ❌ 创建存储桶 (`CreateBucket` / `obsutil mb`) | 存储桶创建有专门的技能，并具有完整的前提条件 |
| ❌ 复制对象 (`CopyObject` / `hcloud OBS CopyObject`) | 跨存储桶对象复制超出此技能的范围 |
| ❌ 生命周期配置 (`SetBucketLifecycle`) | 存储成本管理是单独的存储桶级配置任务 |
| ❌ 恢复归档对象 (`RestoreObject` / `obsutil restore`) | 归档恢复是具有检索模式和TTL的单独工作流 |
| ❌ 预签名URL (`CreatePresignedUrl`) | 临时共享需要SDK签名；CLI上传不支持 |
| ❌ 存储桶ACL/策略 (`SetBucketAcl` / `SetBucketPolicy`) | 权限管理是单独的安全任务 |
| ❌ 直接在对话中要求用户提供AK/SK | 凭证绝不能出现在对话中 |
| ❌ 从hcloud配置文件中提取AK/SK | 凭证是加密的，不能直接使用 |
| ❌ 在OBS操作之前跳过obsutil凭证检查 | 没有配置凭证，操作会失败 |
| ❌ 在未经询问客户的情况下使用`-flat`进行目录上传 | `-flat`会丢弃目录结构；必须遵循客户的明确回答 |
| ❌ 猜测本地路径、存储桶名称或目标前缀 | 必须参数必须由用户提供 |

> **如果用户请求删除操作，你必须拒绝并告知：**
> "根据安全约束，此技能不允许删除操作（删除存储桶/对象/批量删除/清空存储桶）。请使用华为云OBS控制台或手动obsutil。"

> **如果用户请求超出范围的操作，不要尝试执行。使用下表中的推荐替代方案告知用户：**

| 操作 | 推荐替代方案 |
|------|------------|
| 下载对象 | 使用`obsutil cp obs://<存储桶>/<键> <本地路径>`手动，或使用OBS控制台 |
| 创建存储桶 | 使用专门的技能[huawei-cloud-obs-bucket-create](https://skills.huaweicloud.com/detail/huawei-cloud-obs-bucket-create)，或使用OBS控制台 |
| 复制对象 | 使用`hcloud OBS CopyObject`手动，或使用OBS控制台 |
| 生命周期配置 | 使用OBS控制台（存储桶 > 生命周期），或`hcloud OBS SetBucketLifecycle` |
| 恢复归档对象 | 使用`obsutil restore obs://<存储桶>/<键>`手动，或使用OBS控制台 |
| 预签名URL | 使用华为云SDK（Java/Python/Go）生成预签名URL，或使用OBS控制台 |
| 存储桶ACL/策略 | 使用OBS控制台（存储桶 > 权限），或`hcloud OBS SetBucketAcl`/`SetBucketPolicy` |

## 架构

```
华为云OBS上传管理
├── 任务 1: ListBucketsWithStats   (列出具有容量和对象计数的存储桶)
│   ├── 1a. hcloud obs ls: 列出所有存储桶
│   ├── 1b. CES指标 / OBS API: 查询存储桶容量和对象计数
│   └── 1c. 向用户报告存储桶统计表
├── 任务 2: UploadFile             (将本地文件或目录上传到目标存储桶)
│   ├── 2a. 与用户确认本地路径 + 存储桶名称 + 目标前缀
│   ├── 2b. 对于目录：询问客户是否保留源目录结构（决定 -flat）
│   ├── 2c. obsutil cp: 单个文件（-flat）或目录（-r，可选 -flat 由客户回答决定）
│   └── 2d. 验证上传结果
└── 任务 3: ScheduledUpload       (通过crontab计划本地目录到目标存储桶的周期性上传)
    ├── 3a. 与用户确认本地目录 + 存储桶 + 前缀 + 计划周期
    ├── 3b. 询问客户是否保留目录结构（决定 -flat）
    ├── 3c. 生成obsutil上传脚本（根据客户回答决定是否使用 -flat）
    ├── 3d. 设置crontab / 任务调度器计划任务
    └── 3e. 验证计划任务是否设置
```

## 前提条件

> **前提检查 1/3: 华为云CLI (hcloud / KooCLI) >= 3.2.0 必须安装**
> 运行 `hcloud version` 以验证版本 >= 3.2.0。如果未安装或版本过低，
> 请参阅[参考资料/cli安装指南.md](references/cli-installation-guide.md)获取安装指南。

```bash
hcloud version
```

> **前提检查 2/3: obsutil >= 5.5.0 必须安装（用于上传功能）**
> 文件/目录上传需要华为云obsutil CLI工具。
> 运行 `obsutil version` 以验证版本 >= 5.5.0。如果未安装，
> 请参阅[参考资料/cli安装指南.md](references/cli-installation-guide.md)获取安装指南。

```bash
obsutil version
```

> **前提检查 3/3: obsutil凭证配置必须**
>
> hcloud obs模块在底层映射到obsutil，该工具需要单独的AK/SK和Endpoint配置。
> 在执行OBS操作之前，**你必须检查obsutil凭证是否已配置**：
>
> ```bash
> hcloud obs ls -limit=1
> ```
>
> **如果响应是 `Please set ak, sk and endpoint in the configuration file!` 或 `InvalidAccessKeyId`，obsutil凭证未配置。**
>
> **解决方法：提供以下示例命令，并让用户在其终端中配置（不要在对话中要求用户提供AK/SK）：**
>
> ```
> obsutil凭证未配置。请在您的终端中运行以下命令进行配置（AK/SK可以从华为云控制台“我的凭证”页面获取）：
>
>   hcloud obs config -i=<您的AK> -k=<您的SK> -e=obs.<区域>.myhuaweicloud.com
>
> 示例（广州区域）：
>   hcloud obs config -i=<您的AK> -k=<您的SK> -e=obs.cn-south-1.myhuaweicloud.com
>
> 常见Endpoint：
>   cn-north-4  → obs.cn-north-4.myhuaweicloud.com
>   cn-east-3   → obs.cn-east-3.myhuaweicloud.com
>   cn-south-1  → obs.cn-south-1.myhuaweicloud.com
>   cn-southwest-2 → obs.cn-southwest-2.myhuaweicloud.com
>
> 配置完成后重新尝试。
> ```

> **⚠️ hcloud参数格式要求**
>
> hcloud（KooCLI）云服务API命令（大写模块，例如`hcloud CES ShowMetricData`）**必须使用`--param=value`格式**（用等号连接）；空格分隔格式不受支持。
>
> ✅ 正确：`hcloud CES ShowMetricData --region=cn-south-1 --namespace=SYS.OBS`
>
> ❌ 错误：`hcloud CES ShowMetricData --region cn-south-1`
>
> **注意：** `hcloud obs`（小写，obsutil模式）直接映射到obsutil命令，并使用obsutil参数样式（例如`hcloud obs ls`，`hcloud obs config -i=...`）；`--param=value`规则不适用。没有`hcloud OBS ListBuckets`命令 — 使用`hcloud obs ls`列出存储桶。

---

## 身份验证

> **安全规则（必须遵守）：**
> - **禁止**读取、回显或打印AK/SK值
> - **禁止**在对话中直接要求用户输入AK/SK
> - **禁止**使用`hcloud configure set`传递明文凭证值
> - **禁止**接受对话中用户直接提供的AK/SK
> - **仅允许**从环境变量或配置的CLI配置文件中读取凭证
>
> **⚠️ 重要：处理用户提供的凭证**
>
> 如果用户尝试直接提供AK/SK（例如，“我的AK是xxx，SK是yyy”）：
> 1. **立即停止** — 不要执行任何命令
> 2. **礼貌地拒绝**并返回以下消息：
>    ```
>    为账户安全，请不要在对话中直接提供华为云访问密钥ID和访问密钥。
>
>    请使用以下安全方法之一配置凭证：
>
>    方法 1：交互式配置（推荐）
>        hcloud configure
>        # 按提示输入AK/SK；凭证将安全地存储在本地配置文件中
>
>    方法 2：环境变量配置
>        export HW_ACCESS_KEY=<your-access-key-id>
>        export HW_SECRET_KEY=<your-access-key-secret>
>
>    配置完成后，请重试您的请求。
>    ```
> 3. **不要继续**执行任何华为云操作，直到凭证配置完成
>
> **检查CLI配置**：
> ```bash
>    hcloud configure list
> ```
>    检查输出是否包含有效配置（AK/SK、IAM等）。
>
> **如果没有有效凭证，请停止。**

---

## IAM权限策略

确保IAM用户具有所需的权限。请参阅[参考资料/iam策略.md](references/iam-policies.md)获取完整权限表。

**最低权限要求：**
- `obs:bucket:list` — 列出存储桶
- `obs:bucket:get` — 获取存储桶属性（容量、对象计数）
- `obs:object:get` — 读取对象信息
- `obs:object:put` — 上传对象

**权限边界：**

- **范围约束**：仅上传到和列出用户指定的存储桶。永远不会删除或修改存储桶级配置。
- **必须停止**：凭证缺失或无效，用户拒绝任何确认，目标存储桶不存在，或本地路径不存在。
- **禁止操作**：任何删除操作，上述任何超出范围的操作，访问用户指定存储桶外的资源。

---

## 核心工作流

### 任务 1: 列出具有容量和对象计数的存储桶

通过obsutil列出存储桶，然后使用CES容量指标或OBS API查询存储桶容量和对象计数。

> **⚠️ 工具分离：`hcloud obs ls`用于列出，`hcloud CES ShowMetricData`用于统计**
>
> - **`hcloud obs ls`**：列出所有存储桶（obsutil模式；没有`--region`参数 — 区域通过`hcloud obs config -e=...`设置）
> - **`hcloud CES ShowMetricData` / OBS API**：查询每个存储桶的容量和对象计数

📄 详细步骤 → [参考资料/task-list-buckets-with-stats.md](references/task-list-buckets-with-stats.md)

**子任务：**

1. **1a. 列出存储桶** — `hcloud obs ls`（或`obsutil ls`）
2. **1b. 查询存储桶统计** — CES容量指标或OBS API用于容量和对象计数
3. **1c. 报告统计** — 以表格形式呈现存储桶名称、容量、对象计数

### 任务 2: 将本地文件或目录上传到目标存储桶

使用obsutil将文件或目录上传到指定的OBS存储桶，支持单个文件和目录上传。

> **⚠️ 上传操作需要obsutil，hcloud不需要**
>
> hcloud CLI不支持OBS对象上传操作（没有PutObject/UploadPart CLI命令）。上传文件/目录**必须使用obsutil**。

> **⚠️ 对于目录上传，你必须首先询问客户是否保留源目录结构，然后根据他们的明确回答决定是否使用`-flat`。从不默认。**

📄 详细步骤 → [参考资料/task-upload-file.md](references/task-upload-file.md)

**子任务：**

1. **2a. 确认参数** — 本地路径、目标存储桶名称、目标前缀（可选）与用户确认
2. **2b. 决定`-flat`** — 单个文件：使用`-flat`无需询问；目录：询问客户是否保留目录结构
3. **2c. 执行上传** — `obsutil cp`单个文件或目录（根据客户回答决定是否使用`-flat`）
4. **2d. 验证结果** — 检查上传退出代码并确认对象存在于存储桶中

### 任务 3: 计划本地目录到目标存储桶的周期性上传

通过crontab计划任务定期将本地目录增量上传到指定的OBS存储桶。

> **⚠️ 定期上传基于操作系统级计划任务机制（Linux/macOS: crontab，Windows: 任务调度器），无守护进程依赖。**

> **⚠️ 在生成定期上传脚本之前，你必须首先询问客户是否保留源目录结构，然后根据他们的明确回答决定是否使用`-flat`。从不默认。**

📄 详细步骤 → [参考资料/task-scheduled-upload.md](references/task-scheduled-upload.md)

**子任务：**

1. **3a. 确认参数** — 本地目录、存储桶、前缀、计划周期与用户确认
2. **3b. 决定`-flat`** — 询问客户是否保留目录结构
3. **3c. 生成上传脚本** — `$HOME/obs-scheduled-upload-<存储桶名称>.sh`（根据客户回答决定是否使用`-flat`）
4. **3d. 设置计划任务** — crontab（Linux/macOS）或任务调度器（Windows）
5. **3e. 验证** — `crontab -l`或`schtasks /query`确认任务已设置

---

## 核心命令

### obsutil（上传核心 — hcloud没有PutObject）

```bash
# 上传单个文件
obsutil cp <本地文件路径> obs://<存储桶名称>/<对象键> -flat

# 上传目录，保留结构（客户选择了“是”）
obsutil cp <本地目录路径> obs://<存储桶名称>/<前缀> -r

# 上传目录，扁平化文件（客户选择了“否”）
obsutil cp <本地目录路径> obs://<存储桶名称>/<前缀> -r -flat

# 定期增量上传，保留结构
obsutil cp <本地目录路径> obs://<存储桶名称>/<前缀> -r -f -u

# 定期增量上传，扁平化文件
obsutil cp <本地目录路径> obs://<存储桶名称>/<前缀> -r -flat -f -u

# 列出存储桶
obsutil ls
```

### hcloud CLI（存储桶列出 + 统计）

```bash
# 列出所有存储桶（obsutil模式；没有--region参数）
hcloud obs ls

# 检查obsutil凭证配置
hcloud obs ls -limit=1

# 配置obsutil凭证（用户在终端中运行）
hcloud obs config -i=<AK> -k=<SK> -e=<Endpoint>

# 查询存储桶容量/对象计数统计（云服务API模式，--param=value格式）
hcloud CES ShowMetricData \
  --region=cn-south-1 \
  --namespace=SYS.OBS \
  --metric_name=capacity_total \
  --dim.0=bucket_name,my-bucket \
  --period=86400 \
  --filter=average \
  --from=1746057600000 \
  --to=1747612800000
```

> **⚠️ 核心命令的关键约束：**
>
> - 上传：**必须使用obsutil cp** — hcloud CLI没有PutObject支持
> - 列出存储桶：**必须使用`hcloud obs ls`** — 没有`hcloud OBS ListBuckets`命令
> - 目录上传的`-flat`：**必须遵循客户的明确回答**，从不默认
> - hcloud云服务API参数（大写模块，例如`hcloud CES ...`）：**必须使用`--param=value`格式**；`hcloud obs`（obsutil模式）使用obsutil参数样式
> - AK/SK：**绝不能出现在对话中**；用户在其终端中配置obsutil凭证

---

## 参数确认

> **在执行任何任务之前，必须与用户确认以下参数。禁止猜测。**

| 参数 | 必填/可选 | 描述 | 默认值 |
|-------|------------|-------|-------|
| 区域 | 必填 | 华为云区域（例如，`cn-south-1`，`cn-north-4`）；必须由用户显式选择 | - |
| 本地文件/目录路径 | 必填（任务2/3） | 上传的本地路径；必须存在且可读 | - |
| 目标存储桶名称 | 必填（任务2/3） | 上传的目标OBS存储桶名称 | - |
| 目标路径前缀 | 可选（任务2/3） | 存储桶内的目标路径前缀 | 存储桶根目录 |
| 保留目录结构 | 必填（目录上传） | 询问用户："是" → 无`-flat`；"否" → `-flat` | -（必须询问） |
| 定时周期 | 必填（任务3） | 执行周期，例如，每小时、每天8:00、每30分钟 | - |
| Cron表达式 | 可选（任务3） | 如果用户熟悉cron表达式，可以直接提供 | - |

> **注意**：对话中不需要AK/SK参数。用户通过终端中的`hcloud obs config`配置凭证。

---

## 验证方法

详细内容请参阅[references/verification-method.md](references/verification-method.md)。常见问题和解决方案请参阅[references/troubleshooting.md](references/troubleshooting.md)。

**快速验证：**
```bash
hcloud version && obsutil version && hcloud obs ls -limit=1
```

**上传后验证：** `obsutil ls obs://<BucketName>/<Prefix>`以确认上传的对象存在。

---

## 参考

| 文档 | 描述 |
|------|------|
| [task-list-buckets-with-stats.md](references/task-list-buckets-with-stats.md) | 任务1：列出具有容量和对象计数的存储桶 |
| [task-upload-file.md](references/task-upload-file.md) | 任务2：上传文件或目录 |
| [task-scheduled-upload.md](references/task-scheduled-upload.md) | 任务3：定时上传 |
| [related-apis.md](references/related-apis.md) | API和CLI命令详情 |
| [iam-policies.md](references/iam-policies.md) | IAM权限策略 |
| [obs-metrics.md](references/obs-metrics.md) | OBS CES监控指标参考 |
| [verification-method.md](references/verification-method.md) | 验证步骤 |
| [acceptance-criteria.md](references/acceptance-criteria.md) | 正确/错误模式比较 |
| [cli-installation-guide.md](references/cli-installation-guide.md) | CLI安装指南 |
| [troubleshooting.md](references/troubleshooting.md) | 故障排除和实践经验 |
