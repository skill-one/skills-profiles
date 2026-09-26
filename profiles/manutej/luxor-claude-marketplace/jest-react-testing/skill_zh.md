# Jest React 测试

使用 Jest 和 React Testing Library 测试 React 应用的全面技能。本技能涵盖从基本组件测试到高级模式的所有内容，包括模拟、异步测试、自定义钩子测试和集成测试策略。

## 何时使用此技能

使用此技能时：

- 使用 Jest 和 React Testing Library 测试 React 组件
- 为 React 项目设置 Jest 配置
- 为组件、钩子和实用工具编写单元测试
- 测试用户交互和组件行为
- 模拟模块、函数、API 调用和外部依赖
- 测试异步操作（API 调用、计时器、Promise）
- 测试自定义 React 钩子
- 为复杂组件树编写集成测试
- 调试失败的测试或提高测试覆盖率
- 遵循测试最佳实践和模式

## 核心概念

### 测试理念

React Testing Library 遵循以下指导原则：

- **测试用户行为，而非实现**：编写类似于用户与应用程序交互的测试
- **优先考虑可访问性**：使用促进可访问组件的查询（getByRole, getByLabelText）
- **避免测试实现细节**：不要直接测试状态、属性或内部方法
- **可维护的测试**：测试应在行为改变时中断，而非代码重构时
- **信心重于覆盖率**：专注于提供信心的测试，而非 100% 覆盖率

### 关键测试概念

1. **查询**：查找元素的函数（getBy, queryBy, findBy）
2. **用户事件**：模拟用户交互（点击、输入、选择）
3. **异步测试**：测试具有异步操作的组件
4. **模拟**：用受控的测试替身替换依赖项
5. **断言**：使用匹配器验证预期结果

## Jest 配置

### 基本 Jest 配置

**jest.config.js**（JavaScript 项目）：
```javascript
/** @type {import('jest').Config} */
const config = {
  // 用于 DOM 测试的测试环境
  testEnvironment: 'jsdom',

  // 环境设置后加载的设置文件
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],

  // 模块路径
  moduleDirectories: ['node_modules', 'src'],

  // 使用 babel-jest 转换文件
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest',
  },

  // 模块名称映射器，用于静态资源和 CSS
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },

  // 覆盖率配置
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/**/*.test.{js,jsx}',
    '!src/**/__tests__/**',
  ],

  // 覆盖率阈值
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

module.exports = config;
```

**jest.config.js**（TypeScript 项目）：
```typescript
import type {Config} from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],

  moduleDirectories: ['node_modules', 'src'],

  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },

  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/__mocks__/fileMock.ts',
    '^@/(.*)$': '<rootDir>/src/$1',
  },

  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/index.tsx',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/__tests__/**',
    '!src/**/*.d.ts',
  ],

  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

export default config;
```

### 设置文件

**src/setupTests.js**：
```javascript
// 添加来自 jest-dom 的自定义 Jest 匹配器
import '@testing-library/jest-dom';

// 扩展 expect 以使用 jest-extended 匹配器（可选）
import * as matchers from 'jest-extended';
expect.extend(matchers);

// 模拟 window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// 模拟 IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};

// 在测试中抑制控制台错误（可选）
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// 每个测试后重置模拟
afterEach(() => {
  jest.clearAllMocks();
});
```

### 文件模拟

**__mocks__/fileMock.js**：
```javascript
module.exports = 'test-file-stub';
```

**__mocks__/styleMock.js**：
```javascript
module.exports = {};
```

## React Testing Library 查询

### 查询类型

React Testing Library 提供三种类型的查询：

1. **getBy**：返回元素或在元素不存在时抛出错误（用于确保存在的元素）
2. **queryBy**：返回元素或 null（用于可能不存在的元素）
3. **findBy**：返回解析为元素的 Promise（用于异步元素）

### 查询优先级

**推荐查询顺序**（以可访问性为中心）：

1. **getByRole**：最可访问的查询
   ```javascript
   getByRole('button', { name: /submit/i })
   getByRole('heading', { level: 1 })
   getByRole('textbox', { name: /username/i })
   ```

