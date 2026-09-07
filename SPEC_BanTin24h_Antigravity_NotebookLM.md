# ĐẶC TẢ YÊU CẦU KỸ THUẬT
# Hệ thống Bản tin 24h tự động — Antigravity × NotebookLM

**Người yêu cầu:** Dương Minh Quang (Ryan) — Chuyên viên Mua hàng ngành hàng Điện thoại
**Ngày lập:** 06/09/2026
**Phiên bản:** 1.0
**Người thực hiện:** Antigravity (AI coding agent)

---

## 0. EXECUTIVE SUMMARY

### Mục tiêu
Xây dựng một hệ thống chạy tự động hoàn toàn mỗi ngày, thay thế việc phải đọc báo từ 10-15 nguồn khác nhau. Đầu ra là **một bộ infographic PNG** được đẩy lên GitHub, truy cập qua một link cố định. Người dùng lướt 3-5 phút là nắm toàn cảnh; tin nào đáng quan tâm thì tự tìm hiểu sâu qua link nguồn đính kèm.

### Kiến trúc chốt
```
[Antigravity: Thu thập + Xác minh + Chuẩn hóa]
            ↓  (đẩy 1 file nguồn tổng hợp .md)
[NotebookLM: Tổng hợp + Phân tích + Sinh Infographic PNG]
            ↓  (tải PNG về)
[Antigravity: Đóng gói + Push GitHub Pages]
            ↓
[Người dùng: mở link đọc]
```

### Phân vai — vì sao chia như vậy

| Việc | Ai làm | Lý do |
|---|---|---|
| Crawl tin tức, gọi API số liệu | **Antigravity** | NotebookLM không tự đi lấy tin theo lịch được. Nó chỉ xử lý nguồn được nạp vào. |
| Xác minh chéo, khử trùng lặp, gắn nhãn độ tin cậy | **Antigravity** | Cần logic có kiểm soát, deterministic. Không giao cho AI tự do phán đoán. |
| Số liệu realtime (vàng, USD, VN-Index, xăng dầu) | **Antigravity** | Cần chính xác tuyệt đối, lấy từ API/nguồn chính thống. Tuyệt đối KHÔNG để AI sinh ra con số. |
| Tổng hợp, viết văn, rút "vì sao quan trọng" | **NotebookLM** | Đây là thế mạnh gốc: đọc nhiều nguồn, tổng hợp có trích dẫn, chống bịa đặt (grounded). |
| **Thiết kế & sinh Infographic** | **NotebookLM** | Theo yêu cầu người dùng. NotebookLM có tính năng Infographic xuất PNG sẵn có, chất lượng thiết kế tốt, không cần Antigravity tự code phần trình bày. |
| Lưu trữ, publish, thông báo | **Antigravity** | Việc hạ tầng. |

### Cảnh báo rủi ro quan trọng — ĐỌC TRƯỚC KHI LÀM

> **[GIẢ ĐỊNH CẦN KIỂM CHỨNG]** Tính đến thời điểm lập spec, **NotebookLM bản consumer KHÔNG có API chính thức công khai**. Google chỉ cung cấp API ở bản **Gemini Notebook Enterprise (Google Cloud)**, đang ở trạng thái *Preview*, và bản Enterprise này **chỉ expose Audio Overview — CHƯA expose Infographic**.
>
> Do đó, việc tự động hóa NotebookLM ở mức "chạy nền hoàn toàn tự động" hiện chỉ khả thi qua **thư viện không chính thức** (ví dụ `notebooklm-py`), vốn dùng endpoint nội bộ của Google và **có thể hỏng bất cứ lúc nào**.
>
> **Antigravity BẮT BUỘC phải làm Bước 1 (Spike kiểm chứng) trước khi code bất cứ thứ gì khác.** Xem Mục 9.

---

## 1. PHẠM VI NỘI DUNG BẢN TIN

Bản tin gồm **2 khối lớn**, chia thành các module. Mỗi module là một trang infographic riêng.

### KHỐI 1 — BẢN TIN THỜI SỰ 24H

#### 1.1. Bảng chỉ số (Dashboard số liệu)
Bắt buộc có, đặt ở trang đầu tiên. Mỗi chỉ số phải hiển thị: **giá trị hiện tại + thay đổi tuyệt đối + thay đổi % so với phiên trước + mũi tên xu hướng**.

| Chỉ số | Chi tiết cần lấy | Nguồn đề xuất |
|---|---|---|
| Giá vàng | SJC (mua/bán), vàng nhẫn 9999, giá vàng thế giới (XAU/USD), chênh lệch VN–thế giới | SJC, PNJ, DOJI, Kitco |
| Tỷ giá USD | USD/VND — tỷ giá trung tâm NHNN, giá mua/bán Vietcombank, giá chợ tự do; chỉ số DXY | SBV, Vietcombank |
| VN-Index | Điểm số, +/- điểm, %, khối lượng, giá trị giao dịch, khối ngoại mua/bán ròng; kèm HNX-Index, UPCoM | HOSE, CafeF, Vietstock |
| Giá xăng dầu | RON 95-III, E5 RON 92-II, dầu DO; ngày điều chỉnh gần nhất và ngày điều chỉnh kế tiếp | Bộ Công Thương, Petrolimex |

