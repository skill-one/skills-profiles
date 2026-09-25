# orchestrating-datacloud：Salesforce Data Cloud Orchestrator

当用户需要**产品级别的Data Cloud工作流指导**而不是单个隔离的命令集时，请使用此技能：管道设置、跨阶段故障排除、数据空间、数据套件，或判断任务是否属于连接、准备、协调、细分、执行或检索。

此技能有意遵循sf-skills的样式指南，同时使用外部`sf data360`命令界面作为运行时。插件**没有被包含在此存储库中**。

---

## 此技能负责的任务

当工作涉及以下内容时，请使用`orchestrating-datacloud`：
- 多阶段Data Cloud设置或修复
- 数据空间（`sf data360 data-space *`）
- 数据套件（`sf data360 data-kit *`）
- 健康检查（`sf data360 doctor`）
- CRM到统一配置文件的管道设计
- 决定如何从摄取→协调→细分→激活移动
- 跨阶段故障排除，其中根本原因尚不清楚

当用户专注于一个特定领域时，请委托给特定阶段的技能：

| 阶段 | 使用此技能 | 典型范围 |
|---|---|---|
| Connect | [connecting-datacloud](../connecting-datacloud/SKILL.md) | 连接、连接器、源发现 |
| Prepare | [preparing-datacloud](../preparing-datacloud/SKILL.md) | 数据流、DLOs、转换、DocAI |
| Harmonize | [harmonizing-datacloud](../harmonizing-datacloud/SKILL.md) | DMOs、映射、身份解析、数据图 |
| Segment | [segmenting-datacloud](../segmenting-datacloud/SKILL.md) | 分段、计算洞察 |
| Act | [activating-datacloud](../activating-datacloud/SKILL.md) | 激活、激活目标、数据操作 |
| Retrieve | [retrieving-datacloud](../retrieving-datacloud/SKILL.md) | SQL、搜索索引、向量搜索、异步查询 |

当用户处于以下情况时，请委托给家族外部：
- 提取会话跟踪/STDM遥测 → [observing-agentforce](../observing-agentforce/SKILL.md)
- 仅编写CRM SOQL → [querying-soql](../querying-soql/SKILL.md)
- 加载CRM源数据 → [handling-sf-data](../handling-sf-data/SKILL.md)
- 创建缺失的CRM架构 → [generating-custom-object](../generating-custom-object/SKILL.md) 或 [generating-custom-field](../generating-custom-field/SKILL.md)
- 实现下游Apex或Flow逻辑 → [generating-apex](../generating-apex/SKILL.md)、[generating-flow](../generating-flow/SKILL.md)

---

## 首先收集必要的上下文

请求或推断：
- 目标组织别名
- 插件是否已安装并链接
- 用户是否需要设计指导、只读检查或实时修改
- 涉及的数据源：CRM对象、外部数据库、文件摄取、知识等
- 期望结果：统一配置文件、分段、激活、向量搜索、分析或故障排除
- 用户是否在默认数据空间或自定义空间中工作
- 组织是否已使用`scripts/diagnose-org.mjs`进行分类
- 如果有的话，今天哪个命令集失败了

如果插件可用性或组织准备状态不确定，可以从以下内容开始：
- [references/plugin-setup.md](references/plugin-setup.md)
- [references/feature-readiness.md](references/feature-readiness.md)
- `scripts/verify-plugin.sh`
- `scripts/diagnose-org.mjs`
- `scripts/bootstrap-plugin.sh`

---

## 核心操作规则

- 使用外部`sf data360`插件运行时；**不要**重新实现或包含命令层。
- 一旦任务本地化，优先使用最小的特定阶段技能。
- 在进行修改密集型工作之前运行准备状态分类。优先使用`scripts/diagnose-org.mjs`而不是从单个失败的命令进行猜测。
- 对于`sf data360`命令，使用`2>/dev/null`抑制链接插件警告噪音，除非需要stderr输出进行调试。
- 区分**Data Cloud SQL**和CRM SOQL。
- **不要**将`sf data360 doctor`视为完整产品的准备状态检查；当前上游命令仅检查搜索索引表面。
- **不要**将`query describe`视为通用的租户探测；仅在确认更广泛的准备状态后，才使用它和一个已知的DMO/DLO表。
- 保留Data Cloud特定的API版本工作绕过，当它们重要的时候。
- 优先使用通用、可重用的JSON定义文件而不是特定组织的研讨会有效负载。

---

## 推荐的工作流程

### 1. 验证运行时和认证
确认：
- `sf`已安装
- 社区Data Cloud插件已链接
- 目标组织已认证

推荐检查：
```bash
sf data360 man
sf org display -o <alias>
bash ./scripts/verify-plugin.sh <alias>
```

将`sf data360 doctor`视为广泛的健康信号，而不是唯一的门控。在部分配置的组织中，即使只读命令集（如连接器、DMOs或分段）仍然可以工作，它也可能失败。

### 2. 在更改任何内容之前进行准备状态分类
首先运行共享分类器：
```bash
node ./scripts/diagnose-org.mjs -o <org> --json
```

只有在你知道表名是真实的情况下，才使用查询平面探测：
```bash
node ./scripts/diagnose-org.mjs -o <org> --phase retrieve --describe-table MyDMO__dlm --json
```

使用分类器区分：
- 空但启用的模块
- 功能门控模块
- 查询平面问题
- 运行时/认证失败

