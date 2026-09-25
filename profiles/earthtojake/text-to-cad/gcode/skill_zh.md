# G-code

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad)。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源和发布审核。

使用此技能从网格文件生成纯 `.gcode`。它对打印机无关，从不上传、启动或打包打印作业。

## 工作流程

1. 确认输入是支持的网格：`.stl`、`.obj`、未切片的 `.3mf`、`.ply`、`.glb` 或 `.gltf`。
2. 需要一个明确的打印机/配置文件包装器 JSON。不要编造真实的打印机配置文件。
3. 当后端未知时发现切片器后端：

```bash
python scripts/gcode_tool.py discover
```

4. 检查输入：

```bash
python scripts/gcode_tool.py inspect --input path/to/model.stl --json
```

5. 在执行前进行切片器命令的干运行：

```bash
python scripts/gcode_tool.py slice \
  --input path/to/model.stl \
  --output /tmp/model.gcode \
  --profile path/to/profile.json \
  --backend auto \
  --dry-run
```

6. 仅在干运行命令和配置文件合适后执行：

```bash
python scripts/gcode_tool.py slice \
  --input path/to/model.stl \
  --output /tmp/model.gcode \
  --profile path/to/profile.json \
  --backend auto \
  --execute
```

7. 验证生成的 G-code：

```bash
python scripts/gcode_tool.py validate \
  --gcode /tmp/model.gcode \
  --profile path/to/profile.json \
  --json
```

## 配置文件契约

每个切片都需要一个带有绝对本地切片器配置文件路径的包装器配置文件 JSON：

```json
{
  "backend": "orcaslicer",
  "native_config": "/absolute/path/to/native-slicer-profile",
  "machine": {
    "name": "Example Printer",
    "bed_size_mm": [180, 180],
    "z_height_mm": 180,
    "motion_bounds_mm": {
      "x": [0, 180],
      "y": [0, 180],
      "z": [0, 180]
    }
  },
  "filament": {
    "type": "PLA",
    "nozzle_temp_c": 220,
    "bed_temp_c": 65
  }
}
```

包装器提供验证边界和后端选择。`machine.motion_bounds_mm` 是可选的；省略它以使用默认的 `0..bed_size` 和 `0..z_height` 边界，或从本地打印机配置文件中设置它，当启动/结束 G-code 故意使用打印区域外安全的擦拭/清理位置时。本地切片器配置文件仍然是详细工艺、打印机和线材行为的来源。

对于 OrcaSlicer，当真实配置文件分布在机器、工艺和线材 JSON 文件中时，使用 `native_settings` 和 `native_filaments`。保持 `native_config` 作为主要本地配置文件的绝对路径以保持兼容性：

```json
{
  "backend": "orcaslicer",
  "native_config": "/absolute/path/to/machine-or-process.json",
  "native_settings": [
    "/absolute/path/to/machine.json",
    "/absolute/path/to/process.json"
  ],
  "native_filaments": [
    "/absolute/path/to/filament.json"
  ],
  "machine": {
    "name": "Example Printer",
    "bed_size_mm": [180, 180],
    "z_height_mm": 180
  },
  "filament": {
    "type": "PLA",
    "nozzle_temp_c": 220,
    "bed_temp_c": 65
  }
}
```

## 后端和输入

首选的切片器后端顺序是 `orcaslicer`、`prusa-slicer`，然后是 `curaengine`。如果没有首选后端，优先安装 OrcaSlicer；在 macOS 上使用 `brew install --cask orcaslicer` 然后重新运行 `discover`。辅助工具会检查 `PATH` 和通常的 `/Applications/OrcaSlicer.app` cask 位置。Bambu Studio 可能会被发现为可用，但由于其 CLI 导出路径在 macOS 上显示不稳定，因此不优先使用。

直接将 `.stl`、`.obj` 和未切片的 `.3mf` 传递给切片器。使用可选的 `trimesh` 在执行时将 `.ply`、`.glb` 和 `.gltf` 转换为临时 STL；如果 `trimesh` 不可用，请要求用户安装它或提供 `.stl`、`.obj` 或未切片的 `.3mf`。

在 v1 中拒绝 `.step`、`.stp`、`.dxf`、`.svg`、`.urdf` 和 `.sdf`。`inspect` 和 `slice` 失败时会生成一个结构化的 `remediation` 对象，命名生成可切片网格的技能和命令；使用它而不是推断转换工作流：

- `.step`、`.stp`：边界表示 CAD，不是网格。使用 `$cad` 导出 STL 侧文件（`cadgen stl build <input.step> <output>.stl` — 门接收 STEP 文件；拒绝模型脚本，首先运行 `python <model>.py`），然后在此处切片导出的 `.stl`。
- `.dxf`、`.svg`：2D 绘图，在此工具链中没有 2D 到网格的转换。在 `$cad` 中将 3D 实体建模为 `@step` 模型脚本并导出 STL 侧文件，然后切片该文件。如果零件是平面切割而不是打印，请使用 `$sendcutsend` 而不是此技能。
- `.urdf`、`.sdf`：参考每个链接网格文件的机器人描述。逐个切片引用的 `.stl`/`.obj` 网格；首先使用 `$cad` 从拥有 CAD 源重新生成陈旧或缺失的网格。使用 `$urdf` 或 `$sdf` 本身用于机器人描述。

当后端行为、配置文件预期或源链接重要时，阅读 `references/slicer-backends.md`。

## 验证

在将生成的 G-code 交给打印机特定工作流之前，始终进行验证。验证器检查非空内容、温度命令、移动命令、挤出移动、XYZ 边界和未知命令警告。

当解释验证输出或决定警告是否可接受时，阅读 `references/gcode-validation.md`。

## Bambu 边界

此技能仅生成纯 `.gcode`。它不会创建 Bambu `.gcode.3mf` 存档，也不会联系打印机。对于 Bambu 上传/启动工作流，将验证的纯 `.gcode` 交给 `$bambu-labs`。让 `$bambu-labs` 选择打印机特定的 LAN 手动，例如 A1 Mini 模板项目或显式启用的 bambox 项目包。
