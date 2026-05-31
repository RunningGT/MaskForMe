import win32com.client
import pythoncom
import time

class OneNoteAPI:
    def __init__(self):
        # 必须在独立线程或进程操作COM前初始化它
        pythoncom.CoInitialize()
        try:
            self.app = win32com.client.Dispatch("OneNote.Application")
        except Exception as e:
            print("初始化 OneNote 失败，请确保您安装了桌面版 OneNote", e)
            self.app = None

    def get_current_page_id(self):
        """
        获取当前活动页面的 ID
        这是一个最容易抛异常的地方（版本不同，后期绑定等）。
        这里我们将捕获异常并返回 None。
        """
        if not self.app:
            return None
        try:
            current_window = self.app.Windows.CurrentWindow
            return current_window.CurrentPageId
        except Exception as e:
            # 静默失败，通常由于权限问题、UWP版本或不在编辑页引起
            return None

    def get_page_content(self, page_id):
        """获取整个页面的 XML 数据"""
        if not self.app or not page_id:
            return None
        try:
            return self.app.GetPageContent(page_id)
        except Exception as e:
            print(f"获取页面内容异常: {e}")
            return None

    def update_page_content(self, xml_content):
        """将修改后的 XML 写回页面"""
        if not self.app:
            return False
        try:
            self.app.UpdatePageContent(xml_content)
            return True
        except Exception as e:
            print(f"更新页面内容异常: {e}")
            return False

    def close(self):
        pythoncom.CoUninitialize()