2. **getByLabelText**：用于带标签的表单字段
   ```javascript
   getByLabelText(/email address/i)
   getByLabelText('Password')
   ```

3. **getByPlaceholderText**：用于带占位符的输入
   ```javascript
   getByPlaceholderText(/search/i)
   ```

4. **getByText**：用于非交互式文本元素
   ```javascript
   getByText(/welcome/i)
   getByText('Error: Invalid credentials')
   ```

5. **getByDisplayValue**：用于带值的表单元素
   ```javascript
   getByDisplayValue('John Doe')
   ```

6. **getByAltText**：用于带 alt 文本的图像
   ```javascript
   getByAltText(/profile picture/i)
   ```

7. **getByTitle**：用于带 title 属性的元素
   ```javascript
   getByTitle(/close/i)
   ```

8. **getByTestId**：当其他查询无效时作为最后手段
   ```javascript
   getByTestId('custom-element')
   ```

### 查询变体

```javascript
// 单个元素查询
screen.getByRole('button')      // 如果未找到或找到多个则抛出
screen.queryByRole('button')    // 如果未找到则返回 null
await screen.findByRole('button') // 异步，最多等待 1000ms

// 多个元素查询
screen.getAllByRole('listitem')      // 如果没有找到则抛出
screen.queryAllByRole('listitem')    // 如果没有找到则返回 []
await screen.findAllByRole('listitem') // 异步版本
```

## 组件测试策略

### 基本组件测试

```javascript
import { render, screen } from '@testing-library/react';
import { Greeting } from './Greeting';

describe('Greeting Component', () => {
  it('renders greeting message', () => {
    render(<Greeting name="Alice" />);

    expect(screen.getByText(/hello, alice/i)).toBeInTheDocument();
  });

  it('renders default greeting when no name provided', () => {
    render(<Greeting />);

    expect(screen.getByText(/hello, guest/i)).toBeInTheDocument();
  });
});
```

### 测试用户交互

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Counter } from './Counter';

describe('Counter Component', () => {
  it('increments counter on button click', async () => {
    const user = userEvent.setup();
    render(<Counter />);

    const button = screen.getByRole('button', { name: /increment/i });
    const count = screen.getByText(/count: 0/i);

    expect(count).toBeInTheDocument();

    await user.click(button);

    expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
  });

  it('decrements counter on button click', async () => {
    const user = userEvent.setup();
    render(<Counter initialCount={5} />);

    const decrementBtn = screen.getByRole('button', { name: /decrement/i });

    await user.click(decrementBtn);

    expect(screen.getByText(/count: 4/i)).toBeInTheDocument();
  });
});
```

### 测试表单

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm Component', () => {
  it('submits form with username and password', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn();

    render(<LoginForm onSubmit={handleSubmit} />);

    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /submit/i });

    await user.type(usernameInput, 'testuser');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    expect(handleSubmit).toHaveBeenCalledTimes(1);
    expect(handleSubmit).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);

    const submitButton = screen.getByRole('button', { name: /submit/i });

    await user.click(submitButton);

    expect(screen.getByText(/username is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });
});
```

### 测试条件渲染

```javascript
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile Component', () => {
  it('shows loading state when loading', () => {
    render(<UserProfile loading={true} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });

  it('shows user data when loaded', () => {
    const user = {
      name: 'John Doe',
      email: 'john@example.com',
    };

    render(<UserProfile loading={false} user={user} />);

    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /john doe/i })).toBeInTheDocument();
    expect(screen.getByText(/john@example.com/i)).toBeInTheDocument();
  });

  it('shows error message when error occurs', () => {
    render(<UserProfile loading={false} error="Failed to load user" />);

    expect(screen.getByText(/failed to load user/i)).toBeInTheDocument();
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });
});
```

## 模拟模式

### 模拟模块

**自动模拟**：
```javascript
// __mocks__/axios.js
export default {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};
```

**测试中使用**：
```javascript
import axios from 'axios';
import { UserService } from './UserService';

jest.mock('axios');

describe('UserService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches users successfully', async () => {
    const mockUsers = [{ id: 1, name: 'Alice' }];
    axios.get.mockResolvedValue({ data: mockUsers });

    const users = await UserService.getUsers();

    expect(axios.get).toHaveBeenCalledWith('/api/users');
    expect(users).toEqual(mockUsers);
  });

  it('handles fetch error', async () => {
    axios.get.mockRejectedValue(new Error('Network Error'));

    await expect(UserService.getUsers()).rejects.toThrow('Network Error');
  });
});
```

