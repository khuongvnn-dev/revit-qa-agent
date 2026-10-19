import argparse
import sys
from pathlib import Path
from core.runner import TestRunner


def list_test_cases(catalog_dir: Path):
    print("\n" + "="*60)
    print(" DANH SÁCH CÁC KỊCH BẢN KIỂM THỬ TRONG KHO (TEST CATALOG)")
    print("="*60)
    cases = list(catalog_dir.glob("**/*.yaml"))
    if not cases:
        print(" (Chưa có kịch bản kiểm thử nào)")
        return

    for c in cases:
        rel = c.relative_to(catalog_dir)
        print(f"  • [{c.parent.name}] {c.name} -> {rel}")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Revit QA Agent - Hệ thống Tự Động Hóa Kiểm Thử Revit Add-in")
    parser.add_argument("--test", type=str, help="Đường dẫn đến tệp kịch bản YAML cần chạy")
    parser.add_argument("--suite", type=str, help="Tên phân hệ / thư mục con cần chạy (ví dụ: mep_tools)")
    parser.add_argument("--all", action="store_true", help="Chạy toàn bộ các kịch bản trong test_catalog")
    parser.add_argument("--list", action="store_true", help="Liệt kê toàn bộ kịch bản có sẵn")
    parser.add_argument("--config", type=str, default=None, help="Đường dẫn tùy chọn tới file cấu hình")

    args = parser.parse_args()
    root_dir = Path(__file__).resolve().parent
    catalog_dir = root_dir / "test_catalog"

    if args.list:
        list_test_cases(catalog_dir)
        sys.exit(0)

    runner = TestRunner(config_path=Path(args.config) if args.config else None)

    if args.test:
        test_file = Path(args.test).resolve()
        success = runner.run_case(test_file)
        sys.exit(0 if success else 1)

    elif args.suite:
        suite_dir = catalog_dir / args.suite
        if not suite_dir.exists():
            print(f"[ERROR] Không tìm thấy phân hệ: {args.suite}")
            sys.exit(1)
        cases = list(suite_dir.glob("*.yaml"))
        print(f"[SUITE] Bắt đầu chạy phân hệ '{args.suite}' gồm {len(cases)} kịch bản...")
        all_passed = True
        for c in cases:
            res = runner.run_case(c)
            if not res:
                all_passed = False
        sys.exit(0 if all_passed else 1)

    elif args.all:
        cases = list(catalog_dir.glob("**/*.yaml"))
        print(f"[ALL] Bắt đầu chạy TOÀN BỘ {len(cases)} kịch bản kiểm thử...")
        all_passed = True
        for c in cases:
            res = runner.run_case(c)
            if not res:
                all_passed = False
        sys.exit(0 if all_passed else 1)

    else:
        # Mặc định gợi ý nếu không truyền đối số
        print("\n[HƯỚNG DẪN SỬ DỤNG REVIT-QA-AGENT]")
        print("  • Xem danh sách kịch bản:  python main.py --list")
        print("  • Chạy 1 kịch bản:        python main.py --test test_catalog/mep_tools/tc_42554_scopebox.yaml")
        print("  • Chạy theo phân hệ:       python main.py --suite mep_tools")
        print("  • Chạy toàn bộ:            python main.py --all\n")


if __name__ == "__main__":
    main()
