---
name: planetscale-pscale-cli-automation
description: 使用来自自动代理的 PlanetScale CLI (pscale) 并使用 --format json、身份验证检查、pscale sql 以及每个命令的 --force。在直接驱动 pscale 时，应在其他 PlanetScale 技能之前运行。当用户要求自动化 pscale、以无头方式运行 CLI 命令或从代理验证 pscale 身份验证时使用。
---

# PlanetScale CLI自动化

## 目的

教会代理如何非交互式地调用`pscale`。这项技能仅涵盖**CLI约定**。操作工作流（库存、安全审查、模式推荐）使用此存储库中的其他技能——从`../planetscale-safe-orchestrator/SKILL.md`开始进行全面评估。

## 两个AGENTS.md文件（不要混淆它们）

| 文档 | 位置 | 目的 |
|------|------|------|
| **CLI代理指南** | 随`pscale`一起提供（CLI存储库中的`AGENTS.md`，或`pscale agent-guide`） | 如何调用`pscale`：认证、`--format json`、标志位置、`pscale sql` |
| **项目代理指南** | 您的应用程序存储库的`AGENTS.md` | 哪个组织、数据库、分支、引擎、生产分支、MCP范围、审批规则 |

未经操作员批准，请不要编辑项目`AGENTS.md`（参见`../planetscale-mcp-agent-operating-model/SKILL.md`）。

## 初始化（始终从这里开始）

```bash
pscale agent-guide --format json
pscale auth check --format json
```

如果`auth check`返回`"status": "action_required"`，请遵循JSON中的`issues`和`next_steps`。对于登录，人类可能需要在浏览器中批准；使用`pscale auth login --format json`。

## 约定

- 自动化时始终传递**`--format json`**。
- 将**`--org <org>`**放在资源子命令（`database`、`branch`、`sql`、`api`、…）上——而不是放在根`pscale`上。
- 将**位置参数放在标志之前**（`pscale sql mydb main --org bb …`）。
- 使用**`pscale sql`**，而不是`pscale shell`（shell需要一个TTY）。
- 默认SQL角色是**reader**；传递`--role admin`（或writer/readwriter）进行写入。匹配`pscale shell`的`--role`和`--replica`语义。
- **`--force`** 仅对子命令有效（例如`database delete … --force`、`pscale sql … --force`）。没有全局`--force`或`PSCALE_FORCE`。
- **单独的`--format json`永远不会跳过确认**——在破坏性子命令上添加`--force`后，需要明确用户批准。

## 典型工作流

```bash
pscale auth check --format json
pscale org list --format json
pscale database list --org <org> --format json
pscale branch list <database> --org <org> --format json
pscale sql <database> <branch> --org <org> --format json --query "SELECT 1"
```

MySQL默认使用`@primary`（与`pscale shell`相同）；仅对多键空间数据库传递`--keyspace`。

## MCP与CLI

- **MCP客户端**——使用托管的PlanetScale MCP服务器（参见`pscale agent-guide --format json`获取当前URL）。
- **Shell脚本和编码代理**——使用上述`pscale`并带有`--format json`。

## 当这项技能不够用时

安装完整的PlanetScale技能包（如果尚未安装）：

```sh
git clone https://github.com/planetscale/skills.git && cd skills && script/setup
# 或：npx skills add planetscale/skills -g -y
```

然后运行子技能或`../planetscale-safe-orchestrator/SKILL.md`进行基本的CLI调用之外的数据库操作。

## 当前约定来源

优先考虑实时输出而不是记忆标志语法：

```bash
pscale agent-guide --format json
```

嵌入的`guide`字段包含随您的`pscale`二进制文件一起提供的完整CLI代理指南。
