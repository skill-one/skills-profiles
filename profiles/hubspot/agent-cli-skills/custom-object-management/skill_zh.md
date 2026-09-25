## 真实数据源

`hubspot schemas --help` 是权威的。子命令：`list`、`get`、`create`、`update`（仅元数据）、`delete`（破坏性）。Schema 写入需要具有 `crm.schemas.custom.write` 权限的私有应用令牌。首先阅读 `bulk-operations/SKILL.md` — 此处的每个命令都使用其 JSONL 语法约定，并且 `schemas delete` 使用其 dry-run / digest / confirm 流程。

## 查找现有 Schema

```bash
hubspot schemas list                                       # JSONL: 名称、标签、单数形式、objectTypeId、来源
hubspot schemas list | jq 'select(.source=="custom")'      # 仅自定义
hubspot objects types | jq -c 'select(.source=="custom")'  # 相同的集合，也显示以确认 `--type` 解析
```

`name` 是其他所有命令使用的。`objectTypeId`（例如 `2-12345678`）仅用于 `PLATFORM_FLOW` 目标的 workflow。

## 检查一个 Schema

```bash
hubspot schemas get pets
```

返回完整的定义 — 属性、关联、标签、`requiredProperties`、`primaryDisplayProperty`、`fullyQualifiedName`。根据需要使用 `jq` 重新整形（参见 `bulk-operations/resources/json-patterns.md`）。

## 创建一个 Schema

构建 JSON 正文并将其管道（或使用 `--file` 传递）。最小的有效正文：

```json
{
  "name": "equipment",
  "labels": {"singular": "Equipment", "plural": "Equipment"},
  "primaryDisplayProperty": "equipment_name",
  "requiredProperties": ["equipment_name"],
  "properties": [
    {"name": "equipment_name", "label": "Name", "type": "string", "fieldType": "text"}
  ],
  "associatedObjects": ["contacts"]
}
```

```bash
cat equipment-schema.json | hubspot schemas create --dry-run   # 预览
hubspot schemas create --file equipment-schema.json            # 执行
```

稍后使用 `hubspot properties create --type <name> ...` 添加更多属性。

## 更新 Schema 元数据

`update` 仅修补标签 / 描述。属性编辑通过 `hubspot properties` 进行。

```bash
echo '{"labels":{"singular":"Device","plural":"Devices"}}' | hubspot schemas update equipment
```

`update` 也支持 `--dry-run` → digest → 使用 `--digest --confirm <name>` 重新运行（参见 `bulk-operations/SKILL.md` 中的模式）。

## 删除 Schema（破坏性）

Schema 删除是破坏性的且不可逆的 — 它永久删除 Schema **以及该类型的所有记录**。它被限制为 `MetadataDestroy`：每个删除都需要首先 `--dry-run`，然后重新运行使用 `--digest <hash> --confirm <name>`（在 5 分钟内）。

遵循 `bulk-operations/SKILL.md` 中记录的三步流程（“安全的破坏性工作流”）。对于 Schema，确认值是 Schema 名称：

```bash
hubspot schemas delete equipment --dry-run
# → digest=blast-... ; apply_command_hint 显示: --digest <hash> --confirm 'equipment'
hubspot schemas delete equipment --digest <hash> --confirm equipment
```

检查 `hubspot history --since 24h --kind MetadataDestroy` 以审计最近的 Schema 删除。

## 创建后使用 Schema

一旦 Schema 存在，所有 `hubspot objects ...` 命令都接受其 `name` 作为 `--type`（例如 `--type pets`）。记录 CRUD、搜索、关联、批量 upsert — 所有与标准对象完全相同。不要在此处重新实现这些流程；参见 `bulk-operations/SKILL.md` 和 `crm-lookup`。
