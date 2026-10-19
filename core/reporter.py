from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class VerificationReporter:
    """
    Biên tập và xuất báo cáo kiểm định Markdown chi tiết (VERIFICATION_REPORT.md)
    kèm bảng tổng kết, điểm tin cậy và danh sách bằng chứng ảnh từng bước.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def generate_report(
        self,
        session_id: str,
        test_case: Dict[str, Any],
        step_results: List[Dict[str, Any]],
        overall_passed: bool,
        confidence_score: float,
        error_message: str = None
    ) -> Path:
        report_file = self.output_dir / "VERIFICATION_REPORT.md"
        meta = test_case.get("metadata", {})
        
        tc_id = meta.get("id", "TC-DEMO")
        tc_name = meta.get("name", "Kiểm thử Revit Add-in")
        ticket_id = meta.get("ticket_id", "N/A")
        module = meta.get("module", "General")
        
        status_text = "PASS (ĐÃ KHẮC PHỤC TRIỆT ĐỂ)" if overall_passed else "FAIL (CẦN XEM XÉT / LỖI)"
        badge_color = "green" if overall_passed else "red"

        content = [
            f"# BÁO CÁO XÁC MINH KIỂM THỬ: {tc_name}",
            "",
            f"> **Mã kịch bản:** `{tc_id}` | **Ticket Redmine:** `{ticket_id}` | **Phân hệ:** `{module}`  ",
            f"> **Thời gian chạy:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Session ID:** `{session_id}`  ",
            f"> **Kết luận từ AI Agent:** **{status_text}** (Độ tin cậy: **{confidence_score:.1f}%**)",
            "",
            "---",
            "",
            "## 1. TỔNG KẾT KẾT QUẢ",
            "",
            "| Chỉ số | Kết quả thực tế | Tiêu chuẩn đánh giá |",
            "|---|---|---|",
            f"| **Trạng thái tổng thể** | **{status_text}** | 100% các bước thành công |",
            f"| **Độ tin cậy (Confidence)** | **{confidence_score:.1f}%** | Căn cứ trên tính ổn định và số lần retry |",
            f"| **Tổng số bước kiểm thử** | **{len(step_results)}** | Các thao tác giao diện & xác minh dữ liệu |",
            f"| **Lỗi phát sinh** | `{error_message or 'Không có lỗi'}` | Ngưỡng ngắt mạch: tối đa 3 lần thử lại |",
            "",
            "---",
            "",
            "## 2. MA TRẬN TIẾN TRÌNH THỰC THI (STEP-BY-STEP AUDIT)",
            "",
            "| Bước | Tên hành động | Loại thao tác | Trạng thái | Lần thử lại | Ảnh minh chứng |",
            "|:---:|---|---|:---:|:---:|:---:|",
        ]

        for i, res in enumerate(step_results, 1):
            step_name = res.get("name", f"Bước {i}")
            action_type = res.get("action", "UI Action")
            st = res.get("status", "SUCCESS")
            retries = res.get("retries", 1)
            img_rel = res.get("screenshot_rel", "")
            img_link = f"[Xem ảnh]({img_rel})" if img_rel else "N/A"
            content.append(f"| **{i:02d}** | {step_name} | `{action_type}` | **{st}** | {retries}/3 | {img_link} |")

        content.extend([
            "",
            "---",
            "",
            "## 3. CHI TIẾT BẰNG CHỨNG ẢNH MÀN HÌNH TỪNG BƯỚC",
            ""
        ])

        for i, res in enumerate(step_results, 1):
            if res.get("screenshot_rel"):
                content.append(f"### Bước {i:02d}: {res.get('name')}")
                content.append(f"![Bước {i}]({res.get('screenshot_rel')})")
                content.append("")

        content.extend([
            "---",
            "",
            "## 4. XÁC NHẬN CỦA KỸ SƯ QA (HUMAN SIGN-OFF)",
            "",
            "- **Người nghiệm thu:** `___________________________`",
            "- **Đánh giá:** [ ] Chấp thuận kết quả (PASS)   [ ] Yêu cầu kiểm tra lại (RETEST)",
            "- **Ghi chú chuyên môn:**",
            "",
        ])

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content))

        print(f"[REPORTER] Đã xuất báo cáo xác minh: {report_file}")
        return report_file
