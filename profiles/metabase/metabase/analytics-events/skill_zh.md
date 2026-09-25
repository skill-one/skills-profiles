# 前端分析事件功能

此功能帮助你将产品分析（Snowplow）事件添加到 Metabase 前端代码库中，以跟踪用户交互。

## 快速参考

Metabase 中的分析事件使用 Snowplow 并具有类型化的事件模式。简单事件在**使用位置**声明——`trackSimpleEvent` 是通用的，并在调用位置验证负载。

**关键文件：**
- `frontend/src/metabase/analytics/event.ts` - 核心跟踪函数，`trackSimpleEvent` / `trackSchemaEvent`（从 `metabase/analytics` 导入）
- `frontend/src/metabase-types/analytics/event.ts` - 仅共享的 `SimpleEventSchema`。**不要在此处添加事件类型**（见下文）
- `frontend/src/metabase-types/analytics/schema.ts` - 模式注册表（仅限自定义/遗留模式）
- 特定功能的 `analytics.ts` 文件 - 你的跟踪函数和任何本地类型所在的文件

## 快速检查清单

添加新分析事件时：

- [ ] 选择事件名称（蛇形命名法，过去式）
- [ ] 在功能的 `analytics.ts` 文件中添加跟踪函数，调用 `trackSimpleEvent()`
- [ ] 将任何字段联合（例如 `"success" | "failure"`）作为同一文件中的本地类型保留
- [ ] 在交互点导入并调用跟踪函数
- [ ] **不要**将事件类型添加到 `metabase-types/analytics/event.ts` 或任何联合中

## 事件模式类型

### 1. 简单事件（最常见）

使用 `SimpleEventSchema` 进行简单跟踪。它支持以下标准字段：

```typescript
type SimpleEventSchema = {
  event: string;                    // 必填：事件名称（蛇形命名法）
  target_id?: number | null;        // 可选：受影响实体的 ID
  triggered_from?: string | null;   // 可选：UI 位置/上下文
  duration_ms?: number | null;      // 可选：以毫秒为单位的持续时间
  result?: string | null;           // 可选：结果（例如，"success"，"failure"）
  event_detail?: string | null;     // 可选：附加详细信息/变体
};
```

**使用场景：** 90% 的事件适用于此模式。用于点击、打开、关闭、创建、删除等。

`trackSimpleEvent` 是通用的，并在传递给它的对象字面量上强制执行此模式：

```typescript
// frontend/src/metabase/analytics/event.ts
export function trackSimpleEvent<
  T extends SimpleEventSchema &
    Record<Exclude<keyof T, keyof SimpleEventSchema>, never>,
>(event: T) {
  trackSchemaEvent("simple_event", event);
}
```

这意味着缺少 `event` 或任何 `SimpleEventSchema` 外的字段会在调用位置导致编译错误。没有单独的事件类型声明，也没有 `satisfies` 子句需要添加——旧的 `ValidateEvent<...>` 辅助函数不再导出，也不属于工作流程。

`trackSchemaEvent` 也是通用的：它将模式名称与负载类型相关联，因此你不能在 `simple_event` 模式下发送仪表板事件。

### 2. 自定义模式（遗留，不再添加事件）

仅在非常特殊的情况下考虑添加新的事件模式。

**示例：** `DashboardEventSchema`，`CleanupEventSchema`，`QuestionEventSchema`

## 分步指南：添加简单事件

### 示例：跟踪用户在表格选择器中应用筛选

#### 第 1 步：创建跟踪函数

在你的功能的 `analytics.ts` 文件中（例如，`enterprise/frontend/src/metabase-enterprise/data-studio/analytics.ts`）：

```typescript
import { trackSimpleEvent } from "metabase/analytics";

export const trackDataStudioTablePickerFiltersApplied = () => {
  trackSimpleEvent({
    event: "data_studio_table_picker_filters_applied",
  });
};

export const trackDataStudioTablePickerFiltersCleared = () => {
  trackSimpleEvent({
    event: "data_studio_table_picker_filters_cleared",
  });
};
```

