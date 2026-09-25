# platform-metadata-deploy：全面的 Salesforce DevOps 自动化

当用户需要**部署编排**时使用此技能：干运行验证、目标或基于清单的部署、CI/CD 工作流建议、沙盒组织管理、故障排查或 Salesforce 元数据的安全生产顺序。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `platform-metadata-deploy`：
- `sf project deploy start`、`quick`、`report` 或检索工作流
- 对对象、权限集、Apex 和流程的发布顺序
- CI/CD 网关、测试级别选择或部署报告
- 排查部署故障和依赖项顺序

当用户处于以下情况时，将任务委托给其他技能：
- 编写 Apex 代码 → [platform-apex-generate](../platform-apex-generate/SKILL.md)
- 编写 LWC 组件 → [experience-lwc-generate](../experience-lwc-generate/SKILL.md)
- 创建自定义对象或字段 → [platform-custom-object-generate](../platform-custom-object-generate/SKILL.md)、[platform-custom-field-generate](../platform-custom-field-generate/SKILL.md)
- 构建 Flow → [automation-flow-generate](../automation-flow-generate/SKILL.md)
- 执行组织数据操作 → [platform-data-manage](../platform-data-manage/SKILL.md)
- 编写或测试 Agentforce 代理 → [agentforce-generate](../agentforce-generate/SKILL.md)

---

## 关键操作规则

- 仅使用 **`sf` CLI v2**。
- 在非源跟踪组织中，部署/检索命令需要显式范围，例如 `--source-dir`、`--metadata` 或 `--manifest`。
- 优先在真实部署前使用 **`--dry-run`**。
- 对于 Flow，安全部署并在验证后激活。
- 在元数据验证或部署后，将测试数据创建指导委托给 **`platform-data-manage`**。

### 默认部署顺序
| 阶段 | 元数据 |
|---|---|
| 1 | 自定义对象 / 字段 |
| 2 | 权限集 |
| 3 | Apex |
| 4 | Flow 作为草稿 |
| 5 | Flow 激活 / 后验证 |

此顺序可防止许多依赖项和 FLS 故障。

---

## 首先收集的必要上下文

请求或推断：
- 目标组织别名和环境类型
- 部署范围：源目录、元数据列表或清单
- 这是否仅验证、部署、快速部署、检索或 CI/CD 指导
- 所需的测试级别和回滚预期
- 是否涉及特殊元数据类型（Flow、权限集、代理、包）

预检查：
```bash
sf --version
sf org list
sf org display --target-org <alias> --json
test -f sfdx-project.json
```

---

## 推荐工作流程

### 1. 预检查
确认认证、仓库结构、包目录和目标范围。

### 2. 首先验证
```bash
sf project deploy start --dry-run --source-dir force-app --target-org <alias> --wait 30 --json
```
当变更集是目标时，使用清单或元数据范围的验证。

### 3. 如果验证成功，提供下一个安全工作流程
验证成功后，引导用户执行正确的下一步操作：
1. 立即部署
2. 分配权限集
3. 通过 [platform-data-manage](../platform-data-manage/SKILL.md) 创建测试数据
4. 运行测试 / 烟雾测试
5. 按顺序编排多个部署后步骤

### 4. 部署最小的正确范围
```bash
# source-dir 部署
sf project deploy start --source-dir force-app --target-org <alias> --wait 30 --json

# manifest 部署
sf project deploy start --manifest manifest/package.xml --target-org <alias> --test-level RunLocalTests --wait 30 --json

# manifest 部署与 Spring '26 相关测试选择
sf project deploy start --manifest manifest/package.xml --target-org <alias> --test-level RunRelevantTests --wait 30 --json

# 验证成功后的快速部署
sf project deploy quick --job-id <validation-job-id> --target-org <alias> --json
```

### 5. 验证
```bash
sf project deploy report --job-id <job-id> --target-org <alias> --json
```
然后验证测试、Flow 状态、权限分配和烟雾测试行为。

### 6. 清晰报告
总结已部署的内容、失败项、跳过项和下一个安全操作。

输出模板：[references/deployment-report-template.md](references/deployment-report-template.md)

---

## 高信号故障模式

