# JavaScript 测试模式

使用现代测试框架和最佳实践在 JavaScript/TypeScript 应用程序中实现稳健测试策略的综合指南。

## 何时使用此技能

- 为新项目设置测试基础设施
- 为函数和类编写单元测试
- 为 API 和服务创建集成测试
- 为用户流程实现端到端测试
- 模拟外部依赖项和 API
- 测试 React、Vue 或其他前端组件
- 实现测试驱动开发 (TDD)
- 在 CI/CD 管道中设置持续测试

## 测试框架

### Jest - 功能全面的测试框架

**设置：**

```typescript
// jest.config.ts
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src"],
  testMatch: ["**/__tests__/**/*.ts", "**/?(*.)+(spec|test).ts"],
  collectCoverageFrom: [
    "src/**/*.ts",
    "!src/**/*.d.ts",
    "!src/**/*.interface.ts",
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ["<rootDir>/src/test/setup.ts"],
};

export default config;
```

### Vitest - 快速、Vite 本地测试

**设置：**

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["**/*.d.ts", "**/*.config.ts", "**/dist/**"],
    },
    setupFiles: ["./src/test/setup.ts"],
  },
});
```

## 单元测试模式

### 模式 1：测试纯函数

```typescript
// utils/calculator.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("除以零");
  }
  return a / b;
}

// utils/calculator.test.ts
import { describe, it, expect } from "vitest";
import { add, divide } from "./calculator";

describe("Calculator", () => {
  describe("add", () => {
    it("应该相加两个正数", () => {
      expect(add(2, 3)).toBe(5);
    });

    it("应该相加负数", () => {
      expect(add(-2, -3)).toBe(-5);
    });

    it("应该处理零", () => {
      expect(add(0, 5)).toBe(5);
      expect(add(5, 0)).toBe(5);
    });
  });

  describe("divide", () => {
    it("应该除以两个数", () => {
      expect(divide(10, 2)).toBe(5);
    });

    it("应该处理小数结果", () => {
      expect(divide(5, 2)).toBe(2.5);
    });

    it("除以零时应该抛出错误", () => {
      expect(() => divide(10, 0)).toThrow("除以零");
    });
  });
});
```

### 模式 2：测试类

```typescript
// services/user.service.ts
export class UserService {
  private users: Map<string, User> = new Map();

  create(user: User): User {
    if (this.users.has(user.id)) {
      throw new Error("用户已存在");
    }
    this.users.set(user.id, user);
    return user;
  }

  findById(id: string): User | undefined {
    return this.users.get(id);
  }

  update(id: string, updates: Partial<User>): User {
    const user = this.users.get(id);
    if (!user) {
      throw new Error("用户未找到");
    }
    const updated = { ...user, ...updates };
    this.users.set(id, updated);
    return updated;
  }

  delete(id: string): boolean {
    return this.users.delete(id);
  }
}

// services/user.service.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { UserService } from "./user.service";

describe("UserService", () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  describe("create", () => {
    it("应该创建新用户", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      const created = service.create(user);

      expect(created).toEqual(user);
      expect(service.findById("1")).toEqual(user);
    });

    it("如果用户已存在，应该抛出错误", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      service.create(user);

      expect(() => service.create(user)).toThrow("用户已存在");
    });
  });

  describe("update", () => {
    it("应该更新现有用户", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      service.create(user);

      const updated = service.update("1", { name: "Jane" });

      expect(updated.name).toBe("Jane");
      expect(updated.email).toBe("john@example.com");
    });

    it("如果用户未找到，应该抛出错误", () => {
      expect(() => service.update("999", { name: "Jane" })).toThrow(
        "用户未找到",
      );
    });
  });
});
```

### 模式 3：测试异步函数

```typescript
// services/api.service.ts
export class ApiService {
  async fetchUser(id: string): Promise<User> {
    const response = await fetch(`https://api.example.com/users/${id}`);
    if (!response.ok) {
      throw new Error("用户未找到");
    }
    return response.json();
  }

