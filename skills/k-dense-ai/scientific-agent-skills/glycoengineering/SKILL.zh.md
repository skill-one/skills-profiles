---
name: glycoengineering
description: 分析和设计蛋白质糖基化。扫描序列以寻找N-糖基化序列子（N-X-S/T），预测O-糖基化热点，并获取精选的糖基工程工具（NetOGlyc、GlycoShield、GlycoWorkbench）。用于糖蛋白工程、治疗性抗体优化和疫苗设计。
---

# 糖基工程

## 概述

糖基化是蛋白质最常见且最复杂的翻译后修饰（PTM），影响超过50%的人类蛋白质。糖链调节蛋白质折叠、稳定性、免疫识别、受体相互作用以及治疗性蛋白质的药代动力学。糖基工程涉及对糖基化模式的合理修饰，以改善治疗效果、稳定性或免疫逃逸。

**两种主要的糖基化类型：**
- **N-糖基化**：连接到天冬酰胺（N）上，在序列子 N-X-[S/T] 中，其中 X ≠ 脯氨酸；发生在内质网/高尔基体
- **O-糖基化**：连接到丝氨酸（S）或苏氨酸（T）；没有严格的共识基序；主要 GalNAc 初始

## 何时使用此技能

使用此技能时：

- **抗体工程**：优化 Fc 糖基化以增强 ADCC、CDC 或降低免疫原性
- **治疗性蛋白质设计**：识别影响半衰期、稳定性或免疫原性的糖基化位点
- **疫苗抗原设计**：设计糖链屏蔽以集中免疫反应在保守表位上
- **生物类似物表征**：比较参考品和生物类似物之间的糖链模式
- **药物靶点分析**：糖基化是否影响受体的靶点结合？
- **蛋白质稳定性**：N-糖基通常稳定蛋白质；识别用于稳定突变的位点

## N-糖基化序列子分析

### 扫描 N-糖基化位点

N-糖基化发生在序列子 **N-X-[S/T]** 中，其中 X ≠ 脯氨酸。

```python
import re
from typing import List, Tuple

def find_n_glycosylation_sequons(sequence: str) -> List[dict]:
    """
    扫描蛋白质序列以寻找经典的 N-连接糖基化序列子。
    基序：N-X-[S/T]，其中 X ≠ 脯氨酸。

    Args:
        sequence: 单字母氨基酸序列

    Returns:
        包含位置（1-based）、基序和上下文的字典列表
    """
    seq = sequence.upper()
    results = []
    i = 0
    while i <= len(seq) - 3:
        triplet = seq[i:i+3]
        if triplet[0] == 'N' and triplet[1] != 'P' and triplet[2] in {'S', 'T'}:
            context = seq[max(0, i-3):i+6]  # ±3 个残基的上下文
            results.append({
                'position': i + 1,   # 1-based
                'motif': triplet,
                'context': context,
                'sequon_type': 'NXS' if triplet[2] == 'S' else 'NXT'
            })
            i += 3
        else:
            i += 1
    return results

def summarize_glycosylation_sites(sequence: str, protein_name: str = "") -> str:
    """生成 N-糖基化位点的科研日志摘要。"""
    sequons = find_n_glycosylation_sequons(sequence)

    lines = [f"# N-糖基化序列子分析：{protein_name or '蛋白质'}"]
    lines.append(f"序列长度：{len(sequence)}")
    lines.append(f"总 N-糖基化序列子数量：{len(sequons)}")

    if sequons:
        lines.append(f"\nN-X-S 位点：{sum(1 for s in sequons if s['sequon_type'] == 'NXS')}")
        lines.append(f"N-X-T 位点：{sum(1 for s in sequons if s['sequon_type'] == 'NXT')}")
        lines.append(f"\n位点详情：")
        for s in sequons:
            lines.append(f"  位置 {s['position']}：{s['motif']}（上下文：...{s['context']}...）")
    else:
        lines.append("未检测到经典的 N-糖基化序列子。")

    return "\n".join(lines)

# 示例：IgG1 Fc 区域
fc_sequence = "APELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"
print(summarize_glycosylation_sites(fc_sequence, "IgG1 Fc"))
```

