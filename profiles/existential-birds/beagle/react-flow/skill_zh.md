# React Flow

React Flow (@xyflow/react) 是一个用于构建基于节点的图、工作流编辑器和交互式图表的库。它提供了一个高度可定制的框架，用于创建可视化编程界面、流程图和网络可视化。

## 快速入门

### 安装

```bash
pnpm add @xyflow/react
```

### 基本设置

```typescript
import { ReactFlow, Node, Edge, Background, Controls, MiniMap } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    data: { label: '输入节点' },
    position: { x: 250, y: 5 },
  },
  {
    id: '2',
    data: { label: '默认节点' },
    position: { x: 100, y: 100 },
  },
  {
    id: '3',
    type: 'output',
    data: { label: '输出节点' },
    position: { x: 400, y: 100 },
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3' },
];

function Flow() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow nodes={initialNodes} edges={initialEdges}>
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default Flow;
```

## 核心概念

### 节点

节点是图的构建块。每个节点具有：
- `id`：唯一标识符
- `type`：节点类型（内置或自定义）
- `position`：{ x, y } 坐标
- `data`：自定义数据对象

```typescript
import { Node } from '@xyflow/react';

const node: Node = {
  id: 'node-1',
  type: 'default',
  position: { x: 100, y: 100 },
  data: { label: '节点标签' },
  style: { background: '#D6D5E6' },
  className: 'custom-node',
};
```

内置节点类型：
- `default`：标准节点
- `input`：无目标连接点
- `output`：无源连接点
- `group`：其他节点的容器

### 边

边连接节点。每个边需要：
- `id`：唯一标识符
- `source`：源节点 ID
- `target`：目标节点 ID

```typescript
import { Edge } from '@xyflow/react';

const edge: Edge = {
  id: 'e1-2',
  source: '1',
  target: '2',
  type: 'smoothstep',
  animated: true,
  label: '边标签',
  style: { stroke: '#fff', strokeWidth: 2 },
};
```

内置边类型：
- `default`：贝塞尔曲线
- `straight`：直线
- `step`：正交且角尖锐
- `smoothstep`：正交且角圆润

### 连接点

连接点是节点上的连接点。使用 `Position` 枚举进行放置：

```typescript
import { Handle, Position } from '@xyflow/react';

<Handle type="target" position={Position.Top} />
<Handle type="source" position={Position.Bottom} />
```

可用位置：`Position.Top`、`Position.Right`、`Position.Bottom`、`Position.Left`

## 状态管理

### 受控流

使用状态钩子进行完全控制：

```typescript
import { useNodesState, useEdgesState, addEdge, OnConnect } from '@xyflow/react';
import { useCallback } from 'react';

function ControlledFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect: OnConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
    />
  );
}
```

### useReactFlow 钩子

访问 React Flow 实例以进行程序化控制：

```typescript
import { useReactFlow } from '@xyflow/react';

function FlowControls() {
  const {
    getNodes,
    getEdges,
    setNodes,
    setEdges,
    addNodes,
    addEdges,
    deleteElements,
    fitView,
    zoomIn,
    zoomOut,
    getNode,
    getEdge,
    updateNode,
    updateEdge,
  } = useReactFlow();

  return (
    <button onClick={() => fitView()}>适应视图</button>
  );
}
```

## 自定义节点

使用 `NodeProps<T>` 和类型化数据定义自定义节点：

```typescript
import { NodeProps, Node, Handle, Position } from '@xyflow/react';

export type CustomNode = Node<{ label: string; status: 'active' | 'inactive' }, 'custom'>;

function CustomNodeComponent({ data, selected }: NodeProps<CustomNode>) {
  return (
    <div className={`px-4 py-2 ${selected ? 'ring-2' : ''}`}>
      <Handle type="target" position={Position.Top} />
      <div className="font-bold">{data.label}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
```

使用 `nodeTypes` 注册：

```typescript
const nodeTypes: NodeTypes = { custom: CustomNodeComponent };
<ReactFlow nodeTypes={nodeTypes} />
```

### 关键模式

- **多个连接点**：使用 `id` 属性和 `style` 进行定位
- **动态连接点**：添加/移除连接点后调用 `useUpdateNodeInternals([nodeId])`
- **交互元素**：在输入/按钮上添加 `className="nodrag"` 以防止拖动

有关详细模式，包括样式、航空图钉和动态连接点，请参阅 [自定义节点参考](./references/custom-nodes.md)。

## 自定义边

使用 `EdgeProps<T>` 和路径工具定义自定义边：

```typescript
import { BaseEdge, EdgeProps, getBezierPath } from '@xyflow/react';

export type CustomEdge = Edge<{ status: 'normal' | 'error' }, 'custom'>;

function CustomEdgeComponent(props: EdgeProps<CustomEdge>) {
  const [edgePath] = getBezierPath(props);

  return (
    <BaseEdge
      id={props.id}
      path={edgePath}
      style={{ stroke: props.data?.status === 'error' ? '#ef4444' : '#64748b' }}
    />
  );
}
```

### 路径工具

- `getBezierPath()` - 平滑曲线
- `getStraightPath()` - 直线
- `getSmoothStepPath()` - 正交且角圆润
- `getSmoothStepPath({ borderRadius: 0 })` - 正交且角尖锐（步进边）

所有工具返回 `[path, labelX, labelY, offsetX, offsetY]`。

### 交互式标签

使用 `EdgeLabelRenderer` 为基于 HTML 的标签添加指针事件：

