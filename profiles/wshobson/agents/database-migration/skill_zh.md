# 数据库迁移

掌握跨ORM（Sequelize、TypeORM、Prisma）的数据库模式和数据迁移，包括回滚策略和零停机部署。

## 何时使用这项技能

- 在不同ORM之间迁移
- 执行模式转换
- 在数据库之间移动数据
- 实施回滚程序
- 零停机部署
- 数据库版本升级
- 数据模型重构

## ORM迁移

### Sequelize迁移

```javascript
// migrations/20231201-create-users.js
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable("users", {
      id: {
        type: Sequelize.INTEGER,
        primaryKey: true,
        autoIncrement: true,
      },
      email: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: false,
      },
      createdAt: Sequelize.DATE,
      updatedAt: Sequelize.DATE,
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable("users");
  },
};

// 运行: npx sequelize-cli db:migrate
// 回滚: npx sequelize-cli db:migrate:undo
```

### TypeORM迁移

```typescript
// migrations/1701234567-CreateUsers.ts
import { MigrationInterface, QueryRunner, Table } from "typeorm";

export class CreateUsers1701234567 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.createTable(
      new Table({
        name: "users",
        columns: [
          {
            name: "id",
            type: "int",
            isPrimary: true,
            isGenerated: true,
            generationStrategy: "increment",
          },
          {
            name: "email",
            type: "varchar",
            isUnique: true,
          },
          {
            name: "created_at",
            type: "timestamp",
            default: "CURRENT_TIMESTAMP",
          },
        ],
      }),
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.dropTable("users");
  }
}

// 运行: npm run typeorm migration:run
// 回滚: npm run typeorm migration:revert
```

### Prisma迁移

```prisma
// schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  createdAt DateTime @default(now())
}

// 生成迁移: npx prisma migrate dev --name create_users
// 应用: npx prisma migrate deploy
```

## 模式转换

### 添加带默认值的列

```javascript
// 安全迁移: 添加带默认值的列
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn("users", "status", {
      type: Sequelize.STRING,
      defaultValue: "active",
      allowNull: false,
    });
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn("users", "status");
  },
};
```

### 列重命名（零停机）

```javascript
// 第一步: 添加新列
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn("users", "full_name", {
      type: Sequelize.STRING,
    });

    // 从旧列复制数据
    await queryInterface.sequelize.query("UPDATE users SET full_name = name");
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn("users", "full_name");
  },
};

// 第二步: 更新应用程序以使用新列

// 第三步: 移除旧列
module.exports = {
  up: async (queryInterface) => {
    await queryInterface.removeColumn("users", "name");
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn("users", "name", {
      type: Sequelize.STRING,
    });
  },
};
```

### 列类型变更

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 对于大表，使用多步骤方法

    // 1. 添加新列
    await queryInterface.addColumn("users", "age_new", {
      type: Sequelize.INTEGER,
    });

    // 2. 复制并转换数据
    await queryInterface.sequelize.query(`
      UPDATE users
      SET age_new = CAST(age AS INTEGER)
      WHERE age IS NOT NULL
    `);

    // 3. 移除旧列
    await queryInterface.removeColumn("users", "age");

    // 4. 重命名新列
    await queryInterface.renameColumn("users", "age_new", "age");
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.changeColumn("users", "age", {
      type: Sequelize.STRING,
    });
  },
};
```

## 数据转换

### 复杂数据迁移

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 获取所有记录
    const [users] = await queryInterface.sequelize.query(
      "SELECT id, address_string FROM users",
    );

    // 转换每条记录
    for (const user of users) {
      const addressParts = user.address_string.split(",");

      await queryInterface.sequelize.query(
        `UPDATE users
         SET street = :street,
             city = :city,
             state = :state
         WHERE id = :id`,
        {
          replacements: {
            id: user.id,
            street: addressParts[0]?.trim(),
            city: addressParts[1]?.trim(),
            state: addressParts[2]?.trim(),
          },
        },
      );
    }

    // 移除旧列
    await queryInterface.removeColumn("users", "address_string");
  },

  down: async (queryInterface, Sequelize) => {
    // 重建原始列
    await queryInterface.addColumn("users", "address_string", {
      type: Sequelize.STRING,
    });

    await queryInterface.sequelize.query(`
      UPDATE users
      SET address_string = CONCAT(street, ', ', city, ', ', state)
    `);

    await queryInterface.removeColumn("users", "street");
    await queryInterface.removeColumn("users", "city");
    await queryInterface.removeColumn("users", "state");
  },
};
```

## 回滚策略

### 基于事务的迁移

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      await queryInterface.addColumn(
        "users",
        "verified",
        { type: Sequelize.BOOLEAN, defaultValue: false },
        { transaction },
      );

      await queryInterface.sequelize.query(
        "UPDATE users SET verified = true WHERE email_verified_at IS NOT NULL",
        { transaction },
      );

      await transaction.commit();
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn("users", "verified");
  },
};
```

### 基于检查点的回滚

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 创建备份表
    await queryInterface.sequelize.query(
      "CREATE TABLE users_backup AS SELECT * FROM users",
    );

    try {
      // 执行迁移
      await queryInterface.addColumn("users", "new_field", {
        type: Sequelize.STRING,
      });

      // 验证迁移
      const [result] = await queryInterface.sequelize.query(
        "SELECT COUNT(*) as count FROM users WHERE new_field IS NULL",
      );

      if (result[0].count > 0) {
        throw new Error("Migration verification failed");
      }

      // 移除备份
      await queryInterface.dropTable("users_backup");
    } catch (error) {
      // 从备份恢复
      await queryInterface.sequelize.query("DROP TABLE users");
      await queryInterface.sequelize.query(
        "CREATE TABLE users AS SELECT * FROM users_backup",
      );
      await queryInterface.dropTable("users_backup");
      throw error;
    }
  },
};
```

## 其他模式和模板

更详细的模板和实例说明位于 `references/details.md`。阅读该文件以获取完整的模式库。