**Bổ sung đề xuất (không có trong yêu cầu gốc nhưng nên có, vì liên quan trực tiếp công việc mua hàng):**
- Tỷ giá **CNY/VND** — phần lớn linh kiện, phụ kiện, hàng ICT nhập từ Trung Quốc.
- Tỷ giá **KRW/VND** — liên quan Samsung.
- **Lãi suất điều hành NHNN** khi có thay đổi.

#### 1.2. Tin thời sự tổng hợp (trong nước + quốc tế)
Các lĩnh vực: **Kinh tế · Chính trị · Văn hóa · Giáo dục · Y tế**, cộng thêm **Tình hình chiến sự / xung đột quốc tế**.

Quy tắc lựa chọn:
- Chỉ lấy tin phát sinh trong **24 giờ gần nhất** (tính từ thời điểm chạy).
- Tối đa **12 tin trong nước** + **10 tin quốc tế**, xếp theo mức độ quan trọng.
- Tin quốc tế **phải được dịch sang tiếng Việt**, giữ nguyên tên riêng.
- Mỗi tin phải có: tiêu đề tiếng Việt · 2 câu tóm tắt · nhãn lĩnh vực · nhãn độ tin cậy · link nguồn.

#### 1.3. Chuyên mục Tài chính
Ba nhóm nội dung:

**a) Tài chính trong nước:** tin nổi bật về thị trường, ngân hàng, trái phiếu, bất động sản; **chính sách đầu tư mới** (nghị định, thông tư, quyết định của Chính phủ / NHNN / Bộ Tài chính / UBCKNN).

**b) Tài chính quốc tế (dịch tiếng Việt):** động thái Fed, ECB, BOJ, PBoC; diễn biến chỉ số lớn (Dow, S&P 500, Nasdaq, Nikkei, Shanghai); giá dầu Brent/WTI; **chính sách đầu tư của nước ngoài** — đặc biệt các chính sách tác động tới dòng vốn vào Việt Nam.

**c) Quét trang tin đầu tư:** tổng hợp góc nhìn, khuyến nghị, dự báo từ các trang chuyên đầu tư trong nước và quốc tế. **Bắt buộc gắn nhãn "Quan điểm/Nhận định — không phải khuyến nghị đầu tư".**

> **Lưu ý bắt buộc:** Toàn bộ nội dung tài chính chỉ mang tính thông tin. Hệ thống không được đưa ra khuyến nghị mua/bán. Cuối mục Tài chính phải có dòng miễn trừ trách nhiệm.

---

### KHỐI 2 — BẢN TIN CÔNG NGHỆ

#### 2.1. Top từ khóa đang tìm kiếm (hot trend)
- Top 10-15 từ khóa xu hướng tại **Việt Nam**, và top 10 **toàn cầu**.
- Nguồn: Google Trends (Daily Trends, RSS/API cho geo=VN và geo=worldwide).
- Hiển thị: từ khóa · khối lượng tìm kiếm ước tính · mức tăng · phân loại chủ đề.
- **Đánh dấu riêng các từ khóa thuộc ngành ICT** — đây là tín hiệu nhu cầu thị trường.

#### 2.2. Top chủ đề người dùng công nghệ đang quan tâm
- Quét các cộng đồng: Reddit (r/Android, r/apple, r/smartphones), Tinhte, Voz, các group/fanpage công nghệ lớn tại VN, X/Twitter.
- Trả về: **top 8-10 chủ đề** đang được thảo luận nhiều nhất, kèm **tâm lý người dùng** (tích cực / tiêu cực / trung lập) và **số lượng thảo luận ước tính**.
- Nêu rõ: người dùng đang khen gì, chê gì, đang so sánh sản phẩm nào với sản phẩm nào.

#### 2.3. Tin sản phẩm ICT mới ra mắt
Phạm vi: **điện thoại · máy tính bảng · phụ kiện · laptop**.

Với mỗi sản phẩm mới, bắt buộc có:
- Tên sản phẩm, hãng, phân khúc giá
- Ngày ra mắt / ngày mở bán tại VN (nếu có)
- Cấu hình rút gọn: chip, RAM/ROM, màn hình, pin, camera
- Giá công bố (nguyên tệ + quy đổi VND)
- Điểm khác biệt so với đời trước và so với đối thủ cùng tầm giá

**Ưu tiên cao nhất:** các hãng Android mà người dùng phụ trách — **Vivo, Realme**, và các hãng Android khác (Samsung, Xiaomi, OPPO, Honor, TECNO, Infinix...). Apple để ở mức thông tin tham khảo.

