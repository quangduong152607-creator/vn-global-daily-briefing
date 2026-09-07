---
description: Quy chuẩn chuẩn hóa dữ liệu báo cáo thị trường và dàn ý Infographic cho NotebookLM & Antigravity
always_on: true
---

# Quy Chuẩn Dữ Liệu & Thiết Kế Infographic Bản Tin 24h

## 1. Nguyên Tắc Bất Di Bất Dịch Về Dữ Liệu
- **Tuyệt đối không để AI tự bịa số liệu.** Mọi con số (giá vàng, tỷ giá, chỉ số chứng khoán, xăng dầu, cấu hình sản phẩm) phải lấy trực tiếp từ nguồn chính thống, lưu kèm timestamp và URL nguồn.
- Nếu không lấy được số liệu -> hiển thị *"Không lấy được số liệu"* chứ tuyệt đối không ước lượng, nội suy, hoặc dùng số cũ mà không ghi chú.
- Mọi mẩu tin phải lưu giữ link nguồn gốc xuyên suốt pipeline.

## 2. Hệ Thống 4 Nhãn Độ Tin Cậy Bắt Buộc

Mỗi tin tức khi đưa vào tài liệu nguồn và hiển thị trên infographic bắt buộc phải mang ĐÚNG MỘT trong bốn nhãn sau:

| Nhãn | Điều kiện áp dụng | Cách hiển thị thị giác |
| :--- | :--- | :--- |
| ✅ **XÁC THỰC** | Có ≥2 nguồn độc lập uy tín, hoặc là thông cáo chính thức từ cơ quan/doanh nghiệp | Badge màu xanh lá (`#10b981`), icon tick |
| ⚠️ **MỘT NGUỒN** | Chỉ 1 nguồn đưa tin, chưa có nguồn thứ hai xác nhận độc lập | Badge màu vàng hổ phách (`#f59e0b`), icon cảnh báo |
| ❓ **TIN ĐỒN / CHƯA XÁC MINH** | Nguồn là rò rỉ (leak), tipster, mạng xã hội, diễn đàn | Badge màu cam/đỏ (`#f97316`), tách khu vực riêng |
| 💭 **NHẬN ĐỊNH** | Quan điểm, dự báo, phân tích chuyên gia, không phải sự kiện khách quan | Badge màu xám (`#64748b`), ghi rõ "Không phải khuyến nghị" |

## 3. Cấu Trúc Trình Bày 5 Tầng Thông Tin
1. **Hero Header**: Tên chuyên mục + 1 Con số ấn tượng nhất (Key Takeaway Stat).
2. **Key Pulse (3-4 Stat Cards)**: Thẻ số liệu lớn kèm nhãn ngắn gọn, phần trăm thay đổi và mũi tên xu hướng.
3. **Comparative / Trend Visual**: Thanh so sánh thị phần hoặc biểu đồ xu hướng.
4. **Strategic Insights**: Bảng đối sánh Động lực thúc đẩy vs Rào cản/Thách thức hoặc Tóm tắt sự kiện.
5. **Actionable Recommendations & Clickable Source Links**: Khuyến nghị ngắn + Danh sách liên kết nguồn gốc để người dùng đọc sâu.

## 4. Thẩm Mỹ & Đồ Họa
- Khổ dọc (Portrait), tối ưu tỉ lệ hiển thị trên màn hình smartphone (mobile-first).
- Bảng màu hiện đại: Modern Dark Editorial Palette (`#0a0f1d`, `#121a2f`, cyan `#00f2fe`, emerald `#10b981`).
- Typography: Font không chân cao cấp (`Plus Jakarta Sans`, `Inter`).
- Không đăng lại toàn văn bài báo. Chỉ tóm tắt 2-3 câu ngắn gọn kèm link gốc.
