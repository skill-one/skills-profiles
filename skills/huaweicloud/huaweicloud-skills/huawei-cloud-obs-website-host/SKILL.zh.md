---
name: huawei-cloud-obs-website-host
description: 使用 Python SDK 和自定义域名配置华为云 OBS 静态网站托管。当用户需要启用或修复 OBS 网站托管、设置索引或错误页面、通过自定义域名公开现有存储桶供网站访问，或在华为云管理区域时通过华为云 DNS 连接该域名时使用。触发词包括：OBS 静态网站托管、网站托管、自定义域名解析。中文触发词包括：OBS 静态网站托管、网站托管、自定义域名解析。
---

# 华为云 OBS 网站托管

## 概述

使用华为云 OBS Python SDK 配置现有的华为云 OBS 存储桶以进行静态网站托管，并为该网站注册自定义域名。

当用户想要执行以下操作时，请使用此技能：

- 启用或修复 OBS 静态网站托管
- 设置索引文档或错误文档
- 通过 OBS 静态网站端点使网站可通过自定义域名访问
- 添加或修复自定义域名（包括适用情况下的华为云 DNS）
- 诊断托管 OBS 网站的 403、404 或 DNS 问题

## 理想状态

- 存储桶已启用静态网站托管。
- 存储桶可以从网站端点提供 `index.html`。
- 匿名用户可以读取网站内容。
- 缺失路径会返回配置的错误页面或干净的 404。
- 自定义域名已注册并通过 DNS 解析到 OBS 网站端点。自定义域名是**必需**的——出于安全合规要求，默认的 OBS 存储桶域名不允许用于在线对象预览。
- 直至自定义域名在存储桶上注册并正确解析，设置才被视为完成。
- 使用的是 OBS 网站端点，而不是常规的存储桶 API 端点。
- 403 通常有两个常见原因：存储桶或对象未启用匿名/公开读取，或用于 OBS 操作的 AK/SK 缺少必要的 IAM 权限。
- 404 通常意味着索引文档名称或上传路径错误。

## 安全合规：自定义域名要求

根据华为云安全合规要求，OBS 存储桶默认域名（`<bucket_name>.obs.<region>.myhuaweicloud.com`）**禁止**用于存储桶内对象的在线预览。因此，静态网站托管**必须**使用自定义域名。

如果用户没有准备自定义域名：

