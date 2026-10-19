import os
import shutil
import ctypes
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any


class RevitManager:
    """
    Quản lý vòng đời tiến trình Revit:
    1. Chống tắt màn hình Windows (SetThreadExecutionState) khi chạy qua đêm.
    2. Sandboxing mô hình .rvt: Luôn sao chép ra thư mục tạm, không bao giờ đụng vào file gốc.
    3. Mở và giám sát tiến trình Revit.exe.
    """

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

    def __init__(self, config: Dict[str, Any]):
        self.revit_cfg = config.get("revit", {})
        self.runtime_cfg = config.get("runtime", {})
        self.revit_exe = Path(self.revit_cfg.get("executable_path", r"C:\Program Files\Autodesk\Revit 2024\Revit.exe"))
        self.output_root = Path(self.runtime_cfg.get("output_dir", "D:/RevitTest/runs"))
        self.prevent_sleep = self.runtime_cfg.get("prevent_display_sleep", True)
        self.process: Optional[subprocess.Popen] = None

    def enable_keep_awake(self):
        """Ngăn Windows tắt màn hình hoặc chuyển sang chế độ Sleep khi test qua đêm."""
        if self.prevent_sleep and os.name == "nt":
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(
                    self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED
                )
                print("[SYSTEM] Đã kích hoạt chế độ chống Sleep / Tắt màn hình của Windows.")
            except Exception as e:
                print(f"[WARN] Không thể thiết lập SetThreadExecutionState: {e}")

    def disable_keep_awake(self):
        """Khôi phục lại chế độ quản lý nguồn mặc định của Windows."""
        if self.prevent_sleep and os.name == "nt":
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
                print("[SYSTEM] Đã trả lại quyền điều khiển Sleep mặc định cho Windows.")
            except Exception:
                pass

    def prepare_sandbox_model(self, fixture_path: str, session_id: str) -> Path:
        """
        Sao chép file model test vào thư mục sandbox tạm của phiên.
        Tuyệt đối không thao tác trực tiếp trên file gốc.
        """
        src = Path(fixture_path).resolve()
        if not src.exists():
            raise FileNotFoundError(f"Không tìm thấy file model test tại: {src}")

        sandbox_dir = self.output_root / session_id / "sandbox"
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        dest = sandbox_dir / src.name

        print(f"[SANDBOX] Đang sao chép file model vào sandbox...")
        print(f"  -> Nguồn: {src}")
        print(f"  -> Đích:  {dest}")
        shutil.copy2(src, dest)
        return dest

    def launch_revit_with_model(self, model_path: Path) -> subprocess.Popen:
        """Khởi động Revit mở kèm file model."""
        if not self.revit_exe.exists():
            raise FileNotFoundError(f"Không tìm thấy Revit.exe tại: {self.revit_exe}")

        cmd = [str(self.revit_exe), str(model_path)]
        print(f"[REVIT] Khởi động lệnh: {' '.join(cmd)}")
        self.process = subprocess.Popen(cmd)
        return self.process
