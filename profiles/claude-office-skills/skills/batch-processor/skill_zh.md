# 批量处理器技能

## 概述

此技能能够高效地批量处理文档——通过并行执行和进度跟踪，将、转换、提取或分析数百个文件。

## 如何使用

1. 描述您想要完成的工作
2. 提供任何必需的输入数据或文件
3. 我将执行相应的操作

**示例提示：**
- "将100个PDF文件转换为Word文档"
- "从文件夹中的所有图像中提取文本"
- "批量重命名和组织文件"
- "批量更新文档页眉/页脚"

## 领域知识


### 批量处理模式

```
输入: [file1, file2, ..., fileN]
         │
         ▼
    ┌─────────────┐
    │  并行      │  ← 同时处理多个文件
    │  工作线程   │
    └─────────────┘
         │
         ▼
输出: [result1, result2, ..., resultN]
```

### Python实现

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

def process_file(file_path: Path) -> dict:
    """处理单个文件。"""
    # 在此处添加您的处理逻辑
    return {"path": str(file_path), "status": "success"}

def batch_process(input_dir: str, pattern: str = "*.*", max_workers: int = 4):
    """处理目录中所有匹配的文件。"""
    
    files = list(Path(input_dir).glob(pattern))
    results = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, f): f for f in files}
        
        for future in tqdm(as_completed(futures), total=len(files)):
            file = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({"path": str(file), "error": str(e)})
    
    return results

# 使用示例
results = batch_process("/documents/invoices", "*.pdf", max_workers=8)
print(f"处理了{len(results)}个文件")
```

### 错误处理与恢复

```python
import json
from pathlib import Path

class BatchProcessor:
    def __init__(self, checkpoint_file: str = "checkpoint.json"):
        self.checkpoint_file = checkpoint_file
        self.processed = self._load_checkpoint()
    
    def _load_checkpoint(self):
        if Path(self.checkpoint_file).exists():
            return json.load(open(self.checkpoint_file))
        return {}
    
    def _save_checkpoint(self):
        json.dump(self.processed, open(self.checkpoint_file, "w"))
    
    def process(self, files: list, processor_func):
        for file in files:
            if str(file) in self.processed:
                continue  # 跳过已处理的
            
            try:
                result = processor_func(file)
                self.processed[str(file)] = {"status": "success", **result}
            except Exception as e:
                self.processed[str(file)] = {"status": "error", "error": str(e)}
            
            self._save_checkpoint()  # 安全恢复
```

## 最佳实践

1. **使用进度条（tqdm）提供用户反馈**
2. **为长任务实现检查点**
3. **设置合理的线程数（CPU核心）**
4. **记录失败信息以便后续审查**

## 安装

```bash
# 安装所需依赖
pip install python-docx openpyxl python-pptx reportlab jinja2
```

## 资源

- [自定义仓库](https://github.com/claude-office-skills/skills)
- [Claude Office Skills Hub](https://github.com/claude-office-skills/skills)
