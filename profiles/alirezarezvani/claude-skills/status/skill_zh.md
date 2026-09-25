# /ar:status — 实验仪表盘

显示所有实验的结果、活跃循环和进度。

## 使用方法

```
/ar:status                                  # 完整仪表盘
/ar:status engineering/api-speed            # 单个实验详情
/ar:status --domain engineering             # 某个域内的所有实验
/ar:status --format markdown                # 导出为 Markdown
/ar:status --format csv --output results.csv  # 导出为 CSV
```

## 功能说明

### 单个实验

```bash
python {skill_path}/scripts/log_results.py --experiment {domain}/{name}
```

同时检查活跃循环：
```bash
cat .autoresearch/{domain}/{name}/loop.json 2>/dev/null
```

如果存在 loop.json，则显示：
```
Active loop: every {interval} (cron ID: {id}, started: {date})
```

### 域视图

```bash
python {skill_path}/scripts/log_results.py --domain {domain}
```

### 完整仪表盘

```bash
python {skill_path}/scripts/log_results.py --dashboard
```

对每个实验，同时检查 loop.json 并显示循环状态。

### 导出

```bash
# CSV
python {skill_path}/scripts/log_results.py --dashboard --format csv --output {file}

# Markdown
python {skill_path}/scripts/log_results.py --dashboard --format markdown --output {file}
```

## 输出示例

```
DOMAIN          EXPERIMENT          RUNS  KEPT  BEST         CHANGE    STATUS   LOOP
engineering     api-speed            47    14   185ms        -76.9%    active   every 1h
engineering     bundle-size          23     8   412KB        -58.3%    paused   —
marketing       medium-ctr           31    11   8.4/10       +68.0%    active   daily
prompts         support-tone         15     6   82/100       +46.4%    done     —
```
