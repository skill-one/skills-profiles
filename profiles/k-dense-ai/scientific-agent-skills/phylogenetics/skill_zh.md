# 系统发育学

## 概述

系统发育学分析通过推断进化谱系分支模式来重建生物序列（基因、蛋白质、基因组）的进化历史。这项技能涵盖了标准流程：

1. **MAFFT** — 多序列比对
2. **IQ-TREE 2** — 基于模型选择的最高似然树推断
3. **FastTree** — 快速近似最高似然（适用于大型数据集）
4. **ETE3** — 用于树操作和可视化的 Python 库

**安装：**
```bash
# Conda（推荐用于命令行工具）
conda install -c bioconda mafft iqtree fasttree
uv pip install ete3

# ete3 的 TreeStyle/NodeStyle 渲染依赖于其 Qt 后端，因此图像输出
# 需要 PyQt5；树解析和统计无需 PyQt5。
uv pip install PyQt5
```

## 何时使用此技能

当您需要：

- **进化关系**：哪个生物/基因与我的序列最接近？
- **病毒系统发育学**：追踪疫情传播并估计传播日期
- **蛋白质家族分析**：推断基因家族内的进化关系
- **水平基因转移检测**：识别具有不一致物种/基因树的基因
- **祖先序列重建**：推断祖先蛋白质序列
- **分子钟分析**：使用时间采样估计分化日期
- **GWAS 伴侣**：将变异置于进化背景中（例如，SARS-CoV-2 变异）
- **微生物学**：基于 16S rRNA 或核心基因组系统发育

## 标准工作流程

### 1. 使用 MAFFT 进行多序列比对

```python
import subprocess
import os

def run_mafft(input_fasta: str, output_fasta: str, method: str = "auto",
               n_threads: int = 4) -> str:
    """
    使用 MAFFT 对序列进行比对。

    Args:
        input_fasta: 未比对 FASTA 文件的路径
        output_fasta: 对齐后输出的路径
        method: 'auto'（自动选择），'einsi'（准确），'linsi'（准确，慢），
                'fftnsi'（中等），'fftns'（快速），'retree2'（快速）
        n_threads: CPU 线程数

    Returns:
        对齐后 FASTA 文件的路径
    """
    methods = {
        "auto": ["mafft", "--auto"],
        "einsi": ["mafft", "--genafpair", "--maxiterate", "1000"],
        "linsi": ["mafft", "--localpair", "--maxiterate", "1000"],
        "fftnsi": ["mafft", "--fftnsi"],
        "fftns": ["mafft", "--fftns"],
        "retree2": ["mafft", "--retree", "2"],
    }

    cmd = methods.get(method, methods["auto"])
    cmd += ["--thread", str(n_threads), "--inputorder", input_fasta]

    with open(output_fasta, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"MAFFT 失败:\n{result.stderr}")

    # 计算对齐序列数量
    with open(output_fasta) as f:
        n_seqs = sum(1 for line in f if line.startswith('>'))
    print(f"MAFFT: 对齐了 {n_seqs} 个序列 → {output_fasta}")

    return output_fasta

# MAFFT 方法选择指南：
# 少序列（<200），准确：linsi 或 einsi
# 多序列（<1000），中等：fftnsi
# 大型数据集（>1000）：fftns 或 auto
# 超快速（>10000）：mafft --retree 1
```

### 2. 修剪比对（可选但推荐）

```python
def trim_alignment_trimal(aligned_fasta: str, output_fasta: str,
                            method: str = "automated1") -> str:
    """
    使用 TrimAl 修剪对齐不良的列。

    方法：
    - 'automated1'：自动启发式（推荐）
    - 'gappyout'：移除含间隙的列
    - 'strict'：严格间隙阈值
    """
    cmd = ["trimal", f"-{method}", "-in", aligned_fasta, "-out", output_fasta, "-fasta"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"TrimAl 警告: {result.stderr}")
        # 回退使用未修剪的对齐
        import shutil
        shutil.copy(aligned_fasta, output_fasta)
    return output_fasta
```

### 3. IQ-TREE 2 — 最高似然树