#### 2.4. Marketshare các hãng
- Tổng hợp số liệu thị phần từ **Counterpoint Research, IDC, Canalys, Omdia, StatCounter, GfK**.
- Phạm vi: **Toàn cầu · Đông Nam Á · Việt Nam** (ưu tiên VN cao nhất).
- Chỉ đăng khi có **báo cáo mới**; nếu trong 24h không có báo cáo mới thì hiển thị số liệu kỳ gần nhất kèm ghi rõ **"Số liệu kỳ [Q/tháng], công bố ngày [ngày]"** — tuyệt đối không để người đọc nhầm là số liệu mới.
- Kèm biến động thị phần so với kỳ trước (điểm %).

---

## 3. KIẾN TRÚC HỆ THỐNG

### 3.1. Sơ đồ luồng

```
┌──────────────────────────────────────────────────────┐
│  GIAI ĐOẠN A — THU THẬP  (Antigravity, ~10-15 phút)  │
├──────────────────────────────────────────────────────┤
│  A1. Lấy số liệu chỉ số (API/scrape nguồn chính thống)│
│  A2. Crawl RSS + API tin tức theo danh sách nguồn     │
│  A3. Lấy Google Trends VN + Global                    │
│  A4. Quét cộng đồng công nghệ                         │
│  A5. Kiểm tra báo cáo marketshare mới                 │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  GIAI ĐOẠN B — XỬ LÝ  (Antigravity, ~3-5 phút)       │
├──────────────────────────────────────────────────────┤
│  B1. Khử trùng lặp (gom tin cùng sự kiện)             │
│  B2. Xác minh chéo → gán nhãn độ tin cậy              │
│  B3. Chấm điểm & xếp hạng độ quan trọng               │
│  B4. Dịch tin quốc tế sang tiếng Việt                 │
│  B5. Xuất file nguồn tổng hợp: daily_source.md        │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  GIAI ĐOẠN C — NOTEBOOKLM  (~10-20 phút, bất đồng bộ) │
├──────────────────────────────────────────────────────┤
│  C1. Tạo/làm mới notebook của ngày                    │
│  C2. Upload daily_source.md làm source                │
│  C3. Gọi lệnh sinh Infographic cho từng module        │
│  C4. Poll cho tới khi xong → tải PNG về               │
│  C5. (Tùy chọn) Sinh Audio Overview                   │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  GIAI ĐOẠN D — PUBLISH  (Antigravity, ~2 phút)       │
├──────────────────────────────────────────────────────┤
│  D1. Kiểm tra chất lượng PNG (kích thước, số lượng)   │
│  D2. Đặt tên chuẩn, đưa vào cấu trúc thư mục theo ngày│
│  D3. Sinh trang index.html + trang lưu trữ            │
│  D4. Commit & push lên GitHub                         │
│  D5. Gửi thông báo kèm link                           │
└──────────────────────────────────────────────────────┘
```

### 3.2. Cấu trúc thư mục dự án

```
bantin-24h/
├── config/
│   ├── sources.yaml           # Danh sách nguồn tin, có bật/tắt & trọng số
│   ├── modules.yaml           # Bật/tắt từng module bản tin
│   ├── schedule.yaml          # Cấu hình lịch chạy
│   └── notebooklm.yaml        # Cấu hình notebook, style infographic
├── src/
│   ├── collectors/            # A — Thu thập
│   │   ├── indices.py         # Vàng, USD, VN-Index, xăng dầu
│   │   ├── news_rss.py
│   │   ├── trends.py
│   │   ├── community.py
│   │   └── marketshare.py
│   ├── processors/            # B — Xử lý
│   │   ├── dedup.py
│   │   ├── verify.py          # Xác minh chéo, gán nhãn tin cậy
│   │   ├── ranker.py
│   │   └── translator.py
│   ├── notebooklm/            # C — Tích hợp NotebookLM
│   │   ├── client.py          # Lớp bọc, có cơ chế dự phòng
│   │   ├── prompts.py         # Prompt sinh infographic
│   │   └── downloader.py
│   ├── publisher/             # D — Xuất bản
│   │   ├── quality_check.py
│   │   ├── site_builder.py
│   │   └── git_push.py
│   └── notifier.py
├── templates/
│   └── source_template.md     # Khung file nguồn nạp vào NotebookLM
├── output/
│   └── 2026/09/06/
│       ├── source/daily_source.md
│       ├── raw/               # JSON thô, phục vụ truy vết
│       └── png/               # Infographic kết quả
├── docs/                      # GitHub Pages publish từ đây
│   ├── index.html             # Bản tin mới nhất
│   ├── archive.html           # Lưu trữ
│   └── 2026-09-06/
├── logs/
├── tests/
├── .env.example
└── README.md
```

---

## 4. GIAI ĐOẠN A — THU THẬP DỮ LIỆU

### 4.1. Nguyên tắc bất di bất dịch

