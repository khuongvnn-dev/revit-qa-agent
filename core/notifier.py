import requests
from typing import Dict, Any


class TelegramNotifier:
    """
    Dịch vụ bắn thông báo tức thời qua Telegram Bot khi:
    1. Hoàn tất toàn bộ kịch bản test.
    2. Kích hoạt bộ ngắt mạch Circuit Breaker sau 3 lần lỗi.
    3. Gặp câu hỏi chặn cần con người quyết định (Zero Guessing).
    """

    def __init__(self, config: Dict[str, Any]):
        self.cfg = config.get("telegram", {})
        self.enabled = self.cfg.get("enabled", False)
        self.bot_token = self.cfg.get("bot_token", "").strip()
        self.chat_id = self.cfg.get("chat_id", "").strip()

    def send_message(self, text: str) -> bool:
        if not self.enabled or not self.bot_token or not self.chat_id:
            print(f"[NOTIFIER (Console)] {text}")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                return True
            else:
                print(f"[NOTIFIER ERROR] Telegram API trả về mã {res.status_code}: {res.text}")
                return False
        except Exception as e:
            print(f"[NOTIFIER ERROR] Không thể gửi tin nhắn Telegram: {e}")
            return False

    def notify_run_completed(self, session_id: str, test_case: str, passed: bool, report_path: str):
        icon = "✅ PASS" if passed else "❌ FAILED"
        msg = (
            f"*{icon}: KẾT THÚC PHIÊN TEST TỰ ĐỘNG*\n\n"
            f"• *Kịch bản:* `{test_case}`\n"
            f"• *Session ID:* `{session_id}`\n"
            f"• *Báo cáo:* `{report_path}`\n\n"
            f"_Người dùng hiện đã có thể sử dụng lại chuột và bàn phím bình thường._"
        )
        self.send_message(msg)

    def notify_circuit_breaker_tripped(self, session_id: str, step_name: str, reason: str):
        msg = (
            f"🚨 *CẢNH BÁO KHẨN CẤP: BỘ NGẮT MẠCH KÍCH HOẠT*\n\n"
            f"• *Bước lỗi:* `{step_name}`\n"
            f"• *Lý do:* Thất bại liên tiếp 3 lần, hệ thống đã dừng lại để chống tốn token và treo máy.\n"
            f"• *Chi tiết:* {reason}\n"
            f"• *Session:* `{session_id}`\n\n"
            f"_Vui lòng kiểm tra lại màn hình máy tính hoặc xem tệp PROGRESS.yaml._"
        )
        self.send_message(msg)

    def notify_question_needed(self, session_id: str, question: str):
        msg = (
            f"❓ *YÊU CẦU XÁC NHẬN TỪ NGƯỜI DÙNG (ZERO GUESSING)*\n\n"
            f"Hệ thống gặp tình huống không rõ ràng và không tự suy đoán:\n\n"
            f"{question}\n\n"
            f"• *Session:* `{session_id}`"
        )
        self.send_message(msg)
