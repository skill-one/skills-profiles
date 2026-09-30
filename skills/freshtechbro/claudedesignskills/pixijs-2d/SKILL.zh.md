---
name: pixijs-2d
description: 快速、轻量级的2D渲染引擎，用于创建交互式图形、粒子效果和基于WebGL/WebGPU的canvas应用程序。在构建2D游戏、粒子系统、交互式canvas、精灵动画或3D场景上的UI叠加层时使用此技能。在涉及PixiJS、2D渲染、精灵表、粒子效果、滤镜或高性能canvas图形的任务上触发。作为Canvas2D的替代方案，支持WebGL加速渲染数千个精灵，实现60 FPS。
---

# PixiJS 2D 渲染技巧

一个快速、轻量级的 2D 渲染引擎，用于使用 WebGL/WebGPU 创建交互式图形、粒子效果和基于 canvas 的应用程序。

---

## 何时使用此技巧

当你遇到以下情况时，请触发此技巧：
- "创建 2D 粒子效果" 或 "动画粒子"
- "2D 图标动画" 或 "图标表处理"
- "交互式 canvas 图形" 或 "2D 游戏"
- "3D 场景上的 UI 叠加层" 或 "HUD 层"
- "按程序绘制形状" 或 "矢量图形 API"
- "优化渲染性能" 或 "成千上万的图标"
- "应用视觉滤镜" 或 "模糊/置换效果"
- "轻量级 2D 引擎" 或 "Canvas2D 的替代方案"

**使用 PixiJS 进行**：高性能 2D 渲染（高达 100,000+ 个图标）、粒子系统、交互式 UI、2D 游戏、WebGL 加速的数据可视化。

**不适用于**：3D 图形（使用 Three.js/R3F）、简单动画（使用 Motion/GSAP）、基本的 DOM 操作。

---

## 核心概念

### 1. 应用程序 & 渲染器

PixiJS 应用程序的入口点：

```javascript
import { Application } from 'pixi.js';

const app = new Application();

await app.init({
  width: 800,
  height: 600,
  backgroundColor: 0x1099bb,
  antialias: true,  // 平滑边缘
  resolution: window.devicePixelRatio || 1
});

document.body.appendChild(app.canvas);
```

**关键属性**：
- `app.stage`：所有显示对象的根容器
- `app.renderer`：WebGL/WebGPU 渲染器实例
- `app.ticker`：动画的更新循环
- `app.screen`：Canvas 尺寸

---

### 2. 图标 & 纹理

从图像加载的核心视觉元素：

```javascript
import { Assets, Sprite } from 'pixi.js';

// 加载纹理
const texture = await Assets.load('path/to/image.png');

// 创建图标
const sprite = new Sprite(texture);
sprite.anchor.set(0.5);  // 中心枢轴
sprite.position.set(400, 300);
sprite.scale.set(2);  // 2x 缩放
sprite.rotation = Math.PI / 4;  // 45 度
sprite.alpha = 0.8;  // 80% 透明度
sprite.tint = 0xff0000;  // 红色滤镜

app.stage.addChild(sprite);
```

**快速创建**：
```javascript
const sprite = Sprite.from('path/to/image.png');
```

---

### 3. 图形 API

按程序绘制矢量形状：

```javascript
import { Graphics } from 'pixi.js';

const graphics = new Graphics();

// 矩形
graphics.rect(50, 50, 100, 100).fill('blue');

// 带描边的圆形
graphics.circle(200, 100, 50).fill('red').stroke({ width: 2, color: 'white' });

// 复杂路径
graphics
  .moveTo(300, 100)
  .lineTo(350, 150)
  .lineTo(250, 150)
  .closePath()
  .fill({ color: 0x00ff00, alpha: 0.5 });

app.stage.addChild(graphics);
```

**SVG 支持**：
```javascript
graphics.svg('<svg><path d="M 100 350 q 150 -300 300 0" /></svg>');
```

---

### 4. ParticleContainer

渲染成千上万个图标的优化容器：

```javascript
import { ParticleContainer, Particle, Texture } from 'pixi.js';

const texture = Texture.from('particle.png');

const container = new ParticleContainer({
  dynamicProperties: {
    position: true,   // 允许位置更新
    scale: false,     // 静态缩放
    rotation: false,  // 静态旋转
    color: false      // 静态颜色
  }
});

// 添加 10,000 个粒子
for (let i = 0; i < 10000; i++) {
  const particle = new Particle({
    texture,
    x: Math.random() * 800,
    y: Math.random() * 600
  });

  container.addParticle(particle);
}

app.stage.addChild(container);
```