1. **Số liệu KHÔNG bao giờ do AI sinh ra.** Mọi con số (giá vàng, tỷ giá, chỉ số, giá xăng) phải lấy trực tiếp từ nguồn, lưu kèm timestamp và URL nguồn. Nếu không lấy được → hiển thị "Không lấy được số liệu" chứ **tuyệt đối không được ước lượng, nội suy, hay dùng số của ngày hôm trước mà không ghi chú**.
2. **Mỗi mẩu tin phải giữ nguyên link nguồn gốc** xuyên suốt pipeline.
3. **Tôn trọng nguồn:** đọc `robots.txt`, đặt `User-Agent` rõ ràng, giới hạn tốc độ tối đa 1 request/giây/domain. Ưu tiên RSS và API chính thức hơn scrape HTML.
4. **Không đăng lại toàn văn bài báo.** Chỉ tóm tắt và trích dẫn ngắn kèm link. Đây là ràng buộc bản quyền, không phải tùy chọn.

### 4.2. Danh sách nguồn (khai báo trong `config/sources.yaml`)

**Số liệu chỉ số:**
- Vàng: `sjc.com.vn`, `pnj.com.vn`, `doji.vn`, `kitco.com`
- Tỷ giá: `sbv.gov.vn` (tỷ giá trung tâm), `vietcombank.com.vn`, `investing.com` (DXY)
- Chứng khoán: `hsx.vn`, `cafef.vn`, `vietstock.vn`, `fireant.vn`
- Xăng dầu: `moit.gov.vn`, `petrolimex.com.vn`

**Tin tức trong nước:**
`vnexpress.net` · `tuoitre.vn` · `thanhnien.vn` · `vietnamnet.vn` · `baochinhphu.vn` · `cafef.vn` · `vietstock.vn` · `theleader.vn` · `nhipcaudautu.vn` · `tapchitaichinh.vn`

**Tin tức quốc tế:**
`reuters.com` · `bloomberg.com` · `apnews.com` · `bbc.com` · `cnbc.com` · `ft.com` · `nikkei.com` · `scmp.com`

**Công nghệ:**
`gsmarena.com` · `theverge.com` · `androidauthority.com` · `9to5google.com` · `notebookcheck.net` · `tinhte.vn` · `genk.vn` · `vnreview.vn` · `cellphones.com.vn/sforum`

**Marketshare:**
`counterpointresearch.com` · `idc.com` · `canalys.com` · `omdia.tech.informa.com` · `gs.statcounter.com`

**Trends & cộng đồng:**
Google Trends (VN + Global) · Reddit API · Voz · Tinhte · X/Twitter

> Antigravity: đưa toàn bộ danh sách này vào file config để người dùng tự thêm/bớt nguồn mà **không cần sửa code**. Mỗi nguồn có các trường: `url`, `type` (rss/api/scrape), `enabled`, `weight`, `category`, `region`.

### 4.3. Xử lý khi nguồn lỗi
- Retry tối đa **3 lần**, giãn cách lũy tiến (2s → 8s → 32s).
- Sau 3 lần vẫn lỗi: ghi log, bỏ qua nguồn đó, **pipeline vẫn tiếp tục chạy**.
- Nếu số nguồn lỗi vượt **30% tổng số nguồn** → vẫn xuất bản tin nhưng chèn cảnh báo "Bản tin hôm nay thiếu dữ liệu từ N nguồn" và gửi cảnh báo riêng cho người dùng.
- **Một nguồn chết không bao giờ được làm sập cả bản tin.**

---

## 5. GIAI ĐOẠN B — XỬ LÝ & XÁC MINH

### 5.1. Khử trùng lặp
Nhiều báo đưa cùng một sự kiện. Cần gom lại thành **một cụm sự kiện**:
- So khớp theo độ tương đồng ngữ nghĩa của tiêu đề + nội dung (ngưỡng đề xuất: 0.85).
- Chọn bài của nguồn có trọng số cao nhất làm bài đại diện; các bài còn lại lưu vào danh sách `corroborating_sources`.

### 5.2. Hệ thống nhãn độ tin cậy — **BẮT BUỘC**

Mỗi tin phải mang **đúng một nhãn**, và nhãn này phải **hiển thị rõ trên infographic**:

| Nhãn | Điều kiện | Cách hiển thị |
|---|---|---|
| ✅ **XÁC THỰC** | Có ≥2 nguồn độc lập uy tín, hoặc là công bố chính thức từ cơ quan/doanh nghiệp | Màu xanh lá |
| ⚠️ **MỘT NGUỒN** | Chỉ 1 nguồn đưa tin, chưa có nguồn khác xác nhận | Màu vàng |
| ❓ **TIN ĐỒN / CHƯA XÁC MINH** | Nguồn là leak, rò rỉ, "theo nguồn tin thân cận", tin từ mạng xã hội | Màu cam, tách thành khu vực riêng |
| 💭 **NHẬN ĐỊNH** | Quan điểm, dự báo, phân tích — không phải sự kiện | Màu xám, ghi rõ "Không phải khuyến nghị" |

