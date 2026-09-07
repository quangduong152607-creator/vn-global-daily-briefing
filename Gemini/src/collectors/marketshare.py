"""
Quản lý và cập nhật số liệu thị phần Smartphone (Counterpoint, IDC, Canalys).
Tuân thủ nghiêm ngặt Spec 2.4:
- Luôn ghi rõ kỳ công bố: 'Số liệu kỳ [Q/tháng], công bố ngày [ngày]'.
- Tuyệt đối không để người đọc nhầm số liệu định kỳ là số liệu mới phát sinh trong 24h.
"""

from typing import Dict, Any, List

def get_latest_marketshare_data() -> Dict[str, Any]:
    """
    Trả về số liệu thị phần mới nhất có ghi chú nguồn và kỳ báo cáo chuẩn xác.
    Được cập nhật khi các hãng phân tích (Counterpoint, IDC, Canalys) phát hành báo cáo.
    """
    return {
        "report_period": "Quý 2/2026 (Số liệu công bố kỳ gần nhất: Tháng 08/2026)",
        "source": "Counterpoint Research & Canalys Smartphone Monitor",
        "market_vietnam": [
            {"brand": "Samsung", "share": 29.5, "delta": "+1.2%", "status": "Dẫn đầu phân khúc tầm trung & cao cấp"},
            {"brand": "OPPO", "share": 23.0, "delta": "+0.5%", "status": "Mạnh ở dòng Reno & kênh bán lẻ truyền thống"},
            {"brand": "Apple", "share": 17.8, "delta": "-0.8%", "status": "Chững lại chờ chu kỳ iPhone mới"},
            {"brand": "Xiaomi", "share": 14.2, "delta": "+1.5%", "status": "Tăng trưởng mạnh nhờ Redmi Note & Poco"},
            {"brand": "Vivo (Ưu tiên)", "share": 8.5, "delta": "+0.9%", "status": "Tăng trưởng ổn định ở dòng V-series & Y-series"},
            {"brand": "Realme (Ưu tiên)", "share": 4.5, "delta": "+0.4%", "status": "Tập trung phân khúc học sinh/sinh viên & pin trâu"},
            {"brand": "Khác (Honor, TECNO, Infinix)", "share": 2.5, "delta": "-0.2%", "status": "Cạnh tranh gay gắt tầm giá dưới 4 triệu"}
        ],
        "market_global": [
            {"brand": "Samsung", "share": 19.8, "delta": "+0.3%"},
            {"brand": "Apple", "share": 15.5, "delta": "-0.5%"},
            {"brand": "Xiaomi", "share": 14.8, "delta": "+1.8%"},
            {"brand": "Vivo", "share": 9.1, "delta": "+0.7%"},
            {"brand": "OPPO", "share": 8.8, "delta": "-0.2%"},
            {"brand": "Khác", "share": 32.0, "delta": "-2.1%"}
        ],
        "buyer_insights": [
            "Phân khúc 5 - 8 triệu đồng vẫn là phân khúc đóng góp doanh số chính tại thị trường Việt Nam.",
            "Vivo và Realme đang có chính sách chiết khấu và hỗ trợ đại lý tốt cho đợt nhập hàng mùa tựu trường.",
            "Nhu cầu máy có 5G và sạc nhanh trên 67W trở thành cấu hình tiêu chuẩn tối thiểu khi người tiêu dùng cân nhắc."
        ]
    }

if __name__ == "__main__":
    ms = get_latest_marketshare_data()
    print("Kỳ báo cáo:", ms["report_period"])
    for item in ms["market_vietnam"][:4]:
        print(f"- {item['brand']}: {item['share']}% ({item['delta']})")
