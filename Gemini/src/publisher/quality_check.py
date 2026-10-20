"""
Kiểm tra chất lượng trước khi publish:
- File nguồn và trang xuất bản tồn tại, không rỗng
- Liệt kê chỉ số không lấy được (cảnh báo, không chặn xuất bản)
- Mọi tin hiển thị phải có link nguồn
"""

from pathlib import Path
from typing import Dict, Any


def perform_pre_publish_qc(daily_source_path: Path, index_html_path: Path, daily_data: Dict[str, Any]) -> Dict[str, Any]:
    errors, warnings = [], []

    for path, min_bytes in ((daily_source_path, 300), (index_html_path, 2000)):
        if not path.exists():
            errors.append(f"Không tìm thấy file {path}")
        elif path.stat().st_size < min_bytes:
            errors.append(f"File {path.name} quá nhỏ (< {min_bytes} bytes)")

    for m in daily_data.get("indices", []):
        if not m["ok"]:
            warnings.append(f"Không lấy được {m['label']} ({m['source']}): {m['error'][:120]}")

    news = daily_data.get("structured_news", {})
    for section, items in news.items():
        if not items and section != "watchlist":
            warnings.append(f"Mục tin '{section}' trống.")
        for it in items:
            if not it.get("link"):
                errors.append(f"Tin '{it.get('title', '')[:40]}' ({section}) thiếu link nguồn.")
        if any(it.get("from_cache") for it in items):
            warnings.append(f"Mục tin '{section}' dùng bộ nhớ đệm do nguồn RSS lỗi.")

    return {"passed": not errors, "errors": errors, "warnings": warnings}