**性能**：对于静态属性，比普通 Container 快 10 倍。

---

### 5. 滤镜

使用 WebGL 着色器应用逐像素效果：

```javascript
import { BlurFilter, DisplacementFilter, ColorMatrixFilter } from 'pixi.js';

// 模糊
const blurFilter = new BlurFilter({ strength: 8, quality: 4 });
sprite.filters = [blurFilter];

// 多个滤镜
sprite.filters = [
  new BlurFilter({ strength: 4 }),
  new ColorMatrixFilter()  // 颜色转换
];

// 自定义滤镜区域以提高性能
sprite.filterArea = new Rectangle(0, 0, 200, 100);
```

**可用滤镜**：
- `BlurFilter`：高斯模糊
- `ColorMatrixFilter`：颜色转换（棕褐色、灰度等）
- `DisplacementFilter`：扭曲像素
- `AlphaFilter`：跨子级扁平化透明度
- `NoiseFilter`：随机颗粒效果
- `FXAAFilter`：抗锯齿

---

### 6. 文本渲染

使用样式显示文本：

```javascript
import { Text, BitmapText, TextStyle } from 'pixi.js';

// 标准文本
const style = new TextStyle({
  fontFamily: 'Arial',
  fontSize: 36,
  fill: '#ffffff',
  stroke: { color: '#000000', width: 4 },
  filters: [new BlurFilter()]  // 将滤镜烘焙到纹理中
});

const text = new Text({ text: 'Hello PixiJS!', style });
text.position.set(100, 100);

// BitmapText（用于动态文本更快）
const bitmapText = new BitmapText({
  text: 'Score: 0',
  style: { fontFamily: 'MyBitmapFont', fontSize: 24 }
});
```

**性能技巧**：使用 `BitmapText` 用于频繁变化的文本（分数、计数器）。

---

## 常见模式

### 模式 1：基本交互式图标

```javascript
import { Application, Assets, Sprite } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const texture = await Assets.load('bunny.png');
const bunny = new Sprite(texture);

bunny.anchor.set(0.5);
bunny.position.set(400, 300);
bunny.eventMode = 'static';  // 启用交互性
bunny.cursor = 'pointer';

// 事件
bunny.on('pointerdown', () => {
  bunny.scale.set(1.2);
});

bunny.on('pointerup', () => {
  bunny.scale.set(1.0);
});

bunny.on('pointerover', () => {
  bunny.tint = 0xff0000;  // 悬停时变红
});

bunny.on('pointerout', () => {
  bunny.tint = 0xffffff;  // 重置
});

app.stage.addChild(bunny);

// 动画循环
app.ticker.add((ticker) => {
  bunny.rotation += 0.01 * ticker.deltaTime;
});
```

---

### 模式 2：使用 Graphics 绘制

```javascript
import { Graphics, Application } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const graphics = new Graphics();

// 带渐变的矩形
graphics.rect(50, 50, 200, 100).fill({
  color: 0x3399ff,
  alpha: 0.8
});

// 带描边的圆形
graphics.circle(400, 300, 80)
  .fill('yellow')
  .stroke({ width: 4, color: 'orange' });

// 星形
graphics.star(600, 300, 5, 50, 0).fill({ color: 0xffdf00, alpha: 0.9 });

// 自定义路径
graphics
  .moveTo(100, 400)
  .bezierCurveTo(150, 300, 250, 300, 300, 400)
  .stroke({ width: 3, color: 'white' });

// 洞
graphics
  .rect(450, 400, 150, 100).fill('red')
  .beginHole()
  .circle(525, 450, 30)
  .endHole();

app.stage.addChild(graphics);

// 动态绘制（动画）
app.ticker.add(() => {
  graphics.clear();

  const time = Date.now() * 0.001;
  const x = 400 + Math.cos(time) * 100;
  const y = 300 + Math.sin(time) * 100;

  graphics.circle(x, y, 20).fill('cyan');
});
```

---

### 模式 3：使用 ParticleContainer 的粒子系统