#### 第 2 步：在组件中使用

在交互点导入并调用跟踪函数：

```typescript
import {
  trackDataStudioTablePickerFiltersApplied,
  trackDataStudioTablePickerFiltersCleared,
} from "metabase-enterprise/data-studio/analytics";

function FilterPopover({ filters, onSubmit }) {
  const handleReset = () => {
    trackDataStudioTablePickerFiltersCleared(); // <- 此处跟踪
    onSubmit(emptyFilters);
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        trackDataStudioTablePickerFiltersApplied(); // <- 此处跟踪
        onSubmit(form);
      }}
    >
      {/* 表单内容 */}
    </form>
  );
}
```

## 使用 SimpleEventSchema 字段

所有以下示例都位于功能的 `analytics.ts` 中——没有任何内容集中注册。

### 示例：具有 target_id 的事件

```typescript
export const trackDataStudioLibraryCreated = (id: CollectionId) => {
  trackSimpleEvent({
    event: "data_studio_library_created",
    target_id: Number(id),
  });
};

// 使用
trackDataStudioLibraryCreated(newLibrary.id);
```

### 示例：具有 triggered_from 的事件

```typescript
// 本地联合，仅当其他功能需要传递相同值时才导出
export type NewButtonLocation = "app-bar" | "empty-collection";

export const trackNewButtonClicked = (location: NewButtonLocation) => {
  trackSimpleEvent({
    event: "new_button_clicked",
    triggered_from: location,
  });
};

// 使用
<Button onClick={() => {
  trackNewButtonClicked("app-bar");
  handleCreate();
}}>
  New
</Button>
```

### 示例：具有 event_detail 的事件

真实示例——`frontend/src/metabase/metadata/pages/shared/analytics.ts`：

```typescript
export type MetadataEditEventDetail =
  | "type_casting"
  | "semantic_type_change"
  | "visibility_change";

export const trackMetadataChange = (detail: MetadataEditEventDetail) => {
  trackSimpleEvent({
    event: "metadata_edited",
    event_detail: detail,
    triggered_from: "admin",
  });
};

// 使用
trackMetadataChange("semantic_type_change");
```

### 示例：具有 result 和 duration 的事件

参见 `frontend/src/metabase/archive/analytics.ts` 以获取此的真实版本。

```typescript
export const trackMoveToTrash = (params: {
  targetId: number | null;
  triggeredFrom: "collection" | "detail_page" | "cleanup_modal";
  durationMs: number | null;
  result: "success" | "failure";
  itemType: "question" | "model" | "metric" | "dashboard";
}) => {
  trackSimpleEvent({
    event: "moved-to-trash",
    target_id: params.targetId,
    triggered_from: params.triggeredFrom,
    duration_ms: params.durationMs,
    result: params.result,
    event_detail: params.itemType,
  });
};

// 使用时计时
const startTime = Date.now();
try {
  await moveToTrash(item);
  trackMoveToTrash({
    targetId: item.id,
    triggeredFrom: "collection",
    durationMs: Date.now() - startTime,
    result: "success",
    itemType: "question",
  });
} catch (error) {
  trackMoveToTrash({
    targetId: item.id,
    triggeredFrom: "collection",
    durationMs: Date.now() - startTime,
    result: "failure",
    itemType: "question",
  });
}
```

## 命名规范

### 事件名称（蛇形命名法）

```typescript
// 良好
"data_studio_library_created"
"table_picker_filters_applied"
"metabot_chat_opened"

// 不良
"DataStudioLibraryCreated"  // 错误的大小写
"tablePickerFiltersApplied" // 错误的大小写
"filters-applied"            // 使用下划线，而不是连字符
```

### 本地字段类型（帕斯卡命名法，以字段命名）

通常不再需要命名 `...Event` 类型。当你确实需要一个联合来表示字段时，以字段命名：