```python
def run_iqtree(aligned_fasta: str, output_prefix: str,
                model: str = "TEST", bootstrap: int = 1000,
                n_threads: int = 4, extra_args: list = None) -> dict:
    """
    使用 IQ-TREE 2 构建最高似然树。

    Args:
        aligned_fasta: 对齐的 FASTA 文件
        output_prefix: 输出文件的名称前缀
        model: 'TEST' 用于自动模型选择，或指定（例如，'GTR+G' 用于 DNA，
               'LG+G4' 用于蛋白质，'JTT+G' 用于蛋白质）
        bootstrap: 超快速自举复制的数量（推荐 1000）
        n_threads: 线程数（'AUTO' 为自动检测）
        extra_args: 额外的 IQ-TREE 参数

    Returns:
        包含输出文件路径的字典
    """
    cmd = [
        "iqtree2",
        "-s", aligned_fasta,
        "--prefix", output_prefix,
        "-m", model,
        "-B", str(bootstrap),   # 超快速自举
        "-T", str(n_threads),
        "--redo"                # 覆盖现有结果
    ]

    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"IQ-TREE 失败:\n{result.stderr}")

    # 打印模型选择结果
    log_file = f"{output_prefix}.log"
    if os.path.exists(log_file):
        with open(log_file) as f:
            for line in f:
                if "Best-fit model" in line:
                    print(f"IQ-TREE: {line.strip()}")

    output_files = {
        "tree": f"{output_prefix}.treefile",
        "log": f"{output_prefix}.log",
        "iqtree": f"{output_prefix}.iqtree",  # 完整报告
        "model": f"{output_prefix}.model.gz",
    }

    print(f"IQ-TREE: 树保存到 {output_files['tree']}")
    return output_files

# IQ-TREE 模型选择指南：
# DNA:     TEST → GTR+G, HKY+G, TrN+G
# 蛋白质: TEST → LG+G4, WAG+G, JTT+G, Q.pfam+G
# 密码子: TEST → MG+F3X4

# 对于时间（分子钟）分析，添加：
# extra_args = ["--date", "dates.txt", "--clock-test", "--date-CI", "95"]
```

### 4. FastTree — 快速近似似然

对于大型数据集（>1000 个序列）且 IQ-TREE 过慢的情况：

```python
def run_fasttree(aligned_fasta: str, output_tree: str,
                  sequence_type: str = "nt", model: str = "gtr",
                  n_threads: int = 4) -> str:
    """
    使用 FastTree 构建快速近似似然树。

    Args:
        sequence_type: 'nt' 为核酸或 'aa' 为氨基酸
        model: 对于 nt: 'gtr'（推荐）或 'jc'; 对于 aa: 'lg', 'wag', 'jtt'
    """
    if sequence_type == "nt":
        cmd = ["FastTree", "-nt", "-gtr"]
    else:
        cmd = ["FastTree", f"-{model}"]

    cmd += [aligned_fasta]

    with open(output_tree, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FastTree 失败:\n{result.stderr}")

    print(f"FastTree: 树保存到 {output_tree}")
    return output_tree
```

### 5. 使用 ETE3 进行树分析和可视化

```python
from ete3 import Tree, TreeStyle, NodeStyle, TextFace, PhyloTree
import matplotlib.pyplot as plt

def load_tree(tree_file: str) -> Tree:
    """加载 Newick 树文件."""
    t = Tree(tree_file)
    print(f"树: {len(t)} 叶片, {len(list(t.traverse()))} 节点")
    return t

def basic_tree_stats(t: Tree) -> dict:
    """计算基本树统计信息."""
    leaves = t.get_leaves()
    distances = [t.get_distance(l1, l2) for l1 in leaves[:min(50, len(leaves))]
                 for l2 in leaves[:min(50, len(leaves))] if l1 != l2]

    stats = {
        "n_leaves": len(leaves),
        "n_internal_nodes": len(t) - len(leaves),
        "total_branch_length": sum(n.dist for n in t.traverse()),
        "max_leaf_distance": max(distances) if distances else 0,
        "mean_leaf_distance": sum(distances)/len(distances) if distances else 0,
    }
    return stats

def find_mrca(t: Tree, leaf_names: list) -> Tree:
    """查找一组叶子的最近共同祖先."""
    return t.get_common_ancestor(*leaf_names)

def visualize_tree(t: Tree, output_file: str = "tree.png",
                    show_branch_support: bool = True,
                    color_groups: dict = None,
                    width: int = 800) -> None:
    """
    将系统发育树渲染为图像。

    Args:
        t: ETE3 树对象
        color_groups: 映射叶片名称 → 颜色（用于着色分类单元）
        show_branch_support: 显示自举值
    """
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_branch_support = show_branch_support
    ts.mode = "r"  # 'r' = 矩形, 'c' = 圆形

    if color_groups:
        for node in t.traverse():
            if node.is_leaf() and node.name in color_groups:
                nstyle = NodeStyle()
                nstyle["fgcolor"] = color_groups[node.name]
                nstyle["size"] = 8
                node.set_style(nstyle)

    t.render(output_file, tree_style=ts, w=width, units="px")
    print(f"树保存到: {output_file}")

def midpoint_root(t: Tree) -> Tree:
    """在中间处根树（当未知外群时）。"""
    t.set_outgroup(t.get_midpoint_outgroup())
    return t

def prune_tree(t: Tree, keep_leaves: list) -> Tree:
    """修剪树以仅保留指定的叶片."""
    t.prune(keep_leaves, preserve_branch_length=True)
    return t
```

