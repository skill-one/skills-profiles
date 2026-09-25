# 使用 UI Bundle 模板

在从零开始构建 Salesforce UI bundle 应用之前，先向用户提供一个**预构建的启动模板**。Salesforce CLI 可以通过一条命令生成这些模板——一个完整的、可部署的 SFDX 项目（UI bundle + 工具链 + `npm run setup` 自动化脚本）——在一条命令中完成。从启动模板开始比手动搭建更快，也更容易出错。

CLI 命令是 `sf template generate project`。

## 第 1 步：提供选择

**确定框架。** 通常情况下，框架已经由调用上下文决定——要么由调用此技能的根/协调技能传递下来，要么在用户请求中声明。使用那个。

本技能支持的框架是 `<SKILL_DIR>/references/` 下对应的参考文件，每个文件命名为 `<框架>-project-generate.md`（例如 `react` → `<SKILL_DIR>/references/react-project-generate.md`）。这是唯一的真实来源——添加一个框架意味着添加一个参考文件，这里没有其他变化。

- **如果框架已知**——打开 `<SKILL_DIR>/references/<框架>-project-generate.md`。
- **如果未知**（一个独立的运行，没有人指定哪个）——列出 `<SKILL_DIR>/references/`，通过从每个文件名中移除 `-project-generate.md` 后缀来推导出支持的集合，并要求用户从这些中选择一个。如果用户指定了一个没有匹配参考文件的框架，则在这里不支持——将任务交给 `experience-ui-bundle-app-coordinate` 从头开始搭建。

每个参考文件列出了该框架的 `--template` 标志以及每个启动模板包含的内容。选择一个适合用户受众（内部 vs. 外部）的模板。

**如果用户希望从头开始**（或者没有合适的模板），在这里停止，并让 `experience-ui-bundle-app-coordinate` 搭建一个新项目。这个技能是可选的——不要强制使用模板。

一旦用户选择，将选定的 `--template` 标志带入第 2 步。

## 第 2 步：将项目生成到目标根目录

项目内容必须**直接位于目标根 `$DEST`**——因此 `sfdx-project.json` 位于 `$DEST/sfdx-project.json`，没有额外的包装子文件夹。`sf template generate project` 总是将其输出嵌套在 `--name` 子文件夹下，因此生成到 `$DEST` 目录，然后将子文件夹中的内容移动到 `$DEST` 中，在冲突时覆盖任何已存在的内容。最后删除空的子文件夹。

- `<SKILL_DIR>` = **此技能自身目录的绝对路径**——包含此 `SKILL.md` 的文件夹；从上下文中的技能路径解析它
- **`$NAME`** — 项目名称（仅限字母数字——不能有空格、连字符、下划线或特殊字符）。要求用户提供。它也命名 UI bundle，因此会出现在项目中。
- **`$DEST`** — 内容落地的目标根目录（使用 `.` 表示当前目录）。

```sh
NAME=MyApp   # 用户选择的项目名称；也命名 UI bundle
DEST=.       # 目标根目录（内容直接放在这里，没有 NAME/ 包装）

# 第 1 步中选择的框架参考的 --template 标志
TEMPLATE=reactinternalapp   # 示例占位符——用你的第 1 步参考中的标志替换

mkdir -p "$DEST"
sf template generate project --name "$NAME" --template "$TEMPLATE" --output-dir "$DEST"

# 将生成的 $DEST/$NAME 内容扁平化到 $DEST（参见 <SKILL_DIR>/scripts/flatten-project.mjs）。
# 使用绝对技能目录路径——相对的 ./scripts 会相对于 $DEST 解析，而不是技能。
node "<SKILL_DIR>/scripts/flatten-project.mjs" "$DEST/$NAME" "$DEST"
rm -rf "$DEST/$NAME"
```

> `<SKILL_DIR>/scripts/flatten-project.mjs` 将每个生成的条目（包括点文件）移动到 `$DEST`，在冲突时覆盖任何类型的现有文件/目录，同时保留用户已经在 `$DEST` 中的无关文件。每个条目的 `rmSync` + `renameSync` 是确保模板文件在冲突时获胜（包括文件与目录类型不匹配）的关键。

### 验证

生成后，确认内容已位于根目录（不在 `$NAME/` 子文件夹中）：

```sh
test -f "$DEST/sfdx-project.json" && echo "OK: project root landed" || echo "FAILED"
```

`sfdx-project.json` 必须位于 `$DEST/sfdx-project.json`。项目还包含 `package.json`、`force-app/main/default/uiBundles/$NAME/`（UI bundle）、`scripts/`、`config/` 和 `README.md`。参考第 1 步中的框架参考以了解具体的 bundle 内容。如果 `sfdx-project.json` 缺失或位于 `$DEST/$NAME/` 下一级，则扁平化未运行——在继续之前重新检查。

## 第 3 步：安装依赖（你来做——不要移交未安装的项目）

如果生成的项目**没有** `node_modules`，**自己安装依赖**再交回项目**——**一个干净的模板在预览/构建/检查点都失败之前无法运行，直到依赖存在。用户应该收到一个可以开发的完整项目。

有**多个** `package.json` 文件，每个文件都需要单独安装：
- **项目根目录** (`$DEST/package.json`)，以及
- `$DEST/force-app/main/default/uiBundles/$NAME/` 下的 UI bundle 目录——这包含预览服务器加载的工具链，因此它也必须有 `node_modules`。

```sh
# 1. 项目根 ($DEST 在第 2 步中设置)
( cd "$DEST" && npm install )

# 2. 每个 UI bundle
for b in "$DEST"/force-app/main/default/uiBundles/*/; do
  [ -f "$b/package.json" ] && ( cd "$b" && npm install )
done
```

> 首次安装 bundle 是耗时操作；预期会有短暂等待。如果安装失败，请报告它——不要移交一个半安装的项目。

## 第 4 步：确认并移交

验证项目已落地并已安装：

```sh
ls "$DEST" # sfdx-project.json, package.json, force-app/, scripts/, README.md ...
ls "$DEST"/force-app/main/default/uiBundles/*/node_modules >/dev/null && echo "bundle deps installed"
```

项目现在可以开发并部署。如果模板中有 `README.md`，查看它以了解是否有任何额外的步骤或指导给用户。

从这里开始，使用其他 ui-bundle 技能（`experience-ui-bundle-frontend-generate`、`experience-ui-bundle-salesforce-data-access`、`experience-ui-bundle-deploy` 等）针对现在搭建好的项目继续开发——搭建和依赖安装已经完成。

## 注意事项

- 启动模板是**最小的**——没有预置的示例数据或自定义对象。使用其他 ui-bundle 技能构建其余部分。
- 这些模板使用 `uiBundles` 元数据约定。UI bundle 目录和元 XML 以传递给 `--name` 的项目名称命名。
- `sf template generate project --help` 如果标志名称发生变化，会列出所有可用的模板。