### 模拟函数

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button Component', () => {
  it('calls onClick handler when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<Button onClick={handleClick}>Click Me</Button>);

    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('calls onClick with event object', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<Button onClick={handleClick}>Click Me</Button>);

    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'click',
      })
    );
  });
});
```

### 使用 MSW 模拟 API 调用

**设置 MSW**：
```javascript
// src/mocks/handlers.js
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
      ])
    );
  },

  rest.post('/api/users', async (req, res, ctx) => {
    const { name, email } = await req.json();

    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        name,
        email,
      })
    );
  }),
];
```

**设置服务器**：
```javascript
// src/mocks/server.js
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

**在 setupTests.js 中配置**：
```javascript
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**测试中使用**：
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import { server } from './mocks/server';
import { rest } from 'msw';
import { UserList } from './UserList';

describe('UserList Component', () => {
  it('fetches and displays users', async () => {
    render(<UserList />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/alice/i)).toBeInTheDocument();
      expect(screen.getByText(/bob/i)).toBeInTheDocument();
    });
  });

  it('handles server error', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({ message: 'Internal Server Error' })
        );
      })
    );

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/error loading users/i)).toBeInTheDocument();
    });
  });
});
```

### 模拟上下文

```javascript
import { render, screen } from '@testing-library/react';
import { AuthContext } from './AuthContext';
import { ProtectedComponent } from './ProtectedComponent';

const mockAuthContext = (overrides = {}) => ({
  user: { id: 1, name: 'Test User' },
  isAuthenticated: true,
  login: jest.fn(),
  logout: jest.fn(),
  ...overrides,
});

describe('ProtectedComponent', () => {
  it('renders content for authenticated user', () => {
    const contextValue = mockAuthContext();

    render(
      <AuthContext.Provider value={contextValue}>
        <ProtectedComponent />
      </AuthContext.Provider>
    );

    expect(screen.getByText(/welcome, test user/i)).toBeInTheDocument();
  });

  it('renders login prompt for unauthenticated user', () => {
    const contextValue = mockAuthContext({
      user: null,
      isAuthenticated: false,
    });

    render(
      <AuthContext.Provider value={contextValue}>
        <ProtectedComponent />
      </AuthContext.Provider>
    );

    expect(screen.getByText(/please log in/i)).toBeInTheDocument();
  });
});
```

### 模拟子组件

```javascript
import { render, screen } from '@testing-library/react';
import { ParentComponent } from './ParentComponent';

// 模拟子组件
jest.mock('./ChildComponent', () => ({
  ChildComponent: ({ title, onAction }) => (
    <div>
      <h2>{title}</h2>
      <button onClick={onAction}>Mocked Action</button>
    </div>
  ),
}));

describe('ParentComponent', () => {
  it('renders with mocked child', () => {
    render(<ParentComponent />);

    expect(screen.getByText(/mocked action/i)).toBeInTheDocument();
  });
});
```

## 异步测试模式

### 使用 waitFor 测试

```javascript
import { render, screen, waitFor } from '@testing-library/react';
import { AsyncComponent } from './AsyncComponent';

describe('AsyncComponent', () => {
  it('loads and displays data', async () => {
    render(<AsyncComponent />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it('waits for specific condition', async () => {
    render(<AsyncComponent />);

    await waitFor(
      () => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });
});
```

### 使用 findBy 查询测试

```javascript
import { render, screen } from '@testing-library/react';
import { DataFetcher } from './DataFetcher';

describe('DataFetcher Component', () => {
  it('displays fetched data', async () => {
    render(<DataFetcher />);

    // findBy 自动等待元素出现
    const heading = await screen.findByRole('heading', { name: /data/i });
    expect(heading).toBeInTheDocument();
  });

  it('handles timeout for missing elements', async () => {
    render(<DataFetcher url="/api/missing" />);

    await expect(
      screen.findByText(/success/i, {}, { timeout: 500 })
    ).rejects.toThrow();
  });
});
```

