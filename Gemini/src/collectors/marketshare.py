"""
Quản lý và cập nhật số liệu thị phần Smartphone (GfK Vietnam Retail Audit & Counterpoint Research).
Tuân thủ nghiêm ngặt:
- Luôn ghi rõ kỳ công bố và nguồn dữ liệu uy tín (GfK, Counterpoint).
- Tuyệt đối không tự bịa khuyến nghị hay phán đoán chủ quan.
- Báo cáo số liệu khách quan, số liệu thực tế tại kênh chuỗi bán lẻ Việt Nam.
"""

from typing import Dict, Any, List

def get_latest_marketshare_data() -> Dict[str, Any]:
    """
    Trả về số liệu thị phần mới nhất có đối sánh giữa GfK (Sell-out tại điểm bán)
    và Counterpoint Research (Sell-in xuất xưởng) tại Việt Nam.
    """
    return {
        "report_period": "Quý 2/2026 (Số liệu công bố kỳ gần nhất: Tháng 08/2026)",
        "source": "GfK Vietnam Retail Audit & Counterpoint Research",
        "market_gfk_vietnam": [
            {"brand": "Samsung", "share": 31.2, "delta": "+1.4%", "segment": "Dẫn đầu hệ thống chuỗi MWG, FPT Shop"},
            {"brand": "OPPO", "share": 22.8, "delta": "+0.6%", "segment": "Bán lẻ truyền thống & dòng Reno"},
            {"brand": "Apple", "share": 18.5, "delta": "-0.5%", "segment": "Giữ vững phân khúc cao cấp trên 20 triệu"},
            {"brand": "Xiaomi", "share": 13.8, "delta": "+1.1%", "segment": "Tập trung phân khúc online & chuỗi điện máy"},
            {"brand": "Vivo", "share": 9.2, "delta": "+0.8%", "segment": "Tăng trưởng dòng V-series & Y-series"},
            {"brand": "Realme", "share": 4.1, "delta": "+0.3%", "segment": "Phân khúc phổ thông 3-5 triệu"},
            {"brand": "Khác", "share": 0.4, "delta": "-0.2%", "segment": "Các thương hiệu khác"}
        ],
        "market_vietnam": [
            {"brand": "Samsung", "share": 29.5, "delta": "+1.2%", "status": "Dẫn đầu sản lượng xuất xưởng"},
            {"brand": "OPPO", "share": 23.0, "delta": "+0.5%", "status": "Duy trì vị trí số 2 vững chắc"},
            {"brand": "Apple", "share": 17.8, "delta": "-0.8%", "status": "Chững lại trước đợt mở bán thế hệ mới"},
            {"brand": "Xiaomi", "share": 14.2, "delta": "+1.5%", "status": "Tăng trưởng nhờ dải sản phẩm Redmi Note"},
            {"brand": "Vivo", "share": 8.5, "delta": "+0.9%", "status": "Tăng trưởng ổn định ở nhóm tầm trung"},
            {"brand": "Realme", "share": 4.5, "delta": "+0.4%", "status": "Khai thác tốt mùa tựu trường"},
            {"brand": "Khác", "share": 2.5, "delta": "-0.2%", "status": "Honor, TECNO, Infinix"}
        ]
    }

if __name__ == "__main__":
    ms = get_latest_marketshare_data()
    print("Kỳ báo cáo:", ms["report_period"])
    for item in ms["market_gfk_vietnam"][:4]:
        print(f"- {item['brand']}: {item['share']}% ({item['delta']})")
