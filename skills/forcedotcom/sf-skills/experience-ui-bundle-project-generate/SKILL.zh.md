---
name: experience-ui-bundle-project-generate
description: 从模板生成一个最小化、可直接用于开发的SFDX启动项目，而不是手动创建脚手架文件。在开始一个全新的Salesforce UI组件应用（React或Angular）且初始项目必须进行脚手架操作时使用此技能——触发短语包括“创建”、“开始”或“脚手架一个新的UI组件应用”、“生成启动项目”，或使用预构建/启动模板。以下情况不触发：编辑、样式化或向现有应用添加页面或组件（使用experience-ui-bundle-frontend-generate）；配置ui-bundle.json或元数据文件（使用experience-ui-bundle-metadata-generate）；部署到组织（使用experience-ui-bundle-deploy）；当用户明确表示他们想从零开始手动创建脚手架；或当创建一个全新的独立Salesforce项目且也需要完整设置时——迁移会话、连接组织、设置默认值和启用源跟踪（使用salesforce-development插件中的dx-project-create）。
---

# 使用 UI Bundle 模板

在从零开始构建 Salesforce UI bundle 应用之前，先向用户提供一个**预构建的启动模板**。Salesforce CLI 可以通过一条命令生成这些模板——一个完整的、可部署的 SFDX 项目（UI bundle + 工具链 + `npm run setup` 自动化脚本）——所有内容都包含在内。从启动模板开始比手动搭建更快，也更容易出错。

CLI 命令是 `sf template generate project`。

## 第 1 步：提供选择

**确定框架。** 通常情况下，框架已经由调用上下文决定——要么由调用此技能的根/协调技能传递下来，要么在用户请求中说明。使用这个框架。

本技能支持的框架与 `<SKILL_DIR>/references/` 下的参考文件完全一致，每个文件命名为 `<框架>-project-generate.md`（例如 `react` → `<SKILL_DIR>/references/react-project-generate.md`）。这是唯一的权威来源——添加一个框架意味着添加一个参考文件，这里的内容不会改变。

- **如果框架已知**——打开 `<SKILL_DIR>/references/<框架>-project-generate.md`。
- **如果未知**（一个独立的运行，没有人指定框架）——列出 `<SKILL_DIR>/references/`，通过从每个文件名中移除 `-project-generate.md` 后缀来推导出支持的框架集，并要求用户从这些框架中选择一个。如果用户指定了一个没有匹配参考文件的框架，则表示这里不支持——将任务交给 `experience-ui-bundle-app-coordinate` 从头开始搭建。

每个参考文件列出了该框架的 `--template` 标志以及每个启动模板包含的内容。选择一个适合用户受众（内部或外部）的模板。

**如果用户希望从头开始**（或者两个模板都不适用），则停止并让 `experience-ui-bundle-app-coordinate` 搭建一个新项目。这个技能是可选的——不要强制使用模板。

一旦用户做出选择，将选定的 `--template` 标志带入第 2 步。

## 第 2 步：将项目生成到目标根目录

项目内容必须**直接位于目标根 `$DEST`**——因此 `sfdx-project.json` 位于 `$DEST/sfdx-project.json`，没有额外的包装子文件夹。`sf template generate project` 总是将其输出嵌套在 `--name` 子文件夹下，所以 `<SKILL_DIR>/scripts/generate-project.mjs` 生成的内容会进入 `$DEST`，将子文件夹的内容平铺到 `$DEST` 中（在冲突时覆盖任何现有内容），然后删除现在空的子文件夹——所有操作都通过 Node 的 `fs`/`child_process` API 完成，因此它在 Windows cmd/PowerShell 上的运行方式与 macOS/Linux/Git Bash 完全相同。

