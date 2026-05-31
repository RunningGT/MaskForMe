import win32gui
import win32process
import psutil

def is_onenote_active():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd: return False
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid: return False
        process = psutil.Process(pid)
        name = process.name().lower()
        # 兼容传统 exe 桌面版及 Windows 10 UWP 版应用
        return "onenote" in name
    except:
        return False
