# UI Bundle Features

使用 `@salesforce/ui-bundle-features` CLI 将预构建、经过测试的功能包安装到 Salesforce UI bundle 中，而不是手动构建它们。此文件是 **框架无关的工作流骨干**；特定于框架的细节——例如文件扩展名、功能文件重写、功能入口组件的挂载方式以及构建命令——位于每个框架的参考文件中，位于 `<SKILL_DIR>/references/<framework>/` 下。

在构建任何东西之前，始终检查是否已存在该功能。CLI 是框架无关的：它会将检测到的框架适当的每个功能变体安装到 bundle 中。认证和搜索是最常用的；运行 `list --verbose` 获取完整的当前目录，因为它可能会随时间增长。

> **所有权说明**：Agentforce AI 对话客户端和文件上传由单独的技能 (`experience-ui-bundle-agentforce-client-generate`, `experience-ui-bundle-file-upload-generate`) 拥有。如果目录中也列出了 Agentforce 或文件上传条目，请勿从两个地方都安装它——与用户确认他们想要的交付路径，并且在一个 bundle 中不要重复安装相同的功能。

> **包名**：`@salesforce/ui-bundle-features` 是规范的包名。一些较旧的模板/示例仍然引用已弃用的 `@salesforce/ui-bundle-features-experimental` 名称——切勿使用 `-experimental` 后缀。如果命令无法解析，请在假设包名错误之前使用 `npm view @salesforce/ui-bundle-features version` 确认发布版本。

## 第 0 步：确定框架

`<SKILL_DIR>` = 此技能自己的目录的绝对路径（包含此 `SKILL.md` 的文件夹）；从上下文中的技能路径解析它。

框架通常由调用上下文预先决定——由调用此技能的协调技能传递下来，或在用户请求中声明。使用那个。

此技能支持的框架正好是 `<SKILL_DIR>/references/` 下面的参考文件夹，每个文件夹都包含一个 `features.md`（所以 `react` → `<SKILL_DIR>/references/react/features.md`）。这是单一事实来源——添加框架意味着添加参考文件夹，这里没有变化。

- **如果框架已知**——打开 `<SKILL_DIR>/references/<framework>/features.md` 并将其与此骨干文件一起保留。它提供了示例扩展名、集成目标、挂载示例和构建命令。
- **如果未知**（一个独立的运行，没有人说明）——在询问任何人之前，在 UI bundle 根目录上运行确定性检测器：

  ```bash
  bash "<SKILL_DIR>/scripts/detect-framework.sh" "<path-to-uiBundles/<name>/ dir>"
  ```

  根据退出代码分支（不要解析文本）：
  - `react` 或 `angular`（退出 0）→ 使用该框架。**不要询问用户**——检测是确定性的。打开 `<SKILL_DIR>/references/<framework>/features.md`。
  - `ambiguous`（退出 2）→ 两个框架都存在。列出 `<SKILL_DIR>/references/` 并询问用户要安装到哪个 bundle 中。如果他们指定了一个没有匹配参考文件夹的框架，则在此处不支持——停止。
  - `unknown`（退出 3）→ **未检测到支持的框架。终止。** 报告在 bundle 中未发现 React 或 Angular 的信号，因此无法安装功能，并停止。不要猜测。

在下面的步骤中，`<framework>` 指的是此处选择的文件夹。

## 工作流

1. **首先搜索项目代码**——在安装任何东西之前，检查 `src/` 是否存在现有的实现。将搜索范围限制在 `src/` 中，以避免匹配 `node_modules/` 或 `dist/`。

2. **搜索可用功能**——使用 `npx @salesforce/ui-bundle-features list` 并带有 `--search <query>` 来按关键字过滤。使用 `--verbose` 获取完整描述。

3. **描述功能——在接线前必须执行。** 运行 `npx @salesforce/ui-bundle-features describe <feature>` 并通过 `npm view <package> readme`（使用该输出的 `Package:` 名称）阅读功能的 README（在接线之前）。README 是合同：它告诉您如何接线功能——包括任何即插即用的入口组件以及每个集成示例所属的文件。对照 `describe` 的 `Copy Operations` 目标下复制的源进行交叉检查——该源（及其 JSDoc/注释）是实际安装的版本匹配的真相，在检测到的框架的文件类型中。不要根据文件名或组件 API 的假设来接线。跳过此步骤是功能安装成功但从未实际运行的最常见原因。

4. **安装**——使用 `npx @salesforce/ui-bundle-features install <feature> --ui-bundle-dir <name>`。关键选项：
   - `--dry-run` 以预览更改
   - `--yes` 用于非交互模式（跳过冲突）
   - `--on-conflict error` 以检测冲突，然后 `--conflict-resolution <file>` 以解决它们

   在此 bundle 中进行自定义前端/布局工作之前安装功能——功能可能会重写应用布局和路由文件（请参阅框架参考以获取其名称），并且在手动构建布局更改后安装可能会产生冲突。

