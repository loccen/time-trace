"""
Windows系统事件监听器
使用Windows API监听系统事件
"""
import platform
import time
import ctypes
import ctypes.wintypes
from typing import List, Dict, Any
from datetime import datetime

from event_listener import EventListener, SystemEventData
from models import EventType, EventSource
from logger import get_logger

logger = get_logger("WindowsListener")

# Windows API常量
WM_POWERBROADCAST = 0x0218
WM_WTSSESSION_CHANGE = 0x02B1
WM_ENDSESSION = 0x0016
WM_QUERYENDSESSION = 0x0011

# 电源事件
PBT_APMQUERYSUSPEND = 0x0000
PBT_APMQUERYSTANDBY = 0x0001
PBT_APMQUERYSUSPENDFAILED = 0x0002
PBT_APMQUERYSTANDBYFAILED = 0x0003
PBT_APMSUSPEND = 0x0004
PBT_APMSTANDBY = 0x0005
PBT_APMRESUMECRITICAL = 0x0006
PBT_APMRESUMESUSPEND = 0x0007
PBT_APMRESUMESTANDBY = 0x0008
PBT_APMBATTERYLOW = 0x0009
PBT_APMPOWERSTATUSCHANGE = 0x000A
PBT_APMOEMEVENT = 0x000B
PBT_APMRESUMEAUTOMATIC = 0x0012

# 会话事件
WTS_CONSOLE_CONNECT = 0x1
WTS_CONSOLE_DISCONNECT = 0x2
WTS_REMOTE_CONNECT = 0x3
WTS_REMOTE_DISCONNECT = 0x4
WTS_SESSION_LOGON = 0x5
WTS_SESSION_LOGOFF = 0x6
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8
WTS_SESSION_REMOTE_CONTROL = 0x9