### 测试 Promise

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AsyncForm } from './AsyncForm';

describe('AsyncForm Component', () => {
  it('submits form and shows success message', async () => {
    const user = userEvent.setup();
    render(<AsyncForm />);

    const input = screen.getByLabelText(/name/i);
    const submitBtn = screen.getByRole('button', { name: /submit/i });

    await user.type(input, 'John Doe');
    await user.click(submitBtn);

    const successMsg = await screen.findByText(/submitted successfully/i);
    expect(successMsg).toBeInTheDocument();
  });

  it('shows error message on failure', async () => {
    const user = userEvent.setup();
    render(<AsyncForm shouldFail={true} />);

    const submitBtn = screen.getByRole('button', { name: /submit/i });
    await user.click(submitBtn);

    const errorMsg = await screen.findByRole('alert');
    expect(errorMsg).toHaveTextContent(/submission failed/i);
  });
});
```

### 使用 Fake Timers 测试

```javascript
import { render, screen, act } from '@testing-library/react';
import { Timer } from './Timer';

describe('Timer Component', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('updates timer every second', () => {
    render(<Timer />);

    expect(screen.getByText(/0 seconds/i)).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(1000);
    });

    expect(screen.getByText(/1 second/i)).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(3000);
    });

    expect(screen.getByText(/4 seconds/i)).toBeInTheDocument();
  });

  it('cleans up timer on unmount', () => {
    const { unmount } = render(<Timer />);

    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');

    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();
  });
});
```

## 测试自定义钩子

### 基本钩子测试

```javascript
import { renderHook } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter Hook', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);
  });

  it('initializes with provided value', () => {
    const { result } = renderHook(() => useCounter(10));

    expect(result.current.count).toBe(10);
  });

  it('increments count', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('decrements count', () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });
});
```

### 使用 Props 测试钩子

```javascript
import { renderHook } from '@testing-library/react';
import { useFetch } from './useFetch';

describe('useFetch Hook', () => {
  it('fetches data for given URL', async () => {
    const { result } = renderHook(() => useFetch('/api/users'));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeDefined();
    expect(result.current.error).toBeNull();
  });

  it('refetches when URL changes', async () => {
    const { result, rerender } = renderHook(
      ({ url }) => useFetch(url),
      { initialProps: { url: '/api/users' }
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const firstData = result.current.data;

    rerender({ url: '/api/posts' });

    await waitFor(() => {
      expect(result.current.data).not.toEqual(firstData);
    });
  });
});
```

### 使用 Context 测试钩子

```javascript
import { renderHook } from '@testing-library/react';
import { ThemeProvider } from './ThemeContext';
import { useTheme } from './useTheme';

describe('useTheme Hook', () => {
  const wrapper = ({ children }) => (
    <ThemeProvider initialTheme="light">
      {children}
    </ThemeProvider>
  );

  it('returns current theme', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe('light');
  });

  it('toggles theme', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe('dark');
  });
});
```

### 测试异步钩子

```javascript
import { renderHook, waitFor } from '@testing-library/react';
import { useAsyncData } from './useAsyncData';

