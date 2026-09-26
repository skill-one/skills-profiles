# GSAP 动画技能

> **文件组织**：此技能采用拆分结构。高级模式请参考 `references/` 文件夹。

## 1. 概述

此技能为 JARVIS AI 助手 HUD 提供了 GSAP（GreenSock 动画平台）专业知识，用于创建流畅、专业的动画效果。

**风险等级**：低 - 动画库具有极小的安全表面

**主要应用场景**：
- HUD 面板进入/退出动画
- 状态指示器过渡动画
- 数据可视化动画
- 滚动触发效果
- 复杂时间轴序列

## 2. 核心职责

### 2.1 基本原则

1. **TDD 优先**：在实现动画前编写测试
2. **性能意识**：使用变换/透明度实现 GPU 加速，避免布局抖动
3. **清理需求**：组件卸载时始终销毁动画
4. **时间轴组织**：使用时间轴处理复杂序列
5. **缓动函数选择**：为 HUD 选择合适的缓动效果
6. **无障碍设计**：尊重减少运动偏好
7. **内存管理**：通过正确清理避免内存泄漏

## 2.5 TDD 实现工作流

### 第一步：先编写失败的测试

```typescript
// tests/animations/panel-animation.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { gsap } from 'gsap'
import HUDPanel from '~/components/HUDPanel.vue'

describe('HUDPanel 动画', () => {
  beforeEach(() => {
    // 模拟减少运动
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query
      }))
    })
  })

  afterEach(() => {
    // 验证清理
    gsap.globalTimeline.clear()
  })

  it('以正确属性动画面板进入', async () => {
    const wrapper = mount(HUDPanel)

    // 等待动画完成
    await new Promise(resolve => setTimeout(resolve, 600))

    const panel = wrapper.find('.hud-panel')
    expect(panel.exists()).toBe(true)
  })

  it('卸载时清理动画', async () => {
    const wrapper = mount(HUDPanel)
    const childCount = gsap.globalTimeline.getChildren().length

    await wrapper.unmount()

    // 所有动画应被销毁
    expect(gsap.globalTimeline.getChildren().length).toBeLessThan(childCount)
  })

  it('尊重减少运动偏好', async () => {
    // 模拟减少运动启用
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: true
    }))

    const wrapper = mount(HUDPanel)
    const panel = wrapper.find('.hud-panel').element

    // 应立即设置最终状态而不动画
    expect(gsap.getProperty(panel, 'opacity')).toBe(1)
  })
})
```

### 第二步：实现最小化通过测试

```typescript
// components/HUDPanel.vue - 实现动画逻辑
const animation = ref<gsap.core.Tween | null>(null)

onMounted(() => {
  if (!panelRef.value) return

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.set(panelRef.value, { opacity: 1 })
    return
  }

  animation.value = gsap.from(panelRef.value, {
    opacity: 0,
    y: 20,
    duration: 0.5
  })
})

onUnmounted(() => {
  animation.value?.kill()
})
```

### 第三步：遵循模式重构

```typescript
// 提取为可复用组合式 API
export function usePanelAnimation(elementRef: Ref<HTMLElement | null>) {
  const animation = ref<gsap.core.Tween | null>(null)

  const animate = () => {
    if (!elementRef.value) return

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      gsap.set(elementRef.value, { opacity: 1 })
      return
    }

    animation.value = gsap.from(elementRef.value, {
      opacity: 0,
      y: 20,
      duration: 0.5,
      ease: 'power2.out'
    })
  }

  onMounted(animate)
  onUnmounted(() => animation.value?.kill())

  return { animation }
}
```

### 第四步：运行完整验证

```bash
# 运行动画测试
npm test -- --grep "Animation"

# 检查内存泄漏
npm run test:memory

# 验证 60fps 性能
npm run test:performance
```

## 3. 技术栈与版本

### 3.1 推荐版本

