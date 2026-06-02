from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
import re
import latex2mathml.converter
import core.state as state
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Number, Operator, Text

class PyCharmStyle(Style):
    # 将原来的 #2b2b2b 调浅为经典的 Darcula 灰色
    background_color = "#3C3F41"
    styles = {
        Text:              "#A9B7C6",
        Comment:           "italic #808080",
        Keyword:           "bold #CC7832",      # 橙色：对应 import, from, if 等关键字
        Keyword.Namespace: "bold #CC7832",      # 橙色：对应命名空间关键字
        Name.Function:     "#FFC66D",           # 黄色：对应函数名
        Name.Class:        "bold #9876AA",      # 紫色：对应 class 类名
        String:            "#6A8759",           # 绿色：对应引用的文本/字符串
        Number:            "#6897BB",
        Operator:          "#A9B7C6",
        Name.Builtin:      "#8888C6",
    }

md = MarkdownIt('commonmark').enable('table').use(tasklists_plugin)

def _pygments_render(text, lang):
    try:
        # 【核心修改】：如果没有指定语言（例如只有 ```），默认当做 Python 处理
        if not lang:
            lang = 'python'
            
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except Exception:
            # 只有当填写的语言找不到（比如拼错）时，才让它去“猜”
            lexer = guess_lexer(text)
            
        b_theme = getattr(state.AppState, 'block_theme', 'PyCharm 深色 (Dark+)')
        
        if '浅色' in b_theme:
            pyg_style = 'vs'
            b_bg = "#f6f8fa"
            fg_color = "#24292e"
            border_color = "#d0d7de"
        elif 'Monokai' in b_theme:
            pyg_style = 'monokai'
            b_bg = "#49483E"
            fg_color = "#f8f8f2"
            border_color = "#55564A"
        else:
            pyg_style = PyCharmStyle
            b_bg = "#3C3F41"
            fg_color = "#A9B7C6"
            border_color = "#4D4D4D"
            
        size = getattr(state.AppState, 'block_size', '11')
        
        formatter = HtmlFormatter(noclasses=True, style=pyg_style, nowrap=True)
        inner_html = highlight(text, lexer, formatter)
        
        return (
            f"<table style=\"width: 100%; border-collapse: collapse; background-color: {b_bg}; border: 1px solid {border_color};\">"
            f"<tr><td style=\"padding: 10px; background-color: {b_bg};\">"
            f"<pre style=\"margin: 0; padding: 0; font-family: Consolas, 'Courier New', monospace; font-size: {size}pt; color: {fg_color}; line-height: 1.4; white-space: pre-wrap; word-wrap: break-word;\">"
            f"{inner_html}"
            f"</pre></td></tr></table>"
        )
    except Exception:
        c_bg = getattr(state.AppState, 'code_bg', '#f6f8fa')
        c_color = getattr(state.AppState, 'code_color', '#d63384')
        size = getattr(state.AppState, 'block_size', '11')
        return (
            f"<table style=\"width: 100%; border-collapse: collapse; background-color: {c_bg}; border: 1px solid #ccc;\">"
            f"<tr><td style=\"padding: 10px; background-color: {c_bg};\">"
            f"<pre style=\"margin: 0; padding: 0; font-family: Consolas, 'Courier New', monospace; font-size: {size}pt; color: {c_color}; line-height: 1.4; white-space: pre-wrap; word-wrap: break-word;\">"
            f"{text}"
            f"</pre></td></tr></table>"
        )

def custom_fence(self, tokens, idx, options, env):
    token = tokens[idx]
    return _pygments_render(token.content, token.info.strip())

def custom_code_block(self, tokens, idx, options, env):
    token = tokens[idx]
    return _pygments_render(token.content, "")

md.add_render_rule("fence", custom_fence)
md.add_render_rule("code_block", custom_code_block)

def preprocess_math(text):
    def block_repl(m):
        try:
            mathml = latex2mathml.converter.convert(m.group(1).strip())
            return f"<div style='text-align: center; margin: 10px 0;'>{mathml}</div>"
        except:
            return m.group(0)
    text = re.sub(r'\$\$(.*?)\$\$', block_repl, text, flags=re.DOTALL)

    def inline_repl(m):
        try:
            mathml = latex2mathml.converter.convert(m.group(1).strip())
            return mathml
        except:
            return m.group(0)
    text = re.sub(r'\$([^$]+?)\$', inline_repl, text)
    return text

def parse_to_html(text):
    text = text.strip()
    if not text:
        return None
        
    has_md_features = any(line.lstrip().startswith(c) for c in ('#', '>', '-', '*', '`', '$') for line in text.split('\n')) or \
                      '**' in text or '`' in text or '~~' in text or '$' in text
                      
    if not has_md_features:
        return None
        
    text = preprocess_math(text)
    html = md.render(text).strip()
    
    html = html.replace('<strong>', '<strong style="font-weight: bold;">')
    html = html.replace('<b>', '<b style="font-weight: bold;">')
    html = html.replace('<em>', '<em style="font-style: italic;">')
    
    c_color = state.AppState.code_color
    c_bg = state.AppState.code_bg
    
    html = html.replace('<code>', f'<code style="font-family: Consolas, monospace; color: {c_color}; background-color: {c_bg}; padding: 2px 4px; border-radius: 4px;">')
    
    html = html.replace(
        '<input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox">',
        '<span style="font-family: Segoe UI Emoji; color: #0078d7;">☑ </span>'
    )
    html = html.replace(
        '<input class="task-list-item-checkbox" disabled="disabled" type="checkbox">',
        '<span style="font-family: Segoe UI Emoji; color: #555;">☐ </span>'
    )
    html = html.replace('<li class="task-list-item">', '<li style="list-style-type: none;">')

    # 【修复2】如果是一段单行文本，剥离 markdown-it 自动生成的 <p> 标签
    if html.startswith('<p>') and html.endswith('</p>') and html.count('<p>') == 1:
        html = html[3:-4].strip()

    # 【修复3】将包裹层从 <div> 改为 <span>。这会告诉 OneNote 它是行内元素，绝对不许自动换行！
    wrapper = f"<span style='font-family: \"Microsoft YaHei UI\", sans-serif; font-size: 11pt;'>{html}</span>"
    return wrapper