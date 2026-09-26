# 高级安全工程师 — 威胁建模 + 安全路由

这项技能本身只做一件工作 — **STRIDE/DREAD威胁建模**（附带快速秘密扫描） — 并将其他所有安全请求路由到负责该领域的专业技能。此处不要重复兄弟内容；应进行路由。

## 路由表（请先阅读此表）

| 用户想要... | 路由到 | 为什么该技能负责它 |
|---|---|---|
| 漏洞评估、渗透测试方法论、OWASP Top 10 测试 | `../security-pen-testing/` | 配送 `vulnerability_scanner.py` + `dependency_auditor.py` 并附带退出码契约 |
| 事件分类、SEV 分类、取证、遏制 | `../incident-response/` | SEV1–SEV4 分类法、NIST SP 800-61 阶段、`incident_triage.py` |
| 生产故障指令（非安全事件） | `../incident-commander/` | 严重性分类器 + 时间线 + 后置分析工具 |
| 安全监控、CVE 分类 SLA、合规检查（SOC 2 等）、安全头 | `../senior-secops/` | `security_scanner.py` + `compliance_checker.py`，CVE SLA 表 |
| 敌意/对抗代码审查 | `../adversarial-reviewer/` | 三人角色审查，BLOCK/CONCERNS/CLEAN 判定 |
| 作为一般审查一部分的安全代码审查 | `../code-reviewer/` | 语言分发 + 回归固定装置 |
| 云 IAM 升级路径、S3 暴露、安全组 | `../cloud-security/` | `cloud_posture_check.py`，每个检查的退出码 |
| 威胁搜寻、IOC 扫描、异常检测 | `../threat-detection/` | z 分数异常 + IOC 陈旧工具 |
| 红队参与规划、ATT&CK 杀链 | `../red-team/` | `engagement_planner.py` 带授权门 |
| LLM/AI 攻击面（提示注入、中毒） | `../ai-security/` | ATLAS 映射的 `ai_threat_scanner.py` |

如果请求跨越多个领域（例如，“保护这个新架构”），请在此处先进行威胁建模 — 其输出（优先级威胁 + 缓解措施）将告诉您下一步需要加载哪些兄弟技能。切勿推测性地批量加载多个安全技能。

## 本技能拥有：STRIDE 威胁建模

### 工作流程

1. **范围：** 要保护的资产、信任边界、数据流（外部实体、进程、数据存储、流）。
2. **按组件生成威胁模型：**
   ```bash
   python3 scripts/threat_modeler.py --component "用户认证" --assets "凭证,会话" --json --output threats.json
   ```
   输出：每个威胁的 STRIDE 类别、DREAD 分数（损害、可重复性、可利用性、受影响用户、可发现性 — 每个 1–10），以及建议的缓解措施。对每个 DFD 元素重复；`--interactive` 引导范围问题；`--list-threats` 显示威胁数据库。
3. **消费输出：** 按 DREAD 分数降序排序 `threats.json`；所有 ≥ 7 平均值的都需要在设计交付前指定缓解措施负责人。将每个缓解措施映射到负责的兄弟领域（例如，IAM 威胁 → `cloud-security`，注入威胁 → `code-reviewer`）。
4. **快速秘密扫描：** 在您打开代码库时：
   ```bash
   python3 scripts/secret_scanner.py /path/to/project --format json --severity high
   ```
   20+ 模式（AWS 密钥、GitHub 令牌、私钥、通用凭证）。任何关键/高发现都会阻止合并，直到旋转并移动到秘密管理器。
5. **验证门：** 每个 DFD 元素都有 ≥ 1 个 STRIDE 行考虑，每个 DREAD ≥ 7 的威胁都有负责人 + 缓解措施，秘密扫描以零高/关键发现退出。在缓解措施落地后重新运行这两个工具 — 重新运行是完成信号，不是文档。

### 每个元素的 STRIDE 矩阵

| DFD 元素 | S | T | R | I | D | E |
|-------------|---|---|---|---|---|---|
| 外部实体 | X | | X | | | |
| 进程 | X | X | X | X | X | X |
| 数据存储 | | X | X | X | X | |
| 数据流 | | X | | X | X | |

(S=欺骗→认证, T=篡改→完整性, R=否认→审计日志, I=信息泄露→加密/访问控制, D=拒绝服务→速率限制/冗余, E=提升→最小权限。)

## 参考文献（按需加载）

| 文档 | 内容 |
|----------|---------|
| [references/threat-modeling-guide.md](references/threat-modeling-guide.md) | STRIDE 方法论、攻击树、DREAD 分数、DFD 创建 |
| [references/security-architecture-patterns.md](references/security-architecture-patterns.md) | 零信任、纵深防御、认证模式、API 安全 |
| [references/cryptography-implementation.md](references/cryptography-implementation.md) | AES-GCM、Ed25519、密码哈希（Argon2id）、密钥管理 |

架构和加密参考文献被保留，因为没有任何兄弟领域发送它们；对于 *操作* 这些控制（扫描、合规、监控）仍然路由到 `senior-secops`。
