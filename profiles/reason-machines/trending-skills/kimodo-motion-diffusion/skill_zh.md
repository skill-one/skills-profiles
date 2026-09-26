# Kimodo Motion Diffusion

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Kimodo 是一个基于700小时商业友好型光学mocap数据训练的动力学运动扩散模型。它可以生成高质量的3D人类和类人机器人运动，通过文本提示和动力学约束（全身关键帧、末端执行器位置/旋转、2D路径、2D航点）进行控制。

## 安装

```bash
# 克隆仓库
git clone https://github.com/nv-tlabs/kimodo.git
cd kimodo

# 使用pip安装（创建kimodo_gen和kimodo_demo CLI命令）
pip install -e .

# 或者使用Docker（推荐用于Windows或干净环境）
docker build -t kimodo .
docker run --gpus all -p 7860:7860 kimodo
```

**要求：**
- ~17GB显存VRAM（GPU：RTX 3090/4090，推荐A100）
- Linux（Windows通过Docker支持）
- 模型在首次使用时自动从Hugging Face下载

## 可用模型

| 模型 | 骨架 | 数据集 | 用途 |
|-------|----------|---------|----------|
| `Kimodo-SOMA-RP-v1` | SOMA（人类） | Bones Rigplay 1（700小时） | 通用人类运动 |
| `Kimodo-G1-RP-v1` | Unitree G1（机器人） | Bones Rigplay 1（700小时） | 类人机器人运动 |
| `Kimodo-SOMA-SEED-v1` | SOMA | BONES-SEED（288小时） | 基准测试 |
| `Kimodo-G1-SEED-v1` | Unitree G1 | BONES-SEED（288小时） | 基准测试 |
| `Kimodo-SMPLX-RP-v1` | SMPL-X | Bones Rigplay 1（700小时） | 重定向/AMASS导出 |

## CLI: `kimodo_gen`

### 基础文本到运动

```bash
# 使用文本提示生成单个运动（默认使用SOMA模型）
kimodo_gen "一个人以中等速度向前行走"

# 指定持续时间和样本数量
kimodo_gen "一个人在圈中慢跑" --duration 5.0 --num_samples 3

# 使用G1机器人模型
kimodo_gen "一个机器人向前行走" --model Kimodo-G1-RP-v1 --duration 4.0

# 使用SMPL-X模型（用于AMASS兼容导出）
kimodo_gen "一个人挥动右手" --model Kimodo-SMPLX-RP-v1

# 设置种子以实现可重复性
kimodo_gen "一个人缓慢坐下" --seed 42

# 控制扩散步数（更多 = 更慢但质量更高）
kimodo_gen "一个人做跳跃杰克" --diffusion_steps 50
```

### 输出格式

```bash
# 默认：保存与网络演示兼容的NPZ文件
kimodo_gen "一个人行走" --output ./outputs/walk.npz

# G1机器人：保存MuJoCo qpos CSV
kimodo_gen "机器人向前行走" --model Kimodo-G1-RP-v1 --output ./outputs/walk.csv

# SMPL-X：保存AMASS兼容的NPZ（stem_amass.npz）
kimodo_gen "一个人挥手" --model Kimodo-SMPLX-RP-v1 --output ./outputs/wave.npz
# 也写入：./outputs/wave_amass.npz

# 禁用后处理（脚部滑行校正、约束清理）
kimodo_gen "一个人行走" --no-postprocess
```

### 多提示序列

```bash
# 文本提示序列用于过渡
kimodo_gen "一个人静止站立" "一个人向前行走" "一个人停下并转身"

# 每个片段的定时控制
kimodo_gen "一个人慢跑" "一个人慢走到行走" "一个人停止" \
  --duration 8.0 --num_samples 2
```

### 基于约束的生成

```bash
# 加载交互式演示保存的约束
kimodo_gen "一个人走向桌子并拿起某物" \
  --constraints ./my_constraints.json

# 结合文本和约束
kimodo_gen "一个人执行复杂动作" \
  --constraints ./keyframe_constraints.json \
  --model Kimodo-SOMA-RP-v1 \
  --num_samples 5
```

## 交互式演示

```bash
# 启动基于网络的演示：http://127.0.0.1:7860
kimodo_demo

# 远程访问（服务器设置）
kimodo_demo --server-name 0.0.0.0 --server-port 7860
```

演示提供：
- 文本提示和约束的时间轴编辑器
- 全身关键帧约束
- 2D根路径/航点编辑器
- 末端执行器位置/旋转控制
- 实时3D可视化（带骨架和蒙皮网格）
- 将约束导出为JSON，运动导出为NPZ

## 低级Python API

### 基本模型推理