```typescript
// 良好
type MetricDimensionResult = "success" | "failure";     // -> result
export type MetadataEditEventDetail = "type_casting";   // -> event_detail
type NewButtonLocation = "app-bar" | "empty-collection"; // -> triggered_from
```

### 跟踪函数名称（驼峰命名法，以 "track" 为前缀）

```typescript
// 良好
trackDataStudioLibraryCreated
trackTablePickerFiltersApplied
trackMetabotChatOpened

// 不良
DataStudioLibraryCreated      // 缺少 "track" 前缀
track_library_created         // 错误的大小写
logLibraryCreated             // 使用 "track" 前缀
```

## 常见模式

### 模式 1：跨功能共享字段类型

当两个功能发送具有不同 `triggered_from` 的相同事件时，从拥有该功能的 `analytics.ts` 中导出字段联合，并导入它——不要将任何内容提升到 `metabase-types`：

```typescript
// frontend/src/metabase/data-studio/data-model/analytics.ts
import { trackSimpleEvent } from "metabase/analytics";
import type { MetadataEditEventDetail } from "metabase/metadata/pages/shared/analytics";

export function trackMetadataChange(detail: MetadataEditEventDetail) {
  trackSimpleEvent({
    event: "metadata_edited",
    event_detail: detail,
    triggered_from: "data_studio",
  });
}
```

这是可扩展事件设计的要点：企业功能和功能层类型保留在自己的模块中，而不是导入到共享联合中。

### 模式 2：条件跟踪

根据用户操作跟踪不同的事件：

```typescript
const handleSave = async () => {
  if (isNewItem) {
    await createItem(data);
    trackItemCreated(newItem.id);
  } else {
    await updateItem(id, data);
    trackItemUpdated(id);
  }
};
```

## 常见陷阱

### 不要：向简单事件添加自定义字段

```typescript
// 错误 - SimpleEventSchema 不支持自定义字段（这是编译错误）
export const trackFiltersApplied = (filters: FilterState) => {
  trackSimpleEvent({
    event: "filters_applied",
    data_layer: filters.dataLayer,      // ❌ 不在 SimpleEventSchema 中
    data_source: filters.dataSource,    // ❌ 不在 SimpleEventSchema 中
    with_owner: filters.hasOwner,       // ❌ 不在 SimpleEventSchema 中
  });
};

// 正确 - 仅使用标准 SimpleEventSchema 字段
export const trackFiltersApplied = () => {
  trackSimpleEvent({
    event: "filters_applied",
  });
};

// 或者使用 event_detail 表示单个变体
export const trackFilterApplied = (filterType: string) => {
  trackSimpleEvent({
    event: "filter_applied",
    event_detail: filterType,  // ✓ "data_layer"，"data_source" 等
  });
};
```

### 不要：向 `metabase-types/analytics/event.ts` 添加事件类型

中央 `SimpleEvent` 联合已移除——它强制功能层类型导入到共享代码中，导致模块边界违规。`trackSimpleEvent` 现在是通用的，因此类型除了重复外没有其他作用。

```typescript
// ❌ 错误 - 中央声明 + 重新导入用于 `satisfies` 子句
// frontend/src/metabase-types/analytics/event.ts
export type NewFeatureClickedEvent = ValidateEvent<{
  event: "new_feature_clicked";
  target_id: number;
}>;

// frontend/src/metabase/my-feature/analytics.ts
import type { NewFeatureClickedEvent } from "metabase-types/analytics";

export const trackNewFeatureClicked = (id: number) => {
  trackSimpleEvent({
    event: "new_feature_clicked",
    target_id: id,
  } satisfies NewFeatureClickedEvent);
};

// ✓ 正确 - 对象字面量已由通用函数检查
// frontend/src/metabase/my-feature/analytics.ts
export const trackNewFeatureClicked = (id: number) => {
  trackSimpleEvent({
    event: "new_feature_clicked",
    target_id: id,
  });
};
```

一些 `...Event` 类型仍然位于 `metabase-types/analytics/event.ts` 中。它们是重构期间落地的 PR 的遗留物——不要复制它们，也不要添加到它们中。