### 突变 N-糖基化位点

```python
def eliminate_glycosite(sequence: str, position: int, replacement: str = "Q") -> str:
    """
    通过将天冬酰胺（Asn）→ 谷氨酰胺（Gln）进行保守替换来消除 N-糖基化位点。

    Args:
        sequence: 蛋白质序列
        position: 要突变的 Asn 的 1-based 位置
        replacement: 替换的氨基酸（默认 Q = 谷氨酰胺；大小相似，未糖基化）

    Returns:
        突变的序列
    """
    seq = list(sequence.upper())
    idx = position - 1
    assert seq[idx] == 'N', f"位置 {position} 是 '{seq[idx]}'，不是 'N'"
    seq[idx] = replacement.upper()
    return ''.join(seq)

def add_glycosite(sequence: str, position: int, flanking_context: str = "S") -> str:
    """
    通过将残基突变成天冬酰胺（Asn）来引入 N-糖基化位点，
    并确保 X ≠ 脯氨酸且 +2 = S/T。

    Args:
        position: 引入 Asn 的 1-based 位置
        flanking_context: 'S' 或 'T' 在位置+2（如果需要修改）
    """
    seq = list(sequence.upper())
    idx = position - 1

    # 突变成 Asn
    seq[idx] = 'N'

    # 确保 X+1 ≠ 脯氨酸（如果需要，将脯氨酸突变成丙氨酸）
    if idx + 1 < len(seq) and seq[idx + 1] == 'P':
        seq[idx + 1] = 'A'

    # 确保 X+2 = S 或 T
    if idx + 2 < len(seq) and seq[idx + 2] not in ('S', 'T'):
        seq[idx + 2] = flanking_context

    return ''.join(seq)
```

## O-糖基化分析

### 启发式 O-糖基化热点预测

```python
def predict_o_glycosylation_hotspots(
    sequence: str,
    window: int = 7,
    min_st_fraction: float = 0.4,
    disallow_proline_next: bool = True
) -> List[dict]:
    """
    基于局部 S/T 密度的启发式 O-糖基化热点评分。
    不能替代 NetOGlyc；用作快速基线。

    规则：
    - O-GalNAc 糖基化在富含 Ser/Thr 的片段上聚集
    - 标记富含 S/T 的窗口中的 Ser/Thr 残基
    - 避免 S/T 紧随脯氨酸之后（TP/SP 基序抑制 GalNAc-T）

    Args:
        window: 奇数窗口大小，用于局部 S/T 密度
        min_st_fraction: 窗口中 S/T 的最小分数以标记位点
    """
    if window % 2 == 0:
        window = 7
    seq = sequence.upper()
    half = window // 2
    candidates = []

    for i, aa in enumerate(seq):
        if aa not in ('S', 'T'):
            continue
        if disallow_proline_next and i + 1 < len(seq) and seq[i+1] == 'P':
            continue

        start = max(0, i - half)
        end = min(len(seq), i + half + 1)
        segment = seq[start:end]
        st_count = sum(1 for c in segment if c in ('S', 'T'))
        frac = st_count / len(segment)

        if frac >= min_st_fraction:
            candidates.append({
                'position': i + 1,
                'residue': aa,
                'st_fraction': round(frac, 3),
                'window': f"{start+1}-{end}",
                'segment': segment
            })

    return candidates
```

## 外部糖基工程工具

### 1. NetOGlyc 4.0 (O-糖基化预测)

高精度 O-GalNAc 位点预测的网页服务：
- **URL**: https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/
- **输入**: FASTA 蛋白质序列
- **输出**: 每个残基的 O-糖基化概率分数
- **方法**: 在实验验证的 O-GalNAc 位点上训练的神经网络

