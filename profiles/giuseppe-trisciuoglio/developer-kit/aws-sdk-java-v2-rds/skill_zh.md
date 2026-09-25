# AWS SDK for Java v2 - RDS 管理

## 概述

本指南提供了使用 AWS SDK for Java 2.x 操作 Amazon RDS（关系数据库服务）的全面指导，涵盖数据库实例管理、快照、参数组以及 RDS 操作。

## 使用场景

- 创建、修改或删除 RDS 数据库实例
- 管理 DB 快照、参数组和配置
- 设置 Multi-AZ 部署和自动备份
- 将 Lambda 函数连接到 RDS 数据库
- 监控实例状态和性能

## 操作步骤

按照以下步骤使用 Amazon RDS：

1. **添加依赖项** - 包含 AWS RDS SDK 依赖项和数据库驱动程序
2. **创建 RDS 客户端** - 使用正确的区域和凭证实例化 RdsClient
3. **创建数据库实例** - 使用 createDBInstance() 并配置适当参数
4. **配置安全设置** - 设置 VPC 安全组和加密
5. **设置备份** - 配置自动备份窗口和保留期
6. **监控状态** - 使用 describeDBInstances() 检查实例状态
7. **创建快照** - 在进行重大更改前手动创建快照
8. **处理故障转移** - 配置 Multi-AZ 以实现高可用性

## 入门指南

### RDS 客户端设置

`RdsClient` 是与 Amazon RDS 交互的主要入口点。

**基本客户端创建：**
```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.rds.RdsClient;

RdsClient rdsClient = RdsClient.builder()
    .region(Region.US_EAST_1)
    .build();

// 使用客户端
describeInstances(rdsClient);

// 始终关闭客户端
rdsClient.close();
```

**自定义配置的客户端：**
```java
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;

RdsClient rdsClient = RdsClient.builder()
    .region(Region.US_WEST_2)
    .credentialsProvider(ProfileCredentialsProvider.create("myprofile"))
    .httpClient(ApacheHttpClient.builder()
        .connectionTimeout(Duration.ofSeconds(30))
        .socketTimeout(Duration.ofSeconds(60))
        .build())
    .build();
```

### 描述数据库实例

```java
DescribeDbInstancesResponse response = rdsClient.describeDBInstances();
for (DBInstance instance : response.dbInstances()) {
    System.out.println(instance.dbInstanceArn() + " - " + instance.dbInstanceStatus());
}
```

## 关键操作

### 创建数据库实例

```java
CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
    .dbInstanceIdentifier(dbInstanceIdentifier)
    .dbName(dbName)
    .engine("postgres")
    .engineVersion("15.4")
    .dbInstanceClass("db.t3.micro")
    .allocatedStorage(20)
    .masterUsername(masterUsername)
    .masterUserPassword(masterPassword)
    .publiclyAccessible(false)
    .build();

CreateDbInstanceResponse response = rdsClient.createDBInstance(request);

// 验证点：等待实例可用
rdsClient.waiter().waitUntilDBInstanceAvailable(
    DescribeDbInstancesRequest.builder().dbInstanceIdentifier(dbInstanceIdentifier).build()
);
System.out.println("Instance " + dbInstanceIdentifier + " is available!");
```

### 管理 DB 参数组

```java
CreateDbParameterGroupRequest request = CreateDbParameterGroupRequest.builder()
    .dbParameterGroupName(groupName)
    .dbParameterGroupFamily("postgres15")
    .description(description)
    .build();
rdsClient.createDBParameterGroup(request);
```

### 管理 DB 快照

```java
CreateDbSnapshotRequest request = CreateDbSnapshotRequest.builder()
    .dbInstanceIdentifier(dbInstanceIdentifier)
    .dbSnapshotIdentifier(snapshotIdentifier)
    .build();
CreateDbSnapshotResponse response = rdsClient.createDBSnapshot(request);
```

## 集成模式

### Spring Boot 集成

参考 [references/spring-boot-integration.md](references/spring-boot-integration.md) 获取完整的 Spring Boot 集成示例，包括：

- 使用 application properties 的 Spring Boot 配置
- RDS 客户端 Bean 配置
- 服务层实现
- REST 控制器设计
- 异常处理
- 测试策略

