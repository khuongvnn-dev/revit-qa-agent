# KHO KỊCH BẢN KIỂM THỬ TẬP TRUNG (TEST CATALOG)

> **Mục đích:** Nơi lưu trữ toàn bộ các testcase và kịch bản bug dưới dạng tệp YAML minh bạch, con người có thể đọc, hiểu và sửa đổi trực tiếp bằng tay khi sản phẩm có những thay đổi lớn (Breaking Changes).

---

## 1. Cấu trúc phân loại thư mục theo Phân hệ (Modules)

```
test_catalog/
├── mep_tools/                      # Các công cụ tạo Scopebox, Hanger, Vẽ ống, v.v.
│   └── tc_42554_scopebox.yaml      # Kịch bản kiểm thử tạo Scopebox (Ticket #42554)
│
├── electrical/                     # Các công cụ phần Điện, Conduit, Thang máng cáp
│
├── hvac/                           # Các công cụ phần Thông gió, Miệng gió, Chia Zone
│
└── plumbing/                       # Các công cụ phần Cấp thoát nước
```

---

## 2. Cách cập nhật Kịch bản khi Phần mềm có Breaking Change

Khi lập trình viên đổi tên Ribbon, đổi giao diện hộp thoại hoặc thay đổi luồng nghiệp vụ:
1. Bạn không cần sửa bất kỳ dòng code Python nào trong thư mục `core/`.
2. Chỉ cần mở tệp YAML tương ứng trong thư mục này (ví dụ `tc_42554_scopebox.yaml`).
3. Cập nhật lại tên Ribbon Tab mới, tên nút bấm hoặc các giá trị điền vào Dialog.
4. Chạy lại lệnh:
   ```powershell
   python main.py --test test_catalog/mep_tools/tc_42554_scopebox.yaml
   ```

---

## 3. Cấu trúc chuẩn của một tệp Kịch bản YAML

```yaml
metadata:
  id: "TC-42554"
  name: "Tạo Scopebox tự động cho phòng"
  author: "QA Team"
  ticket_id: "Redmine #42554"
  module: "mep_tools"

preconditions:
  fixture_model: "D:/RevitTest/runs/42554-scopebox/Project1.rvt"
  launch_revit: true

steps:
  - name: "Kết nối cửa sổ Revit 2024"
    action: "find_window"
    timeout: 60

  - name: "Chuyển sang Ribbon Tab của Add-in"
    action: "click_ribbon_tab"
    tab: "Hawee Tools"
    timeout: 10

  - name: "Kích hoạt nút lệnh trên Ribbon"
    action: "click_ribbon_button"
    button: "Scope Box"
    label: "ribbon_clicked"

  - name: "Chờ hộp thoại xuất hiện"
    action: "wait_dialog"
    title: "Tạo Scope Box"
    timeout: 15

  - name: "Nhập thông số Offset"
    action: "fill_dialog_input"
    title: "Tạo Scope Box"
    control: "txtOffset"
    value: "150"

  - name: "Nhấn nút Thực hiện"
    action: "click_dialog_button"
    title: "Tạo Scope Box"
    button: "OK"
```
