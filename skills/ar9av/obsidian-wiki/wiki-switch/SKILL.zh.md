---
name: wiki-switch
description: 在多个 Obsidian 知识库档案之间切换。当用户说 "/wiki-switch NAME"、"切换到我的工作知识库"、"切换档案"、"更改知识库"、"我在哪个知识库上"、"列出我的知识库"、"显示我的档案"、"创建新的档案配置" 或 "添加新的知识库配置" 时，使用此技能。该技能管理名为 config.NAME 的配置文件，并通过将其符号链接到 <全局配置目录>/config 来激活其中一个。
---

# Wiki Switch — 管理多个 Vault 配置文件

**全局配置目录**。以下所有路径都相对于全局配置目录，根据 `llm-wiki/SKILL.md` 中的配置解析协议进行解析：`$XDG_CONFIG_HOME/obsidian-wiki`（默认 `~/.config/obsidian-wiki`），如果磁盘上已经存在 `~/.obsidian-wiki`，则使用旧版路径。使用以下命令一次性解析：

```bash
CONFIG_DIR="$( [[ -d "$HOME/.obsidian-wiki" && ! -e "${XDG_CONFIG_HOME:-$HOME/.config}/obsidian-wiki" ]] && echo "$HOME/.obsidian-wiki" || echo "${XDG_CONFIG_HOME:-$HOME/.config}/obsidian-wiki" )"
```

每个 Vault 是一个完整的配置文件，位于 `$CONFIG_DIR/config.<name>`。当前活动的 Vault 是 `$CONFIG_DIR/config` 符号链接指向的文件。切换 Vault 意味着重新指向该符号链接。

**切换与内联目标**。`/wiki-switch <name>` 会更改你的**持久默认值**（重新指向符号链接，影响所有未来的请求）。要仅对单个请求使用不同的 Vault 而不更改默认值，请在任何请求中使用内联的 **`@name`** 覆盖（例如 `@work save this`，`wiki-query @personal about X`）。`@name` 覆盖由 `llm-wiki/SKILL.md` 中的**配置解析协议**处理，而不是由这个技能处理——它仅解析 `$CONFIG_DIR/config.<name>` 并不会重新指向符号链接。

## 分发

解析调用并路由到正确的部分：

| 调用 | 动作 |
|---|---|
| `/wiki-switch <name>` | → **切换** |
| `/wiki-switch list` | → **列出** |
| `/wiki-switch show [name]` | → **显示** |
| `/wiki-switch new <name>` | → **新建** |
| `/wiki-switch`（无参数） | → **列出**（视为列出） |
| `@<name> …`（内联，在任何请求中） | → 不是这个技能——**配置解析协议**为单次调用解析该 Vault 而不会重新指向符号链接 |

---

## 切换（默认动作）

激活命名的 Vault 配置文件。

1. 验证 `$CONFIG_DIR/config.<name>` 是否存在。如果不存在，告诉用户 Vault 不存在并运行**列出**以列出可用 Vault。
2. 运行：
   ```bash
   ln -sf "$CONFIG_DIR/config.<name>" "$CONFIG_DIR/config"
   ```
3. 从新激活的配置中读取 `OBSIDIAN_VAULT_PATH`。
4. 向用户确认：
   ```
   切换到 Vault: <name>
   Vault 路径: <config 中 OBSIDIAN_VAULT_PATH 的值>
   ```

---

## 列出

显示所有已注册的 Vault 配置文件以及当前活动的 Vault。

1. 查找所有匹配 `$CONFIG_DIR/config.*` 的文件（排除 `config` 本身——那是符号链接）。
2. 解析当前符号链接目标：`readlink "$CONFIG_DIR/config"`。
3. 对于每个配置文件，读取第一个非空注释行（以 `#` 开头的行）作为 Vault 的人类描述。如果没有注释，则使用文件的后缀作为标签。
4. 显示：
   ```
   Vaults:
     personal   我的个人研究 Wiki    ← 活动
     work       工作项目 Wiki
   ```
   标记活动的一个为 `← 活动`。如果符号链接已损坏或 `config` 不存在，显示 `(无活动)`。

---

## 显示

打印 Vault 的完整配置。

- 如果给定名称，读取 `$CONFIG_DIR/config.<name>`。
- 如果未给定名称，读取 `$CONFIG_DIR/config`（活动的 Vault）。
- 如果文件不存在，告诉用户并列出可用 Vault。
- 原样打印文件内容（编辑包含 `API_KEY` 或 `SECRET` 的行——显示 `***` 而不是值）。

---

## 新建

从当前活动的配置作为模板创建新的 Vault 配置文件。

1. 检查 `$CONFIG_DIR/config.<name>` 是否已存在。如果存在则中止。
2. 复制当前配置：
   ```bash
   cp "$CONFIG_DIR/config" "$CONFIG_DIR/config.<name>"
   ```
3. 读取复制的配置。配置文件使用 `# --- Section name ---` 注释头将字段分组到部分（例如，`# --- Vault-specific ---`，`# --- Vault-independent ---`，`# --- Secrets ---`）。使用这些部分来确定要询问的内容：
   - 标记为 "vault-specific"、"paths" 或类似的字段 → 询问用户新的值
   - 标记为 "vault-independent"、"global"、"shared" 的字段 → 保持不变（原样复制）
   - 标记为 "secrets" 的字段 → 询问新 Vault 是否使用相同的凭证或不同的凭证
   - 如果没有部分头，显示所有字段并让用户决定要更改哪些
4. 询问用户 Vault 特定字段的更新值。使用当前值作为可见默认值——用户只需提供不同的部分。
5. 将更新值写入 `$CONFIG_DIR/config.<name>`。
6. 更新顶部注释行以描述新 Vault（例如，`# Obsidian Wiki — <name> Vault`）。
7. 确认：
   ```
   创建: $CONFIG_DIR/config.<name>
   运行 `/wiki-switch <name>` 激活它，然后运行 `wiki-setup` 初始化新的 Vault。
   ```
   不要自动切换——让用户决定何时激活。
