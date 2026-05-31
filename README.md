# MarkForMe 🚀

**MarkForMe** 是一款专为Microsoft OneNote设计的后台无缝 Markdown 渲染器。 
它通过监听全局系统键盘事件与接管剪贴板，实现在 OneNote 这种不支持原生 Markdown 的富文本编辑器中，敲击回车瞬间将纯文本原地转换为美观的排版格式。

---

## ✨ 核心特性

- ⚡️ **无缝拦截与渲染**：在 OneNote 中输入文本或选中代码后，按下 `Enter` 或 `Ctrl+Enter`，即可瞬间原地替换为富文本。
- 📐 **原生数学公式支持**：支持内联 `$E=mc^2$` 与块级 `$$...$$` 公式，利用 `latex2mathml` 转换为 OneNote 原生可识别的 MathML。
- 💻 **IDE 级的长代码块高亮**：由 `Pygments` 强力驱动大段代码块 (`` ` ``包裹)，内置 3 种极客配色 (`PyCharm 深色 (Dark+)`、`极客暗黑 (Monokai)`、`经典浅色 (VS Light)`)，并利用 `<table>` 级注入完美解决 OneNote 吞背景色的痛点。
- 🔧 **三种高度自由的交互模式**：
    1. **追加渲染**：读取剪贴板，在当前光标下一行写入渲染结果。
    2. **局部覆盖**：读取剪贴板，直接覆盖当前被鼠标选中的原生文本。
    3. **全自动替换**：自动模拟 `Ctrl+C` 提取鼠标选中区域，后台渲染后自动覆盖，无需提前复制！
- 🎨 **现代配置 UI**：基于 `customtkinter` 设计的暗色透明交互控制台，支持断电记忆存储。

---

## 环境要求

- **操作系统**：Windows 10 / Windows 11 (依赖 `pywin32` 操作 Windows 系统剪贴板格式)
- **Python 版本**：Python 3.10+

### 运行依赖
你可以通过项目根目录的 `requirements.txt` 快速安装所有依赖：
```bash
pip install -r requirements.txt
```

*(主要包含：`customtkinter`、`markdown-it-py`、`mdit-py-plugins`、`latex2mathml`、`pygments`、`keyboard`、`pywin32`、`pyperclip`、`psutil`)*

---

## 使用说明

### 1. 源码运行
在终端中激活你的 Python 环境，并在项目根目录下执行：
```bash
python main.py
```
此时会弹出一个控制面板。确认“后台运行监听”处于开启状态。随后在 OneNote 中直接选中想要渲染的纯文本，按下回车即可生效！

### 2. 打包为独立的 `.exe` 可执行程序
如果你希望将其发送给没有 Python 环境的电脑使用，可以使用 `PyInstaller` 将其打包为单文件版。
**注意**：`latex2mathml` 内部存在静态数据字典，你需要显式地使用 `--add-data` 挂载本地的环境文件：

```bash
# 请将下面路径中的 D:\Python\envs\XXX 替换为你本地真实环境的 Python 路径
pyinstaller --clean -F -w --add-data "D:\Python\envs\MarkForMe\lib\site-packages\latex2mathml\unimathsymbols.txt;latex2mathml\" -y main.py
```
打包成功后，可在 `dist\` 目录下找到 `main.exe`。

---

## 项目结构

```text
MarkForMe/
├── main.py                # 主入口文件
├── core/
│   ├── state.py           # 全局状态管理与配置本地持久化 (config.json)
│   ├── key_listener.py    # 全局键盘事件钩子及模式路由
│   ├── clipboard_mgr.py   # Windows 原生 HTML 格式剪贴板深度封装
│   └── window_utils.py    # 追踪聚焦窗口，锁定 OneNote 进程状态
├── parser/
│   └── md_parser.py       # Markdown、Pygments、LaTex->MathML 的调度渲染引擎
├── ui/
│   └── main_window.py     # CustomTkinter 现代控制台面板界面
└── requirements.txt       # 项目第三方库依赖清单
```

---

## 证书与开源协议
本项目遵循 MIT 开源协议，支持自由修改与二次分发。
