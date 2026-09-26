# FreeCAD 脚本

用于 FreeCAD CAD 应用程序生成生产质量 Python 脚本的专家技能。解释简写、类代码和 3D 建模任务的自然语言描述，并将它们转换为正确的 FreeCAD Python API 调用。

## 使用此技能的场景

- 为 FreeCAD 的内置控制台或宏系统编写 Python 脚本
- 创建或操作 3D 几何体（Part、Mesh、Sketcher、Path、FEM）
- 构建具有自定义属性的参数化 FeaturePython 对象
- 使用 PySide/Qt 在 FreeCAD 中开发 GUI 工具
- 通过 Pivy 操作 Coin3D 场景图
- 创建自定义工作台或 Gui Commands
- 使用宏自动执行重复的 CAD 操作
- 在网格和实体表示之间转换
- 脚本 FEM 分析、光线追踪或绘图导出

## 前置条件

- 已安装 FreeCAD（推荐 0.19+；最新 API 需要 0.21+/1.0+）
- Python 3.x（随 FreeCAD 一并提供）
- 对于 GUI 工作：PySide2（随 FreeCAD 一并提供）
- 对于场景图：Pivy（随 FreeCAD 一并提供）

## FreeCAD Python 环境

FreeCAD 嵌入了一个 Python 解释器。脚本在以下关键模块可用的环境中运行：

```python
import FreeCAD          # 核心模块（也别名为 'App'）
import FreeCADGui       # GUI 模块（也别名为 'Gui'）— 仅在 GUI 模式下可用
import Part             # Part 工作台 — BRep/OpenCASCADE 形状
import Mesh             # Mesh 工作台 — 三角网格
import Sketcher         # Sketcher 工作台 — 2D 受约束草图
import Draft            # Draft 工作台 — 2D 绘图工具
import Arch             # Arch/BIM 工作台
import Path             # Path/CAM 工作台
import FEM              # FEM 工作台
import TechDraw         # TechDraw 工作台（替换 Drawing）
import BOPTools         # 布尔运算
import CompoundTools    # 复合形状工具
```

### FreeCAD 文档模型

```python
# 创建或访问文档
doc = FreeCAD.newDocument("MyDoc")
doc = FreeCAD.ActiveDocument

# 添加对象
box = doc.addObject("Part::Box", "MyBox")
box.Length = 10.0
box.Width = 10.0
box.Height = 10.0

# 重新计算
doc.recompute()

# 访问对象
obj = doc.getObject("MyBox")
obj = doc.MyBox  # 属性访问也有效

# 移除对象
doc.removeObject("MyBox")
```

## 核心概念

### 向量和放置

```python
import FreeCAD

# 向量
v1 = FreeCAD.Vector(1, 0, 0)
v2 = FreeCAD.Vector(0, 1, 0)
v3 = v1.cross(v2)          # 叉积
d = v1.dot(v2)              # 点积
v4 = v1 + v2                # 加法
length = v1.Length           # 模长
v_norm = FreeCAD.Vector(v1)
v_norm.normalize()           # 原地归一化

# 旋转
rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 45)  # 轴, 角度(度)
rot = FreeCAD.Rotation(0, 0, 45)                       # 欧拉角 (偏航, 俯仰, 翻滚)

# 放置（位置 + 方向）
placement = FreeCAD.Placement(
    FreeCAD.Vector(10, 20, 0),    # 平移
    FreeCAD.Rotation(0, 0, 45),   # 旋转
    FreeCAD.Vector(0, 0, 0)       # 旋转中心
)
obj.Placement = placement

# 矩阵（4x4 变换）
import math
mat = FreeCAD.Matrix()
mat.move(FreeCAD.Vector(10, 0, 0))
mat.rotateZ(math.radians(45))
```

### 创建和操作几何体（Part 模块）

Part 模块封装了 OpenCASCADE，并提供 BRep 实体建模：

