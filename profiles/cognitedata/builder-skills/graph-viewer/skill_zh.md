# 图形查看器

## 使用场景

当用户希望在 Flows 应用程序中嵌入交互式 CDF 数据模型图形时使用此功能——节点、直接关系、边和反向关系。

**不要**使用此功能来创建静态图表、纯数据流可视化或非 CDF 图形。

## 前置条件

- 应用程序被包裹在 `@cognite/dune` 的 `<DuneProvider>` 中，因此 `useDune()` 返回一个经过身份验证的 SDK。
- 目标数据模型存在于 CDF 中，并且您知道其 `space`、`externalId` 和 `version`。
- 应用程序使用 React 18+ 和 TypeScript。

## 集成流程

按顺序执行以下步骤。应遵循目标存储库的约定，而不是自行发明新的约定。

1. **检查目标应用程序。** 阅读 `package.json` 并查看现有的文件夹结构（例如 `src/features/*`、`src/components/*`、路径别名如 `@/*`）。
2. **使用应用程序的包管理器（`npm`、`pnpm`、`yarn`、…）安装缺失的依赖项。** 有关目的和建议版本，请参阅下表中的 [依赖项](#dependencies) 表。重用应用程序已固定版本的 React，而不是升级它，并优先使用存储库已固定的任何版本，而不是这里建议的版本。
3. **将捆绑包复制到应用程序中。** 将 `skills/graph-viewer/code/` 中的每个文件复制到应用程序本地的功能文件夹中，例如：

   ```text
   src/features/graph-viewer/
   ```

   如果存储库已经具有不同的功能/组件布局或别名，请镜像它。
4. **从本地文件夹导入**，永远不要从 `@skills/...` 导入。使用典型的 `@/*` 别名：

   ```tsx
   import { useGraphViewer } from "@/features/graph-viewer";
   ```
5. **在具有明确尺寸的容器内渲染 `GraphCanvas`**（高度是必需的——请参阅下面的最小示例）。
6. **运行类型检查和构建** (`tsc --noEmit`、`npm run build` 等）并修复由复制引入的任何路径或类型问题。

## 最小示例

```tsx
import { useGraphViewer } from "@/features/graph-viewer";

export function GraphPanel() {
  const { GraphCanvas, isLoading, error } = useGraphViewer({
    dataModel: { space: "my-space", externalId: "my-data-model", version: "1" },
    instance: { space: "my-instance-space", externalId: "pump-001" },
  });

  if (isLoading) return <div>Loading graph…</div>;
  if (error) return <div>Error: {error}</div>;

  return <GraphCanvas className="h-[600px] w-full" />;
}
```

## 依赖项

建议的版本反映了编写本文时最新发布的版本。它们是起点——如果目标应用程序已经固定了不同的版本，请遵循应用程序。

| 包名          | 建议版本     | 目的                                        |
| ------------- | ------------ | ---------------------------------------------- |
| `react`       | `^18.2.0`    | UI 框架（同伴；重用应用程序的版本）   |
| `@cognite/sdk` | `^10.10.0`   | CDF API 客户端（实例、数据模型）        |
| `@cognite/dune` | `^2.1.0`     | 通过 `useDune()` 提供经过身份验证的 SDK |
| `reagraph`    | `^4.30.8`    | WebGL 图形渲染引擎                   |
| `lucide-react` | `^1.14.0`    | 节点类型图例使用的图标集          |

示例安装（npm；根据应用程序的包管理器进行调整）：

```bash
npm install @cognite/sdk@^10.10.0 @cognite/dune@^2.1.0 reagraph@^4.30.8 lucide-react@^1.14.0
```

## CDF 成本与性能

图形扩展可能会发出许多 CDF 请求，尤其是在使用反向关系时。对于大型或不熟悉的数据模型，请谨慎：

- 将 `whitelistedRelationProps` 设置为应用程序实际需要遍历的几个属性。
- 降低 `initialConnectionLimit`（它是每次扩展获取连接的**硬最大值**）。
- 降低 `maxNodes` 以限制内存中的 LRU 缓冲区。
- 仅对应用程序必须显示的关系声明 `coreReverseQueries`；每个条目都会在每次扩展时增加一个额外的查询。

`coreReverseQueries` 中的元组是**版本感知的**：
`[space, viewExternalId, viewVersion, propertyName, isList]`。

## 高级参考

有关完整配置表、返回值文档、布局、主题和更丰富的示例，请阅读 `code/README.md`。

有关实现细节，请检查 `code/` 下方的源文件。

## 验证检查清单

- [ ] 应用程序被包裹在 `<DuneProvider>` 中。
- [ ] 从 `skills/graph-viewer/code/` 复制了所有文件到应用程序本地的文件夹。
- [ ] 导入指向应用程序本地的文件夹（例如 `@/features/graph-viewer`），而不是 `@skills/...`。
- [ ] `@cognite/dune`、`@cognite/sdk`、`reagraph` 和 `lucide-react` 存在于 `package.json` 中。
- [ ] 渲染 `<GraphCanvas>` 的容器具有明确的高度。
- [ ] `tsc --noEmit` 和应用程序的构建都通过。
- [ ] 未引入对 `dune-industrial-components` 的引用。
