# 相机
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的相机扩展。

## 概述

该技能通过预制的 React 钩子添加网页相机访问功能。支持拍照、切换相机和错误处理。

# 前端

要支持相机功能：

存在一个不可修改的预制的 React 钩子 `@caffeinelabs/camera/hooks/useCamera.ts`。

```typescript filepath=@caffeinelabs/camera/hooks/useCamera.ts
import { RefObject } from 'react';

export interface CameraConfig {
  // 相机朝向模式 - 'user' 表示前置相机，'environment' 表示后置相机
  facingMode?: 'user' | 'environment';
  // 理想的视频宽度和高度（像素）
  width?: number;
  height?: number;
  // 拍照的图像质量（0-1，其中 1 表示最高质量）
  quality?: number;
  format?: 'image/jpeg' | 'image/png' | 'image/webp';
}

export interface CameraError {
  type: 'permission' | 'not-supported' | 'not-found' | 'unknown' | 'timeout';
  message: string;
}

export interface UseCameraReturn {
  // 当前相机是否处于激活状态并正在流式传输
  isActive: boolean;
  // 当前浏览器是否支持相机（检查时为 null）
  isSupported: boolean | null;
  // 当前错误状态，如果有
  error: CameraError | null;
  // 相机是否正在初始化、启动、切换或停止
  isLoading: boolean;
  currentFacingMode: 'user' | 'environment';
  
  // 成功时返回 true
  startCamera: () => Promise<boolean>;
  stopCamera: () => Promise<void>;
  capturePhoto: () => Promise<File | null>;
  // 成功时返回 true
  switchCamera: () => (newFacingMode?: 'user' | 'environment') : Promise<boolean>;
  // 成功时返回 true
  retry: () => Promise<boolean>;
  
  // 用于相机预览的视频元素的引用
  videoRef: RefObject<HTMLVideoElement>;
  // 用于拍照的画布元素的引用（可以隐藏）
  canvasRef: RefObject<HTMLCanvasElement>;
}

export declare function useCamera(config?: CameraConfig): UseCameraReturn;
```

使用示例：

```
import { useCamera } from '@caffeineai/camera';

function CameraComponent() {
    const { 
        isActive, 
        isSupported, 
        error, 
        isLoading,
        startCamera, 
        stopCamera, 
        capturePhoto,
        switchCamera,
        videoRef, 
        canvasRef 
    } = useCamera({ 
        autoStart: true,
        facingMode: 'environment' 
    });

    if (isSupported === false) {
        return <div>相机不支持</div>;
    }

    return (
        <div>
            <video 
                ref={videoRef} 
                style={{ width: '100%', height: 'auto' }}
                playsInline
                muted
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            
            {error && <div>错误：{error.message}</div>}
            
            <div>
                <button onClick={startCamera} disabled={isLoading || isActive}>
                    启动相机
                </button>
                <button onClick={stopCamera} disabled={isLoading || !isActive}>
                    停止相机
                </button>
                <button onClick={switchCamera} disabled={isLoading || !isActive}>
                    切换相机
                </button>
                <button onClick={capturePhoto} disabled={!isActive}>
                    拍照
                </button>
            </div>
        </div>
    );
}
```

始终在相机预览中放置一个拍照按钮！
当用户打开相机时，始终显示相机预览
在桌面端，确保相机无法切换。只有 'environment' 是可用的。
在应用中正确显示相机错误消息。
直到相机完全初始化并准备好后，才使相机按钮可点击。
确保相机预览具有明确的非零尺寸（固定高度、min-height 或一个 aspect-ratio 包裹器），以防止其因布局而塌陷。
确保预览在不同屏幕尺寸下具有响应性（例如，宽度：100% 且具有稳定的宽高比）。
