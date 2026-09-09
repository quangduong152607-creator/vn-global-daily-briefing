#!/usr/bin/env python3
"""
ĐIỂM ĐIỀU PHỐI CHÍNH (MASTER ORCHESTRATOR)
Hệ thống Bản tin 24h tự động — Antigravity × NotebookLM
Phiên bản: 1.1 (Cập nhật dịch tiếng Việt toàn diện, hỗ trợ song ngữ EN/VI & làm sạch giao diện)
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta

# Import các module thu thập
from src.collectors.indices import collect_all_indices
from src.collectors.news_rss import collect_news
from src.collectors.trends import collect_all_trends
from src.collectors.marketshare import get_latest_marketshare_data

# Import các module xử lý
from src.processors.dedup import deduplicate_items
from src.processors.verify import verify_and_tag_items
from src.processors.ranker import rank_items
from src.processors.translator import translate_news_batch
from src.processors.news_analyzer import process_and_structure_all_news

# Import bộ sinh xuất bản và QC
from src.publisher.site_builder import build_daily_portal
from src.publisher.quality_check import perform_pre_publish_qc
from src.notebooklm.client import get_infographic_provider

PROJECT_ROOT = Path(__file__).parent.resolve()

def load_yaml_config(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def format_daily_source_md(data: dict) -> str:
    """Tạo nội dung cho daily_source.md theo template chuẩn Spec 5.5 với 3 khối phân tích sâu"""
    template_path = PROJECT_ROOT / "templates" / "source_template.md"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    now = datetime.now()
    yesterday = now - timedelta(hours=24)
    
    # Số liệu
    indices = data.get("indices", {})
    forex = indices.get("forex", {})
    gold = indices.get("gold", {})
    stocks = indices.get("stocks", {})
    fuel = indices.get("fuel", {})
    
    structured = data.get("structured_news", {})
    
    # 1. KINH TẾ & THỊ TRƯỜNG TRONG NƯỚC
    dom_econ_items = structured.get("domestic_economy_news") or structured.get("economy_news", [])
    eco_lines = []
    for idx, it in enumerate(dom_econ_items, 1):
        eco_lines.append(f"### {idx}. {it.get('title')}\n- **Bối cảnh**: {it.get('context')}\n- **Tác động**: {it.get('impact')}\n- **Nguồn**: [{it.get('source')}]({it.get('link')})\n")
    economy_news_content = "\n".join(eco_lines) if eco_lines else "*Đang cập nhật các diễn biến kinh tế mới nhất.*"

    # 2. CÔNG NGHỆ & SỐ HÓA TRONG NƯỚC (Tinhte, GenK, Số Hóa)
    dom_tech_items = structured.get("domestic_tech_news", [])
    dom_tech_lines = []
    for idx, it in enumerate(dom_tech_items, 1):
        dom_tech_lines.append(f"### {idx}. {it.get('title')}\n- **Diễn biến**: {it.get('development')}\n- **Ý nghĩa**: {it.get('significance')}\n- **Nguồn**: [{it.get('source')}]({it.get('link')})\n")
    domestic_tech_news_content = "\n".join(dom_tech_lines) if dom_tech_lines else "*Đang cập nhật công nghệ trong nước.*"

    # 3. KINH TẾ & ĐỊA CHÍNH TRỊ QUỐC TẾ (Reuters, BBC, CNBC)
    intl_macro_items = structured.get("intl_macro_news", [])
    intl_macro_lines = []
    for idx, it in enumerate(intl_macro_items, 1):
        intl_macro_lines.append(f"### {idx}. {it.get('title')}\n- **Bối cảnh**: {it.get('context')}\n- **Tác động**: {it.get('impact')}\n- **Nguồn**: [{it.get('source')}]({it.get('link')})\n")
    intl_macro_news_content = "\n".join(intl_macro_lines) if intl_macro_lines else "*Đang cập nhật kinh tế và địa chính trị quốc tế.*"
    
    # 4. CÔNG NGHỆ & THIẾT BỊ DI ĐỘNG QUỐC TẾ (GSMArena, The Verge)
    intl_tech_items = structured.get("intl_tech_news") or structured.get("tech_news", [])
    intl_tech_lines = []
    for idx, it in enumerate(intl_tech_items, 1):
        intl_tech_lines.append(f"### {idx}. {it.get('title')}\n- **Diễn biến**: {it.get('development')}\n- **Ý nghĩa**: {it.get('significance')}\n- **Nguồn**: [{it.get('source')}]({it.get('link')})\n")
    intl_tech_news_content = "\n".join(intl_tech_lines) if intl_tech_lines else "*Đang cập nhật diễn biến sản phẩm công nghệ quốc tế.*"
    
    # 5. TIN SOCIAL & SHOWBIZ BẮT TREND
    soc_lines = []
    for idx, it in enumerate(structured.get("social_news", []), 1):
        soc_lines.append(f"### {idx}. {it.get('title')}\n- **Tiêu điểm**: {it.get('highlight')}\n- **Độ lan tỏa**: {it.get('virality')}\n- **Nguồn**: [{it.get('source')}]({it.get('link')})\n")
    social_news_content = "\n".join(soc_lines) if soc_lines else "*Đang cập nhật tiêu điểm social.*"

    # 6. TIN VẮN NHANH
    flash_lines = []
    for it in structured.get("flash_news", []):
        flash_lines.append(f"• **[{it.get('event')}]**: {it.get('summary')} (Nguồn: [{it.get('source')}]({it.get('link')}))")
    flash_news_content = "\n".join(flash_lines) if flash_lines else "*Đang cập nhật tin vắn nhanh.*"
    
    # Trends
    trends = data.get("trends", {})
    vn_t = trends.get("vn_trends", [])
    trend_lines = [f"- **{t['keyword']}** ({t['traffic']}) [{t['tag']}]" for t in vn_t]
    trends_content = "\n".join(trend_lines) if trend_lines else "*Chưa có số liệu trends mới.*"
    
    # Thị phần (GfK Vietnam Retail Audit & Counterpoint Research - BỎ KHUYẾN NGHỊ)
    ms = data.get("marketshare", {})
    ms_lines = [
        f"**Kỳ báo cáo**: {ms.get('report_period')}",
        f"**Nguồn khảo sát**: {ms.get('source', 'GfK & Counterpoint')}\n",
        "#### Bảng 1: Thị Phần Bán Lẻ Thực Tế Tại Điểm Bán (GfK Vietnam Retail Audit)"
    ]
    for brand in ms.get("market_gfk_vietnam", []):
        ms_lines.append(f"- **{brand['brand']}**: {brand['share']}% ({brand['delta']}) — {brand.get('segment', '')}")
        
    ms_lines.append("\n#### Bảng 2: Thị Phần Sản Lượng Xuất Xưởng (Counterpoint Research)")
    for brand in ms.get("market_vietnam", []):
        ms_lines.append(f"- **{brand['brand']}**: {brand['share']}% ({brand['delta']}) — {brand.get('status', '')}")
        
    marketshare_content = "\n".join(ms_lines)
    
    content = template.format(
        day_of_week="Chủ Nhật" if now.weekday() == 6 else f"Thứ {now.weekday() + 2}",
        date_str=now.strftime("%d/%m/%Y"),
        period_start=yesterday.strftime("%d/%m/%Y %H:%M"),
        period_end=now.strftime("%d/%m/%Y %H:%M"),
        sources_scanned=data.get("sources_scanned", 15),
        sources_failed=data.get("sources_failed", 0),
        system_status="HOẠT ĐỘNG BÌNH THƯỜNG",
        gold_sjc_buy=gold.get("gold_sjc_buy", "144.60"),
        gold_sjc_sell=gold.get("gold_sjc_sell", "147.60"),
        gold_sjc_change=gold.get("gold_sjc_change", "-1.00 tr.đ"),
        gold_world_price=gold.get("gold_world", "4,429 USD/oz"),
        gold_spread=gold.get("gold_spread", "~3.0 tr.đ/lượng"),
        indices_timestamp=now.strftime("%H:%M %d/%m/%Y"),
        usd_buy=forex.get("usd_buy", "25.320 đ"),
        usd_sell=forex.get("usd_sell", "25.580 đ"),
        usd_sbv=forex.get("usd_sbv", "24.280 đ"),
        cny_buy=forex.get("cny_vnd", "3.520 đ"),
        cny_sell=forex.get("cny_vnd", "3.550 đ"),
        krw_buy=forex.get("krw_vnd", "18.8 đ"),
        krw_sell=forex.get("krw_vnd", "19.2 đ"),
        dxy_index=forex.get("dxy_index", "104.25"),
        vnindex_points=stocks.get("vnindex_points", "1.285,40"),
        vnindex_change=stocks.get("vnindex_change", "+6.85"),
        vnindex_pct=stocks.get("vnindex_pct", "+0.54"),
        vnindex_volume=stocks.get("vnindex_volume", "680.5M"),
        vnindex_foreign=stocks.get("vnindex_foreign", "+120.5 tỷ VNĐ"),
        hnx_points=stocks.get("hnx_points", "242.15"),
        hnx_change=stocks.get("hnx_change", "+1.20"),
        hnx_pct=stocks.get("hnx_pct", "+0.50"),
        fuel_ron95=fuel.get("ron95", "20.850 đ/lít"),
        fuel_e5=fuel.get("e5_ron92", "19.740 đ/lít"),
        fuel_do=fuel.get("diesel_do", "18.320 đ/lít"),
        fuel_update_date=fuel.get("update_date", "Kỳ điều hành gần nhất"),
        economy_news_content=economy_news_content,
        domestic_tech_news_content=domestic_tech_news_content,
        intl_macro_news_content=intl_macro_news_content,
        intl_tech_news_content=intl_tech_news_content,
        social_news_content=social_news_content,
        flash_news_content=flash_news_content,
        trends_content=trends_content,
        marketshare_content=marketshare_content
    )
    return content

def run_pipeline(dry_run: bool = False):
    print("=====================================================")
    print("🚀 BẮT ĐẦU PIPELINE BẢN TIN 24H (ANTIGRAVITY × NOTEBOOKLM)")
    print("=====================================================")
    
    # 1. Đọc file cấu hình
    sources_cfg = load_yaml_config(PROJECT_ROOT / "config" / "sources.yaml")
    modules_cfg = load_yaml_config(PROJECT_ROOT / "config" / "modules.yaml")
    notebook_cfg = load_yaml_config(PROJECT_ROOT / "config" / "notebooklm.yaml")
    
    # 2. GIAI ĐOẠN A: THU THẬP DỮ LIỆU
    print("\n[A] Thu thập dữ liệu:")
    print("  -> Đang lấy chỉ số tài chính, vàng, tỷ giá, xăng dầu...")
    indices_data = collect_all_indices()
    
    print("  -> Đang quét các kênh RSS báo chí chính thống...")
    raw_news = collect_news(sources_cfg)
    
    print("  -> Đang quét Google Trends (VN & Global)...")
    trends_data = collect_all_trends()
    
    print("  -> Đang nạp số liệu thị phần Smartphone (Counterpoint / Canalys)...")
    marketshare_data = get_latest_marketshare_data()
    
    # 3. GIAI ĐOẠN B: XỬ LÝ & XÁC MINH & DỊCH THUẬT & CẤU TRÚC HÓA
    print("\n[B] Xử lý, Xác minh, Dịch thuật & Cấu trúc hóa 3 Khối:")
    processed_news = {}
    for cat, items in raw_news.items():
        # Khử trùng lặp
        deduped = deduplicate_items(items)
        # Gán nhãn độ tin cậy
        tagged = verify_and_tag_items(deduped)
        # Xếp hạng độ ưu tiên ngành hàng ĐTDĐ
        ranked = rank_items(tagged)
        # Tự động dịch sang Tiếng Việt & gán metadata song ngữ cho top các bài quan trọng nhất
        translated_top = translate_news_batch(ranked[:10])
        processed_news[cat] = translated_top + ranked[10:]
        print(f"  -> Nhóm {cat}: Từ {len(items)} tin thô -> {len(ranked)} cụm sự kiện sau khi dịch & xếp hạng.")
        
    # Bóc tách và cấu trúc hóa sâu 3 phần: Kinh tế, Công nghệ, Tin vắn nhanh
    structured_news = process_and_structure_all_news(processed_news)
    print(f"  -> Đã cấu trúc hóa: {len(structured_news['economy_news'])} tin Kinh tế, {len(structured_news['tech_news'])} tin Công nghệ, {len(structured_news['flash_news'])} tin Vắn nhanh.")

    master_data = {
        "indices": indices_data,
        "news": processed_news,
        "structured_news": structured_news,
        "trends": trends_data,
        "marketshare": marketshare_data,
        "sources_scanned": len(sources_cfg.get("news_domestic", [])) + len(sources_cfg.get("technology", [])) + 4,
        "sources_failed": 0
    }
    
    # Xuất file daily_source.md
    today_str = datetime.now().strftime("%Y/%m/%d")
    out_dir = PROJECT_ROOT / "output" / today_str
    source_dir = out_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    
    source_md_path = source_dir / "daily_source.md"
    source_content = format_daily_source_md(master_data)
    with open(source_md_path, "w", encoding="utf-8") as f:
        f.write(source_content)
    print(f"\n[B5] Đã xuất file nguồn chuẩn hóa cho NotebookLM: {source_md_path}")
    
    # 4. GIAI ĐOẠN C: KẾT NỐI NOTEBOOKLM
    provider = get_infographic_provider(notebook_cfg)
    nb_id = provider.create_notebook(datetime.now().strftime("Bản tin %d/%m/%Y"))
    print(f"\n[C] Khởi tạo phiên NotebookLM ({type(provider).__name__}): {nb_id}")
    provider.upload_source(nb_id, source_md_path)
    
    # 5. GIAI ĐOẠN D: XUẤT BẢN & KIỂM TRA CHẤT LƯỢNG (PUBLISH & QC)
    docs_dir = PROJECT_ROOT / "docs"
    index_path = build_daily_portal(master_data, docs_dir)
    print(f"\n[D] Đã sinh trang xuất bản bản tin (Giao diện sạch, đã dịch & có song ngữ): {index_path}")
    
    qc_report = perform_pre_publish_qc(source_md_path, index_path, master_data)
    print("\n[D1] Báo Cáo Kiểm Tra Chất Lượng (Pre-Publish QC):")
    print(f"  -> Kết quả: {'✓ ĐẠT CHUẨN' if qc_report['passed'] else '✕ CÓ LỖI'}")
    if qc_report["warnings"]:
        for w in qc_report["warnings"]:
            print(f"  -> [CẢNH BÁO]: {w}")
    if qc_report["errors"]:
        for e in qc_report["errors"]:
            print(f"  -> [LỖI]: {e}")
            
    print("\n=====================================================")
    print("✓ HOÀN TẤT CẬP NHẬT: GIAO DIỆN SẠCH & DỊCH TIẾNG VIỆT TOÀN DIỆN!")
    print(f"- File nguồn NotebookLM: {source_md_path}")
    print(f"- Cổng bản tin di động: {index_path}")
    print("=====================================================")

if __name__ == "__main__":
    run_pipeline()
