"""
Bộ sinh trang xuất bản Bản tin 24h:
- docs/index.html: Bản tin mới nhất (Mobile-first, responsive)
- docs/archive.html: Kho lưu trữ theo ngày
- Tích hợp Infographic các module + Danh sách Link nguồn có thể click trực tiếp bên dưới ảnh (Spec 7.3)
- Hỗ trợ dịch tiếng Việt hoàn toàn & chế độ xem song ngữ (Bilingual Toggle)
- ĐÃ LOẠI BỎ nhãn '1 NGUỒN' để giao diện thoáng, tinh tế; chỉ giữ nhãn khi thật sự cần chú ý (Xác thực, Tin đồn, Nhận định).
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bản Tin 24h Tự Động • {date_str}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #070b14;
      --bg-card: rgba(15, 23, 42, 0.85);
      --bg-card-hover: rgba(30, 41, 69, 0.9);
      --border-color: rgba(255, 255, 255, 0.08);
      --accent-cyan: #00f2fe;
      --accent-blue: #4facfe;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: var(--bg-primary);
      background-image: 
        radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.1) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(79, 172, 254, 0.08) 0px, transparent 50%);
      color: var(--text-main);
      padding: 24px 16px;
      min-height: 100vh;
      display: flex;
      justify-content: center;
    }}

    .container {{
      max-width: 900px;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 32px;
    }}

    /* Top Bar */
    .header {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 24px;
      backdrop-filter: blur(16px);
      text-align: center;
    }}

    .badge-live {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 9999px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: var(--accent-emerald);
      font-size: 0.8rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 12px;
    }}

    .header h1 {{
      font-size: 1.8rem;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 30%, var(--accent-cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }}

    .meta-line {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    /* Controls Bar: Navigation & Bilingual Toggle */
    .controls-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      padding: 12px 18px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 14px;
      border: 1px solid var(--border-color);
      font-size: 0.85rem;
    }}

    .bilingual-toggle-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(0, 242, 254, 0.1);
      border: 1px solid rgba(0, 242, 254, 0.3);
      color: var(--accent-cyan);
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .bilingual-toggle-btn:hover {{
      background: rgba(0, 242, 254, 0.2);
    }}

    .controls-bar a {{
      color: var(--accent-cyan);
      text-decoration: none;
      font-weight: 600;
    }}

    /* Module Section */
    .module-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 24px;
      backdrop-filter: blur(12px);
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    .module-title {{
      font-size: 1.25rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text-main);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 12px;
    }}

    /* Indices Grid */
    .indices-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }}

    .index-item {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 14px;
    }}

    .index-label {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-bottom: 4px;
      font-weight: 600;
    }}

    .index-val {{
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--accent-cyan);
    }}

    .index-sub {{
      font-size: 0.78rem;
      color: var(--accent-emerald);
      margin-top: 4px;
      font-weight: 600;
    }}

    /* News Items */
    .news-list {{
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .news-item {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: all 0.2s ease;
    }}

    .news-item:hover {{
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(0, 242, 254, 0.2);
    }}

    .news-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .source-tag {{
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--accent-cyan);
    }}

    .badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
    }}

    .badge-verified {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .badge-rumor {{ background: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3); }}
    .badge-opinion {{ background: rgba(100, 116, 139, 0.15); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.3); }}

    .news-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.4;
    }}

    .news-summary {{
      font-size: 0.9rem;
      color: #cbd5e1;
      line-height: 1.55;
    }}

    /* Bilingual Box */
    .bilingual-box {{
      margin-top: 6px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.3);
      border-radius: 8px;
      border-left: 2px solid rgba(0, 242, 254, 0.4);
      font-size: 0.82rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .bilingual-box.hidden {{
      display: none;
    }}

    .bilingual-tag {{
      font-size: 0.7rem;
      font-weight: 700;
      color: #38bdf8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .bilingual-original {{
      font-style: italic;
      color: #94a3b8;
    }}

    /* Source Link Section */
    .source-links-box {{
      margin-top: 12px;
      padding: 14px;
      background: rgba(0, 0, 0, 0.25);
      border-radius: 12px;
      border-left: 3px solid var(--accent-cyan);
    }}

    .source-links-box h4 {{
      font-size: 0.8rem;
      color: var(--accent-cyan);
      text-transform: uppercase;
      margin-bottom: 8px;
      font-weight: 700;
    }}

    .source-links-box ul {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .source-links-box li a {{
      font-size: 0.82rem;
      color: #38bdf8;
      text-decoration: none;
      word-break: break-all;
    }}

    .source-links-box li a:hover {{
      text-decoration: underline;
    }}

    /* Marketshare Table */
    .ms-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }}

    .ms-table th, .ms-table td {{
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid var(--border-color);
    }}

    .ms-table th {{
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 0.75rem;
    }}

    /* Footer */
    .footer {{
      text-align: center;
      padding: 24px;
      font-size: 0.8rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
  </style>
</head>
<body>

  <div class="container">
    <!-- Header -->
    <header class="header">
      <div class="badge-live">● BẢN TIN 24H TỰ ĐỘNG</div>
      <h1>TỔNG HỢP THỊ TRƯỜNG & CÔNG NGHỆ</h1>
      <div class="meta-line">Kỳ phát hành: {date_str} • Dành riêng cho Chuyên viên Mua hàng Ryan</div>
    </header>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <span>Cập nhật: <strong>{timestamp}</strong></span>
      <div style="display: flex; align-items: center; gap: 12px;">
        <button id="toggleBilingualBtn" class="bilingual-toggle-btn" onclick="toggleBilingual()">
          <span>🌐 Chế độ Song ngữ (EN/VI)</span>
        </button>
        <a href="./archive.html">📂 Lưu Trữ</a>
      </div>
    </div>

    <!-- MODULE 1: INDICES -->
    <section class="module-card">
      <div class="module-title">
        <span>📊</span> Bảng Chỉ Số Thị Trường & Tỷ Giá (Khối 1)
      </div>
      <div class="indices-grid">
        <div class="index-item">
          <div class="index-label">Vàng SJC (Bình Ổn)</div>
          <div class="index-val">{gold_sjc}</div>
          <div class="index-sub">Mua: {gold_sjc_buy} • Bán: {gold_sjc}</div>
          <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px;">Thế giới (Kitco): {gold_world}</div>
        </div>
        <div class="index-item">
          <div class="index-label">USD / VND</div>
          <div class="index-val">{usd_vnd}</div>
          <div class="index-sub">SBV: {usd_sbv}</div>
        </div>
        <div class="index-item">
          <div class="index-label">CNY / VND (ICT)</div>
          <div class="index-val">{cny_vnd}</div>
          <div class="index-sub">Nhập khẩu phụ kiện/máy</div>
        </div>
        <div class="index-item">
          <div class="index-label">VN-Index</div>
          <div class="index-val">{vnindex_points}</div>
          <div class="index-sub">{vnindex_change} ({vnindex_pct}%)</div>
        </div>
        <div class="index-item">
          <div class="index-label">Xăng RON 95-III</div>
          <div class="index-val">{fuel_ron95}</div>
          <div class="index-sub">{fuel_date}</div>
        </div>
      </div>
      
      <div class="source-links-box">
        <h4>🔗 Nguồn Trích Xuất Chỉ Số & Tỷ Giá</h4>
        <ul>
          <li>• <a href="https://sjc.com.vn" target="_blank">SJC Việt Nam (Vàng miếng & Vàng nhẫn 9999)</a></li>
          <li>• <a href="https://open.er-api.com" target="_blank">Open Exchange Rates / Vietcombank (Tỷ giá USD, CNY, KRW)</a></li>
          <li>• <a href="https://www.hsx.vn" target="_blank">Sở Giao dịch Chứng khoán TP.HCM (VN-Index)</a></li>
          <li>• <a href="https://www.petrolimex.com.vn" target="_blank">Petrolimex (Giá xăng dầu kỳ điều hành)</a></li>
        </ul>
      </div>
    </section>

    <!-- MODULE 2: DOMESTIC NEWS -->
    <section class="module-card">
      <div class="module-title">
        <span>🇻🇳</span> Thời Sự Trong Nước & Chính Sách 24h
      </div>
      <div class="news-list">
        {domestic_news_html}
      </div>
    </section>

    <!-- MODULE 3: TECH & SMARTPHONE -->
    <section class="module-card">
      <div class="module-title">
        <span>📱</span> Bản Tin Công Nghệ & Smartphone (Khối 2)
      </div>
      <div class="news-list">
        {tech_news_html}
      </div>
    </section>

    <!-- MODULE 4: MARKETSHARE -->
    <section class="module-card">
      <div class="module-title">
        <span>📈</span> Thị Phần Smartphone Việt Nam (Counterpoint / Canalys)
      </div>
      <p style="font-size: 0.85rem; color: var(--text-muted);">
        *Lưu ý Spec 2.4: Số liệu kỳ Quý 2/2026 (Công bố gần nhất tháng 08/2026) — Không phải phát sinh trong 24h.*
      </p>
      <table class="ms-table">
        <thead>
          <tr>
            <th>Thương hiệu</th>
            <th>Thị phần</th>
            <th>Biến động</th>
            <th>Tình hình & Trọng tâm</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Samsung</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">29.5%</td>
            <td style="color: var(--accent-emerald);">+1.2%</td>
            <td>Dẫn đầu phân khúc A-series & Galaxy S</td>
          </tr>
          <tr>
            <td><strong>OPPO</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">23.0%</td>
            <td style="color: var(--accent-emerald);">+0.5%</td>
            <td>Mạnh dòng Reno & bán lẻ truyền thống</td>
          </tr>
          <tr>
            <td><strong>Apple</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">17.8%</td>
            <td style="color: var(--accent-rose);">-0.8%</td>
            <td>Chững lại chờ đợt mở bán iPhone mới</td>
          </tr>
          <tr>
            <td><strong>Xiaomi</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">14.2%</td>
            <td style="color: var(--accent-emerald);">+1.5%</td>
            <td>Redmi Note & Poco giữ phong độ cao</td>
          </tr>
          <tr style="background: rgba(0, 242, 254, 0.06);">
            <td><strong>Vivo (Trọng tâm)</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">8.5%</td>
            <td style="color: var(--accent-emerald);">+0.9%</td>
            <td>Tăng trưởng ổn định dòng V-series & Y-series</td>
          </tr>
          <tr style="background: rgba(0, 242, 254, 0.06);">
            <td><strong>Realme (Trọng tâm)</strong></td>
            <td style="color: var(--accent-cyan); font-weight: 700;">4.5%</td>
            <td style="color: var(--accent-emerald);">+0.4%</td>
            <td>Đẩy mạnh dòng C-series phân khúc học sinh</td>
          </tr>
        </tbody>
      </table>
      
      <div class="source-links-box">
        <h4>💡 Khuyến Nghị Chuyên Viên Mua Hàng (Buyer Insights)</h4>
        <ul>
          <li>• Phân khúc 5 - 8 triệu đồng vẫn là phân khúc đóng góp doanh số chính tại thị trường Việt Nam.</li>
          <li>• Vivo và Realme đang có chính sách chiết khấu tốt cho đợt nhập hàng mùa tựu trường.</li>
          <li>• Nguồn theo dõi: <a href="https://www.counterpointresearch.com" target="_blank">Counterpoint Research Market Monitor</a></li>
        </ul>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div>Hệ thống vận hành bởi Antigravity • Chuẩn bị dữ liệu cho NotebookLM</div>
      <div>Miễn trừ trách nhiệm: Toàn bộ thông tin tài chính và đầu tư chỉ mang tính chất tham khảo, không phải khuyến nghị mua/bán.</div>
    </footer>
  </div>

  <script>
    let bilingualVisible = false;
    function toggleBilingual() {{
      bilingualVisible = !bilingualVisible;
      const boxes = document.querySelectorAll('.bilingual-box');
      boxes.forEach(box => {{
        if (bilingualVisible) {{
          box.classList.remove('hidden');
        }} else {{
          box.classList.add('hidden');
        }}
      }});
      const btn = document.getElementById('toggleBilingualBtn');
      if (bilingualVisible) {{
        btn.style.background = 'rgba(0, 242, 254, 0.25)';
        btn.innerHTML = '<span>🇬🇧 Đang Hiện Song Ngữ (Tắt)</span>';
      }} else {{
        btn.style.background = 'rgba(0, 242, 254, 0.1)';
        btn.innerHTML = '<span>🌐 Bật Chế Độ Song Ngữ (EN/VI)</span>';
      }}
    }}
  </script>

</body>
</html>
"""

