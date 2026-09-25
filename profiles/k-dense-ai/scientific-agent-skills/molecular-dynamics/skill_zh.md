# 分子动力学

## 概述

分子动力学（MD）模拟通过积分牛顿运动方程，计算分子系统的动力学演化。这项技能涵盖两个互补的工具：

- **OpenMM** (https://openmm.org/)：高性能MD模拟引擎，支持GPU，具有Python API和灵活的力场支持
- **MDAnalysis** (https://mdanalysis.org/)：用于读取、写入和分析所有主要模拟软件生成的MD轨迹的Python库

**安装：**
```bash
conda install -c conda-forge openmm mdanalysis nglview
# 或者
uv pip install openmm mdanalysis
```

## 何时使用此技能

使用分子动力学模拟：

- **蛋白质稳定性分析**：突变如何影响蛋白质动力学？
- **药物结合模拟**：表征配体的结合模式和停留时间
- **构象采样**：探索蛋白质的柔性和构象变化
- **蛋白质-蛋白质相互作用**：模拟界面动力学和结合能
- **RMSD/RMSF分析**：从参考结构量化结构波动
- **自由能估计**：计算结合自由能或构象自由能
- **膜模拟**：在脂质双分子层中模拟蛋白质
- **内在无序蛋白质**：研究IDR构象集合

## 核心工作流：OpenMM模拟

### 1. 系统准备

```python
from openmm.app import *
from openmm import *
from openmm.unit import *
import sys

def prepare_system_from_pdb(pdb_file, forcefield_name="amber14-all.xml",
                              water_model="amber14/tip3pfb.xml"):
    """
    从PDB文件准备OpenMM系统。

    Args:
        pdb_file: 清洗后的PDB文件路径（原始PDB文件使用PDBFixer）
        forcefield_name: 力场XML文件
        water_model: 水模型XML文件

    Returns:
        pdb, forcefield, system, topology
    """
    # 加载PDB
    pdb = PDBFile(pdb_file)

    # 加载力场
    forcefield = ForceField(forcefield_name, water_model)

    # 添加氢原子和溶剂化
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens(forcefield)

    # 添加溶剂盒子（10 Å填充，150 mM NaCl）
    modeller.addSolvent(
        forcefield,
        model='tip3p',
        padding=10*angstroms,
        ionicStrength=0.15*molar
    )

    print(f"系统：{modeller.topology.getNumAtoms()}个原子， "
          f"{modeller.topology.getNumResidues()}个残基")

    # 创建系统
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=PME,         # 用于长程静电的粒子网格Ewald方法
        nonbondedCutoff=1.0*nanometer,
        constraints=HBonds,           # 约束氢键（允许2 fs时间步长）
        rigidWater=True,
        ewaldErrorTolerance=0.0005
    )

    return modeller, system
```

### 2. 能量最小化

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

def minimize_energy(modeller, system, output_pdb="minimized.pdb",
                     max_iterations=1000, tolerance=10.0):
    """
    能量最小化系统以消除空间位阻冲突。

    Args:
        modeller: 具有拓扑和位置信息的Modeller对象
        system: OpenMM System
        output_pdb: 保存最小化结构的PDB文件路径
        max_iterations: 最大最小化步数
        tolerance: 收敛标准（kJ/mol/nm）

    Returns:
        具有最小化位置信息的模拟对象
    """
    # 设置积分器（对最小化无关紧要）
    integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.004*picoseconds)

    # 创建模拟对象
    # 如果可用，使用GPU（CUDA或OpenCL），否则回退到CPU
    try:
        platform = Platform.getPlatformByName('CUDA')
        properties = {'DeviceIndex': '0', 'Precision': 'mixed'}
    except Exception:
        try:
            platform = Platform.getPlatformByName('OpenCL')
            properties = {}
        except Exception:
            platform = Platform.getPlatformByName('CPU')
            properties = {}

    simulation = Simulation(
        modeller.topology, system, integrator,
        platform, properties
    )
    simulation.context.setPositions(modeller.positions)

    # 检查初始能量
    state = simulation.context.getState(getEnergy=True)
    print(f"初始能量：{state.getPotentialEnergy()}")

    # 最小化
    simulation.minimizeEnergy(
        tolerance=tolerance*kilojoules_per_mole/nanometer,
        maxIterations=max_iterations
    )

    state = simulation.context.getState(getEnergy=True, getPositions=True)
    print(f"最小化能量：{state.getPotentialEnergy()}")

    # 保存最小化结构
    with open(output_pdb, 'w') as f:
        PDBFile.writeFile(simulation.topology, state.getPositions(), f)

    return simulation
```

### 3. NVT 热平衡

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

def run_nvt_equilibration(simulation, n_steps=50000, temperature=300,
                            report_interval=1000, output_prefix="nvt"):
    """
    NVT 热平衡：恒定 N, V, T。
    平衡速度至目标温度。

    Args:
        simulation: OpenMM Simulation（最小化后）
        n_steps: MD 步数（50000 × 2fs = 100 ps）
        temperature: 温度（开尔文）
        report_interval: 数据报告之间的步数
        output_prefix: 轨迹和日志文件的前缀
    """
    # 在NVT期间对主链添加位置约束（可选：约束重原子）

    # 设置温度
    simulation.context.setVelocitiesToTemperature(temperature*kelvin)

    # 添加报告器
    simulation.reporters = []

    # 日志文件
    simulation.reporters.append(
        StateDataReporter(
            f"{output_prefix}_log.txt",
            report_interval,
            step=True,
            potentialEnergy=True,
            kineticEnergy=True,
            temperature=True,
            volume=True,
            speed=True
        )
    )

    # DCD轨迹（紧凑的二进制格式）
    simulation.reporters.append(
        DCDReporter(f"{output_prefix}_traj.dcd", report_interval)
    )

    print(f"运行NVT热平衡：{n_steps}步 ({n_steps*2/1000:.1f} ps)")
    simulation.step(n_steps)
    print("NVT热平衡完成")

    return simulation
```

### 4. NPT 热平衡和生产

```python
def run_npt_production(simulation, n_steps=500000, temperature=300, pressure=1.0,
                        report_interval=5000, output_prefix="npt"):
    """
    NPT 生产运行：恒定 N, P, T。

    Args:
        n_steps: 生产步数（500000 × 2fs = 1 ns）
        temperature: 温度（开尔文）
        pressure: 压力（巴）
        report_interval: 报告之间的步数
    """
    # 添加蒙特卡洛压力计以控制压力
    system = simulation.context.getSystem()
    system.addForce(MonteCarloBarostat(pressure*bar, temperature*kelvin, 25))
    simulation.context.reinitialize(preserveState=True)

    # 更新报告器
    simulation.reporters = []
    simulation.reporters.append(
        StateDataReporter(
            f"{output_prefix}_log.txt",
            report_interval,
            step=True,
            potentialEnergy=True,
            temperature=True,
            density=True,
            speed=True
        )
    )
    simulation.reporters.append(
        DCDReporter(f"{output_prefix}_traj.dcd", report_interval)
    )

    # 保存检查点
    simulation.reporters.append(
        CheckpointReporter(f"{output_prefix}_checkpoint.chk", 50000)
    )

    print(f"运行NPT生产：{n_steps}步 ({n_steps*2/1000000:.2f} ns)")
    simulation.step(n_steps)
    print("生产MD完成")
    return simulation
```

## 使用 MDAnalysis 进行轨迹分析

### 1. 加载轨迹

```python
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align, contacts
import numpy as np
import matplotlib.pyplot as plt

def load_trajectory(topology_file, trajectory_file):
    """
    使用MDAnalysis加载MD轨迹。

    Args:
        topology_file: PDB、PSF或其他拓扑文件
        trajectory_file: DCD、XTC、TRR或其他轨迹文件
    """
    u = mda.Universe(topology_file, trajectory_file)
    print(f"Universe: {u.atoms.n_atoms}个原子， {u.trajectory.n_frames}帧")
    print(f"时间范围：0 到 {u.trajectory.totaltime:.0f} ps")
    return u
```

### 2. RMSD 分析

```python
def compute_rmsd(u, selection="backbone", reference_frame=0):
    """
    计算选定原子的RMSD（相对于参考帧）。

    Args:
        u: MDAnalysis Universe
        selection: 原子选择字符串（MDAnalysis语法）
        reference_frame: 参考结构的帧索引

    Returns:
        (时间，RMSD)值的numpy数组
    """
    # 将轨迹对齐以最小化RMSD
    aligner = align.AlignTraj(u, u, select=selection, in_memory=True)
    aligner.run()

    # 计算RMSD
    R = rms.RMSD(u, select=selection, ref_frame=reference_frame)
    R.run()

    rmsd_data = R.results.rmsd  # 列：帧，时间，RMSD
    return rmsd_data

def plot_rmsd(rmsd_data, title="随时间的RMSD", output_file="rmsd.png"):
    """绘制随模拟时间的RMSD。"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(rmsd_data[:, 1] / 1000, rmsd_data[:, 2], 'b-', linewidth=0.5)
    ax.set_xlabel("时间 (ns)")
    ax.set_ylabel("RMSD (Å)")
    ax.set_title(title)
    ax.axhline(rmsd_data[:, 2].mean(), color='r', linestyle='--',
               label=f'平均值：{rmsd_data[:, 2].mean():.2f} Å')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    return fig
```

### 3. RMSF 分析（每残基的柔性）

```python
def compute_rmsf(u, selection="backbone", start_frame=0):
    """
    计算每残基的RMSF（柔性）。

    Returns:
        resids, rmsf_values数组
    """
    # 选择原子
    atoms = u.select_atoms(selection)

    # 计算RMSF
    R = rms.RMSF(atoms)
    R.run(start=start_frame)

    # 按残基平均
    resids = []
    rmsf_per_res = []
    for res in u.select_atoms(selection).residues:
        res_atoms = res.atoms.intersection(atoms)
        if len(res_atoms) > 0:
            resids.append(res.resid)
            rmsf_per_res.append(R.results.rmsf[res_atoms.indices].mean())

    return np.array(resids), np.array(rmsf_per_res)
```

### 4. 蛋白质-配体接触

```python
def analyze_contacts(u, protein_sel="protein", ligand_sel="resname LIG",
                      radius=4.5, start_frame=0):
    """
    跟踪轨迹中蛋白质-配体接触。

    Args:
        radius: 接触距离截止值（埃）
    """
    protein = u.select_atoms(protein_sel)
    ligand = u.select_atoms(ligand_sel)

    contact_frames = []
    for ts in u.trajectory[start_frame:]:
        # 查找蛋白质原子与配体原子距离小于radius的原子
        distances = contacts.contact_matrix(
            protein.positions, ligand.positions, radius
        )
        contact_residues = set()
        for i in range(distances.shape[0]):
            if distances[i].any():
                contact_residues.add(protein.atoms[i].resid)
        contact_frames.append(contact_residues)

    return contact_frames
```

## 力场选择指南

| 系统 | 推荐力场 | 水模型 |
|------|----------|--------|
| 标准蛋白质 | AMBER14 (`amber14-all.xml`) | TIP3P-FB |
| 蛋白质+小分子 | AMBER14 + GAFF2 | TIP3P-FB |
| 膜蛋白 | CHARMM36m | TIP3P |
| 核酸 | AMBER99-bsc1 或 AMBER14 | TIP3P |
| 无序蛋白质 | ff19SB 或 CHARMM36m | TIP3P |

## 系统准备工具

### PDBFixer（用于原始PDB文件）

```python
from pdbfixer import PDBFixer
from openmm.app import PDBFile

def fix_pdb(input_pdb, output_pdb, ph=7.0):
    """修复常见的PDB问题：缺失残基、原子，添加H，标准化。"""
    fixer = PDBFixer(filename=input_pdb)
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(True)    # 移除水/配体
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(ph)

    with open(output_pdb, 'w') as f:
        PDBFile.writeFile(fixer.topology, fixer.positions, f)

    return output_pdb
```

### GAFF2 用于小分子（通过 OpenFF 工具包）

```python
# 用于配体参数化，使用 OpenFF 工具包或 ACPYPE
# uv pip install openff-toolkit
from openff.toolkit import Molecule, ForceField as OFFForceField
from openff.interchange import Interchange

def parameterize_ligand(smiles, ff_name="openff-2.0.0.offxml"):
    """为小分子生成GAFF2/OpenFF参数。"""
    mol = Molecule.from_smiles(smiles)
    mol.generate_conformers(n_conformers=1)

    off_ff = OFFForceField(ff_name)
    interchange = off_ff.create_interchange(mol.to_topology())
    return interchange
```

## 最佳实践

- **始终在MD前最小化**：原始PDB结构存在空间位阻冲突
- **在生产行为前进行热平衡**：NVT（50–100 ps）→ NPT（100–500 ps）→ 生产
- **使用GPU**：GPU（CUDA/OpenCL）可加速模拟10–100倍
- **2 fs时间步长，带HBonds约束**：标准；使用4 fs带HMR（氢质量重新分配）
- **仅分析平衡后的轨迹**：舍弃最初20–50%作为热平衡部分
- **保存检查点**：MD运行可能失败；检查点允许重新启动
- **周期性边界条件**：溶剂化系统必需
- **PME用于静电**：比截断方法对带电系统更准确

## 额外资源

- **OpenMM文档**：https://openmm.org/documentation.html
- **MDAnalysis用户指南**：https://docs.mdanalysis.org/
- **GROMACS**（替代MD引擎）：https://manual.gromacs.org/
- **NAMD**（替代）：https://www.ks.uiuc.edu/Research/namd/
- **CHARMM-GUI**（基于Web的系统构建器）：https://charmm-gui.org/
- **AmberTools**（免费Amber工具）：https://ambermd.org/AmberTools.php
- **OpenMM论文**：Eastman P et al. (2017) PLOS Computational Biology. PMID: 28278240
- **MDAnalysis论文**：Michaud-Agrawal N et al. (2011) J Computational Chemistry. PMID: 21500218
