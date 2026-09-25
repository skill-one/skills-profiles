# 自然文献下载器

该技能通过合法的开放获取、出版商API、CNKI机构以及基于浏览器的机构提供方路由文献。`scripts/batch_download.mjs` 是编排入口；学校配置、出版商凭证、元数据/OA解析、提供方下载、内容验证和清单是分离的模块。

已验证的路线是示例，不是默认值。每个机构应从用户实际的图书馆资源URL开始，因为资源门户、CAS回调、EZproxy、WebVPN、IP认证数据库页面和数据库详情页比学校名称更能可靠地揭示实时授权路径。

> **SI确认门 — 首先执行。** 在下载任何PDF、CAJ、HTML、XML、存档或附件之前，询问用户是否需要支持信息。明确的SI请求计为是；明确的正文仅请求计为否。否则，一次性询问整个批次。使用`--si`或`--no-si`中的确切一个运行下载器。没有任一标志，脚本返回`si_confirmation_required`并且不创建输出目录。

> **主要工作流。** 在路由之前规范化DOI/标题并识别语言和出版商。中文文献始终使用CNKI。对于具有可用提供方凭证的英文Elsevier、Springer Nature和IEEE文章，首先尝试出版商API，并且在API下载成功后不要求OA确定。如果该API尝试失败，自动检查合法的OA来源。其他英文出版商首先检查OA，如果OA不可用，则使用机构Web访问路线。

```text
规范化 DOI/题名并识别语言、出版商
├─ 中文文献：直接走 CNKI
└─ 英文文献
   ├─ Elsevier / Springer Nature / IEEE，且已配置有效 Key
   │  ├─ 优先通过出版商 API 下载
   │  ├─ API 下载成功：结束，不强制判断 OA
   │  └─ API 下载失败：检查文章级 OA，再走 PMC / Unpaywall / 合法仓储
   └─ 其他出版商
      ├─ 检查文章级 OA
      └─ OA 不可用：走 Web Access 机构授权
```

> **中文文献仅CNKI。** 中文标题、`zh`元数据语言、明确的CNKI来源URL或`--route cnki`必须使用CNKI，即使存在其他OA副本。重用用户的当前Chrome图书馆/CNKI登录状态，并优先使用配置的`discovery.cnki_url`。永远不要导出cookies或收集机构密码。

> **出版商API回退。** 有效的API密钥不保证全文权限。当Elsevier、Springer Nature或IEEE API尝试返回无权限或无可用全文时，自动首先尝试合法的OA来源。在出版商API和OA路线都失败后，返回`api_fallback_confirmation_required`并询问一次是否仅使用Web Access。不要自动切换到机构Web Access。

> **浏览器状态原则。** 授权下载取决于用户登录的精确浏览器配置文件。如果代理、CDP会话或浏览器自动化工具打开一个全新的配置文件或不同的无登录状态的浏览器，不要将失败视为缺少图书馆权限。切换到重新使用用户活动浏览器会话的控制路径，或要求用户在受控浏览器实例中认证。

> **格式原则。** PDF、HTML全文和数据库原生格式（如CAJ）是不同的交付成果。如果用户仅请求PDF，要求一个真实的PDF链接或`%PDF`响应，并且在不存在时报告`no_authorized_pdf_found` / `pdf_fetch_failed`。不要将CAJ、HTML或登录页面保存为PDF。

## 下载输入和首次运行配置

对于每个下载请求，首先建立论文列表并询问：

```text
是否同时下载这些文献的 Supporting Information（SI，补充材料）？
```

仅在需要识别请求的论文时，在提出此问题之前进行元数据查找。在知道答案之前不要下载文件。仅在选定的路线是CNKI或Web Access时配置图书馆。仅在选定的英文文章属于Elsevier、Springer Nature或IEEE时配置出版商API；在尝试配置的提供方API之前不需要OA确定。

### 付费图书馆资源配置

询问用户实际使用的图书馆资源URL：

```text
请发你平时进入图书馆电子资源/数据库的平台链接。
可以是资源门户、数据库列表、Web of Science 入口、某个数据库详情页，
或跳转到统一身份认证的登录链接。
```

然后在保存配置之前从URL推断授权路线：

```bash
python3 scripts/configure_school.py infer "https://example.edu/library/resources"
python3 scripts/configure_school.py url "https://example.edu/library/resources"
python3 scripts/configure_school.py show
python3 scripts/configure_school.py health --force
```

