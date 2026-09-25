## 概述

TanStack Table 是一个无头 UI 库，用于构建数据表格和 datagrids。它提供了排序、筛选、分页、分组、展开、列固定/排序/可见性/调整大小和行选择等逻辑，而无需渲染任何标记或样式。

**包:** `@tanstack/react-table`
**工具:** `@tanstack/match-sorter-utils`（模糊筛选）
**当前版本:** v8

## 安装

```bash
npm install @tanstack/react-table
```

## 核心架构

### 构建块

1. **列定义** - 描述列（数据访问、渲染、功能）
2. **表格实例** - 中央协调器，包含状态和 API
3. **行模型** - 数据处理管道（筛选 -> 排序 -> 分组 -> 分页）
4. **表头、行、单元格** - 可渲染单元

### 重要：数据和列稳定性

```typescript
// 错误 - 每次渲染都创建新引用，导致无限循环
const table = useReactTable({
  data: fetchedData.results,     // 新引用！
  columns: [{ accessorKey: 'name' }], // 新引用！
})

// 正确 - 稳定引用
const columns = useMemo(() => [...], [])
const data = useMemo(() => fetchedData?.results ?? [], [fetchedData])

const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })
```

## 列定义

### 使用 createColumnHelper（推荐）

```typescript
import { createColumnHelper } from '@tanstack/react-table'

type Person = {
  firstName: string
  lastName: string
  age: number
  status: 'active' | 'inactive'
}

const columnHelper = createColumnHelper<Person>()

const columns = [
  // 访问器列（数据列）
  columnHelper.accessor('firstName', {
    header: 'First Name',
    cell: info => info.getValue(),
    footer: info => info.column.id,
  }),

  // 带函数的访问器
  columnHelper.accessor(row => row.lastName, {
    id: 'lastName', // 使用 accessorFn 时必须
    header: () => <span>Last Name</span>,
    cell: info => <i>{info.getValue()}</i>,
  }),

  // 显示列（无数据，自定义渲染）
  columnHelper.display({
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) => (
      <button onClick={() => deleteRow(row.original)}>Delete</button>
    ),
  }),

  // 分组列（嵌套表头）
  columnHelper.group({
    id: 'info',
    header: 'Info',
    columns: [
      columnHelper.accessor('age', { header: 'Age' }),
      columnHelper.accessor('status', { header: 'Status' }),
    ],
  }),
]
```

### 列选项

| 选项 | 类型 | 描述 |
|------|------|------|
| `id` | `string` | 唯一标识符（自动从 accessorKey 派生） |
| `accessorKey` | `string` | 行数据的点标记路径 |
| `accessorFn` | `(row) => any` | 自定义访问器函数 |
| `header` | `string \| (context) => ReactNode` | 表头渲染器 |
| `cell` | `(context) => ReactNode` | 单元格渲染器 |
| `footer` | `(context) => ReactNode` | 脚部渲染器 |
| `size` | `number` | 默认宽度（默认：150） |
| `minSize` | `number` | 最小宽度（默认：20） |
| `maxSize` | `number` | 最大宽度 |
| `enableSorting` | `boolean` | 启用排序 |
| `sortingFn` | `string \| SortingFn` | 排序函数 |
| `enableFiltering` | `boolean` | 启用筛选 |
| `filterFn` | `string \| FilterFn` | 筛选函数 |
| `enableGrouping` | `boolean` | 启用分组 |
| `aggregationFn` | `string \| AggregationFn` | 聚合函数 |
| `enableHiding` | `boolean` | 启用可见性切换 |
| `enableResizing` | `boolean` | 启用调整大小 |
| `enablePinning` | `boolean` | 启用固定 |
| `meta` | `any` | 自定义元数据 |

## 表格实例

### 创建表格

```typescript
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
} from '@tanstack/react-table'

function MyTable() {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  })

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, pagination },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id} onClick={header.column.getToggleSortingHandler()}>
                {header.isPlaceholder ? null :
                  flexRender(header.column.columnDef.header, header.getContext())}
                {{ asc: ' ↑', desc: ' ↓' }[header.column.getIsSorted() as string] ?? null}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
```

## 排序

```typescript
const table = useReactTable({
  state: { sorting },
  onSortingChange: setSorting,
  getSortedRowModel: getSortedRowModel(),
  enableSorting: true,
  enableMultiSort: true,
  // manualSorting: true,  // 用于服务器端排序
})

// 内置排序函数：'alphanumeric', 'text', 'datetime', 'basic'
// 列级别：sortingFn: 'alphanumeric'
```

## 筛选

### 列筛选

