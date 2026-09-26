# /ar:loop — 自动实验循环

启动一个在用户选定的时间间隔内循环运行的实验。

## 使用方法

```
/ar:loop engineering/api-speed             # 启动循环（提示输入间隔）
/ar:loop engineering/api-speed 10m         # 每10分钟
/ar:loop engineering/api-speed 1h          # 每小时
/ar:loop engineering/api-speed daily       # 每日约9点
/ar:loop engineering/api-speed weekly      # 每周一约9点
/ar:loop engineering/api-speed monthly     # 每月1日约9点
/ar:loop stop engineering/api-speed        # 停止活跃的循环
```

## 功能说明

### 第1步：解析实验

如果没有指定实验，则列出实验并让用户选择。

### 第2步：选择间隔

如果未将间隔作为参数提供，则显示选项：

```
选择循环间隔：
  1. 每10分钟  (快速 — 保持监视)
  2. 每小时         (后台 — 之后检查)
  3. 每日约9点      (夜间实验)
  4. 每周一   (长期实验)
  5. 每月1日     (缓慢实验)
```

映射到cron表达式：

| 间隔       | Cron表达式 | 简写 |
|------------|-----------|------|
| 10分钟     | `*/10 * * * *` | `10m` |
| 1小时     | `7 * * * *` | `1h` |
| 每日       | `57 8 * * *` | `daily` |
| 每周       | `57 8 * * 1` | `weekly` |
| 每月       | `57 8 1 * *` | `monthly` |

### 第3步：创建循环任务

使用`CronCreate`并填写实验详情：

```
您正在运行自动实验 "{domain}/{name}"。

1. 读取 .autoresearch/{domain}/{name}/config.cfg 获取：目标、评估命令、指标、指标方向
2. 读取 .autoresearch/{domain}/{name}/program.md 获取策略和约束条件
3. 读取 .autoresearch/{domain}/{name}/results.tsv 获取实验历史
4. 执行：git checkout autoresearch/{domain}/{name}

然后执行一次迭代：
- 查看results.tsv：哪些有效、哪些失败、哪些未尝试
- 修改目标文件进行一次更改（基于运行次数的策略升级）
- 提交：git add {目标文件} && git commit -m "实验：{描述}"
- 评估：python {技能路径}/scripts/run_experiment.py --experiment {domain}/{name} --single
- 阅读输出（保留/丢弃/崩溃）

规则：
- 每个实验仅允许一次更改
- 永远不要修改评估器
- 如果results.tsv中连续5次崩溃，则删除此cron任务（CronDelete）并报警
- 每完成10个实验后，更新program.md中的策略部分

当前最佳指标：{从results.tsv读取或"尚无基准"}|
已完成实验总数：{从results.tsv计数}|
```

### 第4步：存储循环元数据

写入 `.autoresearch/{domain}/{name}/loop.json`：

```json
{
  "cron_id": "{CronCreate生成的ID}",
  "interval": "{用户选择}",
  "started": "{ISO时间戳}",
  "experiment": "{domain}/{name}"
}
```

### 第5步：向用户确认

```
已为 {domain}/{name} 启动循环
  间隔：{间隔描述}
  Cron ID：{ID}
  自动过期：3天（CronCreate限制）

  查看进度：/ar:ar-status
  停止循环： /ar:loop stop {domain}/{name}

  注意：循环任务在3天后自动过期。
  过期后重新运行 /ar:loop 可重启。
```

## 停止循环

当用户运行 `/ar:loop stop {实验}` 时：

1. 读取 `.autoresearch/{domain}/{name}/loop.json` 获取cron ID
2. 调用 `CronDelete` 并使用该ID
3. 删除 `loop.json`
4. 确认："已停止 {实验} 循环。已完成 {n} 个实验。"

## 重要限制

- **3天自动过期**：CronCreate任务在3天后过期。对于更长时间的实验，用户必须重新运行 `/ar:loop` 以重启。结果会保留——新循环会从旧循环停止的地方继续。
- **每个实验一个循环**：不要为同一个实验启动多个循环。
- **并发实验**：多个实验可以同时循环，前提是它们位于不同的git分支（默认情况下每个实验都会获得 `autoresearch/{domain}/{name}` 分支）。
