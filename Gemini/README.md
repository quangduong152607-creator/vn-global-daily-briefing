# Hệ Thống Bản Tin 24h Tự Động — Antigravity × NotebookLM

**Người sử dụng:** Dương Minh Quang (Ryan) — Chuyên viên Mua hàng ngành hàng Điện thoại  
**Mục tiêu:** Tự động hóa việc tổng hợp tin tức từ 10-15 nguồn, xác minh chéo số liệu, nạp chuẩn hóa vào Google NotebookLM và xuất bản bản tin dạng Infographic trực quan, đọc được trong 3-5 phút trên smartphone.

---

## 1. Kiến Trúc Vận Hành Hoàn Chỉnh

```text
market-intel-notebooklm/
├── .agents/
│   └── rules/
│       └── infographic-standards.md      # Quy chuẩn 4 nhãn tin cậy & thiết kế infographic
├── config/
│   ├── sources.yaml                      # Danh mục nguồn Vàng, Tỷ giá, Chứng khoán, Xăng, Báo chí
│   ├── modules.yaml                      # Cấu hình bật/tắt 8 module bản tin
│   ├── schedule.yaml                     # Lịch chạy 05:30 sáng hàng ngày & chính sách retry
│   ├── notebooklm.yaml                   # Cấu hình NotebookLM & Fallback Engine
│   └── mcp_config.json                   # Cấu hình MCP (Google Drive, Web Fetch, Filesystem)
├── src/
│   ├── collectors/
│   │   ├── indices.py                    # Vàng SJC/Kitco, Tỷ giá USD/CNY/KRW, VN-Index, Xăng Petrolimex
│   │   ├── news_rss.py                   # Quét RSS VnExpress, CafeF, Tinhte, Android Authority, BBC
│   │   ├── trends.py                     # Google Trends VN & Global, phát hiện từ khóa ICT
│   │   └── marketshare.py                # Thị phần Counterpoint/Canalys kèm kỳ báo cáo chuẩn
│   ├── processors/
│   │   ├── dedup.py                      # Khử trùng lặp, gom cụm sự kiện
│   │   ├── verify.py                     # Gán 4 nhãn: ✅ XÁC THỰC, ⚠️ MỘT NGUỒN, ❓ TIN ĐỒN, 💭 NHẬN ĐỊNH
│   │   └── ranker.py                     # Chấm điểm ưu tiên ngành hàng ĐTDĐ (Vivo, Realme, bán lẻ)
│   ├── notebooklm/
│   │   ├── client.py                     # Interface trừu tượng InfographicProvider & Fallback Engine
│   │   └── prompts.py                    # Bộ prompt 8 module được chuẩn hóa cho NotebookLM
│   └── publisher/
│       ├── site_builder.py               # Sinh trang web di động docs/index.html & docs/archive.html
│       └── quality_check.py              # Kiểm tra số liệu, kích thước và link nguồn trước khi xuất bản
├── templates/
│   └── source_template.md                # Khung mẫu daily_source.md (Ground Truth)
├── output/
│   └── [YYYY]/[MM]/[DD]/
│       └── source/daily_source.md        # File nguồn duy nhất nạp vào NotebookLM
├── docs/                                 # Thư mục xuất bản GitHub Pages
│   ├── index.html                        # Bản tin mới nhất kèm danh sách link nguồn có thể click
│   └── archive.html                      # Kho lưu trữ các kỳ bản tin
├── main.py                               # Bộ điều phối chính (chạy 1 lệnh toàn bộ pipeline)
└── README.md                             # Tài liệu kỹ thuật
```

---

## 2. Hướng Dẫn Vận Hành

### Chạy pipeline tự động một lệnh:
```bash
python3 main.py
```
Toàn bộ quá trình thu thập, khử trùng lặp, gán nhãn độ tin cậy, xuất `daily_source.md` và sinh trang web xuất bản tại `docs/index.html` sẽ hoàn tất trong vòng 15-30 giây.

### Xem bản tin trên trình duyệt máy Mac:
Mở trực tiếp file:
👉 `docs/index.html` bằng Google Chrome hoặc Safari.

### Nạp vào NotebookLM:
File nguồn đã chuẩn hóa tại:
👉 `output/[YYYY]/[MM]/[DD]/source/daily_source.md`
Tải file này lên NotebookLM để:
1. Tạo **Audio Overview (Deep Dive Podcast)** 2 người dẫn bằng tiếng Việt/Anh.
2. Dùng bộ prompt tại `src/notebooklm/prompts.py` để trích xuất thêm góc nhìn chuyên sâu.
