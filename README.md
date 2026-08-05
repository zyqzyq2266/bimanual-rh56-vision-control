# Bimanual RH56 Vision Control

使用一个电脑摄像头同时识别操作者的左手和右手，并通过两条独立 USB-RS485
连接实时控制两只因时 RH56DFTP-2L 灵巧手。

> 本项目用于学习、演示和基础人机交互验证。灵巧手会产生真实运动，首次
> 使用或更改标定参数时，请保持手指周围无障碍物，并从单根手指的小幅动作开始。

```mermaid
flowchart LR
    A[电脑摄像头] --> B[MediaPipe HandLandmarker]
    B --> C[21 个手部关键点]
    C --> D[六轴手势映射]
    D --> E[限幅 死区 频率过滤]
    E --> F[USB-RS485]
    F --> G[两只 RH56DFTP-2L 灵巧手]
```

## 功能

- 实时读取摄像头，并在画面中显示手部关键点和六轴目标值。
- 同时识别镜像画面中的物理左手和右手，并分别路由到 COM3、COM4。
- 分别跟随小拇指、无名指、中指和食指的弯曲动作。
- 使用大拇指关节夹角控制弯曲轴，并使用拇指根部相对掌骨的展开角控制旋转轴。
- 通过行程限幅、死区和发送频率限制，降低抖动和误动作风险。
- 提供 `--no-serial` 摄像头预览模式，以及 Windows 双击启动脚本。

## 硬件要求

| 项目 | 要求 |
| --- | --- |
| 灵巧手 | 两只因时 RH56DFTP-2L 灵巧手 |
| 电源 | 灵巧手独立 24V 电源 |
| 通信 | USB-RS485 转接器 |
| 摄像头 | Windows 可用的普通 USB 摄像头或内置摄像头 |
| 软件 | Windows 10/11、Python 3.9 或更高版本 |

本项目开发时使用的设备参数为 `COM3`、`115200`、手部 ID `1`。你的设备
可能不同，应在本地 `config.yaml` 中修改，**不要提交该文件**。

## Bimanual Setup

Create separate local configurations for the left and right hands:

```powershell
Copy-Item config.left.example.yaml config.left.yaml
Copy-Item config.right.example.yaml config.right.yaml
```

Preview both hands without opening COM ports:

```powershell
.\.venv\Scripts\python.exe -m hand_tracking.dual_app --left-config config.left.yaml --right-config config.right.yaml --no-serial
```

For hardware control, close the Inspire desktop controller, verify that both hands have clear space, then run:

```powershell
.\.venv\Scripts\python.exe -m hand_tracking.dual_app --left-config config.left.yaml --right-config config.right.yaml
```## 关键实现与标定过程

### 镜像双手识别

程序会镜像摄像头画面，便于操作者像照镜子一样活动双手。MediaPipe 在这种画面中
通常将物理左手标记为 `Right`、物理右手标记为 `Left`，程序据此分别路由到左右设备。

### 四指映射

四个手指各使用两个关节的夹角平均值计算弯曲量。硬件标定发现前四轴与视觉数值
方向相反，因此实际设备配置中使用前四轴反向。为使完整握拳达到足够行程，弯曲
增益设为 `13`，同时仍限制在 `0` 到 `1000`。

### 大拇指映射

第五轴通过大拇指 MCP-IP-指尖的关节夹角控制弯曲；第六轴通过拇指根部相对掌骨的
有符号展开角控制内外运动。两只灵巧手可分别用各自配置中的第六项 `invert_axes` 校准方向。


## Demo

https://github.com/user-attachments/assets/1f19b065-f330-492e-9e07-4d0c72f63753
## 双手同时跟随

双手模式使用同一个摄像头窗口和两条独立串口。镜像画面中，MediaPipe 通常把物理左手标记为 `Right`、物理右手标记为 `Left`，程序按下表固定路由：

| 摄像头中的物理手 | MediaPipe 标签 | 灵巧手 | 串口 |
| --- | --- | --- | --- |
| 左手 | `Right` | 左 RH56DFTP-2L | `COM3` |
| 右手 | `Left` | 右 RH56DFTP-2L | `COM4` |

先创建两份本机配置文件。它们不会被 Git 提交，便于保存各自的标定参数：

```powershell
Copy-Item config.left.example.yaml config.left.yaml
Copy-Item config.right.example.yaml config.right.yaml
```

首次只验证识别画面，不打开 COM3、COM4：

```powershell
.\.venv\Scripts\python.exe -m hand_tracking.dual_app --left-config config.left.yaml --right-config config.right.yaml --no-serial
```

确认两只手均能识别后，关闭因时上位机，确认手指周围无障碍物，再双击 `启动双手灵巧手跟随.bat`。按 `Space` 会给两只手分别发送各自配置中的 `open_pose`，按 `Esc` 同时退出并释放两个串口。

右手的轴方向、拇指行程和安全限位必须在 `config.right.yaml` 中单独标定。首次实机运行请维持 `motion_scale: 0.2`，每次只测试一根手指；不要直接复制左手的 `invert_axes`。

- [项目报告](docs/PROJECT_REPORT.md)：构建过程、问题、解决方法与最终成果。
- [代码](hand_tracking/)：可直接查看摄像头、映射、串口协议和安全模块实现。

## 许可证

本项目使用 [MIT License](LICENSE)。使用者需自行确认其灵巧手、驱动和第三方
软件的许可条款，并对实际硬件操作负责。
