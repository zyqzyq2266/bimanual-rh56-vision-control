# Bimanual RH56 Vision Control

浣跨敤涓€涓數鑴戞憚鍍忓ご鍚屾椂璇嗗埆鎿嶄綔鑰呯殑宸︽墜鍜屽彸鎵嬶紝骞堕€氳繃涓ゆ潯鐙珛 USB-RS485
杩炴帴瀹炴椂鎺у埗涓ゅ彧鍥犳椂 RH56DFTP-2L 鐏靛阀鎵嬨€?
> 鏈」鐩敤浜庡涔犮€佹紨绀哄拰鍩虹浜烘満浜や簰楠岃瘉銆傜伒宸ф墜浼氫骇鐢熺湡瀹炶繍鍔紝棣栨浣跨敤鎴栨洿鏀?> 鏍囧畾鍙傛暟鏃讹紝璇蜂繚鎸佹墜鎸囧懆鍥存棤闅滅鐗╋紝骞朵粠鍗曟牴鎵嬫寚鐨勫皬骞呭姩浣滃紑濮嬨€?
```mermaid
flowchart LR
    A[鐢佃剳鎽勫儚澶碷 --> B[MediaPipe HandLandmarker]
    B --> C[宸﹀彸鎵嬪叧閿偣]
    C --> D[鍙屾墜鍏酱鎵嬪娍鏄犲皠]
    D --> E[闄愬箙 姝诲尯 棰戠巼杩囨护]
    E --> F[涓ゆ潯 USB-RS485]
    F --> G[宸?RH56 涓庡彸 RH56]
```

## 鍔熻兘

- 鍚屾椂璇嗗埆闀滃儚鐢婚潰涓殑鐗╃悊宸︽墜鍜屽彸鎵嬶紝鍒嗗埆璺敱鍒颁袱鍙伒宸ф墜銆?- 鐗╃悊宸︽墜鏄犲皠鍒板乏 RH56锛堥粯璁?`COM3`锛夛紝鐗╃悊鍙虫墜鏄犲皠鍒板彸 RH56锛堥粯璁?`COM4`锛夈€?- 鍥涙寚璺熼殢寮洸鍔ㄤ綔锛涘ぇ鎷囨寚浣跨敤鐙珛寮洸涓庡唴澶栨棆杞槧灏勩€?- 瀵瑰乏鍙虫墜鍒嗗埆閰嶇疆琛岀▼闄愬箙銆佹鍖恒€佸彂閫侀鐜囧拰杞村弽鍚戯紝闄嶄綆璇姩浣滈闄┿€?- 鏀寔 `--no-serial` 鎽勫儚澶撮瑙堜笌 Windows 鍙屽嚮鍚姩銆?
## 纭欢瑕佹眰

| 椤圭洰 | 瑕佹眰 |
| --- | --- |
| 鐏靛阀鎵?| 涓ゅ彧鍥犳椂 RH56DFTP-2L锛屽乏鎵嬩笌鍙虫墜鍚勪竴鍙?|
| 鐢垫簮 | 涓ゅ彧鐏靛阀鎵嬪潎鎺ョ嫭绔?24V 鐢垫簮 |
| 閫氫俊 | 涓や釜 USB-RS485 杞帴鍣?|
| 鎽勫儚澶?| Windows 鍙敤鐨?USB 鎽勫儚澶存垨鍐呯疆鎽勫儚澶?|
| 杞欢 | Windows 10/11銆丳ython 3.9 鎴栨洿楂樼増鏈?|

## 浠庨浂閮ㄧ讲

### 1. 鑾峰彇浠ｇ爜

```powershell
git clone https://github.com/zyqzyq2266/bimanual-rh56-vision-control.git
cd bimanual-rh56-vision-control
```

### 2. 鍒涘缓 Python 鐜骞跺畨瑁呬緷璧?
瀹夎 Python 3.9 鎴栨洿楂樼増鏈紝骞跺湪瀹夎鐣岄潰鍕鹃€?`Add Python to PATH`銆?
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

