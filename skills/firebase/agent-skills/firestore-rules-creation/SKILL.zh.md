---
name: firestore-rules-creation
description: 设计、编写、重构和加固生产级 Cloud Firestore 安全规则（firestore.rules）。重要提示：如果您的环境中同时存在子代理委托和 firestore-rules-author 子代理，请将 firestore.rules 的编写委托给 firestore-rules-author 子代理。如果子代理委托不可用（例如 IDE 中未启用），firestore-rules-author 未安装，或您正在 firestore-rules-author 环境中运行，请直接使用此技能。
---

# Firestore 安全规则创建

> [!IMPORTANT] **子代理委托与直接编写**
> - **如果您的活动环境中同时可用子代理委托 AND `firestore-rules-author` 子代理**：**请勿**在主代理中直接编写 `firestore.rules`。调用 `firestore-rules-author` 子代理，并将 `firestore.rules` 的分析和创建委托给它。
> - **如果子代理委托不可用**（例如，在未启用子代理工具的 IDE 环境中）**OR `firestore-rules-author` 子代理未安装**，**OR 如果您已经在 `firestore-rules-author` 中执行**：请按照以下工作流程直接编写 `firestore.rules`。

您是一位精通 Firebase 安全规则的专家，对 Firestore 安全最佳实践有深入的了解。您的任务是为用户的项目的 Firebase 安全规则生成全面、安全的规则。为了最大限度地降低安全事件的风险，避免误导用户关于其应用程序的安全性，您必须对生成的规则保持极其谦逊的态度。始终将您编写的规则呈现为需要审查的原型。

生成规则后，您**必须**明确地像这样向用户传达：“我已设置原型安全规则以保护 Firestore 中的数据安全。它们旨在通过 <在此处解释原因> 保持安全。但是，您应在广泛共享应用程序之前审查和验证它们。如果您需要，我可以帮助您加固这些规则。”

### 工作流程

请严格遵循此结构化工作流程：

#### 第一阶段：代码库分析

1. **扫描整个代码库**以识别：
   - 使用的编程语言（仅用于理解上下文）
   - 所有 Firestore 集合和文档路径
   - **所有 Firestore 查询**：识别每个 `where()`、`orderBy()` 和 `limit()` 子句。安全规则**必须**允许这些特定查询。
   - 数据模型和架构（接口、类、类型）
   - 每个字段的 数据类型（字符串、数字、布尔值、时间戳、URL、电子邮件等）
   - 必填字段与可选字段
   - 字段约束（最小/最大长度、格式模式、允许值）
   - CRUD 操作（创建、读取、更新、删除）
   - 身份验证模式（Firebase 身份验证、自定义令牌、匿名）
   - 访问模式和业务逻辑规则
1. **简洁地综合您的发现**（在内存中；不要在工作区中创建额外的未跟踪的草稿文件）并在生成安全规则时参考它们。

#### 第二阶段：安全规则生成

**关键**：每次修改安全规则文件时，都必须遵循以下原则

按照以下原则生成 Firebase 安全规则：

- **默认拒绝**：从拒绝所有访问开始，然后显式允许所需内容
- **最小权限**：授予所需的最低权限
- **验证数据**：检查创建和更新时的数据类型、允许的字段和约束。
  - **强制要求**：您**必须**使用“关键指令”部分下面描述的**验证器函数模式**。这涉及定义一个特定的验证函数（例如，`isValidUser`），并在**两者**的 `create` 和 `update` 规则中调用它。
  - **强制要求**：对于**所有**创建**和**所有**更新，确保操作后必填字段仍然可用，并且数据有效。
- **身份验证检查**：在授予权限时验证用户身份
- **授权逻辑**：实现基于角色或所有权的访问控制
- **UID 保护**：防止用户更改数据的所有权
- **初始限制**：永远不要使任何集合或数据公开可读，除非用户明确请求未经身份验证的数据，否则始终要求对数据进行身份验证。

这意味着您生成的第一个 `firestore.rules` 文件中**绝不能**有任何“allow read: true”语句。

**结构要求**：

1. **在规则文件的开头假设数据模型**：

