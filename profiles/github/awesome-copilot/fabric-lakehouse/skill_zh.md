# 何时使用此技能

当您需要时使用此技能：
- 生成包含 Fabric Lakehouse 定义及其能力的文档或说明。
- 使用最佳实践设计、构建和优化 Lakehouse 解决方案。
- 了解 Microsoft Fabric 中 Lakehouse 的核心概念和组件。
- 学习如何在 Lakehouse 中管理表格和非表格数据。

# Fabric Lakehouse

## 核心概念

### 什么是 Lakehouse？

Microsoft Fabric 中的 Lakehouse 是一个为用户提供存储表格数据（如表）和非表格数据（如文件）的地方。它结合了数据湖的灵活性以及数据仓库的管理能力。它提供：

- **统一存储**：在 OneLake 中存储结构化和非结构化数据
- **Delta Lake 格式**：支持 ACID 事务、版本控制和时间旅行
- **SQL 分析端点**：用于 T-SQL 查询
- **语义模型**：用于 Power BI 集成
- 支持其他表格格式，如 CSV、Parquet
- 支持任何文件格式
- 表格优化和数据管理工具

### 关键组件

- **Delta 表**：具有 ACID 合规性和模式强制管理的表格
- **文件**：存储在 Files 部分的非结构化/半结构化数据
- **SQL 端点**：自动生成的只读 SQL 接口，用于查询
- **快捷方式**：指向外部/内部数据的虚拟链接，无需复制
- **Fabric 物化视图**：预计算表格，用于快速查询性能

### Lakehouse 中的表格数据

表格数据以表格形式存储在 "Tables" 文件夹下。Lakehouse 中表格的主要格式为 Delta。Lakehouse 可以存储 CSV 或 Parquet 等其他格式的表格数据，这些格式仅适用于 Spark 查询。
表格可以是内部的，当数据存储在 "Tables" 文件夹下；也可以是外部的，当仅存储指向表格的引用，而数据本身存储在引用位置。表格通过快捷方式引用，快捷方式可以是内部的（指向 Fabric 中的另一个位置）或外部的（指向 Fabric 外部存储的数据）。

### Lakehouse 中表格的模式

创建 Lakehouse 时，用户可以选择启用模式。模式用于组织 Lakehouse 表格。模式作为 "Tables" 文件夹下的文件夹实现，并存储在这些文件夹中的表格。默认模式为 "dbo"，它不能被删除或重命名。所有其他模式都是可选的，可以创建、重命名或删除。用户可以使用模式快捷方式引用位于另一个 Lakehouse 中的模式，从而使用单个快捷方式引用目标模式中的所有表格。

### Lakehouse 中的文件

文件存储在 "Files" 文件夹下。用户可以创建文件夹和子文件夹来组织文件。Lakehouse 中可以存储任何文件格式。

### Fabric 物化视图

一组根据计划自动更新的预计算表格。它们为复杂的聚合和连接提供快速查询性能。物化视图使用 PySpark 或 Spark SQL 定义，并存储在关联的 Notebook 中。

### Spark 视图

由 SQL 查询定义的逻辑表格。它们不存储数据，但提供查询的虚拟层。视图使用 Spark SQL 定义，并存储在 Lakehouse 中，与表格相邻。

## 安全

### 项目访问或控制平面安全

用户可以拥有工作区角色（管理员、成员、贡献者、查看者），这些角色提供不同级别的访问权限，用于 Lakehouse 及其内容。用户还可以使用 Lakehouse 的共享功能获取访问权限。

### 数据访问或 OneLake 安全

使用 OneLake 安全模型进行数据访问，该模型基于 Microsoft Entra ID（以前称为 Azure Active Directory）和基于角色的访问控制（RBAC）。Lakehouse 数据存储在 OneLake 中，因此数据访问通过 OneLake 权限控制。除了对象级权限外，Lakehouse 还支持表格的列级和行级安全，允许对谁可以看到表格中的特定列或行进行细粒度控制。

## Lakehouse 快捷方式

快捷方式创建指向数据的虚拟链接，无需复制：

### 快捷方式类型

- **内部**：指向其他 Fabric Lakehouse/表格，跨工作区数据共享
- **ADLS Gen2**：指向 Azure 中的 ADLS Gen2 容器
- **Amazon S3**：AWS S3 存储桶，跨云数据访问
- **Dataverse**：Microsoft Dataverse，业务应用数据
- **Google Cloud Storage**：GCS 存储桶，跨云数据访问

## 性能优化

### V-Order 优化

启用语义模型时，为 Delta 表启用 V-Order 优化，以更快地读取数据。这按方式预排序数据，从而提高常见访问模式的查询性能。

### 表格优化

表格也可以使用 OPTIMIZE 命令进行优化，该命令将小文件合并为大文件，还可以对特定列应用 Z-ordering 以提高查询性能。定期优化有助于随着时间的推移维护性能。可以使用 Vacuum 命令清理旧文件并释放存储空间，尤其是在更新和删除之后。

## 血缘关系

Lakehouse 项目支持血缘关系，允许用户跟踪数据的来源和转换。Lakehouse 中的表格和文件会自动捕获血缘信息，显示数据如何从源流向目的地。这有助于调试、审计和理解数据依赖关系。

## PySpark 代码示例

请参阅 [PySpark 代码](references/pyspark.md) 了解详细信息。

## 将数据导入 Lakehouse

请参阅 [获取数据](references/getdata.md) 了解详细信息。
