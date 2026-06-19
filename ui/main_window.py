import customtkinter as ctk
import tkinter as tk
import core.state as state
import pyperclip
import threading
from core.key_listener import KeyListener

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        state.AppState.load()

        self.title("MarkForMe - OneNote 渲染器")
        self.geometry("980x720")
        self.minsize(900, 600)

        self.listener = KeyListener()
        self.hook_thread = threading.Thread(target=self.listener.start_listening, daemon=True)
        self.hook_thread.start()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_panel()
        self.update_monitor()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkScrollableFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MarkForMe", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(padx=20, pady=(30, 10))

        self.mode_switch = ctk.CTkSwitch(self.sidebar_frame, text="后台运行监听", command=self.toggle_mode)
        self.mode_switch.pack(padx=20, pady=10, anchor="w")
        if state.AppState.is_auto_mode:
            self.mode_switch.select()

        ctk.CTkLabel(self.sidebar_frame, text="渲染触发热键:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=(15, 0), anchor="w")

        self.radio_var = tk.StringVar(value=state.AppState.render_trigger)
        ctk.CTkRadioButton(self.sidebar_frame, text="直接 Enter 渲染", variable=self.radio_var, value="enter", command=self.update_trigger).pack(padx=20, pady=5, anchor="w")
        ctk.CTkRadioButton(self.sidebar_frame, text="按下 Ctrl+Enter 渲染", variable=self.radio_var, value="ctrl_enter", command=self.update_trigger).pack(padx=20, pady=5, anchor="w")

        ctk.CTkLabel(self.sidebar_frame, text="触发后的执行操作策略:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=(15, 0), anchor="w")

        current_mode = str(getattr(state.AppState, 'interaction_mode', 4))
        self.seg_var = ctk.StringVar(value=current_mode)

        self.seg_btn = ctk.CTkSegmentedButton(self.sidebar_frame, values=["1", "2", "3", "4"], variable=self.seg_var, command=self.update_interaction)
        self.seg_btn.pack(padx=20, pady=(5, 0), fill="x")

        desc = ("1: 读取剪贴板，追加渲染在下一行\n"
                "2: 读取剪贴板，使用渲染覆盖当前选中文本\n"
                "3: 自动复制当前选中文本，渲染后覆盖替换\n"
                "4: MD工作模式(自动提取行，防误删并渲染至下一行)")
        ctk.CTkLabel(self.sidebar_frame, text=desc, justify="left", text_color="gray", font=ctk.CTkFont(size=11)).pack(padx=20, pady=5, anchor="w")

        ctk.CTkLabel(self.sidebar_frame, text="行内代码样式 (`Code`):", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=(15, 0), anchor="w")
        self.color_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="字体颜色 例:#d63384")
        self.color_entry.insert(0, state.AppState.code_color)
        self.color_entry.pack(padx=20, pady=5, fill="x")
        self.color_entry.bind("<KeyRelease>", self.update_colors)

        self.bg_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="背景颜色 例:#f6f8fa")
        self.bg_entry.insert(0, state.AppState.code_bg)
        self.bg_entry.pack(padx=20, pady=5, fill="x")
        self.bg_entry.bind("<KeyRelease>", self.update_colors)

        ctk.CTkLabel(self.sidebar_frame, text="长代码块样式 (```Code```):", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=(15, 0), anchor="w")
        self.theme_combo = ctk.CTkComboBox(self.sidebar_frame, values=["经典浅色 (VS Light)", "极客暗黑 (Monokai)", "PyCharm 深色 (Dark+)"], command=self.update_colors)
        self.theme_combo.set(state.AppState.block_theme)
        self.theme_combo.pack(padx=20, pady=5, fill="x")

        size_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        size_frame.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(size_frame, text="字号(pt):").pack(side="left")
        self.size_entry = ctk.CTkEntry(size_frame, width=60)
        self.size_entry.insert(0, state.AppState.block_size)
        self.size_entry.pack(side="left", padx=10)
        self.size_entry.bind("<KeyRelease>", self.update_colors)

        ctk.CTkLabel(self.sidebar_frame, text="快速片段:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(padx=20, pady=(15, 0), anchor="w")
        self.snippet_btn = ctk.CTkButton(self.sidebar_frame, text="悬浮此处弹出快捷菜单", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.snippet_btn.pack(padx=20, pady=5, fill="x")
        self.snippet_btn.bind("<Enter>", self.show_snippet_menu)

        self._build_menus()

    def update_trigger(self):
        state.AppState.render_trigger = self.radio_var.get()
        state.AppState.save()

    def update_interaction(self, value):
        state.AppState.interaction_mode = int(value)
        state.AppState.save()

    def _build_menus(self):
        self.menu_font = ("Microsoft YaHei UI", 16)
        self.snippet_menu = tk.Menu(self, tearoff=0, font=self.menu_font)

        math_menu = tk.Menu(self.snippet_menu, tearoff=0, font=self.menu_font)
        math_menu.add_command(label="分式 (\\frac)", command=lambda: pyperclip.copy(r"$\frac{a}{b}$"))
        math_menu.add_command(label="矩阵 (pmatrix)", command=lambda: pyperclip.copy(r"$\begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}$"))
        math_menu.add_command(label="累加 (\\sum)", command=lambda: pyperclip.copy(r"$\sum_{i=1}^{n}$"))
        math_menu.add_command(label="累乘 (\\prod)", command=lambda: pyperclip.copy(r"$\prod_{i=1}^{n}$"))
        math_menu.add_command(label="微积分 (\\int)", command=lambda: pyperclip.copy(r"$\int_{a}^{b} f(x) dx$"))
        math_menu.add_command(label="极限 (\\lim)", command=lambda: pyperclip.copy(r"$\lim_{x \to \infty}$"))
        self.snippet_menu.add_cascade(label="数学符号", menu=math_menu)

        code_menu = tk.Menu(self.snippet_menu, tearoff=0, font=self.menu_font)
        lang_map = {
            "Python": "python",
            "C": "c",
            "C#": "csharp",
            "JS": "javascript",
            "Go": "go",
            "Java": "java",
            "SQL": "sql",
        }

        for display_name, md_tag in lang_map.items():
            code_menu.add_command(
                label=f"{display_name} 语法块",
                command=lambda tag=md_tag: pyperclip.copy(f"```\n{tag}\n```")
            )

        self.snippet_menu.add_cascade(label="代码块", menu=code_menu)

        self.custom_menu = tk.Menu(self.snippet_menu, tearoff=0, font=self.menu_font)
        self._refresh_custom_menu()
        self.snippet_menu.add_cascade(label="自定义操作符", menu=self.custom_menu)

        self.snippet_menu.add_separator()
        self.snippet_menu.add_command(label="添加新的自定义操作符...", command=self.add_custom_op)

    def _refresh_custom_menu(self):
        self.custom_menu.delete(0, 'end')
        if not state.AppState.custom_ops:
            self.custom_menu.add_command(label="(空)", state="disabled")
        else:
            for op in state.AppState.custom_ops:
                self.custom_menu.add_command(label=op["name"], command=lambda s=op["snippet"]: pyperclip.copy(s))

    def show_snippet_menu(self, event):
        x = self.snippet_btn.winfo_rootx() + self.snippet_btn.winfo_width()
        y = self.snippet_btn.winfo_rooty()
        self.snippet_menu.post(x, y)

    def add_custom_op(self):
        dialog = ctk.CTkInputDialog(text="输入操作符名称与片段，格式：\n名称|代码片段", title="添加自定义片段")
        result = dialog.get_input()
        if result and "|" in result:
            name, snippet = result.split("|", 1)
            state.AppState.custom_ops.append({"name": name.strip(), "snippet": snippet.strip()})
            state.AppState.save()
            self._refresh_custom_menu()

    def create_main_panel(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure((1, 3), weight=1)

        self.md_label = ctk.CTkLabel(self.main_frame, text="最近拦截渲染的代码原文", font=ctk.CTkFont(size=14, weight="bold"))
        self.md_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.md_box = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(family="Consolas", size=14), fg_color="#BFDBF7")
        self.md_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.html_label = ctk.CTkLabel(self.main_frame, text="编译注入到 OneNote 的 HTML 结构", font=ctk.CTkFont(size=14, weight="bold"))
        self.html_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.html_box = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(family="Consolas", size=12), text_color="#a8c7fa")
        self.html_box.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def toggle_mode(self):
        state.AppState.is_auto_mode = (self.mode_switch.get() == 1)

    def update_colors(self, event=None):
        state.AppState.code_color = self.color_entry.get()
        state.AppState.code_bg = self.bg_entry.get()
        state.AppState.block_theme = self.theme_combo.get()
        state.AppState.block_size = self.size_entry.get()
        state.AppState.save()

    def update_monitor(self):
        current_md = self.md_box.get("0.0", "end").strip()
        if current_md != state.AppState.last_md.strip():
            self.md_box.delete("0.0", "end")
            self.md_box.insert("0.0", state.AppState.last_md)

        current_html = self.html_box.get("0.0", "end").strip()
        if current_html != state.AppState.last_html.strip():
            self.html_box.delete("0.0", "end")
            self.html_box.insert("0.0", state.AppState.last_html)

        self.after(500, self.update_monitor)
