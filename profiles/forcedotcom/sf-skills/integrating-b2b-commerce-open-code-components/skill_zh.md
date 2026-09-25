## 使用此技能的时机

当你需要执行以下操作时，请使用此技能：
- 将所有开源B2B Commerce组件集成到商店中
- 向新商店或现有B2B Commerce商店添加开源组件
- 在体验构建器中提供开源代码组件

## 规则

1. **执行前必须解释。** 在运行任何命令之前，你必须告诉用户该命令的作用以及你运行它的原因。不要只显示原始命令并请求权限。用户应该能够阅读你的解释并理解其目的，然后再批准。

## 概述

此技能将官方Salesforce存储库（https://github.com/forcedotcom/b2b-commerce-open-source-components）中的所有开源B2B Commerce组件复制到B2B Commerce商店的站点元数据中。集成后，这些组件将出现在体验构建器组件调色板中。

---

## 启动流程

当此技能被触发时，在复制之前自动执行以下检查。

### 检查0：解析包目录

读取`sfdx-project.json`并选择活动的包目录。提取`packageDirectories[]`并使用标记为默认的条目；如果没有条目被标记为默认，则使用第一个条目。将此值作为下方所有地方的`<package-dir>`使用。如果`sfdx-project.json`丢失或没有`packageDirectories`，则告诉用户并中止。

### 检查1：开源存储库

验证存储库是否克隆在`.tmp/b2b-commerce-open-source-components`：

1. **如果目录不存在：** 告诉用户：“我正在将官方B2B Commerce开源组件存储库从GitHub克隆到本地`.tmp/`文件夹中。这使我们能够访问所有开源代码组件。”
   然后运行：`git clone https://github.com/forcedotcom/b2b-commerce-open-source-components .tmp/b2b-commerce-open-source-components`
2. **如果目录存在**并且包含`force-app/main/default/sfdc_cms__lwc`和`sfdc_cms__label`，则提供选项：
   > “开源存储库已经克隆。您希望如何继续？”
   > 1. **重用现有** — 使用已经克隆的存储库
   > 2. **重新克隆** — 删除并从GitHub克隆新鲜副本
3. **如果目录存在但结构无效：** 告诉用户：“克隆的存储库具有意外的结构。我将删除它并克隆一个新鲜副本。”
   然后删除并重新克隆。
4. **如果克隆失败：** 告知用户并中止

### 检查2：商店和站点元数据

验证已选择商店并且本地可用站点元数据：

1. 告诉用户：“我正在检查您的项目是否已经具有本地B2B商店元数据。”
   检查`<package-dir>/main/default/digitalExperiences/site/`是否包含任何商店目录。
2. **如果商店元数据存在：** 使用它。如果找到多个商店，请要求用户选择一个。
3. **如果未找到商店元数据：** 在委派之前尝试从连接的org中检索：
   1. 运行`sf org list`（或检查`sf config get target-org`）以找到连接的org。要求用户确认或选择一个，如果有一个以上的org。
   2. 列出该org中的`DigitalExperienceBundle`站点包，使用`sf org list metadata --metadata-type DigitalExperienceBundle --target-org <alias>`。过滤到`site/*`条目。
   3. 如果至少存在一个站点包，请要求用户选择一个，然后运行：
      `sf project retrieve start --metadata "DigitalExperienceBundle:site/<storeName>" --target-org <alias>`
      套件将位于`<package-dir>/main/default/digitalExperiences/site/<storeName>/`。
   4. **只有当没有连接的org可用，或者没有找到站点包，或者检索失败时：** 委派给**创建B2B Commerce商店**技能。

**所有检查后的必要状态：**
- **包目录** — 检查0中解析的值（例如，`force-app`）
- **商店名称** — 选择的`fullName`值（例如，`My_B2B_Store1`）
- **站点元数据路径** — `<package-dir>/main/default/digitalExperiences/site/<store-name>/`
- **存储库路径** — `.tmp/b2b-commerce-open-source-components/`

---

## 集成任务

将克隆存储库中的所有组件和标签复制到站点目录：

- **源：** `.tmp/b2b-commerce-open-source-components/force-app/main/default/sfdc_cms__lwc/*`和`sfdc_cms__label/*`（开源存储库自己的布局——始终是`force-app`）
- **目标：** `<package-dir>/main/default/digitalExperiences/site/<store-name>/sfdc_cms__lwc/`和`sfdc_cms__label/`（`<package-dir>`在检查0中解析）

**步骤：**

1. 告诉用户：“我正在检查您的商店的站点元数据中是否已经存在开源代码组件。”
   检查目标目录是否已经包含文件。
2. 如果文件存在，提供选项：
   > “**{store-name}**中已经存在组件。您希望如何继续？”
   > 1. **全部覆盖** — 使用最新从存储库替换所有现有组件
   > 2. **仅复制新** — 跳过现有组件，仅复制尚未存在的组件
3. 告诉用户：“我现在正在将克隆存储库中的所有开源代码LWC组件复制到您的商店的站点元数据目录中。”
   将所有组件目录从源复制到目标。
4. 告诉用户：“我正在复制这些组件所需的关联标签文件。”
   将所有标签目录从源复制到目标。
5. 报告：“复制了X个组件和Y个标签集”

**输出：**
```
✅ 集成完成！

复制到<store-name>：X个组件和Y个标签集

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
> 2. **重新克隆** — 删除并从GitHub克隆新鲜副本

**用户：** “1”

**代理：** “我正在检查您的项目是否已经具有本地B2B商店元数据……”
- ✓ 找到`My_B2B_Store1`的商店元数据

**代理：** “我正在检查您的商店的站点元数据中是否已经存在开源代码组件……”

**代理：** _(文件存在)_
> “**My_B2B_Store1**中已经存在组件。您希望如何继续？”
> 1. **全部覆盖** — 使用最新从存储库替换所有现有组件
> 2. **仅复制新** — 跳过现有组件，仅复制尚未存在的组件

**用户：** “1”

**代理：** “我现在正在将克隆存储库中的所有开源代码LWC组件复制到您的商店的站点元数据目录中……”
**代理：** “我正在复制这些组件所需的关联标签文件……”
- ✓ 复制了45个组件和38个标签集

```
✅ 集成完成！

复制到My_B2B_Store1：45个组件和38个标签集

下一步：
1. 部署：sf project deploy start -d force-app/main/default/digitalExperiences/site/My_B2B_Store1
2. 打开体验构建器并使用调色板中的新组件
3. 准备好后发布您的站点
```

---

## 错误处理

| 错误 | 消息 | 操作 |
|-------|---------|--------|
| 商店未找到 | “在org中找不到商店'{name}'。” | 再次列出商店 |
| Git克隆失败 | “克隆存储库失败。检查网络连接。” | 重试或中止 |
| 存储库结构无效 | “存储库结构已更改。预期`sfdc_cms__lwc`和`sfdc_cms__label`。” | 警告用户，中止 |
| 文件复制失败 | “复制文件失败。检查文件权限。” | 显示错误详情 |

---

## 验证清单

- [ ] 启动流程完成：存储库克隆，商店元数据可用
- [ ] 组件复制到正确的目标路径（`sfdc_cms__lwc/`）
- [ ] 标签复制到正确的目标路径（`sfdc_cms__label/`）
- [ ] 复制过程中没有文件权限错误
- [ ] 提供了部署命令并告知用户进行测试
