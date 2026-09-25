# harmonizing-datacloud：数据云协调阶段

当用户需要**模式协调和统一工作**时，使用此技能：DMO、字段映射、关系、身份解析、统一档案、数据图或通用ID查询。

## 此技能拥有任务的时机

当工作涉及以下内容时，使用 `harmonizing-datacloud`：
- `sf data360 dmo *`
- `sf data360 identity-resolution *`
- `sf data360 data-graph *`
- `sf data360 profile *`
- `sf data360 universal-id lookup`

当用户处于以下情况时，将任务委派给其他技能：
- 仍在摄入流或构建DLO → [preparing-datacloud](../preparing-datacloud/SKILL.md)
- 正在工作细分逻辑或计算洞察 → [segmenting-datacloud](../segmenting-datacloud/SKILL.md)
- 运行SQL、describe或搜索索引工作流 → [retrieving-datacloud](../retrieving-datacloud/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 源DLO和目标DMO名称
- 任务是否与模式创建、映射、IR或图相关
- 目标组织别名
- 是否已存在规则集
- 用户期望的统一实体模型

---

## 核心操作规则

- 创建映射前检查DMO模式。
- 在修改协调资产前运行共享就绪分类器：`node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase harmonize --json`。
- 浏览目录时优先使用 `dmo list --all`，但快速就绪检查时使用第一页 `dmo list`。
- 使用 `query describe` 或 `dmo get --json` 而不是发明不支持的describe流程。
- 将身份解析运行视为异步操作，执行后验证结果。
- 将统一档案工作与STDM/会话跟踪工作分开。

---

## 推荐工作流程

### 1. 协调工作就绪分类
```bash
node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase harmonize --json
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

### 5. 映射可信后仅运行IR
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
- 如果 `dmo list` 工作但 `identity-resolution list` 受限，将其视为特定阶段的差距，而非完整的Data Cloud中断。

---

## 输出格式

```text
协调任务：<dmo / 映射 / 关系 / ir / 数据图>
源/目标：<dlo → dmo或规则集/图名称>
目标组织：<别名>
工件：<json文件 / 命令>
验证：<通过 / 部分通过 / 阻塞>
下一步：<细分 / 检索 / 跟进>
```

---

## 参考

- [README.md](README.md)
- [../orchestrating-datacloud/assets/definitions/dmo.template.json](../orchestrating-datacloud/assets/definitions/dmo.template.json)
- [../orchestrating-datacloud/assets/definitions/mapping.template.json](../orchestrating-datacloud/assets/definitions/mapping.template.json)
- [../orchestrating-datacloud/assets/definitions/relationship.template.json](../orchestrating-datacloud/assets/definitions/relationship.template.json)
- [../orchestrating-datacloud/assets/definitions/identity-resolution.template.json](../orchestrating-datacloud/assets/definitions/identity-resolution.template.json)
- [../orchestrating-datacloud/assets/definitions/data-graph.template.json](../orchestrating-datacloud/assets/definitions/data-graph.template.json)
- [../orchestrating-datacloud/references/feature-readiness.md](../orchestrating-datacloud/references/feature-readiness.md)