```typescript
const table = useReactTable({
  state: { columnFilters },
  onColumnFiltersChange: setColumnFilters,
  getFilteredRowModel: getFilteredRowModel(),
  getFacetedRowModel: getFacetedRowModel(),
  getFacetedUniqueValues: getFacetedUniqueValues(),
  getFacetedMinMaxValues: getFacetedMinMaxValues(),
})

// 内置：'includesString', 'equalsString', 'arrIncludes', 'inNumberRange', 等。

// 筛选 UI
function Filter({ column }) {
  return (
    <input
      value={(column.getFilterValue() ?? '') as string}
      onChange={e => column.setFilterValue(e.target.value)}
      placeholder={`Filter... (${column.getFacetedUniqueValues()?.size})`}
    />
  )
}
```

### 全局筛选

```typescript
const [globalFilter, setGlobalFilter] = useState('')

const table = useReactTable({
  state: { globalFilter },
  onGlobalFilterChange: setGlobalFilter,
  globalFilterFn: 'includesString',
  getFilteredRowModel: getFilteredRowModel(),
})
```

### 模糊筛选

```typescript
import { rankItem } from '@tanstack/match-sorter-utils'

const fuzzyFilter: FilterFn<any> = (row, columnId, value, addMeta) => {
  const itemRank = rankItem(row.getValue(columnId), value)
  addMeta({ itemRank })
  return itemRank.passed
}

const table = useReactTable({
  filterFns: { fuzzy: fuzzyFilter },
  globalFilterFn: 'fuzzy',
})
```

## 分页

```typescript
const table = useReactTable({
  state: { pagination },
  onPaginationChange: setPagination,
  getPaginationRowModel: getPaginationRowModel(),
  // 对于服务器端：
  // manualPagination: true,
  // pageCount: serverPageCount,
})

// 导航
table.nextPage()
table.previousPage()
table.firstPage()
table.lastPage()
table.setPageSize(20)
table.getCanNextPage()     // boolean
table.getCanPreviousPage() // boolean
table.getPageCount()       // 总页数
```

## 行选择

```typescript
const [rowSelection, setRowSelection] = useState<RowSelectionState>({})

const table = useReactTable({
  state: { rowSelection },
  onRowSelectionChange: setRowSelection,
  enableRowSelection: true,
  enableMultiRowSelection: true,
})

// 复选框列
columnHelper.display({
  id: 'select',
  header: ({ table }) => (
    <input
      type="checkbox"
      checked={table.getIsAllRowsSelected()}
      onChange={table.getToggleAllRowsSelectedHandler()}
    />
  ),
  cell: ({ row }) => (
    <input
      type="checkbox"
      checked={row.getIsSelected()}
      disabled={!row.getCanSelect()}
      onChange={row.getToggleSelectedHandler()}
    />
  ),
})

// 获取选中的行
table.getSelectedRowModel().rows
```

## 列可见性

```typescript
const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})

const table = useReactTable({
  state: { columnVisibility },
  onColumnVisibilityChange: setColumnVisibility,
})

// 切换 UI
{table.getAllLeafColumns().map(column => (
  <label key={column.id}>
    <input
      type="checkbox"
      checked={column.getIsVisible()}
      onChange={column.getToggleVisibilityHandler()}
    />
    {column.id}
  </label>
))}
```

## 列固定

```typescript
const [columnPinning, setColumnPinning] = useState<ColumnPinningState>({
  left: ['select', 'name'],
  right: ['actions'],
})

const table = useReactTable({
  state: { columnPinning },
  onColumnPinningChange: setColumnPinning,
  enableColumnPinning: true,
})

// 分别渲染固定部分
row.getLeftVisibleCells()   // 左固定
row.getCenterVisibleCells() // 未固定
row.getRightVisibleCells()  // 右固定
```

## 列调整大小

```typescript
const table = useReactTable({
  enableColumnResizing: true,
  columnResizeMode: 'onChange', // 'onChange' | 'onEnd'
  defaultColumn: { size: 150, minSize: 50, maxSize: 500 },
})

// 头部中的调整大小手柄
<div
  onMouseDown={header.getResizeHandler()}
  onTouchStart={header.getResizeHandler()}
  className={`resizer ${header.column.getIsResizing() ? 'isResizing' : ''}`}
/>
```

## 分组与聚合

```typescript
const [grouping, setGrouping] = useState<GroupingState>([])

const table = useReactTable({
  state: { grouping },
  onGroupingChange: setGrouping,
  getGroupedRowModel: getGroupedRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
})

// 内置聚合：'sum', 'min', 'max', 'mean', 'median', 'count', 'unique', 'uniqueCount'
columnHelper.accessor('amount', {
  aggregationFn: 'sum',
  aggregatedCell: ({ getValue }) => `Total: ${getValue()}`,
})
```

## 行展开

