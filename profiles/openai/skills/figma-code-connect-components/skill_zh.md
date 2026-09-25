# 代码连接组件

## 概述

此技能帮助您使用 Figma 的代码连接功能，将 Figma 设计组件与其对应的代码实现连接起来。它分析 Figma 设计结构，搜索您的代码库以查找匹配的组件，并建立维护设计-代码一致性的映射关系。

## 技能边界

- 使用此技能用于 `get_code_connect_suggestions` + `send_code_connect_mappings` 工作流。
- 如果任务需要使用插件 API 脚本向 Figma 画布写入，请切换到 [figma-use](../figma-use/SKILL.md)。
- 如果任务是从代码或描述中在 Figma 中构建或更新全页屏幕，请切换到 [figma-generate-design](../figma-generate-design/SKILL.md)。
- 如果任务是从 Figma 实现产品代码，请切换到 [figma-implement-design](../figma-implement-design/SKILL.md)。

## 前置条件

- Figma MCP 服务器必须已连接并可访问
- 用户必须提供一个包含节点 ID 的 Figma URL：`https://figma.com/design/:fileKey/:fileName?node-id=1-2`
  - **重要提示：** Figma URL 必须包含 `node-id` 参数。如果没有该参数，代码连接映射将失败。
- **或者** 当使用 `figma-desktop` MCP 时：用户可以直接在 Figma 桌面应用中选择节点（无需 URL）
- **重要提示：** Figma 组件必须发布到团队库。代码连接仅适用于已发布的组件或组件集。
- **重要提示：** 代码连接仅在组织和企业计划中可用。
- 可以访问项目代码库以进行组件扫描

## 必需的工作流

**按顺序执行以下步骤。不要跳过步骤。**

### 第 1 步：获取代码连接建议

调用 `get_code_connect_suggestions` 以一次性识别所有未映射的组件。此工具自动执行以下操作：

- 从 Figma 场景图获取组件信息
- 识别选择中的已发布组件
- 检查现有的代码连接映射并过滤掉已连接的组件
- 返回每个未映射组件的组件名称、属性和缩略图

#### 选项 A：使用 `figma-desktop` MCP（未提供 URL）

如果 `figma-desktop` MCP 服务器已连接且用户**未**提供 Figma URL，请立即调用 `get_code_connect_suggestions`。无需解析 URL——桌面 MCP 服务器会自动使用打开的 Figma 文件中当前选择的节点。

**注意：** 用户必须在 Figma 桌面应用中打开文件并选择一个节点。`fileKey` 不会作为参数传递——服务器会使用当前打开的文件。

#### 选项 B：当提供 Figma URL 时

解析 URL 以提取 `fileKey` 和 `nodeId`，然后调用 `get_code_connect_suggestions`。

**重要提示：** 从 Figma URL 中提取节点 ID 时，需要转换格式：

- URL 格式使用连字符：`node-id=1-2`
- 工具期望使用冒号：`nodeId=1:2`

**解析 Figma URL：**

- URL 格式：`https://figma.com/design/:fileKey/:fileName?node-id=1-2`
- 提取文件密钥：`:fileKey`（`/design/` 后面的部分）
- 从 URL 中提取 `1-2`，然后将其转换为 `1:2` 以供工具使用

```
get_code_connect_suggestions(fileKey=":fileKey", nodeId="1:2")
```

**处理响应：**

- 如果工具返回 **"在此选择中未发现已发布的组件"** → 通知用户并停止。组件可能需要先发布到团队库。
- 如果工具返回 **"此选择中的所有组件实例均已通过 Code Connect 连接到代码"** → 通知用户所有内容均已映射。
- 否则，响应包含未映射组件的列表，每个组件具有：
  - 组件名称
  - 节点 ID
  - 组件属性（JSON 格式，包含属性名称和值）
  - 组件的缩略图（用于视觉检查）

### 第 2 步：扫描代码库以查找匹配的组件

对于 `get_code_connect_suggestions` 返回的每个未映射组件，在代码库中搜索匹配的代码组件。

**查找内容：**

