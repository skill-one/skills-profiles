# 生成 Actor 输出模式

您正在为 Apify Actor 生成输出模式文件。输出模式告诉 Apify Console 如何显示运行结果。您将分析 Actor 的源代码，创建 `dataset_schema.json`、`output_schema.json` 和 `key_value_store_schema.json`（如果 Actor 使用键值存储），并更新 `actor.json`。

## 核心原则

- **先分析代码**：阅读 Actor 的源代码以了解它实际推送到数据集的数据——切勿猜测
- **每个字段都是可空的**：API 和网站是不可预测的——始终设置 `"nullable": true`
- **匿名化示例**：示例中切勿使用真实的用户 ID、用户名或个人数据
- **与代码验证**：如果存在 TypeScript 类型，请将模式与类型定义和生成值的代码进行交叉检查
- **重用现有模式**：在生成模式之前，检查同一存储库中的其他 Actor 是否已经具有输出模式——匹配其结构、命名约定、描述风格和格式
- **不要重新发明轮子**：重用代码库中的现有类型定义、接口和工具，而不是创建重复的定义

---

## 第一阶段：发现 Actor 结构

**目标**：定位 Actor 并了解其输出

初始请求：$ARGUMENTS

**操作**：
1. 创建包含所有阶段的待办事项列表
2. 查找包含 `actor.json` 的 `.actor/` 目录
3. 读取 `actor.json` 以了解 Actor 的配置
4. 检查 `dataset_schema.json`、`output_schema.json` 和 `key_value_store_schema.json` 是否已存在
5. **在存储库中搜索现有模式**：查找其他 `.actor/` 目录或模式文件（例如，`**/dataset_schema.json`、`**/output_schema.json`、`**/key_value_store_schema.json`）以了解存储库的约定——匹配其描述风格、字段命名、示例格式和整体结构
6. 查找所有将数据推送到数据集的位置：
   - **JavaScript/TypeScript**：搜索 `Actor.pushData(`、`dataset.pushData(`、`Dataset.pushData(`
   - **Python**：搜索 `Actor.push_data(`、`dataset.push_data(`、`Dataset.push_data(`
7. 查找所有将数据存储在键值存储中的位置：
   - **JavaScript/TypeScript**：搜索 `Actor.setValue(`、`keyValueStore.setValue(`、`KeyValueStore.setValue(`
   - **Python**：搜索 `Actor.set_value(`、`key_value_store.set_value(`、`KeyValueStore.set_value(`
8. 查找输出类型定义——**直接重用**，而不是从头开始重新创建：
   - **TypeScript**：查找输出类型接口/类型（例如，在 `src/types/`、`src/types/output.ts` 中）。如果接口或类型已经定义了输出形状，则从它派生模式字段——不要创建并行的定义
   - **Python**：查找 TypedDict、dataclass 或 Pydantic 模型定义。使用现有的字段名、类型和 docstrings 作为真实来源
9. 检查代码库中现有的用于处理模式生成或验证的共享模式实用程序或辅助函数——重用它们，而不是创建新的逻辑
10. 如果 `actor.json` 中存在内联 `storages.dataset` 或 `storages.keyValueStore` 配置，请将其记录为迁移目标

向用户展示发现结果：列出所有发现的数据集输出字段、键值存储键、它们的类型以及它们的来源。

---

## 第二阶段：生成 `dataset_schema.json`

**目标**：创建包含字段定义和显示视图的完整数据集模式

### 文件结构

```json
{
    "actorSpecification": 1,
    "fields": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            // 所有输出字段都在这里——Actor 可以产生的每个字段，
            // 而不仅仅是概览视图中显示的字段
        },
        "required": [],
        "additionalProperties": true
    },
    "views": {
        "overview": {
            "title": "概览",
            "description": "一瞥最重要的字段",
            "transformation": {
                "fields": [
                    // 8-12 个最重要的字段名
                ]
            },
            "display": {
                "component": "table",
                "properties": {
                    // 每个概览字段的显示配置
                }
            }
        }
    }
}
```

### 与现有模式的兼容性

