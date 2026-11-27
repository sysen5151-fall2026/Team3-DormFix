# DormFix Windows 安装包

**Cornell SYSEN 5151 / SYSEN 5930 · Team 3**

适用于 Windows 10 / Windows 11。默认演示网站只依赖 Python 3.10+。

> DormFix 是课程演示原型，不是 Cornell 或任何真实住房机构的生产维修系统。

## 1. 安装

1. 解压 `DormFix_Windows_2026-10-26.zip`。
2. 确认 Python 3.10+ 已安装，并在安装 Python 时勾选 **Add Python to PATH**；也支持 Windows `py` launcher。
3. 双击 **`Install DormFix.bat`**。
4. 安装到 `%LOCALAPPDATA%\DormFix`，并在桌面创建 **DormFix** 快捷方式。
5. 双击桌面的 DormFix，浏览器打开 `http://127.0.0.1:8502`。

## 2. Windows Defender SmartScreen 阻止时

下载的 ZIP/脚本可能带有 Internet 标记，Windows 可能显示 **“Windows protected your PC”**。

- 确认包来自本对话后，点击 **More info（更多信息）** → **Run anyway（仍要运行）**。
- 或者右键 ZIP / `.bat` → **Properties（属性）** → 如果底部出现 **Unblock（解除锁定）**，勾选后 Apply，再解压/运行。
- 不需要、也不建议全局关闭 Microsoft Defender SmartScreen。

如果 Windows 防火墙询问 Python 网络权限，本演示默认只绑定 `127.0.0.1`（本机）。不要允许 Public networks；通常 localhost 演示不需要开放外部入站访问。

## 3. 日常启动

安装后可以：

- 双击桌面 **DormFix** 快捷方式；或
- 运行 `%LOCALAPPDATA%\DormFix\Start DormFix.bat`

停止：`Stop DormFix.bat`  
诊断：`Diagnose DormFix.bat`  
重置数据：`Reset Demo Database.bat`

## 4. Streamlit / FastAPI（可选）

运行 `%LOCALAPPDATA%\DormFix\Install Optional Streamlit and API.bat`，然后：

- `Start Streamlit.bat` → `http://127.0.0.1:8501`
- `Start FastAPI.bat` → `http://127.0.0.1:8000/docs`

详细说明见 `WINDOWS_INSTALL_GUIDE.md`。


# 完整 Windows 指南

## Python 检查

在 PowerShell 或 Command Prompt：

```bat
py -3 --version
```

或：

```bat
python --version
```

需要 Python 3.10+，推荐 Python 3.12。

## 安装目录

```text
%LOCALAPPDATA%\DormFix
```

安装器会在桌面建立快捷方式，指向 `Start DormFix.bat`。

## 课堂前验证

运行：

```text
%LOCALAPPDATA%\DormFix\Diagnose DormFix.bat
```

或：

```bat
cd /d "%LOCALAPPDATA%\DormFix"
python -m unittest discover -s tests -v
```

之后按 `docs\DEMO_SCRIPT.md` 演练 Resident → Manager → Technician → Resident。

## 本地 LLM（可选）

PowerShell 示例：

```powershell
$env:DORMFIX_LLM_URL="http://127.0.0.1:1234/v1/chat/completions"
$env:DORMFIX_LLM_MODEL="local-model"
```

未配置 LLM 时系统仍使用人工/确定性 fallback。