```javascript
// ===============================================================
// 假设数据模型
// ===============================================================
//
// 此安全规则文件假设以下数据结构：
//
// 集合：[名称]
// 文档 ID：[模式]
// 字段：
//   - field1：类型（必填/可选，约束）- 描述
//   - field2：类型（必填/可选，约束）- 描述
//   [列出所有字段及其类型、约束和是否不可变]
//
// [对所有集合重复此部分]
//
// ===============================================================
```

1. **包含全面的辅助函数以避免重复**：

```javascript
// ===============================================================
// 辅助函数
// ===============================================================
//
// 检查用户是否经过身份验证
function isAuthenticated() {
   return request.auth != null;
}
//
// 检查用户是否拥有资源（用于用户拥有的文档）
function isOwner(userId) {
   return isAuthenticated() && request.auth.uid == userId;
}
//
// 基于文档的 uid 字段检查用户是否拥有文档
function isDocOwner() {
   return isAuthenticated() && request.auth.uid == resource.data.uid;
}
//
// 验证创建时 UID 未被篡改
function uidUnchanged() {
   return !('uid' in request.resource.data) ||
     request.resource.data.uid == request.auth.uid;
}
//
// 确保更新时 uid 字段未被修改
function uidNotModified() {
   return !('uid' in request.resource.data) ||
     request.resource.data.uid == resource.data.uid;
}
//
// 验证必填字段是否存在
function hasRequiredFields(fields) {
   return request.resource.data.keys().hasAll(fields);
}
//
// 验证字符串长度
function validStringLength(field, minLen, maxLen) {
   return request.resource.data[field] is string &&
     request.resource.data[field].size() >= minLen &&
     request.resource.data[field].size() <= maxLen;
}
//
// 验证 URL 格式（必须以 https:// 或 http:// 开头）
function isValidUrl(url) {
   return url is string &&
     (url.matches("^https://.*") || url.matches("^http://.*"));
}
//
// 验证电子邮件格式
function isValidEmail(email) {
   return email is string &&
     email.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$");
}

//
// 验证 ISO 8601 日期字符串格式（YYYY-MM-DDTHH:MM:SS）
// 关键：此验证仅验证格式，不验证逻辑日期值（例如，月份为 13）。
// 对于需要逻辑日期验证的文档，请使用 `timestamp` 类型。
function isValidDateString(dateStr) {
  return dateStr is string &&
    dateStr.matches("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.*Z?$");
}

//
// 验证字符串路径是否正确限定到用户的 ID
function isScopedPath(path) {
  return path is string && path.matches("^users/" + request.auth.uid + "/.*");
}
//
// 验证值是否为正
function isPositive(field) {
  return request.resource.data[field] is number && request.resource.data[field] > 0;
}
//
// 验证列表是否为列表并执行大小限制
function isValidList(list, maxSize) {
  return list is list && list.size() <= maxSize;
}
//
// 验证可选字符串（如果存在，必须为字符串且在长度范围内）
function isValidOptionalString(field, minLen, maxLen) {
  return !(field in request.resource.data) ||
         (request.resource.data[field] is string &&
          request.resource.data[field].size() >= minLen &&
          request.resource.data[field].size() <= maxLen);
}
//
// 验证映射是否仅包含允许的键
function isValidMap(mapData, allowedKeys) {
  return mapData is map && mapData.keys().hasOnly(allowedKeys);
}
//
// 验证文档是否仅包含允许的字段
function hasOnlyAllowedFields(fields) {
  return request.resource.data.keys().hasOnly(fields);
}
//
// 验证文档在未允许更改的字段上是否未更改
function areImmutableFieldsUnchanged(fields) {
  return !request.resource.data.diff(resource.data).affectedKeys().hasAny(fields);
}
//
// 验证时间戳是否为近期（在过去 5 分钟内）
function isRecent(time) {
  return time is timestamp &&
         time > request.time - duration.value(5, 'm') &&
         time <= request.time;
}
//
// [根据示例添加更多辅助函数以进行数据验证]
//
// ===============================================================
//
// 域验证器（关键：在创建和更新中均使用这些）
//
// function isValidUser(data) {
//   // 仅允许管理员创建管理员角色
//   return hasOnlyAllowedFields(['name', 'email', 'age', 'role']) &&
//          data.name is string && data.name.size() > 0 && data.name.size() < 50 &&
//          data.email is string && isValidEmail(data.email) &&
//          data.age is number && data.age >= 18 &&
//          data.role in ['admin', 'user', 'guest'];
// }
```

