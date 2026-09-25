# 部署 OmniStudio 数据包：Vlocity 构建数据包部署

在用户需要 **Vlocity 数据包部署编排** 时使用此技能：数据包导出/部署工作流、基于清单的部署、故障分派以及 OmniStudio/行业数据包的 CI/CD 顺序。

---

## 范围

当工作涉及以下内容时，使用 `deploying-omnistudio-datapacks`：
- `vlocity packDeploy`, `packRetry`, `packContinue`, `packExport`, `packGetDiffs`, `validateLocalData`
- 数据包工作文件设计 (`projectPath`, `expansionPath`, `manifest`, `queries`)
- 组织间数据包迁移和重试循环
- 排查数据包依赖、匹配键和 GlobalKey 问题

当用户处于以下情况时，将任务委托给其他技能：
- 使用 `sf project deploy` 部署标准元数据 -> [deploying-metadata](../deploying-metadata/SKILL.md)
- 构建 OmniScripts、FlexCards、IP 或数据映射器 -> `building-omnistudio-*`
- 设计 Product2 EPC 套件 -> [modeling-omnistudio-epc-catalog](../modeling-omnistudio-epc-catalog/SKILL.md)
- 编写 Apex/LWC 代码 -> [generating-apex](../generating-apex/SKILL.md), [generating-lwc-components](../generating-lwc-components/SKILL.md)

---

## 关键操作规则

- 使用 **Vlocity Build (`vlocity`)** 命令部署数据包，而不是 `sf project deploy`。
- 优先使用 Salesforce CLI 身份验证集成 (`-sfdx.username <alias>`) 而不是用户名/密码文件（如果可用）。
- 在完整部署前，始终运行 **预部署质量门禁**：
  1) `validateLocalData`
  2) 可选 `packGetDiffs`
  3) 然后 `packDeploy`
- 当错误计数下降时，重复使用 `packRetry`；当重试不再改善结果时停止。
- 在源组织和目标组织中保持匹配键策略和 GlobalKey 完整性一致。

---

## 首要收集的上下文

询问或推断：
- 源组织和目标组织别名
- 工作文件路径和数据包项目路径
- 部署范围（完整项目、清单子集或特定 `-key`）
- 这是导出、部署、重试、继续还是仅差异
- 命名空间模型 (`%vlocity_namespace%`, `vlocity_cmt` 或核心)
- 已知约束（新沙盒引导、触发行为、匹配键自定义）

预检查：

```bash
vlocity help
sf org list
sf org display --target-org <alias> --json
test -f <job-file>.yaml
```

---

## 推荐工作流程

### 1. 确保工具就绪
```bash
npm install --global vlocity
vlocity help
```

### 2. 本地验证项目数据
```bash
vlocity -sfdx.username <source-alias> -job <job-file>.yaml validateLocalData
```

仅在明确请求且解释影响后使用 `--fixLocalGlobalKeys`。

### 3. 从源导出（当需要时）
```bash
vlocity -sfdx.username <source-alias> -job <job-file>.yaml packExport
vlocity -sfdx.username <source-alias> -job <job-file>.yaml packRetry
```

### 4. 部署到目标
```bash
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packDeploy
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packRetry
```

### 5. 继续中断的任务
```bash
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packContinue
```

### 6. 验证部署后一致性
```bash
vlocity -sfdx.username <target-alias> -job <job-file>.yaml packGetDiffs
```

工作文件模板：[references/job-file-template.md](references/job-file-template.md)

---

## 注意事项

| 错误 / 症状 | 可能原因 | 默认修复方向 |
|---|---|---|
| `No match found for ...` | 目标组织中缺少依赖项 | 包含缺少的数据包键并重新部署 |
| `Duplicate Results found for ... GlobalKey` | 目标中存在重复记录 | 清理重复记录并重新运行部署 |
| `Multiple Imported Records ... same Salesforce Record` | 源中存在重复的匹配键记录 | 删除源中的重复记录并重新导出 |
| `No Configuration Found` | 数据包设置过时 | 运行 `packUpdateSettings` 或启用 `autoUpdateSettings` |
| `Some records were not processed` | 设置不匹配 / 部分依赖状态 | 两个组织都刷新设置，然后重试 |
| SASS / 模板编译失败 | 缺少引用的 UI 模板资源 | 首先导出/部署引用的模板依赖项 |

详细矩阵：[references/troubleshooting-matrix.md](references/troubleshooting-matrix.md)

---

## CI/CD 指导

默认管道形状：
1. 身份验证组织 (`sf org login ...`)
2. 验证本地数据包完整性 (`validateLocalData`)
3. 导出更改范围 (`packExport` 或基于清单的导出)
4. 部署 (`packDeploy`)
5. 重试循环 (`packRetry`) 直到稳定
6. 比较 (`packGetDiffs`) 并发布部署报告

为增量部署优化，使用工作文件选项，例如：
- `gitCheck: true`
- `gitCheckKey: <folder>`
- `manifest` 用于确定性范围控制

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 数据包外部的元数据部署 | [deploying-metadata](../deploying-metadata/SKILL.md) | 元数据 API 工作流 |
| OmniStudio 组件编写 | `building-omnistudio-*` | 部署前的构建工件 |
| EPC 产品和报价有效载荷编写 | [modeling-omnistudio-epc-catalog](../modeling-omnistudio-epc-catalog/SKILL.md) | Product2/数据包模型质量 |
| Apex 触发器/日志错误诊断 | [debugging-apex-logs](../debugging-apex-logs/SKILL.md), [generating-apex](../generating-apex/SKILL.md) | 自动化端的根本原因修复 |

---

## 输出预期

完成数据包操作后，交付完成块：

```text
数据包目标：<导出 / 部署 / 重试 / 差异 / ci-cd>
源组织：<别名 或 N/A>
目标组织：<别名 或 N/A>
范围：<工作文件 + 清单/键/完整>
结果：<通过 / 失败 / 部分通过>
关键发现：<错误、依赖项、重试、差异>
下一步：<安全的后续操作>
```

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/job-file-template.md` | 在提供工作文件结构建议之前 — 作为基准配置参考加载 |
| `references/troubleshooting-matrix.md` | 当用户报告部署失败时 — 加载以诊断数据包错误并应用修复方向 |
| `examples/business-internet-plus-bundle/TRANSCRIPT.md` | Product2 套件验证规划和执行的示例 |
| `examples/business-internet-plus-bundle/deploy-business-internet-plus-bundle.yaml` | 范围有限 `validateLocalData` 运行的示例工作文件 |
| `examples/business-internet-plus-bundle-deploy/TRANSCRIPT.md` | 包含 `packDeploy` 和 `packRetry` 结果的完整部署周期示例 |
| `examples/business-internet-plus-bundle-deploy/deploy-business-internet-plus-bundle.yaml` | 阶段性部署的示例工作文件，目标为清单 |
