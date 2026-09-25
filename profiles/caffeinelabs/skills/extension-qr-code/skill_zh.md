# 二维码扫描器
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的二维码扫描器扩展。

## 概述

此技能通过设备相机添加二维码扫描功能。基于相机组件并使用 jsQR 进行解码构建。

# 前端

要支持二维码扫描器：

有一个从 `@caffeinelabs/qr-code` 导入的预构建 React 钩子，不能修改。

```typescript filepath=@caffeinelabs/qr-code/src/hooks/useQRScanner.ts
import { RefObject } from 'react';
import { CameraConfig, CameraError } from '@caffeineai/camera';

export interface QRResult {
  // 解码后的二维码数据
  data: string;
  // 扫描二维码的时间戳
  timestamp: number;
}

export interface QRScannerConfig extends CameraConfig {
  // 多久扫描一次二维码（毫秒）（默认：100）
  scanInterval?: number;
  // 历史记录中保留的最大结果数量（默认：10）
  maxResults?: number;
  // 从 jsQR 库加载的 URL（默认：jsdelivr CDN）
  jsQRUrl?: string;
}

export interface UseQRScannerReturn {
  // 扫描的二维码数组（最新的在前）
  qrResults: QRResult[];
  // 当前是否正在扫描二维码
  isScanning: boolean;
  // 是否已加载 jsQR 库
  jsQRLoaded: boolean;
  
  // 相机状态（从 useCamera 传递）
  isActive: boolean;
  isSupported: boolean | null;
  error: CameraError | null;
  isLoading: boolean;
  currentFacingMode: 'user' | 'environment';
  
  // 启用相机并开始扫描 - 成功返回 true
  startScanning: () => Promise<boolean>;
  // 停止扫描和相机
  stopScanning: () => Promise<void>;
  // 切换相机朝向模式 - 成功返回 true
  switchCamera: () => Promise<boolean>;
  // 清除所有扫描结果
  clearResults: () => void;
  // 重置扫描器状态（停止扫描并清除结果）
  reset: () => void;
  // 出错后重试相机初始化 - 成功返回 true
  retry: () => Promise<boolean>;
  
  // 视频元素引用，用于相机预览
  videoRef: RefObject<HTMLVideoElement>;
  // 画布元素引用，用于二维码处理（可以隐藏）
  canvasRef: RefObject<HTMLCanvasElement>;
  
  // 计算状态
  // 扫描器是否准备好使用（jsQR 已加载且相机受支持）
  isReady: boolean;
  // 是否可以开始扫描（准备好 + 未加载中）
  canStartScanning: boolean;
}

export declare function useQRScanner(config?: QRScannerConfig): UseQRScannerReturn;
```

使用示例：

```typescript filepath=example.ts
import { useQRScanner } from '@caffeineai/qr-code';

function QRScannerComponent() {
    const { 
        qrResults,
        isScanning,
        isActive,
        isSupported,
        error,
        isLoading,
        canStartScanning,
        startScanning,
        stopScanning,
        switchCamera,
        clearResults,
        videoRef,
        canvasRef 
    } = useQRScanner({ 
        facingMode: 'environment',
        scanInterval: 100,
        maxResults: 5
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
                <button onClick={startScanning} disabled={!canStartScanning}>
                    开始扫描
                </button>
                <button onClick={stopScanning} disabled={isLoading || !isActive}>
                    停止扫描
                </button>
                {/* 仅在移动设备上显示切换相机 */}
                {/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) && (
                    <button onClick={switchCamera} disabled={isLoading || !isActive}>
                        切换相机
                    </button>
                )}
            </div>
            
            <div>
                <h3>结果 {qrResults.length > 0 && <button onClick={clearResults}>清除</button>}</h3>
                {qrResults.map(result => (
                    <div key={result.timestamp}>
                        <small>{new Date(result.timestamp).toLocaleTimeString()}</small>
                        <p>{result.data}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
```

在应用中正确显示二维码扫描器错误消息。
