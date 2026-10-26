# DormFix macOS 安装包

**Cornell SYSEN 5151 / SYSEN 5930 · Team 3**

适用于 Apple Silicon（M1/M2/M3/M4）和 Intel Mac。默认演示网站只依赖 Python 3.10+，不需要 Streamlit 或 FastAPI。

> DormFix 是课程演示原型，不是 Cornell 或任何真实住房机构的生产维修系统。

## 1. 安装

1. 解压 `DormFix_macOS_2026-10-26.zip`。
2. 确认 Python：打开 Terminal，运行 `python3 --version`。需要 Python 3.10+。
3. 双击 **`Install DormFix.command`**。
4. 安装完成后，打开 `~/Applications/DormFix.app`。
5. 浏览器地址：`http://127.0.0.1:8502`。

## 2. macOS 显示“Apple 无法验证 Install DormFix.command”时

这个安装脚本是课程用的未签名本地脚本，没有 Apple Developer ID notarization，因此 Gatekeeper 可能阻止第一次运行。**不要关闭整个 Gatekeeper。**

### 推荐方法：系统设置放行

1. 先双击一次 `Install DormFix.command`，让 macOS 产生阻止提示。
2. 打开 **系统设置（System Settings）**。
3. 进入 **隐私与安全性（Privacy & Security）**。
4. 向下滚动到 **安全性（Security）**。
5. 找到类似“`Install DormFix.command` 已被阻止，因为无法验证开发者”的提示。
6. 点击 **仍要打开（Open Anyway）**。
7. 使用 Touch ID 或输入 Mac 登录密码确认。
8. 再次点击 **打开（Open）**。

这就是本安装包第一次运行时最推荐的方式。

### 备选方法：Finder 右键打开

在 Finder 中 Control-click / 右键 `Install DormFix.command` → **Open（打开）** → 再确认 **Open**。

### 仍被阻止时：仅解除这个安装包的 quarantine

如果你确认 ZIP 来自本对话，可以在 Terminal 中进入解压后的目录，再运行：

```bash
xattr -dr com.apple.quarantine .
chmod +x "Install DormFix.command"
./"Install DormFix.command"
```

不要使用 `sudo spctl --master-disable`；DormFix 不需要全局关闭 macOS 安全机制。

## 3. 日常启动与停止

安装后：

- 启动：双击 `~/Applications/DormFix.app`
- 备用启动：双击 `~/Applications/DormFix/Start DormFix.command`
- 停止：双击 `~/Applications/DormFix/Stop DormFix.command`
- 诊断：双击 `~/Applications/DormFix/Diagnose DormFix.command`
- 重置演示数据库：双击 `~/Applications/DormFix/Reset Demo Database.command`

## 4. Streamlit / FastAPI（可选）

默认 8502 Web UI 不需要第三方依赖。若要安装课程原规划的 Streamlit + FastAPI：

双击：

`~/Applications/DormFix/Install Optional Streamlit and API.command`

然后可以启动：

- `Start Streamlit.command` → `http://127.0.0.1:8501`
- `Start FastAPI.command` → `http://127.0.0.1:8000/docs`

详细说明见 `MAC_INSTALL_GUIDE.md` 和安装后的 `DormFix/README.md`。


# 完整 macOS 指南

## Python 检查

```bash
python3 --version
```

推荐 Python 3.12；Python 3.10+ 可以运行当前工程。

## 安装位置

安装器创建：

```text
~/Applications/DormFix.app
~/Applications/DormFix/
```

升级时如果存在旧安装，安装器会保留旧 SQLite 数据库，并把旧工程移动为带时间戳的备份目录。

## 课堂前建议

1. 运行 `Diagnose DormFix.command`。
2. 运行自动化测试：

```bash
cd ~/Applications/DormFix
python3 -m unittest discover -s tests -v
```

3. 启动 DormFix.app。
4. 按 `docs/DEMO_SCRIPT.md` 完成 Resident → Manager → Technician → Resident 流程。

## 本地 LLM（可选）

DormFix 的 AI 为 advisory only。没有 LLM 时仍可运行人工/确定性 fallback。

如使用 LM Studio：

```bash
export DORMFIX_LLM_URL=http://127.0.0.1:1234/v1/chat/completions
export DORMFIX_LLM_MODEL=local-model
```

AI 不得设置 priority、technician assignment 或 closure。

## 卸载

双击根目录的 `Uninstall DormFix.command`，输入 `UNINSTALL`。