| 包 | 版本 | 备注 |
|----|------|------|
| gsap | ^3.12.0 | 核心库 |
| @gsap/vue | ^3.12.0 | Vue 集成 |
| ScrollTrigger | 内置 | 滚动效果 |

### 3.2 Vue 集成

```typescript
// plugins/gsap.ts
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

export default defineNuxtPlugin(() => {
  gsap.registerPlugin(ScrollTrigger)

  return {
    provide: {
      gsap,
      ScrollTrigger
    }
  }
})
```

## 4. 实现模式

### 4.1 面板进入动画

```vue
<script setup lang="ts">
import { gsap } from 'gsap'
import { onMounted, onUnmounted, ref } from 'vue'

const panelRef = ref<HTMLElement | null>(null)
let animation: gsap.core.Tween | null = null

onMounted(() => {
  if (!panelRef.value) return

  // ✅ 检查减少运动偏好
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.set(panelRef.value, { opacity: 1 })
    return
  }

  animation = gsap.from(panelRef.value, {
    opacity: 0,
    y: 20,
    scale: 0.95,
    duration: 0.5,
    ease: 'power2.out'
  })
})

// ✅ 卸载时清理
onUnmounted(() => {
  animation?.kill()
})
</script>

<template>
  <div ref="panelRef" class="hud-panel">
    <slot />
  </div>
</template>
```

### 4.2 状态指示器动画

```typescript
// composables/useStatusAnimation.ts
import { gsap } from 'gsap'

export function useStatusAnimation(element: Ref<HTMLElement | null>) {
  const timeline = ref<gsap.core.Timeline | null>(null)

  const animateStatus = (status: string) => {
    if (!element.value) return

    timeline.value?.kill()

    timeline.value = gsap.timeline()

    switch (status) {
      case 'active':
        timeline.value
          .to(element.value, {
            scale: 1.2,
            duration: 0.2,
            ease: 'power2.out'
          })
          .to(element.value, {
            scale: 1,
            duration: 0.3,
            ease: 'elastic.out(1, 0.3)'
          })
        break

      case 'warning':
        timeline.value.to(element.value, {
          backgroundColor: '#f59e0b',
          boxShadow: '0 0 10px #f59e0b',
          duration: 0.3,
          repeat: 2,
          yoyo: true
        })
        break

      case 'error':
        timeline.value.to(element.value, {
          x: -5,
          duration: 0.05,
          repeat: 5,
          yoyo: true
        })
        break
    }
  }

  onUnmounted(() => {
    timeline.value?.kill()
  })

  return { animateStatus }
}
```

### 4.3 数据可视化动画

```vue
<script setup lang="ts">
import { gsap } from 'gsap'

const props = defineProps<{
  data: number[]
}>()

const barsRef = ref<HTMLElement[]>([])
let animations: gsap.core.Tween[] = []

watch(() => props.data, (newData) => {
  // 销毁之前的动画
  animations.forEach(a => a.kill())
  animations = []

  // 动画每个条形
  newData.forEach((value, index) => {
    const bar = barsRef.value[index]
    if (!bar) return

    const tween = gsap.to(bar, {
      height: `${value}%`,
      duration: 0.5,
      delay: index * 0.05,
      ease: 'power2.out'
    })

    animations.push(tween)
  })
}, { immediate: true })

onUnmounted(() => {
  animations.forEach(a => a.kill())
})
</script>

<template>
  <div class="flex items-end h-40 gap-1">
    <div
      v-for="(_, index) in data"
      :key="index"
      ref="barsRef"
      class="w-4 bg-jarvis-primary"
    />
  </div>
</template>
```

### 4.4 时间轴序列