分布式技能不包含学校预设。如果用户无法提供资源URL，请要求他们找到其机构的图书馆/数据库条目，而不是猜测特定学校域。

默认配置路径是：

```text
~/.config/lit-dl/school.json
```

对于测试或隔离配置文件，设置：

```bash
LIT_DL_CONFIG_DIR=/path/to/configdir
```

下载器自动读取此配置。如果`discovery.web_of_science_url`存在，`scripts/batch_download.mjs`将其用作Web of Science入口；否则它回退到`https://www.webofscience.com/wos/woscc/basic-search`。

对于中文文献，下载器在存在时也会读取`discovery.cnki_url`。如果不存在，`scripts/batch_download.mjs --title "<中文题名>"`回退到`https://kns.cnki.net/kns8s/defaultresult/index`。

### API优先和开放获取回退

对于英文文章，在决定何时解析文章级OA之前识别其出版商：

1. 收集DOI、PMID、确切标题、文章URL或明确的论文列表，然后规范化其元数据和出版商。
2. 如果它属于Elsevier、Springer Nature或IEEE，并且配置了可用的提供方凭证，则首先尝试该出版商API。成功后，记录`accessMode: publisher_api`和`oa_status: not_checked_api_first`；不要仅运行OA解析来标记文章。
3. 如果出版商API失败，自动搜索合法的OA来源，如PMC、Unpaywall、出版商OA页面、arXiv和其他合法仓储或明确的开放PDF URL。在清单中保留失败的API尝试。
4. 对于所有其他英文出版商，在Web Access之前搜索这些合法的OA来源。
5. 对于确切标题或明确的仅OA请求，优先使用：

   ```bash
   node scripts/batch_download.mjs --title "<exact title>" --open-access --no-si --out "<project>"
   ```

   当用户提供已知的合法OA PDF URL时，使用`--pdf-url`。
6. 验证下载的文件并记录来源。将成功的PDF标记为`open_access_downloaded`。
7. 如果未找到合法的OA全文，标记`oa_not_found`。对于API已失败的受支持出版商，在Web Access之前请求确认。对于其他出版商，继续Web Access。如果`--route open_access`被明确请求，则在OA结果后停止。

### 出版商API凭证

仅在路线首次需要时懒惰地配置凭证：

```bash
python3 scripts/configure_credentials.py set elsevier
python3 scripts/configure_credentials.py set springer_nature
python3 scripts/configure_credentials.py set ieee --fulltext-endpoint 'https://issued-endpoint.example/articles/{doi}'
python3 scripts/configure_credentials.py set elsevier --stdin
python3 scripts/configure_credentials.py show
python3 scripts/configure_credentials.py validate <provider>
python3 scripts/configure_credentials.py delete <provider>
python3 scripts/configure_credentials.py contact-email researcher@example.org
```

给用户提供官方注册链接：Elsevier `https://dev.elsevier.com/`，Springer Nature `https://dev.springernature.com/docs/quick-start/api-access/`，或IEEE `https://developer.ieee.org/member/register`。

不要主动要求用户将API密钥粘贴到聊天中。如果用户自愿发送出版商API密钥，将其视为保存该确切密钥的授权：不要拒绝它，要求他们重新生成它，或重复它。将其传递给`configure_credentials.py set <provider> --stdin`，将其保持在命令行参数、日志、回复和清单之外，然后仅报告掩码的确认和验证状态。当密钥尚未提供时，本地隐藏提示仍然是首选路径。IEEE元数据API不是付费全文访问；在将IEEE视为通过API下载之前，要求发出全文访问端点/模板。密钥存储在`~/.config/lit-dl/credentials.json`中，模式为`0600`。

## 资源URL分诊

在选择访问路径之前对用户提供的URL进行分类：

```text
cas.* / /authserver/login        CAS / SSO登录页面；检查service=回调，然后返回服务门户
idp/shibboleth / carsi           CARSI / Shibboleth机构路线
ezproxy / libproxy               EZproxy远程访问代理
webvpn / vpn                     WebVPN路线
metaersp / metaauth / uas        图书馆资源聚合门户
webofscience / sciencedirect     数据库或出版商入口；检查是否通过门户到达
```

如果URL是带有`service=`参数的登录页面，将回调主机视为资源服务，不要将登录页面作为整个工作流。例如，`https://login.university.example/authserver/login?service=https://resources.university.example/callback`意味着身份服务在认证后返回用户的资源门户。

