import os
import yaml
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
EXAMPLE_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.example.yaml"


def load_config(config_path: Path = None) -> Dict[str, Any]:
    """
    Nạp cấu hình từ config.yaml.
    Nếu config.yaml chưa có, tự động nạp từ config.example.yaml để không bị crash.
    """
    target = config_path or DEFAULT_CONFIG_PATH
    if not target.exists():
        if EXAMPLE_CONFIG_PATH.exists():
            print(f"[WARN] Không tìm thấy '{target.name}'. Đang dùng cấu hình mẫu từ '{EXAMPLE_CONFIG_PATH.name}'.")
            target = EXAMPLE_CONFIG_PATH
        else:
            raise FileNotFoundError(f"Không tìm thấy file cấu hình tại {target}")

    with open(target, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Đảm bảo các trường mặc định tối thiểu luôn tồn tại
    config.setdefault("revit", {})
    config["revit"].setdefault("version", "2024")
    config["revit"].setdefault("executable_path", r"C:\Program Files\Autodesk\Revit 2024\Revit.exe")
    config["revit"].setdefault("startup_timeout_seconds", 90)
    config["revit"].setdefault("action_timeout_seconds", 30)

    config.setdefault("runtime", {})
    config["runtime"].setdefault("output_dir", "D:/RevitTest/runs")
    config["runtime"].setdefault("progress_file", "./PROGRESS.yaml")
    config["runtime"].setdefault("max_retries", 3)
    config["runtime"].setdefault("retry_backoff_seconds", 2)
    config["runtime"].setdefault("prevent_display_sleep", True)

    config.setdefault("telegram", {})
    config["telegram"].setdefault("enabled", False)

    return config