> Đây là yêu cầu **không thương lượng**. Một bản tin trộn lẫn tin đồn với tin xác thực còn tệ hơn không có bản tin, vì nó dẫn tới quyết định sai.

### 5.3. Chấm điểm độ quan trọng
Điểm tổng hợp từ các yếu tố (trọng số cấu hình được):
- Độ uy tín nguồn (0-30)
- Số nguồn cùng đưa tin (0-25)
- Độ liên quan tới ngành ĐTDĐ / bán lẻ / mua hàng (0-25) — **trọng số cao vì đúng nghề của người dùng**
- Độ mới (0-10)
- Mức độ lan truyền / thảo luận (0-10)

### 5.4. Dịch thuật
Tin quốc tế dịch sang tiếng Việt tự nhiên. Giữ nguyên: tên riêng, tên tổ chức, thuật ngữ tài chính chuẩn (Fed, GDP, CPI...). **Không dịch máy thô** — phải đọc trôi chảy như người Việt viết.

### 5.5. Đầu ra: `daily_source.md`

Đây là file duy nhất nạp vào NotebookLM. Cấu trúc bắt buộc — Antigravity dùng `templates/source_template.md`:

```markdown
# BẢN TIN 24H — [Ngày] [Thứ], [dd/mm/yyyy]
Kỳ dữ liệu: từ [dd/mm/yyyy HH:mm] đến [dd/mm/yyyy HH:mm] (giờ Việt Nam)
Số nguồn đã quét: [N] | Số nguồn lỗi: [M]

## PHẦN 1 — CHỈ SỐ THỊ TRƯỜNG
### Vàng
- SJC mua vào: [x] tr.đ/lượng | bán ra: [y] tr.đ/lượng | Thay đổi: [+/-z] ([%])
  Nguồn: [URL] | Cập nhật: [HH:mm dd/mm]
[... các chỉ số khác theo đúng khuôn mẫu này ...]

## PHẦN 2 — TIN THỜI SỰ TRONG NƯỚC
### [Lĩnh vực] — [ĐỘ TIN CẬY: XÁC THỰC]
**[Tiêu đề]**
[Tóm tắt 2-3 câu]
Nguồn chính: [URL] | Nguồn xác nhận: [URL], [URL]

[... tiếp tục cho các phần còn lại ...]
```

**Quy tắc:** file này là **sự thật gốc**. NotebookLM chỉ được tổng hợp và trình bày lại từ đây, **không được bổ sung thông tin từ bên ngoài**. Prompt phải nói rõ điều này.

---

## 6. GIAI ĐOẠN C — TÍCH HỢP NOTEBOOKLM

### 6.1. Chọn phương án tích hợp

Antigravity phải đánh giá và chọn theo **thứ tự ưu tiên** sau. Chỉ chuyển xuống phương án dưới khi phương án trên chứng minh là không khả thi:

| # | Phương án | Ưu điểm | Nhược điểm |
|---|---|---|---|
| **1** | **Thư viện không chính thức** (`notebooklm-py` hoặc tương đương) | Truy cập đầy đủ tính năng, **có Infographic xuất PNG**, có cơ chế tự làm mới phiên đăng nhập | Dùng endpoint nội bộ Google, Google có thể đổi bất cứ lúc nào → **rủi ro hỏng cao** |
| **2** | **Tự động hóa trình duyệt** (Playwright) trên giao diện web NotebookLM | Dùng đúng giao diện chính thức, không phụ thuộc thư viện bên thứ ba | Giòn khi Google đổi giao diện; chậm; cần xử lý đăng nhập cẩn thận |
| **3** | **Gemini Notebook Enterprise API** (Google Cloud) | Chính thức, ổn định, có hỗ trợ | Đang ở Preview; **chưa expose Infographic**; cần tài khoản Google Cloud Enterprise, phát sinh chi phí |
| **4** | **Phương án dự phòng — không dùng NotebookLM cho infographic** | Hoàn toàn kiểm soát được, không bao giờ hỏng vì bên thứ ba | Antigravity phải tự dựng lớp thiết kế |

**Yêu cầu bắt buộc về kiến trúc:** viết `src/notebooklm/client.py` theo **interface trừu tượng**, để đổi giữa 4 phương án chỉ bằng **sửa config, không sửa code nghiệp vụ**.

```python
class InfographicProvider(ABC):
    @abstractmethod
    def create_notebook(self, title: str) -> str: ...
    @abstractmethod
    def upload_source(self, notebook_id: str, file_path: Path) -> str: ...
    @abstractmethod
    def generate_infographic(self, notebook_id: str, prompt: str,
                              orientation: str, detail_level: str) -> str: ...
    @abstractmethod
    def wait_and_download(self, job_id: str, out_path: Path,
                          timeout_sec: int = 900) -> Path: ...
```

### 6.2. Phương án dự phòng (Fallback) — BẮT BUỘC PHẢI CÓ