- 与 Figma 组件名称匹配或相似的组件名称
- 与 Figma 层级结构一致的组件结构
- 对应于 Figma 属性的属性（变体、文本、样式）
- 位于典型组件目录中的文件（`src/components/`、`components/`、`ui/` 等）

**搜索策略：**

1. 搜索具有匹配名称的组件文件
2. 读取候选文件以检查结构和属性
3. 将代码组件的属性与第 1 步返回的 Figma 组件属性进行比较
4. 检测编程语言（TypeScript、JavaScript）和框架（React、Vue 等）
5. 基于结构相似性识别最佳匹配，权衡：
   - 属性名称及其与 Figma 属性的对应关系
   - 默认值是否与 Figma 默认值匹配
   - CSS 类或样式对象
   - 说明意图的描述性注释
6. 如果多个候选者同样优秀，选择具有最接近属性接口匹配的组件，并在工具调用前的注释中简要说明理由

**示例搜索模式：**

- 如果 Figma 组件是 "PrimaryButton"，搜索 `Button.tsx`、`PrimaryButton.tsx`、`Button.jsx`
- 检查常用组件路径：`src/components/`、`app/components/`、`lib/ui/`
- 查找匹配 Figma 变体的变体属性，如 `variant`、`size`、`color`

### 第 3 步：向用户展示匹配项

展示您的发现并让用户选择要创建哪些映射。用户可以接受所有、部分或全部建议的映射。

**以以下格式展示匹配项：**

```
以下组件与设计匹配：
- [ComponentName](path/to/component)：DesignComponentName at nodeId [nodeId](figmaUrl?node-id=X-Y)
- [AnotherComponent](path/to/another)：AnotherDesign at nodeId [nodeId2](figmaUrl?node-id=X-Y)

您要连接这些组件吗？您可以接受所有内容、选择特定组件或跳过。
```

**如果未为组件找到确切匹配：**

- 显示 2 个最接近的候选者
- 解释差异
- 询问用户要使用哪个组件或提供正确路径

**如果用户拒绝所有映射**，通知他们并停止。无需进行进一步工具调用。

### 第 4 步：创建代码连接映射

一旦用户确认其选择，请仅使用接受的映射调用 `send_code_connect_mappings`。此工具在单个调用中处理所有映射的批量创建。

**示例：**

```
send_code_connect_mappings(
  fileKey=":fileKey",
  nodeId="1:2",
  mappings=[
    { nodeId: "1:2", componentName: "Button", source: "src/components/Button.tsx", label: "React" },
    { nodeId: "1:5", componentName: "Card", source: "src/components/Card.tsx", label: "React" }
  ]
)
```

**每个映射的关键参数：**

- `nodeId`：Figma 节点 ID（使用冒号格式：`1:2`）
- `componentName`：要连接的组件名称（例如，"Button"、"Card"）
- `source`：代码组件文件的路径（相对于项目根目录）
- `label`：此代码连接映射的框架或语言标签。有效值包括：
  - Web：'React'、'Web Components'、'Vue'、'Svelte'、'Storybook'、'Javascript'
  - iOS：'Swift UIKit'、'Objective-C UIKit'、'SwiftUI'
  - Android：'Compose'、'Java'、'Kotlin'、'Android XML Layout'
  - 跨平台：'Flutter'
  - 文档：'Markdown'

**调用后：**

- 成功：工具确认映射已创建
- 失败：工具报告哪些特定映射失败及其原因（例如，"组件已映射到代码"、"未找到已发布的组件"、"权限不足"）

**处理后提供摘要：**

```
代码连接摘要：
- 成功连接：3
  - Button (1:2) → src/components/Button.tsx
  - Card (1:5) → src/components/Card.tsx
  - Input (1:8) → src/components/Input.tsx
- 无法连接：1
  - CustomWidget (1:10) - 代码库中未找到匹配组件
```

## 示例

### 示例 1：连接一个按钮组件

用户说："将这个 Figma 按钮连接到我的代码：https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15"

**操作：**