```python
import FreeCAD
import Part

# --- 基本形状 ---
box = Part.makeBox(10, 10, 10)               # 长度, 宽度, 高度
cyl = Part.makeCylinder(5, 20)               # 半径, 高度
sphere = Part.makeSphere(10)                  # 半径
cone = Part.makeCone(5, 2, 10)               # r1, r2, 高度
torus = Part.makeTorus(10, 2)                 # 主半径, 次半径

# --- 线和边 ---
edge1 = Part.makeLine((0, 0, 0), (10, 0, 0))
edge2 = Part.makeLine((10, 0, 0), (10, 10, 0))
edge3 = Part.makeLine((10, 10, 0), (0, 0, 0))
wire = Part.Wire([edge1, edge2, edge3])

# 圆和圆弧
circle = Part.makeCircle(5)                   # 半径
arc = Part.makeCircle(5, FreeCAD.Vector(0, 0, 0),
                       FreeCAD.Vector(0, 0, 1), 0, 180)  # 开始/结束角度

# --- 面 ---
face = Part.Face(wire)                        # 从闭合线创建

# --- 从面/线创建实体 ---
extrusion = face.extrude(FreeCAD.Vector(0, 0, 10))       # 拉伸
revolved = face.revolve(FreeCAD.Vector(0, 0, 0),
                         FreeCAD.Vector(0, 0, 1), 360)    # 旋转

# --- 布尔运算 ---
fused = box.fuse(cyl)           # 并集
cut = box.cut(cyl)              # 差集
common = box.common(cyl)        # 交集
fused_clean = fused.removeSplitter()  # 清理接缝

# --- 圆角和倒角 ---
filleted = box.makeFillet(1.0, box.Edges)          # 半径, 边缘
chamfered = box.makeChamfer(1.0, box.Edges)        # 距离, 边缘

# --- 放样和扫描 ---
loft = Part.makeLoft([wire1, wire2], True)          # 线, 实体
swept = Part.Wire([path_edge]).makePipeShell([profile_wire],
                                              True, False)  # 实体, frenet

# --- B 样条曲线 ---
from FreeCAD import Vector
points = [Vector(0,0,0), Vector(1,2,0), Vector(3,1,0), Vector(4,3,0)]
bspline = Part.BSplineCurve()
bspline.interpolate(points)
edge = bspline.toShape()

# --- 在文档中显示 ---
Part.show(box, "MyBox")    # 快速显示（添加到活动文档）
# 或显式:
doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()
obj = doc.addObject("Part::Feature", "MyShape")
obj.Shape = box
doc.recompute()
```

### 拓扑探索

```python
shape = obj.Shape

# 访问子元素
shape.Vertexes    # Vertex 对象列表
shape.Edges       # Edge 对象列表
shape.Wires       # Wire 对象列表
shape.Faces       # Face 对象列表
shape.Shells      # Shell 对象列表
shape.Solids      # Solid 对象列表

# 边界框
bb = shape.BoundBox
print(bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)
print(bb.Center)

# 属性
shape.Volume
shape.Area
shape.Length       # 对于边/线
face.Surface       # 底层几何表面
edge.Curve         # 底层几何曲线

# 形状类型
shape.ShapeType    # "Solid", "Shell", "Face", "Wire", "Edge", "Vertex", "Compound"
```

### Mesh 模块

```python
import Mesh

# 从顶点和面创建网格
mesh = Mesh.Mesh()
mesh.addFacet(
    0.0, 0.0, 0.0,   # 顶点 1
    1.0, 0.0, 0.0,   # 顶点 2
    0.0, 1.0, 0.0    # 顶点 3
)

# 导入/导出
mesh = Mesh.Mesh("/path/to/file.stl")
mesh.write("/path/to/output.stl")

# 将 Part 形状转换为 Mesh
import Part
import MeshPart
shape = Part.makeBox(1, 1, 1)
mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1,
                                AngularDeflection=0.5)

# 将 Mesh 转换为 Part 形状
shape = Part.Shape()
shape.makeShapeFromMesh(mesh.Topology, 0.05)  # 容差
solid = Part.makeSolid(shape)
```

### Sketcher 模块

# 在 XY 平面上创建草图
sketch = doc.addObject("Sketcher::SketchObject", "MySketch")
sketch.Placement = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Rotation(0, 0, 0, 1)
)

# 添加几何体（返回几何体索引）
idx_line = sketch.addGeometry(Part.LineSegment(
    FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(10, 0, 0)))
idx_circle = sketch.addGeometry(Part.Circle(
    FreeCAD.Vector(5, 5, 0), FreeCAD.Vector(0, 0, 1), 3))

# 添加约束
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, 10.0))
sketch.addConstraint(Sketcher.Constraint("Radius", 1, 3.0))
sketch.addConstraint(Sketcher.Constraint("Fixed", 0, 1))
# 约束类型: Coincident, Horizontal, Vertical, Parallel, Perpendicular,
#   Tangent, Equal, Symmetric, Distance, DistanceX, DistanceY, Radius, Angle,
#   Fixed (Block), InternalAlignment