Nếu NotebookLM lỗi (hết phiên đăng nhập, đổi API, quá tải, timeout), hệ thống **không được im lặng bỏ ngày đó**. Thứ tự dự phòng:

1. **Thử lại** tối đa 2 lần, cách nhau 5 phút.
2. Vẫn lỗi → **tự sinh infographic bằng HTML/CSS rồi chụp thành PNG** (Playwright screenshot). Antigravity chuẩn bị sẵn một bộ template HTML tối giản nhưng sạch sẽ cho mục đích này. Chất lượng thiết kế có thể kém hơn NotebookLM, nhưng **bản tin vẫn ra đúng giờ**.
3. Đánh dấu bản tin đó là `"Chế độ dự phòng"` ở góc trang.
4. Gửi cảnh báo cho người dùng: "Bản tin hôm nay dùng bản dự phòng do NotebookLM lỗi. Lý do: [...]".

> Nguyên tắc: **thà bản tin xấu hơn một chút còn hơn không có bản tin.**

### 6.3. Prompt sinh Infographic

Với mỗi module, gọi NotebookLM sinh một infographic riêng. Prompt phải:
- Chỉ định rõ **chỉ dùng dữ liệu trong source, không bổ sung từ bên ngoài**
- Yêu cầu **giữ nguyên nhãn độ tin cậy** đúng màu quy định
- Yêu cầu **giữ nguyên con số chính xác đến từng chữ số**
- Yêu cầu bố cục dọc (portrait) — vì người dùng đọc trên điện thoại
- Yêu cầu tiếng Việt, font dễ đọc

**Về mặt thiết kế:** theo yêu cầu người dùng, **giao toàn quyền thẩm mỹ cho NotebookLM**. Antigravity **không được** áp đặt màu sắc, bố cục chi tiết, hay tự vẽ lại. Chỉ ràng buộc 4 điểm cứng: (1) hướng dọc, (2) tiếng Việt, (3) số liệu chính xác, (4) nhãn độ tin cậy đúng màu.

Mẫu prompt cho module chỉ số:

```
Từ nguồn đã cung cấp, tạo một infographic khổ dọc, hoàn toàn bằng tiếng Việt,
trình bày Bảng chỉ số thị trường ngày [ngày].

Yêu cầu bắt buộc:
- CHỈ dùng số liệu có trong nguồn. Không suy đoán, không bổ sung.
- Mỗi con số phải giữ nguyên chính xác như trong nguồn.
- Mỗi chỉ số hiển thị: giá trị, mức thay đổi, phần trăm, mũi tên xu hướng.
- Tăng dùng màu xanh lá, giảm dùng màu đỏ.
- Ghi rõ thời điểm cập nhật của từng chỉ số.

Về phong cách thiết kế: bạn tự quyết định bố cục, màu sắc, biểu tượng và cách
trình bày sao cho dễ đọc nhất trên màn hình điện thoại. Ưu tiên sự rõ ràng
và khả năng nắm bắt nhanh trong vài giây.
```

Tương tự cho từng module còn lại — Antigravity soạn đầy đủ trong `src/notebooklm/prompts.py`.

### 6.4. Số lượng trang đầu ra
Đề xuất **6-8 trang PNG**, mỗi trang một module:
1. Trang bìa + Bảng chỉ số
2. Thời sự trong nước
3. Thời sự quốc tế + chiến sự
4. Chuyên mục Tài chính
5. Công nghệ: Trends + chủ đề nóng
6. Công nghệ: Sản phẩm mới
7. Công nghệ: Marketshare
8. Góc Mua hàng + Lịch sự kiện

### 6.5. Xử lý bất đồng bộ
Việc sinh infographic mất **vài phút mỗi trang** và không đồng bộ. Yêu cầu:
- Poll trạng thái mỗi 15 giây, timeout **15 phút/trang**.
- Sinh **song song tối đa 3 trang** cùng lúc (tránh bị giới hạn tốc độ).
- Nếu 1 trang lỗi, các trang khác vẫn tiếp tục; trang lỗi chuyển sang dự phòng.

---

## 7. GIAI ĐOẠN D — XUẤT BẢN LÊN GITHUB

### 7.1. Kiểm tra chất lượng trước khi publish
Trước khi commit, kiểm tra tự động:
- Đủ số trang PNG mong đợi (hoặc đã đánh dấu trang lỗi)
- Mỗi file PNG > 50KB (loại file rỗng/hỏng)
- Kích thước ảnh đạt tối thiểu 1080px chiều rộng
- **Kiểm tra chéo số liệu:** trích xuất văn bản từ PNG (OCR) và đối chiếu các con số chính với `daily_source.md`. Nếu lệch → cảnh báo. *(Đây là chốt chặn cuối chống việc AI đọc/vẽ sai số.)*