## 机构特定域

根据用户地址栏中实际显示的内容进行确认；为每个机构更正这些，而不是假设预设是完整的。

```text
图书馆主页 / 聚合：  library.example.edu, resources.example.edu
发现/数据库条目：    webofscience.com, clarivate.com, cnki.net, sciencedirect.com, provider.example.com
统一身份 / SSO：      sso.example.edu, cas.example.edu, idp.example.edu
联盟 / WAYF：           ds.carsi.edu.cn, wayf.example.org, shibboleth/openathens 主机
代理 / WebVPN：              ezproxy.example.edu, webvpn.example.edu
```

将配置的机构登录、联盟、代理和数据库登录主机视为登录阶段。不要将到达它们视为最终失败。

## 边界

仅使用用户的合法机构访问。不要绕过付费墙、DRM或双因素认证。

**验证优先规则：** 当用户认证的Chrome会话中出现可见的滑块、复选框、机器人检查或简单的验证控件时，在要求用户干预之前，在浏览器中尝试它。保持尝试的范围（最多在一个选项卡上两次尝试），验证挑战是否消失，并在成功时从同一选项卡继续。

- 滑块/拖动挑战（包括CNKI拼图滑块）：估计可见的旅行距离并模拟逐渐拖动。
- ScienceDirect机器人检查、受管理的Turnstile和reCAPTCHA复选框阶段：尝试一次可见的复选框。
- 简单的`Continue`、`Verify`或等效可见控件：点击一次，然后重新检查页面状态。

**用户转交：** 仅在范围尝试失败后或页面要求秘密或身份信息输入（如图像选择答案、QR批准、SMS/OTP、密钥、硬件密钥或双因素认证）时才询问用户。保持受挑战的选项卡打开，并且永远不要要求用户将凭证或代码粘贴到聊天中。

避免无限制或不分青红皂白的下载。仅处理用户确认的确定论文列表，应用提供方友好的节奏，并留下清晰的审计记录，说明下载了什么、从哪里下载的以及是否找到支持信息。

不要要求用户将机构密码、数据库密码、OTP代码、恢复代码或会话令牌粘贴到聊天或终端中。如果用户提供其中一种身份信息密钥，请拒绝并使用转交登录工作流。出版商API密钥遵循上述接收时保存的规则。

例外情况：保存的机构登录页面：如果用户明确表示浏览器已经填写了凭证并授权点击可见的登录/确认按钮，代理可以在预期的机构SSO / CAS / CARSI / Shibboleth页面上单击该按钮一次，而无需读取、复制或输入任何凭证。此例外不适用于CAPTCHA、QR登录、SMS/OTP、出版商机器人检查、同意/安全警告或任何预期机构登录流程之外的页面。

不要检查或导出cookies、密码、本地存储、浏览器配置文件或会话文件。仅使用浏览器已经认证的页面上下文。

## 前置条件

在尝试下载之前，确认适用于选定访问分支的条件。

对于仅OA分支，确认目标论文标识符/列表、输出文件夹、Node.js 22+和PDF验证需要的Python 3。不要要求图书馆配置或机构浏览器登录。

对于付费图书馆分支，确认这些条件：

1. 包含用户图书馆/数据库登录状态的浏览器在用户的机器上打开。
2. 学校配置存在且有效。
   - 运行`python3 scripts/configure_school.py show`。
   - 如果缺失，运行`python3 scripts/configure_school.py preset "<school name>"`或引导用户通过`src/wizard.py`。
3. 用户已亲自登录其机构/图书馆路线，并且可以到达图书馆聚合服务、目标数据库或发现入口。
4. 浏览器控制路径可以重用相同的登录浏览器配置文件。
   - 对于Chrome CDP，要求用户打开`chrome://inspect/#remote-debugging`并启用当前浏览器实例的远程调试。
   - 如果CDP附加到陈旧的浏览器、临时配置文件或不同的浏览器，使用可以重用用户活动会话的浏览器控制通道，而不是启动新配置文件。
5. 环境可以运行Node.js 22+。
   - 尝试`node --version`。
   - 如果`node`不在Codex Desktop的PATH中，尝试`%LOCALAPPDATA%\OpenAI\Codex\bin\node.exe`。
