import win32clipboard

def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return text
    except:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        return ""

def set_clipboard_html(html_fragment):
    # 组装符合 Windows 剪贴板的 HTML 格式头
    template = (
        "Version:0.9\r\n"
        "StartHTML:{0:08d}\r\n"
        "EndHTML:{1:08d}\r\n"
        "StartFragment:{2:08d}\r\n"
        "EndFragment:{3:08d}\r\n"
    )
    html_prefix = "<html><body><!--StartFragment-->"
    html_suffix = "<!--EndFragment--></body></html>"

    # 精确计算字节长度 (使用 utf-8 编码)
    fragment_start = len(template.format(0,0,0,0)) + len(html_prefix)
    fragment_end = fragment_start + len(html_fragment.encode('utf-8'))
    start_html = len(template.format(0,0,0,0))
    end_html = fragment_end + len(html_suffix)

    header = template.format(start_html, end_html, fragment_start, fragment_end)
    clipboard_data = (header + html_prefix + html_fragment + html_suffix).encode('utf-8')

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        cf_html = win32clipboard.RegisterClipboardFormat("HTML Format")
        win32clipboard.SetClipboardData(cf_html, clipboard_data)
        win32clipboard.CloseClipboard()
    except Exception as e:
        print(f"写入剪贴板失败: {e}")