1. 解析 URL：fileKey=`kL9xQn2VwM8pYrTb4ZcHjF`，nodeId=`42-15` → 转换为 `42:15`
2. 运行 `get_code_connect_suggestions(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42:15")`
3. 响应显示：一个未映射的 Button 组件，具有 `variant`（primary/secondary）和 `size`（sm/md/lg）属性，以及缩略图
4. 在代码库中搜索 Button 组件：找到 `src/components/Button.tsx`
5. 读取 `Button.tsx` 并确认它具有 `variant` 和 `size` 属性
6. 向用户展示：
   ```
   我找到了一个匹配项：
   - [Button](src/components/Button.tsx)：Button at nodeId [42:15](https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15)

   您要连接此组件吗？
   ```

7. 用户确认："是"
8. 检测到这是一个 TypeScript React 组件
9. 运行 `send_code_connect_mappings(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42:15", mappings=[{ nodeId: "42:15", componentName: "Button", source: "src/components/Button.tsx", label: "React" }])`

**结果：** Figma 按钮组件现在已连接到代码 Button 组件。

### 示例 2：多个组件的部分选择

用户说："连接此框架中的组件：https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Components?node-id=10-50"

**操作：**

1. 解析 URL：fileKey=`pR8mNv5KqXzGwY2JtCfL4D`，nodeId=`10-50` → 转换为 `10:50`
2. 运行 `get_code_connect_suggestions(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10:50")`
3. 响应显示 3 个未映射组件：ProductCard、Badge 和 CustomWidget
4. 在代码库中搜索：
   - ProductCard：找到 `src/components/ProductCard.tsx`（属性匹配）
   - Badge：找到 `src/components/Badge.tsx`（属性匹配）
   - CustomWidget：代码库中未找到匹配组件
5. 向用户展示：
   ```
   以下组件与设计匹配：
   - [ProductCard](src/components/ProductCard.tsx)：ProductCard at nodeId [10:51](https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Components?node-id=10-51)
   - [Badge](src/components/Badge.tsx)：Badge at nodeId [10:52](https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Components?node-id=10-52)

   我未找到 CustomWidget (10:53) 的匹配项。

   您要连接这些组件吗？您可以接受所有内容、选择特定组件或跳过。
   ```

6. 用户："暂时跳过 Badge，只连接 ProductCard"
7. 运行 `send_code_connect_mappings(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10:50", mappings=[{ nodeId: "10:51", componentName: "ProductCard", source: "src/components/ProductCard.tsx", label: "React" }])`

**结果：** 仅按用户的选择连接了 ProductCard。

### 示例 3：组件需要创建

用户说："连接此图标：https://figma.com/design/8yJDMeWDyBz71EnMOSuUiw/Icons?node-id=5-20"

**操作：**

1. 解析 URL：fileKey=`8yJDMeWDyBz71EnMOSuUiw`，nodeId=`5-20` → 转换为 `5:20`
2. 运行 `get_code_connect_suggestions(fileKey="8yJDMeWDyBz71EnMOSuUiw", nodeId="5:20")`
3. 响应显示：CheckIcon 组件（未映射），具有颜色和大小属性
4. 在代码库中搜索 CheckIcon：未找到匹配项
5. 搜索通用 Icon 组件：找到 `src/icons/` 目录中的其他图标
6. 向用户报告："我未找到 CheckIcon 组件，但我在 src/icons/ 找到了一个图标目录。您想：
   - 首先创建一个新的 CheckIcon.tsx 组件，然后连接它
   - 连接到不同的现有图标
   - 如果 CheckIcon 存在于其他地方，请提供其路径"
7. 用户提供路径："src/icons/CheckIcon.tsx"
8. 从文件名检测语言和框架
9. 运行 `send_code_connect_mappings(fileKey="8yJDMeWDyBz71EnMOSuUiw", nodeId="5:20", mappings=[{ nodeId: "5:20", componentName: "CheckIcon", source: "src/icons/CheckIcon.tsx", label: "React" }])`

**结果：** CheckIcon 组件已成功连接到 Figma 设计。

