import time
from pathlib import Path
from typing import Optional, Tuple
import uiautomation as auto
from PIL import ImageGrab, ImageDraw


class RevitUIDriver:
    """
    Điều khiển giao diện Autodesk Revit thông qua Windows UIAutomation:
    - Tìm cửa sổ Revit chính
    - Điều hướng Ribbon Tab và Button
    - Tương tác với Hộp thoại (Dialog, Input Textbox, OK/Cancel Button)
    - Chụp ảnh màn hình cửa sổ kèm đánh dấu vị trí tương tác
    """

    def __init__(self, revit_title_pattern: str = "Autodesk Revit 2024"):
        self.revit_title_pattern = revit_title_pattern
        self.revit_window: Optional[auto.WindowControl] = None

    def find_revit_window(self, timeout: float = 60.0) -> auto.WindowControl:
        """Tìm cửa sổ chính của Autodesk Revit."""
        start_time = time.time()
        print(f"[UI-DRIVER] Đang tìm cửa sổ Revit chứa '{self.revit_title_pattern}' (timeout {timeout}s)...")

        while time.time() - start_time < timeout:
            # Tìm kiếm top-level window
            win = auto.WindowControl(searchDepth=1, SubName=self.revit_title_pattern)
            if win.Exists(maxSearchSeconds=1):
                win.SetActive()
                self.revit_window = win
                print(f"[UI-DRIVER] Đã kết nối với cửa sổ Revit: '{win.Name}'")
                return win
            time.sleep(1.0)

        # Fallback tìm kiếm theo ClassName nếu tiêu đề chưa load xong tên file
        win = auto.WindowControl(searchDepth=1, ClassName="Afx:00007FF")
        if win.Exists(maxSearchSeconds=1):
            win.SetActive()
            self.revit_window = win
            return win

        raise TimeoutError(f"Không tìm thấy cửa sổ Revit sau {timeout} giây.")

    def click_ribbon_tab(self, tab_name: str, timeout: float = 10.0) -> bool:
        """Click chọn một Tab trên thanh Ribbon."""
        win = self.revit_window or self.find_revit_window()
        tab = win.TabItemControl(Name=tab_name)
        if tab.Exists(maxSearchSeconds=timeout):
            tab.Click(simulateMove=False)
            print(f"[UI-DRIVER] Đã click Tab Ribbon: '{tab_name}'")
            time.sleep(0.5)
            return True
        raise LookupError(f"Không tìm thấy Ribbon Tab có tên: '{tab_name}'")

    def click_ribbon_button(self, button_name: str, timeout: float = 15.0) -> Tuple[int, int]:
        """Click một nút lệnh trên thanh Ribbon. Trả về tọa độ điểm click."""
        win = self.revit_window or self.find_revit_window()
        btn = win.ButtonControl(Name=button_name)
        if btn.Exists(maxSearchSeconds=timeout):
            rect = btn.BoundingRectangle
            click_x = (rect.left + rect.right) // 2
            click_y = (rect.top + rect.bottom) // 2
            btn.Click(simulateMove=False)
            print(f"[UI-DRIVER] Đã click nút: '{button_name}' tại tọa độ ({click_x}, {click_y})")
            time.sleep(1.0)
            return click_x, click_y
        raise LookupError(f"Không tìm thấy Button trên Ribbon có tên: '{button_name}'")

    def find_dialog(self, dialog_title: str, timeout: float = 10.0) -> auto.WindowControl:
        """Tìm một cửa sổ hộp thoại popup của Addin hoặc Revit."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            dlg = auto.WindowControl(searchDepth=2, SubName=dialog_title)
            if dlg.Exists(maxSearchSeconds=1):
                dlg.SetActive()
                return dlg
            time.sleep(0.5)
        raise TimeoutError(f"Hộp thoại '{dialog_title}' không xuất hiện sau {timeout} giây.")

    def fill_dialog_input(self, dialog: auto.WindowControl, control_name: str, value: str):
        """Điền giá trị vào ô Edit trong dialog."""
        edit = dialog.EditControl(SubName=control_name)
        if not edit.Exists(maxSearchSeconds=3):
            # Thử tìm theo AutomationId
            edit = dialog.EditControl(AutomationId=control_name)
        
        if edit.Exists(maxSearchSeconds=2):
            edit.Click(simulateMove=False)
            edit.SendKeys("{Ctrl}a{Delete}")
            edit.SendKeys(value)
            print(f"[UI-DRIVER] Đã điền '{value}' vào ô '{control_name}'")
            return
        raise LookupError(f"Không tìm thấy ô nhập liệu '{control_name}' trong dialog")

    def click_dialog_button(self, dialog: auto.WindowControl, button_text: str):
        """Nhấn nút bấm trong hộp thoại (ví dụ: OK, Cancel, Áp dụng)."""
        btn = dialog.ButtonControl(Name=button_text)
        if btn.Exists(maxSearchSeconds=5):
            btn.Click(simulateMove=False)
            print(f"[UI-DRIVER] Đã bấm nút '{button_text}' trong dialog")
            return
        raise LookupError(f"Không tìm thấy nút '{button_text}' trong dialog")

    def capture_window_screenshot(self, save_path: Path, highlight_coord: Optional[Tuple[int, int]] = None) -> Path:
        """Chụp ảnh màn hình cửa sổ Revit và vẽ vòng tròn highlight nếu có tọa độ click."""
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        win = self.revit_window or self.find_revit_window()
        rect = win.BoundingRectangle
        bbox = (rect.left, rect.top, rect.right, rect.bottom)

        img = ImageGrab.grab(bbox=bbox)

        if highlight_coord:
            # Chuyển đổi tọa độ màn hình sang tọa độ tương đối của ảnh
            rel_x = highlight_coord[0] - rect.left
            rel_y = highlight_coord[1] - rect.top
            draw = ImageDraw.Draw(img)
            r = 15
            draw.ellipse((rel_x - r, rel_y - r, rel_x + r, rel_y + r), outline="red", width=3)
            draw.ellipse((rel_x - 3, rel_y - 3, rel_x + 3, rel_y + 3), fill="red")

        img.save(str(save_path))
        print(f"[UI-DRIVER] Đã lưu ảnh minh chứng: {save_path.name}")
        return save_path