describe('useAsyncData Hook', () => {
  it('loads data asynchronously', async () => {
    const { result } = renderHook(() => useAsyncData('/api/data'));

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeNull();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeDefined();
  });

  it('handles errors', async () => {
    const { result } = renderHook(() => useAsyncData('/api/error'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeNull();
  });
});
```

## 集成测试模式

### 测试组件集成

```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from './App';

describe('App Integration', () => {
  it('navigates between pages', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText(/home page/i)).toBeInTheDocument();

    const aboutLink = screen.getByRole('link', { name: /about/i });
    await user.click(aboutLink);

    expect(screen.getByText(/about page/i)).toBeInTheDocument();
  });

  it('completes full user flow', async () => {
    const user = userEvent.setup();
    render(<App />);

    // 导航到注册
    await user.click(screen.getByRole('link', { name: /sign up/i });

    // 填写表单
    await user.type(screen.getByLabelText(/email/i), 'user@example.com';
    await user.type(screen.getByLabelText(/password/i), 'password123';

    // 提交表单
    await user.click(screen.getByRole('button', { name: /submit/i }));

    // 验证成功
    expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
  });
});
```

### 使用 Router 测试

```javascript
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { AppRoutes } from './AppRoutes';

const renderWithRouter = (ui, { initialEntries = ['/'] } = {}) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      {ui}
    </MemoryRouter>
  );
};

describe('AppRoutes Integration', () => {
  it('renders home page by default', () => {
    renderWithRouter(<AppRoutes />);

    expect(screen.getByText(/home/i)).toBeInTheDocument();
  });

  it('renders user page at /users/:id', () => {
    renderWithRouter(<AppRoutes />, { initialEntries: ['/users/123'] });

    expect(screen.getByText(/user profile/i)).toBeInTheDocument();
  });

  it('navigates programmatically', async () => {
    const user = userEvent.setup();
    renderWithRouter(<AppRoutes />);

    const navButton = screen.getByRole('button', { name: /go to profile/i });
    await user.click(navButton);

    expect(screen.getByText(/profile page/i)).toBeInTheDocument();
  });
});
```

### 使用 Redux 测试

```javascript
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import userEvent from '@testing-library/user-event';
import { TodoList } from './TodoList';
import todosReducer from './todosSlice';

const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      todos: todosReducer,
    },
    preloadedState: initialState,
  });
};

const renderWithStore = (ui, { store = createMockStore() } = {}) => {
  return render(<Provider store={store}>{ui}</Provider>);
};

describe('TodoList Integration', () => {
  it('adds new todo', async () => {
    const user = userEvent.setup();
    renderWithStore(<TodoList />);

    const input = screen.getByPlaceholderText(/new todo/i);
    const addButton = screen.getByRole('button', { name: /add/i });

    await user.type(input, 'Buy groceries');
    await user.click(addButton);

    expect(screen.getByText(/buy groceries/i)).toBeInTheDocument();
  });

  it('renders initial todos from store', () => {
    const initialState = {
      todos: {
        items: [
          { id: 1, text: 'Existing todo', completed: false },
        ],
      },
    };

    renderWithStore(<TodoList />, { store: createMockStore(initialState) });

    expect(screen.getByText(/existing todo/i)).toBeInTheDocument();
  });
});
```

## Jest DOM 匹配器

### 常用匹配器

```javascript
// 元素存在
expect(element).toBeInTheDocument();
expect(element).not.toBeInTheDocument();

// 可见性
expect(element).toBeVisible();
expect(element).not.toBeVisible();

// 文本内容
expect(element).toHaveTextContent('Hello World');
expect(element).toHaveTextContent(/hello/i);

// 属性
expect(element).toHaveAttribute('type', 'submit');
expect(element).toHaveAttribute('disabled');

// 类
expect(element).toHaveClass('active');
expect(element).toHaveClass('btn', 'btn-primary');

// 样式
expect(element).toHaveStyle({ color: 'red' });
expect(element).toHaveStyle('display: none');

// 表单
expect(input).toHaveValue('test');
expect(input).toHaveDisplayValue('Test');
expect(checkbox).toBeChecked();
expect(checkbox).not.toBeChecked();
expect(input).toBeDisabled();
expect(input).toBeEnabled();
expect(input).toBeRequired();
expect(input).toBeInvalid();
expect(input).toBeValid();

// 聚焦
expect(element).toHaveFocus();

// 可访问性
expect(element).toHaveAccessibleName('Submit button');
expect(element).toHaveAccessibleDescription('Click to submit form');