### 3. 鍒涘缓宸﹀彸鎵嬫湰鏈洪厤缃?
```powershell
Copy-Item config.left.example.yaml config.left.yaml
Copy-Item config.right.example.yaml config.right.yaml
```

`config.left.yaml` 涓?`config.right.yaml` 鏄湰鏈烘爣瀹氭枃浠讹紝涓嶄細琚?Git 鎻愪氦銆?鍒嗗埆纭涓插彛銆佹尝鐗圭巼銆佹墜閮?ID銆佽酱鏂瑰悜鍜岄檺浣嶃€傞粯璁よ矾鐢变负锛?
| 鎽勫儚澶翠腑鐨勭墿鐞嗘墜 | MediaPipe 鏍囩 | 鐏靛阀鎵?| 涓插彛 |
| --- | --- | --- | --- |
| 宸︽墜 | `Right` | 宸?RH56DFTP-2L | `COM3` |
| 鍙虫墜 | `Left` | 鍙?RH56DFTP-2L | `COM4` |

棣栨璋冭瘯淇濇寔 `motion_scale: 0.2`锛屾瘡娆″彧娲诲姩涓€鏍规墜鎸囥€傚彸鎵嬬殑杞存柟鍚戙€佹媷鎸囪绋?鍜屽畨鍏ㄩ檺浣嶅繀椤诲湪 `config.right.yaml` 涓崟鐙爣瀹氾紝涓嶈鐩存帴澶嶅埗宸︽墜鐨?`invert_axes`銆?
### 4. 鍏堥獙璇佹憚鍍忓ご锛屼笉鎺у埗纭欢

```powershell
.\.venv\Scripts\python.exe -m hand_tracking.dual_app --left-config config.left.yaml --right-config config.right.yaml --no-serial
```

绐楀彛涓簲鑳界湅鍒伴暅鍍忕敾闈€佷袱鍙墜鐨勯粍鑹插叧閿偣锛屼互鍙婂乏鍙虫墜鐘舵€併€傛寜 `Esc` 閫€鍑恒€?
### 5. 杩炴帴骞跺惎鍔ㄤ袱鍙伒宸ф墜

