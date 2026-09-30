---
name: prisma-orm-setup
description: 在应用程序中配置 Prisma ORM，连接其数据库，或排查现有 Prisma 6、7 或 8 应用的连接问题。新应用程序默认使用 Prisma ORM 8 并加载由该包自带的 prisma-8 技能；现有 Prisma 6/7 应用则保留其当前版本，并提供 PostgreSQL、MySQL、SQLite、SQL Server、CockroachDB、MongoDB 及 Prisma Postgres 的供应商引用。
---

# Prisma ORM 设置

此技能负责设置和连接工作中的 ORM 版本选择。保留应用程序的 ORM 版本和预期数据库。连接修复不需要主要升级。

新应用程序默认使用 **Prisma ORM 8**。详细的 Prisma 8 配置、查询、迁移和运行时代码属于与 ORM 包一同分发的版本化 [prisma-8 技能](https://github.com/prisma/orm/tree/main/skills/prisma-8)。

## 1. 检测起始点

读取包清单、锁定文件、Prisma 配置、模式和应用程序导入。识别 ORM 版本、数据库提供者和运行时。仅 CLI 版本无法识别应用程序版本：Prisma 8 CLI 可以与旧版客户端共存，因此检查 `@prisma/client`、`@prisma/prisma7` 以及模式和配置。

| 起始点                                          | 路径                                                     |
| ------------------------------------------------------- | -------------------------------------------------------- |
| Prisma 8 应用程序                                    | 第 4 步，无需重新初始化                           |
| 没有选择版本的全新应用程序                | 第 3 步                                                   |
| Prisma 6 或 7 应用程序，或显式选择更早的主要版本 | [第 5 步](#5-设置或修复更早的版本)         |

对于全新应用程序，在安装前检查所选 Prisma 8 版本的 [提供者支持](https://www.prisma.io/docs/orm/supported-databases) 和运行时要求。如果提供者不受支持，解释限制并提供显式选择的更早版本。保留请求的数据库；不要无声地回退或虚构一个受支持的靶标。

使用提供的现有数据库。仅在需要 Prisma Postgres 且尚未选择连接时加载 `prisma-postgres-setup`；连接后返回此处。

## 2. 分别处理请求的主要升级

当用户请求主要升级时，加载支持源版本和提供者的工作流。对于 PostgreSQL 7 到 8，使用 [Prisma 迁移指南](https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql)；对于 MongoDB 6 到 8，使用 [prisma-mongodb-upgrade](../prisma-mongodb-upgrade/SKILL.md)。其他提供者需要显式支持的迁移路径。`prisma-upgrade-v7` 覆盖 **6 到 7**；包拥有的 `prisma-8` 升级参考覆盖 8 内的更新。

## 3. 引导全新 Prisma 8 应用程序

检查所选版本的 [运行时要求](https://www.prisma.io/docs/orm/release-status) 和 [初始化指南](https://www.prisma.io/docs/cli/orm-init)。解析并固定已发布的 Prisma CLI **8** 版本，如有必要包括其预发布后缀；初始化前验证其版本。不要依赖浮动 `latest` 保持版本 8。

使用项目的包管理器运行安装的 CLI。对于 PostgreSQL 和 Prisma 模式语言编写：

```bash
prisma orm init --yes --target postgres --authoring psl
```

使用所选提供者的支持目标。保留现有应用程序文件和连接配置；不要让设置提供无关的数据库。在继续之前，验证解析的 ORM 包是版本 8。

## 4. 加载已安装的 Prisma 8 指导

通过项目的包管理器运行已安装的 CLI：

```bash
prisma skills sync
```

然后 **读取** 同步的 `prisma-8/SKILL.md`，例如 `.agents/skills/prisma-8/SKILL.md`，并遵循其先决条件和选定参考。仅同步不会加载说明。如果包拥有的指导无法加载，报告障碍。继续第 6 步。

## 5. 设置或修复更早的版本

对于显式选择更早版本的全新设置，将包固定到该主要版本并使用其运行时要求。保持 CLI、客户端和 SQL 适配器版本兼容。现有依赖项在连接修复时无需更改。

- **Prisma 7 SQL:** 使用下方的提供者参考和 [客户端设置](references/v7-client-setup.md)。
- **Prisma 6 MongoDB:** 使用 [MongoDB 设置](references/v6-mongodb.md)。SQL 驱动适配器不适用。
- **Prisma 6 SQL:** 保留其生成器、模式 URL 和客户端初始化。使用下方的提供者连接细节和 [Prisma 6 文档](https://www.prisma.io/docs/orm/v6)；不要将 Prisma 7 配置或适配器示例复制到其中。

| 数据库                         | 参考                                                 |
| -------------------------------- | --------------------------------------------------------- |
| PostgreSQL                       | [PostgreSQL](references/v7-postgresql.md)                 |
| MySQL / MariaDB / PlanetScale    | [MySQL](references/v7-mysql.md)                           |
| SQLite / Turso                   | [SQLite](references/v7-sqlite.md)                         |
| Microsoft SQL Server / Azure SQL | [SQL Server](references/v7-sqlserver.md)                  |
| CockroachDB                      | [CockroachDB](references/v7-cockroachdb.md)               |
| MongoDB / Atlas on Prisma 6      | [MongoDB](references/v6-mongodb.md)                       |
| Prisma Postgres with Prisma 7    | [Prisma Postgres](references/v7-prisma-postgres.md)       |

Prisma 7 SQL 示例使用 Prisma 7.10.0 验证；MongoDB 示例使用 Prisma 6.19.3。

## 6. 连接和验证

CLI 和应用程序可以加载不同的环境文件。为每个加载预期环境而不打印秘密，并将凭证保留在忽略的环境文件或主机的秘密配置中。对于 SQL 适配器，使适配器的运行时选项与 CLI 连接 URL 指向相同的数据库。

对于现有应用程序，除非请求的工作需要更改，否则保留模式、迁移和生成器配置。在运行模式更改命令前诊断连接。

通过应用程序的客户端对预期数据库运行项目的相关检查和只读查询。报告 ORM 版本、适用的 `prisma-8` 技能版本和查询结果。包安装或成功的技能同步本身不是完成的设置。