```python
import requests

def submit_netoglycv4(fasta_sequence: str) -> str:
    """
    将序列提交给 NetOGlyc 4.0 网页服务。
    返回用于结果检索的工作 URL。

    注意：此服务使用 DTU Health Tech 网页服务。结果需要 ~1-5 分钟。
    """
    url = "https://services.healthtech.dtu.dk/cgi-bin/webface2.cgi"
    # NetOGlyc 提交（参数可能因网页服务版本而异）
    # 建议大多数情况下直接使用网页界面
    print("在 https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/ 提交序列")
    return url

# 另外：NetNGlyc 用于 N-糖基化预测
# URL: https://services.healthtech.dtu.dk/services/NetNGlyc-1.0/
```

### 2. GlycoSHIELD (糖链屏蔽分析)

GlycoSHIELD 将预先模拟的糖链构象库嫁接到静态蛋白质结构上，并评分蛋白质表面有多少被糖链屏蔽，而无需运行新的 MD
(Tsai 等人，《Cell》2024，doi:10.1016/j.cell.2024.01.034):
- **URL**: https://gitlab.mpcdf.mpg.de/dioscuri-biophysics/glycoshield-md/（网页应用：https://glycoshield.eu）
- **用途**：在糖蛋白上模拟糖链屏蔽，并映射每个残基的屏蔽情况
- **输出**：每个位点的糖基化 PDB/XTC 集合，每个残基的屏蔽图，B 因子列中包含屏蔽信息的 PDB

GlycoSHIELD **不在 PyPI 上**——`uv pip install glycoshield` 失败。它作为三个脚本打包，基于一个小的 `glycoshield` 包（需要 numpy、scipy、matplotlib、MDAnalysis；`GlycoSASA.py` 还需要 `gmx` 从 GROMACS 在 `PATH` 上）。从检出中安装：

```bash
# 安装（GPL-3.0）。糖链构象库需要单独下载——
# 参见 glycan_library_downloader.py 和 GLYCAN_LIBRARY/ 在存储库中。
git clone https://gitlab.mpcdf.mpg.de/dioscuri-biophysics/glycoshield-md.git
cd glycoshield-md
uv pip install -e .

# 1. 将糖链构象嫁接到输入文件中列出的每个序列子上。
#    每行一个位点：<chain> <res-1,res,res+1> <1,2,3> <glycan.pdb> <glycan.xtc> <out.pdb> <out.xtc>
python GlycoSHIELD.py --protpdb protein.pdb --inputfile sequons_input \
    --threshold 3.5 --mode CG --shuffle-sugar

# 2. 跨嫁接集合的每个残基屏蔽分数（探针半径以 nm 为单位）
python GlycoSASA.py --pdblist A_463.pdb,A_492.pdb --xtclist A_463.xtc,A_492.xtc \
    --probelist 0.14,0.25 --plottrace
```

说明：标志来自脚本 argparse 定义和上游教程
(N-cadherin EC5 与 Man5 糖链)；这里没有运行。`--mode CG` 仅检查与 Cα 原子冲突，并配对 `--threshold 3.5`；`--mode All` 与 `--threshold 0.7` 是全原子设置。

### 3. GlycoWorkbench (糖链结构绘制/分析)

- **URL**: https://www.eurocarbdb.org/project/glycoworkbench
- **用途**：绘制糖链结构，计算质量，注释质谱图
- **格式**：GlycoCT、IUPAC 缩写糖链表示法

### 4. GlyConnect (糖链-蛋白质数据库)

- **URL**: https://glyconnect.expasy.org/
- **用途**：查找实验验证的糖蛋白和糖基化位点
- **查询**：通过蛋白质（UniProt ID）、糖链结构或组织

