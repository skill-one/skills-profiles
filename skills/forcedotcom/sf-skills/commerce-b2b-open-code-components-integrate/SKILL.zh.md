---
name: commerce-b2b-open-code-components-integrate
description: 将 GitHub 上的 Salesforce 官方 B2B Commerce 开源组件库集成到现有店铺的站点元数据中。使用此技能复制库的组件和标签，以便它们在体验构建器中可用。触发条件为：用户请求集成或添加开源代码组件、组件名称为 forcedotcom/b2b-commerce-open-source-components，或希望将官方开源库复制到 B2B 店铺。不触发条件为：用户需要创建或检索 B2B 店铺（使用 commerce-b2b-store-create）、仅映射或替换 OOTB 组件定义（使用 commerce-b2b-open-code-components-replace）、编写自定义 LWC，或执行与该库无关的通用体验构建器工作。
---

## 何时使用此技能

当你需要执行以下操作时，请使用此技能：
- 将所有开源 B2B 商务组件集成到商店中
- 向新商店或现有 B2B 商务商店添加开源组件
- 在体验构建器中提供开源代码组件

## 规则

1. **执行前必须解释。** 在运行任何命令之前，你必须告诉用户该命令的作用以及你运行它的原因。不要只显示原始命令并请求权限。用户应该能够通过你的解释来理解目的，然后再进行批准。

## 概述

此技能将官方 Salesforce 存储库（https://github.com/forcedotcom/b2b-commerce-open-source-components）中的所有开源 B2B 商务组件复制到 B2B 商务商店的站点元数据中。集成后，这些组件将出现在体验构建器的组件调色板中。

---

## 启动流程

当此技能被触发时，在复制之前自动执行以下检查。

### 检查 0：解析包目录

从 Salesforce 项目根目录运行插件的确定性解析器：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-package-directory.py"
```

将其单行标准输出用作下面所有地方的 `<package-dir>`。解析器解析 `sfdx-project.json`，选择具有 `"default": true` 的条目，或者在未声明默认值时选择第一个条目。如果它以非零状态退出，请将它的诊断信息传递给用户并中止；不要猜测包目录或重新实现选择逻辑。

### 检查 1：开源存储库

验证存储库是否克隆在 `.tmp/b2b-commerce-open-source-components`：

1. **如果目录不存在：** 告诉用户：“我将从 GitHub 将官方 B2B 商务开源组件存储库克隆到本地 `.tmp/` 文件夹中。这使我们能够访问所有开源代码组件。”
   然后运行：`git clone https://github.com/forcedotcom/b2b-commerce-open-source-components .tmp/b2b-commerce-open-source-components`
2. **如果目录存在** 并且包含 `force-app/main/default/sfdc_cms__lwc` 和 `sfdc_cms__label`，则提供选项：
   > “开源存储库已经克隆。您希望如何继续？”
   > 1. **重用现有** — 使用已经克隆的存储库
   > 2. **重新克隆** — 删除并从 GitHub 克隆新鲜副本
3. **如果目录存在但结构无效：** 告诉用户：“克隆的存储库具有意外的结构。我将删除它并克隆一个新鲜副本。”
   然后删除并重新克隆。
4. **如果克隆失败：** 通知用户并中止

### 检查 2：商店和站点元数据

验证已选择商店并且本地可用站点元数据：

1. 告诉用户：“我正在检查您的项目是否已经本地具有 B2B 商店元数据。”
   检查 `<package-dir>/main/default/digitalExperiences/site/` 是否包含任何商店目录。
2. **如果商店元数据存在：** 使用它。如果找到多个商店，请要求用户选择一个。
3. **如果未找到商店元数据：** 在委派之前尝试从连接的 org 中检索：
   1. 运行 `sf org list`（或检查 `sf config get target-org`）以找到连接的 org。要求用户确认或选择一个（如果有多个）。
   2. 使用 `sf org list metadata --metadata-type DigitalExperienceBundle --target-org <alias>` 列出该 org 中的 `DigitalExperienceBundle` 站点包。过滤到 `site/*` 条目。
   3. 如果至少存在一个站点包，请要求用户使用哪个，然后运行：
      `sf project retrieve start --metadata "DigitalExperienceBundle:site/<storeName>" --target-org <alias>`
      包将位于 `<package-dir>/main/default/digitalExperiences/site/<storeName>/`。
   4. **只有在没有可用的连接 org，或者没有找到站点包，或者检索失败时：** 委派给 **commerce-b2b-store-create** 技能。

