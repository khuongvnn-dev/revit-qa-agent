import time
from typing import Callable, Any, Optional


class CircuitBreakerTripped(Exception):
    """Ngoại lệ ném ra khi số lần thử lại vượt quá giới hạn 3 lần."""
    pass


class CircuitBreaker:
    """
    Bộ ngắt mạch chống lặp vô tận (Loop & Token Depletion Guardrail).
    Nếu một hành động kiểm thử gặp lỗi, cho phép thử lại tối đa max_retries (mặc định = 3).
    Nếu vượt quá 3 lần, ngắt mạch ngay lập tức và ném ra CircuitBreakerTripped để thông báo người dùng.
    """

    def __init__(self, max_retries: int = 3, backoff_seconds: float = 2.0, on_retry: Optional[Callable] = None):
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.on_retry = on_retry
        self.failure_history = []

    def execute(self, action_name: str, func: Callable, *args, **kwargs) -> Any:
        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            attempts += 1
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_error = e
                self.failure_history.append({
                    "action": action_name,
                    "attempt": attempts,
                    "error": str(e)
                })
                print(f"[CIRCUIT-BREAKER] Bước '{action_name}' gặp lỗi lần {attempts}/{self.max_retries}: {e}")

                if self.on_retry:
                    self.on_retry(action_name, attempts, self.max_retries, str(e))

                if attempts < self.max_retries:
                    # Chờ theo cơ chế backoff trước khi thử lại
                    time.sleep(self.backoff_seconds * attempts)

        # Đã hết 3 lần thử lại -> Ngắt mạch
        error_msg = (
            f"BỘ NGẮT MẠCH KÍCH HOẠT: Bước '{action_name}' thất bại liên tiếp {self.max_retries} lần! "
            f"Dừng khẩn cấp để tránh loop vô tận và lãng phí tài nguyên. Lỗi cuối: {last_error}"
        )
        print(f"\n[CRITICAL] {error_msg}\n")
        raise CircuitBreakerTripped(error_msg)