doc.recompute()
```

### Draft 模块

```python
import Draft
import FreeCAD

# 2D 形状
line = Draft.makeLine(FreeCAD.Vector(0,0,0), FreeCAD.Vector(10,0,0))
circle = Draft.makeCircle(5)
rect = Draft.makeRectangle(10, 5)
poly = Draft.makePolygon(6, radius=5)   # 六边形

# 操作
moved = Draft.move(obj, FreeCAD.Vector(10, 0, 0), copy=True)
rotated = Draft.rotate(obj, 45, FreeCAD.Vector(0,0,0),
                        axis=FreeCAD.Vector(0,0,1), copy=True)
scaled = Draft.scale(obj, FreeCAD.Vector(2,2,2), center=FreeCAD.Vector(0,0,0),
                      copy=True)
offset = Draft.offset(obj, FreeCAD.Vector(1,0,0))
array = Draft.makeArray(obj, FreeCAD.Vector(15,0,0),
                         FreeCAD.Vector(0,15,0), 3, 3)
```

## 创建参数化对象（FeaturePython）

FeaturePython 对象是具有触发重新计算的自定义参数化对象：

```python
import FreeCAD
import Part

class MyBox:
    """一个自定义参数化盒子。"""

    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLength", "Length", "尺寸",
                         "盒子长度").Length = 10.0
        obj.addProperty("App::PropertyLength", "Width", "尺寸",
                         "盒子宽度").Width = 10.0
        obj.addProperty("App::PropertyLength", "Height", "尺寸",
                         "盒子高度").Height = 10.0

    def execute(self, obj):
        """在文档重新计算时调用。"""
        obj.Shape = Part.makeBox(obj.Length, obj.Width, obj.Height)

    def onChanged(self, obj, prop):
        """当属性更改时调用。"""
        pass

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class ViewProviderMyBox:
    """自定义图标和显示设置的视图提供程序。"""

    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        return ":/icons/Part_Box.svg"

    def attach(self, vobj):
        self.Object = vobj.Object

    def updateData(self, obj, prop):
        pass

    def onChanged(self, vobj, prop):
        pass

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


# --- 使用 ---
doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("Test")
obj = doc.addObject("Part::FeaturePython", "CustomBox")
MyBox(obj)
ViewProviderMyBox(obj.ViewObject)
doc.recompute()
```

### 常见属性类型

| 属性类型 | Python 类型 | 描述 |
|---|---|---|
| `App::PropertyBool` | `bool` | 布尔值 |
| `App::PropertyInteger` | `int` | 整数 |
| `App::PropertyFloat` | `float` | 浮点数 |
| `App::PropertyString` | `str` | 字符串 |
| `App::PropertyLength` | `float` (单位) | 带单位的长度 |
| `App::PropertyAngle` | `float` (度) | 角度（度） |
| `App::PropertyVector` | `FreeCAD.Vector` | 3D 向量 |
| `App::PropertyPlacement` | `FreeCAD.Placement` | 位置 + 旋转 |
| `App::PropertyLink` | 对象引用 | 引用另一个对象 |
| `App::PropertyLinkList` | 引用列表 | 引用多个对象 |
| `App::PropertyEnumeration` | `list`/`str` | 下拉选择 |
| `App::PropertyFile` | `str` | 文件路径 |
| `App::PropertyColor` | `tuple` | RGB 颜色 (0.0-1.0) |
| `App::PropertyPythonObject` | 任意 | 可序列化的 Python 对象 |

## 创建 GUI 工具

### Gui Commands

```python
import FreeCAD
import FreeCADGui

class MyCommand:
    """一个自定义工具栏/菜单命令。"""

    def GetResources(self):
        return {
            "Pixmap": ":/icons/Part_Box.svg",
            "MenuText": "我的自定义命令",
            "ToolTip": "创建自定义盒子",
            "Accel": "Ctrl+Shift+B"
        }

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None

    def Activated(self):
        # 命令逻辑在此处
        FreeCAD.Console.PrintMessage("命令已激活\n")

FreeCADGui.addCommand("My_CustomCommand", MyCommand())
```

### PySide 对话框

```python
from PySide2 import QtWidgets, QtCore, QtGui

