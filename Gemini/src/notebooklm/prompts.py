"""
Bộ Prompt sinh Infographic chuyên biệt cho 8 module bản tin 24h nạp vào NotebookLM.
Tuân thủ nghiêm ngặt Spec 6.3:
- CHỈ dùng dữ liệu trong source, không bổ sung từ bên ngoài.
- Giữ nguyên con số chính xác 100%.
- Giữ nguyên nhãn độ tin cậy.
- Khổ dọc (Portrait) tối ưu điện thoại.
"""

from typing import Dict

SYSTEM_INSTRUCTION = """
Bạn là Giám đốc Nghiên cứu Thị trường kiêm Chuyên gia Thiết kế Trực quan hóa Dữ liệu (Data Visualization Specialist) cho ngành Bán lẻ & Thiết bị Di động.
Nhiệm vụ của bạn là đọc tài liệu nguồn (daily_source.md) và thiết kế bản đặc tả Infographic trực quan (Infographic Blueprint) theo từng module được yêu cầu.

CÁC NGUYÊN TẮC BẤT DI BẤT DỊCH:
1. CHỈ dùng dữ liệu và con số có trong tài liệu nguồn. Tuyệt đối KHÔNG tự sáng tạo thêm con số.
2. Mọi con số phải giữ nguyên chính xác (giá trị, đơn vị, phần trăm, mốc thời gian).
3. Luôn giữ nguyên các nhãn độ tin cậy [XÁC THỰC], [MỘT NGUỒN], [TIN ĐỒN], [NHẬN ĐỊNH].
4. Ngôn ngữ: Hoàn toàn bằng Tiếng Việt, văn phong sắc bén, ngắn gọn, dễ nắm bắt trên điện thoại trong 30 giây.
"""

MODULE_PROMPTS: Dict[str, str] = {
    "module_1_indices": """
Từ Phần 1 của nguồn, hãy tạo Infographic BẢNG CHỈ SỐ THỊ TRƯỜNG & TỶ GIÁ 24H:
- Tiêu đề: BẢNG CHỈ SỐ TÀI CHÍNH & TIỀN TỆ 24H
- Hero Stat: Chọn 1 biến động ấn tượng nhất (VD: Mức tăng giá vàng hoặc biến động VN-Index).
- 4 Thẻ chỉ số cốt lõi:
  1. Vàng SJC (Mua/Bán + Thay đổi).
  2. Tỷ giá USD/VND (kèm tỷ giá trung tâm SBV).
  3. Tỷ giá CNY/VND & KRW/VND (dành riêng cho ngành Mua hàng ICT).
  4. VN-Index (Điểm số + % thay đổi + Khối ngoại).
- Xăng dầu: Giá RON 95-III & ngày điều chỉnh gần nhất.
- Yêu cầu visual: Dùng màu xanh cho tăng, đỏ cho giảm, ghi rõ timestamp cập nhật của từng số liệu.
""",

    "module_2_news_domestic": """
Từ Phần 2 của nguồn, hãy tạo Infographic THỜI SỰ TỔNG HỢP 24H:
- Trích xuất 5 tin trong nước quan trọng nhất.
- Mỗi tin gồm:
  + Tiêu đề ngắn gọn (dưới 15 từ).
  + Nhãn độ tin cậy hiển thị đầu dòng (✅ XÁC THỰC, ⚠️ MỘT NGUỒN...).
  + Tóm tắt cốt lõi trong 2 câu ngắn.
  + Ghi chú nguồn gốc báo chí.
- Bố cục: Thẻ dạng dòng thời gian (Timeline Cards) dễ cuộn trên điện thoại.
""",

    "module_3_finance": """
Từ Phần 4 của nguồn, hãy tạo Infographic CHUYÊN MỤC TÀI CHÍNH & CHÍNH SÁCH ĐẦU TƯ:
- Hero Stat: 1 con số hoặc chính sách mới ban hành có tác động lớn nhất.
- Phân tách rõ 3 khu vực:
  1. Chính sách mới của Chính phủ / NHNN / Bộ Tài chính.
  2. Diễn biến kinh tế vĩ mô & dòng tiền FDI.
  3. Nhận định chuyên gia (Bắt buộc mang nhãn [NHẬN ĐỊNH] - Không phải khuyến nghị đầu tư).
""",

    "module_4_tech_trends": """
Từ Phần 5 của nguồn, hãy tạo Infographic TOP XU HƯỚNG TÌM KIẾM GOOGLE TRENDS:
- Bảng đối chiếu Top 8 từ khóa tại Việt Nam vs Top 5 từ khóa Toàn cầu.
- Đánh dấu nổi bật bằng biểu tượng [📱 ICT] cho các từ khóa thuộc ngành công nghệ/điện thoại.
- Kèm lưu lượng tìm kiếm ước tính (traffic count).
""",

    "module_6_new_products": """
Từ Phần 7 của nguồn, hãy tạo Infographic SẢN PHẨM ICT MỚI RA MẮT:
- Ưu tiên làm nổi bật các dòng sản phẩm của Vivo, Realme, Samsung, Xiaomi.
- Với mỗi sản phẩm mới, lập thẻ thông số:
  + Tên máy & Phân khúc giá (VNĐ).
  + Cấu hình chính: Chipset, Màn hình, Sạc nhanh, Camera.
  + Điểm nhấn cạnh tranh so với đối thủ cùng tầm giá.
  + Nhãn độ tin cậy (nếu là rò rỉ thì bắt buộc gắn [TIN ĐỒN]).
""",

    "module_7_marketshare": """
Từ Phần 8 của nguồn, hãy tạo Infographic CỤC DIỆN THỊ PHẦN SMARTPHONE:
- Ghi rõ kỳ báo cáo: (VD: Báo cáo Quý 2/2026 - Counterpoint).
- Biểu đồ thanh ngang (Horizontal Bar) thể hiện thị phần các hãng tại Việt Nam (Samsung, OPPO, Apple, Xiaomi, Vivo, Realme...).
- 3 Điểm lưu ý quan trọng dành cho Chuyên viên Mua hàng (Buyer Insights).
"""
}

def get_prompt_for_module(module_id: str) -> str:
    """Lấy prompt theo mã module"""
    return MODULE_PROMPTS.get(module_id, SYSTEM_INSTRUCTION)
