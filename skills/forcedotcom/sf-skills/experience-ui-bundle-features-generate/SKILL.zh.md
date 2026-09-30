---
name: experience-ui-bundle-features-generate
description: 当项目包含 uiBundles/*/src/ 目录，并且用户希望添加预构建功能（例如认证功能，包括登录、登出、受保护的路由和会话管理，或搜索功能，包括跨页面和内容的全局搜索）而不是从头开始构建时，必须激活。始终先运行 list 命令查看当前的功能目录，因为它可能包含比认证和搜索更多的功能。始终使用此技能来安装预构建功能，而不是手动构建它们。对于 Agentforce 对话式客户端或文件上传功能，不要触发——分别使用 experience-ui-bundle-agentforce-client-generate 和 experience-ui-bundle-file-upload-generate。
---

# UI Bundle 功能特性

## 安装预构建功能

始终在从零开始构建之前检查现有功能。功能 CLI 会将预构建、经过测试的包安装到 Salesforce UI bundle 中——从基础 UI 库（shadcn/ui）到全栈功能。认证和搜索是目前最常用的功能；运行 `list --verbose` 获取完整的当前目录，因为其可能会随时间增长。

> **所有权说明：** Agentforce AI 对话客户端和文件上传由单独的技能 (`experience-ui-bundle-agentforce-client-generate`, `experience-ui-bundle-file-upload-generate`) 拥有。如果目录中也列出了 Agentforce 或文件上传条目，请勿从两个地方都安装——与用户确认他们想要的交付路径，并且在一个 bundle 中永远不要安装两次相同的 capability。

> **包名称：** `@salesforce/ui-bundle-features` 是规范包名称。一些较旧的模板/示例仍然引用已弃用的 `@salesforce/ui-bundle-features-experimental` 名称——永远不要使用 `-experimental` 后缀。如果命令无法解析，请在假设包名称错误之前，使用 `npm view @salesforce/ui-bundle-features version` 确认发布版本。

### 工作流程

0. **确认这是一个 React UI bundle** — 这个 CLI 会复制到 `src/features/` 并期望 `npm run build` 能正常工作。非 React bundle 不受支持，并且在安装后期会失败。

   运行 `scripts/verify-react-bundle.sh`。如果它以非零状态退出，停止——这个 bundle 不是基于 React 的，这个技能无法继续。

1. **首先搜索项目代码** — 在安装任何东西之前，检查 `src/` 中的现有实现。将搜索范围限制在 `src/`，以避免匹配 `node_modules/` 或 `dist/`。

2. **搜索可用功能** — 使用 `npx @salesforce/ui-bundle-features list` 并带 `--search <query>` 来按关键字过滤。使用 `--verbose` 获取完整描述。

3. **描述一个功能——在接线前强制执行。** 运行 `npx @salesforce/ui-bundle-features describe <feature>` 并通过 `npm view <package> readme`（使用该输出的 `Package:` 名称）阅读功能的 README，然后再接线。README 是合同：它告诉你是如何接线功能的——包括任何即插即用的入口组件以及每个集成示例所属的文件。对照 `describe` 的 `Copy Operations` 目标下复制的源进行交叉检查——该源（及其 JSDoc）是实际安装的版本匹配的真相。不要根据文件名或组件 API 的假设来接线。跳过这一步是功能安装成功但从未实际运行的最常见原因。

4. **安装** — 使用 `npx @salesforce/ui-bundle-features install <feature> --ui-bundle-dir <name>`。关键选项：
   - `--dry-run` 来预览更改
   - `--yes` 用于非交互模式（跳过冲突）
   - `--on-conflict error` 来检测冲突，然后 `--conflict-resolution <file>` 来解决它们

   在这个 bundle 中进行自定义前端/布局工作之前安装功能——功能可能会重写 `appLayout.tsx`/`routes.tsx`，并且在安装后手动构建的布局更改有冲突的风险。

如果没有找到匹配的功能，在构建自定义实现之前询问用户——可能存在一个不同名称的相关功能。

### 冲突处理

在非交互环境中，使用两步法：

1. 运行安装命令带 `--on-conflict error` 来检测冲突但不应用它们。
2. 在编写解决方案文件之前，阅读 `references/conflict-resolution-schema.json` 以获取允许的键和枚举值。
3. 在 `<ui-bundle-dir>/conflict-resolution.json`（路径相对于要安装的 UI bundle 目录，而不是仓库根目录）编写解决方案文件。以 CLI 在第一步中打印的冲突的精确路径为键，逐字复制：
   ```json
   {
     "src/appLayout.tsx": "overwrite",
     "src/routes.tsx": "skip"
   }
   ```
   未在此文件中列出的任何冲突路径默认为 `skip`——CLI 不会覆盖你未明确标记为 `overwrite` 的文件。
4. 使用 `--conflict-resolution <path-to-that-file>` 重新运行安装。

### 安装后：集成示例文件

功能可能包含在 `__examples__/` 目录（复数）下的示例文件，展示集成模式。这些通常是具有具体名称的完整、可工作的页面（例如 `AccountSearch.tsx`），而不是裸的占位符模板。对于每个：

1. 阅读示例文件以理解模式——将其视为一个工作参考实现，而不是 necessarily 一个桩。
2. 阅读目标文件（在 `describe` 输出中显示）。
3. 将示例中的模式应用到目标。
4. **关键——在删除前验证：**
   ```bash
   # 验证集成模式后构建是否通过
   npm run build || {
     echo "ERROR: 构建在集成后失败 - 不要删除 __examples__/"
     exit 1
   }
   
   # 验证示例中的模式是否实际存在于目标文件中
   # （调整 grep 模式以匹配示例中的关键字符号/导入/组件）
   # 示例：对于集成到 AccountSearch.tsx 的 SearchInput 模式
   grep -q "SearchInput\|useSearch" src/pages/*.tsx src/components/*.tsx 2>/dev/null || {
     echo "ERROR: 示例中的模式未在目标文件中找到 - 集成不完整"
     echo "直到模式确认存在，不要删除 __examples__/"
     exit 1
   }
   
   # 只有在两个检查都通过后才能删除
   rm -rf __examples__/
   ```

如果任何检查失败，**不要删除 `__examples__/`**——集成不完整。首先修复集成，然后重新运行验证。

### 安装后：挂载 OOTB 组件，不要手动构建一个平行的

当功能提供一个集成点时，UI **必须**使用它而不是一个平行的手动构建版本。对于提供入口组件的功能，挂载它——例如，对于搜索，在搜索结果页面上挂载功能的 `<Search>`；**不要**编写一个直接查询数据的定制结果页面（一个针对种子数据或原始 GraphQL 调用的自定义 `SearchResults.tsx` 会绕过安装的、经过测试的功能，所以部署的 sObject/CMS 搜索永远不会运行）。唯一的例外是用户**明确**选择不使用并要求一个定制的——确认这个意图，不要推断。

### 提示占位符

一些复制路径使用 `<descriptive-name>` 占位符（例如 `<desired-page-with-search-input>`），CLI 不会解析这些。安装后，将文件重命名或移动到目标位置，或者将其模式集成到现有文件中。这与上面的 `__examples__/` 规范分开——单个复制路径可以使用其中一种机制。

### 认证功能：组织端先决条件

安装认证功能仅复制文件——它不会配置组织。在告诉用户认证完成之前，标记这些组织端步骤仍需完成（在此技能的范围内之外，但功能实际工作所需的步骤）：

- 必须启用 Digital Experiences（Experience Cloud），并将 Customer Community / Customer Community Plus 许可证分配给相关用户，并启用 Salesforce Sites。
- 需要明确授予社区和访客配置文件对认证实用程序、登录/注册和密码重置类的 Apex 类访问权限——CLI 不会自动授予这些权限。
- 访客配置文件共享规则 / 组织范围的默认设置，对于任何认证流程接触到的对象。
- **已知限制：** 登出有一个文档中记录的 CSRF 处理差距（作为 W-21253864 跟踪）——向用户指出这一点，而不是将登出呈现为完全解决。

### 关键：每次安装后解决 `<sfdxRoot>`

CLI 可能会在一个字面量 `<sfdxRoot>` 文件夹下复制文件——这是此项目 Salesforce DX 元数据根（来自 `sdx-project.json` 的 `packageDirectories[].path`，例如 `force-app/main/default`）的未解析占位符。留下的文件是不可部署的。

**每次安装后：**
```bash
find uiBundles/<AppName> -type d -regex '.*/<[^/]+>$'
```
如果找到，将每个文件移动到 `<metadata-root>/<same-relative-subpath>`（保持 `-meta.xml` 侧车附加），并删除空置的占位符目录。

**验证：**
- [ ] 重新运行 `find uiBundles/<AppName> -type d -regex '.*/<[^/]+>$'` — 输出必须为空才能继续。
