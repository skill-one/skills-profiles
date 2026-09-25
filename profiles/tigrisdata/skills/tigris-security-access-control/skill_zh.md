# Tigris 安全与访问控制

配置 Tigris 对象存储的访问密钥、CORS 规则、存储桶可见性和预签名 URL 安全性。涵盖密钥生命周期管理、基于角色的访问控制和安全审计。

## 前置条件

**在其他任何操作之前**，如果 Tigris CLI 尚未安装，请安装它：

```bash
tigris help || npm install -g @tigrisdata/cli
```

如果您需要安装它，请告诉用户：“我正在安装 Tigris CLI (`@tigrisdata/cli`)，以便我们可以使用 Tigris 对象存储。”

## 快速参考

| 操作 | 命令 |
|-------|---------|
| 创建密钥 | `tigris access-keys create "my-key"` |
| 列出密钥 | `tigris access-keys list` |
| 分配到存储桶 | `tigris access-keys assign <tid> --bucket <name> --role Editor` |
| 撤销密钥 | `tigris access-keys delete <tid>` |
| 设置 CORS | `tigris buckets cors set <bucket> --config cors.json` |
| 获取 CORS | `tigris buckets cors get <bucket>` |
| 移除 CORS | `tigris buckets cors delete <bucket>` |

---

## 密钥生命周期

### 创建

```bash
tigris access-keys create "production-app-key"
# 输出：
# Access Key ID: tid_xxx
# Secret Access Key: tsec_yyy  ← 仅显示一次，立即保存
```

### 分配到存储桶

```bash
# Editor: 读取 + 写入 + 删除
tigris access-keys assign tid_xxx --bucket my-app-uploads --role Editor

# ReadOnly: 仅读取
tigris access-keys assign tid_xxx --bucket my-app-uploads --role ReadOnly
```

| 角色 | 读取 | 写入 | 删除 | 使用场景 |
|------|------|-------|--------|----------|
| `Editor` | 是 | 是 | 是 | 上传/修改文件的 App 服务器 |
| `ReadOnly` | 是 | 否 | 否 | 仅读取/提供文件的服务 |

### 精确限制密钥范围

为不同用途创建单独的密钥：

```bash
# App 服务器密钥（对上传存储桶进行读取/写入）
tigris access-keys create "app-server"
tigris access-keys assign tid_app --bucket app-uploads --role Editor

# CDN/读取服务密钥（仅读取）
tigris access-keys create "cdn-reader"
tigris access-keys assign tid_cdn --bucket app-uploads --role ReadOnly

# 备份密钥（仅写入备份存储桶）
tigris access-keys create "backup-writer"
tigris access-keys assign tid_bak --bucket app-backups --role Editor
```

### 密钥轮换（零停机时间）

```bash
# 1. 创建新密钥
tigris access-keys create "production-app-key-v2"
tigris access-keys assign tid_new --bucket my-app-uploads --role Editor

# 2. 更新应用程序环境中的新密钥
# (部署时使用新的 TIGRIS_STORAGE_ACCESS_KEY_ID / SECRET)

# 3. 验证应用程序使用新密钥正常工作

# 4. 撤销旧密钥
tigris access-keys delete tid_old
```

### 列出和审计

```bash
# 列出所有访问密钥
tigris access-keys list

# 检查密钥可以访问哪些存储桶
tigris access-keys info tid_xxx
```

---

## CORS 配置

CORS 对于基于浏览器的上传（直接上传、预签名 PUT URL）是必需的。

### 设置 CORS 规则

```bash
tigris buckets cors set my-app-uploads --config cors.json
```

### 开发环境（本地主机）

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://localhost:3000", "http://localhost:5173"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag", "Content-Length"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

### 生产环境（特定域名）

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://myapp.com", "https://www.myapp.com"],
      "AllowedMethods": ["GET", "PUT", "HEAD"],
      "AllowedHeaders": ["Content-Type", "Content-MD5", "Content-Disposition"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 86400
    }
  ]
}
```

### 开发 + 生产组合

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": [
        "https://myapp.com",
        "https://www.myapp.com",
        "http://localhost:3000"
      ],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag", "Content-Length"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

### 任何来源（宽松配置）

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 86400
    }
  ]
}
```

**警告**：仅对真正公开的、仅读内容使用 `"*"` 来源。永远不要允许任何来源的 `PUT`/`DELETE`。

### 验证 CORS

```bash
# 检查当前的 CORS 配置
tigris buckets cors get my-app-uploads

# 使用 curl 测试
curl -I -H "Origin: https://myapp.com" \
  -H "Access-Control-Request-Method: PUT" \
  -X OPTIONS \
  https://my-app-uploads.t3.storage.dev/test
```

---

## 公共与私有存储桶

