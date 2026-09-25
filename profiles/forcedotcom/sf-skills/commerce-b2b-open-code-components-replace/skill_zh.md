# 用开源代码替换开箱即用的 B2B 商业组件

此技能将站点元数据 `content.json` 文件中的开箱即用（OOTB）B2B 商业组件定义替换为其开源 `site:` 对等组件，或者在不进行更改的情况下查找给定 OOTB 定义的等效开源代码组件。它使用从 `assets/ootb-to-open-code-mapping.json` 加载的权威映射。

## 范围

**模式：** **完全替换** 运行扫描（步骤 1），如果需要则用户选择，然后更新 `content.json`（步骤 2-3）。**仅查找**（用户要求查找等效组件但不更改文件）：应用映射权威规则，并报告命名组件或作用域内 `content.json` 中找到的定义的 OOTB → `site:` — **不要**调用 Write，除非用户确认替换。**视图作用域**工作：将文件发现和读取限制为 `sfdc_cms__view/<视图名>/`（或用户提供的路径），而不是所有视图。

---

## 前置条件

### 解析 `<package-dir>`

读取 `sfdx-project.json` 并选择活动包目录。提取 `packageDirectories[]` 并使用标有 `"default": true` 的条目；如果没有条目被标记为默认，则使用第一个条目。将此值用作 `<package-dir>`，在下方所有地方使用。如果 `sfdx-project.json` 缺失或没有 `packageDirectories`，则通知用户并中止。

### 代理设置

在替换组件之前，委托给 **commerce-b2b-open-code-components-integrate** 技能以确保：

1. 开源代码库克隆在 `.tmp/b2b-commerce-open-source-components`
2. 选择商店并本地检索站点元数据
3. 开源代码组件复制到商店的站点元数据

集成技能拥有 `.tmp/` 克隆的生命周期（它提示用户重用或重新克隆现有的检出）；此技能假定克隆已经存在。

向用户发送纯文本聊天回复（根据规则 1）："在替换组件之前，我需要验证您的商店中的开源代码组件是否已设置。让我检查..."

如果任何前置条件未满足，集成技能将处理它。所有检查通过后，继续替换工作流。

**前置条件后的所需状态：**
- **包目录** — 上面解析的值（例如，`force-app`）
- **商店名称** — 例如，`My_B2B_Store1`
- **站点元数据路径** — `<package-dir>/main/default/digitalExperiences/site/<store-name>/`

---

## 替换工作流

### 步骤 1：扫描站点和映射交叉引用

**此步骤是强制性的。** 在尝试任何替换之前，始终先扫描站点。

向用户发送纯文本聊天回复（根据规则 1）："我正在扫描您商店的站点元数据，以查找当前使用的所有 OOTB 商业组件，并检查哪些有开源代码等效组件。"

**步骤 1a — 查找受影响的文件**（一个命令，简单字面量匹配）：

```bash
grep -rl '"commerce' \
  <package-dir>/main/default/digitalExperiences/site/<store-name>/sfdc_cms__view/ \
  <package-dir>/main/default/digitalExperiences/site/<store-name>/sfdc_cms__themeLayout/ \
  --include="content.json"
```

**步骤 1b — 读取映射并解析匹配的文件。** 将 `assets/ootb-to-open-code-mapping.json` 一次性读入内存。然后，使用 **Read** 工具，解析每个匹配的文件并提取所有以 `commerce` 开头的 `"definition"` 值（例如，`commerce_builder:cartBadge`）。跨所有文件收集一个去重的 OOTB 组件列表。

**步骤 1c — 列出仓库组件**（一个命令）：

```bash
ls .tmp/b2b-commerce-open-source-components/force-app/main/default/sfdc_cms__lwc/
```

使用解析的定义、`ls` 输出和映射表，将每个发现的 OOTB 组件分为三个组：

**向用户显示分解和可选择的列表：**

首先，通知用户关于跳过和未映射的组件：
```text
在您的站点中找到 X 个 OOTB 组件：

在映射表中但未在仓库中（跳过）：
  - commerce_builder:quoteSummary → site:quoteSummary（未在仓库中找到）

没有映射可用（不在映射表中）：
  - commerce_builder:actionButtons
  - commerce_builder:layoutHeaderOne
  - commerce_builder:searchInputContainer
  - commerce_builder:myAccountMegaMenu
```

