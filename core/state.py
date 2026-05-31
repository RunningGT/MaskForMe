import json
import os

class AppState:
    is_auto_mode = True
    render_trigger = 'enter'  # 'enter' or 'ctrl_enter'
    interaction_mode = 3 # 1, 2, 3
    last_md = "在此等待获取文本..."
    last_html = "等待渲染预览..."
    code_color = "#d63384"
    code_bg = "#f6f8fa"
    block_theme = "PyCharm 深色 (Dark+)"
    block_size = "11"
    custom_ops = []

    @classmethod
    def load(cls):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls.render_trigger = data.get("render_trigger", cls.render_trigger)
                    cls.interaction_mode = data.get("interaction_mode", cls.interaction_mode)
                    cls.code_color = data.get("code_color", cls.code_color)
                    cls.code_bg = data.get("code_bg", cls.code_bg)
                    cls.block_theme = data.get("block_theme", cls.block_theme)
                    cls.block_size = str(data.get("block_size", cls.block_size))
                    cls.custom_ops = data.get("custom_ops", cls.custom_ops)
            except:
                pass

    @classmethod
    def save(cls):
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump({
                    "render_trigger": cls.render_trigger,
                    "interaction_mode": cls.interaction_mode,
                    "code_color": cls.code_color,
                    "code_bg": cls.code_bg,
                    "block_theme": cls.block_theme,
                    "block_size": cls.block_size,
                    "custom_ops": cls.custom_ops
                }, f, ensure_ascii=False, indent=2)
        except:
            pass