### 6. 完整分析脚本

```python
import subprocess, os
from ete3 import Tree

def full_phylogenetic_analysis(
    input_fasta: str,
    output_dir: str = "phylo_results",
    sequence_type: str = "nt",
    n_threads: int = 4,
    bootstrap: int = 1000,
    use_fasttree: bool = False
) -> dict:
    """
    完整系统发育流程：比对 → 修剪 → 构建树 → 可视化。

    Args:
        input_fasta: 未比对 FASTA
        sequence_type: 'nt'（核酸）或 'aa'（氨基酸/蛋白质）
        use_fasttree: 使用 FastTree 而不是 IQ-TREE（适用于大型数据集）
    """
    os.makedirs(output_dir, exist_ok=True)
    prefix = os.path.join(output_dir, "phylo")

    print("=" * 50)
    print("步骤 1：多序列比对 (MAFFT)")
    aligned = run_mafft(input_fasta, f"{prefix}_aligned.fasta",
                         method="auto", n_threads=n_threads)

    print("\n步骤 2：树推断")
    if use_fasttree:
        tree_file = run_fasttree(
            aligned, f"{prefix}.tree",
            sequence_type=sequence_type,
            model="gtr" if sequence_type == "nt" else "lg"
        )
    else:
        model = "TEST" if sequence_type == "nt" else "TEST"
        iqtree_files = run_iqtree(
            aligned, prefix,
            model=model,
            bootstrap=bootstrap,
            n_threads=n_threads
        )
        tree_file = iqtree_files["tree"]

    print("\n步骤 3：树分析")
    t = Tree(tree_file)
    t = midpoint_root(t)

    stats = basic_tree_stats(t)
    print(f"树统计信息: {stats}")

    print("\n步骤 4：可视化")
    visualize_tree(t, f"{prefix}_tree.png", show_branch_support=True)

    # 保存根树
    rooted_tree_file = f"{prefix}_rooted.nwk"
    t.write(format=1, outfile=rooted_tree_file)

    results = {
        "aligned_fasta": aligned,
        "tree_file": tree_file,
        "rooted_tree": rooted_tree_file,
        "visualization": f"{prefix}_tree.png",
        "stats": stats
    }

    print("\n" + "=" * 50)
    print("系统发育分析完成！")
    print(f"结果在: {output_dir}/")
    return results
```

## IQ-TREE 模型指南

### DNA 模型

| 模型 | 描述 | 用例 |
|------|------|------|
| `GTR+G4` | 通用时间反转 + Gamma | 最灵活的 DNA 模型 |
| `HKY+G4` | Hasegawa-Kishino-Yano + Gamma | 双速率模型（常见） |
| `TrN+G4` | Tamura-Nei | 不等价转换 |
| `JC` | Jukes-Cantor | 最简单；所有速率相等 |

### 蛋白质模型

| 模型 | 描述 | 用例 |
|------|------|------|
| `LG+G4` | Le-Gascuel + Gamma | 最佳平均蛋白质模型 |
| `WAG+G4` | Whelan-Goldman | 广泛使用 |
| `JTT+G4` | Jones-Taylor-Thornton | 经典模型 |
| `Q.pfam+G4` | pfam 训练 | 用于 Pfam 类似蛋白质家族 |
| `Q.bird+G4` | Bird 特定 | 脊椎动物蛋白质 |

**提示：** 使用 `-m TEST` 让 IQ-TREE 自动选择最佳模型。

## 最佳实践

- **比对质量优先**：不良比对 → 不可靠的树；手动检查比对
- **使用 `linsi` 对小（<200 序列），`fftns` 或 `auto` 对大型比对**
- **模型选择**：始终使用 `-m TEST` 除非有特定原因
- **自举**：使用 ≥1000 超快速自举（`-B 1000`）用于分支支持
- **根树**：未根树可能误导；使用外群或中间根
- **FastTree 对 >5000 序列**：IQ-TREE 变慢；FastTree 快 10–100 倍
- **修剪长比对**：TrimAl 移除不可靠的列；提高树准确性
- **检查重组** 在病毒/细菌序列中构建树前（`RDP4`, `GARD`）

## 额外资源

- **MAFFT**：https://mafft.cbrc.jp/alignment/software/
- **IQ-TREE 2**：http://www.iqtree.org/ | 教程：https://www.iqtree.org/workshop/molevol2022
- **FastTree**：http://www.microbesonline.org/fasttree/
- **ETE3**：http://etetoolkit.org/
- **FigTree**（GUI 可视化）：https://tree.bio.ed.ac.uk/software/figtree/
- **iTOL**（网络可视化）：https://itol.embl.de/
- **MUSCLE**（替代比对器）：https://www.drive5.com/muscle/
- **TrimAl**（比对修剪）：https://vicfero.github.io/trimal/
