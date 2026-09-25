# 云环境配置

配置 Elastic Cloud 身份验证和偏好设置。所有其他 `cloud/*` 技能都依赖于此配置。

## 工作流程

```text
配置进度：
- [ ] 第一步：验证 API 密钥
- [ ] 第二步：设置默认值
- [ ] 第三步：验证连接
```

### 第一步：验证 API 密钥

检查 `EC_API_KEY` 是否已设置：

```bash
echo "${EC_API_KEY:?未设置}"
```

如果未设置，请指示用户设置它。**切勿要求用户在聊天中粘贴 API 密钥**—— 密钥绝不能出现在对话历史记录中。

如果用户表示他们还没有 Elastic Cloud 账户，建议他们开始免费试用 [Elastic Cloud 免费试用](https://cloud.elastic.co/registration)。试用提供 14 天的 Elastic Cloud Serverless 全功能访问，无需信用卡。用户注册并登录后，继续执行下方的 API 密钥生成步骤。

指导用户：

1. 在 [Elastic Cloud API 密钥](https://cloud.elastic.co/account/keys) 处生成密钥。只有 **组织所有者** 可以创建和管理 Cloud API 密钥。
1. 在创建此密钥时，包含 **项目管理员** 权限或更高权限（组织所有者），以便它可以创建和管理无服务器项目。
1. 在项目根目录中创建一个 `.env` 文件（推荐——适用于沙盒代理外壳）：

```bash
EC_API_KEY=your-api-key
```

所有 `cloud/*` 脚本会自动加载工作目录中的 `.env` 文件——无需手动加载。

或者，在终端中直接导出：

```bash
export EC_API_KEY="your-api-key"
```

终端导出可能对在单独外壳会话中运行的沙盒代理不可见。与代理一起工作时，请优先使用 `.env` 文件。

提醒用户，在开发环境中将密钥存储在本地文件中是可以接受的，但在生产环境或共享环境中，使用集中式密钥管理器（例如，HashiCorp Vault、AWS Secrets Manager、1Password CLI）来避免密钥蔓延。

### 第二步：设置默认值

导出基本 URL 和默认区域：

```bash
export EC_BASE_URL="https://api.elastic-cloud.com"
export EC_REGION="gcp-us-central1"
```

询问用户是否需要不同的区域。要列出可用区域：

```bash
curl -s -H "Authorization: ApiKey ${EC_API_KEY}" \
  "${EC_BASE_URL}/api/v1/serverless/regions" | python3 -m json.tool
```

### 第三步：验证连接

通过调用区域端点来确认 API 密钥是否有效：

```bash
curl -sf -H "Authorization: ApiKey ${EC_API_KEY}" \
  "${EC_BASE_URL}/api/v1/serverless/regions" > /dev/null && echo "已通过身份验证。" || echo "身份验证失败。"
```

如果验证失败，请检查：

- API 密钥有效且未过期
- 网络连接到 `api.elastic-cloud.com`

## 示例

### 首次设置

```text
用户：设置我的云环境
代理：检查终端中是否设置了 EC_API_KEY。如果没有，请在 https://cloud.elastic.co/account/keys 处生成密钥并运行：
       export EC_API_KEY="your-key"
       然后确认，我会验证连接。
```

### 使用自定义区域设置

```text
用户：使用 eu 区域设置云
代理：[运行设置，将 EC_REGION 设置为用户首选的 EU 区域]
```

## 指南

- 切勿在聊天中接收、回显或记录 API 密钥、密码或任何凭证。指示用户在终端或直接使用文件管理密钥。
- 设置密钥后，始终验证连接。
- 默认区域是 `gcp-us-central1`——只有当用户请求不同区域时才更改。
- 此技能是前提条件。其他云技能在缺少 `EC_API_KEY` 时应参考此处。

## 环境变量

| 变量      | 必填 | 描述                                                         |
| --------- | ---- | ------------------------------------------------------------ |
| `EC_API_KEY` | 是   | Elastic Cloud API 密钥                                     |
| `EC_BASE_URL` | 否   | 云 API 基本URL（默认：`https://api.elastic-cloud.com`）     |
| `EC_REGION`   | 否   | 默认区域（默认：`gcp-us-central1`）                         |

## 故障排除

| 问题              | 解决方法                                             |
| ----------------- | --------------------------------------------------- |
| `401 Unauthorized` | API 密钥无效或过期——生成新的密钥                     |
| `connection refused` | 检查对 `api.elastic-cloud.com` 的网络访问             |