1. 指导用户通过 [华为云域名注册服务](https://www.huaweicloud.com/product/domain.html) 或其他常见域名注册网站注册域名。
2. 对于中国大陆地区的用户，域名必须完成 **ICP 备案** 才能用于网站托管。
3. 仅在域名注册（如适用，则完成备案）后，才应继续静态网站托管配置。

> **重要提示**：在确认自定义域名先决条件之前，不要继续静态网站托管配置。即使在测试环境中，默认的 OBS 域名也不是网站访问的有效替代方案。

## 必需输入

在做出更改之前收集这些信息：

- `region`
- `bucket_name`
- `custom_domain` (**必需**——参见上述安全合规部分)
- `index_document` (可选，默认：`index.html`)
- `error_document` (可选)
- `dns_zone` 或 DNS 账户上下文 (可选；仅在用户希望在此运行中更改华为云 DNS 时需要)

假设用户已上传静态网站文件。

## 依赖项

该技能依赖于以下运行时/工具组件：

- Python 3.10+ (用于 `scripts/set_obs_website_sdk.py` 和 `scripts/verify_obs_website.py` 所需)
- 华为 OBS Python SDK 包：`esdk-obs-python`
- `obsutil` (用于生成和维护 `.obsutilconfig` 凭证配置)
- 华为云 AK/SK 凭证 (来自 `.obsutilconfig`)
- 到 OBS 端点和网站端点的网络访问
- `hcloud` CLI (仅在技能管理华为云 DNS 记录操作时需要)
- dig / nslookup (可选)

安装命令：

```bash
pip install esdk-obs-python
```

## hcloud CLI 参考

当需要 hcloud CLI 或 obsutil 安装和配置时，加载 `references/cli-installation-guide.md`。
当创建或管理 OBS 静态网站自定义域名的 DNS CNAME 记录时，加载 `references/hcloud-dns-obs-website.md` (使用 hcloud `DNS CreateRecordSet` 命令的逐步指南)。

安全提示：

- 不要在脚本或提交的文件中硬编码 AK/SK。
- 对于 SDK 脚本，优先使用环境变量；对于 CLI 使用，使用安全的本地配置文件存储。

## obsutil 配置依赖项

当需要 obsutil 安装或 `.obsutilconfig` 设置指导时，加载 `references/cli-installation-guide.md`。

Python SDK 辅助脚本 (`scripts/set_obs_website_sdk.py`) 默认从以下位置读取凭证：

1. CLI 标志 (`--access-key`, `--secret-key`, `--security-token`)
2. 环境变量 (`HW_ACCESS_KEY`, `HW_SECRET_KEY`, `HW_SECURITY_TOKEN`)
3. `.obsutilconfig`

如果所有来源中的 `ak`/`sk` 为空，脚本必须停止并要求用户在 `.obsutilconfig` 中填写缺失的密钥（或提供 CLI/环境凭证）。

凭证检查规则：

- 仅报告密钥的存在/缺失 (`ak`, `sk`, `securitytoken`)。
- 检查期间绝不能打印凭证值。
- 绝不向控制台打印来自 `.obsutilconfig` 的完整行。
- 将控制台输出视为模型上下文；任何泄露的值都是安全事件。

安全检查示例（仅状态，无密钥值）：

Linux/macOS：

```bash
CFG="${HOME}/.obsutilconfig"
if [ ! -f "$CFG" ]; then
  echo "obsutilconfig_exists=false"
  echo "ak_configured=false"
  echo "sk_configured=false"
  echo "securitytoken_configured=false"
else
  awk -F= '
    BEGIN { ak=0; sk=0; st=0 }
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*(ak|access_key_id)[[:space:]]*=/ { if ($2 ~ /[^[:space:]]/) ak=1 }
    /^[[:space:]]*(sk|secret_access_key)[[:space:]]*=/ { if ($2 ~ /[^[:space:]]/) sk=1 }
    /^[[:space:]]*(securitytoken|security_token|token)[[:space:]]*=/ { if ($2 ~ /[^[:space:]]/) st=1 }
    END {
      print "obsutilconfig_exists=true"
      print "ak_configured=" (ak ? "true" : "false")
      print "sk_configured=" (sk ? "true" : "false")
      print "securitytoken_configured=" (st ? "true" : "false")
    }
  ' "$CFG"
fi
```

Windows (PowerShell):

```powershell
$cfg = Join-Path $HOME ".obsutilconfig"
if (-not (Test-Path $cfg)) {
  "obsutilconfig_exists=false"
  "ak_configured=false"
  "sk_configured=false"
  "securitytoken_configured=false"
} else {
  $lines = Get-Content $cfg
  $ak = $false; $sk = $false; $st = $false
  foreach ($line in $lines) {
    if ($line -match '^\s*#') { continue }
    if ($line -match '^\s*(ak|access_key_id)\s*=\s*(\S.*)$') { $ak = $true }
    if ($line -match '^\s*(sk|secret_access_key)\s*=\s*(\S.*)$') { $sk = $true }
    if ($line -match '^\s*(securitytoken|security_token|token)\s*=\s*(\S.*)$') { $st = $true }
  }
  "obsutilconfig_exists=true"
  "ak_configured=$ak"
  "sk_configured=$sk"
  "securitytoken_configured=$st"
}
```

不要使用：

- `cat ~/.obsutilconfig`
- `grep -E "ak|sk|token" ~/.obsutilconfig`

## 脚本使用目的

默认情况下，使用捆绑的脚本执行它们构建的任务：

- `scripts/set_obs_website_sdk.py` 应用或更新存储桶网站配置并注册所需的自定义域名。每当任务是要启用、修复或更改 OBS 静态网站托管设置时，使用它。
- `scripts/verify_obs_website.py` 验证发布的网站端点。在执行任何网站配置更改后使用它，并且在用户询问网站是否可达或排查 403/404 行为时也使用它。
- 不要用临时的单次代码替换这些脚本，除非脚本本身损坏并必须修补。
- 使用脚本以在运行之间保持凭证处理、SDK 对象构建和验证行为的一致性。

## 工作流程

1. 验证 Python 运行时和 OBS SDK 是否可用（如果缺少，则运行 `pip install esdk-obs-python`）。
2. 验证自定义域名先决条件（参见 **安全合规** 部分）：
   - 确认用户提供了 `custom_domain`。
   - 如果用户没有域名，指导他们到 [华为云域名注册](https://www.huaweicloud.com/product/domain.html) 注册域名，并完成中国大陆地区的 **ICP 备案**。在此停止并等待用户完成此步骤。
   - 检查用户是否在华为云 DNS 或外部提供程序中管理 DNS。
   - 如果此运行中包含华为云 DNS 更改，请验证 `hcloud` 是否已安装并认证。
   - 如果 DNS 管理在华为云外部或在此运行之外，请明确收集该约束后再继续。
3. 验证在请求的区域中是否存在存储桶（使用下方的 **存储桶存在和区域检查方法**）。
4. 检查调用者是否有权限更新存储桶网站设置。
5. 检查网站文件是否允许匿名读取（使用下方的 **匿名读取检查方法**）。
6. 不要上传或修改网站内容对象（`index.html`、资源等）。假设内容已存在于存储桶中。
7. 通过运行 `scripts/set_obs_website_sdk.py` 并使用 `--custom-domain <domain>` 配置静态网站托管（如果未提供 `index_document`，则使用 `index.html`）。
   - 脚本的存在是为了保持 SDK 对象构建和凭证查找的一致性。
   - 使用它而不是在响应中编写临时的 SDK 调用。
8. 通过脚本使用的 OBS SDK 路径在存储桶上注册所需的自定义域名：
   - `client.setBucketCustomDomain(bucket_name, custom_domain)` —— 即使 DNS CNAME 已存在，也需要此操作。
   - 如果在此运行中请求 DNS 记录更改，请创建指向 OBS 网站主机名的 DNS CNAME 记录并等待传播。（读取 `references/hcloud-dns-obs-website.md`）
   - 如果 DNS 管理在华为云外部或在此运行之外，请提供所需的 CNAME 目标，并明确指导用户在 OBS 自定义域名注册完成后使用外部 DNS 提供商创建或更新 CNAME 记录。
   - 对于外部管理的 DNS，请包含用户需要的手动交接细节：记录类型 `CNAME`、主机/名称、目标/值，以及验证命令，例如 `dig`。
9. 通过运行 `scripts/verify_obs_website.py --bucket-name <bucket_name> --region <region> [--domain <custom_domain>] [--index-document <name>]` 验证发布的网站。
   - 如果用户提供了自定义域名，最终验证**必须**使用该自定义域名通过 `--domain <custom_domain>`。
   - 仅在临时检查或未提供自定义域名时使用默认的 OBS 主机名。
10. 确认根路径返回主页（HTTP 200）。
11. 确认缺失路径返回配置的错误行为（HTTP 404 或配置的错误页面）。
12. 验证 DNS 解析 (`dig` / `nslookup`) 和通过用户提供的自定义域名的 HTTP 访问。当请求中包含自定义域名时，不要仅基于默认的 OBS 主机名就视为设置完成。

## 存储桶存在和区域检查方法

在网站配置之前，使用 `verify_obs_website.py` 运行只读 SDK 检查。

```bash
python scripts/verify_obs_website.py \
  --bucket-name "<bucket_name>" \
  --region "<region>" \
  --index-document "<index_document>"
```

`obs endpoint` 自动构建为 `https://obs.<region>.myhuaweicloud.com`。

通过/失败规则：

- `PASS`：`headBucket` 为 `2xx` 且区域匹配（或区域无法返回但存储桶使用 `2xx` 可达）。
- `FAIL`：`headBucket` 非 `2xx`，`getBucketLocation` 非 `2xx`，或明确区域不匹配。

## 匿名读取检查方法

使用针对 OBS 网站端点的匿名 HTTP 请求（无需 AK/SK）作为事实来源。

1. 验证器自动构建默认网站 URL：
   - `http://<bucket_name>.obs.<region>.myhuaweicloud.com`
2. 运行捆绑验证器（首选）：

```bash
python scripts/verify_obs_website.py \
  --bucket-name "<bucket_name>" \
  --region "<region>" \
  --domain "<custom_domain>" \
  --index-document "<index_document>"
```

3. 如果用户未提供自定义域名，请验证默认的 OBS 网站端点：

```bash
python scripts/verify_obs_website.py \
  --bucket-name "<bucket_name>" \
  --region "<region>" \
  --index-document "<index_document>"
```

4. 如果需要快速的单个文件检查，请运行：

```bash
site_url="http://<custom_domain>"
curl -s -o /dev/null -w "%{http_code}\n" "$site_url/<index_document>"
```

通过/失败规则：

- `root_path` 和 `index_document` 上 `200`：匿名读取正常工作。
- `403`：视为两个必须向用户报告的可能问题：匿名/公开读取未启用（ACL/策略问题），或用于 SDK 验证/配置的 AK/SK 缺少必要的 IAM 权限。
- `404`：对象路径/名称问题（例如，`index.html` 缺失或密钥路径不匹配），不是匿名权限成功。

当出现 `403` 时，将设置视为失败，并告知用户两个常见可能性：

- 存储桶/对象未对网站访问公开读取
- AK/SK 缺少 OBS 操作所需的 IAM 权限

通过 `references/iam-policies.md` 提供修复措施。

## 响应格式

始终返回：

1. 输入摘要
2. 执行的操作
3. 验证结果
4. 如果任何操作失败，则提供修复步骤

当 DNS 外部管理时，还包含一个简短的 DNS 手动交接部分，告诉用户确切要使用哪个 CNAME 记录配置他们的提供程序。

## 安全规则

- 绝不打印密钥、AK/SK 或令牌。
- 直至网站端点验证通过，才声称成功。
- 如果用户提供了自定义域名，最终成功必须基于通过该自定义域名的验证，而不仅仅是默认的 OBS 主机名。
- 如果权限缺失，停止并报告缺失的功能。
- 如果 DNS 提供商所有权未指定，在假设 `hcloud` 步骤之前，询问区域是否在华为云 DNS 中管理或外部管理。
- 如果需要华为云 DNS 更改才能完成，但区域未知，请要求用户提供区域，而不是猜测。
- 不要使用常规的存储桶端点作为最终的网站结果。
- 如果存储桶名称包含点，请警告 HTTPS 访问可能存在问题。
- 如果用户需要 HTTPS 访问，必须通过 `https://` 验证成功（使用 `verify_obs_website.py --https`），这需要将证书绑定到自定义域名通过 `setBucketCustomDomain(..., certificateInfo=...)`。OBS 仅在自定义域名上支持 HTTPS，并且仅支持国际（通用）证书，不支持 SM（国家加密）证书。
- 绝不打印或回显通过 `--private-key` 传递的私钥材料。
- `obsutil` 仅允许用于管理 `~/.obsutilconfig`；不要用它来配置网站托管。
- 在此技能中不要执行任何对象上传操作。
- 特别是在验证期间，仅使用只读检查；绝不要上传测试文件。
- 对于外部管理的 DNS，不要在“DNS 外部”停止；提供用户完成设置所需的面向用户 CNAME 手动交接细节。

## 权限失败处理（必须）

当任何命令由于 IAM 权限错误失败时：

1. 阅读 `references/iam-policies.md`。
2. 向用户显示所需的权限列表和策略 JSON。
3. 指导用户创建自定义 IAM 策略并在华为云 IAM 控制台授予权限。
4. 暂停执行并等待用户确认权限已授予。

## 参考

加载 `references/obs-python-sdk-website.md` 以获取网站托管**和**自定义域名注册的 SDK 方法使用说明 (`setBucketCustomDomain`)。
加载 `references/iam-policies.md` 以获取所需的 IAM 操作和策略 JSON。
加载 `references/hcloud-dns-obs-website.md` 以获取通过华为云 DNS (`hcloud` CLI) 为自定义域名创建/管理 DNS CNAME 的逐步指南，包括区域查找、记录创建和验证。

> **已知陷阱**：esdk-obs-python >= 3.x 中的 `setBucketWebsite` API 使用 `WebsiteConfiguration` 模型对象，**不是**像 `indexDocumentSuffix` 这样的关键字参数。始终导入 `WebsiteConfiguration`、`IndexDocument` 和 `ErrorDocument` 并正确构建它们。

## 脚本

仅用于重复性检查和验证。保持命令输出人类可读，并专注于成功/失败。

- `scripts/set_obs_website_sdk.py <bucket_name> <endpoint> --custom-domain <domain> [--index-document <name>] [--error-document <name>]` 通过 OBS SDK 应用静态网站托管设置，注册所需的自定义域名，并从 CLI 参数、环境变量或 `~/.obsutilconfig` 中读取凭证。OBS 可通过 `setBucketCustomDomain(..., certificateInfo=...)` 在自定义域名上支持 HTTPS。要绑定证书，请使用 `--certificate-name` 与 `--certificate` + `--private-key`（直接 PEM）或 `--certificate-id`（CCM 证书）之一配合。仅支持国际（通用）证书，不支持 SM（国家加密）证书。
- `scripts/verify_obs_website.py --bucket-name <name> --region <region> [--domain <custom_domain>] [--index-document <name>] [--https] [--json]` 验证端点的 DNS/HTTP 行为，并执行只读存储桶存在性 + 区域检查（`headBucket` + `getBucketLocation`）。如果提供 `--domain`，则该自定义域名是最终验证目标；否则会自动构建默认网站 URL 为 `http://<bucket>.obs.<region>.myhuaweicloud.com`。添加 `--https` 可验证端点通过 TLS（通常与已绑定证书的自定义域名一起使用）。OBS API 端点保持为 `https://obs.<region>.myhuaweicloud.com`。它会打印结构化部分（`输入摘要`、`执行的操作`、`验证结果`、`修复步骤`），以便代理响应可以直接复用它们。

## 验证规则

加载 `references/verification-method.md` 获取验证规则。
