# 邀请链接与RSVP
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)的邀请链接与RSVP扩展。

## 概述

此技能添加了邀请链接生成和RSVP收集功能。管理员生成唯一的邀请码；嘉宾使用它们来提交响应，无需身份验证。

前提条件：您必须先遵循[扩展授权](../extension-authorization/SKILL.md)，因为此集成依赖于它。

# 后端

## 模块API

预制模块`mo:caffeineai-invite-links/invite-links-module.mo`提供低级别的邀请链接和RSVP状态管理。不要修改它。

```mo:caffeineai-invite-links/invite-links-module
module {
    public type RSVP = {
        name : Text;
        attending : Bool;
        timestamp : Time.Time;
        inviteCode : Text;
    };

    public type InviteCode = {
        code : Text;
        created : Time.Time;
        used : Bool;
    };

    public type InviteLinksSystemState = {
        var rsvps : Map.Map<Text, RSVP>;
        var inviteCodes : Map.Map<Text, InviteCode>;
    };

    public func initState() : InviteLinksSystemState;
    public func generateUUID(blob: Blob) : Text;
    public func generateInviteCode(state: InviteLinksSystemState, code: Text);
    public func getInviteCodes(state: InviteLinksSystemState) : [InviteCode];
    public func submitRSVP(state: InviteLinksSystemState, name: Text, attending: Bool, inviteCode: Text);
    public func getAllRSVPs(state: InviteLinksSystemState) : [RSVP];
}
```

## 在main.mo中设置

`include MixinInviteLinks(accessControlState, inviteState)` 必须放在`main.mo`中，而不是在自定义混合文件中。混合文件自动提供这些公共端点：

- `generateInviteCode()`
- `submitRSVP(name, attending, inviteCode)`
- `getAllRSVPs()`
- `getInviteCodes()`

不要重新声明任何这些函数。它们完全由`MixinInviteLinks`提供。

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinInviteLinks "mo:caffeineai-invite-links/MixinInviteLinks";
import InviteLinksModule "mo:caffeineai-invite-links/invite-links-module";

actor {
    let accessControlState : AccessControl.AccessControlState;
    include MixinAuthorization(accessControlState, null);
    let inviteState : InviteLinksModule.InviteLinksSystemState;
    include MixinInviteLinks(accessControlState, inviteState);

    // 在此处编写应用程序特定的代码。
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import InviteLinksModule "mo:caffeineai-invite-links/invite-links-module";

module {
    type NewActor = {
        accessControlState : AccessControl.AccessControlState;
        inviteState : InviteLinksModule.InviteLinksSystemState;
    };

    public func migration(_old : {}) : NewActor {
        {
            accessControlState = AccessControl.initState();
            inviteState = InviteLinksModule.initState();
        };
    };
};
```

# 前端

邀请链接和RSVP系统功能：

以下是如何在前端实现Internet Identity身份验证以及仅管理员可访问的邀请链接/RSVP的示例：

```typescript filepath=src/App.tsx
import AdminDashboard from './components/AdminDashboard';
import GuestRSVP from './components/GuestRSVP';
import LoginButton from './components/LoginButton';
import { useIsCurrentUserAdmin } from './hooks/useQueries';

export default function App() {
  const { data: isAdmin } = useIsCurrentUserAdmin();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-pink-100">
      <header className="p-4 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-bold text-purple-800">RSVP</h1>
          <LoginButton />
        </div>
      </header>
      <main className="max-w-7xl mx-auto p-4 mt-8">
        {isAdmin ? <AdminDashboard /> : <GuestRSVP />}
      </main>
    </div>
  );
}
```

```typescript filepath=src/components/GuestRSVP.tsx
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useSubmitRSVP } from '../hooks/useQueries';

export default function GuestRSVP() {
  const [name, setName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [attending, setAttending] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const submitRSVP = useSubmitRSVP();

  // 从URL自动填充邀请码
  useEffect(() => {
    const codeFromUrl = new URLSearchParams(window.location.search).get('code');
    if (codeFromUrl) setInviteCode(codeFromUrl);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    submitRSVP.mutate({ name, attending, inviteCode }, {
      onSuccess: () => setSubmitted(true)
    });
  };

  if (submitted) return <div>感谢！您的RSVP已提交。</div>;

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="您的姓名" required />
      <input value={inviteCode} onChange={(e) => setInviteCode(e.target.value)} placeholder="邀请码" required />
      <label>
        <input type="radio" checked={attending} onChange={() => setAttending(true)} />
        是，我会参加
      </label>
      <label>
        <input type="radio" checked={!attending} onChange={() => setAttending(false)} />
        否，我不能参加
      </label>
      <button type="submit" disabled={submitRSVP.isPending}>提交RSVP</button>
      {submitRSVP.error && <p>错误：{submitRSVP.error.message}</p>}
    </form>
  );
}
```

### 管理员仪表板
```typescript filepath=src/components/AdminDashboard.tsx
import { useGetAllRSVPs, useGetInviteCodes, useGenerateInviteCode } from '../hooks/useQueries';

export default function AdminDashboard() {
  const { data: rsvps } = useGetAllRSVPs();
  const { data: inviteCodes } = useGetInviteCodes();
  const generateInviteCode = useGenerateInviteCode();

  const unusedCodes = inviteCodes?.filter(code => !code.used) || [];
  const attendingCount = rsvps?.filter(rsvp => rsvp.attending).length || 0;

  return (
    <div>
      <div>
        <h2>统计信息</h2>
        <p>总RSVP数：{rsvps?.length || 0}</p>
        <p>参加人数：{attendingCount}</p>
        <p>未参加人数：{(rsvps?.length || 0) - attendingCount}</p>
      </div>

      <div>
        <h2>邀请码</h2>
        <button onClick={() => generateInviteCode.mutate()}>生成新码</button>
        {unusedCodes.map(code => (
          <div key={code.code}>
            <code>{code.code}</code>
            <button onClick={() => navigator.clipboard.writeText(`${window.location.origin}?code=${code.code}`)}>
              复制链接
            </button>
          </div>
        ))}
      </div>

      <div>
        <h2>RSVP</h2>
        <table>
          <thead><tr><th>姓名</th><th>状态</th><th>日期</th></tr></thead>
          <tbody>
            {rsvps?.map(rsvp => (
              <tr key={rsvp.inviteCode}>
                <td>{rsvp.name}</td>
                <td>{rsvp.attending ? '参加' : '未参加'}</td>
                <td>{new Date(Number(rsvp.timestamp / BigInt(1000000))).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

## 必需的钩子
- `useIsCurrentUserAdmin()` - 检查当前用户是否为管理员
- `useSubmitRSVP()` - 提交RSVP变异
- `useGetAllRSVPs()` - 获取所有RSVP（仅管理员）
- `useGetInviteCodes()` - 获取邀请码（仅管理员）  
- `useGenerateInviteCode()` - 生成新的邀请码（仅管理员）
- `useInternetIdentity()` - Internet Identity身份验证

## 主要功能
- URL参数解析用于邀请码（`?code=xyz`）
- 复制邀请链接到剪贴板功能
- 基于身份验证的管理员/嘉宾视图切换
- 基本表单验证和错误处理
- 时间戳转换用于显示