如果在第一阶段（第 5 步）中在存储库中找到现有的输出模式，请遵循它们的约定：
- 匹配**描述编写风格**（句子大小写与小写、句号与无句号等）
- 匹配**字段命名约定**（驼峰式与蛇形式）——这也必须与 Actor 代码生成的实际键匹配
- 匹配**示例值风格**（例如，日期格式、URL 模式、占位符名称）
- 匹配**视图结构**（概览中的字段数量、显示格式选择）
- 匹配**JSON 格式**（缩进、属性排序、空格）——存储库中的所有模式必须使用相同的格式，包括独立的 Actor

当 Actor 代码已经具有定义良好的 TypeScript 接口或 Python 类型类时，直接从这些类型派生字段，而不是从头开始重新分析 `pushData/push_data` 调用。类型定义是权威来源。

### 硬性规则（无例外）

| 规则 | 详细说明 |
|------|--------|
| **`properties` 中的所有字段** | `fields.properties` 对象必须包含 Actor 可以输出的**每个**字段，而不仅仅是概览视图中显示的字段。视图部分选择用于显示的子集——`properties` 部分必须是完整的超集 |
| `"nullable": true` | 在**每个**字段上——API 是不可预测的 |
| `"additionalProperties": true` | 在**顶层 `fields` 对象**上和 `properties` 中**每个嵌套对象**上。这是最常被遗漏的规则——它必须在两个级别都出现 |
| `"required": []` | 始终为空数组——在**顶层 `fields` 对象**上和 `properties` 中**每个嵌套对象**上 |
| 匿名化示例 | 无真实用户 ID、用户名或内容 |
| `"type"` 与 `"nullable"` 必须一起出现 | AJV 在同一字段上拒绝没有 `type` 的 `nullable` |

> **警告——最常见的错误**：
> 1. 仅包括出现在概览视图中的字段。`fields.properties` 必须列出所有输出字段，即使它们不在 `views` 部分中。
> 2. 仅在嵌套对象类型的属性上添加 `"required": []` 和 `"additionalProperties": true`，但忘记在顶层 `fields` 对象上添加它们。两个级别都需要它们。

> **注意**：`nullable` 是 Apify 对 JSON Schema draft-07 的特定扩展。这是有意且正确的。

### 字段类型模式

**字符串字段**：
```json
"title": {
    "type": "string",
    "description": "抓取项的标题",
    "nullable": true,
    "example": "示例项标题"
}
```

**数字字段**：
```json
"viewCount": {
    "type": "number",
    "description": "浏览次数",
    "nullable": true,
    "example": 15000
}
```

**布尔字段**：
```json
"isVerified": {
    "type": "boolean",
    "description": "账户是否已验证",
    "nullable": true,
    "example": true
}
```

**数组字段**：
```json
"hashtags": {
    "type": "array",
    "description": "与项关联的标签",
    "items": { "type": "string" },
    "nullable": true,
    "example": ["#example", "#demo"]
}
```

**嵌套对象字段**：
```json
"authorInfo": {
    "type": "object",
    "description": "关于作者的信息",
    "properties": {
        "name": { "type": "string", "nullable": true },
        "url": { "type": "string", "nullable": true }
    },
    "required": [],
    "additionalProperties": true,
    "nullable": true,
    "example": { "name": "示例作者", "url": "https://example.com/author" }
}
```

**枚举字段**：
```json
"contentType": {
    "type": "string",
    "description": "内容类型",
    "enum": ["article", "video", "image"],
    "nullable": true,
    "example": "article"
}
```

**联合类型（例如，TypeScript `ObjectType | string`）**：
```json
"metadata": {
    "type": ["object", "string"],
    "description": "结构化元数据对象，或不可用时的错误字符串",
    "nullable": true,
    "example": { "key": "value" }
}
```

### 匿名化示例值

使用真实但通用的值。遵循平台 ID 格式约定：