### 7.2. Cấu trúc GitHub
- Repository: **riêng tư hoặc công khai** tùy người dùng chọn (mặc định: riêng tư, bật GitHub Pages).
- Publish từ nhánh `main`, thư mục `/docs`.
- Link cố định: `https://[username].github.io/bantin-24h/`
- URL bản tin theo ngày: `.../2026-09-06/`

### 7.3. Trang index.html
Tự sinh, gồm:
- Toàn bộ PNG của ngày mới nhất, xếp dọc, tối ưu cho điện thoại
- Nút chuyển ngày trước / ngày sau
- Link tới trang lưu trữ
- **Danh sách link nguồn dạng văn bản, đặt dưới ảnh** — vì link trong ảnh PNG không bấm được. Đây là điểm bắt buộc để người dùng "cái nào hay thì tự tìm hiểu thêm".
- Thời điểm cập nhật cuối

> **Lưu ý quan trọng:** PNG không cho phép bấm link. Nên trang HTML **phải** có danh sách nguồn dạng text đi kèm, đánh số khớp với số thứ tự tin trên infographic.

### 7.4. Lưu trữ
- Giữ toàn bộ lịch sử, không xóa.
- Trang `archive.html` liệt kê theo tháng, có ô tìm kiếm theo từ khóa.
- Giữ lại cả `daily_source.md` và JSON thô để truy vết khi cần kiểm chứng.

### 7.5. Commit
```
git commit -m "Bản tin 24h — 06/09/2026"
```
Push tự động. Nếu push lỗi (xung đột, mất mạng): retry 3 lần, sau đó giữ file ở local và cảnh báo.

---

## 8. LỊCH CHẠY & THÔNG BÁO

### 8.1. Lịch
- **Chạy chính: 05:30 sáng giờ Việt Nam, hàng ngày.** Bản tin sẵn sàng khoảng 06:00-06:15, trước giờ đi làm.
- Kỳ dữ liệu: 24 giờ tính ngược từ 05:30.
- Cơ chế: cron (Linux) / launchd (macOS) / GitHub Actions (nếu chạy trên cloud).
- **Khuyến nghị: chạy trên GitHub Actions** để không phụ thuộc máy cá nhân có bật hay không. *(Cần cân nhắc: đăng nhập NotebookLM trên môi trường CI phức tạp hơn — Antigravity đánh giá và báo lại ở giai đoạn spike.)*

### 8.2. Thông báo
Khi bản tin sẵn sàng, gửi thông báo kèm:
- Link bản tin
- 3 tin quan trọng nhất trong ngày (dạng chữ, để đọc lướt ngay trên thông báo)
- Cảnh báo nếu có nguồn lỗi hoặc chạy ở chế độ dự phòng

Kênh: Telegram bot (đơn giản nhất, đề xuất) hoặc email. Cấu hình được.

### 8.3. Nếu một ngày chạy lỗi hoàn toàn
Vẫn phải publish một trang tối giản ghi rõ: "Bản tin ngày [x] không tạo được. Lý do: [...]. Hệ thống sẽ tự chạy lại lúc [giờ]." **Không được để trang trống hoặc hiển thị bản tin cũ mà không ghi chú** — điều đó khiến người đọc tưởng nhầm là tin mới.

---

## 9. KẾ HOẠCH TRIỂN KHAI THEO GIAI ĐOẠN

### GIAI ĐOẠN 0 — SPIKE KIỂM CHỨNG *(BẮT BUỘC LÀM ĐẦU TIÊN — 1 ngày)*

**Không viết dòng code sản phẩm nào trước khi hoàn thành bước này.**

Cần trả lời dứt điểm 5 câu hỏi:
1. Có tự động hóa được NotebookLM để sinh Infographic không? Bằng phương án nào trong 4 phương án ở Mục 6.1?
2. Phiên đăng nhập duy trì được bao lâu? Có cơ chế tự làm mới không?
3. Có bị giới hạn số lần sinh infographic mỗi ngày không? Con số cụ thể?
4. Chất lượng infographic NotebookLM sinh ra với **nội dung tiếng Việt** có đạt không? *(Đây là rủi ro thực tế — nhiều công cụ sinh ảnh xử lý dấu tiếng Việt kém.)*
5. Số liệu trên infographic có khớp chính xác với source không, hay bị AI viết lại sai?

**Đầu ra của giai đoạn 0:** một báo cáo ngắn + **1 file PNG mẫu thật** sinh từ dữ liệu thật. Trình cho người dùng duyệt trước khi đi tiếp.

> Nếu câu 4 hoặc câu 5 cho kết quả không đạt → **dừng lại, báo cáo, và cùng người dùng chọn lại phương án thiết kế** (khả năng cao là chuyển sang phương án 4: Antigravity tự dựng infographic bằng HTML/CSS). Không tự ý đi tiếp với chất lượng kém.

### GIAI ĐOẠN 1 — MVP *(3-5 ngày)*
- Thu thập: chỉ số + tin trong nước + tin quốc tế
- Xử lý: khử trùng lặp + nhãn tin cậy + xếp hạng
- NotebookLM: sinh 3 trang infographic
- Publish GitHub + trang index
- Chạy tay được từ đầu tới cuối