如果没有找到匹配的功能，请在构建自定义实现之前询问用户——可能存在一个不同名称的相关功能。

## 冲突处理

在非交互环境中，使用两步法：

1. 运行安装命令并带有 `--on-conflict error` 以检测冲突而不应用它们。
2. 在编写解决方案文件之前，阅读 `references/common/conflict-resolution-schema.json` 以获取允许的键和枚举值。
3. 在 `<ui-bundle-dir>/conflict-resolution.json`（路径相对于要安装的 UI bundle 目录，而不是代码库根目录）编写解决方案文件。按 CLI 在第一步中打印的冲突的精确路径（逐字）进行键入：
   ```json
   {
     "src/appLayout.tsx": "overwrite",
     "src/routes.tsx": "skip"
   }
   ```
   （冲突路径是 CLI 为检测到的框架打印的任何内容——上面的键是说明性的。）未列出的任何冲突路径默认为 `skip`——CLI 不会覆盖您未明确标记为 `overwrite` 的文件。
4. 使用 `--conflict-resolution <path-to-that-file>` 重新运行安装。

## 安装后：集成示例文件

功能可能包括在 `__examples__/` 目录（复数）下的示例文件，展示集成模式。这些通常是具有具体名称的完整、可工作的页面，而不是空的占位符模板——在检测到的框架的文件类型中（请参阅框架参考）。对于每个：

1. 阅读示例文件以了解模式——将其视为一个工作参考实现，而不是必然的桩。
2. 阅读目标文件（在 `describe` 输出中显示）。
3. 将示例中的模式应用到目标。
4. **关键——在删除之前验证：**
   ```bash
   # 使用框架参考中的构建命令验证集成模式后的构建是否通过
   npm run build || {
     echo "ERROR: 集成后构建失败 - 不要删除 __examples__/"
     exit 1
   }

   # 验证示例中的模式是否实际存在于目标中。
   # 调整 grep 以示例中的键符号/导入/组件为基准，覆盖检测到的框架的源文件（请参阅框架参考以获取一个工作模式）。
   ```
   在删除 `__examples__/` 之后，**必须**通过构建通过和模式在目标中确认存在。

如果任何检查失败，**不要删除 `__examples__/`**——集成不完整。首先修复集成，然后重新运行验证。

## 安装后：挂载现成的组件，不要手动编写一个平行的组件

当功能提供集成点时，UI **必须**使用它而不是一个平行的手动编写的版本。对于提供入口组件的功能，挂载它（框架参考显示了挂载模式）；**不要**编写一个直接查询数据的自定义页面。针对种子数据或原始 GraphQL 调用的自定义结果页面绕过了安装的、经过测试的功能，因此部署的 sObject/CMS 逻辑不会运行。唯一的例外是当用户**明确**选择不使用并要求自定义一个时——确认该意图，不要推断。

## 提示占位符

某些复制路径使用 `<descriptive-name>` 描述性名称占位符（例如 `<desired-page-with-search-input>`），CLI 不会解析这些占位符。安装后，将这些文件重命名或移动到目标位置，或将它们的模式集成到现有文件中。这与上面的 `__examples__/` 规范是分开的——单个复制路径可以使用其中一种机制。

## 认证功能：组织端先决条件

安装认证功能仅复制文件——它不会配置组织。这是框架无关的（纯组织/元数据配置）。在告诉用户认证完成之前，标记这些组织端步骤仍需完成（在此技能的范围内之外，但功能实际工作所需的）：

- 必须启用 Digital Experiences（Experience Cloud），并为相关用户分配 Customer Community / Customer Community Plus 许可证，并启用 Salesforce Sites。
- 社区和访客配置文件需要明确授予认证实用程序、登录/注册和密码重置类对 Apex 类的访问权限——CLI 不会自动授予此权限。
- 访客配置文件共享规则 / 组织范围的默认设置，针对认证流程接触到的任何对象。
- **已知限制**：注销有一个记录在案的 CSRF 处理差距（跟踪为 W-21253864）——向用户指出这一点，而不是将注销呈现为完全解决。

## 关键：每次安装后解析 `<sfdxRoot>`

CLI 可能会在一个字面值 `<sfdxRoot>` 文件夹下复制文件——这是此项目 Salesforce DX 元数据根（来自 `sfdx-project.json` 的 `packageDirectories[].path`，例如 `force-app/main/default`）的未解析占位符。留下的文件是不可部署的。这是框架无关的。

**每次安装后：**
```bash
find uiBundles/<AppName> -type d -regex '.*/<[^/]+>$'
```
如果找到，将每个文件移动到 `<metadata-root>/<same-relative-subpath>`（保持 `-meta.xml` 侧车附件），并删除清空的占位符目录。

**验证：**
- [ ] 重新运行 `find uiBundles/<AppName> -type d -regex '.*/<[^/]+>$'`——输出必须为空才能继续。