| 字段类型 | 示例方法 |
|---|---|
| ID | 匹配平台格式和长度（例如，YouTube 视频ID为 11 个字符） |
| 用户名 | `"exampleuser"`、`"sampleuser123"` |
| 显示名称 | `"示例频道"`、`"示例作者"` |
| URL | 使用平台的标准 URL 格式与假 ID |
| 日期 | `"2025-01-15T12:00:00.000Z"`（ISO 8601） |
| 文本内容 | 通用描述性文本，例如 `"这是一个示例描述。"` |

### 视图部分

- `transformation.fields`：列出 8–12 个最重要的字段名（顺序 = UI 中的列顺序）
- `display.properties`：每个概览字段有一个条目，带有 `label` 和 `format`
- 可用格式：`"text"`、`"number"`、`"date"`、`"link"`、`"boolean"`、`"image"`、`"array"`、`"object"`

选择字段，使用户能够获得最有用的数据概览。

---

## 第三阶段：生成 `key_value_store_schema.json`（如果适用）

**目标**：如果 Actor 将数据存储在键值存储中，则定义键值存储集合

> **跳过此阶段**，如果 Phase 1（除了默认 `INPUT` 键）中没有找到 `Actor.setValue()` / `Actor.set_value()` 调用。

### 文件结构

```json
{
    "actorKeyValueStoreSchemaVersion": 1,
    "title": "<描述性标题——键值存储包含的内容>",
    "description": "<一句话描述存储的数据>",
    "collections": {
        "<collectionName>": {
            "title": "<人类可读的标题>",
            "description": "<该集合包含的内容>",
            "keyPrefix": "<前缀->"
        }
    }
}
```

### 如何识别集合

按 `setValue` / `set_value` 调用的键模式分组：

1. **固定键**（例如，`"RESULTS"`、`"summary"`）——使用 `"key"`（精确匹配）
2. **带前缀的动态键**（例如，`"screenshot-${id}"`、`f"image-{name}"`）——使用 `"keyPrefix"`

每个组成为一个集合。

### 集合属性

| 属性 | 必填 | 描述 |
|----------|----------|-------------|
| `title` | 是 | 在 UI 标签中显示 |
| `description` | 否 | 在 UI 提示中显示 |
| `key` | 条件性 | 单键集合的精确键（使用 `key` 或 `keyPrefix`，不能同时使用） |
| `keyPrefix` | 条件性 | 多键集合的前缀（使用 `key` 或 `keyPrefix`，不能同时使用） |
| `contentTypes` | 否 | 限制允许的 MIME 类型（例如，`["image/jpeg"]`、`["application/json"]`） |
| `jsonSchema` | 否 | 用于验证 `application/json` 内容的 JSON Schema draft-07 |

### 示例

**单个文件输出（例如，报告）**：
```json
{
    "actorKeyValueStoreSchemaVersion": 1,
    "title": "分析结果",
    "description": "包含分析输出的键值存储",
    "collections": {
        "report": {
            "title": "报告",
            "description": "最终分析报告",
            "key": "REPORT",
            "contentTypes": ["application/json"]
        }
    }
}
```

**带前缀的多个文件（例如，截图）**：
```json
{
    "actorKeyValueStoreSchemaVersion": 1,
    "title": "抓取文件",
    "description": "包含下载文件和截图的键值存储",
    "collections": {
        "screenshots": {
            "title": "截图",
            "description": "抓取期间捕获的页面截图",
            "keyPrefix": "screenshot-",
            "contentTypes": ["image/png", "image/jpeg"]
        },
        "documents": {
            "title": "文档",
            "description": "下载的文档文件",
            "keyPrefix": "doc-",
            "contentTypes": ["application/pdf", "text/html"]
        }
    }
}
```

---

## 第四阶段：生成 `output_schema.json`

**目标**：创建告诉 Apify Console 结果位置的输出模式

对于大多数将数据推送到数据集的 Actor，这是一个最小的文件：

```json
{
    "actorOutputSchemaVersion": 1,
    "title": "<描述性标题——Actor 返回的内容>",
    "description": "<一句话描述输出数据>",
    "properties": {
        "dataset": {
            "type": "string",
            "title": "结果",
            "description": "包含所有抓取数据的集合",
            "template": "{{links.apiDefaultDatasetUrl}}/items"
        }
    }
}
```