```python
from kimodo.model import Kimodo

# 初始化模型（自动下载）
model = Kimodo(model_name="Kimodo-SOMA-RP-v1")

# 简单文本到运动生成
result = model(
    prompts=["一个人以中等速度向前行走"],
    duration=4.0,
    num_samples=1,
    seed=42,
)

# 结果包含姿势关节、旋转矩阵、脚部接触
print(result["posed_joints"].shape)       # [T, J, 3]
print(result["global_rot_mats"].shape)    # [T, J, 3, 3]
print(result["local_rot_mats"].shape)     # [T, J, 3, 3]
print(result["foot_contacts"].shape)      # [T, 4]
print(result["root_positions"].shape)     # [T, 3]
```

### 带引导和约束的高级API

```python
from kimodo.model import Kimodo
import numpy as np

model = Kimodo(model_name="Kimodo-SOMA-RP-v1")

# 多提示带classifier-free引导控制
result = model(
    prompts=["一个人站立", "一个人向前行走", "一个人坐下"],
    duration=9.0,
    num_samples=3,
    diffusion_steps=50,
    guidance_scale=7.5,           # classifier-free引导权重
    seed=0,
)

# 访问每个样本结果
for i in range(3):
    joints = result["posed_joints"][i]   # [T, J, 3]
    print(f"样本{i}: {joints.shape}")
```

### 程序化处理约束

```python
from kimodo.model import Kimodo
from kimodo.constraints import ConstraintSet, FullBodyKeyframe, EndEffectorConstraint
import numpy as np

model = Kimodo(model_name="Kimodo-SOMA-RP-v1")

# 创建约束集
constraints = ConstraintSet()

# 在第30帧（30fps的1秒）添加全身关键帧
# keyframe_pose: [J, 3] 关节位置
keyframe_pose = np.zeros((model.num_joints, 3))  # 替换为实际姿势
constraints.add_full_body_keyframe(frame=30, joint_positions=keyframe_pose)

# 添加右手末端执行器约束
constraints.add_end_effector(
    joint_name="right_hand",
    frame_start=45,
    frame_end=60,
    position=np.array([0.5, 1.2, 0.3]),   # [x, y, z] 米为单位
    rotation=None,                           # 可选旋转矩阵 [3,3]
)

# 添加根路径的2D航点
constraints.add_root_waypoints(
    waypoints=np.array([[0, 0], [1, 0], [1, 1], [0, 1]]),  # [N, 2] 米为单位
)

# 带约束生成
result = model(
    prompts=["一个人在方形中行走"],
    duration=6.0,
    constraints=constraints,
    num_samples=2,
)
```

### 加载和使用保存的约束

```python
from kimodo.model import Kimodo
from kimodo.constraints import ConstraintSet
import json

model = Kimodo(model_name="Kimodo-SOMA-RP-v1")

# 从网络演示加载约束
with open("constraints.json") as f:
    constraint_data = json.load(f)

constraints = ConstraintSet.from_dict(constraint_data)

result = model(
    prompts=["一个人执行编排序列"],
    duration=8.0,
    constraints=constraints,
)
```

### 保存和加载生成的运动

```python
import numpy as np

# 保存结果
result = model(prompts=["一个人行走"], duration=4.0)
np.savez("walk_motion.npz", **result)

# 加载并检查保存的运动
data = np.load("walk_motion.npz")
posed_joints = data["posed_joints"]       # [T, J, 3] 全局关节位置
global_rot_mats = data["global_rot_mats"] # [T, J, 3, 3]
local_rot_mats = data["local_rot_mats"]   # [T, J, 3, 3]
foot_contacts = data["foot_contacts"]     # [T, 4] [L-heel, L-toe, R-heel, R-toe]
root_positions = data["root_positions"]   # [T, 3] 实际根关节轨迹
smooth_root_pos = data["smooth_root_pos"] # [T, 3] 模型平滑根轨迹
global_root_heading = data["global_root_heading"]  # [T, 2] 方向（2D单位向量）
```

## 机器人集成

### MuJoCo可视化（G1机器人）

```bash
# 生成G1运动并保存为MuJoCo qpos CSV
kimodo_gen "一个机器人向前行走并挥手" \
  --model Kimodo-G1-RP-v1 \
  --output ./robot_walk.csv \
  --duration 5.0

# 在MuJoCo中可视化（编辑脚本指向你的CSV）
python -m kimodo.scripts.mujoco_load
```

```python
# mujoco_load.py自定义模式
import mujoco
import numpy as np

# 在脚本中编辑这些路径
CSV_PATH = "./robot_walk.csv"
MJCF_PATH = "./assets/g1/g1.xml"  # G1 MuJoCo模型路径

# 加载qpos数据
qpos_data = np.loadtxt(CSV_PATH, delimiter=",")

# 标准MuJoCo播放循环
model = mujoco.MjModel.from_xml_path(MJCF_PATH)
data = mujoco.MjData(model)
with mujoco.viewer.launch_passive(model, data) as viewer:
    for frame_qpos in qpos_data:
        data.qpos[:] = frame_qpos
        mujoco.mj_forward(model, data)
        viewer.sync()
```

