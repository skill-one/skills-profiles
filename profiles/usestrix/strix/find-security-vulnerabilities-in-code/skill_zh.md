# 在代码中查找安全漏洞

使用 Strix 进行白盒安全审查：代理读取源代码以构建路由、汇点以及授权检查的模型，然后尝试实际利用。发现的问题会附带概念验证，因此输出的是一个经过验证的问题短列表，而不是模式匹配扫描器产生的数百个“潜在”命中。

安装、LLM 设置、所有标志以及托管云路径都在 **penetration-testing-with-strix** 技能中。对于没有 Docker 和没有 LLM 密钥的运行，相同的二进制文件驱动托管平台：`strix cloud login`，然后 `strix cloud scans start ...`（详细信息在 **managed-pentesting-with-strix**）。

## 运行它

```bash
# 本地工作区
strix -n -t ./ --scan-mode standard --max-budget 15

# 直接指向 GitHub 仓库
strix -n -t https://github.com/org/app --max-budget 15

# 单一仓库：指向重要的服务，而不是整个树
strix -n -t ./services/checkout --max-budget 20

# 仅针对分支更改的内容（对大型仓库进行完整仓库审查是浪费的）
strix -n -t ./ --scope-mode diff --diff-base origin/main --max-budget 10
```

本地路径挂载到沙盒中是**可写的**，因此代理可以修改它。针对干净的检出运行。

有两件事可以显著提高结果：

1. **添加应用程序的运行实例。** `-t ./ -t http://host.docker.internal:3000` 让代理可以针对实际行为确认可利用性，而不是静态推理——这是“看起来不安全”和已验证发现之间的区别。如果没有运行任何内容，静态仅发现应描述为未确认。
2. **限定审查范围。** 指向有风险的下层目录并说明重要内容：
   ```bash
   strix -n -t ./services/api --max-budget 15 \
     --instruction "专注于 src/auth 中的授权层和 src/routes/admin 下每个路由。多租户应用程序：租户 ID 来自 JWT。标记任何按对象 ID 过滤但不按租户过滤的查询。"
   ```
   租户模型、信任边界以及哪些输入是攻击者控制的，代理无法可靠地推断——告诉它们。

## 替代整个仓库审查拉取请求

对于分支或 PR 的差分范围审查（并在发现时阻止合并），使用 **ci-security-scanning-with-strix**——它涵盖差分范围、PR 评论以及 SARIF 上传到 GitHub 代码扫描。托管平台也可以通过 API 直接审查 PR（**managed-pentesting-with-strix**）。

## 查看结果

在 `strix_runs/<run>/` 中：`penetration_test_report.md`（从这里开始），`vulnerabilities/*.md`（每个发现一个，附带概念验证和修复方案），`vulnerabilities.json` / `.csv`，`findings.sarif`（上传到代码扫描），`run.json`。

在向用户报告之前，打开每个发现并检查概念验证是否确实展示了影响。在利用的同时报告文件和行，以便修复显而易见。

退出 `0` 表示在分析的范围内没有证明可利用的内容——并不意味着代码库是干净的。检查 `run.json` 状态和成本与 `--max-budget` 的比较，如果运行被限制，则注意哪些路径未被审查。

## 互补工具

这是经过利用验证的审查，而不是详尽的清单。保留依赖项扫描器（SCA）和密钥扫描，以完整覆盖已知的 CVE 依赖项和提交的凭证；使用此工具查找那些工具在结构上无法发现的逻辑、授权和注入漏洞。

## 修复并验证

将结果交给 **fix-security-vulnerabilities-with-strix**：修复根本原因（共享的授权辅助程序，而不是单个路由），然后重新运行 Strix 以证明利用不再起作用。
