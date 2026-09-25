# indexion 分段

使用基于发散、TF-IDF 或标点符号策略将文本分割为上下文相关的段落。

## 使用场景

- 用户需要为 RAG 或嵌入流程对文本进行分段
- 用户希望将文档分割为有意义的部分
- 用户要求对文本进行分段处理
- 准备在子文档级别进行相似性分析的文本

## 使用方法

```bash
# 默认窗口发散策略
indexion segment <输入文件> <输出目录>

# 基于TF-IDF的分段
indexion segment --strategy=tfidf <输入文件> <输出目录>

# 基于标点符号的分段
indexion segment --strategy=punctuation <输入文件> <输出目录>

# 自定义分段大小
indexion segment --min-size=200 --max-size=3000 --target-size=800 document.txt output/

# 自定义发散阈值
indexion segment --threshold=0.5 document.txt output/

# 自适应阈值模式（默认）
indexion segment --adaptive document.txt output/

# 混合NCD+TF-IDF模式
indexion segment --hybrid --ncd-weight=0.6 --tfidf-weight=0.4 document.txt output/

# 自定义窗口大小
indexion segment --window-size=5 document.txt output/

# 自定义输出前缀
indexion segment --prefix=chunk document.txt output/
```

## 选项

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--strategy=NAME` | window | 策略：window、tfidf、punctuation |
| `--min-size=INT` | 100 | 最小分段字符数 |
| `--max-size=INT` | 2000 | 最大分段字符数 |
| `--target-size=INT` | 500 | 目标分段字符数 |
| `--threshold=FLOAT` | 0.42 | 发散阈值 |
| `--window-size=INT` | 3 | 窗口大小 |
| `--adaptive` | true | 自适应阈值模式 |
| `--hybrid` | false | NCD+TF-IDF混合模式 |
| `--ncd-weight=FLOAT` | 0.5 | 混合模式中的NCD权重 |
| `--tfidf-weight=FLOAT` | 0.5 | 混合模式中的TF-IDF权重 |
| `--prefix=NAME` | segment | 输出文件前缀 |

## 策略

| 策略 | 描述 |
|------|------|
| `window` (默认) | 滑动窗口发散检测 |
| `tfidf` | 基于TF-IDF的主题变化检测 |
| `punctuation` | 基于标点符号/句子边界 |

## 工作流程

1. 运行 `indexion segment <输入文件> <输出目录>` 使用默认值进行文本分段
2. 调整 `--threshold` 和 `--target-size` 来调整分段粒度
3. 使用 `--hybrid` 模式在混合内容文档上获得更好的准确性