| 错误 / 症状 | 可能原因 | 默认修复方向 |
|---|---|---|
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | 验证规则或不良测试数据 | 调整数据或规则时机 |
| `INVALID_CROSS_REFERENCE_KEY` | 缺失依赖项 | 首先包含引用的元数据 |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | 触发器 / Flow / 验证副作用 | 检查自动化堆栈和失败逻辑 |
| 部署期间测试失败 | 代码损坏或脆弱测试 | 运行目标测试，修复根本原因，重新验证 |
| 权限集中未找到字段/对象 | 错误顺序 | 部署对象/字段前权限集 |
| Flow 无效 / 版本冲突 | 依赖项或激活问题 | 作为草稿部署，验证，然后激活 |

完整工作流程：[references/orchestration.md](references/orchestration.md)、[references/trigger-deployment-safety.md](references/trigger-deployment-safety.md)

---

## CI/CD 指导

默认管道形状：
1. 认证
2. 验证仓库 / 组织状态
3. 静态分析
4. 干运行部署
5. 测试 + 覆盖率网关
6. 部署
7. 验证 + 通知

- 当组织策略和发布风险允许时，考虑使用 `--test-level RunRelevantTests` 进行 Apex 密集型部署。
- 与现代 Apex 测试注解（如 `@IsTest(testFor=...)` 和 `@IsTest(isCritical=true)`）配合使用 — 参见 [platform-apex-generate](../platform-apex-generate/SKILL.md) 获取编写指导。

静态分析现在使用 **Code Analyzer v5** (`sf code-analyzer`)，而不是已退役的 `sf scanner`。

深度参考：[references/deployment-workflows.md](references/deployment-workflows.md)

---

## Agentforce 部署说明

使用此技能编排围绕代理的**部署/发布顺序**，但使用特定于代理的技能进行编写决策：
- [agentforce-generate](../agentforce-generate/SKILL.md) 用于 `.agent` 编写、Agent Builder、Prompt Builder 和元数据配置

有关完整代理 DevOps 详细信息，包括 `Agent:` 伪元数据、发布/激活和跨组织同步，请参阅：
- [references/agent-deployment-guide.md](references/agent-deployment-guide.md)

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 自定义对象创建 | [platform-custom-object-generate](../platform-custom-object-generate/SKILL.md) | 部署前定义对象 |
| 自定义字段创建 | [platform-custom-field-generate](../platform-custom-field-generate/SKILL.md) | 部署前定义字段 |
| Apex 编写/修复 | [platform-apex-generate](../platform-apex-generate/SKILL.md) | 代码编写和修复 |
| Flow 创建/修复 | [automation-flow-generate](../automation-flow-generate/SKILL.md) | Flow 编写和激活指导 |
| 测试数据或种子记录 | [platform-data-manage](../platform-data-manage/SKILL.md) | 描述优先数据设置和清理 |
| 代理编写和发布准备 | [agentforce-generate](../agentforce-generate/SKILL.md) | 代理特定正确性 |

---

## 参考地图

### 从这里开始
- [references/orchestration.md](references/orchestration.md)
- [references/deployment-workflows.md](references/deployment-workflows.md)
- [references/deployment-report-template.md](references/deployment-report-template.md)

### 专门的部署安全
- [references/trigger-deployment-safety.md](references/trigger-deployment-safety.md)
- [references/agent-deployment-guide.md](references/agent-deployment-guide.md)
- [references/deploy.sh](references/deploy.sh)

### 资产模板
- [assets/package.xml](assets/package.xml) — 覆盖常见元数据类型的清单模板
- [assets/destructiveChanges.xml](assets/destructiveChanges.xml) — 从目标组织中删除元数据的模板

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 强大的部署计划和执行指导 |
| 75–89 | 良好的部署指导，有少量审查项 |
| 60–74 | 部署风险部分覆盖 |
| < 60 | 信心不足；在发布前收紧计划 |

---

## 完成格式

```text
部署目标：<验证 / 部署 / 检索 / 管道>
目标组织：<别名>
范围：<源目录 / 元数据 / 清单>
结果：<通过 / 失败 / 部分通过>
关键发现：<错误、顺序、测试、跳过项>
下一步：<安全后续操作>
```
