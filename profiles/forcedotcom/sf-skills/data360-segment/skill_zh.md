# data360-segment: 数据云分段阶段

当用户需要 **受众和洞察工作** 时（例如分段、计算洞察、发布工作流、成员计数或排错数据云分段 SQL），请使用此技能。

## 此技能负责任务的条件

当工作涉及以下内容时，请使用 `data360-segment`：
- `sf data360 segment *`
- `sf data360 calculated-insight *`
- 分段发布工作流
- 成员计数和分段排错
- 计算洞察执行和验证

当用户处于以下情况时，请将任务委派给其他技能：
- 仍在构建数据模型对象 (DMOs)、映射或身份解析 → [data360-harmonize](../data360-harmonize/SKILL.md)
- 激活下游分段 → [data360-activate](../data360-activate/SKILL.md)
- 编写只读 SQL 或搜索索引查询 → [data360-query](../data360-query/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 目标组织别名
- 统一 DMO（数据模型对象）或基础实体名称
- 用户是否希望创建、发布、检查或排错
- 资产是否为分段或计算洞察
- 预期的成功指标：成员计数、聚合值或发布状态

---

## 核心操作规则

- 将数据云分段 SQL 视为与 CRM SOQL 不同。
- 在修改受众资产之前，从 `data360-orchestrate` 技能运行共享就绪分类器：`node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase segment --json`。
- 优先使用可重用的 JSON 定义来重复创建分段和 CI。
- 当分段创建行为在较新默认值上不稳定时，使用 `--api-version 64.0`。
- 在发布/执行步骤后，通过计数或 SQL 进行验证，而不是假设成功。
- 当需要可读成员详细信息时，使用 SQL 连接而不是 `segment members`。

---

## 推荐工作流程

### 1. 对分段工作就绪情况进行分类
```bash
node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase segment --json
```

### 2. 检查当前状态
```bash
sf data360 segment list -o <org> 2>/dev/null
sf data360 calculated-insight list -o <org> 2>/dev/null
```

### 3. 使用可重用的 JSON 定义创建
```bash
sf data360 segment create -o <org> -f segment.json --api-version 64.0 2>/dev/null
sf data360 calculated-insight create -o <org> -f ci.json 2>/dev/null
```

### 4. 明确发布或执行
```bash
sf data360 segment publish -o <org> --name My_Segment 2>/dev/null
sf data360 calculated-insight run -o <org> --name Lifetime_Value 2>/dev/null
```

### 5. 通过计数或 SQL 进行验证
```bash
sf data360 segment count -o <org> --name My_Segment 2>/dev/null
sf data360 query sql -o <org> --sql 'SELECT COUNT(*) FROM "UnifiedssotIndividualMain__dlm"' 2>/dev/null
```

---

## 高信号注意事项

- 分段创建可能需要 `--api-version 64.0`。
- `segment members` 返回不透明的 ID；当需要可读成员详细信息时，请使用 SQL 连接。
- 分段 SQL 不是 SOQL。
- 计算洞察资产和分段 SQL 具有不同的限制。
- 发布/执行步骤即使命令返回很快，也可能触发异步工作。
- 空的分段或计算洞察列表通常表示模块可达但未配置，而不是不可用。

---

## 输出格式

```text
分段任务： <分段 / 计算洞察>
操作： <创建 / 发布 / 检查 / 排错>
目标组织： <别名>
工件： <定义文件 / 命令>
验证： <成员计数 / 查询结果 / 发布状态>
下一步： <执行 / 获取 / 跟进>
```

---

## 参考

- [../data360-orchestrate/assets/definitions/calculated-insight.template.json](../data360-orchestrate/assets/definitions/calculated-insight.template.json)
- [../data360-orchestrate/assets/definitions/segment.template.json](../data360-orchestrate/assets/definitions/segment.template.json)
- [../data360-orchestrate/references/feature-readiness.md](../data360-orchestrate/references/feature-readiness.md)
