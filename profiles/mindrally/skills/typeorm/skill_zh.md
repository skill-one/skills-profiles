# TypeORM 开发指南

你是一位 TypeORM、TypeScript 和数据库设计的专家，专注于数据映射模式和企业级应用架构。

## 核心原则

- TypeORM 支持Active Record和数据映射模式
- 使用TypeScript装饰器进行实体和列定义
- 支持MySQL、PostgreSQL、MariaDB、SQLite、MS SQL Server、Oracle等
- 可在Node.js、浏览器、Ionic、Cordova、React Native、NativeScript、Expo和Electron中运行
- 对数据库迁移提供一流支持

## TypeScript配置

tsconfig.json中需要的设置：

```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "strict": true,
    "target": "ES2020",
    "module": "commonjs",
    "moduleResolution": "node"
  }
}
```

## 实体定义

### 基本实体

```typescript
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from "typeorm";

@Entity("users")
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: "varchar", length: 255, unique: true })
  email: string;

  @Column({ type: "varchar", length: 255, nullable: true })
  name: string | null;

  @Column({ type: "boolean", default: true })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

### 主键选项

```typescript
// 自增
@PrimaryGeneratedColumn()
id: number;

// UUID
@PrimaryGeneratedColumn("uuid")
id: string;

// 自定义主键
@PrimaryColumn()
id: string;

// 复合主键
@Entity()
export class OrderItem {
  @PrimaryColumn()
  orderId: number;

  @PrimaryColumn()
  productId: number;
}
```

### 列装饰器

```typescript
@Entity()
export class Product {
  @PrimaryGeneratedColumn()
  id: number;

  // 字符串列
  @Column({ type: "varchar", length: 255 })
  name: string;

  @Column({ type: "text", nullable: true })
  description: string | null;

  // 数字列
  @Column({ type: "decimal", precision: 10, scale: 2 })
  price: number;

  @Column({ type: "int", default: 0 })
  stock: number;

  // 布尔值
  @Column({ type: "boolean", default: true })
  isAvailable: boolean;

  // JSON
  @Column({ type: "jsonb", nullable: true })
  metadata: Record<string, any> | null;

  // 枚举
  @Column({
    type: "enum",
    enum: ["active", "inactive", "pending"],
    default: "pending",
  })
  status: "active" | "inactive" | "pending";

  // 时间戳
  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @DeleteDateColumn()
  deletedAt: Date | null; // 用于软删除

  // 版本列，用于乐观锁
  @VersionColumn()
  version: number;
}
```

## 关系

### 一对一

```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @OneToOne(() => Profile, (profile) => profile.user, { cascade: true })
  @JoinColumn()
  profile: Profile;
}

@Entity()
export class Profile {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  bio: string;

  @OneToOne(() => User, (user) => user.profile)
  user: User;
}
```

### 一对多/多对一

```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @OneToMany(() => Post, (post) => post.author)
  posts: Post[];
}

@Entity()
export class Post {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @ManyToOne(() => User, (user) => user.posts, { onDelete: "CASCADE" })
  @JoinColumn({ name: "author_id" })
  author: User;

  @Column()
  authorId: number; // 显式外键列
}
```

### 多对多

```typescript
@Entity()
export class Post {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @ManyToMany(() => Tag, (tag) => tag.posts)
  @JoinTable({
    name: "post_tags",
    joinColumn: { name: "post_id" },
    inverseJoinColumn: { name: "tag_id" },
  })
  tags: Tag[];
}

@Entity()
export class Tag {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  name: string;

  @ManyToMany(() => Post, (post) => post.tags)
  posts: Post[];
}
```

## Repository模式

### 基本Repository使用

```typescript
import { AppDataSource } from "./data-source";
import { User } from "./entities/User";

const userRepository = AppDataSource.getRepository(User);

// 查找所有
const users = await userRepository.find();

// 带条件的查找
const activeUsers = await userRepository.find({
  where: { isActive: true },
});

// 查找一个
const user = await userRepository.findOne({
  where: { id: 1 },
});

