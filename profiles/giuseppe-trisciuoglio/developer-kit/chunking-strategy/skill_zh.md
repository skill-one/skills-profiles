# RAG系统的分块策略

## 概述

为RAG系统、向量数据库和文档处理提供分块策略。推荐分块大小、重叠百分比和边界检测方法；验证语义连贯性；评估检索指标。

## 使用场景

在构建或优化RAG系统、向量搜索流程、文档分块工作流或性能调优检索质量差的现有系统时使用。

## 使用说明

### 选择分块策略

根据文档类型和使用场景选择：

1. **固定大小分块**（级别1）
   - 用于结构不明确的简单文档
   - 初始设置为512个token和10-20%重叠
   - 调整：256个token用于事实性查询，1024个token用于分析性内容

2. **递归字符分块**（级别2）
   - 用于具有结构边界的文档
   - 分层分隔符：段落→句子→单词
   - 根据文档类型定制（HTML、Markdown、JSON）

3. **结构感知分块**（级别3）
   - 用于结构化内容（Markdown、代码、表格、PDF）
   - 保留语义单元：函数、章节、表格块
   - 分割后验证结构保留情况

4. **语义分块**（级别4）
   - 用于具有主题转换的复杂文档
   - 基于嵌入的边界检测，相似度阈值0.8
   - 缓冲区大小：3-5个句子

5. **高级方法**（级别5）
   - 长上下文模型的延迟分块
   - 高精度要求的上下文检索
   - 监控计算成本与检索收益

参考：[references/strategies.md](references/strategies.md)。

### 实现分块流程

1. **预处理文档**
   - 分析结构、内容类型、信息密度
   - 识别多模态内容（表格、图像、代码）

2. **选择参数**
   - 分块大小：嵌入模型上下文窗口/4
   - 重叠：大多数情况10-20%
   - 策略特定设置

3. **处理和验证**
   - 应用分块策略
   - 验证连贯性：运行`evaluate_chunks.py --coherence`（见下文）
   - 使用代表性文档测试

4. **评估和迭代**
   - 测量精确率和召回率
   - 若精确率<0.7：将分块大小减少25%并重新评估
   - 若召回率<0.6：将重叠增加10%并重新评估
   - 监控延迟和内存使用

参考：[references/implementation.md](references/implementation.md)。

### 验证分块质量

运行验证命令评估分块质量：

```bash
# 检查语义连贯性（需要sentence-transformers）
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
chunks = [...]  # 你的分块
embeddings = model.encode(chunks)
similarity = (embeddings @ embeddings.T).mean()
print(f'Cohesion: {similarity:.3f}')  # 目标：0.3-0.7
"

# 测量检索精确率
python -c "
relevant = sum(1 for c in retrieved if c in relevant_chunks)
precision = relevant / len(retrieved)
print(f'Precision: {precision:.2f}')  # 目标：>= 0.7
"

# 检查分块大小分布
python -c "
import numpy as np
sizes = [len(c.split()) for c in chunks]
print(f'Mean: {np.mean(sizes):.0f}, Std: {np.std(sizes):.0f}')
print(f'Min: {min(sizes)}, Max: {max(sizes)}')
"
```

参考：[references/evaluation.md](references/evaluation.md)。

## 示例

### 固定大小分块

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=256,
    chunk_overlap=25,
    length_function=len
)
chunks = splitter.split_documents(documents)
```

### 结构感知代码分块

```python
import ast

def chunk_python_code(code):
    tree = ast.parse(code)
    chunks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            chunks.append(ast.get_source_segment(code, node))
    return chunks
```

### 语义分块

```python
def semantic_chunk(text, similarity_threshold=0.8):
    sentences = split_into_sentences(text)
    embeddings = generate_embeddings(sentences)
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        sim = cosine_similarity(embeddings[i-1], embeddings[i])
        if sim < similarity_threshold:
            chunks.append(" ".join(current))
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    chunks.append(" ".join(current))
    return chunks
```

## 最佳实践

### 核心原则
- 平衡上下文保留与检索精确度
- 保持分块内的语义连贯性
- 优化嵌入模型上下文窗口限制

### 实施建议
- 从固定大小（512个token，15%重叠）开始
- 根据文档特征迭代
- 部署前使用领域特定文档测试

### 需避免的陷阱
- 过度分块：上下文贫乏的小分块
- 不足分块：过大的分块导致信息缺失
- 忽略语义边界和文档结构
- 对多样化内容类型使用一刀切方法

## 限制和警告

### 资源考虑
- 语义方法需要大量计算资源
- 延迟分块需要长上下文嵌入模型
- 复杂策略增加处理延迟
- 监控大文档批次的内存使用

### 质量要求
- 处理后验证语义连贯性
- 部署前使用代表性文档测试
- 确保分块保持独立意义
- 对格式错误的文档实现错误处理

## 参考文献

- [strategies.md](references/strategies.md) - 详细策略
- [implementation.md](references/implementation.md) - 实施指南
- [evaluation.md](references/evaluation.md) - 性能指标
- [tools.md](references/tools.md) - 库和框架
- [research.md](references/research.md) - 研究论文
- [advanced-strategies.md](references/advanced-strategies.md) - 11种高级方法
- [semantic-methods.md](references/semantic-methods.md) - 语义方法
- [visualization-tools.md](references/visualization-tools.md) - 可视化工具
