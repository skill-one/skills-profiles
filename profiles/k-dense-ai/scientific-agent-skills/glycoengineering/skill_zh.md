# 糖基工程

## 概述

糖基化是蛋白质最常见且最复杂的翻译后修饰（PTM），影响超过50%的人类蛋白质。糖链调节蛋白质折叠、稳定性、免疫识别、受体相互作用以及治疗性蛋白质的药代动力学。糖基工程涉及对糖基化模式的合理修饰，以改善治疗效果、稳定性或免疫逃逸。

**两种主要的糖基化类型：**
- **N-糖基化**：连接在序列子 N-X-[S/T] 中的天冬酰胺（N）处，其中 X ≠ 脯氨酸；发生在内质网/高尔基体
- **O-糖基化**：连接在丝氨酸（S）或苏氨酸（T）处；没有严格的共识基序；主要由GalNAc启动

## 何时使用此技能

使用此技能时：

- **抗体工程**：优化Fc糖基化以增强ADCC、CDC或降低免疫原性
- **治疗性蛋白质设计**：识别影响半衰期、稳定性或免疫原性的糖基化位点
- **疫苗抗原设计**：构建糖链屏障以将免疫反应集中于保守表位
- **生物类似物表征**：比较参考品和生物类似物之间的糖链模式
- **药物靶点分析**：糖基化是否影响受体的靶向结合？
- **蛋白质稳定性**：N-糖基通常稳定蛋白质；识别用于稳定突变的位点

## N-糖基化序列子分析

### 扫描N-糖基化位点

N-糖基化发生在序列子 **N-X-[S/T]** 处，其中 X ≠ 脯氨酸。

```python
import re
from typing import List, Tuple

def find_n_glycosylation_sequons(sequence: str) -> List[dict]:
    """
    扫描蛋白质序列以寻找经典的N连接糖基化序列子。
    基序：N-X-[S/T]，其中 X ≠ Proline。

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
            context = seq[max(0, i-3):i+6]  # ±3残基上下文
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
    """生成N-糖基化位点的科研日志摘要。"""
    sequons = find_n_glycosylation_sequons(sequence)

    lines = [f"# N-糖基化序列子分析：{protein_name or '蛋白质'}"]
    lines.append(f"序列长度：{len(sequence)}")
    lines.append(f"总N-糖基化序列子数量：{len(sequons)}")

    if sequons:
        lines.append(f"\nN-X-S位点：{sum(1 for s in sequons if s['sequon_type'] == 'NXS')}")
        lines.append(f"N-X-T位点：{sum(1 for s in sequons if s['sequon_type'] == 'NXT')}")
        lines.append(f"\n位点详情：")
        for s in sequons:
            lines.append(f"  位置 {s['position']}：{s['motif']}（上下文：...{s['context']}...）")
    else:
        lines.append("未检测到经典的N-糖基化序列子。")

    return "\n".join(lines)

# 示例：IgG1 Fc区域
fc_sequence = "APELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"
print(summarize_glycosylation_sites(fc_sequence, "IgG1 Fc"))
```

### 突变N-糖基化位点

```python
def eliminate_glycosite(sequence: str, position: int, replacement: str = "Q") -> str:
    """
    通过将天冬酰胺（Asn）→ 谷氨酰胺（Gln）进行保守替换来消除N-糖基化位点。

    Args:
        sequence: 蛋白质序列
        position: 1-based天冬酰胺突变位置
        replacement: 替换的氨基酸（默认Q = 谷氨酰胺；大小相似，不被糖基化）

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
    通过将残基突变成天冬酰胺来引入N-糖基化位点，
    并确保X ≠ Proline且+2 = S/T。

    Args:
        position: 引入天冬酰胺的1-based位置
        flanking_context: 'S'或'T'在位置+2（如果需要修改）
    """
    seq = list(sequence.upper())
    idx = position - 1

    # 突变成天冬酰胺
    seq[idx] = 'N'

    # 确保X+1 ≠ Proline（如果需要，将脯氨酸突变成丙氨酸）
    if idx + 1 < len(seq) and seq[idx + 1] == 'P':
        seq[idx + 1] = 'A'

    # 确保X+2 = S或T
    if idx + 2 < len(seq) and seq[idx + 2] not in ('S', 'T'):
        seq[idx + 2] = flanking_context

    return ''.join(seq)
```