然后以多选列表的形式向用户展示可替换的组件，以便用户可以通过复选框选择，而不是输入。包括一个 "全部以上" 选项：

```text
您希望替换哪些组件？

[ ] commerce_builder:heading → site:productHeading
[ ] commerce_builder:cartBadge → site:cartBadge
[ ] commerce_builder:searchInput → site:searchInput
[ ] All of the above
```

如果用户在原始请求中提供了特定的组件名称，则预先过滤并跳过选择提示。

### 步骤 2：在 content.json 中替换

向用户发送纯文本聊天回复（根据规则 1）："我现在正在将选定的 OOTB 组件定义替换为您站点 content.json 文件中的其开源代码等效组件。"

受影响的文件已在步骤 1 中确定。对于包含选定组件的每个文件：
1. 使用 **Read** 工具读取文件
2. 对于每个选定的 OOTB 组件，再次确认映射的 **`site:`** 目标存在于开源代码仓库中。仅对通过此检查的替换进行操作。
3. 将所有匹配的 `"definition"` 值替换为它们的映射开源代码等效组件 — **始终**使用映射表中确切的 `site:<name>` 字符串
   - 示例：`"definition": "commerce_builder:heading"` → `"definition": "site:productHeading"`
4. 使用 **Write** 工具保存更新后的文件
5. 保留所有其他 JSON 属性 — 仅 `"definition"` 值会更改

**高效批量处理：** 如果一个文件包含多个 OOTB 组件，请在单个 Read → 修改 → Write 遍中应用所有替换。**不要**多次读取和写入同一个文件。

### 步骤 3：报告

```text
替换完成！

跨 Y 个文件替换了 X 个组件：
- commerce_builder:heading → site:productHeading (3 个文件)
- commerce_builder:cartBadge → site:cartBadge (2 个文件)
- commerce_builder:searchInput → site:searchInput (4 个文件)

跳过（未在仓库中）：
- commerce_builder:quoteSummary

没有映射可用（保持不变）：
- commerce_builder:actionButtons
- commerce_builder:layoutHeaderOne
- commerce_builder:searchInputContainer

修改的文件：
- sfdc_cms__view/Home/content.json
- sfdc_cms__view/Product_Detail/content.json
- sfdc_cms__themeLayout/DefaultTheme/content.json

下一步：
1. 部署：sf project deploy start -d <package-dir>/main/default/digitalExperiences/site/<store-name>
2. 在 Experience Builder 中彻底测试商店
3. 准备好时发布您的站点
```

---

## 示例交互

**用户：** "用开源代码版本替换 OOTB 组件"

**代理：** "在替换组件之前，我需要验证您的商店中的开源代码组件是否已设置。让我检查..."
- [完成] 开源代码库已克隆
- [完成] 商店元数据可用，适用于 My_B2B_Store1
- [完成] 开源代码组件已集成

**代理：** "我正在扫描您商店的站点元数据，以查找所有 OOTB 商业组件，并检查哪些有开源代码等效组件。"

_(运行 grep -rl 以查找包含 commerce 定义的文件，读取这些文件以提取组件名称，运行 ls 以列出仓库组件，然后与映射表交叉引用)_

```text
在您的站点中找到 8 个 OOTB 组件：

没有映射可用（不在映射表中）：
  - commerce_builder:searchInputContainer
  - commerce_builder:layoutHeaderOne
  - commerce_builder:myAccountMegaMenu
  - commerce_builder:actionButtons
```

**代理** _通过多选提示向用户询问：_
```text
您希望替换哪些组件？

[ ] commerce_builder:heading → site:productHeading
[ ] commerce_builder:cartBadge → site:cartBadge
[ ] commerce_builder:searchInput → site:searchInput
[ ] commerce_builder:cartSummary → site:cartSummary
[ ] All of the above
```

**用户：** _(选择 heading 和 cartBadge)_

**代理：** "我现在正在将选定的 OOTB 组件定义替换为您站点 content.json 文件中的其开源代码等效组件。"

