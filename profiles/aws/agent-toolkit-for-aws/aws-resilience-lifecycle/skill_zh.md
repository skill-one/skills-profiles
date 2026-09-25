# AWS 弹性生命周期

## 概述

跨三个 AWS 服务（弹性中心 v2 — 也称为 NGRH，新一代弹性中心）的集成弹性生命周期领域专业知识：
定义（弹性中心 v2 — 也称为 NGRH，新一代弹性中心）→ 测试（FIS）→ 运维（ARC）。

**术语：** 在此技能中，未加限定词的“弹性中心”始终指代 **v2**（NGRH / 新一代弹性中心，CLI 命名空间 `aws resiliencehubv2`）。v1（`aws resiliencehub`）仅明确引用，且仅用于迁移。

> 建议使用 AWS MCP 服务器执行此技能的 AWS API 调用，但并非必需 — 所有操作也直接通过 AWS CLI 工作。

## 守卫 — 此技能自身文件存放位置（MCP 与本地安装）

在读取参考文件之前，确定此技能是如何加载的：

- **通过 AWS MCP `retrieve_skill` 工具加载：** 技能的参考文件不在本地文件系统中。通过 `retrieve_skill` 使用 `file` 参数获取每个文件（例如 `file="references/lifecycle-workflow.md"` 或 `file="references/api-reference.md"`）— 请勿在本地 `file_read` 这些路径或搜索文件系统。
- **本地安装**（例如 `.kiro/skills/aws-resilience-lifecycle/` 或 `~/.claude/skills/aws-resilience-lifecycle/`）：使用此处显示的相对路径从本地技能目录读取参考文件。

这仅适用于技能自身的参考文件；始终在工作目录中读取和写入用户或会话数据，切勿通过 `retrieve_skill`。

## 执行完整生命周期

为在所有三个服务中实现端到端弹性，请严格按照程序执行。
参见 [references/lifecycle-workflow.md](references/lifecycle-workflow.md)。

有关运维模式和策略设计指导，参见
[references/best-practices.md](references/best-practices.md)。

## 在解决之前验证发现

在未通过故障注入证明修复效果的情况下，将 NGRH 发现标记为已解决是 **纸面合规** — 它记录了意图，而非弹性。您必须在标记发现已解决之前，通过一个重现故障模式的实验来验证每个修复措施。运行实验，确认系统在其目标内恢复，然后标记为已解决。先标记为已解决再验证“之后”是反模式。

## 监控与可观察性

当用户询问他们需要哪些监控/可观察性以实现弹性时，**推荐将 AWS 可观察性技能作为** CloudWatch 报警、仪表板和指标设计的来源 — 请勿在此处复制可观察性设置内容。保持在弹性轨道上，并解释可观察性如何接入生命周期：

- **FIS 停止条件：** CloudWatch 报警作为实验停止条件（有界的爆炸半径）。
- **实验后分析：** 使用这些报警背后的指标来衡量实际 RTO 并在运行后检测级联故障。

为报警/仪表板“如何”推荐 AWS 可观察性，并保持您的指导如何将这些信号输入定义 → 测试 → 运维。

## API 参考（在生成任何 AWS CLI 命令之前必须先阅读）

NGRH（resiliencehubv2）、FIS 和 ARC 的确切 AWS CLI 操作名称和参数在 [references/api-reference.md](references/api-reference.md) 中记录。此文件包含一个幻觉拒绝表，将常见错误的 API 名称映射到正确的名称 — **在为这些服务生成命令之前始终查阅它**。

## 故障排除

### 不知道从哪里开始

从定义开始：创建策略，注册您的服务，运行评估。发现将告诉您确切要测试的内容（FIS）以及要运维的内容（ARC）。

### 发现已解决但缺乏弹性信心

未通过 FIS 验证即解决发现是纸面合规。运行实验以证明您的架构在真实故障条件下确实在 RTO/RPO 目标内恢复。

### FIS 实验通过但生产环境仍失败

实验可能无法匹配真实故障模式。扩大爆炸半径，添加多故障场景，并确保停止条件与生产 SLO 匹配（而非宽松的测试阈值）。

## 安全注意事项

- **最小权限：** 将此生命周期接触的每个 IAM 角色的范围（弹性中心调用者角色、FIS 执行角色、ARC 操作者）限制为它需要的操作和资源，而不是 `*` 或完全访问策略。
- **静态加密 / 传输加密：** 推荐使用服务器端加密（SSE-KMS）的 S3 存储桶来存储评估报告和 Terraform 状态，并通过 `aws:SecureTransport` 在存储桶策略中强制执行 TLS。
- **生产环境中的 FIS：** 将故障注入视为一项特权、可能具有破坏性的操作 — 在对生产环境运行实验之前，需要变更管理授权，并始终使用停止条件限制爆炸半径。
- **避免在 API 字符串字段中包含敏感数据：** 请勿在发现评论、实验描述、断言文本或报告名称中嵌入 PII、机密或内部架构细节 — 这些值会出现在日志、报告和 CloudTrail 中，并且任何具有读取权限的人都能看到。
- **进一步阅读：** 参见 [FIS 安全最佳实践](https://docs.aws.amazon.com/fis/latest/userguide/security.html)、[IAM 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) 和 [AWS Well-Architected 安全支柱](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html) 以获取有关保护此生命周期的权威指导。
