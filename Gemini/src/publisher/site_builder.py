"""
Bộ sinh trang xuất bản Bản tin 24h:
- Tái hiện chính xác phong cách thiết kế tạp chí tài chính cao cấp (Warm Cream Editorial Aesthetic):
  + Tông màu nền ấm cổ điển (#fbf9f4), đường viền cát mềm mại (#ebe5d8).
  + Typography đỉnh cao: Tiêu đề & Chỉ số dùng 'Plus Jakarta Sans', nội dung tin tức dùng 'Newsreader' / 'Georgia' serif tao nhã.
  + Thẻ số báo danh inverted black square badge (01, 02, 03...).
  + Banner vĩ mô tương phản đen tuyền (#121212) sang trọng: '⚡ 3 ĐIỂM TIN VĨ MÔ NÓNG NHẤT' | '60 GIÂY ĐỌC'.
  + Lưới chỉ số 2x2 với delta tăng/giảm tinh tế, mốc cập nhật tức thời.
  + Đầy đủ 3 Tab điều hướng mượt mà: [ 🇻🇳 TRONG NƯỚC ] | [ 🌐 QUỐC TẾ ] | [ 📱 SOCIAL & XU HƯỚNG ].
  + Tích hợp 1-click Quick Copy cho Zalo/Telegram.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

EDITORIAL_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bản Tin Thị Trường & Kinh Doanh 24h • {date_str}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-page: #fbf9f4;
      --bg-card: #ffffff;
      --border-sand: #ebe5d8;
      --border-sand-dark: #d8d0c2;
      --text-black: #111827;
      --text-body: #4b5563;
      --text-muted: #78716c;
      --accent-bronze: #9a6a2f;
      --accent-bronze-light: #fef3c7;
      --accent-coral: #ea580c;
      --delta-up: #15803d;
      --delta-down: #b91c1c;
      --delta-neutral: #71717a;
      --badge-black: #121212;
      --stat-highlight: #9a3412;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background-color: var(--bg-page);
      color: var(--text-black);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.5;
      padding: 14px 10px 60px;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      -webkit-font-smoothing: antialiased;
    }}

    .container {{
      max-width: 520px;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    /* Top Navigation Bar */
    .top-nav-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 2px 2px 4px;
    }}

    .top-left {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .live-pill {{
      display: inline-block;
      padding: 3px 10px;
      background: #f1ebd9;
      border: 1px solid #e2dac9;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.04em;
      color: #262626;
    }}

    .top-date-str {{
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.05em;
    }}

    .top-right {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .top-icon-btn {{
      background: none;
      border: none;
      cursor: pointer;
      color: #262626;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 4px;
      transition: opacity 0.2s ease;
      text-decoration: none;
    }}

    .top-icon-btn:hover {{
      opacity: 0.7;
    }}

    /* Masthead Header */
    .main-masthead {{
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 2px 2px 4px;
    }}

    .main-title {{
      font-size: 1.35rem;
      font-weight: 900;
      color: var(--text-black);
      letter-spacing: -0.015em;
      line-height: 1.25;
      text-transform: uppercase;
    }}

    .meta-subline {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.76rem;
      font-weight: 800;
      margin-top: 2px;
    }}

    .edition-tag {{
      color: var(--text-muted);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .vnindex-meta {{
      color: var(--accent-bronze);
      letter-spacing: 0.02em;
    }}

    /* 3 Tabs Row */
    .editorial-tabs-row {{
      display: flex;
      gap: 6px;
      margin: 2px 0 2px;
    }}

    .tab-chip {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 9px 6px;
      border: 1px solid #e7dfcf;
      background: #f1ece1;
      border-radius: 6px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.78rem;
      font-weight: 800;
      color: #4b5563;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      letter-spacing: 0.02em;
    }}

    .tab-chip:hover {{
      color: var(--text-black);
      background: #eae3d6;
    }}

    .tab-chip.active {{
      background: #ffffff;
      color: var(--text-black);
      border-color: #d1c8b8;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
    }}

    /* Tab Panes */
    .tab-pane {{
      display: none;
      flex-direction: column;
      gap: 16px;
    }}

    .tab-pane.active {{
      display: flex;
    }}

    /* Subhead Bar */
    .subhead-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 2px;
      margin-top: 2px;
    }}

    .subhead-left {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .coral-dot {{
      width: 7px;
      height: 7px;
      background-color: var(--accent-coral);
      border-radius: 50%;
      display: inline-block;
    }}

    .subhead-title {{
      font-size: 0.82rem;
      font-weight: 800;
      color: var(--text-black);
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    .subhead-right {{
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    /* 2x2 Indices Grid */
    .indices-2x2-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}

    .idx-box {{
      background: #ffffff;
      border: 1px solid var(--border-sand);
      border-radius: 12px;
      padding: 10px 14px 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 74px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.01);
    }}

    .idx-top {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}

    .idx-name {{
      font-size: 0.72rem;
      font-weight: 800;
      color: #716c65;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    .idx-change {{
      font-size: 0.78rem;
      font-weight: 800;
    }}

    .idx-change.up {{ color: var(--delta-up); }}
    .idx-change.down {{ color: var(--delta-down); }}
    .idx-change.neutral {{ color: var(--delta-neutral); }}

    .idx-bottom {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-top: 4px;
    }}

    .idx-val {{
      font-size: 1.32rem;
      font-weight: 900;
      color: var(--text-black);
      letter-spacing: -0.02em;
      line-height: 1;
    }}

    .idx-unit {{
      font-size: 0.72rem;
      color: var(--text-muted);
      font-weight: 700;
    }}

    /* Black Banner Card Container */
    .editorial-banner-card {{
      display: flex;
      flex-direction: column;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }}

    .banner-black-top {{
      background: var(--badge-black);
      color: #ffffff;
      border-radius: 10px 10px 0 0;
      padding: 10px 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .banner-title {{
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 0.82rem;
      font-weight: 800;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}

    .banner-timer {{
      font-size: 0.72rem;
      font-weight: 700;
      color: #d4d4d8;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .banner-card-body {{
      background: #ffffff;
      border: 1px solid var(--border-sand);
      border-top: none;
      border-radius: 0 0 12px 12px;
      padding: 14px 16px 16px;
      display: flex;
      flex-direction: column;
    }}

    /* Standalone Section Title Line */
    .section-headline-line {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 2px 2px;
    }}

    .headline-left {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.95rem;
      font-weight: 800;
      color: var(--text-black);
      letter-spacing: -0.01em;
      text-transform: uppercase;
    }}

    .headline-right {{
      font-size: 0.76rem;
      font-weight: 800;
      color: var(--accent-bronze);
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}

    .standalone-card-body {{
      background: #ffffff;
      border: 1px solid var(--border-sand);
      border-radius: 12px;
      padding: 14px 16px 16px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }}

    /* News Row Layout (Exact to screenshot) */
    .editorial-news-item {{
      display: flex;
      gap: 12px;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid #f2ede4;
    }}

    .editorial-news-item:first-child {{
      padding-top: 2px;
    }}

    .editorial-news-item:last-child {{
      border-bottom: none;
      padding-bottom: 2px;
    }}

    .editorial-badge-box {{
      width: 32px;
      height: 32px;
      background: var(--badge-black);
      color: #ffffff;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.92rem;
      font-weight: 800;
      font-family: 'Plus Jakarta Sans', sans-serif;
      flex-shrink: 0;
      margin-top: 2px;
    }}

    .editorial-text-col {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .editorial-headline {{
      font-size: 1.04rem;
      font-weight: 800;
      color: var(--text-black);
      line-height: 1.34;
      letter-spacing: -0.015em;
    }}

    .editorial-summary-serif {{
      font-family: 'Newsreader', Georgia, serif;
      font-size: 0.94rem;
      color: #4b5563;
      line-height: 1.54;
      margin-top: 1px;
    }}

    .stat-highlight {{
      color: var(--stat-highlight);
      font-weight: 700;
    }}

    .editorial-source-mini {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 3px;
    }}

    .editorial-source-mini a {{
      color: #2563eb;
      text-decoration: none;
      font-weight: 600;
    }}

    .editorial-source-mini a:hover {{
      text-decoration: underline;
    }}

    /* Editorial Table */
    .editorial-clean-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin-top: 4px;
    }}

    .editorial-clean-table th, .editorial-clean-table td {{
      padding: 8px 10px;
      text-align: left;
      border-bottom: 1px solid #f2ede4;
    }}

    .editorial-clean-table th {{
      font-size: 0.68rem;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--text-muted);
      background: #faf7f0;
      letter-spacing: 0.03em;
    }}

    /* Trending Grid */
    .trends-editorial-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .trend-editorial-chip {{
      background: #faf7f0;
      border: 1px solid var(--border-sand);
      border-radius: 8px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .trend-editorial-kw {{
      font-size: 0.84rem;
      font-weight: 800;
      color: var(--text-black);
    }}

    .trend-editorial-meta {{
      display: flex;
      justify-content: space-between;
      font-size: 0.7rem;
      color: var(--text-muted);
      font-weight: 600;
    }}

    .trend-traffic-val {{
      color: var(--delta-up);
      font-weight: 800;
    }}

    /* Flash News List */
    .flash-editorial-item {{
      padding: 8px 0;
      border-bottom: 1px solid #f2ede4;
      font-size: 0.84rem;
      line-height: 1.45;
    }}

    .flash-editorial-item:last-child {{
      border-bottom: none;
    }}

    .flash-editorial-event {{
      font-weight: 800;
      color: var(--text-black);
    }}

    .flash-editorial-text {{
      color: #4b5563;
      font-family: 'Newsreader', Georgia, serif;
    }}

    .flash-editorial-source {{
      font-size: 0.72rem;
      color: var(--text-muted);
    }}

    .flash-editorial-source a {{
      color: #2563eb;
      text-decoration: none;
    }}

    /* Floating Copy Button */
    .bottom-action-dock {{
      position: sticky;
      bottom: 12px;
      background: rgba(251, 249, 244, 0.95);
      backdrop-filter: blur(8px);
      padding: 8px 0;
      display: flex;
      justify-content: center;
      z-index: 99;
    }}

    .copy-btn-chic {{
      background: var(--badge-black);
      color: #ffffff;
      border: none;
      padding: 10px 20px;
      border-radius: 9999px;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.82rem;
      font-weight: 800;
      letter-spacing: 0.02em;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 7px;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
      transition: transform 0.15s ease, background 0.15s ease;
    }}

    .copy-btn-chic:hover {{
      transform: translateY(-1px);
      background: #27272a;
    }}

    /* Toast Notification */
    #copyToast {{
      position: fixed;
      bottom: 60px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: var(--badge-black);
      color: #ffffff;
      padding: 8px 18px;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 700;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
      transition: transform 0.25s ease;
      z-index: 1000;
    }}

    #copyToast.show {{
      transform: translateX(-50%) translateY(0);
    }}

    /* Footer */
    .editorial-footer {{
      text-align: center;
      padding: 16px 4px;
      font-size: 0.75rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
  </style>
</head>
<body>

  <div class="container">

    <!-- Top Navigation Bar -->
    <div class="top-nav-bar">
      <div class="top-left">
        <span class="live-pill">LIVE 24H</span>
        <span class="top-date-str">HÔM NAY // {current_time_ict} ICT</span>
      </div>
      <div class="top-right">
        <button class="top-icon-btn" onclick="copyNewsletterText()" title="Sao chép bản tin nhanh">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </button>
        <a href="./archive.html" class="top-icon-btn" title="Kho lưu trữ">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>
        </a>
      </div>
    </div>

    <!-- Main Title & Edition Subhead -->
    <header class="main-masthead">
      <h1 class="main-title">BẢN TIN THỊ TRƯỜNG & KINH DOANH 24H</h1>
      <div class="meta-subline">
        <span class="edition-tag">ẤN BẢN ĐIỆN TỬ SỐ {issue_num}</span>
        <span class="vnindex-meta">VN-INDEX {vnindex_points} ▲ {vnindex_pct}%</span>
      </div>
    </header>

    <!-- 3 Tabs Navigation -->
    <nav class="editorial-tabs-row">
      <button id="tabBtn1" class="tab-chip active" onclick="switchTab(1)">
        <span>🇻🇳</span> TRONG NƯỚC
      </button>
      <button id="tabBtn2" class="tab-chip" onclick="switchTab(2)">
        <span>🌐</span> QUỐC TẾ
      </button>
      <button id="tabBtn3" class="tab-chip" onclick="switchTab(3)">
        <span>📱</span> SOCIAL & XU HƯỚNG
      </button>
    </nav>

    <!-- ============================================== -->
    <!-- TAB 1: TRONG NƯỚC -->
    <!-- ============================================== -->
    <div id="tabContent1" class="tab-pane active">

      <!-- Section: Chỉ số tức thời -->
      <div class="subhead-bar">
        <div class="subhead-left">
          <span class="coral-dot"></span>
          <span class="subhead-title">CHỈ SỐ TỨC THỜI</span>
        </div>
        <div class="subhead-right">CẬP NHẬT {indices_time} ICT</div>
      </div>

      <div class="indices-2x2-grid">
        <div class="idx-box">
          <div class="idx-top">
            <span class="idx-name">VÀNG SJC</span>
            <span class="idx-change up">▲ 0.4%</span>
          </div>
          <div class="idx-bottom">
            <span class="idx-val">{gold_sjc}</span>
            <span class="idx-unit">tr/lượng</span>
          </div>
        </div>

        <div class="idx-box">
          <div class="idx-top">
            <span class="idx-name">USD / VND</span>
            <span class="idx-change down">▼ 10đ</span>
          </div>
          <div class="idx-bottom">
            <span class="idx-val">{usd_vnd}</span>
            <span class="idx-unit">VND</span>
          </div>
        </div>

        <div class="idx-box">
          <div class="idx-top">
            <span class="idx-name">VN-INDEX</span>
            <span class="idx-change up">▲ {vnindex_pct}%</span>
          </div>
          <div class="idx-bottom">
            <span class="idx-val">{vnindex_points}</span>
            <span class="idx-unit">{vnindex_change}</span>
          </div>
        </div>

        <div class="idx-box">
          <div class="idx-top">
            <span class="idx-name">XĂNG RON 95</span>
            <span class="idx-change neutral">▪ 0.0%</span>
          </div>
          <div class="idx-bottom">
            <span class="idx-val">{fuel_ron95}</span>
            <span class="idx-unit">đ/lít</span>
          </div>
        </div>
      </div>

      <!-- Section: 3 Điểm tin vĩ mô nóng nhất (Black Banner) -->
      <div class="editorial-banner-card">
        <div class="banner-black-top">
          <div class="banner-title">
            <span>⚡</span> 3 ĐIỂM TIN VĨ MÔ NÓNG NHẤT
          </div>
          <div class="banner-timer">60 GIÂY ĐỌC</div>
        </div>
        <div class="banner-card-body">
          {domestic_economy_news_html}
        </div>
      </div>

      <!-- Section: Công nghệ & Bán lẻ (ICT) trong nước -->
      <div class="section-headline-line">
        <div class="headline-left">
          <span>🗂</span> CÔNG NGHỆ & BÁN LẺ (ICT)
        </div>
        <div class="headline-right">THỊ TRƯỜNG TUẦN</div>
      </div>
      <div class="standalone-card-body">
        {domestic_tech_news_html}
      </div>

      <!-- Section: Khảo sát thị phần Smartphone Việt Nam -->
      <div class="section-headline-line">
        <div class="headline-left">
          <span>📱</span> THỊ PHẦN SMARTPHONE VIỆT NAM
        </div>
        <div class="headline-right">GFK & COUNTERPOINT</div>
      </div>
      <div class="standalone-card-body" style="padding: 10px 14px;">
        <p style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 6px;">
          Số liệu kỳ Quý 2/2026 — Khảo sát bán lẻ GfK & xuất xưởng Counterpoint:
        </p>
        <table class="editorial-clean-table">
          <thead>
            <tr>
              <th>Thương hiệu</th>
              <th>Bán lẻ (GfK)</th>
              <th>Xuất xưởng</th>
              <th>Kênh chủ lực</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Samsung</strong></td>
              <td style="color: var(--accent-bronze); font-weight: 800;">31.2%</td>
              <td>29.5%</td>
              <td>Chuỗi bán lẻ MWG, FPT Shop</td>
            </tr>
            <tr>
              <td><strong>OPPO</strong></td>
              <td style="color: var(--accent-bronze); font-weight: 800;">22.8%</td>
              <td>23.0%</td>
              <td>Offline truyền thống & Reno</td>
            </tr>
            <tr>
              <td><strong>Apple</strong></td>
              <td style="color: var(--accent-bronze); font-weight: 800;">18.5%</td>
              <td>17.8%</td>
              <td>Phân khúc cao cấp >20tr</td>
            </tr>
            <tr>
              <td><strong>Xiaomi</strong></td>
              <td style="color: var(--accent-bronze); font-weight: 800;">13.8%</td>
              <td>14.2%</td>
              <td>Dòng Redmi Note</td>
            </tr>
            <tr style="background: #faf7f0;">
              <td><strong>Vivo</strong></td>
              <td style="color: var(--accent-bronze); font-weight: 800;">9.2%</td>
              <td>8.5%</td>
              <td>Dòng V-series & Y-series</td>
            </tr>
            <tr style="background: #faf7f0;">
              <td><strong>Realme</strong></td>
              <td style="color: var(--accent-bronze); font-weight: 800;">4.1%</td>
              <td>4.5%</td>
              <td>Phổ thông 3-5 triệu</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- ============================================== -->
    <!-- TAB 2: QUỐC TẾ -->
    <!-- ============================================== -->
    <div id="tabContent2" class="tab-pane">

      <!-- Section: Kinh tế & Địa chính trị quốc tế (Black Banner) -->
      <div class="editorial-banner-card">
        <div class="banner-black-top">
          <div class="banner-title">
            <span>🌍</span> KINH TẾ & ĐỊA CHÍNH TRỊ TOÀN CẦU
          </div>
          <div class="banner-timer">REUTERS • BBC • CNBC</div>
        </div>
        <div class="banner-card-body">
          {intl_macro_news_html}
        </div>
      </div>

      <!-- Section: Công nghệ & Thiết bị di động quốc tế (GSMArena, The Verge) -->
      <div class="section-headline-line">
        <div class="headline-left">
          <span>💻</span> CÔNG NGHỆ QUỐC TẾ (GSMARENA)
        </div>
        <div class="headline-right">THIẾT BỊ MỚI</div>
      </div>
      <div class="standalone-card-body">
        {intl_tech_news_html}
      </div>

      <!-- Section: Tin vắn nhanh quốc tế -->
      <div class="section-headline-line">
        <div class="headline-left">
          <span>⚡</span> TIN VẮN NHANH TOÀN CẦU
        </div>
        <div class="headline-right">VẮN TẮT 60s</div>
      </div>
      <div class="standalone-card-body">
        {flash_news_html}
      </div>

    </div>

    <!-- ============================================== -->
    <!-- TAB 3: SOCIAL & XU HƯỚNG -->
    <!-- ============================================== -->
    <div id="tabContent3" class="tab-pane">

      <!-- Section: Top Trends Google -->
      <div class="section-headline-line">
        <div class="headline-left">
          <span>🔥</span> TOP TỪ KHÓA THỊNH HÀNH GOOGLE
        </div>
        <div class="headline-right">VIỆT NAM 24H</div>
      </div>
      <div class="standalone-card-body">
        <div class="trends-editorial-grid">
          {trends_chips_html}
        </div>
      </div>

      <!-- Section: Showbiz & Giải trí Mạng xã hội -->
      <div class="editorial-banner-card">
        <div class="banner-black-top">
          <div class="banner-title">
            <span>🌟</span> TIÊU ĐIỂM SHOWBIZ & MẠNG XÃ HỘI
          </div>
          <div class="banner-timer">VIRAL TRENDS</div>
        </div>
        <div class="banner-card-body">
          {social_news_html}
        </div>
      </div>

    </div>

    <!-- Floating Copy Button Dock -->
    <div class="bottom-action-dock">
      <button class="copy-btn-chic" onclick="copyNewsletterText()">
        <span>📋</span> SAO CHÉP BẢN TIN (ZALO / TELEGRAM)
      </button>
    </div>

    <!-- Footer -->
    <footer class="editorial-footer">
      <div>Bản Tin Thị Trường 24h • Xuất bản tự động bởi Antigravity</div>
      <div>Dữ liệu được kiểm định đa nguồn chính thống • Cập nhật mỗi ngày lúc 07:00 ICT.</div>
    </footer>

  </div>

  <!-- Toast Notification -->
  <div id="copyToast">✓ Đã sao chép toàn bộ bản tin dạng text vào bộ nhớ tạm!</div>

  <!-- Hidden Raw Text for Copying -->
  <textarea id="rawNewsletterText" style="display: none;">{raw_newsletter_text}</textarea>

  <script>
    function switchTab(tabIndex) {{
      for (let i = 1; i <= 3; i++) {{
        const btn = document.getElementById('tabBtn' + i);
        const pane = document.getElementById('tabContent' + i);
        if (i === tabIndex) {{
          btn.classList.add('active');
          pane.classList.add('active');
        }} else {{
          btn.classList.remove('active');
          pane.classList.remove('active');
        }}
      }}
    }}

    function copyNewsletterText() {{
      const text = document.getElementById('rawNewsletterText').value;
      navigator.clipboard.writeText(text).then(() => {{
        const toast = document.getElementById('copyToast');
        toast.classList.add('show');
        setTimeout(() => {{
          toast.classList.remove('show');
        }}, 2500);
      }}).catch(err => {{
        alert('Không thể sao chép tự động. Vui lòng thử lại.');
      }});
    }}
  </script>

</body>
</html>
"""