## 最佳实践

### 主动组件发现

不要仅向用户询问文件路径——主动搜索他们的代码库以查找匹配的组件。这能提供更好的体验并捕获潜在的映射机会。

### 准确的结构匹配

当比较 Figma 组件和代码组件时，不要只看名称。检查：

- 属性是否一致（变体类型、大小选项等）
- 组件层级是否匹配（嵌套元素）
- 组件是否具有相同的目的

### 清晰的沟通

在提供创建映射的选项时，清晰地解释：

- 您发现了什么
- 为什么这是一个好的匹配
- 映射将做什么
- 属性将如何连接

### 处理歧义

如果多个组件可能匹配，请提供选项而不是猜测。让用户做出最终决定，选择要连接的组件。

### 优雅的降级

如果您找不到确切匹配，请提供有用的后续步骤：

- 显示接近的候选者
- 建议创建组件
- 请求用户指导

## 常见问题和解决方案

### 问题："在此选择中未发现已发布的组件"

**原因：** Figma 组件未发布到团队库。代码连接仅适用于已发布的组件。
**解决方案：** 用户需要在 Figma 中将组件发布到团队库：

1. 在 Figma 中选择组件或组件集
2. 右键单击并选择 "发布到库" 或使用团队库发布模态框
3. 发布组件
4. 发布后，使用相同的节点 ID 重新尝试代码连接映射

### 问题："代码连接仅在组织和企业计划中可用"

**原因：** 用户的 Figma 计划不包括代码连接访问权限。
**解决方案：** 用户需要升级到组织或企业计划，或联系管理员。

### 问题：代码库中未找到匹配的组件

**原因：** 代码库搜索未找到具有匹配名称或结构的组件。
**解决方案：** 询问用户组件是否以不同名称存在于其他地方或位于不同位置。他们可能需要先创建组件，或者它可能位于一个意想不到的目录。

### 问题："未找到已发布的组件"（CODE_CONNECT_ASSET_NOT_FOUND）

**原因：** 源文件路径不正确，组件不存在于该位置，或组件名称与实际导出名称不匹配。
**解决方案：** 验证源路径是否正确且相对于项目根目录。检查组件是否已从文件中正确导出，并指定确切的 `componentName`。

### 问题："组件已映射到代码"（CODE_CONNECT_MAPPING_ALREADY_EXISTS）

**原因：** 此组件已存在代码连接映射。
**解决方案：** 组件已连接。如果用户想更新映射，他们可能需要先在 Figma 中删除现有映射。

### 问题："权限不足以创建映射"（CODE_CONNECT_INSUFFICIENT_PERMISSIONS）

**原因：** 用户没有对 Figma 文件或库的编辑权限。
**解决方案：** 用户需要编辑包含组件的文件。联系文件所有者或团队管理员。

### 问题：代码连接映射因 URL 错误而失败

**原因：** Figma URL 格式不正确或缺少 `node-id` 参数。
**解决方案：** 验证 URL 是否遵循所需格式：`https://figma.com/design/:fileKey/:fileName?node-id=1-2`。`node-id` 参数是必需的。还请确保将 `1-2` 转换为 `1:2` 以供工具使用。

### 问题：找到多个相似的组件

**原因：** 代码库中包含多个可能匹配 Figma 组件的组件。
**解决方案：** 向用户展示所有候选者及其文件路径，让他们选择要连接的组件。不同的组件可能用于不同的上下文（例如，`Button.tsx` 与 `LinkButton.tsx`）。

## 理解代码连接

代码连接在设计和代码之间建立双向链接：

**对于设计师：** 查看哪些代码组件实现了 Figma 组件
**对于开发者：** 从 Figma 设计直接导航到实现它们的代码
**对于团队：** 维护组件映射的单源事实

您创建的映射通过使这些连接显式且可发现，帮助保持设计和代码同步。

## 额外资源

有关代码连接的更多信息：

- [代码连接文档](https://help.figma.com/hc/en-us/articles/23920389749655-Code-Connect)
- [Figma MCP 服务器工具和提示](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