// 查找或失败
const user = await userRepository.findOneOrFail({
  where: { id: 1 },
});

// 保存
const newUser = userRepository.create({
  email: "user@example.com",
  name: "John Doe",
});
await userRepository.save(newUser);

// 更新
await userRepository.update({ id: 1 }, { name: "Jane Doe" });

// 删除
await userRepository.delete({ id: 1 });

// 软删除（需要@DeleteDateColumn）
await userRepository.softDelete({ id: 1 });
```

### 自定义Repository

```typescript
import { Repository, DataSource } from "typeorm";
import { User } from "./entities/User";

export class UserRepository extends Repository<User> {
  constructor(private dataSource: DataSource) {
    super(User, dataSource.createEntityManager());
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.findOne({ where: { email } });
  }

  async findActiveUsers(): Promise<User[]> {
    return this.find({
      where: { isActive: true },
      order: { createdAt: "DESC" },
    });
  }

  async findWithPosts(userId: number): Promise<User | null> {
    return this.findOne({
      where: { id: userId },
      relations: ["posts"],
    });
  }
}
```

### 查询构建器

```typescript
const users = await userRepository
  .createQueryBuilder("user")
  .leftJoinAndSelect("user.posts", "post")
  .where("user.isActive = :isActive", { isActive: true })
  .andWhere("post.publishedAt IS NOT NULL")
  .orderBy("user.createdAt", "DESC")
  .skip(0)
  .take(10)
  .getMany();

// 带原始结果
const result = await userRepository
  .createQueryBuilder("user")
  .select("COUNT(*)", "count")
  .where("user.isActive = :isActive", { isActive: true })
  .getRawOne();

// 使用查询构建器插入
await userRepository
  .createQueryBuilder()
  .insert()
  .into(User)
  .values([
    { email: "user1@example.com", name: "User 1" },
    { email: "user2@example.com", name: "User 2" },
  ])
  .execute();
```

## 数据源配置

```typescript
// data-source.ts
import { DataSource } from "typeorm";
import { User } from "./entities/User";
import { Post } from "./entities/Post";

export const AppDataSource = new DataSource({
  type: "postgres",
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  username: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,

  // 实体配置
  entities: [User, Post],
  // 或使用glob模式：entities: ["src/entities/**/*.ts"]

  // 迁移
  migrations: ["src/migrations/**/*.ts"],

  // 同步 - 生产环境中绝对不要使用
  synchronize: false,

  // 日志
  logging: process.env.NODE_ENV === "development",

  // 连接池
  poolSize: 10,

  // SSL（用于生产）
  ssl: process.env.NODE_ENV === "production" ? { rejectUnauthorized: false } : false,
});

// 初始化连接
AppDataSource.initialize()
  .then(() => console.log("Data Source initialized"))
  .catch((error) => console.error("Error initializing Data Source:", error));
```

## 迁移

### 创建迁移

```bash
# 从实体变更生成迁移
npx typeorm migration:generate src/migrations/CreateUsers -d src/data-source.ts

# 创建空迁移
npx typeorm migration:create src/migrations/SeedUsers

# 运行迁移
npx typeorm migration:run -d src/data-source.ts

# 回滚最后一个迁移
npx typeorm migration:revert -d src/data-source.ts
```

### 迁移文件结构

```typescript
import { MigrationInterface, QueryRunner, Table, TableIndex } from "typeorm";

export class CreateUsers1234567890 implements MigrationInterface {
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
            length: "255",
            isUnique: true,
          },
          {
            name: "name",
            type: "varchar",
            length: "255",
            isNullable: true,
          },
          {
            name: "is_active",
            type: "boolean",
            default: true,
          },
          {
            name: "created_at",
            type: "timestamp",
            default: "CURRENT_TIMESTAMP",
          },
          {
            name: "updated_at",
            type: "timestamp",
            default: "CURRENT_TIMESTAMP",
            onUpdate: "CURRENT_TIMESTAMP",
          },
        ],
      }),
      true
    );

    await queryRunner.createIndex(
      "users",
      new TableIndex({
        name: "IDX_USERS_EMAIL",
        columnNames: ["email"],
      })
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.dropIndex("users", "IDX_USERS_EMAIL");
    await queryRunner.dropTable("users");
  }
}
```

## 事务

```typescript
// 使用QueryRunner
const queryRunner = AppDataSource.createQueryRunner();
await queryRunner.connect();
await queryRunner.startTransaction();