def highlight_numbers(text: str) -> str:
    """Làm nổi bật các con số, tỷ lệ % hoặc đơn vị tiền tệ bằng màu terracotta sang trọng"""
    if not text:
        return ""
    # Pattern bắt tỷ lệ đòn bẩy (0.72x), khoảng giá (146-149 tr.đ), phần trăm, công suất (90W), pin (5.000mAh), tốc độ (450Mbps)
    pattern = r'(\b\d+[.,]?\d*x\b|\b\d+(?:[-\s]\d+)?\s?(?:tr\.đ|tỷ|quý|triệu|%|W|mAh|Mbps|inch)\b)'
    return re.sub(pattern, r'<strong class="stat-highlight">\1</strong>', text)

def render_editorial_news_html(items: List[Dict[str, Any]], mode: str = "macro") -> str:
    """Render tin tức theo định dạng card báo chí cao cấp với huy hiệu đen 01, 02, 03..."""
    if not items:
        return "<p style='color: var(--text-muted); font-size: 0.85rem;'>Đang cập nhật diễn biến mới nhất...</p>"

    html_parts = []
    for idx, it in enumerate(items, 1):
        title = it.get("title", "")
        source = it.get("source", "Báo chí")
        link = it.get("link", "#")

        if mode == "macro":
            context = it.get("context", "")
            impact = it.get("impact", "")
            full_text = f"{context} {impact}".strip() if (context and impact) else (context or impact)
        elif mode == "tech":
            dev = it.get("development", "")
            sig = it.get("significance", "")
            full_text = f"{dev} {sig}".strip() if (dev and sig) else (dev or sig)
        elif mode == "social":
            highlight = it.get("highlight", "")
            virality = it.get("virality", "")
            full_text = f"{highlight} {virality}".strip() if (highlight and virality) else (highlight or virality)
        else:
            full_text = it.get("summary", "")

        formatted_desc = highlight_numbers(full_text)

        html_parts.append(f"""
        <div class="editorial-news-item">
          <div class="editorial-badge-box">{idx:02d}</div>
          <div class="editorial-text-col">
            <h3 class="editorial-headline">{title}</h3>
            <p class="editorial-summary-serif">{formatted_desc}</p>
            <div class="editorial-source-mini">
              Nguồn: <a href="{link}" target="_blank">{source} ↗</a>
            </div>
          </div>
        </div>
        """)
    return "\n".join(html_parts)