### 3. 使用只读命令发现现有状态
分类后使用目标检查：
```bash
sf data360 doctor -o <org> 2>/dev/null
sf data360 data-space list -o <org> 2>/dev/null
sf data360 data-stream list -o <org> 2>/dev/null
sf data360 dmo list -o <org> 2>/dev/null
sf data360 identity-resolution list -o <org> 2>/dev/null
sf data360 segment list -o <org> 2>/dev/null
sf data360 activation platforms -o <org> 2>/dev/null
```

### 4. 定位阶段
路由任务：
- 源/连接器问题 → Connect
- 摄取/DLO/流问题 → Prepare
- 映射/IR/统一配置文件问题 → Harmonize
- 受众或洞察问题 → Segment
- 下游推送问题 → Act
- SQL/搜索/索引问题 → Retrieve

### 5. 在可能的情况下选择确定性工件
优先使用JSON定义文件和可重复的脚本而不是一次性手动步骤。通用模板位于：
- `assets/definitions/data-stream.template.json`
- `assets/definitions/dmo.template.json`
- `assets/definitions/mapping.template.json`
- `assets/definitions/relationship.template.json`
- `assets/definitions/identity-resolution.template.json`
- `assets/definitions/data-graph.template.json`
- `assets/definitions/calculated-insight.template.json`
- `assets/definitions/segment.template.json`
- `assets/definitions/activation-target.template.json`
- `assets/definitions/activation.template.json`
- `assets/definitions/data-action-target.template.json`
- `assets/definitions/data-action.template.json`
- `assets/definitions/search-index.template.json`

### 6. 每个阶段后进行验证
典型验证：
- 流/DLO存在
- DMO/映射存在
- 身份解析运行完成
- 统一记录或分段计数看起来正确
- 激活/搜索索引状态健康

---

## 高信号陷阱

- `connection list`需要`--connector-type`。
- `dmo list --all`在您需要完整目录时很有用，但第一页`dmo list`通常足以进行准备状态检查且更快。
- 分段创建可能需要`--api-version 64.0`。
- `segment members`返回不透明的ID；使用SQL连接进行人类可读的详细信息。
- `sf data360 doctor`在部分配置的组织中可能会失败，即使某些只读命令仍然可以工作；回退到目标烟雾检查。
- `query describe`错误，如`Couldn't find CDP tenant ID`或`DataModelEntity ... not found`，是查询平面线索，而不是自动证明整个产品已禁用。
- 许多长时间运行的工作在实践中是异步的，即使命令返回很快。
- 一些Data Cloud操作仍然需要在CLI运行时之外进行UI设置。

---

## 输出格式

完成时，按以下顺序报告：
1. **任务分类**
2. **运行时状态**
3. **准备状态分类**
4. **涉及的阶段**
5. **使用的命令或工件**
6. **验证结果**
7. **下一步推荐步骤**

建议的格式：

```text
Data Cloud任务：<设置/检查/故障排除/迁移>
运行时：<插件就绪/缺失/部分验证>
准备状态：<就绪/就绪空/部分/功能门控/阻塞>
阶段：<连接/准备/协调/分段/执行/检索>
工件：<JSON文件、命令、脚本>
验证：<通过/部分/阻塞>
下一步：<下一阶段、设置指导或跨技能交接>
```

---

## 跨技能集成

| 需要 | 委托给 | 原因 |
|---|---|---|
| 加载或清理CRM源数据 | [handling-sf-data](../handling-sf-data/SKILL.md) | 在摄取之前种子或修复源记录 |
| 创建缺失的CRM架构 | [generating-custom-object](../generating-custom-object/SKILL.md)、[generating-custom-field](../generating-custom-field/SKILL.md) | Data Cloud期望现有的对象/字段 |
| 部署权限或包 | [deploying-metadata](../deploying-metadata/SKILL.md) | 环境准备 |
| 针对Data Cloud输出的Apex编写 | [generating-apex](../generating-apex/SKILL.md) | 代码实现 |
| 分段/激活后的Flow自动化 | [generating-flow](../generating-flow/SKILL.md) | 声明性编排 |
| 会话跟踪/STDM/Parquet分析 | [observing-agentforce](../observing-agentforce/SKILL.md) | 不同的Data Cloud用例 |

---

## 参考地图

### 从这里开始
- [README.md](README.md)
- [references/plugin-setup.md](references/plugin-setup.md)
- [references/feature-readiness.md](references/feature-readiness.md)
- [UPSTREAM.md](UPSTREAM.md)

### 阶段技能
- [connecting-datacloud](../connecting-datacloud/SKILL.md)
- [preparing-datacloud](../preparing-datacloud/SKILL.md)
- [harmonizing-datacloud](../harmonizing-datacloud/SKILL.md)
- [segmenting-datacloud](../segmenting-datacloud/SKILL.md)
- [activating-datacloud](../activating-datacloud/SKILL.md)
- [retrieving-datacloud](../retrieving-datacloud/SKILL.md)

### 确定性助手
- [scripts/bootstrap-plugin.sh](scripts/bootstrap-plugin.sh)
- [scripts/verify-plugin.sh](scripts/verify-plugin.sh)
- [scripts/diagnose-org.mjs](scripts/diagnose-org.mjs)
- [assets/definitions/](assets/definitions/)
