from config import is_admin
import sys
import os

def main():
    if not is_admin():
        print("="*40)
        print(" 【警告】请务必以管理员身份运行此脚本！")
        print(" 不带管理员权限，按键宏将被 Windows 安全机制阻断。")
        print("="*40)

    from ui.main_window import App
    app = App()
    # 当关闭窗口时，TKinter mainloop 退出，程序也会自动清理后台监听线程终止。
    app.mainloop()

if __name__ == '__main__':
    main()