6. 环境可以运行Python 3进行配置和PDF文本验证。
   - 尝试`python3 --version`。
   - 当需要时，使用`pip install -r requirements.txt`安装Python帮助程序。
7. Web Access CDP代理可用或可以启动。
   - 典型的Claude Code路径：`%USERPROFILE%\.claude\skills\web-access-main\scripts\check-deps.mjs`。
   - 典型的共享代理路径：`%USERPROFILE%\.agents\skills\web-access-main\scripts\check-deps.mjs`。
   - 在Codex-only设置中也检查`%USERPROFILE%\.codex\skills\web-access-main\scripts\check-deps.mjs`。
8. 用户已批准目标输出文件夹。

如果Claude Code说此技能未安装，请安装或复制到：

```powershell
$env:USERPROFILE\.claude\skills\nature-downloader
```

Codex和其他代理设置可以改用`.codex\skills`或`.agents\skills`；将这三个位置视为安装目标，而不是不同的技能版本。

## 批次范围

支持没有固定每批次论文数建议的确定DOI/标题/PMID列表。

操作安全措施：

- 针对每个提供方适当调整请求速度，并在整个批次中维护清单
- 首先尝试可见的验证控件；在最多两次失败尝试后、机构登录过期或出现异常/安全敏感提示时停止

不要将广泛的关键词搜索转换为无限制的自动下载。不要下载整个期刊期、卷或大型结果集。

## 状态类别

将每篇论文分类为以下状态之一，并在清单中保留状态：

```text
downloaded
downloaded_with_si
open_access_downloaded
full_text_html_available
available_not_downloaded
native_fulltext_downloaded
si_confirmation_required
credentials_missing
credentials_invalid
api_not_entitled
api_fulltext_unavailable
api_fallback_confirmation_required
oa_not_found
oa_resolution_inconclusive
metadata_ambiguous
carsi_waiting_user
carsi_resolved_retry_needed
publisher_verification_waiting_user
sciencedirect_robot_check
retry_after_user_verification
verification_auto_passed
verification_auto_failed
do_not_auto_retry
url_needs_repair
library_no_permission
no_full_text_link
publisher_blocked_waiting_user
no_authorized_pdf_found
failed_after_retry
```

当自动CAPTCHA/滑块/机器人检查被技能成功解决，并且下载然后正常进行时，使用`verification_auto_passed`。

当自动验证尝试但无法通过挑战时，使用`verification_auto_failed`。这是一个用户转交状态，不是最终失败。

仅当浏览器明显位于机构SSO / CAS / CARSI-Shibboleth / OpenAthens / 数据库认证页面时，使用`carsi_waiting_user`。不要将其视为最终失败。

当出版商页面显示验证挑战但无法进行自动交互时，使用`publisher_verification_waiting_user`或`sciencedirect_robot_check`。当进行了范围自动尝试并且失败时，使用`verification_auto_failed`。这些都不是下载最终失败。

当合法的开放获取路线（如PMC、出版商的OA PDF、arXiv或其他合法开放PDF来源）提供下载的PDF而不需要机构授权时，使用`open_access_downloaded`。

对于成功的API优先下载，记录`oa_status: not_checked_api_first`；这意味着OA解析被有意跳过，而不是文章非OA。仅在支持出版商API尝试及其自动OA回退都失败后，使用`api_fallback_confirmation_required`。

当图书馆/全文解析器授予可读HTML全文但不存在有效PDF链接或`%PDF`响应时，使用`full_text_html_available`。这是一个成功的全文访问结果，不是PDF下载。如果用户请求文章，则保存HTML/文本，并明确告诉用户当前授权路线下不可用PDF。

当图书馆门户、SFX/OpenURL解析器、数据库或出版商页面明确说明用户的机构没有该论文的全文权限时，使用`library_no_permission`。明确告诉用户当前图书馆资源没有权限访问这篇文章。不要将直接出版商访问视为临时网络问题而重试。

## 启动浏览器控制

当Web Access CDP代理可以附加到用户正在使用的同一登录浏览器实例时，使用它。如果任务依赖于现有的登录状态，而CDP打开了一个空白/新配置文件，则优先选择重用用户活动浏览器会话的浏览器控制通道。

在Windows PowerShell中：

