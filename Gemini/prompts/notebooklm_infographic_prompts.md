# Bộ Prompt Mẫu Dành Cho NotebookLM: Tổng Hợp Dữ Liệu Thị Trường Sang Dàn Ý Infographic

Sau khi nạp tài liệu từ thư mục `notebooklm_sources/` vào NotebookLM, hãy sử dụng các prompt sau trong khung chat của NotebookLM để tạo dàn bài thiết kế Infographic:

---

## Prompt 1: Trích Xuất Toàn Diện Dàn Ý Infographic (Khuyên dùng)
> "Dựa trên toàn bộ tài liệu nguồn thị trường đã nạp, hãy đóng vai trò là Giám đốc Nghiên cứu Thị trường (Market Research Director) kết hợp cùng Chuyên gia Thiết kế Trực quan hóa Dữ liệu (Data Visualization Specialist). Hãy thiết kế một bản đặc tả Infographic (Infographic Blueprint) hoàn chỉnh theo cấu trúc sau:
> 
> 1. **TIÊU ĐỀ & HERO STAT**:
>    - 1 Tiêu đề giật gân, xúc tích về xu hướng chính.
>    - 1 Con số ấn tượng nhất (Hero Stat) kèm chú thích ngắn gọn (tối đa 15 từ).
> 
> 2. **3 - 4 CHỈ SỐ XƯƠNG SỐNG (KEY PULSE METRICS)**:
>    - Trích xuất 4 con số quan trọng nhất (VD: Quy mô thị trường, CAGR, Tổng vốn đầu tư, Thị phần dẫn đầu).
>    - Mỗi chỉ số gồm: [Con số] + [Nhãn ngắn] + [Ý nghĩa kinh doanh].
> 
> 3. **DỮ LIỆU ĐỐI SÁNH / THỊ PHẦN (COMPARATIVE DATA)**:
>    - Lập bảng hoặc danh sách tỷ lệ phần trăm phân chia thị phần giữa các đối thủ lớn hoặc các phân khúc khách hàng.
>    - Đề xuất loại biểu đồ phù hợp nhất để thể hiện (Bar chart, Donut chart, hay Stacked trend).
> 
> 4. **BỨC TRANH ĐỘNG LỰC & RÀO CẢN (MARKET FORCES)**:
>    - 3 Động lực tăng trưởng hàng đầu (Drivers).
>    - 3 Thách thức hoặc rủi ro lớn nhất (Headwinds / Bottlenecks).
> 
> 5. **TỔNG KẾT & HÀNH ĐỘNG (ACTIONABLE TAKEAWAY)**:
>    - 2-3 khuyến nghị chiến lược ngắn gọn cho doanh nghiệp.
> 
> Hãy đảm bảo tất cả con số đều trích xuất chính xác 100% từ tài liệu nguồn và không thêm bớt số liệu không có trong tài liệu."

---

## Prompt 2: Báo Cáo Số Liệu Nhanh (Data-Dense Executive Card)
> "Trích xuất toàn bộ các chỉ số định lượng trong tài liệu thành một bảng Markdown tổng hợp bao gồm các cột:
> | Hạng mục | Giá trị hiện tại | Dự báo tương lai / Tăng trưởng | Đơn vị tính | Nguồn & Mốc thời gian |
> Sau đó, chọn ra top 5 số liệu quan trọng nhất để đưa lên poster/infographic tóm tắt dành cho lãnh đạo cấp cao."

---

## Prompt 3: Kịch Bản Kể Chuyện Bằng Hình Ảnh (Visual Storytelling Arc)
> "Chia tài liệu nguồn thành hành trình 4 bước kể chuyện qua infographic:
> - Giai đoạn 1: Hiện trạng thị trường (Bối cảnh & Điểm nghẽn)
> - Giai đoạn 2: Bước chuyển dịch công nghệ / xu hướng mới
> - Giai đoạn 3: Cuộc đua giữa các đối thủ chính
> - Giai đoạn 4: Viễn cảnh thị trường trong 3-5 năm tới
> Với mỗi giai đoạn, cung cấp 1 câu chuyện ngắn gọn kèm 1 con số minh họa."
