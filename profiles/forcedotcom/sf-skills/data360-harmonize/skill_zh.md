# data360-harmonize：数据云统一阶段

当用户需要**模式统一和整合工作**时，使用此技能：DMO、字段映射、关系、身份解析、统一档案、数据图或通用ID查询。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `data360-harmonize`：
- `sf data360 dmo *`
- `sf data360 identity-resolution *`
- `sf data360 data-graph *`
- `sf data360 profile *`
- `sf data360 universal-id lookup`

当用户处于以下情况时，将任务委派给其他技能：
- 仍在摄入流或构建DLO → [data360-prepare](../data360-prepare/SKILL.md)
- 正在工作细分逻辑或计算洞察 → [data360-segment](../data360-segment/SKILL.md)
- 运行SQL、describe或搜索索引工作流 → [data360-query](../data360-query/SKILL.md)

---

## 首先收集的必要上下文

询问或推断：
- 源DLO和目标DMO名称
- 任务是否与模式创建、映射、IR或图相关
- 目标组织别名
- 是否已存在规则集
- 用户期望的统一实体模型

---

## 核心操作规则

- 在创建映射前检查DMO模式。
- 在修改统一化资产前运行共享就绪分类器：`node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase harmonize --json`。
- 浏览目录时优先使用 `dmo list --all`，但快速就绪检查时使用第一页 `dmo list`。
- 使用 `query describe` 或 `dmo get --json` 而不是发明不支持的describe流程。
- 将身份解析运行视为异步操作，并在执行后验证结果。
- 将统一档案工作与STDM/会话跟踪工作分开。

---

## 推荐工作流程

### 1. 对统一工作就绪情况进行分类
```bash
node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase harmonize --json
```

### 2. 检查目录
```bash
sf data360 dmo list --all -o <org> 2>/dev/null
sf data360 identity-resolution list -o <org> 2>/dev/null
```

### 3. 映射前检查模式
```bash
sf data360 query describe -o <org> --table ssot__Individual__dlm 2>/dev/null
sf data360 dmo get -o <org> --name ssot__Individual__dlm --json 2>/dev/null
```

### 4. 有意创建或审查映射
```bash
sf data360 dmo mapping-list -o <org> --source Contact_Home__dll --target ssot__Individual__dlm 2>/dev/null
sf data360 dmo map-to-canonical -o <org> --dlo Contact_Home__dll --dmo ssot__Individual__dlm --dry-run 2>/dev/null
```

### 5. 仅在映射可信后运行IR
```bash
sf data360 identity-resolution create -o <org> -f ir-ruleset.json 2>/dev/null
sf data360 identity-resolution run -o <org> --name Main 2>/dev/null
```

---

## 高信号注意事项

- `dmo list` 通常应使用 `--all`。
- 使用 `query describe` 或 `dmo get --json`；没有 `dmo describe` 命令。
- 映射和相关命令对API版本差异敏感。
- 统一DMO名称是规则集特定的，而非通用的。
- 数据图定义对字段选择和关系形状敏感。
- 如果 `dmo list` 工作正常但 `identity-resolution list` 受限制，将其视为特定阶段的差距，而非完整的Data Cloud中断。

---

## 输出格式

```text
统一任务：<dmo / 映射 / 关系 / IR / 数据图>
源/目标：<dlo → dmo或规则集/图名称>
目标组织：<别名>
工件：<json文件/命令>
验证：<通过 / 部分通过 / 阻塞>
下一步：<细分 / 获取 / 跟进>
```

---

## 参考

- [../data360-orchestrate/assets/definitions/dmo.template.json](../data360-orchestrate/assets/definitions/dmo.template.json)
- [../data360-orchestrate/assets/definitions/mapping.template.json](../data360-orchestrate/assets/definitions/mapping.template.json)
- [../data360-orchestrate/assets/definitions/relationship.template.json](../data360-orchestrate/assets/definitions/relationship.template.json)
- [../data360-orchestrate/assets/definitions/identity-resolution.template.json](../data360-orchestrate/assets/definitions/identity-resolution.template.json)
- [../data360-orchestrate/assets/definitions/data-graph.template.json](../data360-orchestrate/assets/definitions/data-graph.template.json)
- [../data360-orchestrate/references/feature-readiness.md](../data360-orchestrate/references/feature-readiness.md)
