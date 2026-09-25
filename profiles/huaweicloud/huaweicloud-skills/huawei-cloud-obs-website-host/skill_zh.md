# 华为云OBS网站托管

## 概述

使用华为云OBS Python SDK配置现有的华为云OBS存储桶以进行静态网站托管，并为该站点注册自定义域名。

当用户想要执行以下操作时，请使用此技能：

- 启用或修复OBS静态网站托管
- 设置索引文档或错误文档
- 通过OBS静态网站端点使站点可通过自定义域名访问
- 添加或修复自定义域名，包括适用情况下的华为云DNS
- 诊断托管OBS站点的403、404或DNS问题

## 理想状态

- 存储桶已启用静态网站托管。
- 存储桶可以从网站端点提供`index.html`。
- 匿名用户可以读取网站内容。
- 缺失路径会返回配置的错误页面或干净的404。
- 已注册自定义域名，并通过DNS解析到OBS网站端点。自定义域名是**必需**的——出于安全合规要求，默认的OBS存储桶域名不允许用于在线对象预览。
- 直至自定义域名在存储桶上注册并正确解析，设置才被视为完成。
- 使用的是OBS网站端点，而不是常规的存储桶API端点。
- 403通常有两个常见原因：存储桶或对象未启用匿名/公开读取，或用于OBS操作的AK/SK缺乏必要的IAM权限。
- 404通常意味着索引文档名称或上传路径不正确。

## 安全合规：自定义域名要求

根据华为云安全合规要求，OBS存储桶默认域名（`<bucket_name>.obs.<region>.myhuaweicloud.com`）**禁止**用于存储桶内对象的在线预览。因此，静态网站托管**必须**使用自定义域名。

如果用户没有准备自定义域名：

