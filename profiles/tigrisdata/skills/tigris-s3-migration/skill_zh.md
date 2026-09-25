# 从 S3/GCS/Azure 迁移到 Tigris

将您的对象存储迁移到 Tigris，实现零停机时间。Tigris 兼容 S3，因此大多数应用程序只需更换端点和凭证即可。影子存储桶支持透明迁移，无需提前移动数据。

## 前置条件

**在执行任何操作之前**，如果 Tigris CLI 尚未安装，请安装它：

```bash
tigris help || npm install -g @tigrisdata/cli
```

如果您需要安装，请告知用户："我正在安装 Tigris CLI (`@tigrisdata/cli`)，以便我们可以使用 Tigris 对象存储。"

## 迁移策略

| 策略             | 停机时间 | 适用于                                                              |
| ---------------- | -------- | ------------------------------------------------------------------- |
| **影子存储桶**    | 零       | 生产应用程序 — Tigris 在缓存未命中时读取 S3，自动回填数据             |
| **批量复制**        | 短暂    | 小型数据集，干净的切换                                               |
| **增量同步** | 零       | 大型数据集，渐进式迁移                                               |

---

## 影子存储桶（推荐）

Tigris 在缓存未命中时从您现有的 S3 存储桶读取数据，并逐渐回填数据。无需提前移动数据。

```bash
# 创建 Tigris 存储桶
tigris buckets create my-app-uploads
# 将 Tigris 存储桶指向源 S3 存储桶
tigris buckets set-migration my-app-uploads \
  --bucket my-existing-s3-bucket \
  --endpoint https://s3.us-east-1.amazonaws.com \
  --region us-east-1 \
  --access-key AKIA_YOUR_AWS_KEY \
  --secret-key YOUR_AWS_SECRET
```

添加 `--write-through` 以将新写入同步回源存储桶 — 在迁移窗口期间提供安全的回滚路径时非常有用。

**工作原理：**

1. 请求发送到 Tigris
2. 如果对象存在于 Tigris 中，则直接提供
3. 如果不存在，Tigris 从 S3 获取数据，提供并缓存

**迁移所有数据（可选）：**

懒加载迁移仅在请求对象时复制对象。要主动在服务器端迁移所有剩余对象，请运行：

```bash
# 迁移存储桶中所有未迁移的对象
tigris buckets migrate my-app-uploads

# 或范围到键前缀
tigris buckets migrate my-app-uploads/images/
```

该命令在前台运行并报告进度，因此您可以在切换之前完全清空源。

**迁移完成后：**

```bash
# 禁用迁移（使 Tigris 成为唯一数据源）
tigris buckets set-migration my-app-uploads --disable
```

---

## 批量复制

对于小型数据集或在需要干净切换时：

### 从 Google Cloud Storage

```bash
gsutil -m cp -r gs://my-gcs-bucket /tmp/migration/
tigris cp /tmp/migration/ t3://my-app-uploads/ -r
```

### 从 Azure Blob Storage

```bash
az storage blob download-batch -d /tmp/migration/ -s my-container
tigris cp /tmp/migration/ t3://my-app-uploads/ -r
```

---

## SDK 代码更改

查看您的语言资源文件以了解迁移前后的示例：

- **Node.js / TypeScript** — 阅读 `./resources/sdk-nodejs.md` 了解 AWS SDK → Tigris SDK 迁移
- **Go** — 阅读 `./resources/sdk-go.md` 了解 AWS SDK → Tigris SDK 迁移
- **Python** — 阅读 `./resources/sdk-python.md` 了解 boto3 → tigris-boto3-ext 迁移，或使用 **tigris-python-sdk** 技能获取迁移后的开发者体验（Django、快照、分支、Bundle API）
- **Ruby** — 阅读 `./resources/sdk-ruby.md` 了解 aws-sdk-s3 端点切换
- **PHP** — 阅读 `./resources/sdk-php.md` 了解 aws-sdk-php 端点切换

---

## 环境变量更改

```bash
# 之前（AWS）
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET=my-bucket

# 之后（Tigris）
AWS_ACCESS_KEY_ID=tid_xxx
AWS_SECRET_ACCESS_KEY=tsec_yyy
AWS_ENDPOINT_URL_S3=https://t3.storage.dev
AWS_REGION=auto
S3_BUCKET=my-bucket  # 存储桶名称可以保持不变
```

对于具有特定 Tigris 环境变量的框架：

```bash
TIGRIS_STORAGE_ACCESS_KEY_ID=tid_xxx
TIGRIS_STORAGE_SECRET_ACCESS_KEY=tsec_yyy
TIGRIS_STORAGE_ENDPOINT=https://t3.storage.dev
TIGRIS_STORAGE_BUCKET=my-bucket
```

---

## 验证检查清单

- [ ] 源和 Tigris 之间的对象数量匹配
- [ ] 抽查文件：下载几个并验证内容/校验和
- [ ] 测试预签名 URL 生成（端点必须指向 Tigris）
- [ ] 如果使用浏览器上传，测试 CORS（在 Tigris 存储桶上重新配置）
- [ ] 在暂存环境中测试所有上传/下载代码路径
- [ ] 如果使用 CloudFront/类似服务，请更新 CDN 源（指向 Tigris）
- [ ] 如果使用自定义域名，请更新 DNS

---

## 回滚策略

1. 在迁移期间将源存储桶设置为只读（不要删除数据）
2. 在验证期间并行运行两个系统
3. 确认 Tigris 完全正常工作后，才删除源数据
4. 如果使用影子存储桶，删除影子源是不可逆转的步骤

---

## 常见错误

| 错误                                 | 解决方法                                                                                |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| 忘记更新预签名 URL 端点             | 预签名 URL 必须使用 Tigris 端点，而不是 S3                                                |
| Tigris 上未配置 CORS                 | 重新创建 CORS 规则：`tigris buckets cors set`                                            |
| 区域硬编码为 `us-east-1`             | 使用 `auto` for Tigris                                                              |
| `path_style` 未设置                  | 添加 `force_path_style: true`（Ruby/Rails）或 `use_path_style_endpoint: true`（PHP） |
| 自定义域名 DNS 仍然指向 S3           | 更新 CNAME 以指向 Tigris                                                              |

---

## 相关技能

- **file-storage** — CLI 设置和 SDK 参考
- **tigris-security-access-control** — CORS 和访问密钥设置

## 官方文档

- S3 兼容性：https://www.tigrisdata.com/docs/sdks/s3/
- 影子存储桶 & 迁移：https://www.tigrisdata.com/docs/migration/
- CLI：`tigris buckets set-migration` — https://www.tigrisdata.com/docs/cli/buckets/set-migration
- CLI：`tigris buckets migrate` — https://www.tigrisdata.com/docs/cli/buckets/migrate