```powershell
$node = "node"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  $node = "$env:LOCALAPPDATA\OpenAI\Codex\bin\node.exe"
}
$checkDepsCandidates = @(
  "$env:USERPROFILE\.claude\skills\web-access-main\scripts\check-deps.mjs",
  "$env:USERPROFILE\.agents\skills\web-access-main\scripts\check-deps.mjs",
  "$env:USERPROFILE\.codex\skills\web-access-main\scripts\check-deps.mjs"
)
$checkDeps = $checkDepsCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $checkDeps) { throw "web-access-main/scripts/check-deps.mjs not found" }
& $node $checkDeps
```

然后测试：

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:3456/targets" -TimeoutSec 10
```

如果这挂起或失败：

- 要求用户确认远程调试复选框。
- 查看`%TEMP%\cdp-proxy.log`。
- 如果目标出现但数据库/图书馆页面未认证，怀疑陈旧的CDP端点、错误的浏览器或新的浏览器配置文件，而不是缺少图书馆权限。
- 不要尝试读取Chrome会话文件。

## 快速批次路径（默认用于2+篇论文 — 快速 & token高效）

对于超过一篇论文的情况，运行`scripts/batch_download.mjs`而不是逐步驱动浏览器。OA和出版商API在没有CDP的情况下运行；CNKI、Web Access和请求的SI懒惰地附加到已认证的浏览器。大型DOM和文件字节仍然在脚本内部。

脚本自动读取`~/.config/lit-dl/school.json`。当配置包含`discovery.web_of_science_url`时，该URL用作Web of Science入口；否则脚本回退到其编译的默认Web of Science URL。

```bash
# 按主题（从Web of Science核心集合收集N条记录）:
node scripts/batch_download.mjs --topic "rice blast resistance gene" --count 10 --no-si --out "<project>"
# 按明确的DOIs:
node scripts/batch_download.mjs --dois "10.1007/s00122-021-03957-1,10.1111/pbi.14066" --no-si --out "<project>"
# 按确切开放获取标题（arXiv回退，对无DOI文章有用）:
node scripts/batch_download.mjs --title "Attention Is All You Need" --open-access --no-si --out "<project>"
# 按中文确切标题（默认CNKI路线）:
node scripts/batch_download.mjs --title "乡村振兴背景下数字治理研究" --no-si --out "<project>"
# 按中文确切标题，仅PDF:
node scripts/batch_download.mjs --title "乡村振兴背景下数字治理研究" --cnki-format pdf --no-si --out "<project>"
# 按中文确切标题，带有图书馆提供的CNKI入口:
node scripts/batch_download.mjs --title "乡村振兴背景下数字治理研究" --cnki-url "https://kns.cnki.net/kns8s/defaultresult/index" --no-si --out "<project>"
# 按已知PDF URL:
node scripts/batch_download.mjs --pdf-url "https://arxiv.org/pdf/1706.03762" --title "Attention Is All You Need" --no-si --out "<project>"
# 将 --no-si 替换为 --si 仅在用户明确请求SI后
```

输出包括 `{ summary, manifest, results }`。脚本将`<project>/manifest.json`写入清单、OA证据、访问模式、格式、MIME、字节、SHA-256、SI选择和类型化失败；移除看起来像密钥的字段。PDFs放在`PDFs/`，原生HTML/XML放在`FullText/`，CAJ放在`CNKI/`，补充材料放在`SupportingInformation/`。

**Token纪律（适用于所有路径）：** 不要`eval`整个页面DOM、搜索结果或PDF/SI字节回退到代理上下文。将大量数据保留在Node/`scripts/*.mjs`中，仅显示紧凑状态。将交互式`/eval` + `cdp_open_url.mjs`保留用于单篇论文路线或批量运行后诊断卡住的论文。

## 高级浏览器和交付路线

保持此路由器紧凑，并在其条件适用时加载详细的操作参考：

- 当合法OA和适用出版商-API路线用尽，任务需要Web of Science、机构授权的浏览器会话、出版商验证、认证转交或浏览器上下文PDF传输时，加载[references/institutional-browser-workflow.md](references/institutional-browser-workflow.md)
- 当用户请求支持信息、下载的文件需要最终验证和命名，或访问尝试达到类型化失败或重试状态时，加载
  [references/delivery-verification-and-failures.md](references/delivery-verification-and-failures.md)

此路由器的边界、SI确认门、浏览器状态原则、状态语义和token纪律仍然强制适用。不要将参考视为绕过访问控制或暴露凭证、cookies或会话数据的权限。