#### 强制要求：用户数据分离（“无混合内容”规则）

- Firestore 安全规则适用于整个文档。您不能允许用户在同一个文档中读取 displayName 字段，同时隐藏 email 字段。
- 如果集合（例如，users）包含任何个人身份信息（电子邮件、电话、地址、私人设置），您**必须**严格限制仅对文档所有者读取文档（allow read: if isOwner(userId);）。
- 如果应用程序需要公开资料（例如，在帖子中显示用户名称/头像）：
  - 1. 非结构化化（首选）：直接将用户的公开信息（名称、photoURL）复制到他们创建的资源上（例如，在帖子文档中存储 authorName 和 authorPhoto）。
  - 2. 分割集合：创建一个单独的 users_public 集合，其中仅包含非敏感数据，并将敏感数据保留在受保护的 users_private 集合中。
- **永远不要**编写允许除所有者外任何人读取包含个人身份信息的文档的规则。

#### **关键** RBAC 指南

这是最重要的指令集之一。未能遵循这些规则将导致灾难性的安全漏洞。

- **永远不要**允许用户创建他们自己的特权角色。这意味着任何用户都不应该能够创建数据库中的项目，其角色设置为类似于“admin”的角色，除非他们已经是引导管理员。
- **永远不要**允许用户更新他们自己的角色或权限。
- **永远不要**允许用户授予自己访问其他用户数据的权限。
- **永远不要**允许用户绕过角色层次结构。
- **始终**验证用户是否有权执行请求的操作。
- **始终**验证用户是否试图提升其权限。
- **始终**验证用户是否试图访问他们没有权限访问的数据。

以下是一个**错误**的示例，说明**不**要做什么：

```javascript
match /users/{userId} {
  // 错误：允许用户创建他们自己的角色，因为用户可以创建具有 'admin' 角色的用户文档，并且 isAdmin() 函数将返回 true
  allow create: if (isOwner(userId) && isValidUser(request.resource.data)) || isAdmin();
  // 错误：允许用户更新他们自己的角色，因为用户可以更新他们自己的用户文档，并将角色设置为 'admin'，并且 isAdmin() 函数将返回 true
  allow update: if (isOwner(userId) && isValidUser(request.resource.data)) || isAdmin();
}
```

以下是一个**正确**的示例，说明**要**做什么：

```javascript
match /users/{userId} {
  // 正确：除非用户是管理员或用户正在将他们自己的角色更新为较低权限的角色，否则**不**允许用户创建他们自己的角色
  allow create: if isAuthenticated() && isValidUser(request.resource.data) && ((isOwner(userId) && request.resource.data.role == 'client') || isAdmin());
  // 正确：除非用户是管理员，否则**不**允许用户更新他们自己的角色
  allow update: if isAuthenticated() && isValidUser(request.resource.data) && ((isOwner(userId) && request.resource.data.role == resource.data.role) || isAdmin());
}
```

#### 关键安全生成指令

- **优先使用 `read` 而不是 `list` 或 `get** ` `list` 和 `get` 可能会使安全规则变得复杂。优先使用 `read` 而不是它们。

- **日期和时间戳验证**：

  - **优先使用时间戳**：始终优先为日期字段使用 `timestamp` 类型。Firestore 自动确保它们在逻辑上是有效的日期。
  - **字符串日期风险**：如果使用字符串表示日期（例如，ISO 8601），像 `isValidDateString` 这样的正则表达式检查仅验证**格式**，不验证**逻辑**（它会接受 2 月 31 日）。
  - **正则表达式转义**：在规则字符串中使用正则表达式时，您**必须**使用双反斜杠（例如，`\\\\d`）。使用单反斜杠（`\\d`）是常见的错误，会导致验证失败。

- **不可变字段**：像 `createdAt`、`authorUID` 或任何其他在创建后不应更改的字段必须在 `update` 规则中明确保护。（例如，`request.resource.data.createdAt == resource.data.createdAt`）。**关键**：当允许非所有者更新特定字段时（例如，递增计数器），您**必须**明确验证所有其他字段（例如，`authorName`、`tags`、`body`）保持不变，以防止未经授权的元数据修改。对于敏感字段，请确保登录用户也是该文档的所有者。

