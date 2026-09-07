---
name: market-to-notebooklm
description: Quy trình trích xuất, chuẩn hóa báo cáo số liệu thị trường thành tài liệu tối ưu cho NotebookLM và điều phối tạo dàn bài Infographic
---

# Skill: Market Data to NotebookLM & Infographic Pipeline

## Mục Đích
Hướng dẫn Agent và người dùng thực hiện trọn vẹn luồng công việc từ thu thập thông tin thị trường, chuẩn hóa nguồn nạp (Source Prep) cho NotebookLM, đến trích xuất bản thiết kế Infographic và sinh giao diện Infographic trực tiếp trong Antigravity.

## Quy Trình 4 Bước

### Bước 1: Thu Thập & Chuẩn Hóa Dữ Liệu Thị Trường
1. Lưu tài liệu thô (báo cáo PDF, bài báo, ghi chú, file CSV số liệu) vào thư mục `data/raw/`.
2. Chạy script chuẩn hóa hoặc sử dụng Agent để chuyển đổi dữ liệu thô sang Markdown có cấu trúc tại `notebooklm_sources/`:
   ```bash
   python3 scripts/prepare_notebooklm_source.py --input data/raw/market_report.txt --output notebooklm_sources/market_source_v1.md
   ```

### Bước 2: Nạp Vào NotebookLM (Tùy Chọn Phương Thức)
- **Cách 1 (Google Drive Sync qua MCP)**: File trong thư mục `notebooklm_sources/` được đẩy lên Google Drive qua `gdrive` MCP. Mở NotebookLM, chọn nguồn trực tiếp từ thư mục Google Drive đó. Mọi cập nhật trên Drive sẽ tự động cập nhật vào NotebookLM.
- **Cách 2 (Browser Subagent Tự Động Hóa)**: Antigravity sử dụng subagent trình duyệt mở `notebooklm.google.com`, nạp file nguồn từ `notebooklm_sources/` trực tiếp.
- **Cách 3 (Thủ công / Copy-Paste)**: Mở NotebookLM và dán nội dung từ `notebooklm_sources/` vào mục *Add source -> Copied text* hoặc tải file `.md`/`.pdf`.

### Bước 3: Trích Xuất Dàn Ý Infographic Với NotebookLM
Sử dụng bộ template prompt tại `prompts/notebooklm_infographic_prompts.md` để yêu cầu NotebookLM tạo:
1. **Infographic Data Spec**: Danh sách chỉ số cô đọng, tỷ lệ phần trăm, so sánh định lượng.
2. **Visual Hierarchy Blueprint**: Phân khu bố cục (Hero, Stat Cards, Chart Data, Key Takeaways).
Lưu kết quả phản hồi của NotebookLM vào `output/notebooklm_notes/infographic_brief.md`.

### Bước 4: Render Infographic Thành Phẩm Ngay Trong Antigravity
Agent đọc `output/notebooklm_notes/infographic_brief.md` và sinh ra:
1. File HTML/CSS tương tác đẹp mắt (responsive, modern glassmorphism hoặc dark mode) tại `output/infographics/index.html`.
2. File SVG độc lập (vector sắc nét) để nhúng vào báo cáo trình chiếu (Slide) hoặc xuất ảnh.
