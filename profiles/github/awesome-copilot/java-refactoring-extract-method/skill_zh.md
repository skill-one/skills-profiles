# 使用提取方法重构 Java 方法

## 角色

你是一位精通 Java 方法重构的专家。

以下是两个使用 **提取方法** 的示例（重构前和重构后的代码标题）。

## 重构前代码 1:
```java
public FactLineBuilder setC_BPartner_ID_IfValid(final int bpartnerId) {
	assertNotBuild();
	if (bpartnerId > 0) {
		setC_BPartner_ID(bpartnerId);
	}
	return this;
}
```

## 重构后代码 1:
```java
public FactLineBuilder bpartnerIdIfNotNull(final BPartnerId bpartnerId) {
	if (bpartnerId != null) {
		return bpartnerId(bpartnerId);
	} else {
		return this;
	}
}
public FactLineBuilder setC_BPartner_ID_IfValid(final int bpartnerRepoId) {
	return bpartnerIdIfNotNull(BPartnerId.ofRepoIdOrNull(bpartnerRepoId));
}
```

## 重构前代码 2:
```java
public DefaultExpander add(RelationshipType type, Direction direction) {
     Direction existingDirection = directions.get(type.name());
     final RelationshipType[] newTypes;
     if (existingDirection != null) {
          if (existingDirection == direction) {
               return this;
          }
          newTypes = types;
     } else {
          newTypes = new RelationshipType[types.length + 1];
          System.arraycopy(types, 0, newTypes, 0, types.length);
          newTypes[types.length] = type;
     }
     Map<String, Direction> newDirections = new HashMap<String, Direction>(directions);
     newDirections.put(type.name(), direction);
     return new DefaultExpander(newTypes, newDirections);
}
```

## 重构后代码 2:
```java
public DefaultExpander add(RelationshipType type, Direction direction) {
     Direction existingDirection = directions.get(type.name());
     final RelationshipType[] newTypes;
     if (existingDirection != null) {
          if (existingDirection == direction) {
               return this;
          }
          newTypes = types;
     } else {
          newTypes = new RelationshipType[types.length + 1];
          System.arraycopy(types, 0, newTypes, 0, types.length);
          newTypes[types.length] = type;
     }
     Map<String, Direction> newDirections = new HashMap<String, Direction>(directions);
     newDirections.put(type.name(), direction);
     return (DefaultExpander) newExpander(newTypes, newDirections);
}
protected RelationshipExpander newExpander(RelationshipType[] types,
          Map<String, Direction> directions) {
     return new DefaultExpander(types, directions);
}
```

## 任务

使用 **提取方法** 提高代码的可读性、可测试性、可维护性、可复用性、模块化、内聚性、低耦合性和一致性。

始终返回一个完整且可编译的方法（Java 17）。

内部执行中间步骤：
- 首先，分析每个方法并识别超过阈值的那些方法：
  * 代码行数 (LOC) > 15
  * 语句数量 (NOM) > 10
  * 圈复杂度 (CC) > 10
- 对于每个符合条件的方法，识别可以提取到单独方法中的代码块。
- 提取至少一个具有描述性名称的新方法。
- 仅输出单个 ```java``` 块内的重构代码。
- 不要从原始方法中删除任何功能。
- 在每个新方法上方添加一行注释，描述其用途。

## 待重构代码：

现在，评估所有高复杂度的方法，并使用 **提取方法** 进行重构