```typescript
const [expanded, setExpanded] = useState<ExpandedState>({})

const table = useReactTable({
  state: { expanded },
  onExpandedChange: setExpanded,
  getExpandedRowModel: getExpandedRowModel(),
  getSubRows: (row) => row.subRows, // 用于层次化数据
})

// 展开切换
<button onClick={row.getToggleExpandedHandler()}>
  {row.getIsExpanded() ? '−' : '+'}
</button>

// 详情行模式
{row.getIsExpanded() && (
  <tr>
    <td colSpan={columns.length}>
      <DetailComponent data={row.original} />
    </td>
  </tr>
)}
```

## 虚拟化集成

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualizedTable() {
  const table = useReactTable({ /* ... */ })
  const { rows } = table.getRowModel()
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35,
    overscan: 10,
  })

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <table>
        <tbody style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
          {virtualizer.getVirtualItems().map(virtualRow => {
            const row = rows[virtualRow.index]
            return (
              <tr
                key={row.id}
                style={{
                  position: 'absolute',
                  transform: `translateY(${virtualRow.start}px)`,
                  height: `${virtualRow.size}px`,
                }}
              >
                {row.getVisibleCells().map(cell => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
```

## 服务器端操作

```typescript
const table = useReactTable({
  data: serverData,
  columns,
  manualSorting: true,
  manualFiltering: true,
  manualPagination: true,
  pageCount: serverPageCount,
  state: { sorting, columnFilters, pagination },
  onSortingChange: setSorting,
  onColumnFiltersChange: setColumnFilters,
  onPaginationChange: setPagination,
  getCoreRowModel: getCoreRowModel(),
  // 不要包含 getSortedRowModel, getFilteredRowModel, getPaginationRowModel
})

// 基于状态获取数据
useEffect(() => {
  fetchData({ sorting, filters: columnFilters, pagination })
}, [sorting, columnFilters, pagination])
```

## TypeScript 模式

### 扩展列元数据

```typescript
declare module '@tanstack/react-table' {
  interface ColumnMeta<TData extends RowData, TValue> {
    filterVariant?: 'text' | 'range' | 'select'
    align?: 'left' | 'center' | 'right'
  }
}
```

### 自定义筛选/排序函数注册

```typescript
declare module '@tanstack/react-table' {
  interface FilterFns {
    fuzzy: FilterFn<unknown>
  }
  interface SortingFns {
    myCustomSort: SortingFn<unknown>
  }
}
```

### 通过表格元数据编辑单元格

```typescript
declare module '@tanstack/react-table' {
  interface TableMeta<TData extends RowData> {
    updateData: (rowIndex: number, columnId: string, value: unknown) => void
  }
}

const table = useReactTable({
  meta: {
    updateData: (rowIndex, columnId, value) => {
      setData(old => old.map((row, i) =>
        i === rowIndex ? { ...row, [columnId]: value } : row
      ))
    },
  },
})
```

## 关键导入

```typescript
import {
  createColumnHelper, flexRender, useReactTable,
  getCoreRowModel, getSortedRowModel, getFilteredRowModel,
  getPaginationRowModel, getGroupedRowModel, getExpandedRowModel,
  getFacetedRowModel, getFacetedUniqueValues, getFacetedMinMaxValues,
} from '@tanstack/react-table'

import type {
  ColumnDef, SortingState, ColumnFiltersState, VisibilityState,
  PaginationState, ExpandedState, RowSelectionState, GroupingState,
  ColumnOrderState, ColumnPinningState, FilterFn, SortingFn,
} from '@tanstack/react-table'
```

## 最佳实践

1. **始终 memoize `data` 和 `columns`** 以防止无限重新渲染
2. **使用 `flexRender`** 进行所有表头/单元格/脚部渲染
3. **使用 `table.getRowModel().rows`** 获取最终渲染的行（而不是 getCoreRowModel）
4. **仅导入需要的行模型** - 每个都会向管道添加处理
5. **使用 `getRowId`** 在数据具有唯一 ID 时获取稳定的行键
6. **使用 `manualX` 选项** 进行服务器端操作
7. **将受控状态与 `state.X` 和 `onXChange` 都配对**
8. **使用模块增强** 进行自定义元数据、筛选函数、排序函数
9. **使用列助手** 进行类型安全的列定义
10. **设置 `autoResetPageIndex: true`** 当筛选应重置分页时

## 常见陷阱

- 内联定义列（每次渲染创建新引用）
- 忘记 `getCoreRowModel()`（所有表格都需要）
- 未导入行模型使用行模型
- 使用 `accessorFn` 时未提供 `id`
- 混合 `manualPagination` 与客户端 `getPaginationRowModel`
- 忘记分组表头的 `colSpan`
- 未处理 `header.isPlaceholder` 用于分组列占位符