## O-糖基化分析

### 启发式O-糖基化热点预测

```python
def predict_o_glycosylation_hotspots(
    sequence: str,
    window: int = 7,
    min_st_fraction: float = 0.4,
    disallow_proline_next: bool = True
) -> List[dict]:
    """
    基于局部S/T密度的启发式O-糖基化热点评分。
    不是NetOGlyc的替代品；仅作为快速基线。

    规则：
    - O-GalNAc糖基化在富含Ser/Thr的片段上聚集
    - 标记富含S/T的窗口中的Ser/Thr残基
    - 避免S/T立即后接脯氨酸（TP/SP基序抑制GalNAc-T）

    Args:
        window: 奇数窗口大小用于局部S/T密度
        min_st_fraction: 窗口中S/T的最小分数以标记位点
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

### 1. NetOGlyc 4.0（O-糖基化预测）

用于高精度O-GalNAc位点预测的网页服务：
- **URL**：https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/
- **输入**：FASTA蛋白质序列
- **输出**：每个残基的O-糖基化概率分数
- **方法**：基于实验验证O-GalNAc位点的神经网络训练

```python
import requests

def submit_netoglycv4(fasta_sequence: str) -> str:
    """
    将序列提交给NetOGlyc 4.0网页服务。
    返回用于结果检索的工作URL。

    注意：此服务使用DTU Health Tech网页服务。结果需要1-5分钟。
    """
    url = "https://services.healthtech.dtu.dk/cgi-bin/webface2.cgi"
    # NetOGlyc提交（参数可能随网页服务版本变化）
    # 建议大多数情况下直接使用网页界面
    print("在以下网址提交序列：https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/")
    return url

# 也有NetNGlyc用于N-糖基化预测
# URL：https://services.healthtech.dtu.dk/services/NetNGlyc-1.0/
```

### 2. GlycoSHIELD（糖链屏蔽分析）

GlycoSHIELD将预模拟的糖链构象库嫁接到静态蛋白质结构上，并评分糖链屏蔽了多少蛋白质表面，而无需运行新的MD模拟（Tsai等人，《Cell》2024，doi:10.1016/j.cell.2024.01.034）：
- **URL**：https://gitlab.mpcdf.mpg.de/dioscuri-biophysics/glycoshield-md/（网页应用：https://glycoshield.eu）
- **用途**：在糖蛋白上模拟糖链屏蔽，并映射每个位点的屏蔽情况
- **输出**：每个位点的糖基化PDB/XTC集合，每个残基的屏蔽图，B因子列中包含屏蔽信息的PDB

GlycoSHIELD**不在PyPI上**——`uv pip install glycoshield`会失败。它作为三个脚本随一个小的`glycoshield`包一起提供（需要numpy、scipy、matplotlib、MDAnalysis；`GlycoSASA.py`还需要`gmx`从GROMACS在`PATH`中）。从检出中安装：

```bash
# 安装（GPL-3.0）。糖链构象库需要单独下载——
# 参见glycan_library_downloader.py和GLYCAN_LIBRARY/在存储库中。
git clone https://gitlab.mpcdf.mpg.de/dioscuri-biophysics/glycoshield-md.git
cd glycoshield-md
uv pip install -e .

# 1. 将糖链构象嫁接到输入文件中列出的每个序列子上。
#    每行一个位点：<chain> <res-1,res,res+1> <1,2,3> <glycan.pdb> <glycan.xtc> <out.pdb> <out.xtc>
python GlycoSHIELD.py --protpdb protein.pdb --inputfile sequons_input \
    --threshold 3.5 --mode CG --shuffle-sugar

# 2. 跨嫁接集合的每个残基屏蔽分数（探针半径以nm计）
python GlycoSASA.py --pdblist A_463.pdb,A_492.pdb --xtclist A_463.xtc,A_492.xtc \
    --probelist 0.14,0.25 --plottrace