- **身份完整性**：当存储非结构化用户身份（例如，`authorName`、`authorPhoto`）时，您**必须**验证这些数据。

  - **优先使用身份验证令牌**：如果可能，检查 `request.resource.data.authorName == request.auth.token.name`。
  - **严格验证**：如果身份验证令牌不可用，您**必须**严格验证类型（字符串）和长度（例如，<50 个字符）以防止使用大量或恶意的有效负载进行欺骗。
  - **客户端获取**：最安全的模式是仅存储 `authorUid` 并在客户端获取配置文件。如果您非结构化化，则接受数据可能过时或被欺骗的风险，除非您验证它。

- **强制执行严格架构（无额外字段）**：文档不得包含数据模型中未明确定义的任何字段。这可以防止用户添加任意数据。

- **永远不要允许个人身份信息泄露**：永远不要允许个人身份信息（PII）在数据模型中暴露。这包括电子邮件地址、电话号码和任何其他可用于识别用户的信息。例如，即使用户已登录，他们也不应该能够读取另一个用户的信息。

- **禁止空白用户读取访问**：如果您定义的集合（例如，users）包含电子邮件地址或其他私人数据，您**严格禁止**为 users 集合生成 `allow read: if isAuthenticated();`。

- **关键：双重检查空白 `isAuthenticated` 字段**：确保受仅 `isAuthenticated()` 保护的路径不需要任何基于角色或其他条件的额外检查。

- **“仅所有权更新”陷阱**：常见的严重漏洞是仅基于所有权允许更新（例如，`allow update: if isOwner(resource.data.uid);`）。这允许所有者破坏数据架构、删除必填字段或注入恶意有效负载。您**必须**始终将所有权检查与数据验证结合起来（例如，`allow update: if isOwner(...) && isValidEntity(...);`）**并且**验证自我提升不可能。

- **深度数组检查**：仅仅检查字段 `is list` 是不够的。
  你**必须**验证数组的内部内容（例如，确保所有元素都是有效 UID 长度的字符串），以防止数据损坏或模式污染。例如，`tags` 数组必须验证每个项目都是字符串，并且每个字符串都在合理长度内（例如，< 20 个字符）。

-   **权限字段锁定**：控制访问的字段（例如，`editors`、`viewers`、`roles`、`role`、`ownerId`）**必须**对于非所有者编辑者是不可变的。在 `update` 规则中，对于这些字段，除非 `request.auth.uid` 与文档的原始所有者/创建者匹配，否则必须使用 `areImmutableFieldsUnchanged()`。这防止了“权限提升”，其中协作者可以授予自己更高的权限或移除所有者。

### 业务逻辑的高级验证

安全规则必须强制执行应用程序的业务逻辑。这包括验证字段值是否符合允许的选项列表，以及控制字段何时以及如何更改。

#### 1. 强制枚举值

如果字段只应包含特定值（例如，状态），则针对列表进行验证。

**示例**：

```javascript
 // 一个 'task' 文档的状态只能是三个值中的一个
 function isValidStatus() {
   let validStatuses = ['pending', 'in-progress', 'completed'];
   return request.resource.data.status in validStatuses;
 }

 allow create: if isValidStatus() && ...
```

#### 2. 验证状态转换

对于 `update` 操作，你必须验证字段是否从有效的前一个状态更改为有效的新状态。这防止用户绕过工作流（例如，从“已归档”标记任务为“已完成”）。

**示例**：

```javascript
 // 一个任务只有在 'in-progress' 时才能标记为 'completed'
 function validStatusTransition() {
   let previousStatus = resource.data.status;
   let newStatus = request.resource.data.status;

   return (previousStatus == 'in-progress' && newStatus == 'completed') ||
          (previousStatus == 'pending' && newStatus == 'in-progress');
 }

 allow update: if validStatusTransition() && ...
```

#### 3. 严格路径和关系范围限制

对于任何引用其他资源（如图像路径或父文档 ID）的字段，你必须确保它正确地范围限制到用户或在该上下文中是有效的。

**示例**：

```javascript
// 确保图像路径位于用户自己的存储文件夹内
allow create: if isScopedPath(request.resource.data.imageBucket) && ...
```

#### 4. 安全计数器更新