  async createUser(user: CreateUserDTO): Promise<User> {
    const response = await fetch("https://api.example.com/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user),
    });
    return response.json();
  }
}

// services/api.service.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ApiService } from "./api.service";

// 全局模拟 fetch
global.fetch = vi.fn();

describe("ApiService", () => {
  let service: ApiService;

  beforeEach(() => {
    service = new ApiService();
    vi.clearAllMocks();
  });

  describe("fetchUser", () => {
    it("应该成功获取用户", async () => {
      const mockUser = { id: "1", name: "John", email: "john@example.com" };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const user = await service.fetchUser("1");

      expect(user).toEqual(mockUser);
      expect(fetch).toHaveBeenCalledWith("https://api.example.com/users/1");
    });

    it("如果用户未找到，应该抛出错误", async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect(service.fetchUser("999")).rejects.toThrow("用户未找到");
    });
  });

  describe("createUser", () => {
    it("应该成功创建用户", async () => {
      const newUser = { name: "John", email: "john@example.com" };
      const createdUser = { id: "1", ...newUser };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => createdUser,
      });

      const user = await service.createUser(newUser);

      expect(user).toEqual(createdUser);
      expect(fetch).toHaveBeenCalledWith(
        "https://api.example.com/users",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify(newUser),
        }),
      );
    });
  });
});
```

## 模拟模式

### 模式 1：模拟模块

```typescript
// services/email.service.ts
import nodemailer from "nodemailer";

export class EmailService {
  private transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: 587,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });

  async sendEmail(to: string, subject: string, html: string) {
    await this.transporter.sendMail({
      from: process.env.EMAIL_FROM,
      to,
      subject,
      html,
    });
  }
}

// services/email.service.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { EmailService } from "./email.service";

vi.mock("nodemailer", () => ({
  default: {
    createTransport: vi.fn(() => ({
      sendMail: vi.fn().mockResolvedValue({ messageId: "123" }),
    })),
  },
}));

describe("EmailService", () => {
  let service: EmailService;

  beforeEach(() => {
    service = new EmailService();
  });

  it("应该成功发送邮件", async () => {
    await service.sendEmail(
      "test@example.com",
      "测试主题",
      "<p>测试正文</p>",
    );

    expect(service["transporter"].sendMail).toHaveBeenCalledWith(
      expect.objectContaining({
        to: "test@example.com",
        subject: "测试主题",
      }),
    );
  });
});
```

### 模式 2：依赖注入用于测试

```typescript
// services/user.service.ts
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  create(user: User): Promise<User>;
}

export class UserService {
  constructor(private userRepository: IUserRepository) {}

  async getUser(id: string): Promise<User> {
    const user = await this.userRepository.findById(id);
    if (!user) {
      throw new Error("用户未找到");
    }
    return user;
  }

  async createUser(userData: CreateUserDTO): Promise<User> {
    // 业务逻辑
    const user = { id: generateId(), ...userData };
    return this.userRepository.create(user);
  }
}

// services/user.service.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { UserService, IUserRepository } from "./user.service";

describe("UserService", () => {
  let service: UserService;
  let mockRepository: IUserRepository;

  beforeEach(() => {
    mockRepository = {
      findById: vi.fn(),
      create: vi.fn(),
    };
    service = new UserService(mockRepository);
  });

  describe("getUser", () => {
    it("如果找到用户，应该返回用户", async () => {
      const mockUser = { id: "1", name: "John", email: "john@example.com" };
      vi.mocked(mockRepository.findById).mockResolvedValue(mockUser);

      const user = await service.getUser("1");

      expect(user).toEqual(mockUser);
      expect(mockRepository.findById).toHaveBeenCalledWith("1");
    });

    it("如果用户未找到，应该抛出错误", async () => {
      vi.mocked(mockRepository.findById).mockResolvedValue(null);

      await expect(service.getUser("999")).rejects.toThrow("用户未找到");
    });
  });

  describe("createUser", () => {
    it("应该成功创建用户", async () => {
      const userData = { name: "John", email: "john@example.com" };
      const createdUser = { id: "1", ...userData };

      vi.mocked(mockRepository.create).mockResolvedValue(createdUser);

      const user = await service.createUser(userData);

      expect(user).toEqual(createdUser);
      expect(mockRepository.create).toHaveBeenCalled();
    });
  });
});
```

### 模式 3：监视函数

```typescript
// utils/logger.ts
export const logger = {
  info: (message: string) => console.log(`INFO: ${message}`),
  error: (message: string) => console.error(`ERROR: ${message}`),
};