```

说明：标志来自脚本argparse定义和上游教程（N-钙粘蛋白EC5与Man5糖链）；此处未运行。`--mode CG`仅检查与Cα原子冲突，并配对`--threshold 3.5`；`--mode All`与`--threshold 0.7`是全原子设置。

### 3. GlycoWorkbench（糖链结构绘制/分析）

- **URL**：https://www.eurocarbdb.org/project/glycoworkbench
- **用途**：绘制糖链结构，计算质量，标注质谱图
- **格式**：GlycoCT，IUPAC缩合糖链表示法

### 4. GlyConnect（糖链-蛋白质数据库）

- **URL**：https://glyconnect.expasy.org/
- **用途**：查找实验验证的糖蛋白和糖基化位点
- **查询**：通过蛋白质（UniProt ID）、糖链结构或组织

```python
import requests

def query_glyconnect(uniprot_id: str) -> dict:
    """查询GlyConnect以获取蛋白质的糖基化数据。"""
    url = f"https://glyconnect.expasy.org/api/proteins/uniprot/{uniprot_id}"
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code == 200:
        return response.json()
    return {}

# 示例：查询EGFR糖基化
egfr_glyco = query_glyconnect("P00533")
```

### 5. UniCarbKB（糖链结构数据库）

- **URL**：https://unicarbkb.org/
- **用途**：浏览糖链结构，按质量或组成搜索
- **格式**：GlycoCT或IUPAC表示法

## 关键糖基工程策略

### 用于治疗性抗体

| 目标 | 策略 | 备注 |
|------|------|------|
| 增强ADCC | Fc Asn297去岩藻糖基化 | 去岩藻糖基化IgG1的FcγRIIIa结合能力提高约50倍 |
| 降低免疫原性 | 去除非人糖链 | 消除α-Gal，NGNA表位 |
| 改善PK半衰期 | 神经氨酸化 | 神经氨酸化糖链延长半衰期 |
| 减少炎症 | 超神经氨酸化 | IVIG抗炎机制 |
| 创建糖链屏障 | 在表面添加N-糖基位点 | 遮蔽易感表位（疫苗设计） |

### 常用突变

| 突变 | 效果 |
|------|------|
| N297A/Q (IgG1) | 去除Fc糖基化（无糖基化） |
| N297D (IgG1) | 去除Fc糖基化 |
| S298A/E333A/K334A | 增加FcγRIIIa结合 |
| F243L (IgG1) | 增加去岩藻糖基化 |
| T299A | 去除Fc糖基化 |

## 糖链表示法

### IUPAC缩合表示法（单糖缩写）

| 符号 | 全称 | 类型 |
|------|------|------|
| Glc | Glucose | 六碳糖 |
| GlcNAc | N-Acetylglucosamine | 六碳N-乙酰氨基糖 |
| Man | Mannose | 六碳糖 |
| Gal | Galactose | 六碳糖 |
| Fuc | Fucose | 去氧六碳糖 |
| Neu5Ac | N-Acetylneuraminic acid (Sialic acid) | 神经氨酸 |
| GalNAc | N-Acetylgalactosamine | 六碳N-乙酰氨基糖 |

### 复杂N-糖链结构

```
典型的双天线复合N-糖链：
Neu5Ac-Gal-GlcNAc-Man\
                       Man-GlcNAc-GlcNAc-[Asn]
Neu5Ac-Gal-GlcNAc-Man/
(±最内层GlcNAc处的核心岩藻糖)
```

## 最佳实践

- **先使用NetNGlyc/NetOGlyc进行计算预测**，然后再进行实验验证
- **使用质谱法验证**：糖组学（Byonic，Mascot）进行位点特异性糖链分析
- **考虑位点上下文**：并非所有预测的序列子都会被糖基化（可及性、细胞类型、蛋白质构象）
- **对于抗体**：Fc N297糖基化至关重要——始终首先表征此位点
- **使用GlyConnect**检查您的目标蛋白质是否具有实验验证的糖基化数据

## 其他资源

- **GlyTouCan**（糖链结构数据库）：https://glytoucan.org/
- **GlyConnect**：https://glyconnect.expasy.org/
- **CFG功能糖组学**：http://www.functionalglycomics.org/
- **DTU Health Tech服务器**（NetNGlyc，NetOGlyc）：https://services.healthtech.dtu.dk/
- **GlycoWorkbench**：https://glycoworkbench.software.informer.com/
- **综述**：Apweiler R等人（1999）Biochim Biophys Acta. PMID: 10564035
- **治疗性糖基工程综述**：Jefferis R（2009）Nature Reviews Drug Discovery. PMID: 19448661
