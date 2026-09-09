"""
Kiểm tra chất lượng trước khi publish (Quality Check - Spec 7.1 & 10):
- Đảm bảo file nguồn và trang xuất bản tồn tại, không rỗng
- Kiểm tra tính toàn vẹn của số liệu (không để trống, không bịa số)
- Đảm bảo 100% tin tức có link nguồn
- Đảm bảo 100% tin tức có nhãn độ tin cậy hợp lệ
"""

from pathlib import Path
from typing import Dict, Any, List

VALID_RELIABILITY_CODES = {"VERIFIED", "SINGLE_SOURCE", "RUMOR", "OPINION"}

def verify_indices_integrity(indices: Dict[str, Any]) -> List[str]:
    issues = []
    forex = indices.get("forex", {})
    if forex.get("usd_vnd") == "Không lấy được số liệu":
        issues.append("Cảnh báo: Tỷ giá USD/VND không lấy được.")
    if forex.get("cny_vnd") == "Không lấy được số liệu":
        issues.append("Cảnh báo: Tỷ giá CNY/VND không lấy được.")
        
    stocks = indices.get("stocks", {})
    if not stocks.get("vnindex_points"):
        issues.append("Lỗi: Thiếu điểm số VN-Index.")
        
    return issues

def verify_news_integrity(news_items: List[Dict[str, Any]]) -> List[str]:
    issues = []
    for it in news_items:
        title = it.get("title", "")
        link = it.get("link", "")
        if not link or link == "#":
            issues.append(f"Lỗi: Tin '{title[:30]}...' thiếu link nguồn.")
            
        rel = it.get("reliability", {})
        code = rel.get("code")
        if code not in VALID_RELIABILITY_CODES:
            issues.append(f"Lỗi: Tin '{title[:30]}...' chưa được gán nhãn độ tin cậy hợp lệ.")
            
    return issues

def verify_structured_news_integrity(structured_news: Dict[str, Any]) -> List[str]:
    issues = []
    economy = structured_news.get("domestic_economy_news") or structured_news.get("economy_news", [])
    domestic_tech = structured_news.get("domestic_tech_news", [])
    intl_macro = structured_news.get("intl_macro_news", [])
    intl_tech = structured_news.get("intl_tech_news") or structured_news.get("tech_news", [])
    social = structured_news.get("social_news", [])
    flash = structured_news.get("flash_news", [])

    if not economy:
        issues.append("Cảnh báo: Khối Kinh tế & Thị trường trong nước chưa có bài viết.")
    for idx, it in enumerate(economy, 1):
        if not it.get("context"):
            issues.append(f"Cảnh báo: Bài Kinh tế trong nước #{idx} thiếu phân tích Bối cảnh.")
        if not it.get("impact"):
            issues.append(f"Cảnh báo: Bài Kinh tế trong nước #{idx} thiếu phân tích Tác động.")
        if not it.get("link") or it.get("link") == "#":
            issues.append(f"Lỗi: Bài Kinh tế trong nước #{idx} thiếu link nguồn.")

    if not domestic_tech:
        issues.append("Cảnh báo: Khối Công nghệ & Số hóa trong nước chưa có bài viết.")
    for idx, it in enumerate(domestic_tech, 1):
        if not it.get("development"):
            issues.append(f"Cảnh báo: Bài Công nghệ trong nước #{idx} thiếu Diễn biến.")
        if not it.get("significance"):
            issues.append(f"Cảnh báo: Bài Công nghệ trong nước #{idx} thiếu Ý nghĩa ngành hàng.")
        if not it.get("link") or it.get("link") == "#":
            issues.append(f"Lỗi: Bài Công nghệ trong nước #{idx} thiếu link nguồn.")

    if not intl_macro:
        issues.append("Cảnh báo: Khối Kinh tế & Địa chính trị quốc tế chưa có bài viết.")
    for idx, it in enumerate(intl_macro, 1):
        if not it.get("context"):
            issues.append(f"Cảnh báo: Bài Địa chính trị quốc tế #{idx} thiếu phân tích Bối cảnh.")
        if not it.get("impact"):
            issues.append(f"Cảnh báo: Bài Địa chính trị quốc tế #{idx} thiếu phân tích Tác động.")
        if not it.get("link") or it.get("link") == "#":
            issues.append(f"Lỗi: Bài Địa chính trị quốc tế #{idx} thiếu link nguồn.")

    if not intl_tech:
        issues.append("Cảnh báo: Khối Công nghệ & Di động quốc tế chưa có bài viết.")
    for idx, it in enumerate(intl_tech, 1):
        if not it.get("development"):
            issues.append(f"Cảnh báo: Bài Công nghệ quốc tế #{idx} thiếu Diễn biến.")
        if not it.get("significance"):
            issues.append(f"Cảnh báo: Bài Công nghệ quốc tế #{idx} thiếu Ý nghĩa ngành hàng.")
        if not it.get("link") or it.get("link") == "#":
            issues.append(f"Lỗi: Bài Công nghệ quốc tế #{idx} thiếu link nguồn.")

    if not social:
        issues.append("Cảnh báo: Khối Tin Social & Showbiz giải trí chưa có nội dung.")

    if not flash:
        issues.append("Cảnh báo: Khối Tin vắn nhanh chưa có nội dung.")

    return issues

def perform_pre_publish_qc(daily_source_path: Path, index_html_path: Path, daily_data: Dict[str, Any]) -> Dict[str, Any]:
    """Kiểm tra toàn bộ điều kiện trước khi nghiệm thu xuất bản"""
    report = {
        "passed": True,
        "errors": [],
        "warnings": [],
        "file_checks": {}
    }
    
    # 1. Kiểm tra file daily_source.md
    if not daily_source_path.exists():
        report["errors"].append(f"Không tìm thấy file {daily_source_path}")
    else:
        size = daily_source_path.stat().st_size
        report["file_checks"]["daily_source_bytes"] = size
        if size < 500:
            report["errors"].append("File daily_source.md quá nhỏ (< 500 bytes)")
            
    # 2. Kiểm tra file index.html
    if not index_html_path.exists():
        report["errors"].append(f"Không tìm thấy file {index_html_path}")
    else:
        size = index_html_path.stat().st_size
        report["file_checks"]["index_html_bytes"] = size
        if size < 2000:
            report["errors"].append("File index.html quá nhỏ (< 2000 bytes)")
            
    # 3. Kiểm tra số liệu
    indices_issues = verify_indices_integrity(daily_data.get("indices", {}))
    report["warnings"].extend(indices_issues)
    
    # 4. Kiểm tra tin tức thô
    all_news = daily_data.get("news", {}).get("domestic", []) + daily_data.get("news", {}).get("technology", [])
    news_issues = verify_news_integrity(all_news)
    report["errors"].extend(news_issues)

    # 5. Kiểm tra tin tức cấu trúc 3 khối
    structured = daily_data.get("structured_news", {})
    if structured:
        struct_issues = verify_structured_news_integrity(structured)
        for issue in struct_issues:
            if issue.startswith("Lỗi:"):
                report["errors"].append(issue)
            else:
                report["warnings"].append(issue)
    
    if report["errors"]:
        report["passed"] = False
        
    return report

if __name__ == "__main__":
    print("Module Quality Check sẵn sàng.")