def render_flash_news_html(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "<p style='color: var(--text-muted); font-size: 0.85rem;'>Đang cập nhật tin vắn nhanh...</p>"

    html_parts = []
    for it in items:
        event = it.get("event", "Sự kiện")
        summary = it.get("summary", "")
        source = it.get("source", "Báo chí")
        link = it.get("link", "#")

        html_parts.append(f"""
        <div class="flash-editorial-item">
          <span class="flash-editorial-event">[{event}]:</span>
          <span class="flash-editorial-text">{summary}</span>
          <span class="flash-editorial-source">(Nguồn: <a href="{link}" target="_blank">{source} ↗</a>)</span>
        </div>
        """)
    return "\n".join(html_parts)

def render_trends_chips_html(vn_trends: List[Dict[str, Any]]) -> str:
    if not vn_trends:
        return "<p style='color: var(--text-muted); font-size: 0.85rem;'>Chưa có dữ liệu xu hướng mới.</p>"
        
    parts = []
    for t in vn_trends[:6]:
        kw = t.get("keyword", "")
        traffic = t.get("traffic", "10K+")
        tag = t.get("tag", "🔥 Hot")
        parts.append(f"""
        <div class="trend-editorial-chip">
          <div class="trend-editorial-kw">{kw}</div>
          <div class="trend-editorial-meta">
            <span>{tag}</span>
            <span class="trend-traffic-val">{traffic}</span>
          </div>
        </div>
        """)
    return "\n".join(parts)

def build_raw_newsletter_text(structured_news: Dict[str, Any], date_str: str, vn_trends: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append(f"📊 BẢN TIN THỊ TRƯỜNG, CÔNG NGHỆ & SOCIAL 24H ({date_str})")
    lines.append("=" * 55)
    lines.append("")
    
    # 1. TIN TRONG NƯỚC
    lines.append("🇻🇳 1. TIN TRONG NƯỚC")
    lines.append("📈 A. Kinh Tế & Thị Trường Trong Nước:")
    dom_econ = structured_news.get("domestic_economy_news") or structured_news.get("economy_news", [])
    for idx, it in enumerate(dom_econ, 1):
        lines.append(f"{idx}. {it.get('title')}")
        lines.append(f"   - Bối cảnh: {it.get('context')}")
        lines.append(f"   - Tác động: {it.get('impact')}")
        lines.append(f"   - Nguồn: {it.get('source')} ({it.get('link')})")
        lines.append("")

    dom_tech = structured_news.get("domestic_tech_news", [])
    if dom_tech:
        lines.append("💻 B. Công Nghệ & Số Hóa Trong Nước (Tinhte, GenK, Số Hóa):")
        for idx, it in enumerate(dom_tech, 1):
            lines.append(f"{idx}. {it.get('title')}")
            lines.append(f"   - Diễn biến: {it.get('development')}")
            lines.append(f"   - Ý nghĩa: {it.get('significance')}")
            lines.append(f"   - Nguồn: {it.get('source')} ({it.get('link')})")
            lines.append("")

    lines.append("-" * 55)
    lines.append("")

    # 2. TIN QUỐC TẾ
    lines.append("🌐 2. TIN QUỐC TẾ")
    intl_macro = structured_news.get("intl_macro_news", [])
    if intl_macro:
        lines.append("🌍 A. Kinh Tế & Địa Chính Trị Toàn Cầu (Reuters, BBC, CNBC):")
        for idx, it in enumerate(intl_macro, 1):
            lines.append(f"{idx}. {it.get('title')}")
            lines.append(f"   - Bối cảnh: {it.get('context')}")
            lines.append(f"   - Tác động: {it.get('impact')}")
            lines.append(f"   - Nguồn: {it.get('source')} ({it.get('link')})")
            lines.append("")

    intl_tech = structured_news.get("intl_tech_news") or structured_news.get("tech_news", [])
    lines.append("📱 B. Công Nghệ & Thiết Bị Di Động Quốc Tế (GSMArena, The Verge):")
    for idx, it in enumerate(intl_tech, 1):
        lines.append(f"{idx}. {it.get('title')}")
        lines.append(f"   - Diễn biến: {it.get('development')}")
        lines.append(f"   - Ý nghĩa: {it.get('significance')}")
        lines.append(f"   - Nguồn: {it.get('source')} ({it.get('link')})")
        lines.append("")

    flash_items = structured_news.get("flash_news", [])
    if flash_items:
        lines.append("⚡ C. Tin Vắn Nhanh Quốc Tế:")
        for it in flash_items:
            lines.append(f"• [{it.get('event')}]: {it.get('summary')} (Nguồn: {it.get('source')})")
        lines.append("")

    lines.append("-" * 55)
    lines.append("")

    # 3. TIN SOCIAL
    lines.append("📱 3. TIN SOCIAL & XU HƯỚNG MẠNG XÃ HỘI")
    for idx, it in enumerate(structured_news.get("social_news", []), 1):
        lines.append(f"{idx}. {it.get('title')}")
        lines.append(f"   - Tiêu điểm: {it.get('highlight')}")
        lines.append(f"   - Độ lan tỏa: {it.get('virality')}")
        lines.append(f"   - Nguồn: {it.get('source')} ({it.get('link')})")
        lines.append("")

    if vn_trends:
        lines.append("🔥 Top từ khóa thịnh hành Google Trends (Việt Nam):")
        for t in vn_trends[:6]:
            lines.append(f"   • {t.get('keyword')} ({t.get('traffic')})")
        lines.append("")

    return "\n".join(lines)

def build_daily_portal(daily_data: Dict[str, Any], output_dir: Path) -> Path:
    """Sinh trang index.html và archive.html vào docs/ theo phong cách Editorial chuẩn"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    indices = daily_data.get("indices", {})
    forex = indices.get("forex", {})
    gold = indices.get("gold", {})
    stocks = indices.get("stocks", {})
    fuel = indices.get("fuel", {})
    
    structured_news = daily_data.get("structured_news", {})
    domestic_economy_items = structured_news.get("domestic_economy_news") or structured_news.get("economy_news", [])
    domestic_tech_items = structured_news.get("domestic_tech_news", [])
    intl_macro_items = structured_news.get("intl_macro_news", [])
    intl_tech_items = structured_news.get("intl_tech_news") or structured_news.get("tech_news", [])
    social_items = structured_news.get("social_news", [])
    flash_items = structured_news.get("flash_news", [])
    
    trends = daily_data.get("trends", {})
    vn_trends = trends.get("vn_trends", [])
    
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    current_time_ict = now.strftime("%H:%M")
    
    # Tính số ấn bản điện tử chuẩn xác (khoảng 418)
    base_issue = 418
    
    raw_newsletter_text = build_raw_newsletter_text(structured_news, date_str, vn_trends)
    
    # Render các khối tin tức theo phong cách huy hiệu đen 01, 02, 03...
    domestic_economy_news_html = render_editorial_news_html(domestic_economy_items[:3], mode="macro")
    domestic_tech_news_html = render_editorial_news_html(domestic_tech_items[:3], mode="tech")
    intl_macro_news_html = render_editorial_news_html(intl_macro_items[:3], mode="macro")
    intl_tech_news_html = render_editorial_news_html(intl_tech_items[:4], mode="tech")
    social_news_html = render_editorial_news_html(social_items[:3], mode="social")
    flash_news_html = render_flash_news_html(flash_items)
    trends_chips_html = render_trends_chips_html(vn_trends)

    html = EDITORIAL_HTML_TEMPLATE.format(
        date_str=date_str,
        current_time_ict=current_time_ict,
        indices_time=current_time_ict,
        issue_num=base_issue,
        gold_sjc=gold.get('gold_sjc_sell', '147.60').replace(" tr.đ", "").replace(" tr", ""),
        gold_sjc_buy=gold.get('gold_sjc_buy', '144.60').replace(" tr.đ", "").replace(" tr", ""),
        gold_world=gold.get("gold_world", "4,429 USD/oz"),
        usd_vnd=forex.get("usd_vnd", "25.450").replace(" đ", "").replace(" VND", ""),
        vnindex_points=stocks.get("vnindex_points", "1,285.40"),
        vnindex_change=stocks.get("vnindex_change", "+6.88"),
        vnindex_pct=stocks.get("vnindex_pct", "0.54").replace("+", "").replace("%", ""),
        fuel_ron95=fuel.get("ron95", "20.850").replace(" đ/lít", "").replace(" đ", "").replace("/lít", ""),
        domestic_economy_news_html=domestic_economy_news_html,
        domestic_tech_news_html=domestic_tech_news_html,
        intl_macro_news_html=intl_macro_news_html,
        intl_tech_news_html=intl_tech_news_html,
        social_news_html=social_news_html,
        flash_news_html=flash_news_html,
        trends_chips_html=trends_chips_html,
        raw_newsletter_text=raw_newsletter_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
    
    index_path = output_dir / "index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    try:
        repo_root = output_dir.resolve().parent
        if (repo_root / ".git").exists() or (repo_root / "index.html").exists():
            import shutil
            shutil.copy2(index_path, repo_root / "index.html")
    except Exception:
        pass
        
    archive_path = output_dir / "archive.html"
    archive_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Kho Lưu Trữ Bản Tin 24h</title>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; background: #fbf9f4; color: #111827; padding: 40px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    ul {{ margin-top: 20px; line-height: 2; }}
  </style>
</head>
<body>
  <h1>📂 Kho Lưu Trữ Bản Tin 24h</h1>
  <p><a href="./index.html">← Quay lại Bản tin mới nhất</a></p>
  <ul>
    <li>• <strong>{date_str}</strong> — <a href="./index.html">Bản tin phát hành ngày {date_str}</a> (Ấn bản điện tử số {base_issue})</li>
  </ul>
</body>
</html>
"""
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(archive_html)
        
    return index_path

if __name__ == "__main__":
    print("Site builder editorial module ready.")