```typescript
import { EdgeLabelRenderer, BaseEdge, getBezierPath } from '@xyflow/react';

function ButtonEdge(props: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath(props);
  return (
    <>
      <BaseEdge id={props.id} path={edgePath} />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <button onClick={() => console.log('删除')}>×</button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}
```

有关动画边、时间标签和 SVG 文本模式，请参阅 [自定义边参考](./references/custom-edges.md)。

## 视图控制

使用 `useReactFlow()` 钩子进行程序化视图控制：

```typescript
import { useReactFlow } from '@xyflow/react';

function ViewportControls() {
  const { fitView, zoomIn, zoomOut, setCenter, screenToFlowPosition } = useReactFlow();

  // 适应所有节点
  const handleFitView = () => fitView({ padding: 0.2, duration: 400 });

  // 缩放控制
  const handleZoomIn = () => zoomIn({ duration: 300 });
  const handleZoomOut = () => zoomOut({ duration: 300 });

  // 居中于特定坐标
  const handleCenter = () => setCenter(250, 250, { zoom: 1.5, duration: 500 });

  // 将屏幕坐标转换为流坐标
  const addNodeAtClick = (event: React.MouseEvent) => {
    const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
    // 使用 position 添加节点
  };

  return null;
}
```

有关保存/恢复状态、受控视图和坐标转换，请参阅 [视图参考](./references/viewport.md)。

## 事件

React Flow 提供了全面的事件处理：

### 节点事件

```typescript
import { NodeMouseHandler, OnNodeDrag } from '@xyflow/react';

const onNodeClick: NodeMouseHandler = (event, node) => {
  console.log('节点被点击:', node.id);
};

const onNodeDrag: OnNodeDrag = (event, node, nodes) => {
  console.log('拖动:', node.id);
};

<ReactFlow
  onNodeClick={onNodeClick}
  onNodeDrag={onNodeDrag}
  onNodeDragStop={onNodeClick}
/>
```

### 边和连接事件

```typescript
import { EdgeMouseHandler, OnConnect } from '@xyflow/react';

const onEdgeClick: EdgeMouseHandler = (event, edge) => console.log('边:', edge.id);
const onConnect: OnConnect = (connection) => console.log('连接:', connection);

<ReactFlow onEdgeClick={onEdgeClick} onConnect={onConnect} />
```

### 选择和视图事件

```typescript
import { useOnSelectionChange, useOnViewportChange } from '@xyflow/react';

useOnSelectionChange({
  onChange: ({ nodes, edges }) => console.log('选择:', nodes.length, edges.length),
});

useOnViewportChange({
  onChange: (viewport) => console.log('视图:', viewport.zoom),
});
```

有关完整事件目录，包括验证、删除和错误处理，请参阅 [事件参考](./references/events.md)。

## 常见模式

### 防止拖动/平移

```typescript
<input className="nodrag" />
<button className="nodrag nopan">点击我</button>
```

### 连接验证

```typescript
const isValidConnection = (connection: Connection) => {
  return connection.source !== connection.target; // 防止自连接
};

<ReactFlow isValidConnection={isValidConnection} />
```

### 点击添加节点

```typescript
const { screenToFlowPosition, setNodes } = useReactFlow();

const onPaneClick = (event: React.MouseEvent) => {
  const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
  setNodes(nodes => [...nodes, { id: `node-${Date.now()}`, position, data: { label: '新' } }]);
};
```

### 更新节点数据

```typescript
const { updateNodeData } = useReactFlow();
updateNodeData('node-1', { label: '更新' });
updateNodeData('node-1', (node) => ({ ...node.data, count: node.data.count + 1 }));
```

## 提供者模式

当在流外使用 `useReactFlow()` 时，使用 `ReactFlowProvider` 包裹应用：

```typescript
import { ReactFlow, ReactFlowProvider, useReactFlow } from '@xyflow/react';

function Controls() {
  const { fitView } = useReactFlow(); // 必须在提供者内
  return <button onClick={() => fitView()}>适应视图</button>;
}

function App() {
  return (
    <ReactFlowProvider>
      <Controls />
      <ReactFlow nodes={nodes} edges={edges} />
    </ReactFlowProvider>
  );
}
```

## 实现门禁

在将集成视为完成之前，使用这些**顺序检查**（它们针对常见陷阱，而不是样式偏好）。

1. **包中的 CSS** — 确保 `import '@xyflow/react/dist/style.css'` 在应用中运行（入口或布局）。**通过**：节点和边具有预期的默认样式；连接点是可见且可交互的。
2. **稳定的 `nodeTypes` / `edgeTypes`** — 不要每次渲染都传递一个新的对象字面量；在组件外部定义映射，或使用 `useMemo` 和正确的依赖项进行记忆化。**通过**：没有重新挂载闪烁或“最大更新深度”/失控更新，当仅选择或视图更改时。
3. **提供者边界** — 调用 `useReactFlow()` 的组件必须是 `ReactFlowProvider` 的后代，并且流实际上已挂载。**通过**：没有运行时缺失上下文错误；程序化 API（`fitView` 等）按预期工作。

## 参考文件

有关详细实现模式，请参阅：

- [自定义节点](./references/custom-nodes.md) - NodeProps 类型化、Handle 组件、动态连接点、样式模式
- [自定义边](./references/custom-edges.md) - EdgeProps 类型化、路径工具、EdgeLabelRenderer、动画边
- [视图](./references/viewport.md) - useReactFlow 方法、fitView 选项、坐标转换
- [事件](./references/events.md) - 节点/边/连接事件、选择处理、视图变化
