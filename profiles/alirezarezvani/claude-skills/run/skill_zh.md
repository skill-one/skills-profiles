# /ar:run — 单次实验迭代

运行恰好一个实验迭代：回顾历史，决定一个改动，编辑，提交，评估。

## 使用方法

```
/ar:run engineering/api-speed              # 运行一个迭代
/ar:run                                     # 列出实验，让用户选择
```

## 它的作用

### 第一步：解析实验

如果没有指定实验，将运行 `python {skill_path}/scripts/setup_experiment.py --list` 并让用户选择。

### 第二步：加载上下文

```bash
# 读取实验配置
cat .autoresearch/{domain}/{name}/config.cfg

# 读取策略和约束
cat .autoresearch/{domain}/{name}/program.md

# 读取实验历史
cat .autoresearch/{domain}/{name}/results.tsv

# 切换到实验分支
git checkout autoresearch/{domain}/{name}
```

### 第三步：决定尝试什么

回顾 results.tsv：
- 保留了哪些改动？它们有什么共同模式？
- 舍弃了哪些？避免重复那些方法。
- 哪些崩溃了？理解原因。
- 目前运行了多少次？（相应调整策略）

**策略升级：**
- 运行 1-5 次：低垂的果实（明显的改进）
- 运行 6-15 次：系统性探索（改变一个参数）
- 运行 16-30 次：结构性改动（算法替换）
- 运行 30 次以上：激进实验（完全不同的方法）

### 第四步：做一个改动

仅编辑 config.cfg 中指定的目标文件。改动一件事。保持简单。

### 第五步：提交和评估

```bash
git add {target}
git commit -m "experiment: {改动简短描述}"

python {skill_path}/scripts/run_experiment.py \
  --experiment {domain}/{name} --single
```

### 第六步：报告结果

阅读脚本输出。告诉用户：
- **保留**："改进！{metric}: {value} ({delta} 相较于之前的最佳)"
- **舍弃**："没有改进。{metric}: {value} vs 最佳 {best}。已回滚。"
- **崩溃**："评估失败：{reason}。已回滚。"

### 第七步：自我改进检查

每进行 10 次实验后（检查 results.tsv 行数），更新 program.md 中的策略部分，记录学到的模式。

## 规则

- 每次迭代做一个改动。不要一次改动 5 件事。
- 永远不要修改评估器（evaluate.py）。它是绝对标准。
- 简单性胜利。同等性能但更简单的代码就是改进。
- 没有新的依赖项。