- `<SKILL_DIR>` = **此技能自身目录的绝对路径**——包含此 `SKILL.md` 的文件夹；从上下文中的技能路径解析它
- **`$NAME`** — 项目名称（仅限字母数字——不能有空格、连字符、下划线或特殊字符）。询问用户。它也命名 UI bundle，因此会出现在项目中。
- **`$DEST`** — 内容落地的目标根目录（使用 `.` 表示当前目录）。
- **`$TEMPLATE`** — 第 1 步中选择的框架参考的 `--template` 标志值（例如 `reactinternalapp`）。

使用实际、字面的值替换 `$NAME`、`$DEST` 和 `$TEMPLATE` 运行脚本——不要使用 shell 变量赋值/插值（`NAME=...` / `$NAME` / `%NAME%` / `$env:NAME`），因为这种语法在不同的 bash、cmd 和 PowerShell 之间有所不同，并且此命令必须在所有三种环境中都能工作：

```sh
node "<SKILL_DIR>/scripts/generate-project.mjs" "<name>" "<dest>" "<template>"
```

脚本在成功时打印 `OK: project root landed at <dest> (...)` 并退出 0。如果 `sf template generate project` 失败、生成的项目没有 `sfdx-project.json` 或平铺操作没有留下有效的项目根，则脚本会以非零状态退出（并带有清晰的 stderr 消息）——停止并显示错误，而不是继续。

`sfdx-project.json` 必须位于 `$DEST/sfdx-project.json`。项目还包含 `package.json`、`force-app/main/default/uiBundles/$NAME/`（UI bundle）、`scripts/`、`config/` 和 `README.md`。参考第 1 步的框架参考文件以了解具体的 bundle 内容。

## 第 3 步：安装依赖（你来做——不要移交未安装的项目）

如果生成的项目**没有** `node_modules`，**在将项目交回之前自己安装依赖**——一个全新的模板在依赖存在之前无法运行（预览/构建/检查都会失败）。用户应该收到一个可以开发的完整项目。

有**多个** `package.json` 文件，每个文件都需要单独安装：
- **项目根** (`$DEST/package.json`)，以及
- `$DEST/force-app/main/default/uiBundles/$NAME/` 下的 UI bundle 目录——这包含预览服务器加载的工具链，因此它也必须有 `node_modules`。

`<SKILL_DIR>/scripts/install-deps.mjs` 会为根目录和每个具有 `package.json` 的 UI bundle 运行 `npm install`（通过 Node 的 `child_process` 并使用显式的 `cwd`——没有 `cd &&` shell 链接），然后验证 `node_modules` 是否安装到所有指定位置：

```sh
node "<SKILL_DIR>/scripts/install-deps.mjs" "<dest>"
```

将第 2 步中的实际 `$DEST` 值替换为 `<dest>`。脚本在成功时打印 `OK: all dependencies installed.` 并退出 0；否则会以非零状态退出并列出失败的安装摘要。bundle 的首次安装是耗时操作；请预期短暂的等待。如果安装失败，请显示错误——不要移交一个半安装的项目。

## 第 4 步：确认并移交

`install-deps.mjs` 已经在步骤 3 中打印了验证摘要（根目录 + 每个 UI bundle 的 `node_modules`）。要自行查看生成的项目，请使用你自己的文件列表/读取工具，而不是 shell 的 `ls`——无论底层 OS shell 如何，这种方式都能完全一致地工作。

项目现在可以开发并部署。如果模板中有 `README.md`，请查看它，看看是否有任何额外的步骤或用户指导。

从这里开始，使用其他 ui-bundle 技能（`experience-ui-bundle-frontend-generate`、`experience-ui-bundle-salesforce-data-access`、`experience-ui-bundle-deploy` 等）针对现在搭建好的项目继续开发——搭建和依赖安装已经完成。

## 注意事项

- 启动模板是**最小的**——没有预置的示例数据或自定义对象。使用其他 ui-bundle 技能构建其余部分。
- 这些模板使用 `uiBundles` 元数据约定。UI bundle 目录和 meta XML 会以传递给 `--name` 的项目名称命名。
- `sf template generate project --help` 如果标志名称发生变化，会列出所有可用的模板。