```javascript
import { Application, ParticleContainer, Particle, Texture } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600, backgroundColor: 0x000000 });
document.body.appendChild(app.canvas);

const texture = Texture.from('spark.png');

const particles = new ParticleContainer({
  dynamicProperties: {
    position: true,  // 每帧更新位置
    scale: true,     // 通过缩放淡出
    rotation: true,  // 旋转粒子
    color: false     // 静态颜色
  }
});

const particleData = [];

// 创建粒子
for (let i = 0; i < 5000; i++) {
  const particle = new Particle({
    texture,
    x: 400,
    y: 300,
    scaleX: 0.5,
    scaleY: 0.5
  });

  particles.addParticle(particle);

  particleData.push({
    particle,
    vx: (Math.random() - 0.5) * 5,
    vy: (Math.random() - 0.5) * 5 - 2,  // 轻微向上偏移
    life: 1.0
  });
}

app.stage.addChild(particles);

// 更新循环
app.ticker.add((ticker) => {
  particleData.forEach(data => {
    // 物理
    data.particle.x += data.vx * ticker.deltaTime;
    data.particle.y += data.vy * ticker.deltaTime;
    data.vy += 0.1 * ticker.deltaTime;  // 重力

    // 淡出
    data.life -= 0.01 * ticker.deltaTime;
    data.particle.scaleX = data.life * 0.5;
    data.particle.scaleY = data.life * 0.5;

    // 重置粒子
    if (data.life <= 0) {
      data.particle.x = 400;
      data.particle.y = 300;
      data.vx = (Math.random() - 0.5) * 5;
      data.vy = (Math.random() - 0.5) * 5 - 2;
      data.life = 1.0;
    }
  });
});
```

---

### 模式 4：应用滤镜

```javascript
import { Application, Sprite, Assets, BlurFilter, DisplacementFilter } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const texture = await Assets.load('photo.jpg');
const photo = new Sprite(texture);
photo.position.set(100, 100);

// 模糊滤镜
const blurFilter = new BlurFilter({ strength: 5, quality: 4 });

// 置换滤镜（波浪效果）
const displacementTexture = await Assets.load('displacement.jpg');
const displacementSprite = Sprite.from(displacementTexture);
const displacementFilter = new DisplacementFilter({
  sprite: displacementSprite,
  scale: 50
});

// 应用多个滤镜
photo.filters = [blurFilter, displacementFilter];

// 使用 filterArea 优化
photo.filterArea = new Rectangle(0, 0, photo.width, photo.height);

app.stage.addChild(photo);

// 动置换
app.ticker.add((ticker) => {
  displacementSprite.x += 1 * ticker.deltaTime;
  displacementSprite.y += 0.5 * ticker.deltaTime;
});
```

---

### 模式 5：使用着色器创建自定义滤镜

```javascript
import { Filter, GlProgram } from 'pixi.js';

const vertex = `
  in vec2 aPosition;
  out vec2 vTextureCoord;

  uniform vec4 uInputSize;
  uniform vec4 uOutputFrame;
  uniform vec4 uOutputTexture;

  vec4 filterVertexPosition() {
    vec2 position = aPosition * uOutputFrame.zw + uOutputFrame.xy;
    position.x = position.x * (2.0 / uOutputTexture.x) - 1.0;
    position.y = position.y * (2.0*uOutputTexture.z / uOutputTexture.y) - uOutputTexture.z;
    return vec4(position, 0.0, 1.0);
  }

  vec2 filterTextureCoord() {
    return aPosition * (uOutputFrame.zw * uInputSize.zw);
  }

  void main() {
    gl_Position = filterVertexPosition();
    vTextureCoord = filterTextureCoord();
  }
`;

const fragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uTime;

  void main() {
    vec2 uv = vTextureCoord;

    // 波浪扭曲
    float wave = sin(uv.y * 10.0 + uTime) * 0.05;
    vec4 color = texture(uTexture, vec2(uv.x + wave, uv.y));

    gl_FragColor = color;
  }
`;

const customFilter = new Filter({
  glProgram: new GlProgram({ fragment, vertex }),
  resources: {
    timeUniforms: {
      uTime: { value: 0.0, type: 'f32' }
    }
  }
});

sprite.filters = [customFilter];

// 更新 uniform
app.ticker.add((ticker) => {
  customFilter.resources.timeUniforms.uniforms.uTime += 0.04 * ticker.deltaTime;
});
```

---

### 模式 6：图标表动画

```javascript
import { Application, Assets, AnimatedSprite } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

// 加载图标表
await Assets.load('spritesheet.json');

// 从帧创建动画
const frames = [];
for (let i = 0; i < 10; i++) {
  frames.push(Texture.from(`frame_${i}.png`));
}

const animation = new AnimatedSprite(frames);
animation.anchor.set(0.5);
animation.position.set(400, 300);
animation.animationSpeed = 0.16;  // ~10 FPS
animation.play();

app.stage.addChild(animation);