_(文件已在扫描中确定 — 每个受影响的文件一个 Read/Write 遍，所有替换批量处理)_

```text
替换完成！

跨 5 个文件替换了 2 个组件：
- commerce_builder:heading → site:productHeading (3 个文件)
- commerce_builder:cartBadge → site:cartBadge (2 个文件)

没有映射可用（保持不变）：
- commerce_builder:searchInputContainer
- commerce_builder:layoutHeaderOne
- commerce_builder:myAccountMegaMenu
- commerce_builder:actionButtons

修改的文件：
- sfdc_cms__view/Home/content.json
- sfdc_cms__view/Product_Detail/content.json
- sfdc_cms__themeLayout/DefaultTheme/content.json

下一步：
1. 部署：sf project deploy start -d force-app/main/default/digitalExperiences/site/My_B2B_Store1
2. 在 Experience Builder 中彻底测试商店
```

---

## 规则

1. **始终在执行前在聊天中解释。** 在每个 Bash 或 Write 工具调用之前，在对话中发送纯文本回复，说明命令将做什么以及为什么。解释**必须**作为正常聊天消息出现在工具调用之前。**不要**将解释嵌入命令本身（没有 `echo` 行，没有 `#` 注释），**不要**在命令前添加它，**不要**仅依赖工具的 `description` 参数 — 该字段不保证对用户可见。解释后，发出工具调用并等待用户批准后再继续。
2. **`assets/ootb-to-open-code-mapping.json` 是唯一的信息来源。** 每个 OOTB → 开源代码映射都来自该文件；**不要**猜测、推断或凭空想象组件名称。每个替换的新的 `"definition"` **必须**是来自文件的精确映射值，该文件始终使用 `site:` 命名空间（例如 `site:productHeading`）。在写入之前，验证映射目标是否存在于克隆的开源代码组件仓库中（在 `.tmp/b2b-commerce-open-source-components/force-app/main/default/sfdc_cms__lwc/`）；如果不存在，则跳过替换并报告为 "未在仓库中"。
3. **使用 Read 和 Write 工具处理 JSON 文件。** 使用 Read 工具解析 `content.json` 文件，使用 Write 工具更新它们。**不要**使用 bash 解析或编辑 JSON — 没有 sed、awk、perl 或正则表达式用于 JSON 内容。Bash 仅用于**简单文件发现**（`grep -rl`、`find`、`ls`）—**从不**用于提取或修改 JSON 值。
4. **最小化命令。** 尽可能将工作批处理到最少的命令中。使用单个 grep 扫描所有文件，使用单个 ls 验证仓库，并为每个文件使用一个 Read/Write 遍。**不要**为每个组件或每个目录运行单独的命令。

---

## 错误处理

| 错误 | 消息 | 操作 |
|------|------|------|
| 前置条件未满足 | "开源代码组件尚未在您的商店中集成。" | 首先运行集成技能 |
| 未找到映射 | "未找到 '{component}' 的映射。" | 显示可用映射，报告为未映射 |
| 组件不在仓库中 | "克隆的仓库中未找到开源代码组件 '{name}'。" | 跳过并通知用户 |
| 站点中没有 OOTB 组件 | "在站点元数据中未找到 OOTB 商业组件。" | 通知用户，无内容可替换 |
| 没有可替换的组件 | "找到的所有 OOTB 组件都是未映射的 — 没有一个可以替换。" | 显示未映射列表，建议检查更新的映射 |
| content.json 解析错误 | "Failed to parse content.json: {file}" | 显示错误，跳过文件，继续剩余文件 |

---

## 验证清单

- [ ] 通过集成技能验证前置条件（仓库、商店、组件）
- [ ] 扫描站点 + 仓库验证 + 映射交叉引用在最少命令中完成（步骤 1）
- [ ] 每个替换使用精确的映射 `site:` 定义，并在写入前验证其在开源代码仓库中存在
- [ ] 在继续之前向用户显示三个类别的分解
- [ ] 用户选择了要替换的组件（或提供了名称）
- [ ] 每个 `content.json` 文件在单个 Read → 修改 → Write 遍中更新
- [ ] 保留 JSON 结构，未引入语法错误
- [ ] 通知用户跳过和未映射的组件
- [ ] 提供部署命令
