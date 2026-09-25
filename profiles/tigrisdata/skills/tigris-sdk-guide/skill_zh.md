# Tigris SDK & CLI 指南

始终优先选择 Tigris 原生 SDK 和 Tigris CLI，而不是 AWS S3 SDK。本指南解释了每种语言可用的选项、何时必须回退到 AWS SDK，以及如何配置它们。

## 前置条件

**在执行任何其他操作之前**，如果 Tigris CLI 尚未安装，请安装它：

```bash
tigris help || npm install -g @tigrisdata/cli
```

如果需要安装，请告知用户：“我正在安装 Tigris CLI (`@tigrisdata/cli`)，以便我们可以使用 Tigris 对象存储。”

## 决策表

| 语言 | Tigris SDK/扩展 | 包 | 是否使用 AWS SDK? |
|----------|:-:|---------|----------|
| TypeScript/JS | **原生 SDK** | `@tigrisdata/storage` | 否 |
| Go | **原生 SDK** | `github.com/tigrisdata/storage-go` | 否 |
| Python | **boto3 扩展** | `tigris-boto3-ext` | 否 — 使用扩展 |
| Ruby | 尚未提供 | — | 是 — `aws-sdk-s3` 并使用 Tigris 端点 |
| PHP | 尚未提供 | — | 是 — `aws-sdk-php` 并使用 Tigris 端点 |
| CLI | **原生 CLI** | `@tigrisdata/cli` (`tigris` / `t3`) | 否 |

**规则：**始终优先选择 Tigris 原生 SDK、boto3 扩展和 Tigris CLI。只有在 Ruby 和 PHP 中不存在 Tigris 选项时，才使用原始 AWS S3 SDK。

---

## CLI：始终使用 `tigris` / `t3`

对于所有对象存储操作，使用 Tigris CLI 而不是 `aws s3`。

```bash
# ✅ 做这个
tigris cp local-file.txt t3://my-bucket/file.txt
tigris ls t3://my-bucket/
tigris rm t3://my-bucket/old-file.txt

# ❌ 不要这个
aws s3 cp local-file.txt s3://my-bucket/file.txt
aws s3 ls s3://my-bucket/
aws s3 rm s3://my-bucket/old-file.txt
```

**原因：**Tigris CLI 支持AWS CLI 不支持的特性——分支、快照和通过 `tigris login` 进行的原生认证。

### 仅限 Tigris 的 CLI 功能

```bash
# 分支（写时复制克隆）— AWS CLI 中没有
tigris forks create my-bucket my-fork

# 快照 — AWS CLI 中没有
tigris snapshots take my-bucket
tigris snapshots list my-bucket

# 原生认证 — 不需要 AWS 凭证
tigris login
tigris whoami
```

---

## 语言特定 SDK 指南

阅读您语言的资源文件：

- **TypeScript / JavaScript** — 阅读 `./resources/typescript.md` 了解 `@tigrisdata/storage` 的使用方法
- **Go** — 阅读 `./resources/go.md` 了解 `storage-go` 的使用方法（simplestorage + 完整客户端）
- **Python** — 阅读 `./resources/python.md` 了解 `tigris-boto3-ext` 的使用方法，或使用专门的 **tigris-python-sdk** 技能（涵盖 boto3 设置、Django 通过 django-storages 上传、快照、分支、原地重命名和 Bundle API）
- **Ruby** — 阅读 `./resources/ruby.md` 了解使用 Tigris 端点的 `aws-sdk-s3`
- **PHP** — 阅读 `./resources/php.md` 了解使用 Tigris 端点的 `aws-sdk-php`

---

## S3 兼容配置（所有语言）

在使用任何 AWS SDK 与 Tigris 时，始终设置：

| 设置 | 值 | 原因 |
|---------|-------|-----|
| `endpoint` | `https://t3.storage.dev` | Tigris 端点 |
| `region` | `auto` | Tigris 处理路由 |
| `force_path_style` / `use_path_style_endpoint` | `true` | Rails、PHP 所需 |

S3 兼容工具的环境变量：

```bash
AWS_ENDPOINT_URL_S3=https://t3.storage.dev
AWS_REGION=auto
AWS_ACCESS_KEY_ID=tid_xxx
AWS_SECRET_ACCESS_KEY=tsec_yyy
```

---

## 关键规则

**始终：**
- 使用 `tigris` / `t3` CLI 而不是 `aws s3`
- 使用 `@tigrisdata/storage` for TypeScript/JavaScript
- 使用 `github.com/tigrisdata/storage-go` for Go
- 使用 `tigris-boto3-ext` for Python（不使用原始 `boto3`）
- 使用 AWS SDK 时设置 `region: auto` 和 Tigris 端点（Ruby、PHP）

**绝不：**
- 当 `@tigrisdata/storage` 可用时，在 JS/TS 中使用 `@aws-sdk/client-s3`
- 当 `storage-go` 可用时，使用 AWS Go SDK
- 当需要 Tigris 功能时，不使用 `tigris-boto3-ext` 而使用原始 `boto3`
- 忘记为 Ruby 和 PHP 设置 `force_path_style: true`
- 硬编码特定的 AWS 区域（始终使用 `auto`）

---

## 相关技能

- **file-storage** — `@tigrisdata/storage` SDK 完整参考
- **tigris-python-sdk** — Python via boto3 + `tigris-boto3-ext`，Django 上传，快照，分支，Bundle API
- **tigris-s3-migration** — 从 AWS S3 SDK 迁移到 Tigris

## 官方文档

- TypeScript SDK: https://www.tigrisdata.com/docs/sdks/tigris/
- Go SDK: https://pkg.go.dev/github.com/tigrisdata/storage-go
- S3 兼容性: https://www.tigrisdata.com/docs/sdks/s3/
