# React 现代化

掌握 React 版本升级、类组件到 Hooks 的迁移、并发特性的采用以及 codemods 实现自动化转换。

## 何时使用这项技能

- 升级 React 应用到最新版本
- 将类组件迁移到使用 Hooks 的函数组件
- 采用并发 React 特性（Suspense、过渡效果）
- 应用 codemods 实现自动化重构
- 现代化状态管理模式
- 更新到 TypeScript
- 使用 React 18+ 特性提升性能

## 版本升级路径

### React 16 → 17 → 18

**各版本中的破坏性变更：**

**React 17：**

- 事件委托变更
- 无事件池
- 效果清理时机
- JSX 转换（无需 React 导入）

**React 18：**

- 自动批处理
- 并发渲染
- StrictMode 变更（双重调用）
- 新的根 API
- 服务器端 Suspense

## 类组件到 Hooks 的迁移

### 状态管理

```javascript
// 之前：类组件
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      count: 0,
      name: "",
    };
  }

  increment = () => {
    this.setState({ count: this.state.count + 1 });
  };

  render() {
    return (
      <div>
        <p>计数：{this.state.count}</p>
        <button onClick={this.increment}>增加</button>
      </div>
    );
  }
}

// 之后：使用 Hooks 的函数组件
function Counter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState("");

  const increment = () => {
    setCount(count + 1);
  };

  return (
    <div>
      <p>计数：{count}</p>
      <button onClick={increment}>增加</button>
    </div>
  );
}
```

### 生命周期方法到 Hooks

```javascript
// 之前：生命周期方法
class DataFetcher extends React.Component {
  state = { data: null, loading: true };

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.id !== this.props.id) {
      this.fetchData();
    }
  }

  componentWillUnmount() {
    this.cancelRequest();
  }

  fetchData = async () => {
    const data = await fetch(`/api/${this.props.id}`);
    this.setState({ data, loading: false });
  };

  cancelRequest = () => {
    // 清理
  };

  render() {
    if (this.state.loading) return <div>加载中...</div>;
    return <div>{this.state.data}</div>;
  }
}

// 之后：useEffect Hook
function DataFetcher({ id }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        const response = await fetch(`/api/${id}`);
        const result = await response.json();

        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      } catch (error) {
        if (!cancelled) {
          console.error(error);
        }
      }
    };

    fetchData();

    // 清理函数
    return () => {
      cancelled = true;
    };
  }, [id]); // id 变化时重新运行

  if (loading) return <div>加载中...</div>;
  return <div>{data}</div>;
}
```

### Context 和 HOCs 到 Hooks

```javascript
// 之前：Context 消费者和 HOC
const ThemeContext = React.createContext();

class ThemedButton extends React.Component {
  static contextType = ThemeContext;

  render() {
    return (
      <button style={{ background: this.context.theme }}>
        {this.props.children}
      </button>
    );
  }
}

// 之后：useContext Hook
function ThemedButton({ children }) {
  const { theme } = useContext(ThemeContext);

  return <button style={{ background: theme }}>{children}</button>;
}

// 之前：用于数据获取的 HOC
function withUser(Component) {
  return class extends React.Component {
    state = { user: null };

    componentDidMount() {
      fetchUser().then((user) => this.setState({ user }));
    }

    render() {
      return <Component {...this.props} user={this.state.user} />;
    }
  };
}

// 之后：自定义 Hook
function useUser() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser().then(setUser);
  }, []);

  return user;
}

function UserProfile() {
  const user = useUser();
  if (!user) return <div>加载中...</div>;
  return <div>{user.name}</div>;
}
```

## React 18 并发特性

### 新的根 API

```javascript
// 之前：React 17
import ReactDOM from "react-dom";

ReactDOM.render(<App />, document.getElementById("root"));

// 之后：React 18
import { createRoot } from "react-dom/client";

const root = createRoot(document.getElementById("root"));
root.render(<App />);
```

### 自动批处理

```javascript
// React 18：所有更新都会批处理
function handleClick() {
  setCount((c) => c + 1);
  setFlag((f) => !f);
  // 只会触发一次重渲染（批处理）
}

// 即使在异步中：
setTimeout(() => {
  setCount((c) => c + 1);
  setFlag((f) => !f);
  // React 18 中仍然会批处理！
}, 1000);

// 如需退出批处理
import { flushSync } from "react-dom";

flushSync(() => {
  setCount((c) => c + 1);
});
// 此时触发重渲染
setFlag((f) => !f);
// 另一次重渲染
```

### 过渡效果

```javascript
import { useState, useTransition } from "react";

function SearchResults() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // 紧急：立即更新输入
    setQuery(e.target.value);

    // 非紧急：更新结果（可以被中断）
    startTransition(() => {
      setResults(searchResults(e.target.value));
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <Spinner />}
      <Results data={results} />
    </>
  );
}
```

### 用于数据获取的 Suspense

```javascript
import { Suspense } from "react";

// 基于资源的获取数据（使用 React 18）
const resource = fetchProfileData();

function ProfilePage() {
  return (
    <Suspense fallback={<Loading />}>
      <ProfileDetails />
      <Suspense fallback={<Loading />}>
        <ProfileTimeline />
      </Suspense>
    </Suspense>
  );
}

function ProfileDetails() {
  // 如果数据未就绪，这里会挂起
  const user = resource.user.read();
  return <h1>{user.name}</h1>;
}

function ProfileTimeline() {
  const posts = resource.posts.read();
  return <Timeline posts={posts} />;
}
```

## 其他模式和模板

更详细的模板和实例说明位于 `references/details.md`。阅读该文件以获取完整的模式库。