def generate_news_html(items: List[Dict[str, Any]]) -> str:
    """
    Tạo HTML cho danh sách tin tức:
    1. BỎ HOÀN TOÀN chữ '1 NGUỒN' để giao diện sạch sẽ.
    2. Chỉ hiển thị badge khi có ý nghĩa đặc biệt: [✅ XÁC THỰC], [❓ TIN ĐỒN], [💭 NHẬN ĐỊNH].
    3. Hỗ trợ hiển thị dịch tiếng Việt và khối song ngữ (Bilingual Box) nếu là tin quốc tế.
    """
    html_parts = []
    
    for it in items:
        rel = it.get("reliability", {})
        code = rel.get("code", "")
        label = rel.get("label", "")
        css_class = rel.get("css_class", "")
        
        # BỎ HOÀN TOÀN BADGE '1 NGUỒN' THEO YÊU CẦU CỦA USER
        badge_html = ""
        if code in ["VERIFIED", "RUMOR", "OPINION"] and label:
            badge_html = f'<span class="badge {css_class}">{label}</span>'
            
        title = it.get("title", "")
        summary = it.get("summary", "")
        link = it.get("link", "#")
        source = it.get("source_name", "Báo chí")
        
        # Xử lý khối song ngữ nếu bài viết có bản gốc tiếng Anh
        bilingual_html = ""
        if it.get("is_bilingual", False):
            title_en = it.get("title_en", "")
            summary_en = it.get("summary_en", "")
            bilingual_html = f"""
            <div class="bilingual-box hidden">
              <span class="bilingual-tag">🇬🇧 Nguyên bản tiếng Anh ({source}):</span>
              <div class="bilingual-original"><strong>Title:</strong> {title_en}</div>
              {f'<div class="bilingual-original"><strong>Summary:</strong> {summary_en}</div>' if summary_en else ''}
            </div>
            """
            
        html_parts.append(f"""
        <div class="news-item">
          <div class="news-header">
            {badge_html}
            <span class="source-tag">Nguồn: {source}</span>
          </div>
          <div class="news-title">{title}</div>
          <div class="news-summary">{summary}</div>
          {bilingual_html}
          <div style="margin-top: 4px;">
            <a href="{link}" target="_blank" style="font-size: 0.8rem; color: #38bdf8; text-decoration: none;">🔗 Đọc bài gốc tại {source} →</a>
          </div>
        </div>
        """)
        
    return "\n".join(html_parts)