class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or FreeCADGui.getMainWindow())
        self.setWindowTitle("我的工具")
        self.setMinimumWidth(300)

        layout = QtWidgets.QVBoxLayout(self)

        # 输入字段
        self.label = QtWidgets.QLabel("长度:")
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setRange(0.1, 1000.0)
        self.spinbox.setValue(10.0)
        self.spinbox.setSuffix(" mm")

        form = QtWidgets.QFormLayout()
        form.addRow(self.label, self.spinbox)
        layout.addLayout(form)

        # 按钮
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_ok = QtWidgets.QPushButton("确定")
        self.btn_cancel = QtWidgets.QPushButton("取消")
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

# 使用
dialog = MyDialog()
if dialog.exec_() == QtWidgets.QDialog.Accepted:
    length = dialog.spinbox.value()
    FreeCAD.Console.PrintMessage(f"长度: {length}\n")
```

### 任务面板（推荐用于 FreeCAD 集成）

```python
class MyTaskPanel:
    """左侧边栏中显示的任务面板。"""

    def __init__(self):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setValue(10.0)
        layout.addWidget(QtWidgets.QLabel("长度:"))
        layout.addWidget(self.spinbox)

    def accept(self):
        # 当用户点击确定时调用
        length = self.spinbox.value()
        FreeCAD.Console.PrintMessage(f"接受: {length}\n")
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCADGui.Control.closeDialog()
        return True

    def getStandardButtons(self):
        return int(QtWidgets.QDialogButtonBox.Ok |
                   QtWidgets.QDialogButtonBox.Cancel)

# 显示面板
panel = MyTaskPanel()
FreeCADGui.Control.showDialog(panel)
```

## Coin3D 场景图（Pivy）

```python
from pivy import coin
import FreeCADGui

# 访问场景图根节点
sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()

# 添加一个自定义分隔符和球体
sep = coin.SoSeparator()
mat = coin.SoMaterial()
mat.diffuseColor.setValue(1.0, 0.0, 0.0)  # 红色
trans = coin.SoTranslation()
trans.translation.setValue(10, 10, 10)
sphere = coin.SoSphere()
sphere.radius.setValue(2.0)
sep.addChild(mat)
sep.addChild(trans)
sep.addChild(sphere)
sg.addChild(sep)

# 后续移除
sg.removeChild(sep)
```

## 自定义工作台创建

```python
import FreeCADGui

class MyWorkbench(FreeCADGui.Workbench):
    MenuText = "我的工作台"
    ToolTip = "一个自定义工作台"
    Icon = ":/icons/freecad.svg"

    def Initialize(self):
        """在工作台激活时调用。"""
        import MyCommands  # 导入你的命令模块
        self.appendToolbar("我的工具", ["My_CustomCommand"])
        self.appendMenu("我的菜单", ["My_CustomCommand"])

    def Activated(self):
        pass

    def Deactivated(self):
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(MyWorkbench)
```

## 宏最佳实践

```python
# 标准宏头部
# -*- coding: utf-8 -*-
# FreeCAD Macro: MyMacro
# 描述: 简要描述宏的作用
# 作者: 你的名字
# 版本: 1.0
# 日期: 2026-04-07

import FreeCAD
import Part
from FreeCAD import Base

# 检查 GUI 可用性
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide2 import QtWidgets, QtCore

def main():
    doc = FreeCAD.ActiveDocument
    if doc is None:
        FreeCAD.Console.PrintError("没有活动文档\n")
        return

    if FreeCAD.GuiUp:
        sel = FreeCADGui.Selection.getSelection()
        if not sel:
            FreeCAD.Console.PrintWarning("没有选择对象\n")

    # ... 宏逻辑 ...

    doc.recompute()
    FreeCAD.Console.PrintMessage("宏完成\n")

if __name__ == "__main__":
    main()
```

### 选择处理

```python
# 获取选中的对象
sel = FreeCADGui.Selection.getSelection()           # 对象列表
sel_ex = FreeCADGui.Selection.getSelectionEx()       # 扩展 (子元素)

for selobj in sel_ex:
    obj = selobj.Object
    for sub in selobj.SubElementNames:
        print(f"{obj.Name}.{sub}")
        shape = obj.getSubObject(sub)  # 获取子形状

# 程序化选择
FreeCADGui.Selection.addSelection(doc.MyBox)
FreeCADGui.Selection.addSelection(doc.MyBox, "Face1")
FreeCADGui.Selection.clearSelection()
```

### 控制台输出

```python
FreeCAD.Console.PrintMessage("信息消息\n")
FreeCAD.Console.PrintWarning("警告消息\n")
FreeCAD.Console.PrintError("错误消息\n")
FreeCAD.Console.PrintLog("调试/日志消息\n")
```

## 常见模式

### 从草图创建参数化垫

```python
doc = FreeCAD.ActiveDocument