**Tiêu chí nghiệm thu GĐ1:** chạy một lệnh, 20 phút sau có link GitHub với 3 trang PNG đọc được, số liệu chính xác, mỗi tin có nguồn.

### GIAI ĐOẠN 2 — Đầy đủ nội dung *(3-5 ngày)*
- Thêm toàn bộ khối Công nghệ (trends, cộng đồng, sản phẩm, marketshare)
- Thêm chuyên mục Tài chính đầy đủ
- Đủ 6-8 trang infographic
- Trang lưu trữ + tìm kiếm

### GIAI ĐOẠN 3 — Tự động hóa & module chuyên sâu *(2-3 ngày)*
- Cron / GitHub Actions chạy nền
- Thông báo Telegram
- Cơ chế dự phòng hoàn chỉnh
- 4 module bổ sung ở Mục 2
- Bảng theo dõi tình trạng hệ thống

### GIAI ĐOẠN 4 — Tinh chỉnh *(liên tục)*
- Điều chỉnh trọng số xếp hạng theo phản hồi thực tế
- Thêm/bớt nguồn
- Tùy chọn Audio Overview

---

## 10. TIÊU CHÍ NGHIỆM THU TỔNG THỂ

Hệ thống được coi là hoàn thành khi đạt **toàn bộ** các tiêu chí sau:

**Về độ tin cậy**
- [ ] Chạy tự động 7 ngày liên tiếp, tỷ lệ thành công ≥ 90%
- [ ] Không ngày nào bản tin trống mà không có thông báo lý do
- [ ] Cơ chế dự phòng đã được kiểm chứng bằng cách chủ động gây lỗi NotebookLM

**Về độ chính xác** *(quan trọng nhất)*
- [ ] Kiểm tra thủ công 30 con số ngẫu nhiên trên infographic → **khớp 100%** với nguồn gốc
- [ ] Không có tin nào thiếu link nguồn
- [ ] Nhãn độ tin cậy gắn đúng, kiểm tra trên mẫu 20 tin
- [ ] Không có tin nào cũ hơn 24 giờ lọt vào (trừ mục marketshare có ghi chú kỳ)

**Về trải nghiệm**
- [ ] Đọc trọn bản tin trên điện thoại trong **dưới 5 phút**
- [ ] Chữ tiếng Việt trên PNG rõ nét, đủ dấu, không vỡ
- [ ] Mọi tin đều bấm được vào link nguồn từ trang HTML
- [ ] Link cố định, mở ra là thấy bản mới nhất

**Về vận hành**
- [ ] Thêm/bớt nguồn tin chỉ cần sửa file config, không sửa code
- [ ] Bật/tắt từng module qua config
- [ ] Có log đủ chi tiết để truy nguyên khi bản tin sai

---

## 11. NHỮNG ĐIỀU TUYỆT ĐỐI KHÔNG ĐƯỢC LÀM

1. **Không để AI tự bịa số liệu.** Mọi con số phải truy vết được về nguồn.
2. **Không trộn tin đồn với tin xác thực** mà không gắn nhãn phân biệt rõ.
3. **Không đăng lại toàn văn bài báo** — chỉ tóm tắt + link.
4. **Không đưa ra khuyến nghị đầu tư.** Chỉ đưa thông tin và nhận định có gắn nhãn.
5. **Không để hệ thống im lặng khi lỗi.** Lỗi phải hiển thị và phải gửi cảnh báo.
6. **Không hiển thị bản tin cũ như thể là bản tin mới.**
7. **Không hardcode danh sách nguồn hay API key vào code.** Dùng config và biến môi trường.
8. **Không tự ý đổi phần thiết kế infographic** khi đã giao cho NotebookLM — trừ khi giai đoạn 0 chứng minh chất lượng không đạt và người dùng đã đồng ý đổi phương án.

---

## 12. CÂU HỎI ANTIGRAVITY CẦN LÀM RÕ VỚI NGƯỜI DÙNG

Trước khi bắt đầu Giai đoạn 1, xác nhận các điểm sau:

1. Tài khoản Google dùng cho NotebookLM là tài khoản nào? Là bản miễn phí, Google One AI Premium, hay Workspace/Enterprise? *(Ảnh hưởng trực tiếp tới giới hạn sử dụng và khả năng dùng API chính thức.)*
2. Repository GitHub để riêng tư hay công khai?
3. Chạy trên MacBook cá nhân hay trên GitHub Actions?
4. Kênh thông báo: Telegram hay email?
5. Có sẵn API key trả phí nào cho tin tức (NewsAPI, GNews...) không, hay chỉ dùng RSS miễn phí?
6. Ngân sách vận hành hàng tháng cho phép ở mức nào? *(Có thể phát sinh chi phí API dịch thuật, tin tức, hoặc Google Cloud.)*

---

*Hết đặc tả.*