try {
  const user = queryRunner.manager.create(User, {
    email: "user@example.com",
    name: "User",
  });
  await queryRunner.manager.save(user);

  const post = queryRunner.manager.create(Post, {
    title: "First Post",
    author: user,
  });
  await queryRunner.manager.save(post);

  await queryRunner.commitTransaction();
} catch (error) {
  await queryRunner.rollbackTransaction();
  throw error;
} finally {
  await queryRunner.release();
}

// 使用事务方法
await AppDataSource.transaction(async (manager) => {
  const user = manager.create(User, {
    email: "user@example.com",
    name: "User",
  });
  await manager.save(user);

  const post = manager.create(Post, {
    title: "First Post",
    author: user,
  });
  await manager.save(post);
});
```

## NestJS集成

```typescript
// app.module.ts
import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { User } from "./entities/user.entity";
import { UsersModule } from "./users/users.module";

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: "postgres",
      host: "localhost",
      port: 5432,
      username: "user",
      password: "password",
      database: "db",
      entities: [User],
      synchronize: false,
    }),
    UsersModule,
  ],
})
export class AppModule {}

// users/users.module.ts
@Module({
  imports: [TypeOrmModule.forFeature([User])],
  providers: [UsersService],
  controllers: [UsersController],
})
export class UsersModule {}

// users/users.service.ts
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}

  findAll(): Promise<User[]> {
    return this.usersRepository.find();
  }

  findOne(id: number): Promise<User | null> {
    return this.usersRepository.findOneBy({ id });
  }
}
```

## 最佳实践

### 生产环境中使用迁移

生产环境中绝对不要使用`synchronize: true`。始终使用迁移：

```typescript
// 开发环境：使用迁移，不要同步
synchronize: false,
```

###  eagerly加载 vs 懒加载

```typescript
// eagerly加载 - 自动加载关系
@OneToMany(() => Post, (post) => post.author, { eager: true })
posts: Post[];

// 懒加载 - 在访问时加载关系
@OneToMany(() => Post, (post) => post.author)
posts: Promise<Post[]>;

// 显式加载（推荐）
const user = await userRepository.findOne({
  where: { id: 1 },
  relations: ["posts"],
});
```

### 避免 N+1 查询

```typescript
// 不好：N+1查询
const users = await userRepository.find();
for (const user of users) {
  console.log(user.posts); // 对每个用户进行单独查询
}

// 好：eager加载关系
const users = await userRepository.find({
  relations: ["posts"],
});
```

### 使用索引

```typescript
@Entity()
@Index(["email"])
@Index(["firstName", "lastName"])
export class User {
  @Column()
  @Index()
  email: string;

  @Column()
  firstName: string;

  @Column()
  lastName: string;
}
```

### 级联操作

```typescript
@OneToMany(() => Post, (post) => post.author, {
  cascade: true, // 保存/删除相关帖子
  onDelete: "CASCADE", // 数据库级别的级联
})
posts: Post[];
```

### 命名策略

为了在TypeScript和数据库之间保持一致的命名：

```typescript
import { DefaultNamingStrategy, NamingStrategyInterface } from "typeorm";
import { snakeCase } from "typeorm/util/StringUtils";

export class SnakeNamingStrategy extends DefaultNamingStrategy implements NamingStrategyInterface {
  tableName(targetName: string, userSpecifiedName: string | undefined): string {
    return userSpecifiedName ? userSpecifiedName : snakeCase(targetName);
  }

  columnName(propertyName: string, customName: string, embeddedPrefixes: string[]): string {
    return snakeCase(embeddedPrefixes.join("_")) + (customName ? customName : snakeCase(propertyName));
  }
}

// 在数据源配置中使用
namingStrategy: new SnakeNamingStrategy(),
```