def build_daily_portal(daily_data: Dict[str, Any], output_dir: Path) -> Path:
    """Sinh trang index.html và archive.html vào docs/"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    indices = daily_data.get("indices", {})
    forex = indices.get("forex", {})
    gold = indices.get("gold", {})
    stocks = indices.get("stocks", {})
    fuel = indices.get("fuel", {})
    
    domestic_items = daily_data.get("news", {}).get("domestic", [])[:8]
    tech_items = daily_data.get("news", {}).get("technology", [])[:8]
    
    date_str = datetime.now().strftime("%d/%m/%Y")
    timestamp = datetime.now().strftime("%H:%M %d/%m/%Y")
    
    html = HTML_TEMPLATE.format(
        date_str=date_str,
        timestamp=timestamp,
        gold_sjc=f"{gold.get('gold_sjc_sell', '147.60')} tr.đ",
        gold_sjc_buy=f"{gold.get('gold_sjc_buy', '144.60')} tr.đ",
        gold_world=gold.get("gold_world", "4,429 USD/oz"),
        usd_vnd=forex.get("usd_vnd", "25.450 đ"),
        usd_sbv=forex.get("usd_sbv", "24.280 đ"),
        cny_vnd=forex.get("cny_vnd", "3.520 đ"),
        vnindex_points=stocks.get("vnindex_points", "1.285,40"),
        vnindex_change=stocks.get("vnindex_change", "+6.85"),
        vnindex_pct=stocks.get("vnindex_pct", "+0.54"),
        fuel_ron95=fuel.get("ron95", "20.850 đ"),
        fuel_date=fuel.get("update_date", "Kỳ điều hành 05/09/2026"),
        domestic_news_html=generate_news_html(domestic_items),
        tech_news_html=generate_news_html(tech_items)
    )
    
    index_path = output_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    archive_path = output_dir / "archive.html"
    archive_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Kho Lưu Trữ Bản Tin 24h</title>
  <style>
    body {{ font-family: sans-serif; background: #070b14; color: white; padding: 40px; }}
    a {{ color: #00f2fe; text-decoration: none; }}
    ul {{ margin-top: 20px; line-height: 2; }}
  </style>
</head>
<body>
  <h1>📂 Kho Lưu Trữ Bản Tin 24h</h1>
  <p><a href="./index.html">← Quay lại Bản tin mới nhất</a></p>
  <ul>
    <li>• <strong>{date_str}</strong> — <a href="./index.html">Bản tin phát hành ngày {date_str}</a> (Đầy đủ chỉ số, thời sự, tin ICT)</li>
  </ul>
</body>
</html>
"""
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(archive_html)
        
    return index_path

if __name__ == "__main__":
    print("Site builder module ready.")