# 创建草图
sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(0,0,0), FreeCAD.Vector(10,0,0))
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(10,0,0), FreeCAD.Vector(10,10,0)))
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(10,10,0), FreeCAD.Vector(0,10,0)))
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(0,10,0), FreeCAD.Vector(0,0,0)))
# 使用重合约束闭合
for i in range(3):
    sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, i+1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))

# 垫 (PartDesign)
pad = doc.addObject("PartDesign::Pad", "Pad")
pad.Profile = sketch
pad.Length = 5.0
sketch.Visibility = False
doc.recompute()
```

### 导出形状

```python
# STEP 导出
Part.export([doc.MyBox], "/path/to/output.step")

# STL 导出 (网格)
import Mesh
Mesh.export([doc.MyBox], "/path/to/output.stl")

# IGES 导出
Part.export([doc.MyBox], "/path/to/output.iges")

# 多种格式通过 importlib
import importlib
importlib.import_module("importOBJ").export([doc.MyBox], "/path/to/output.obj")
```

### 单位和数量

```python
# FreeCAD 内部使用毫米
q = FreeCAD.Units.Quantity("10 mm")
q_inch = FreeCAD.Units.Quantity("1 in")
print(q_inch.getValueAs("mm"))  # 25.4

# 解析带单位的用户输入
q = FreeCAD.Units.parseQuantity("2.5 in")
value_mm = float(q)  # 值（毫米，内部单位）
```

## 补偿规则（Quasi-Coder 集成）

在解释 FreeCAD 脚本的简写或类代码时：

1. **术语映射**: "box" → `Part.makeBox()`, "cylinder" → `Part.makeCylinder()`, "sphere" → `Part.makeSphere()`, "merge/combine/join" → `.fuse()`, "subtract/cut/remove" → `.cut()`, "intersect" → `.common()`, "round edges/fillet" → `.makeFillet()`, "bevel/chamfer" → `.makeChamfer()`
2. **隐式文档**: 如果没有提及文档处理，请用标准 `doc = FreeCAD.ActiveDocument or FreeCAD.newDocument()`
3. **单位假设**: 默认为毫米，除非另有说明
4. **重新计算**: 修改后始终调用 `doc.recompute()`
5. **GUI 保护**: 当脚本可能以无头方式运行时，将 GUI 依赖代码包装在 `if FreeCAD.GuiUp:` 中
6. **Part.show()**: 使用 `Part.show(shape, "Name")` 进行快速显示，或 `doc.addObject("Part::Feature", "Name")` 创建命名持久对象

## 参考

### 主要链接

- [编写 Python 代码](https://wiki.freecad.org/Manual:A_gentle_introduction#Writing_Python_code)
- [操作 FreeCAD 对象](https://wiki.freecad.org/Manual:A_gentle_introduction#Manipulating_FreeCAD_objects)
- [向量和放置](https://wiki.freecad.org/Manual:A_gentle_introduction#Vectors_and_Placements)
- [创建和操作几何体](https://wiki.freecad.org/Manual:Creating_and_manipulating_geometry)
- [创建参数化对象](https://wiki.freecad.org/Manual:Creating_parametric_objects)
- [创建界面工具](https://wiki.freecad.org/Manual:Creating_interface_tools)
- [Python](https://en.wikipedia.org/wiki/Python_%28programming_language%29)
- [Python 简介](https://wiki.freecad.org/Introduction_to_Python)
- [Python 脚本教程](https://wiki.freecad.org/Python_scripting_tutorial)
- [FreeCAD 脚本基础](https://wiki.freecad.org/FreeCAD_Scripting_Basics)
- [Gui Command](https://wiki.freecad.org/Gui_Command)

### 随附参考文档

参见 [参考资料/](references/) 目录中的主题组织指南：

1. [scripting-fundamentals.md](references/scripting-fundamentals.md) — 核心脚本, 文档模型, 控制台
2. [geometry-and-shapes.md](references/geometry-and-shapes.md) — Part, Mesh, Sketcher, 拓扑
3. [parametric-objects.md](references/parametric-objects.md) — FeaturePython, 属性, 脚本对象
4. [gui-and-interface.md](references/gui-and-interface.md) — PySide, 对话框, 任务面板, Coin3D
5. [workbenches-and-advanced.md](references/workbenches-and-advanced.md) — 工作台, 宏, FEM, Path, 配方
