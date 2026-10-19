# REVIT-QA-AGENT: HỆ THỐNG TỰ ĐỘNG HÓA KIỂM THỬ REVIT ADD-IN CHO QA/QC

> **Mục tiêu:** Tăng tốc độ xác minh Bug (Verify Bug) từ 2 tuần xuống còn **1 tuần/lần**, loại bỏ 100% sai sót thao tác con người, tự động lưu bằng chứng ảnh/log và hỗ trợ chạy dài hạn qua đêm mà không cần người túc trực.

---

## 1. Cấu trúc Dự án Mở rộng (Scalable Architecture)

Dự án được phân tách hoàn toàn giữa **Lõi Thực Thi (`core/`)** và **Kho Kịch Bản Kiểm Thử (`test_catalog/`)**. Khi phần mềm có thêm 50 tính năng mới hoặc có Breaking Changes, bạn chỉ cần tạo/sửa tệp YAML kịch bản mà **không phải sửa một dòng code Python nào**:

```
revit-qa-agent/
├── config.example.yaml        # [COMMIT LÊN GIT] Mẫu cấu hình chuẩn hóa cho toàn team
├── config.yaml                # [ĐÃ BỊ CHẶN BỞI .GITIGNORE] Cấu hình cục bộ riêng của từng máy
├── requirements.txt           # Danh mục thư viện phụ thuộc (uiautomation, pillow, pyyaml, requests)
├── setup.ps1                  # Script 1-click tự động cài đặt môi trường cho thành viên mới
├── main.py                    # Điểm kích hoạt dòng lệnh (CLI Runner)
│
├── core/                      # LÕI ĐIỀU PHỐI (ENGINE KHÔNG PHỤ THUỘC TÍNH NĂNG)
│   ├── config_loader.py       # Nạp cấu hình an toàn với fallback tự động
│   ├── progress_tracker.py    # Ghi tệp PROGRESS.yaml thời gian thực (Atomic Write)
│   ├── circuit_breaker.py     # Bộ ngắt mạch tối đa 3 lần thử lại (Chống loop vô tận)
│   ├── revit_manager.py       # Quản lý Revit.exe, Sandboxing mô hình, chống Windows Sleep
│   ├── ui_driver.py           # Windows UIAutomation điều khiển Ribbon, Dialogs, chụp ảnh
│   ├── notifier.py            # Gửi cảnh báo Telegram khi xong hoặc gặp lỗi chặn
│   └── reporter.py            # Xuất biên bản VERIFICATION_REPORT.md chuẩn nghiệm thu
│
└── test_catalog/              # KHO KỊCH BẢN KIỂM THỬ TẬP TRUNG (CON NGƯỜI ĐỌC & SỬA TAY)
    ├── README.md              # Hướng dẫn cập nhật kịch bản khi có Breaking Change
    ├── mep_tools/             # Phân hệ MEP (Scopebox, Hanger, ...)
    │   └── tc_42554_scopebox.yaml
    ├── electrical/            # Phân hệ Điện (Conduit, Cable Tray, ...)
    └── hvac/                  # Phân hệ Thông gió (Duct, Grille, ...)
```

---

## 2. Hướng dẫn Bắt đầu Nhanh cho Thành viên Mới (Quickstart trong 2 phút)

Khi bất kỳ thành viên nào trong team pull mã nguồn về máy:

### Bước 1: Chạy script cài đặt tự động 1-click
Mở PowerShell tại thư mục dự án và chạy:
```powershell
.\setup.ps1
```
*Script sẽ tự động tạo môi trường ảo `.venv`, cài đặt đầy đủ thư viện qua `uv` (hoặc `pip`), và tự động sao chép `config.example.yaml` thành `config.yaml`.*

### Bước 2: Kiểm tra cấu hình `config.yaml`
Mở tệp `config.yaml` vừa được sinh ra trên máy bạn để đối chiếu:
- Đường dẫn `executable_path` đến Revit 2024 trên máy của bạn.
- Thư mục lưu kết quả `output_dir` (mặc định: `D:/RevitTest/runs`).
- (Tùy chọn) Điền `bot_token` Telegram nếu muốn nhận thông báo qua điện thoại.

*(Lưu ý: Tệp `config.yaml` đã được đưa vào `.gitignore`, sẽ KHÔNG BAO GIỜ bị push lên Git làm lộ thông tin cá nhân hay xung đột cấu hình của người khác).*

### Bước 3: Xem danh sách các kịch bản kiểm thử sẵn có
```powershell
.\.venv\Scripts\Activate.ps1
python main.py --list
```

### Bước 4: Chạy kiểm thử
- **Chạy 1 kịch bản cụ thể:**
  ```powershell
  python main.py --test test_catalog/mep_tools/tc_42554_scopebox.yaml
  ```
- **Chạy toàn bộ một phân hệ (Suite):**
  ```powershell
  python main.py --suite mep_tools
  ```
- **Chạy toàn bộ kho kiểm thử:**
  ```powershell
  python main.py --all
  ```

---

## 3. Các cơ chế vận hành đặc thù

1. **Bộ ngắt mạch chống lặp vô tận (Max 3 Retries & Circuit Breaker):**  
   Mỗi bước thao tác (tìm Ribbon, điền Dialog) nếu chưa thành công sẽ được thử lại tối đa 3 lần. Nếu sau 3 lần vẫn lỗi, hệ thống ngắt mạch ngay lập tức và bắn cảnh báo Telegram, tuyệt đối không loop vô tận.

2. **Theo dõi tiến độ thời gian thực (`PROGRESS.yaml`):**  
   Trong lúc Agent đang chạy, bạn có thể mở tệp `PROGRESS.yaml` bất kỳ lúc nào để xem trạng thái bước hiện tại, số bước đạt/hỏng mà không làm gián đoạn chương trình.

3. **Chống tắt màn hình Windows (`SetThreadExecutionState`):**  
   Hệ thống tự động ngăn Windows tắt màn hình khi chạy dài hạn qua đêm, đảm bảo giao diện Revit luôn sẵn sàng để nhận lệnh UIAutomation.

4. **Bảo toàn dữ liệu gốc (Sandboxing Model):**  
   File mô hình kiểm thử (`.rvt`) luôn được sao chép sang thư mục tạm của phiên test. Revit chỉ thao tác trên bản sao tạm, bảo vệ 100% dữ liệu gốc của dự án.