1. 缁欎袱鍙伒宸ф墜鎺ラ€?24V 鐢垫簮锛屽苟鍒嗗埆杩炴帴 USB-RS485銆?2. 鍏抽棴鍥犳椂涓婁綅鏈哄拰鍏朵粬鍗犵敤 `COM3`銆乣COM4` 鐨勪覆鍙ｅ伐鍏枫€?3. 纭鎵嬫寚鍛ㄥ洿鏃犻殰纰嶇墿銆?4. 鍙屽嚮 `鍚姩鍙屾墜鐏靛阀鎵嬭窡闅?bat`锛屾垨杩愯锛?
```powershell
.\.venv\Scripts\python.exe -m hand_tracking.dual_app --left-config config.left.yaml --right-config config.right.yaml
```

鎸?`Space` 浼氬悜涓ゅ彧鎵嬪垎鍒彂閫佸悇鑷厤缃腑鐨?`open_pose`锛涙寜 `Esc` 鍚屾椂閫€鍑哄苟閲婃斁涓や釜涓插彛銆?
## 椤圭洰缁撴瀯

```text
bimanual-rh56-vision-control/
鈹溾攢 assets/hand_landmarker.task       # MediaPipe 鎵嬮儴璇嗗埆妯″瀷
鈹溾攢 hand_tracking/
鈹? 鈹溾攢 dual_app.py                    # 鍙屾墜鎽勫儚澶村惊鐜€佽矾鐢变笌绋嬪簭鍏ュ彛
鈹? 鈹溾攢 app.py                         # 琚弻鎵嬪叆鍙ｅ鐢ㄧ殑鍗曞彧鎵嬫帶鍒堕€昏緫
鈹? 鈹溾攢 config.py                      # 閰嶇疆璇诲彇鍜屾牎楠?鈹? 鈹溾攢 mapper.py                      # 21 涓叧閿偣鍒板叚杞存帶鍒跺€肩殑鏄犲皠
鈹? 鈹溾攢 rh56.py                        # RH56 涓插彛鍗忚
鈹? 鈹斺攢 safety.py                      # 闄愬箙銆佹鍖哄拰鍙戦€侀鐜囦繚鎶?鈹溾攢 tests/                            # 鍙屾墜涓庡叡浜ā鍧楄嚜鍔ㄥ寲娴嬭瘯
鈹溾攢 config.left.example.yaml          # 宸︽墜閰嶇疆妯℃澘
鈹溾攢 config.right.example.yaml         # 鍙虫墜閰嶇疆妯℃澘
鈹溾攢 鍚姩鍙屾墜鐏靛阀鎵嬭窡闅?bat             # Windows 鍙屾墜鍚姩鑴氭湰
鈹斺攢 pyproject.toml                    # Python 渚濊禆瀹氫箟
```

## 甯歌闂

| 鐜拌薄 | 鎺掓煡涓庤В鍐?|
| --- | --- |
| 鏃犳硶鎵撳紑 COM 鍙?| 鍏抽棴涓婁綅鏈哄拰鍏朵粬涓插彛宸ュ叿锛屽垎鍒鏌ュ乏鍙抽厤缃腑鐨勭鍙ｃ€?|
| 鎽勫儚澶撮粦灞?| 鍏抽棴鍗犵敤鎽勫儚澶寸殑搴旂敤锛涘皾璇曞湪鍚姩鍛戒护杩藉姞 `--camera 1`銆?|
| 鍙兘璇嗗埆涓€鍙墜 | 淇濇寔涓ゅ彧鎵嬫帉鏈濆悜鎽勫儚澶淬€佸厜绾垮厖瓒筹紝骞堕伩鍏嶄袱鎵嬮噸鍙犮€?|
| 宸﹀彸鎵嬫帶鍒跺弽鍚?| 鍒嗗埆璋冩暣 `config.left.yaml` 鎴?`config.right.yaml` 鐨勫搴?`invert_axes` 椤广€?|
| 澶ф媷鎸囧姩浣滀笉姝ｇ‘ | 鍏堝崟鐙祴璇曠 5銆? 杞达紱澶ф媷鎸囩殑琛岀▼鍜屾柟鍚戝簲鍒嗗埆鍦ㄥ乏鍙抽厤缃腑鏍″噯銆?|

## 娴嬭瘯

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 婕旂ず鏁堟灉

婕旂ず灞曠ず鎽勫儚澶村弻鎵嬪叧閿偣璇嗗埆锛屼互鍙婁袱鍙?RH56DFTP-2L 鐏靛阀鎵嬬殑瀹炴椂鎵嬫寚璺熼殢鏁堟灉銆?
https://github.com/user-attachments/assets/1f19b065-f330-492e-9e07-4d0c72f63753

## 椤圭洰鏂囨。

- [椤圭洰鎶ュ憡](docs/PROJECT_REPORT.md)锛氭瀯寤鸿繃绋嬨€侀棶棰樸€佽В鍐虫柟娉曚笌鏈€缁堟垚鏋溿€?- [浠ｇ爜](hand_tracking/)锛氭憚鍍忓ご銆佹槧灏勩€佷覆鍙ｅ崗璁拰瀹夊叏妯″潡瀹炵幇銆?
## 璁稿彲璇?
鏈」鐩娇鐢?[MIT License](LICENSE)銆備娇鐢ㄨ€呴渶鑷纭鍏剁伒宸ф墜銆侀┍鍔ㄥ拰绗笁鏂硅蒋浠剁殑
璁稿彲鏉℃锛屽苟瀵瑰疄闄呯‖浠舵搷浣滆礋璐ｃ€?