| 设置 | 谁可以读取 | URL 访问 | 使用场景 |
|---------|-------------|------------|---------|
| 私有（默认） | 仅认证请求 | 预签名 URL | 用户文档、敏感文件 |
| 公共 | 任何拥有 URL 的人 | 直接 URL | 静态资源、公共图片、CDN 内容 |

```bash
# 创建公共存储桶
tigris buckets create my-public-assets --public

# 创建私有存储桶（默认）
tigris buckets create my-private-docs
```

---

## 预签名 URL 安全性

### 最佳实践

| 参数 | 建议 |
|-----------|---------------|
| 过期时间（下载） | 大多数场景下为 5-60 分钟 |
| 过期时间（上传） | 5-15 分钟 |
| 范围 | 每个文件一个 URL，每个 URL 一个操作 |

```typescript
import { getPresignedUrl } from "@tigrisdata/storage";

// 短暂的下载 URL
const { data } = await getPresignedUrl("documents/report.pdf", {
  operation: "get",
  expiresIn: 300, // 5 分钟
});

// 短暂的上传 URL，带内容类型限制
const { data } = await getPresignedUrl("uploads/photo.jpg", {
  operation: "put",
  expiresIn: 600,
  contentType: "image/jpeg", // 客户端必须上传此类型
});
```

### 永远不要做

- 设置超过 24 小时的过期时间
- 为整个存储桶前缀生成预签名 URL
- 在公共渠道共享预签名 URL（它们是秘密）
- 使用预签名 URL 作为永久链接（使用公共存储桶 URL 代替）

---

## 环境变量安全性

```bash
# .env（永远不要提交此文件）
TIGRIS_STORAGE_ACCESS_KEY_ID=tid_xxx
TIGRIS_STORAGE_SECRET_ACCESS_KEY=tsec_yyy
```

```bash
# .gitignore（必须包含）
.env
.env.local
.env.*.local
```

对于 CI/CD，使用您平台的密钥管理：

```bash
# GitHub Actions
gh secret set TIGRIS_STORAGE_ACCESS_KEY_ID
gh secret set TIGRIS_STORAGE_SECRET_ACCESS_KEY

# Vercel
vercel env add TIGRIS_STORAGE_ACCESS_KEY_ID

# Fly.io
fly secrets set TIGRIS_STORAGE_ACCESS_KEY_ID=tid_xxx
```

---

## 安全审计清单

- [ ] **代码中无密钥** — 在您的代码库中搜索 `tid_` 和 `tsec_`
- [ ] **`.env` 在 `.gitignore` 中** — 密钥从未提交
- [ ] **密钥分配到存储桶** — 无未分配的全局访问密钥
- [ ] **角色与需求匹配** — 仅读服务使用 `ReadOnly` 角色
- [ ] **CORS 不过于宽松** — 无 `"*"` 来源带写方法
- [ ] **预签名 URL 过期时间短** — 大多数情况下少于 1 小时
- [ ] **撤销未使用的密钥** — 无来自前团队成员或旧部署的过期密钥
- [ ] **每个环境使用不同密钥** — 开发/测试/生产使用不同密钥

---

## 密钥泄露响应

如果访问密钥泄露（提交到 git、日志中泄露等）：

```bash
# 1. 立即撤销泄露的密钥
tigris access-keys delete tid_compromised

# 2. 创建新密钥
tigris access-keys create "replacement-key"
tigris access-keys assign tid_new --bucket my-bucket --role Editor

# 3. 更新所有部署中的新密钥
# (更新 .env、CI/CD 密钥、部署配置)

# 4. 审计访问 — 检查未授权的上传/下载
tigris ls t3://my-bucket --recursive -l | sort -k4 -r | head -50

# 5. 如果密钥提交到 git，轮换并考虑整个
#    git 历史已泄露 — 使用 git-filter-repo 删除它
```

---

## 严格规则

**总是**：每个环境和关注点创建单独的密钥 | 将密钥分配到特定存储桶，并使用最低必要角色 | 定期轮换密钥（建议每季度一次） | 生产环境中设置特定来源的 CORS | 使用短暂有效的预签名 URL

**永远不要**：将密钥提交到 git | 为所有环境使用单个密钥 | 生产环境中设置 `"*"` 带写方法的 CORS | 公开共享预签名 URL | 保留未使用的密钥

---

## 已知问题

| 问题 | 解决方法 |
|---------|-----|
| CORS 预检失败 | 确保 `AllowedOrigins` 包含您的确切来源（带协议） |
| 密钥轮换后“访问拒绝” | 确保新密钥分配到具有正确角色的存储桶 |
| 失去密钥 | 无法恢复 — 创建新密钥并重新分配 |
| 浏览器上传失败静默 | 确保 CORS 配置包含 `PUT` 在 `AllowedMethods` 中 |

---

## 相关技能

- **file-storage** — CLI 设置和访问密钥创建
- **tigris-s3-migration** — 迁移期间的 CORS 和凭证设置

## 官方文档

- Tigris: https://www.tigrisdata.com/docs/