```typescript
// 创建复杂的 HUD 启动序列
export function createStartupSequence(elements: {
  logo: HTMLElement
  panels: HTMLElement[]
  status: HTMLElement
}): gsap.core.Timeline {
  const tl = gsap.timeline({
    defaults: { ease: 'power2.out' }
  })

  // Logo 揭示
  tl.from(elements.logo, {
    opacity: 0,
    scale: 0,
    duration: 0.8,
    ease: 'back.out(1.7)'
  })

  // 面板交错进入
  tl.from(elements.panels, {
    opacity: 0,
    x: -30,
    stagger: 0.1,
    duration: 0.5
  }, '-=0.3')

  // 状态指示器
  tl.from(elements.status, {
    opacity: 0,
    y: 10,
    duration: 0.3
  }, '-=0.2')

  return tl
}
```

### 4.5 滚动触发动画

```vue
<script setup lang="ts">
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const sectionRef = ref<HTMLElement | null>(null)

onMounted(() => {
  if (!sectionRef.value) return

  gsap.from(sectionRef.value.querySelectorAll('.animate-item'), {
    scrollTrigger: {
      trigger: sectionRef.value,
      start: 'top 80%',
      end: 'bottom 20%',
      toggleActions: 'play none none reverse'
    },
    opacity: 0,
    y: 30,
    stagger: 0.1,
    duration: 0.5
  })
})

onUnmounted(() => {
  ScrollTrigger.getAll().forEach(trigger => trigger.kill())
})
</script>
```

## 5. 质量标准

### 5.1 性能

```typescript
// ✅ GOOD - 使用变换实现 GPU 加速
gsap.to(element, {
  x: 100,
  y: 50,
  rotation: 45,
  scale: 1.2
})

// ❌ BAD - 触发布局重新计算
gsap.to(element, {
  left: 100,
  top: 50,
  width: '120%'
})
```

### 5.2 无障碍设计

```typescript
// ✅ 尊重减少运动
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches

if (prefersReducedMotion) {
  gsap.set(element, { opacity: 1 })
} else {
  gsap.from(element, { opacity: 0, duration: 0.5 })
}
```

## 6. 性能模式

### 6.1 will-change 属性使用

```typescript
// 良好：动画前应用 will-change
const animatePanel = (element: HTMLElement) => {
  element.style.willChange = 'transform, opacity'

  gsap.to(element, {
    x: 100,
    opacity: 0.8,
    duration: 0.5,
    onComplete: () => {
      element.style.willChange = 'auto'
    }
  })
}

// 差：从不移除 will-change
const animatePanelBad = (element: HTMLElement) => {
  element.style.willChange = 'transform, opacity' // 内存泄漏！
  gsap.to(element, { x: 100, opacity: 0.8 })
}
```

### 6.2 变换与布局属性

```typescript
// 良好：使用变换（GPU 加速）
gsap.to(element, {
  x: 100,           // translateX
  y: 50,            // translateY
  scale: 1.2,       // scale
  rotation: 45,     // rotate
  opacity: 0.5      // opacity
})

// 差：布局触发属性（CPU，导致重排）
gsap.to(element, {
  left: 100,        // 触发布局
  top: 50,          // 触发布局
  width: '120%',    // 触发布局
  height: 200,      // 触发布局
  margin: 10        // 触发布局
})
```

### 6.3 时间轴重用

```typescript
// 良好：重用时间轴实例
const timeline = gsap.timeline({ paused: true })
timeline
  .to(element, { opacity: 1, duration: 0.3 })
  .to(element, { y: -20, duration: 0.5 })

// 按需播放/反转
const show = () => timeline.play()
const hide = () => timeline.reverse()

// 差：每次创建新时间轴
const showBad = () => {
  gsap.timeline()
    .to(element, { opacity: 1, duration: 0.3 })
    .to(element, { y: -20, duration: 0.5 })
}
```

### 6.4 ScrollTrigger 批量处理

