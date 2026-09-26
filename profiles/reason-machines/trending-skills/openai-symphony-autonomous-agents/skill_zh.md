# OpenAI 交响乐

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

交响乐将项目工作转化为隔离的、自主的执行运行，使团队能够**管理工作**而不是**监督编码代理**。与其看着代理编码，你定义任务（例如在 Linear 中），交响乐会生成代理来完成这些任务，提供工作证明（CI 状态、PR 审查、演示视频），并自动合并 PR。

---

## 交响乐的功能

- 监控工作追踪器（例如 Linear）中的任务
- 每个任务生成隔离的代理运行（使用 Codex 或类似工具）
- 每个代理实现任务、打开 PR 并提供工作证明
- 工程师审查结果，而不是代理会话
- 在使用 [ Harness 工程](https://openai.com/index/harness-engineering/) 的代码库中效果最佳

---

## 安装选项

### 选项 1：让代理来构建它

将以下提示粘贴到 Claude Code、Cursor 或 Codex 中：

```
根据以下规范实现 Symphony：
https://github.com/openai/symphony/blob/main/SPEC.md
```

### 选项 2：使用 Elixir 参考实现

```bash
git clone https://github.com/openai/symphony.git
cd symphony/elixir
```

遵循 `elixir/README.md`，或者让代理：

```
根据 https://github.com/openai/symphony/blob/main/elixir/README.md 为我的仓库设置 Symphony
```

---

## Elixir 参考实现设置

### 要求

- 已安装 Elixir + Mix
- OpenAI API 密钥（用于 Codex 代理）
- Linear API 密钥（如果使用 Linear 集成）
- GitHub 令牌（用于 PR 操作）

### 环境变量

```bash
export OPENAI_API_KEY="sk-..."           # OpenAI API 密钥用于 Codex
export LINEAR_API_KEY="lin_api_..."      # Linear 集成
export GITHUB_TOKEN="ghp_..."           # GitHub PR 操作
export SYMPHONY_REPO_PATH="/path/to/repo"  # 目标仓库
```

### 安装依赖

```bash
cd elixir
mix deps.get
```

### 配置 (`elixir/config/config.exs`)

```elixir
import Config

config :symphony,
  openai_api_key: System.get_env("OPENAI_API_KEY"),
  linear_api_key: System.get_env("LINEAR_API_KEY"),
  github_token: System.get_env("GITHUB_TOKEN"),
  repo_path: System.get_env("SYMPHONY_REPO_PATH", "./"),
  poll_interval_ms: 30_000,
  max_concurrent_agents: 3
```

### 运行 Symphony

```bash
mix symphony.start
# 或者在 IEx 中进行开发
iex -S mix
```

---

## 核心概念

### 隔离的执行运行

每个任务都有自己的隔离运行：
- 每个任务一个新鲜的 git 分支
- 代理只在该分支上操作
- 运行之间没有共享状态
- 在 PR 合并前收集工作证明

### 工作证明

在 PR 被接受之前，交响乐会收集：
- CI/CD 管道状态
- PR 审查反馈
- 复杂性分析
- （可选）演示视频

---

## 关键 Elixir 模块和模式

### 启动 Symphony 监督器

```elixir
# 在你的 application.ex 或直接
defmodule MyApp.Application do
  use Application

  def start(_type, _args) do
    children = [
      Symphony.Supervisor
    ]
    Supervisor.start_link(children, strategy: :one_for_one)
  end
end
```

### 定义任务（Symphony Task 结构）

```elixir
defmodule Symphony.Task do
  @type t :: %__MODULE__{
    id: String.t(),
    title: String.t(),
    description: String.t(),
    source: :linear | :manual,
    status: :pending | :running | :completed | :failed,
    branch: String.t() | nil,
    pr_url: String.t() | nil,
    proof_of_work: map() | nil
  }

  defstruct [:id, :title, :description, :source,
             status: :pending, branch: nil,
             pr_url: nil, proof_of_work: nil]
end
```

### 启动代理运行

```elixir
defmodule Symphony.AgentRunner do
  @doc """
  为给定任务生成一个隔离的代理运行。
  每个运行都有自己的分支和 Codex 会话。
  """
  def run(task) do
    branch = "symphony/#{task.id}-#{slugify(task.title)}"

    with :ok <- Git.create_branch(branch),
         {:ok, result} <- Codex.implement(task, branch),
         {:ok, pr_url} <- GitHub.open_pr(branch, task),
         {:ok, proof} <- ProofOfWork.collect(pr_url) do
      {:ok, %{task | status: :completed, pr_url: pr_url, proof_of_work: proof}}
    else
      {:error, reason} -> {:error, reason}
    end
  end

  defp slugify(title) do
    title
    |> String.downcase()
    |> String.replace(~r/[^a-z0-9]+/, "-")
    |> String.trim("-")
  end
end
```

### Linear 集成 — 定时轮询任务

```elixir
defmodule Symphony.Linear.Poller do
  use GenServer

  @poll_interval Application.compile_env(:symphony, :poll_interval_ms, 30_000)

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def init(_opts) do
    schedule_poll()
    {:ok, %{processed_ids: MapSet.new()}}
  end

  def handle_info(:poll, state) do
    case Symphony.Linear.Client.fetch_todo_tasks() do
      {:ok, tasks} ->
        new_tasks = Enum.reject(tasks, &MapSet.member?(state.processed_ids, &1.id))
        Enum.each(new_tasks, &Symphony.AgentRunner.run/1)
        new_ids = Enum.reduce(new_tasks, state.processed_ids, &MapSet.put(&2, &1.id))
        schedule_poll()
        {:noreply, %{state | processed_ids: new_ids}}

      {:error, reason} ->
        Logger.error("Linear 轮询失败：#{inspect(reason)}")
        schedule_poll()
        {:noreply, state}
    end
  end

  defp schedule_poll do
    Process.send_after(self(), :poll, @poll_interval)
  end
end
```

### Linear API 客户端

```elixir
defmodule Symphony.Linear.Client do
  @linear_api "https://api.linear.app/graphql"

  def fetch_todo_tasks do
    query = """
    query {
      issues(filter: { state: { name: { eq: "Todo" } } }) {
        nodes {
          id
          title
          description
        }
      }
    }
    """

    case HTTPoison.post(@linear_api, Jason.encode!(%{query: query}), headers()) do
      {:ok, %{status_code: 200, body: body}} ->
        tasks =
          body
          |> Jason.decode!()
          |> get_in(["data", "issues", "nodes"])
          |> Enum.map(&to_task/1)
        {:ok, tasks}

      {:error, reason} ->
        {:error, reason}
    end
  end

  defp headers do
    [
      {"Authorization", System.get_env("LINEAR_API_KEY")},
      {"Content-Type", "application/json"}
    ]
  end

  defp to_task(%{"id" => id, "title" => title, "description" => desc}) do
    %Symphony.Task{id: id, title: title, description: desc, source: :linear}
  end
end
```

### 工作证明收集

```elixir
defmodule Symphony.ProofOfWork do
  @doc """
  在 PR 合并前收集工作证明。
  返回包含 CI 状态、审查反馈和复杂性的映射。
  """
  def collect(pr_url) do
    with {:ok, ci_status} <- wait_for_ci(pr_url),
         {:ok, reviews} <- fetch_reviews(pr_url),
         {:ok, complexity} <- analyze_complexity(pr_url) do
      {:ok, %{
        ci_status: ci_status,
        reviews: reviews,
        complexity: complexity,
        collected_at: DateTime.utc_now()
      }}
    end
  end

  defp wait_for_ci(pr_url, retries \\ 30) do
    case GitHub.get_pr_ci_status(pr_url) do
      {:ok, :success} -> {:ok, :success}
      {:ok, :pending} when retries > 0 ->
        Process.sleep(60_000)
        wait_for_ci(pr_url, retries - 1)
      {:ok, status} -> {:ok, status}
      {:error, reason} -> {:error, reason}
    end
  end

  defp fetch_reviews(pr_url), do: GitHub.get_pr_reviews(pr_url)
  defp analyze_complexity(pr_url), do: GitHub.get_pr_diff_complexity(pr_url)
end
```

---

## 实现 SPEC.md（自定义实现）

在另一种语言中构建交响乐时，规范定义了：

1. **任务源** — 定时轮询 Linear/GitHub/Jira 中的特定状态任务
2. **代理调用** — 使用 Codex（或其他代理）调用任务上下文
3. **隔离** — 每个运行在新鲜分支上，如果可能的话，容器化
4. **工作证明** — 在合并前进行 CI、审查和分析
5. **合并** — 自动合并或展示给工程师审批

伪代码中的最小实现循环：

```elixir
# 核心交响乐循环
def symphony_loop(state) do
  tasks = fetch_new_tasks(state.source)

  tasks
  |> Enum.filter(&(&1.status == :todo))
  |> Enum.each(fn task ->
    Task.async(fn ->
      branch = create_isolated_branch(task)
      invoke_agent(task, branch)         # Codex / Claude / 等.
      proof = collect_proof_of_work(branch)
      present_for_review(task, proof)
    end)
  end)

  Process.sleep(state.poll_interval)
  symphony_loop(state)
end
```

---

## 常见模式

### 限制并发代理运行

```elixir
defmodule Symphony.AgentPool do
  use GenServer

  @max_concurrent 3

  def start_link(_), do: GenServer.start_link(__MODULE__, %{running: 0, queue: []}, name: __MODULE__)

  def submit(task) do
    GenServer.cast(__MODULE__, {:submit, task})
  end

  def handle_cast({:submit, task}, %{running: n} = state) when n < @max_concurrent do
    spawn_agent(task)
    {:noreply, %{state | running: n + 1}}
  end

  def handle_cast({:submit, task}, %{queue: q} = state) do
    {:noreply, %{state | queue: q ++ [task]}}
  end

  def handle_info({:agent_done, _result}, %{running: n, queue: [next | rest]} = state) do
    spawn_agent(next)
    {:noreply, %{state | running: n, queue: rest}}
  end

  def handle_info({:agent_done, _result}, %{running: n} = state) do
    {:noreply, %{state | running: n - 1}}
  end

  defp spawn_agent(task) do
    parent = self()
    spawn(fn ->
      result = Symphony.AgentRunner.run(task)
      send(parent, {:agent_done, result})
    end)
  end
end
```

### 手动任务注入（无 Linear）

```elixir
# 在 IEx 或 Mix 任务中
Symphony.AgentPool.submit(%Symphony.Task{
  id: "manual-001",
  title: "为 API 添加速率限制",
  description: "在 /api/v1 端点实现令牌桶速率限制",
  source: :manual
})
```

---

## 故障排除

| 问题 | 可能原因 | 解决方法 |
|---|---|---|
| 代理未启动 | 缺少 `OPENAI_API_KEY` | 检查环境变量是否已导出 |
| Linear 任务未被检测到 | 线性状态过滤器错误 | 更新查询过滤器以匹配你的看板的状态名称 |
| PR 未打开 | 缺少 `GITHUB_TOKEN` 或仓库错误 | 验证令牌具有 `repo` 范围 |
| CI 永远未完成 | 超时太短 | 增加 `wait_for_ci/2` 中的 `retries` |
| 并发运行过多 | 默认池大小 | 在配置中设置 `max_concurrent_agents` |
| 分支冲突 | 代理重复使用分支名称 | 确保每个运行的任务 ID 是唯一的 |

### 调试模式

```elixir
# 在 config/dev.exs 中
config :symphony, log_level: :debug

# 或者在运行时
Logger.put_module_level(Symphony.AgentRunner, :debug)
Logger.put_module_level(Symphony.Linear.Poller, :debug)
```

---

## 资源

- [SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md) — 完整的交响乐规范
- [elixir/README.md](https://github.com/openai/symphony/blob/main/elixir/README.md) — Elixir 设置指南
- [Harness 工程](https://openai.com/index/harness-engineering/) — 先决条件方法论
- [Apache 2.0 许可证](https://github.com/openai/symphony/blob/main/LICENSE)