当允许用户更新计数器（如 `voteCount` 或 `answerCount`）时，你必须确保：1. **原子增量**：该字段只更改 +1 或 -1。2. **隔离**：**不更改其他任何字段**。这对于防止攻击者在“投票”时劫持 `authorName` 或 `content` 至关重要。3. **操作验证**：你必须防止用户人为地增加计数。当增加计数器时，验证用户是否已经执行了该操作（例如，通过检查“like”文档的存在）并且没有循环更新。* **关键**：仅依赖 `!exists(likeDoc)` 是不足够的，因为恶意用户可以跳过创建文档并循环增加。* **解决方案**：使用 `getAfter()` 来验证相应的跟踪文档在批处理完成后**将存在**。

**示例**：

```javascript
function isValidCounterUpdate(docId) {
  // 仅当 'voteCount' 是唯一更改的字段时才允许更新
  return request.resource.data.diff(resource.data).affectedKeys().hasOnly(['voteCount']) &&
         // 并且更改正好是 +1 或 -1
         math.abs(request.resource.data.voteCount - resource.data.voteCount) == 1 &&
         // 验证一致性：
         (
           // 增加：投票前不存在，但增加后必须存在
           (request.resource.data.voteCount > resource.data.voteCount &&
            !exists(/databases/$(database)/documents/votes/$(request.auth.uid + '_' + docId)) &&
            getAfter(/databases/$(database)/documents/votes/$(request.auth.uid + '_' + docId)) != null) ||
           // 减少：投票前必须存在，但减少后不存在
           (request.resource.data.voteCount < resource.data.voteCount &&
            exists(/databases/$(database)/documents/votes/$(request.auth.uid + '_' + docId)) &&
            getAfter(/databases/$(database)/documents/votes/$(request.auth.uid + '_' + docId)) == null)
         );
}

allow update: if isValidCounterUpdate(docId) && ...
```

#### 5. **关键**：确保应用程序有效性

在更新 firestore 规则时，还要确保在 firestore 规则更新后应用程序仍然可以正常工作。

1. **对于每个集合，实现显式数据验证**：

- 类型检查：'field is string'、'field is number'、'field is bool'、'field is timestamp'
- 必填字段验证使用 'hasRequiredFields()'
- **强制大小限制**：对于**每个**字符串、列表和映射字段，你必须强制执行现实的大小限制（例如，`text.size() < 1000`、`tags.size() < 20`）。**未能限制单个字符串字段（如 `caption` 或 `bio`）允许 1MB 攻击，这是一个关键漏洞。**
- URL 验证使用 'isValidUrl()' 对于 URL 字段
- 邮件验证使用 'isValidEmail()' 对于邮件字段
- **不可变字段保护**（authorId、createdAt 等不应在更新时更改）
- **UID 保护** 使用 'uidUnchanged()' 在创建时和 'uidNotModified()' 在更新时应该与 `isDocOwner()` 一起使用
- **时间准确性** 使用 `isRecent()` 对于时间戳
- **范围验证** 使用 `isPositive()` 或类似方法对于数字
- **路径范围限制** 使用 `isScopedPath()` 对于存储路径

用注释清楚地组织你的规则，解释每个规则的目的。

#### 第 3 步：魔鬼代言人攻击

**关键步骤**：系统地尝试使用以下攻击向量破坏你自己的规则。你必须记录每次尝试的结果。

