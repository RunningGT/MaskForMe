import keyboard
import time
import threading
from core.window_utils import is_onenote_active
from core.clipboard_mgr import get_clipboard_text, set_clipboard_html
from parser.md_parser import parse_to_html
import core.state as state

class KeyListener:
    def __init__(self):
        self.is_simulating = False

    def start_listening(self):
        keyboard.on_press_key('enter', self._global_hook_enter, suppress=True)
        keyboard.on_press_key('f5', self._global_hook_f5, suppress=True)
        keyboard.wait()
        
    def _global_hook_f5(self, event):
        if self.is_simulating: return
        if is_onenote_active() and getattr(state.AppState, 'is_auto_mode', True):
            threading.Thread(target=self._handle_f5, daemon=True).start()
        else:
            self.is_simulating = True
            try: keyboard.send('f5')
            finally: self.is_simulating = False

    def _global_hook_enter(self, event):
        if self.is_simulating: return
        is_ctrl = keyboard.is_pressed('ctrl')
        
        if not is_onenote_active() or not getattr(state.AppState, 'is_auto_mode', True):
            threading.Thread(target=self._passthrough_enter, args=(is_ctrl,), daemon=True).start()
            return

        trig = getattr(state.AppState, 'render_trigger', 'enter')
        if (trig == 'enter' and not is_ctrl) or (trig == 'ctrl_enter' and is_ctrl):
            threading.Thread(target=self._handle_enter, args=(is_ctrl,), daemon=True).start()
        else:
            threading.Thread(target=self._passthrough_enter, args=(is_ctrl,), daemon=True).start()

    def _passthrough_enter(self, is_ctrl):
        self.is_simulating = True
        try:
            self._safe_send_enter(is_ctrl)
        finally:
            self.is_simulating = False

    # 【新增护城河】：安全的独立回车发送逻辑，防止状态死锁
    def _safe_send_enter(self, is_ctrl):
        keyboard.release('enter')
        if is_ctrl: keyboard.release('ctrl')
        time.sleep(0.01)
        if is_ctrl: keyboard.send('ctrl+enter')
        else: keyboard.send('enter')

    def _handle_f5(self):
        self.is_simulating = True
        try:
            keyboard.release('f5')
            time.sleep(0.05)
            
            keyboard.send('ctrl+a')
            time.sleep(0.1)
            keyboard.send('ctrl+c')
            time.sleep(0.15)
            
            text = get_clipboard_text()
            if text:
                state.AppState.last_md = text.strip()
                html = parse_to_html(text)
                if html:
                    state.AppState.last_html = html
                    set_clipboard_html(html)
                    time.sleep(0.1)
                    keyboard.send('ctrl+v')
                    time.sleep(0.05)
                    keyboard.send('right')
                    return
                else:
                    state.AppState.last_html = "未识别到有效的 Markdown/Math"
        except Exception as e:
            pass
        finally:
            self.is_simulating = False

    def _handle_enter(self, is_ctrl):
        self.is_simulating = True
        bs_hook = keyboard.on_press_key('backspace', lambda e: None, suppress=True)
        
        try:
            keyboard.release('enter')
            if is_ctrl: keyboard.release('ctrl')
            time.sleep(0.05) 
            
            mode = int(getattr(state.AppState, 'interaction_mode', 4))
            
            if mode == 4:
                keyboard.send('ctrl+a')
                time.sleep(0.05)
                keyboard.send('ctrl+c')
                time.sleep(0.15) # 适当增加等待时间，防止 OneNote 没反应过来导致提取为空
                
            elif mode == 3:
                keyboard.send('ctrl+c')
                time.sleep(0.15)
            
            text = get_clipboard_text()
            if not text:
                if mode == 4 or mode == 3:
                    keyboard.send('right')
                    time.sleep(0.02)
                self._safe_send_enter(is_ctrl)
                return

            text = text.strip()
            html = parse_to_html(text)
            
            if not html:
                state.AppState.last_html = "单行普通文本跳过渲染"
                if mode == 4 or mode == 3:
                    keyboard.send('right')
                    time.sleep(0.02)
                self._safe_send_enter(is_ctrl)
                return

            state.AppState.last_md = text
            state.AppState.last_html = html
            set_clipboard_html(html)
            time.sleep(0.1)

            # --- 渲染输出操作 ---
            if mode == 4:
                # 模式4：仅仅替换当前行，绝对不换行
                keyboard.send('ctrl+v')
                time.sleep(0.05)
                keyboard.send('right')
                
            elif mode in [2, 3]:
                # 模式2、3：替换当前行，然后去往下一行
                keyboard.send('ctrl+v')
                time.sleep(0.05)
                keyboard.send('right')
                time.sleep(0.02)
                self._safe_send_enter(is_ctrl) # 替换完成后发送真实换行
                
            elif mode == 1:
                keyboard.send('right')
                time.sleep(0.02)
                self._safe_send_enter(is_ctrl)
                time.sleep(0.05)
                keyboard.send('ctrl+v')
                
        except Exception as e:
            # 【终极保险】如果这里发生任何未知的代码崩溃，立即解除选中状态并还给用户正常的回车
            try:
                keyboard.send('right') 
                self._safe_send_enter(is_ctrl)
            except:
                pass
        finally:
            keyboard.unhook(bs_hook)
            self.is_simulating = False