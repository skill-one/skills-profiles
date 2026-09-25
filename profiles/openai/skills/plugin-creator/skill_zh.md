# 插件创建器

## 快速入门

1. 运行脚手架脚本：

```bash
  # 插件名称将被规范化为小写连字符形式，且长度必须 <= 64 个字符。
  # 生成的文件夹和 plugin.json 名称始终相同。
# 从仓库根目录运行（或替换 .agents/... 为此 SKILL 的绝对路径）。
# 默认创建在 <repo_root>/plugins/<plugin-name>。
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py <plugin-name>
```

2. 打开 `<plugin-path>/.codex-plugin/plugin.json` 并替换 `[TODO: ...]` 占位符。

3. 当插件需要在 Codex UI 排序中出现时，生成或更新仓库市场入口：

```bash
# marketplace.json 始终位于 <repo-root>/.agents/plugins/marketplace.json
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin --with-marketplace
```

对于本地插件，将 `<home>` 视为根目录并使用：

```bash
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin \
  --path ~/plugins \
  --marketplace-path ~/.agents/plugins/marketplace.json \
  --with-marketplace
```

4. 根据需要生成/调整可选的配套文件夹：

```bash
python3 .agents/skills/plugin-creator/scripts/create_basic_plugin.py my-plugin --path <parent-plugin-directory> \
  --with-skills --with-hooks --with-scripts --with-assets --with-mcp --with-apps --with-marketplace
```

`<parent-plugin-directory>` 是插件文件夹 `<plugin-name>` 将被创建的目录（例如 `~/code/plugins`）。

## 该技能创建的内容

- 如果用户没有明确指定插件位置，则在生成市场条目之前询问他们是否想要仓库本地插件还是本地插件。
- 在 `<parent-plugin-directory>/<plugin-name>/` 创建插件根目录。
- 始终创建 `/<parent-plugin-directory>/<plugin-name>/.codex-plugin/plugin.json`。
- 用完整模式形状、占位符值和完整的 `interface` 部分填充清单。
- 当设置 `--with-marketplace` 时，创建或更新 `<repo-root>/.agents/plugins/marketplace.json`。
  - 如果市场文件还不存在，则在添加第一个插件条目之前，先填充顶层 `name` 和 `interface.displayName` 占位符。
- `<plugin-name>` 使用技能创建器命名规则进行规范化：
  - `My Plugin` → `my-plugin`
  - `My--Plugin` → `my-plugin`
  - 下划线、空格和标点符号转换为 `-`
  - 结果是小写连字符分隔的，连续连字符被压缩
- 支持可选创建：
  - `skills/`
  - `hooks/`
  - `scripts/`
  - `assets/`
  - `.mcp.json`
  - `.app.json`

## 市场流程

- `marketplace.json` 始终位于 `<repo-root>/.agents/plugins/marketplace.json`。
- 对于本地插件，使用 `<home>` 作为根目录的相同约定：
  `~/.agents/plugins/marketplace.json` 加上 `./plugins/<plugin-name>`。
- 市场根元数据支持顶层 `name` 以及可选的 `interface.displayName`。
- 将 `plugins[]` 中的插件顺序视为 Codex 中的渲染顺序。追加新条目，除非用户明确要求重新排序列表。
- `displayName` 属于市场 `interface` 对象内部，而不是单独的 `plugins[]` 条目。
- 每个生成的市场条目必须包含所有：
  - `policy.installation`
  - `policy.authentication`
  - `category`
- 默认新条目为：
  - `policy.installation: "AVAILABLE"`
  - `policy.authentication: "ON_INSTALL"`
- 仅当用户明确指定其他允许值时才覆盖默认值。
- 允许的 `policy.installation` 值：
  - `NOT_AVAILABLE`
  - `AVAILABLE`
  - `INSTALLED_BY_DEFAULT`
- 允许的 `policy.authentication` 值：
  - `ON_INSTALL`
  - `ON_USE`
- 将 `policy.products` 视为覆盖。除非用户明确要求产品限制，否则省略它。
- 生成的插件条目形状为：

```json
{
  "name": "plugin-name",
  "source": {
    "source": "local",
    "path": "./plugins/plugin-name"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

- 仅在故意替换相同插件名称的现有市场条目时使用 `--force`。
- 如果 `<repo-root>/.agents/plugins/marketplace.json` 还不存在，则创建它，包含顶层 `"name"`，一个包含 `"displayName"` 的 `"interface"` 对象，以及 `plugins` 数组，然后添加新条目。

- 对于全新的市场文件，根对象应如下所示：

```json
{
  "name": "[TODO: marketplace-name]",
  "interface": {
    "displayName": "[TODO: Marketplace Display Name]"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": {
        "source": "local",
        "path": "./plugins/plugin-name"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

## 必须行为

- 外层文件夹名称和 `plugin.json` `"name"` 始终是相同的规范化插件名称。
- 不要删除必需的结构；保留 `.codex-plugin/plugin.json`。
- 保持清单值作为占位符，直到人类或后续步骤明确填充它们。
- 如果在现有插件路径内创建文件，仅在覆盖是故意时使用 `--force`。
- 保留任何现有的市场 `interface.displayName`。
- 在生成市场条目时，即使它们的值是默认值，也始终写入 `policy.installation`、`policy.authentication` 和 `category`。
- 仅当用户明确要求该覆盖时，才添加 `policy.products`。
- 保持市场 `source.path` 相对于仓库根目录为 `./plugins/<plugin-name>`。

## 精确规范样本的引用

对于插件清单和市场条目的精确规范样本 JSON，使用：

- `references/plugin-json-spec.md`

## 验证

编辑 `SKILL.md` 后，运行：

```bash
python3 <path-to-skill-creator>/scripts/quick_validate.py .agents/skills/plugin-creator
```
