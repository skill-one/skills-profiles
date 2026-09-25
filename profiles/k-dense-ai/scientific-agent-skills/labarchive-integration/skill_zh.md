# LabArchives 集成

仅从当前官方方法页面使用 LabArchives API。公共文档是一个共享笔记本，不是版本化的 SDK 参考，因此在实施远程操作之前，请立即验证特定页面。

## 选择正确的接口

不要组合这些接口：

- **遗留 ELN API**：笔记本树、条目、附件、用户、搜索、导出和站点许可功能。它使用区域 `*api.labarchives.com` 主机、`/api/<class>/<method>` 路径、对许多响应使用 XML，并使用签名查询参数。
- **库存 API v1**：库存、项目类型、订单、存储位置和供应商。它记录相对 `/public/v1/...` 路径、JSON 架构和签名的 `X-LabArchives-*` 请求头。
- **产品集成**：Jupyter、REDCap、Protocols.io、GraphPad Prism、SnapGene、Geneious 等是特定于产品的 UI 或文件工作流。它们不是 LabArchives OAuth 2.0 API 的证明。

在编写 API 代码之前，请阅读 [`references/api_reference.md`](references/api_reference.md)，在自动化宣传的集成之前，请阅读 [`references/integrations.md`](references/integrations.md)。

## 访问和凭证

LabArchives ELN 开发者 API 访问是一项企业功能。当前的库存 FAQ 将库存 API 访问限制为企业和企业 Plus 许可证持有人，并需要一个具有 API 权限的库存帐户。请联系机构的 LabArchives 团队或 LabArchives 支持以获取访问权限和随附的开发文档。

下面的环境名称是此技能的约定，不是供应商定义的标准：

- `LABARCHIVES_ELN_API_URL` — 一个以 `/api` 结尾的确切区域 ELN API URL
- `LABARCHIVES_ACCESS_KEY_ID` — LabArchives 发布的 Access Key ID (`akid`)
- `LABARCHIVES_ACCESS_PASSWORD` — HMAC 签名密钥
- `LABARCHIVES_USER_ID` — 可选的绑定到该 Access Key ID 的持久 UID
- `LABARCHIVES_INVENTORY_LAB_ID` — 库存请求所需的

将密钥保存在进程环境或批准的密钥管理器中。不要将它们放在 YAML、源代码、命令行参数、提示、日志、笔记本或提交的 `.env` 文件中。捆绑的工具永远不会搜索 `.env` 文件。

从此技能目录：

```bash
uv run scripts/setup_config.py regions
uv run scripts/setup_config.py check --require-user-id
```

`setup_config.py` 仅验证端点结构和命名变量的存在；它不会进行身份验证、持久化或打印凭证。请参阅 [`references/authentication_guide.md`](references/authentication_guide.md)。

## 区域端点

浏览器登录主机和 API 主机是不同的。当前的官方 ELN API 概览目前列出了美国/其他地区、澳大利亚/新西兰、英国、英国以外的欧洲和加拿大 API 主机。帮助中心单独列出了五个区域浏览器登录主机。

使用 `setup_config.py regions` 获取当前允许列表，并使用身份验证指南中的完整表格。永远不要从浏览器登录 URL 构建 API URL。

此更新文档检索的公共库存 v1 页面会检索相对路径，但不是完整的区域绝对基础 URL 表。从机构/供应商文档中获取该基础 URL，而不是从库存登录主机猜测。

## 身份验证模型

### ELN 请求

官方算法完全记录：

1. 将 `expires` 设置为当前 Unix 纪元时间（以毫秒为单位），如有必要，根据服务器时钟差异进行调整。尽管其名称如此，但它不是一个未来的过期时间。
2. 连接，不要分隔符：
   `<Access Key ID><API 方法名称><expires>`。
3. 使用 Access Password 作为密钥计算 HMAC-SHA-512。
4. 对摘要进行 Base64 编码。
5. 对该签名进行 URI 编码，并将 `akid`、`expires` 和 `sig` 作为记录的查询参数发送。

对于普通的 ELN 调用，签名输入仅是方法名称，而不是 API 类。用户授权是一个记录的特殊情况：对 `api_user_login` 重定向进行签名使用未编码的重定向 URI，而不是方法名称。

### 库存 API v1 请求

库存共享 HMAC 算法，但签名确切的相对路由，包括解析的路径参数，不包括查询字符串。其身份验证页面记录了这些头：

- `X-LabArchives-UId`
- `X-LabArchives-AKId`
- `X-LabArchives-LabId`
- `X-LabArchives-Signature`
- `X-LabArchives-Expires`

为每个请求创建一个新的签名。不要将 ELN 查询身份验证移动到库存头或库存头移动到 ELN 调用。

## 本地请求规划

`scripts/entry_operations.py` 是故意无网络的。它实现了记录的签名原语，并发出红acted JSON 计划，永远不会发出实时请求或可重用签名：

```bash
uv run scripts/entry_operations.py self-test
uv run scripts/entry_operations.py eln-plan \
  --api-class entries --api-method entry_info
uv run scripts/entry_operations.py inventory-plan \
  --path /public/v1/users/me
```

在需要时，将 `create_signature`、`build_eln_auth_params` 或 `build_inventory_headers` 函数导入机构审核的代码中。将返回的身份验证材料直接传递给 HTTP 客户端；永远不要打印或持久化它。

在任何远程写入之前：

1. 打开确切的官方方法页面，并验证动词、路径、参数、正文和响应架构。
2. 生成一个红acted 身份标识符和敏感值的干运行计划。
3. 确认目标区域、笔记本/实验室和用户可见效果。
4. 在发送之前需要明确批准。
5. 重新阅读并验证结果对象；当方法记录响应正文时，不要仅从 HTTP 200 推断成功。

捆绑的脚本不会执行远程写入。

## 本地 LA 容器检查

**LA 容器** 是一个包含 `lamanifest.xml`、应用程序文件和可选的预览/索引文件的 ZIP 文件。它与笔记本备份不是同义词。在不提取它的情