// services/order.service.ts
import { logger } from "../utils/logger";

export class OrderService {
  async processOrder(orderId: string): Promise<void> {
    logger.info(`处理订单 ${orderId}`);
    // 处理订单逻辑
    logger.info(`订单 ${orderId} 处理成功`);
  }
}

// services/order.service.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { OrderService } from "./order.service";
import { logger } from "../utils/logger";

describe("OrderService", () => {
  let service: OrderService;
  let loggerSpy: any;

  beforeEach(() => {
    service = new OrderService();
    loggerSpy = vi.spyOn(logger, "info");
  });

  afterEach(() => {
    loggerSpy.mockRestore();
  });

  it("应该记录订单处理", async () => {
    await service.processOrder("123");

    expect(loggerSpy).toHaveBeenCalledWith("处理订单 123");
    expect(loggerSpy).toHaveBeenCalledWith("订单 123 处理成功");
    expect(loggerSpy).toHaveBeenCalledTimes(2);
  });
});
```

## 集成测试

集成测试使用 `supertest` 和测试数据库实例验证真实的数据库操作和 HTTP 端点。始终在 `beforeEach` 中截断表，并在 `afterAll` 中销毁。

有关完整的 API 集成测试示例（supertest + PostgreSQL）和数据库仓库集成测试，请参阅 [references/advanced-testing-patterns.md](references/advanced-testing-patterns.md)。

## 使用 Testing Library 进行前端测试

通过渲染它们并按角色、占位符或测试 ID 进行查询来测试 React 组件。使用 `renderHook` + `act` 测试钩子。优先使用语义查询（`getByRole`、`getByPlaceholderText`）而不是 `data-testid`。

有关完整的 React 组件测试示例（UserForm、使用 `renderHook`/`act` 的钩子），请参阅 [references/advanced-testing-patterns.md](references/advanced-testing-patterns.md)。

## 测试 fixtures 和 factories

使用 `@faker-js/faker` 生成逼真的测试数据 factories。Factories 接受可选的 `overrides`，以便测试可以仅设置它们关心的字段：

```typescript
// tests/fixtures/user.fixture.ts
import { faker } from "@faker-js/faker";

export function createUserFixture(overrides?: Partial<User>): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    createdAt: faker.date.past(),
    ...overrides,
  };
}
```

有关快照测试、覆盖率配置、测试组织模式、Promise 测试和计时器模拟，请参阅 [references/advanced-testing-patterns.md](references/advanced-testing-patterns.md)。

## 最佳实践

1. **遵循 AAA 模式**：准备、执行、断言
2. **每个测试一个断言**：或逻辑相关的断言
3. **描述性测试名称**：应描述正在测试的内容
4. **使用 beforeEach/afterEach**：用于设置和销毁
5. **模拟外部依赖项**：保持测试隔离
6. **测试边界情况**：不只是成功路径
7. **避免实现细节**：测试行为，而不是实现
8. **使用测试 factories**：用于一致测试数据
9. **保持测试快速**：模拟慢操作
10. **尽可能先写测试（TDD）**：当可能时
11. **维护测试覆盖率**：目标是 80%+
12. **使用 TypeScript**：用于类型安全的测试
13. **测试错误处理**：不只是成功情况
14. **谨慎使用 data-testid**：优先使用语义查询
15. **测试后清理**：防止测试污染