### 不要：混淆事件名称格式

```typescript
// 错误
event: "dataStudioLibraryCreated"  // camelCase
event: "data-studio-library-created"  // kebab-case
event: "Data_Studio_Library_Created"  // 混合大小写

// 正确
event: "data_studio_library_created"  // snake_case
```

### 不要：跟踪 PII 或敏感数据

```typescript
// 错误 - 不要跟踪用户电子邮件、姓名或敏感数据
trackSimpleEvent({
  event: "user_logged_in",
  event_detail: user.email,  // ❌ PII
});

// 正确 - 仅跟踪非敏感标识符
trackSimpleEvent({
  event: "user_logged_in",
  target_id: user.id,  // ✓ 仅 ID
});
```

### 不要：忘记跟踪成功和失败

```typescript
// 错误 - 仅跟踪成功
try {
  await saveData();
  trackDataSaved();
} catch (error) {
  // ❌ 没有跟踪失败情况
}

// 正确 - 跟踪两种结果
try {
  await saveData();
  trackDataSaved({ result: "success" });
} catch (error) {
  trackDataSaved({ result: "failure" });
}
```

## 测试分析事件

开发过程中，你可以验证事件是否触发：

1. **检查浏览器控制台** - 当 `SNOWPLOW_ENABLED=true` 在开发环境中时，事件会被记录
2. **使用 shouldLogAnalytics** - 在 `metabase/env` 中设置以在控制台中查看所有分析事件
3. **检查 Snowplow 调试器** - Snowplow 事件的浏览器扩展

示例控制台输出：

```
[SNOWPLOW EVENT | event sent:true], data_studio_table_picker_filters_applied
```

## 文件组织

### 放置跟踪函数的位置：

```
跟踪函数及其本地字段类型（新事件位于此处）：
frontend/src/metabase/{feature}/analytics.ts
enterprise/frontend/src/metabase-enterprise/{feature}/analytics.ts

核心跟踪工具：
frontend/src/metabase/analytics/ (从 `metabase/analytics` 导入)

仅共享 SimpleEventSchema —— 此处不再添加新内容：
frontend/src/metabase-types/analytics/event.ts
```

在嵌入 SDK 代码时，使用 `trackSdkSimpleEvent`
(`frontend/src/embedding-sdk-bundle/analytics/snowplow.ts`) 而不是 `trackSimpleEvent`——主应用程序的 `"sp"` 跟踪器在客户的页面上未初始化，因此 `trackSimpleEvent` 的 Snowplow 部分在那里是无操作的。

## 真实世界示例

参考以下文件：

- **简单事件 + 本地字段联合**：`frontend/src/metabase/metadata/pages/shared/analytics.ts`
- **复用其他功能的字段类型**：`frontend/src/metabase/data-studio/data-model/analytics.ts`
- **结果 + 持续时间计时**：`frontend/src/metabase/archive/analytics.ts`
- **企业功能事件**：`enterprise/frontend/src/metabase-enterprise/google_drive/analytics.ts`

## 工作流程总结

1. **确定要跟踪的用户交互**
2. **确定事件名称**（蛇形命名法，描述性）
3. **在功能的 `analytics.ts` 中创建跟踪函数**，调用 `trackSimpleEvent()`
4. **在相同文件中添加本地字段联合**，如果字段具有固定值集
5. **导入并在交互点调用**
6. **测试**事件是否正确触发

## 小贴士

- **保持具体** - `filters_applied` 比 `action_performed` 更好
- **使用过去式** - `library_created` 而不是 `create_library`
- **分组相关事件** - 将功能跟踪函数保留在其 `analytics.ts` 中
- **跟踪有意义的操作** - 不是每个点击都需要跟踪
- **考虑数据** - 你以后想分析什么？
- **保持一致性** - 遵循代码库中现有的命名模式
- **记录上下文** - 使用 `triggered_from` 跟踪操作发生的位置