// 控制播放
animation.stop();
animation.gotoAndPlay(0);
animation.onComplete = () => {
  console.log('动画完成!');
};
```

---

### 模式 7：对象池化以提高性能

```javascript
class SpritePool {
  constructor(texture, initialSize = 100) {
    this.texture = texture;
    this.available = [];
    this.active = [];

    // 预创建图标
    for (let i = 0; i < initialSize; i++) {
      this.createSprite();
    }
  }

  createSprite() {
    const sprite = new Sprite(this.texture);
    sprite.visible = false;
    this.available.push(sprite);
    return sprite;
  }

  spawn(x, y) {
    let sprite = this.available.pop();

    if (!sprite) {
      sprite = this.createSprite();
    }

    sprite.position.set(x, y);
    sprite.visible = true;
    this.active.push(sprite);

    return sprite;
  }

  despawn(sprite) {
    sprite.visible = false;
    const index = this.active.indexOf(sprite);

    if (index > -1) {
      this.active.splice(index, 1);
      this.available.push(sprite);
    }
  }

  reset() {
    this.active.forEach(sprite => {
      sprite.visible = false;
      this.available.push(sprite);
    });
    this.active = [];
  }
}

// 使用
const bulletTexture = Texture.from('bullet.png');
const bulletPool = new SpritePool(bulletTexture, 50);

// 生成子弹
const bullet = bulletPool.spawn(100, 200);
app.stage.addChild(bullet);

// 2 秒后销毁
setTimeout(() => {
  bulletPool.despawn(bullet);
}, 2000);
```

---

## 集成模式

### React 集成

```jsx
import { useEffect, useRef } from 'react';
import { Application } from 'pixi.js';

function PixiCanvas() {
  const canvasRef = useRef(null);
  const appRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      const app = new Application();

      await app.init({
        width: 800,
        height: 600,
        backgroundColor: 0x1099bb
      });

      canvasRef.current.appendChild(app.canvas);
      appRef.current = app;

      // 设置场景
      // ... 添加图标、图形等
    };

    init();

    return () => {
      if (appRef.current) {
        appRef.current.destroy(true, { children: true });
      }
    };
  }, []);

  return <div ref={canvasRef} />;
}
```

---

### Three.js 叠加层（2D UI 在 3D 上）

```javascript
import * as THREE from 'three';
import { Application, Sprite, Text } from 'pixi.js';

// Three.js 场景
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight);
const renderer = new THREE.WebGLRenderer();
document.body.appendChild(renderer.domElement);

// PixiJS 叠加层
const pixiApp = new Application();
await pixiApp.init({
  width: window.innerWidth,
  height: window.innerHeight,
  backgroundAlpha: 0  // 透明背景
});

pixiApp.canvas.style.position = 'absolute';
pixiApp.canvas.style.top = '0';
pixiApp.canvas.style.left = '0';
pixiApp.canvas.style.pointerEvents = 'none';  // 可点击穿透
document.body.appendChild(pixiApp.canvas);

// 添加 UI 元素
const scoreText = new Text({ text: 'Score: 0', style: { fontSize: 24, fill: 'white' } });
scoreText.position.set(20, 20);
pixiApp.stage.addChild(scoreText);

// 渲染循环
function animate() {
  requestAnimationFrame(animate);

  renderer.render(scene, camera);  // 3D 场景
  pixiApp.renderer.render(pixiApp.stage);  // 2D 叠加层
}

animate();
```

---

## 性能最佳实践

### 1. 使用 ParticleContainer 处理大量图标

```javascript
// 不使用：普通 Container（1000+ 图标慢）
const container = new Container();
for (let i = 0; i < 10000; i++) {
  container.addChild(new Sprite(texture));
}

// 使用：ParticleContainer（10 倍更快）
const particles = new ParticleContainer({
  dynamicProperties: { position: true }
});
for (let i = 0; i < 10000; i++) {
  particles.addParticle(new Particle({ texture }));
}
```

---

### 2. 优化滤镜使用

```javascript
// 设置 filterArea 以避免运行时测量
sprite.filterArea = new Rectangle(0, 0, 200, 100);

// 不需要时释放滤镜
sprite.filters = null;

// 在创建时将滤镜烘焙到纹理
const style = new TextStyle({
  filters: [new BlurFilter()]  // 在纹理创建时应用一次
});
```

---

### 3. 管理纹理内存

```javascript
// 完成时销毁纹理
texture.destroy();

// 延迟批量销毁以防止帧率下降
textures.forEach((tex, i) => {
  setTimeout(() => tex.destroy(), Math.random() * 100);
});
```

---

### 4. 为离屏对象启用剔除

```javascript
sprite.cullable = true;  // 如果在视口外则跳过渲染