**所有检查后的必要状态：**
- **包目录** — 检查 0 中解析的值（例如，`force-app`）
- **商店名称** — 选择的 `fullName` 值（例如，`My_B2B_Store1`）
- **站点元数据路径** — `<package-dir>/main/default/digitalExperiences/site/<store-name>/`
- **存储库路径** — `.tmp/b2b-commerce-open-source-components/`

---

## 集成任务

将克隆存储库中的所有组件和标签复制到站点目录：

- **源：** `.tmp/b2b-commerce-open-source-components/force-app/main/default/sfdc_cms__lwc/*` 和 `sfdc_cms__label/*`（开源存储库自己的布局——始终是 `force-app`）
- **目标：** `<package-dir>/main/default/digitalExperiences/site/<store-name>/sfdc_cms__lwc/` 和 `sfdc_cms__label/`（检查 0 中解析的 `<package-dir>`）

**步骤：**

1. 告诉用户：“我正在检查您的商店的站点元数据中是否已经存在开源代码组件。”
   检查目标目录是否已经包含文件。
2. 如果文件存在，提供选项：
   > “**{store-name}** 中已经存在组件。您希望如何继续？”
   > 1. **全部覆盖** — 使用最新从存储库替换所有现有组件
   > 2. **仅复制新组件** — 跳过现有组件，仅复制尚未存在的组件
3. 告诉用户：“我现在正在将所有开源代码 LWC 组件从克隆的存储库复制到您的商店的站点元数据目录中。”
   将所有组件目录从源复制到目标。
4. 告诉用户：“我正在复制这些组件所需的关联标签文件。”
   将所有标签目录从源复制到目标。
5. 报告：“复制了 X 个组件和 Y 个标签集”

**输出：**
```text
集成完成！

已复制：X 个组件和 Y 个标签集到 <store-name>

下一步：
1. 部署：sf project deploy start -d <package-dir>/main/default/digitalExperiences/site/<store-name>
2. 打开体验构建器并使用调色板中的新组件
3. 准备好后发布您的站点
```

---

## 示例交互

**用户：** “将开源代码组件集成到我的商店”

**代理：** “我正在检查本地是否已经克隆了开源组件存储库……”

**代理：** _(存储库存在)_
> “开源存储库已经克隆。您希望如何继续？”
> 1. **重用现有** — 使用已经克隆的存储库
> 2. **重新克隆** — 删除并从 GitHub 克隆新鲜副本

**用户：** “1”

**代理：** “我正在检查您的项目是否已经本地具有 B2B 商店元数据……”
- [完成] 找到 My_B2B_Store1 的商店元数据

**代理：** “我正在检查您的商店的站点元数据中是否已经存在开源代码组件……”

**代理：** _(文件存在)_
> “**My_B2B_Store1** 中已经存在组件。您希望如何继续？”
> 1. **全部覆盖** — 使用最新从存储库替换所有现有组件
> 2. **仅复制新组件** — 跳过现有组件，仅复制尚未存在的组件

**用户：** “1”

**代理：** “我现在正在将所有开源代码 LWC 组件从克隆的存储库复制到您的商店的站点元数据目录中……”
**代理：** “我正在复制这些组件所需的关联标签文件……”
- [完成] 复制了 45 个组件和 38 个标签集

```text
集成完成！

已复制：45 个组件和 38 个标签集到 My_B2B_Store1

下一步：
1. 部署：sf project deploy start -d force-app/main/default/digitalExperiences/site/My_B2B_Store1
2. 打开体验构建器并使用调色板中的新组件
3. 准备好后发布您的站点
```

---

## 错误处理

| 错误 | 消息 | 操作 |
|------|------|------|
| 商店未找到 | “在 org 中未找到商店 '{name}'。” | 再次列出商店 |
| Git 克隆失败 | “克隆存储库失败。检查网络连接。” | 重试或中止 |
| 存储库结构无效 | “存储库结构已更改。预期 sfdc_cms__lwc 和 sfdc_cms__label。” | 警告用户，中止 |
| 文件复制失败 | “复制文件失败。检查文件权限。” | 显示错误详情 |

---

## 验证检查清单

- [ ] 启动流程完成：存储库已克隆，商店元数据可用
- [ ] 组件已复制到正确的目标路径（`sfdc_cms__lwc/`）
- [ ] 标签已复制到正确的目标路径（`sfdc_cms__label/`）
- [ ] 复制过程中没有文件权限错误
- [ ] 提供了部署命令并告知用户进行测试