> **关键**：每个属性条目**必须**包含 `"type": "string"`——这是 Apify 的特定约定。Apify 元验证器会拒绝没有它的属性（并且会拒绝 `"type": "object"`——这里只允许 `"string"`）。

如果生成了 Phase 3 的 `key_value_store_schema.json`，请添加第二个属性：
```json
"files": {
    "type": "string",
    "title": "文件",
    "description": "包含下载文件的键值存储",
    "template": "{{links.apiDefaultKeyValueStoreUrl}}/keys"
}
```

### 可用的模板变量

- `{{links.apiDefaultDatasetUrl}}` — 默认数据集的 API URL
- `{{links.apiDefaultKeyValueStoreUrl}}` — 默认键值存储的 API URL
- `{{links.publicRunUrl}}` — 公共运行 URL
- `{{links.consoleRunUrl}}` — 控制台运行 URL
- `{{links.apiRunUrl}}` — API 运行 URL
- `{{links.containerRunUrl}}` — 运行内部运行的服务器 URL
- `{{run.defaultDatasetId}}` — 默认数据集的 ID
- `{{run.defaultKeyValueStoreId}}` — 默认键值存储的 ID

---

## 第五阶段：更新 `actor.json`

**目标**：将模式文件连接到 Actor 配置

**操作**：
1. 读取当前的 `actor.json`
2. 添加或更新 `storages.dataset` 引用：
   ```json
   "storages": {
       "dataset": "./dataset_schema.json"
   }
   ```
3. 如果生成了 `key_value_store_schema.json`，请添加引用：
   ```json
   "storages": {
       "dataset": "./dataset_schema.json",
       "keyValueStore": "./key_value_store_schema.json"
   }
   ```
4. 添加或更新 `output` 引用：
   ```json
   "output": "./output_schema.json"
   ```
5. 如果 `actor.json` 中存在内联 `storages.dataset` 或 `storages.keyValueStore` 对象（不是字符串路径），请将它们的内容迁移到相应的模式文件中，并用文件路径字符串替换内联对象

---

## 第六阶段：审查和验证

**目标**：确保正确性和完整性

**检查清单**：
- [ ] **每个**源代码中的输出字段都在 `dataset_schema.json` `fields.properties` 中——不仅是概览视图字段，而是 Actor 可以产生的所有字段
- [ ] 每个字段都有 `"nullable": true`
- [ ] 顶层 `fields` 对象具有 `"additionalProperties": true` 和 `"required": []`
- [ ] `properties` 中的每个嵌套对象也具有 `"additionalProperties": true` 和 `"required": []`
- [ ] 每个字段都有一个 `"description"` 和一个 `"example"`
- [ ] 所有示例值都是匿名的
- [ ] 每个具有 `"nullable"` 的字段都存在 `"type"`
- [ ] 视图列出了 8–12 个最有用的字段，并具有正确的显示格式
- [ ] `output_schema.json` 每个属性都有 `"type": "string"`
- [ ] 如果使用键值存储：`key_value_store_schema.json` 具有与所有 `setValue`/`set_value` 调用匹配的集合
- [ ] 如果使用键值存储：每个集合使用 `key` 或 `keyPrefix`（不能同时使用）
- [ ] `actor.json` 引用了所有生成的模式文件
- [ ] 模式字段名与代码中的实际键匹配（驼峰式/蛇形式一致性）
- [ ] 如果在存储库中找到现有模式，新模式遵循其约定（描述风格、示例格式、视图结构）
- [ ] 模式字段是从现有的类型定义（接口、TypedDicts、dataclasses）派生的（如果可用）——没有重复或不同的字段定义

在将生成的模式写入用户之前，向用户展示审查结果。

---

## 第七阶段：总结

**目标**：记录创建的内容

报告：
- 创建或更新的文件
- 数据集模式中的字段数量
- 键值存储模式中的集合数量（如果生成）
- 选择用于概览视图的字段
- 需要用户澄清的字段（模糊类型、不明确的可空性）
- 建议的下一步（使用 `apify run --user-agent apify-agent-skills/apify-generate-output-schema` 本地测试，在控制台中验证输出选项）
