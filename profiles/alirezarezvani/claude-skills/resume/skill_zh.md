# /ar:resume — 恢复实验

恢复已暂停或受上下文限制的实验。读取所有历史记录，并从您停止的地方继续。

## 使用方法

```
/ar:resume                                  # 列出实验，让用户选择
/ar:resume engineering/api-speed            # 恢复特定实验
```

## 它的作用

### 第一步：如有需要，列出实验

如果没有指定实验：

```bash
python {skill_path}/scripts/setup_experiment.py --list
```

显示每个实验的状态（根据 results.tsv 的年龄判断为活动/暂停/完成），并让用户选择。

### 第二步：加载完整上下文

```bash
# 切换到实验分支
git checkout autoresearch/{domain}/{name}

# 读取配置
cat .autoresearch/{domain}/{name}/config.cfg

# 读取策略
cat .autoresearch/{domain}/{name}/program.md

# 读取完整结果历史
cat .autoresearch/{domain}/{name}/results.tsv

# 读取该分支的最近 git 日志
git log --oneline -20
```

### 第三步：报告当前状态

为用户总结：

```
恢复：engineering/api-speed
  目标：src/api/search.py
  指标：p50_ms（越低越好）
  实验：总共 23 个 — 保留 8 个，丢弃 12 个，3 个崩溃
  最佳：185ms（比基线 320ms 低 42%）
  最后一个实验："添加响应缓存" → 保留（185ms）

  近期模式：
  - 缓存更改：保留 3 个，丢弃 1 个（持续有效）
  - 算法更改：丢弃 2 个，崩溃 1 个（高风险，目前回报低）
  - I/O 优化：保留 2 个（有前景的方向）
```

### 第四步：询问下一步操作

```
您想如何继续？
  1. 单次迭代 (/ar:run)  — 我会做一个更改并评估
  2. 开始循环 (/ar:loop)     — 自动化，按计划间隔执行
  3. 只显示结果    — 我会审查并决定
```

如果用户选择循环，将实验预先选择并交由 `/ar:loop` 处理。
如果选择单次，将交由 `/ar:run` 处理。