// 包含
expect(container).toContainElement(child);
expect(container).toContainHTML('<span>Text</span>');
```

## 最佳实践

### 测试组织

1. **分组相关测试**：使用 `describe` 块组织测试
   ```javascript
   describe('UserProfile', () => {
     describe('when loading', () => {
       it('shows loading spinner', () => {});
     });

     describe('when loaded', () => {
       it('displays user information', () => {});
       it('shows profile picture', () => {});
     });
   });
   ```

2. **使用描述性测试名称**：测试名称应描述行为
   ```javascript
   // 好
   it('displays error message when login fails', () => {};

   // 差
   it('test login', () => {});
   ```

3. **遵循 AAA 模式**：安排、行动、断言
   ```javascript
   it('increments counter', async () => {
     // 安排
     const user = userEvent.setup();
     render(<Counter />);

     // 行动
     await user.click(screen.getByRole('button', { name: /increment/i });

     // 断言
     expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
   });
   ```

### 查询最佳实践

1. **优先使用可访问性查询**：使用 getByRole, getByLabelText
2. **使用 screen 查询**：从 screen 考虑，而非解构 render
3. **避免使用 getByTestId**：仅在必要时使用
4. **使用正则表达式**：比精确字符串更灵活

### 异步测试最佳实践

1. **使用 findBy 进行异步测试**：优先使用 findBy 考虑
2. **设置适当的超时**：为 waitFor 设置超时，用于慢速操作
3. **避免 act() 警告**：适当使用 userEvent, waitFor, findBy
4. **测试后重置模拟**：每次测试后重置模拟

### 模拟最佳实践

1. **在正确的级别模拟**：模拟外部依赖，而非内部逻辑
2. **测试后重置模拟**：测试后清除模拟
3. **使用 MSW 模拟 API**：优先使用 MSW 考虑
4. **避免过度模拟**：不要模拟你正在测试的内容

### 覆盖率最佳实践

1. **关注行为**：测试用户行为，而非实现
2. **不要追求 100% 覆盖率**：专注于提供信心的测试，而非 100% 覆盖率
3. **测试错误状态**：包括错误处理测试
4. **测试边界条件**：包括边界条件测试

## 常见测试模式

### 测试列表和迭代

```javascript
it('renders list of items', () => {
    const items = ['Apple', 'Banana', 'Cherry'];
    render(<ItemList items={items} />);

    items.forEach(item => {
        expect(screen.getByText(item)).toBeInTheDocument();
    });
});
```

### 测试可访问性

```javascript
it('has accessible form', () => {
  render(<ContactForm />);

  const nameInput = screen.getByLabelText(/username/i);
  const passwordInput = screen.getByLabelText(/password/i);
  const submitButton = screen.getByRole('button', { name: /submit/i });

  await user.type(nameInput, 'user@example.com');
  await user.type(passwordInput, 'password123');
  await user.click(submitButton);

  expect(screen.getByText(/welcome/i)).toBeInTheDocument();
});
```

### 测试错误边界

```javascript
it('catches errors and displays fallback', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    // 抑制控制台错误（可选）
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Something went wrong</div>}>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

    spy.mockRestore();
});
```

### 测试 Portal

```javascript
it('renders modal in portal', () => {
    render(<Modal isOpen={true}>Modal Content</Modal>);

    const modal = screen.getByText(/modal content/i);
    expect(modal).toBeInTheDocument();

    // Portal 应在 document.body 中，而非组件树中
    expect(modal.parentElement).toBe(document.body);
});
```

## 故障排除

### 常见问题

**问题**：无法找到元素
- **解决方案**：使用 screen.debug() 查看DOM，检查查询类型，等待异步更新

**问题**：act 警告
- **解决方案**：使用 userEvent 考虑，使用 waitFor/findBy, wrap state updates in act(), use userEvent, waitFor, findBy

**问题**：Jest 超时
- **解决方案**：增加超时，检查无限循环，确保异步操作完成

**问题**：无法读取未定义的属性
- **解决方案**：检查模拟是否设置正确，确保组件接收必要的属性

**问题**：找到多个元素
- **解决方案**：使查询更具体，使用 getAllBy 用于多个元素

## 资源

- Jest 文档：https://jestjs.io/
- React Testing Library：https://testing-library.com/react
- Testing Library 查询：https://testing-library.com/docs/queries/about
- Jest DOM 匹配器：https://github.com/testing-library/jest-dom
- MSW 文档：https://mswjs.io/
- 常见错误：https://kentcdodds.com/blog/common-mistakes-with-react-testing-library

---

**技能版本**：1.0.0
**最后更新**：2025 年 10 月
**技能类别**：测试、React、质量保证
**兼容版本**：Jest 29+, React Testing Library 13+, React 16.8+
```