1. 指导用户通过[华为云域名注册服务](https://www.huaweicloud.com/product/domain.html)或其他常见的域名注册网站注册域名。
2. 对于中国大陆地区的用户，域名必须完成**ICP备案（网站备案）**后才能用于网站托管。
3. 只有在域名注册（如适用，则完成备案）后，才应继续静态网站托管配置。

> **重要提示**：在确认自定义域名先决条件之前，不要继续静态网站托管配置。即使在测试环境中，默认的OBS域名也不是网站访问的有效替代方案。

## 必需的输入

在做出更改之前收集这些信息：

- `region`
- `bucket_name`
- `custom_domain` (**必需**——见上文安全合规部分)
- `index_document` (可选，默认：`index.html`)
- `error_document` (可选)
- `dns_zone` 或DNS账户上下文 (可选；仅在用户希望在此运行中更改华为云DNS时需要)

假设静态网站文件已由用户上传。

## 依赖项

该技能依赖于以下运行时/工具组件：

- Python 3.10+ (用于`scripts/set_obs_website_sdk.py`和`scripts/verify_obs_website.py`)
- 华为OBS Python SDK包：`esdk-obs-python`
- `obsutil` (用于生成和维护`.obsutilconfig`凭证配置)
- 华为云AK/SK凭证（来自`.obsutilconfig`）
- 到OBS端点和网站端点的网络访问权限
- `hcloud` CLI (仅在技能管理华为云DNS记录操作时需要)
- dig / nslookup (可选)

安装命令：

```bash
pip install esdk-obs-python
```

## hcloud CLI参考

当需要hcloud CLI或obsutil安装和配置时，加载`references/cli-installation-guide.md`。
当创建或管理OBS静态网站自定义域名的DNS CNAME记录时，加载`references/hcloud-dns-obs-website.md`（使用hcloud `DNS CreateRecordSet`命令的逐步指南）。

安全提示：

- 不要在脚本或提交的文件中硬编码AK/SK。
- 偏好使用环境变量进行SDK脚本，并使用安全的本地配置文件进行CLI使用。

## obsutil配置依赖

当需要obsutil安装或`.obsutilconfig`设置指导时，加载`references/cli-installation-guide.md`。

Python SDK辅助脚本（`scripts/set_obs_website_sdk.py`）默认从以下位置读取凭证：

1. CLI标志（`--access-key`，`--secret-key`，`--security-token`）
2. 环境变量（`HW_ACCESS_KEY`，`HW_SECRET_KEY`，`HW_SECURITY_TOKEN`）
3. `.obsutilconfig`

如果所有来源中的`ak`/`sk`为空，则脚本必须停止并要求用户在`.obsutilconfig`（或提供CLI/环境凭证）中填写缺失的密钥。

凭证检查规则：

- 仅报告密钥的存在/缺失（`ak`，`sk`，`securitytoken`）。
- 检查期间不要打印凭证值。
- 不要将`.obsutilconfig`的完整行打印到控制台。
- 将控制台输出视为模型上下文；任何泄露的值都是安全事件。

安全检查示例（仅状态，不包含秘密值）：

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

默认情况下，使用这些脚本执行它们构建的任务：

- `scripts/set_obs_website_sdk.py` 应用或更新存储桶网站配置并注册所需的自定义域名。无论何时需要启用、修复或更改OBS静态网站托管设置，都使用它。
- `scripts/verify_obs_website.py` 验证发布的网站端点。在执行任何网站配置更改后，以及当用户询问站点是否可访问或进行403/404行为故障排除时，使用它。
- 除非脚本本身损坏并必须修补，否则不要用一次性临时的代码替换这些脚本。
- 使用这些脚本以保持凭证处理、SDK对象构建和验证行为在多次运行中保持一致。

## 工作流程

1. 验证Python运行时和OBS SDK是否可用（如果缺失，则运行`pip install esdk-obs-python`）。
2. 验证自定义域名先决条件（见**安全合规**部分）：
   - 确认用户提供了`custom_domain`。
   - 如果用户没有域名，指导他们到[华为云域名注册](https://www.huaweicloud.com/product/domain.html)注册域名，并完成中国大陆地区的**ICP备案（网站备案）**。在此停止并等待用户完成此步骤。
   - 检查用户是否在华为云DNS或外部提供程序中管理DNS。
   - 如果此运行中包含华为云DNS更改，请验证`hcloud`是否已安装和认证。
   - 如果DNS由外部管理或在此运行之外管理，请在继续之前明确收集该约束。
3. 验证在请求的区域中是否存在存储桶（使用下文的**存储桶存在和区域检查方法**）。
4. 检查调用者是否有权限更新存储桶网站设置。
5. 检查网站文件是否允许匿名读取（使用下文的**匿名读取检查方法**）。
6. 不要上传或修改网站内容对象（`index.html`、资源等）。假设内容已存在于存储桶中。
7. 通过运行`scripts/set_obs_website_sdk.py`并使用`--custom-domain <domain>`（如果未提供`index_document`，则使用`index.html`）配置静态网站托管：
   - 该脚本的存在是为了保持SDK对象构建和凭证查找的一致性。
   - 使用它而不是在响应中编写一次性SDK调用。
8. 通过脚本使用的OBS SDK路径在存储桶上注册所需的自定义域名：
   - `client.setBucketCustomDomain(bucket_name, custom_domain)`——即使DNS CNAME已存在，也需要此操作。
   - 如果在此运行中请求DNS记录更改，请创建一个解析到OBS网站主机名的DNS CNAME记录并等待传播。（读取`references/hcloud-dns-obs-website.md`）
   - 如果DNS由外部管理或在此运行之外管理，请提供所需的CNAME目标，并明确指导用户在OBS自定义域名注册完成后，使用外部DNS提供程序创建或更新CNAME记录。
   - 对于外部管理的DNS，包括用户需要的手动交接详细信息：记录类型`CNAME`、主机/名称、目标/值，以及验证命令（如`dig`）。
9. 通过运行`scripts/verify_obs_website.py --bucket-name <bucket_name> --region <region> [--domain <custom_domain>] [--index-document <name>]`验证发布的站点：
   - 如果用户提供了自定义域名，最终验证必须使用该自定义域名通过`--domain <custom_domain>`进行。
   - 仅在临时检查或未提供自定义域名时使用默认的OBS主机名。
10. 确认根路径返回主页（HTTP 200）。
11. 确认缺失路径返回配置的错误行为（HTTP 404或配置的错误页面）。
12. 验证DNS解析（`dig` / `nslookup`）和通过用户提供的自定义域名的HTTP访问。当请求中包含自定义域名时，不要仅基于默认的OBS主机名就认为设置完成。

## 存储桶存在和区域检查方法

在网站配置之前，使用`verify_obs_website.py`运行只读SDK检查。

```bash
python scripts/verify_obs_website.py \
  --bucket-name "<bucket_name>" \
  --region "<region>" \
  --index-document "<index_document>"
```

`obs endpoint`自动构建为`https://obs.<region>.myhuaweicloud.com`。

通过/失败规则：

- `PASS`：`headBucket`为`2xx`且区域匹配（或区域无法返回但存储桶可通过`2xx`访问）。
- `FAIL`：`headBucket`非`2xx`，`getBucketLocation`非`2xx`，或明确区域不匹配。

## 匿名读取检查方法

使用针对OBS网站端点的匿名HTTP请求（无需AK/SK）作为真实来源。

1. 验证器自动构建默认网站URL：
   - `http://<bucket_name>.obs.<region>.myhuaweicloud.com`
2. 运行捆绑验证器（首选）：

```bash
python scripts/verify_obs_website.py \
  --bucket-name "<bucket_name>" \
  --region "<region>" \
  --domain "<custom_domain>" \
  --index-document "<index_document>"
```

3. 如果用户没有提供自定义域名，请验证默认的OBS网站端点：

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

- `root_path`和`index_document`返回`200`：匿名读取正常工作。
- `403`：视为两个必须向用户报告的问题：匿名/公开读取未启用（ACL/策略问题），或用于SDK验证/配置的AK/SK缺乏必要的IAM权限。
- `404`：对象路径/名称问题（例如，`index.html`缺失或密钥路径不匹配），不是匿名权限成功。

当出现`403`时，将设置视为失败，并告知用户两个常见可能性：

- 存储桶/对象未对网站访问公开读取
- AK/SK缺乏用于OBS操作的必要IAM权限

通过`references/iam-policies.md`提供修复措施。

## 响应格式

始终返回：

1. 输入摘要
2. 执行的操作
3. 验证结果
4. 如果有任何失败，则提供修复步骤

当DNS由外部管理时，还包含一个简短的DNS手动交接部分，告诉用户他们需要使用提供程序配置哪个CNAME记录。

## 安全规则

- 不要打印秘密、AK/SK或令牌。
- 直至网站端点验证成功，才声明成功。
- 如果用户提供了自定义域名，最终成功必须基于通过该自定义域名的验证，而不仅仅是默认的OBS主机名。
- 如果权限缺失，停止并报告缺失的功能。
- 如果DNS提供程序所有权未指定，在假设`hcloud`步骤之前，询问区域是否在华为云DNS中管理或外部管理。
- 如果需要华为云DNS更改才能完成，但区域未知，请要求用户提供区域，而不是猜测。
- 不要使用常规的存储桶端点作为最终的网站结果。
- 如果存储桶名称包含点，请警告HTTPS访问可能存在问题。
- 如果用户需要HTTPS访问，必须通过`https://`（使用`verify_obs_website.py --https`）验证成功，这需要将证书绑定到自定义域名通过`setBucketCustomDomain(..., certificateInfo=...)`。OBS仅支持自定义域名上的HTTPS，且仅支持国际（通用）证书，不支持SM（国家加密）证书。
- 不要打印或回显通过`--private-key`传递的私钥材料。
- `obsutil`仅允许用于管理`~/.obsutilconfig`；不要用它来配置网站托管。
- 不要在此技能中执行任何对象上传操作。
- 特别是在验证期间，仅使用只读检查；永远不要上传测试文件。
- 对于外部管理的DNS，不要在“DNS是外部”时停止；提供用户完成设置所需的面向用户的CNAME手动交接详细信息。

## 权限失败处理（必须）

当任何命令由于IAM权限错误失败时：

1. 阅读`references/iam-policies.md`。
2. 向用户显示所需的权限列表和策略JSON。
3. 指导用户创建自定义IAM策略并在华为云IAM控制台授予权限。
4. 暂停执行并等待用户确认权限已授予。

## 参考

加载`references/obs-python-sdk-website.md`以获取网站托管**和自定义域名注册**的SDK方法使用说明（`setBucketCustomDomain`）。
加载`references/iam-policies.md`以获取所需的IAM操作和策略JSON。
加载`references/hcloud-dns-obs-website.md`以获取通过华为云DNS（`hcloud` CLI）为自定义域名配置DNS CNAME的逐步指南，包括区域查找、记录创建和验证。

> **已知陷阱**：esdk-obs-python >= 3.x中的`setBucketWebsite` API使用`WebsiteConfiguration`模型对象，**不是**像`indexDocumentSuffix`这样的关键字参数。始终导入`WebsiteConfiguration`、`IndexDocument`和`ErrorDocument`并正确构建它们。

## 脚本

仅用于重复检查和验证。保持命令输出人类可读，并专注于成功/失败。

- `scripts/set_obs_website_sdk.py <bucket_name> <endpoint> --custom-domain <domain> [--index-document <name>] [--error-document <name>]`通过OBS SDK应用静态网站托管设置，注册所需的自定义域名，并从CLI参数、环境变量或`~/.obsutilconfig`读取凭证。OBS支持通过`setBucketCustomDomain(..., certificateInfo=...)`在自定义域名上使用HTTPS。要绑定证书，请使用`--certificate-name`与`--certificate` + `--private-key`（直接PEM）或`--certificate-id`（CCM证书）之一结合。仅支持国际（通用）证书，不支持SM（国家加密）证书。
- `scripts/verify_obs_website.py --bucket-name <name> --region <region> [--domain <custom_domain>] [--index-document <name>] [--https] [--json]`验证端点DNS/HTTP行为，并执行只读存储桶存在+区域检查（`headBucket` + `getBucketLocation`）。如果提供`--domain`，则该自定义域名是最终验证目标；否则，它自动构建默认网站URL为`http://<bucket>.obs.<region>.myhuaweicloud.com`。添加`--https`以验证端点通过TLS（通常使用绑定到自定义域名的证书）。OBS API端点仍然是`https://obs.<region>.myhuaweicloud.com`。它打印结构化部分（`Input summary`，`Actions performed`，`Verification results`，`Remediation steps`），以便代理响应可以直接重用它们。

## 验证规则

加载`references/verification-method.md`以获取验证规则。