```python
import requests

def query_glyconnect(uniprot_id: str) -> dict:
    """查询 GlyConnect 以获取蛋白质的糖基化数据。"""
    url = f"https://glyconnect.expasy.org/api/proteins/uniprot/{uniprot_id}"
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code == 200:
        return response.json()
    return {}

# 示例：查询 EGFR 糖基化
egfr_glyco = query_glyconnect("P00533")
```

### 5. UniCarbKB (糖链结构数据库)

- **URL**: https://unicarbkb.org/
- **用途**：浏览糖链结构，按质量或组成搜索
- **格式**：GlycoCT 或 IUPAC 表示法

## 关键糖基工程策略

### 用于治疗性抗体

| 目标 | 策略 | 备注 |
|------|------|------|
| 增强 ADCC | Fc Asn297 去岩藻糖化 | 去岩藻糖化 IgG1 的 FcγRIIIa 结合能力提高约 50 倍 |
| 降低免疫原性 | 移除非人糖链 | 消除 α-Gal、NGNA 表位 |
| 改善 PK 半衰期 | 脱唾液酸化 | 脱唾液酸化糖链延长半衰期 |
| 减少炎症 | 超脱唾液酸化 | IVIG 抗炎机制 |
| 创建糖链屏蔽 | 在表面添加 N-糖基位点 | 遮蔽易感表位（疫苗设计） |

### 常用突变

| 突变 | 效果 |
|------|------|
| N297A/Q (IgG1) | 移除 Fc 糖基化（去糖基化） |
| N297D (IgG1) | 移除 Fc 糖基化 |
| S298A/E333A/K334A | 增加 FcγRIIIa 结合 |
| F243L (IgG1) | 增加 去岩藻糖化 |
| T299A | 移除 Fc 糖基化 |

## 糖链表示法

### IUPAC 缩写表示法（单糖缩写）

| 符号 | 全称 | 类型 |
|------|------|------|
| Glc | Glucose | 六碳糖 |
| GlcNAc | N-Acetylglucosamine | 六碳 N-乙酰氨基葡萄糖 |
| Man | Mannose | 六碳糖 |
| Gal | Galactose | 六碳糖 |
| Fuc | Fucose | 去氧六碳糖 |
| Neu5Ac | N-Acetylneuraminic acid (Sialic acid) | 唾液酸 |
| GalNAc | N-Acetylgalactosamine | 六碳 N-乙酰氨基半乳糖 |

### 复杂 N-糖基化结构

```
典型的双天线 N-糖基化：
Neu5Ac-Gal-GlcNAc-Man\
                       Man-GlcNAc-GlcNAc-[Asn]
Neu5Ac-Gal-GlcNAc-Man/
(±核心 Fuc 在最内层 GlcNAc)
```

## 最佳实践

- **在实验验证之前，先使用 NetNGlyc/NetOGlyc 进行计算预测**
- **使用质谱法验证**：糖组学（Byonic、Mascot）用于位点特异性糖链分析
- **考虑位点上下文**：并非所有预测的序列子都会实际糖基化（可及性、细胞类型、蛋白质构象）
- **对于抗体**：Fc N297 糖基化至关重要——始终首先表征此位点
- **使用 GlyConnect** 检查您的目标蛋白质是否具有实验验证的糖基化数据

## 其他资源

- **GlyTouCan**（糖链结构存储库）：https://glytoucan.org/
- **GlyConnect**：https://glyconnect.expasy.org/
- **CFG 功能糖组学**：http://www.functionalglycomics.org/
- **DTU Health Tech 服务器**（NetNGlyc、NetOGlyc）：https://services.healthtech.dtu.dk/
- **GlycoWorkbench**：https://glycoworkbench.software.informer.com/
- **综述**：Apweiler R 等人（1999）Biochim Biophys Acta. PMID: 10564035
- **治疗性糖基工程综述**：Jefferis R (2009) Nature Reviews Drug Discovery. PMID: 19448661