```typescript
// 良好：批量 ScrollTrigger 动画
ScrollTrigger.batch('.animate-item', {
  onEnter: (elements) => {
    gsap.to(elements, {
      opacity: 1,
      y: 0,
      stagger: 0.1,
      overwrite: true
    })
  },
  onLeave: (elements) => {
    gsap.to(elements, {
      opacity: 0,
      y: -20,
      overwrite: true
    })
  }
})

// 差：每个元素单独的 ScrollTrigger
document.querySelectorAll('.animate-item').forEach(item => {
  gsap.to(item, {
    scrollTrigger: {
      trigger: item,
      start: 'top 80%'
    },
    opacity: 1,
    y: 0
  })
})
```

### 6.5 懒加载初始化

```typescript
// 良好：仅在需要时初始化动画
let panelAnimation: gsap.core.Timeline | null = null

const getPanelAnimation = () => {
  if (!panelAnimation) {
    panelAnimation = gsap.timeline({ paused: true })
      .from('.panel', { opacity: 0, y: 20 })
      .from('.panel-content', { opacity: 0, stagger: 0.1 })
  }
  return panelAnimation
}

const showPanel = () => getPanelAnimation().play()
const hidePanel = () => getPanelAnimation().reverse()

// 差：挂载时初始化所有动画
onMounted(() => {
  // 即使从未使用也会创建时间轴
  const animation1 = gsap.timeline().to('.panel1', { x: 100 })
  const animation2 = gsap.timeline().to('.panel2', { y: 100 })
  const animation3 = gsap.timeline().to('.panel3', { scale: 1.2 })
})
```

## 7. 测试与质量

### 7.1 动画测试

```typescript
describe('Panel 动画', () => {
  it('卸载时清理', async () => {
    const wrapper = mount(HUDPanel)
    await wrapper.unmount()

    // 不应保留任何活跃的 GSAP 动画
    expect(gsap.globalTimeline.getChildren().length).toBe(0)
  })
})
```

## 8. 常见错误与反模式

### 8.1 严重反模式

#### 绝对避免：跳过清理

```typescript
// ❌ 内存泄漏
onMounted(() => {
  gsap.to(element, { x: 100, duration: 1 })
})

// ✅ 正确清理
let tween: gsap.core.Tween

onMounted(() => {
  tween = gsap.to(element, { x: 100, duration: 1 })
})

onUnmounted(() => {
  tween?.kill()
})
```

#### 绝对避免：动画布局属性

```typescript
// ❌ BAD - 导致布局抖动
gsap.to(element, { width: 200, height: 100 })

// ✅ GOOD - 使用变换
gsap.to(element, { scaleX: 2, scaleY: 1 })
```

## 13. 实现前检查清单

### 第一阶段：编写代码前

- [ ] 为动画行为编写失败的测试
- [ ] 定义动画时序和缓动函数要求
- [ ] 确定需要 will-change 提示的元素
- [ ] 规划所有动画的清理策略
- [ ] 检查是否需要减少运动支持

### 第二阶段：实现过程中

- [ ] 仅使用变换/透明度（无布局属性）
- [ ] 存储动画引用以便清理
- [ ] 动画前应用 will-change，动画后移除
- [ ] 使用时间轴处理序列
- [ ] 批量处理 ScrollTrigger 动画
- [ ] 实现复杂动画的懒加载初始化

### 第三阶段：提交前

- [ ] 所有测试通过（npm test -- --grep "Animation"）
- [ ] 卸载时所有动画被清理
- [ ] 尊重减少运动偏好
- [ ] 无内存泄漏（使用开发者工具检查）
- [ ] 保持 60fps（使用性能监视器测试）
- [ ] 正确销毁 ScrollTrigger 实例

## 14. 总结

GSAP 为 JARVIS HUD 提供专业动画：

1. **清理**：卸载组件时始终销毁动画
2. **性能**：仅使用变换和透明度
3. **无障碍设计**：尊重减少运动偏好
4. **组织**：使用时间轴处理序列

**记住**：每个动画都必须被清理以防止内存泄漏。

---

**参考文献**：
- `references/advanced-patterns.md` - 复杂动画模式