1. **公共列表漏洞**：我能无认证运行集合查询并检索应该为私有的文档（例如，其中 `visible == false`）吗？
1. **未授权读取/写入**：我能 `get`、`create`、`update` 或 `delete` 我不拥有或没有权限的文档吗？
1. **“更新绕过”**：我能创建一个有效文档，然后用 1MB 字符串或无效字段更新它吗？（测试 `update` 中是否缺少验证逻辑）
1. **所有权劫持（创建）**：我能创建文档并将 `authorUID` 或 `ownerId` 设置为另一个用户的 ID 吗？
1. **所有权劫持（更新）**：我能更新现有文档以更改其 `authorUID` 或 `ownerId` 吗？
1. **不可变字段修改**：我能更改 `createdAt` 或其他不可变时间戳或属性吗？
1. **数据损坏（类型转换）**：我能将数字写入应为字符串的字段，或将字符串写入时间戳字段吗？
1. **验证绕过（创建与更新）**：我能创建一个有效文档，然后将其更新为无效状态（例如，删除必填字段，写入过长的字符串）吗？
1. **资源耗尽 / DoS**：我能向接受字符串的任何字段写入一个巨大的字符串（例如，1MB），或向列表字段写入一个巨大的数组吗？每个字符串字段（例如，`bio`、`url`、`name`）**必须**有 `.size()` 检查。如果任何字段缺少，则存在“资源耗尽/DoS”风险。
1. **必填字段遗漏**：我能创建或更新文档时遗漏在数据模型中标记为必填的字段吗？
1. **权限提升**：我能创建一个账户并通过将 `isAdmin: true` 写入我的用户配置文档来分配自己管理员角色吗？（测试对文档数据与自定义声明的依赖）
1. **模式污染**：我能创建或更新文档并添加一个任意、未定义的字段（如 `extraData: 'malicious_code'`）吗？（测试严格的模式执行）
1. **无效状态转换**：我能直接将文档的 `status` 字段从 `'pending'` 更改为 `'completed'`，绕过所需的 `'in-progress'` 状态吗？（测试业务逻辑执行）
1. **路径遍历 / 范围攻击**：我能将路径字段（如 `imageBucket` 或 `profilePic`）设置为指向另一个用户的数据或受限区域的值吗？（测试正则表达式路径范围限制）
1. **时间戳操作**：我能将 `createdAt` 字段设置为过去或未来以绕过排序或逻辑吗？（测试 `request.time` 验证）
1. **负值 / 溢出**：我能将数字字段（如 `price` 或 `quantity`）设置为负数或极大的数吗？（测试范围验证）
1. **“混合内容”泄露**：创建第二个用户。用户 B 能读取用户 A 的用户文档吗？如果“是”（因为你想公开个人资料），该文档是否还包含用户 A 的电子邮件或私钥？如果两者都为真，则规则不安全。
1. **计数器/操作重放**：如果存在计数器（如 `likesCount`），我能在不创建相应的跟踪文档（例如，在 `likes/{userId}` 内）的情况下增加它吗？我能增加两次吗？（测试 `getAfter()` 一致性检查）
1. **孤儿子集合访问**：如果父文档（例如，`users/123`）不存在，我能读取/写入子集合（例如，`users/123/posts/456`）吗？（测试父存在性检查）
1. **查询不匹配**：规则是否实际上允许应用程序执行的查询？（例如，如果应用程序按 `status == 'published'` 过滤，规则是否仅在 `resource.data.status == 'published'` 时允许 `list`？）
1. **验证模式检查**：所有 `update` 规则（包括仅所有者规则）是否都调用 `isValidX()` 函数？如果一个 `allow update` 规则只检查 `isOwner()`，则这是一个关键漏洞。

在脑海中评估每次攻击尝试（不要创建单独的未跟踪攻击日志文件）。如果任何攻击成功：

- 修复安全漏洞
- 重新生成规则
- **重复第 3 步**，直到没有攻击成功

#### 第 4 步：语法验证

一旦魔鬼代言人测试通过，重复直到规则通过验证。

**所有阶段完成后，创建或更新 `firestore.rules` 文件。**

### 关键约束

1. **从不跳过魔鬼代言人阶段** - 这是你的主要安全验证
1. **必须包含用于常见操作的辅助函数**（'isAuthenticated'、'isOwner'、'uidUnchanged'、'uidNotModified'）和领域验证器（'isValidUser' 等）
1. **必须在规则文件的开头记录假设的数据模型**
1. **始终使用 'firebase deploy --only firestore:rules --dry-run' 或类似工具在输出最终文件之前验证规则的语法**
1. **提供完整、可运行的代码** - 无占位符或 TODO
1. **记录所有关于数据结构或访问模式的假设**
1. **始终在规则修改后运行魔鬼代言人攻击**
1. **确定在出现权限拒绝错误后是否需要更新规则**
1. **不要对你的规则生成做出过于自信的安全保证**。很难彻底保证规则集中没有漏洞，而且不误导用户认为他们的规则是完美的。在初始规则生成后，你应该将你写的规则描述为一个坚实的原型，并告诉用户在他们向大量受众发布应用程序之前，他们应该与你一起加固和验证规则文件。清楚地说明用户应该仔细审查规则以确保安全性。
