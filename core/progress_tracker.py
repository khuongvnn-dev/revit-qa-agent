import os
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List


class ProgressTracker:
    """
    Theo dõi tiến độ kiểm thử thời gian thực và ghi ra tệp PROGRESS.yaml.
    Sử dụng cơ chế NTFS Atomic Write (ghi tệp tạm rồi đổi tên)
    để người dùng có thể mở đọc tệp bất kỳ lúc nào mà không gây lỗi xung đột truy cập.
    """

    def __init__(self, progress_path: str = "./PROGRESS.yaml"):
        self.progress_file = Path(progress_path).resolve()
        self.data: Dict[str, Any] = {
            "session_id": "",
            "started_at": "",
            "updated_at": "",
            "current_status": "IDLE",  # IDLE, RUNNING, RETRYING, BLOCKED, COMPLETED, FAILED
            "current_test_case": "",
            "current_step": "",
            "step_index": 0,
            "total_steps": 0,
            "passed_steps": 0,
            "failed_steps": 0,
            "retries_count": 0,
            "details": [],
            "error_message": None,
        }

    def start_session(self, session_id: str, test_case_name: str, total_steps: int):
        self.data["session_id"] = session_id
        self.data["started_at"] = datetime.now().isoformat()
        self.data["updated_at"] = datetime.now().isoformat()
        self.data["current_status"] = "RUNNING"
        self.data["current_test_case"] = test_case_name
        self.data["total_steps"] = total_steps
        self.data["step_index"] = 0
        self.data["passed_steps"] = 0
        self.data["failed_steps"] = 0
        self.data["retries_count"] = 0
        self.data["details"] = []
        self.data["error_message"] = None
        self._flush()

    def update_step(self, step_name: str, step_index: int, status: str = "RUNNING", note: str = ""):
        self.data["current_step"] = step_name
        self.data["step_index"] = step_index
        self.data["current_status"] = status
        self.data["updated_at"] = datetime.now().isoformat()
        self.data["details"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "step": step_name,
            "index": step_index,
            "status": status,
            "note": note
        })
        self._flush()

    def record_retry(self, step_name: str, attempt: int, max_retries: int, reason: str):
        self.data["current_status"] = "RETRYING"
        self.data["retries_count"] += 1
        self.data["updated_at"] = datetime.now().isoformat()
        self.data["details"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "step": step_name,
            "status": "RETRY",
            "attempt": f"{attempt}/{max_retries}",
            "reason": reason
        })
        self._flush()

    def set_blocked(self, reason: str):
        self.data["current_status"] = "BLOCKED_ON_HUMAN"
        self.data["error_message"] = reason
        self.data["updated_at"] = datetime.now().isoformat()
        self._flush()

    def complete_session(self, success: bool, summary: str = ""):
        self.data["current_status"] = "COMPLETED" if success else "FAILED"
        self.data["updated_at"] = datetime.now().isoformat()
        self.data["details"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "status": "SUMMARY",
            "summary": summary
        })
        self._flush()

    def _flush(self):
        """Ghi tệp atomic với vòng lặp thử lại tối đa 5 lần nếu tệp đang bị khóa đọc."""
        content = yaml.dump(self.data, allow_unicode=True, sort_keys=False)
        temp_file = self.progress_file.with_suffix(".tmp")
        
        for attempt in range(5):
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(content)
                # Thay thế nguyên tử trên Windows
                os.replace(temp_file, self.progress_file)
                break
            except (PermissionError, OSError):
                time.sleep(0.05)
