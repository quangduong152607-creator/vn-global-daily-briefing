"""
Xác minh chéo và gán nhãn độ tin cậy bắt buộc cho từng mẩu tin:
1. ✅ XÁC THỰC: Có >= 2 nguồn độc lập uy tín, hoặc là công bố chính thức từ cơ quan/doanh nghiệp.
2. ⚠️ MỘT NGUỒN: Chỉ 1 nguồn đưa tin, chưa có nguồn khác xác nhận.
3. ❓ TIN ĐỒN / CHƯA XÁC MINH: Nguồn là rò rỉ, leak, tipster, MXH.
4. 💭 NHẬN ĐỊNH: Quan điểm, dự báo, phân tích, không phải sự kiện thực tế.
"""

import re
from typing import Dict, Any

OFFICIAL_SOURCES = {
    "Báo Chính Phủ", "State Bank of Vietnam (SBV)", "Bộ Công Thương", "HOSE", "HNX", "SJC", "Petrolimex"
}

RUMOR_KEYWORDS = [
    "rò rỉ", "tin đồn", "leak", "leaks", "tipster", "theo nguồn tin", "nghi vấn", "tin đồn cho hay", "renders rò rỉ"
]

OPINION_KEYWORDS = [
    "nhận định", "dự báo", "góc nhìn", "chuyên gia cho rằng", "kỳ vọng", "triển vọng", "quan điểm", "đánh giá xu hướng"
]

def assign_reliability_label(item: Dict[str, Any]) -> Dict[str, Any]:
    """Phân loại và gán nhãn độ tin cậy kèm màu sắc hiển thị chuẩn Spec"""
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    source_name = item.get("source_name", "")
    source_count = item.get("source_count", 1)
    
    combined_text = f"{title} {summary}"
    
    # 1. Kiểm tra TIN ĐỒN / CHƯA XÁC MINH
    if any(k in combined_text for k in RUMOR_KEYWORDS):
        return {
            "code": "RUMOR",
            "label": "❓ TIN ĐỒN / CHƯA XÁC MINH",
            "color": "#f97316", # Cam
            "css_class": "badge-rumor",
            "note": "Nguồn rò rỉ hoặc chưa được các bên chính thức xác nhận"
        }
        
    # 2. Kiểm tra NHẬN ĐỊNH / DỰ BÁO
    if any(k in combined_text for k in OPINION_KEYWORDS) or item.get("category") == "opinion":
        return {
            "code": "OPINION",
            "label": "💭 NHẬN ĐỊNH",
            "color": "#64748b", # Xám
            "css_class": "badge-opinion",
            "note": "Quan điểm phân tích/dự báo — không phải khuyến nghị đầu tư"
        }
        
    # 3. Kiểm tra XÁC THỰC
    # Điều kiện: Nguồn chính thức của nhà nước/hãng HOẶC có >= 2 nguồn độc lập
    if source_name in OFFICIAL_SOURCES or source_count >= 2:
        return {
            "code": "VERIFIED",
            "label": "✅ XÁC THỰC",
            "color": "#10b981", # Xanh lá
            "css_class": "badge-verified",
            "note": f"Được xác nhận bởi {source_name}" if source_count == 1 else f"Xác nhận chéo từ {source_count} nguồn độc lập"
        }
        
    # 4. Mặc định là MỘT NGUỒN
    return {
        "code": "SINGLE_SOURCE",
        "label": "⚠️ MỘT NGUỒN",
        "color": "#f59e0b", # Vàng hổ phách
        "css_class": "badge-single",
        "note": "Chỉ mới ghi nhận từ 1 nguồn đơn lẻ"
    }

def verify_and_tag_items(items: list) -> list:
    """Gán nhãn cho toàn bộ danh sách bài viết"""
    tagged = []
    for it in items:
        item_copy = it.copy()
        item_copy["reliability"] = assign_reliability_label(it)
        tagged.append(item_copy)
    return tagged

if __name__ == "__main__":
    t1 = {"title": "Chính phủ ban hành Nghị định mới về ưu đãi thuế xe điện", "source_name": "Báo Chính Phủ", "source_count": 1}
    t2 = {"title": "Rò rỉ hình ảnh thực tế của Vivo X200 Pro với chip Dimensity 9400", "source_name": "GSMArena", "source_count": 1}
    t3 = {"title": "Chuyên gia nhận định lãi suất tiền gửi có thể tăng nhẹ cuối năm", "source_name": "CafeF", "source_count": 1}
    t4 = {"title": "Giá vàng SJC tăng thêm 500 nghìn đồng", "source_name": "VnExpress", "source_count": 2}
    
    for t in [t1, t2, t3, t4]:
        label = assign_reliability_label(t)
        print(f"[{label['label']}] -> {t['title']}")