### ProtoMotions集成

```bash
# 使用Kimodo生成运动
kimodo_gen "一个人跑步和跳跃" --model Kimodo-SOMA-RP-v1 \
  --output ./run_jump.npz --duration 5.0

# 然后按照ProtoMotions文档导入：
# https://github.com/NVlabs/ProtoMotions#motion-authoring-with-kimodo
```

### GMR重定向（SMPL-X到其他机器人）

```bash
# 生成SMPL-X运动（自动保存stem_amass.npz）
kimodo_gen "一个人做翻滚" \
  --model Kimodo-SMPLX-RP-v1 \
  --output ./cartwheel.npz

# 使用cartwheel_amass.npz与GMR进行重定向
# https://github.com/YanjieZe/GMR
```

## NPZ输出格式参考

| 键 | 形状 | 描述 |
|-----|-------|-------------|
| `posed_joints` | `[T, J, 3]` | 全局关节位置（米） |
| `global_rot_mats` | `[T, J, 3, 3]` | 全局关节旋转矩阵 |
| `local_rot_mats` | `[T, J, 3, 3]` | 父相对关节旋转矩阵 |
| `foot_contacts` | `[T, 4]` | 接触标签：[L-heel, L-toe, R-heel, R-toe] |
| `smooth_root_pos` | `[T, 3]` | 模型平滑根轨迹 |
| `root_positions` | `[T, 3]` | 实际根关节（骨盆）轨迹 |
| `global_root_heading` | `[T, 2]` | 方向（2D单位向量） |

`T` = 帧数（30fps），`J` = 关节数（取决于骨架）

## 脚本参考

```bash
# 直接执行脚本（CLI替代方案）
python scripts/generate.py "一个人行走" --duration 4.0

# G1输出的MuJoCo可视化
python -m kimodo.scripts.mujoco_load

# 所有kimodo_gen标志
kimodo_gen --help
```

## 常见模式

### 批量生成流程

```python
from kimodo.model import Kimodo
import numpy as np
from pathlib import Path

model = Kimodo(model_name="Kimodo-SOMA-RP-v1")
output_dir = Path("./batch_outputs")
output_dir.mkdir(exist_ok=True)

prompts = [
    "一个人向前行走",
    "一个人跑步",
    "一个人原地跳跃",
    "一个人坐下",
    "一个人从地板上拿起一个物体",
]

for i, prompt in enumerate(prompts):
    result = model(
        prompts=[prompt],
        duration=4.0,
        num_samples=1,
        seed=i,
    )
    out_path = output_dir / f"motion_{i:03d}.npz"
    np.savez(str(out_path), **result)
    print(f"保存：{out_path}")
```

### 比较模型变体

```python
from kimodo.model import Kimodo
import numpy as np

prompt = "一个人向前行走"
models = ["Kimodo-SOMA-RP-v1", "Kimodo-SOMA-SEED-v1"]

results = {}
for model_name in models:
    model = Kimodo(model_name=model_name)
    results[model_name] = model(
        prompts=[prompt],
        duration=4.0,
        seed=0,
    )
    print(f"{model_name}: 关节形状 = {results[model_name]['posed_joints'].shape}")
```

## 故障排除

**显存不足（~17GB要求）：**
```bash
# 检查可用显存
nvidia-smi

# 减少样本以减少峰值显存
kimodo_gen "一个人行走" --num_samples 1

# 减少扩散步数以加速（质量较低）
kimodo_gen "一个人行走" --diffusion_steps 20
```

**模型下载问题：**
```bash
# 模型从Hugging Face自动下载
# 如果在代理后，设置：
export HF_ENDPOINT=https://huggingface.co
export HUGGINGFACE_HUB_VERBOSITY=debug

# 或者手动指定缓存目录
export HF_HOME=/path/to/your/cache
```

**运动质量问题：**
- 在提示中具体： "一个人以中等速度向前行走" > "行走"
- 对于复杂运动，使用交互式演示添加关键帧约束
- 增加 `--diffusion_steps`（默认~20-30，尝试50以获得更高质量）
- 生成多个样本 (`--num_samples 5`) 并选择最佳结果
- 避免提示中包含极快或物理上不可能的动作
- 模型以30fps运行；非常短的持续时间（<1s）可能产生不良结果

**脚部滑行伪影：**
```bash
# 默认启用后处理；仅用于调试禁用
kimodo_gen "一个人行走" # 后处理开启（默认）
kimodo_gen "一个人行走" --no-postprocess  # 后处理关闭
```

**交互式演示未加载：**
```bash
# 确保端口7860可用
lsof -i :7860

# 在不同端口启动
kimodo_demo --server-port 7861

# 用于远程服务器访问
kimodo_demo --server-name 0.0.0.0 --server-port 7860
# 然后使用SSH端口转发：ssh -L 7860:localhost:7860 user@server
```