class WindowsEventListener(EventListener):
    """Windows系统事件监听器"""
    
    def __init__(self):
        super().__init__("WindowsEventListener")
        self.hwnd = None
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.wtsapi32 = ctypes.windll.wtsapi32
        
        # 事件映射
        self.power_event_map = {
            PBT_APMSUSPEND: (EventType.SUSPEND, "系统挂起"),
            PBT_APMRESUMESUSPEND: (EventType.RESUME, "系统从挂起恢复"),
            PBT_APMSTANDBY: (EventType.SUSPEND, "系统待机"),
            PBT_APMRESUMESTANDBY: (EventType.RESUME, "系统从待机恢复"),
            PBT_APMRESUMEAUTOMATIC: (EventType.RESUME, "系统自动恢复"),
        }
        
        self.session_event_map = {
            WTS_SESSION_LOCK: (EventType.LOCK, "用户锁定会话"),
            WTS_SESSION_UNLOCK: (EventType.UNLOCK, "用户解锁会话"),
            WTS_SESSION_LOGON: (EventType.STARTUP, "用户登录"),
            WTS_SESSION_LOGOFF: (EventType.SHUTDOWN, "用户注销"),
        }
    
    def get_supported_events(self) -> List[EventType]:
        """获取支持的事件类型"""
        return [
            EventType.LOCK,
            EventType.UNLOCK,
            EventType.SUSPEND,
            EventType.RESUME,
            EventType.STARTUP,
            EventType.SHUTDOWN
        ]
    
    def _run(self):
        """监听器主循环"""
        if platform.system() != "Windows":
            logger.error("WindowsEventListener只能在Windows系统上运行")
            return
        
        try:
            self._create_window()
            self._register_notifications()
            self._message_loop()
        except Exception as e:
            logger.error(f"Windows事件监听器运行异常: {e}")
        finally:
            self._cleanup()
    
    def _create_window(self):
        """创建隐藏窗口用于接收消息"""
        # 定义窗口类
        wc = ctypes.wintypes.WNDCLASS()
        wc.lpfnWndProc = self._window_proc
        wc.lpszClassName = "TimeTraceEventListener"
        wc.hInstance = self.kernel32.GetModuleHandleW(None)
        
        # 注册窗口类
        class_atom = self.user32.RegisterClassW(ctypes.byref(wc))
        if not class_atom:
            raise Exception("注册窗口类失败")
        
        # 创建窗口
        self.hwnd = self.user32.CreateWindowExW(
            0,  # dwExStyle
            class_atom,  # lpClassName
            "TimeTrace Event Listener",  # lpWindowName
            0,  # dwStyle
            0, 0, 0, 0,  # x, y, width, height
            None,  # hWndParent
            None,  # hMenu
            wc.hInstance,  # hInstance
            None  # lpParam
        )
        
        if not self.hwnd:
            raise Exception("创建窗口失败")
        
        logger.debug(f"创建隐藏窗口成功: {self.hwnd}")
    
    def _register_notifications(self):
        """注册系统通知"""
        # 注册会话变化通知
        if not self.wtsapi32.WTSRegisterSessionNotification(self.hwnd, 0):
            logger.warning("注册会话通知失败")
    
    def _window_proc(self, hwnd, msg, wparam, lparam):
        """窗口消息处理函数"""
        try:
            if msg == WM_POWERBROADCAST:
                self._handle_power_event(wparam, lparam)
            elif msg == WM_WTSSESSION_CHANGE:
                self._handle_session_event(wparam, lparam)
            elif msg == WM_ENDSESSION:
                if wparam:  # 系统正在关闭
                    self._notify_event(EventType.SHUTDOWN, "系统关闭")
            elif msg == WM_QUERYENDSESSION:
                self._notify_event(EventType.SHUTDOWN, "系统准备关闭")
                return True  # 允许关闭
        except Exception as e:
            logger.error(f"处理窗口消息异常: {e}")
        
        # 调用默认窗口过程
        return self.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
    
    def _handle_power_event(self, wparam, lparam):
        """处理电源事件"""
        if wparam in self.power_event_map:
            event_type, description = self.power_event_map[wparam]
            self._notify_event(event_type, description)
            logger.debug(f"电源事件: {description}")
    
    def _handle_session_event(self, wparam, lparam):
        """处理会话事件"""
        if wparam in self.session_event_map:
            event_type, description = self.session_event_map[wparam]
            self._notify_event(event_type, description)
            logger.debug(f"会话事件: {description}")
    
    def _notify_event(self, event_type: EventType, description: str):
        """通知事件"""
        event_data = SystemEventData(
            event_type=event_type,
            event_time=datetime.now(),
            source=EventSource.SYSTEM,
            details=description,
            platform_info="Windows"
        )
        self._notify_callbacks(event_data)
    
    def _message_loop(self):
        """消息循环"""
        msg = ctypes.wintypes.MSG()
        
        while self.is_running and not self._stop_event.is_set():
            # 非阻塞获取消息
            bRet = self.user32.PeekMessageW(
                ctypes.byref(msg),
                self.hwnd,
                0, 0,
                1  # PM_REMOVE
            )
            
            if bRet:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
            else:
                # 没有消息时短暂休眠
                time.sleep(0.1)
    
    def _cleanup(self):
        """清理资源"""
        try:
            if self.hwnd:
                # 注销会话通知
                self.wtsapi32.WTSUnRegisterSessionNotification(self.hwnd)
                
                # 销毁窗口
                self.user32.DestroyWindow(self.hwnd)
                self.hwnd = None
                
                logger.debug("Windows事件监听器资源已清理")
        except Exception as e:
            logger.error(f"清理Windows事件监听器资源失败: {e}")


# 创建Windows事件监听器实例的工厂函数
def create_windows_listener() -> WindowsEventListener:
    """创建Windows事件监听器"""
    if platform.system() != "Windows":
        raise RuntimeError("WindowsEventListener只能在Windows系统上创建")
    
    return WindowsEventListener()
