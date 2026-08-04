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

## 从零部署

### 1. 获取代码

```powershell
git clone https://github.com/zyqzyq2266/bimanual-rh56-vision-control.git
cd bimanual-rh56-vision-control
```

也可以直接在 GitHub 页面点击 `Code` -> `Download ZIP`，解压后进入项目目录。

### 2. 创建 Python 环境并安装依赖

请先从 [Python 官网](https://www.python.org/downloads/windows/) 安装 Python 3.9
或更高版本，并在安装界面勾选 `Add Python to PATH`。如果终端中 `py` 命令不可用，
关闭并重新打开 PowerShell 后使用 `python` 替代下面命令中的 `py`。

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

如果电脑安装了多个 Python 版本，可将第一行改为 `py -3.12 -m venv .venv`。

### 3. 创建本机配置

```powershell
Copy-Item config.example.yaml config.yaml
```

打开 `config.yaml`，至少确认以下三项：

```yaml
serial_port: COM3   # 按设备管理器显示的实际端口修改
baudrate: 115200
hand_id: 1
```

默认模板使用 `motion_scale: 0.2`，仅用于首次小幅调试。完成实际方向和行程
校准后，才可以逐步提高该值。

### 4. 先验证摄像头，不控制硬件

```powershell
.\.venv\Scripts\python.exe -m hand_tracking.app --config config.yaml --no-serial
```

窗口中应能看到镜像画面和黄色手部关键点。按 `Esc` 退出。

### 5. 连接并校准灵巧手

1. 给灵巧手接通 24V 电源，并连接 USB-RS485。
2. 关闭因时上位机。上位机与本程序不能同时占用同一个 COM 口。
3. 确认手指周围无障碍物。
4. 启动实机控制：

```powershell
.\.venv\Scripts\python.exe -m hand_tracking.app --config config.yaml
```

5. 先缓慢活动一根手指。若实际方向相反，在 `config.yaml` 的
   `invert_axes` 中将对应轴设为 `true`，退出并重新启动。
6. 按 `Esc` 关闭窗口并释放串口。空格会发送 `open_pose`，首次调试前不要依赖
   它作为安全姿态。

Windows 用户也可以直接双击 `启动灵巧手跟随.bat`，它等价于第 5 步的命令。

## 项目结构

```text
yinshi-dexterous-hand/
├─ assets/hand_landmarker.task     # MediaPipe 手部识别模型
├─ hand_tracking/
│  ├─ app.py                       # 摄像头循环、窗口与程序入口
│  ├─ config.py                    # 配置读取和校验
│  ├─ mapper.py                    # 21 个关键点到六轴控制值的映射
│  ├─ rh56.py                      # RH56 串口协议
│  └─ safety.py                    # 限幅、死区和发送频率保护
├─ tests/                          # 自动化测试
├─ docs/PROJECT_REPORT.md          # 完整项目报告
├─ config.example.yaml             # 安全配置模板
├─ pyproject.toml                  # Python 依赖定义
└─ 启动灵巧手跟随.bat              # Windows 双击启动脚本
```

## 关键实现与标定过程

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

## 常见问题

| 现象 | 排查与解决 |
| --- | --- |
| 提示无法打开 COM 口 | 关闭因时上位机和其他串口工具，确认 `config.yaml` 中的端口正确。 |
| 摄像头黑屏 | 关闭占用摄像头的应用；尝试使用 `--camera 1` 选择另一摄像头。 |
| 识别不到某只手 | 保持手掌朝向摄像头、光线充足；镜像画面中左手为 `Right`，右手为 `Left`。 |
| 手指动作方向相反 | 仅调整对应的 `invert_axes` 项；一次只改一个轴。 |
| 手指运动过小或过大 | 从 `motion_scale: 0.2` 开始，完成方向验证后再逐步调高。 |
| 大拇指内外方向相反 | 仅翻转对应配置中 `invert_axes` 的第六项，然后重启程序。 |

## 测试

运行全部自动化测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

当前测试覆盖配置读取、六轴映射、反向逻辑、大拇指关节映射、RH56 串口数据帧、
安全过滤、丢失手部暂停和串口启动不自动发运动命令等行为。

## 如何高质量地向 AI 提问

灵巧手调试属于软硬件联合问题。描述越具体，AI 越容易给出能验证的修改，而不是
猜测。建议一次只调整一个问题，并提供下面四类信息：

1. **硬件事实**：型号、左/右手、COM 口、波特率、手部 ID、是否独立供电。
2. **复现步骤**：例如“握拳时其余四指已闭合，但大拇指仍向外伸”。
3. **证据**：控制窗口截图、上位机六轴读数、10 至 30 秒演示视频或报错全文。
4. **期望结果**：例如“大拇指应随握拳向掌心收拢，第六轴不应横向变化”。

可直接使用以下提问模板：

```text
我在 Windows 上使用 RH56DFTP-2L 左手，USB-RS485 为 COM3，115200，ID 1。
现象：{说明一个可重复的动作问题}。
我期望：{说明正确姿态或动作}。
我已尝试：{列出已修改的配置或代码}。
证据：{附上截图、视频或完整报错}。
请先判断可能的映射轴和原因，再给出一次只改一个变量的测试方案。
```

## 演示效果

![灵巧手手指跟随演示](demo.gif)

演示展示摄像头手部关键点识别与 RH56DFTP-2L 左手灵巧手的实时手指跟随效果。

[观看完整 MP4 演示](demo.mp4)

## 项目文档

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