// 使用CullerPlugin
import { CullerPlugin } from 'pixi.js';
```

---

### 5. 将静态图形缓存为位图

```javascript
// 将复杂图形转换为纹理以加快渲染速度
const complexShape = new Graphics();
// ... 绘制许多图形

complexShape.cacheAsBitmap = true;  // 一次性渲染到位图纹理
```

---

### 6. 优化渲染器设置

```javascript
const app = new Application();
await app.init({
  antialias: false,  // 在移动设备上禁用以提升性能
  resolution: 1,     // 在低端设备上降低分辨率
  autoDensity: true
});
```

---

### 7. 使用BitmapText处理动态文本

```javascript
// 不要：标准Text（更新开销大）
const text = new Text({ text: `Score: ${score}` });
app.ticker.add(() => {
  text.text = `Score: ${++score}`;  // 每帧重新渲染纹理
});

// 推荐：BitmapText（速度更快）
const bitmapText = new BitmapText({ text: `Score: ${score}` });
app.ticker.add(() => {
  bitmapText.text = `Score: ${++score}`;
});
```

---

## 常见陷阱

### 陷阱1：未销毁对象

**问题**：未释放的GPU资源导致内存泄漏。

**解决方案**:
```javascript
// 始终销毁精灵和纹理
sprite.destroy({ children: true, texture: true, baseTexture: true });

// 销毁滤镜
sprite.filters = null;

// 销毁图形
graphics.destroy();
```

---

### 陷阱2：更新静态ParticleContainer属性

**问题**：当`dynamicProperties.scale = false`时，修改`scale`无效。

**解决方案**:
```javascript
const container = new ParticleContainer({
  dynamicProperties: {
    position: true,
    scale: true,  // 如需更新请启用
    rotation: true,
    color: true
  }
});

// 如果属性静态但需要修改，请调用update:
container.update();
```

---

### 陷阱3：过度使用滤镜

**问题**：滤镜开销大，过多使用会导致性能问题。

**解决方案**:
```javascript
// 限制滤镜使用
sprite.filters = [blurFilter];  // 最多1-2个滤镜

// 使用filterArea限制处理范围
sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);

// 可能时将滤镜烘焙到位图纹理
const filteredTexture = renderer.filters.generateFilteredTexture({
  texture,
  filters: [blurFilter]
});
```

---

### 陷阱4：频繁更新文本

**问题**：更新文本会每次重新生成纹理。

**解决方案**:
```javascript
// 使用BitmapText处理频繁变化的文本
const bitmapText = new BitmapText({ text: 'Score: 0' });

// 降低分辨率以减少内存占用
text.resolution = 1;  // 低于设备像素比
```

---

### 陷阱5：未重绘的Graphics.clear()

**问题**：调用`clear()`会清除所有几何图形但不会自动重绘。

**解决方案**:
```javascript
graphics.clear();  // 清除所有图形

// 绘制新图形
graphics.rect(0, 0, 100, 100).fill('blue');
```

---

### 陷阱6：未使用资源加载

**问题**：从URL创建精灵会导致异步问题。

**解决方案**:
```javascript
// 不要:
const sprite = Sprite.from('image.png');  // 可能异步加载

// 推荐:
const texture = await Assets.load('image.png');
const sprite = new Sprite(texture);
```

---

## 资源

- **官网**：https://pixijs.com
- **API文档**：https://pixijs.download/release/docs/
- **示例**：https://pixijs.io/examples/
- **GitHub**：https://github.com/pixijs/pixijs
- **滤镜库**：@pixi/filter-* 包
- **社区**：https://github.com/pixijs/pixijs/discussions

---

## 相关技能

- **threejs-webgl**：用于3D图形；PixiJS可提供2D UI叠加层
- **gsap-scrolltrigger**：用于滚动时动画化PixiJS属性
- **motion-framer**：用于React组件动画与PixiJS画布结合
- **react-three-fiber**：相似的React集成模式

---

## 总结

PixiJS擅长高性能2D渲染，支持WebGL加速。主要优势：

1. **性能**：可渲染10万+精灵并保持60 FPS
2. **ParticleContainer**：静态属性处理速度提升10倍
3. **滤镜**：基于WebGL的视觉特效
4. **图形API**：直观的矢量绘图
5. **资源管理**：强大的纹理和精灵表处理

适用于粒子系统、2D游戏、数据可视化以及需要高性能的交互式画布应用。