### Lambda 集成

参考 [references/lambda-integration.md](references/lambda-integration.md) 获取 Lambda 集成示例，包括：

- 传统 Lambda + RDS 连接
- 使用连接池的 Lambda
- 使用 AWS Secrets Manager 存储凭证
- 使用 AWS SDK for RDS 管理的 Lambda
- 安全配置和最佳实践

## 高级操作

### 修改数据库实例

```java
ModifyDbInstanceRequest request = ModifyDbInstanceRequest.builder()
    .dbInstanceIdentifier(dbInstanceIdentifier)
    .dbInstanceClass(newInstanceClass)
    .applyImmediately(false)
    .build();
rdsClient.modifyDBInstance(request);
```

### 删除数据库实例

```java
// 验证点：验证实例存在并检查状态
DBInstance instance = rdsClient.describeDBInstances(
    DescribeDbInstancesRequest.builder().dbInstanceIdentifier(dbInstanceIdentifier).build()
).dbInstances().get(0);

if ("available".equals(instance.dbInstanceStatus())) {
    DeleteDbInstanceRequest request = DeleteDbInstanceRequest.builder()
        .dbInstanceIdentifier(dbInstanceIdentifier)
        .skipFinalSnapshot(false)
        .finalDBSnapshotIdentifier(snapshotId)
        .build();
    rdsClient.deleteDBInstance(request);
}
```

## 示例

### 带验证的完整 RDS 实例创建

```java
public String createSecurePostgreSQLInstance(RdsClient rdsClient,
                                            String instanceIdentifier,
                                            String dbName,
                                            String masterUsername,
                                            String masterPassword,
                                            String vpcSecurityGroupId) {
    // 创建带安全设置的实例
    CreateDbInstanceRequest request = CreateDbInstanceRequest.builder()
        .dbInstanceIdentifier(instanceIdentifier)
        .dbName(dbName)
        .masterUsername(masterUsername)
        .masterUserPassword(masterPassword)
        .engine("postgres")
        .engineVersion("15.4")
        .dbInstanceClass("db.t3.micro")
        .allocatedStorage(20)
        .storageEncrypted(true)
        .vpcSecurityGroupIds(vpcSecurityGroupId)
        .publiclyAccessible(false)
        .multiAZ(true)
        .backupRetentionPeriod(7)
        .deletionProtection(true)
        .build();

    rdsClient.createDBInstance(request);

    // 验证：等待实例可用
    rdsClient.waiter().waitUntilDBInstanceAvailable(
        DescribeDbInstancesRequest.builder().dbInstanceIdentifier(instanceIdentifier).build()
    );
    System.out.println("Instance " + instanceIdentifier + " is available!");
    return instanceIdentifier;
}
```

## 最佳实践

**安全**：启用加密（`storageEncrypted=true`），使用 VPC 安全组，禁用公共访问。

**高可用性**：为生产工作负载启用 Multi-AZ。

**备份**：配置自动备份，保留期 7 天以上。

**删除保护**：为生产数据库启用 `deletionProtection(true)`。

**资源管理**：始终使用 try-with-resources 关闭客户端：
```java
try (RdsClient rdsClient = RdsClient.builder().region(Region.US_EAST_1).build()) {
    // 使用客户端
}
```

## 依赖项

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>rds</artifactId>
    <version>2.20.0</version>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.6.0</version>
</dependency>
```

## 参考文档

有关详细 API 参考，请参阅：
- [API 参考](references/api-reference.md) - 完整 API 文档和数据模型
- [Spring Boot 集成](references/spring-boot-integration.md) - Spring Boot 模式和示例
- [Lambda 集成](references/lambda-integration.md) - Lambda 函数模式和最佳实践

## 错误处理

有关全面的错误处理模式，包括常见异常、错误响应结构和分页支持，请参阅 [API 参考](references/api-reference.md#error-handling)。

## 限制和警告

- **实例限制**：每个区域的数据库实例账户限制
- **Multi-AZ 成本**：计算成本大约翻倍
- **快照成本**：手动快照按使用的存储量计费
- **删除保护**：无法删除已启用保护的实例
- **维护窗口**：更新期间实例可能不可用
