# 数据库识别（步骤 5）

根据步骤 3 项目分析产出的 `db_signals` 判断是否需要 RDS。

---

## 判断逻辑

| 信号 | 动作 |
|------|------|
| MySQL 信号（`mysql`/`mysql2`/`sequelize`/`typeorm`/`prisma` + mysql） | AskUserQuestion：新建 RDS / 跳过自行配置 |
| 非 MySQL 数据库（postgres/redis/mongo 等） | 告知用户目前仅自动编排 MySQL RDS，其他需自行配置 |
| 无数据库信号 | 跳过此步骤，直接进入步骤 6 |

---

## 拉取实时可用规格

用户选择新建 RDS 时，从当前地域实时可用的规格里选。此步骤先于实例规格选择执行，尚未确定可用区：
先列出该地域的可用区，再逐个可用区查询按量付费可用的 MySQL 8.0 规格。

```bash
aliyun rds DescribeRegions --RegionId "$REGION"
```

从 `Regions.RDSRegion[]` 收集 `$REGION` 下的各 `ZoneId`，再逐可用区查询：

```bash
aliyun rds DescribeAvailableClasses \
  --RegionId "$REGION" --ZoneId "<zone>" \
  --Engine MySQL --EngineVersion 8.0 \
  --Category Basic --DBInstanceStorageType cloud_essd \
  --CommodityCode bards --OrderType BUY
```

从 `DBInstanceClasses[]` 收集 `DBInstanceClass`（规格 ID）及其 `DBInstanceClassInfos`
里的 vCPU / 内存；汇总各可用区结果去重。

## 降噪过滤

只呈现适合轻量部署的常规规格：排除 vCPU > 8 或内存 > 16 GiB 的超大规格；
去重后按 vCPU→内存升序排序，逐条完整呈现。

## 呈现与选择（AskUserQuestion）

逐条列出规格，每条展示 `规格 ID · vCPU/内存`，让用户选一个。
价格不在此展示（以步骤 9 实时询价为准）。

---

## 产出

- `DB_INSTANCE_CLASS`：用户选择的 RDS 规格 ID（或为空 = 不创建 RDS）
- `DB_PASSWORD`：Agent 生成的随机密码（≥12 位，特殊字符仅 `!@%^*+=_-`），不输出到聊天

---

## 注意事项

- RDS 为 MySQL 8.0，按量付费
- 密码由 Agent 随机生成，通过环境变量传入 `generate_template.py`
- 选择跳过时，用户需自行配置外部数据库连接
