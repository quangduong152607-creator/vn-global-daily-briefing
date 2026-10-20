#!/usr/bin/env python3
"""
ĐIỂM ĐIỀU PHỐI CHÍNH — Bản tin 24h tự động.
Thu thập -> xử lý -> xuất daily_source.md (nguồn cho AI/NotebookLM) -> dựng trang docs/ -> QC.
"""

import yaml
from pathlib import Path
from datetime import datetime

from src.collectors.indices import collect_all_indices
from src.collectors.news_rss import collect_news
from src.collectors.trends import collect_all_trends
from src.collectors.marketshare import get_latest_marketshare_data
from src.collectors.competitors import collect_competitor_campaigns

from src.processors.dedup import deduplicate_items
from src.processors.verify import verify_and_tag_items
from src.processors.ranker import rank_items
from src.processors.translator import translate_news_batch
from src.processors.news_analyzer import process_and_structure_all_news, SECTION_LIMITS
from src.processors.history import apply_history, change_of

from src.publisher.site_builder import build_daily_portal, fmt_num, NEWS_SECTIONS
from src.publisher.quality_check import perform_pre_publish_qc

PROJECT_ROOT = Path(__file__).parent.resolve()


def load_yaml_config(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def format_daily_source_md(data: dict, now: datetime) -> str:
    """File nguồn dạng Markdown: chỉ chứa số liệu và tin đã thu thập, kèm nguồn."""
    lines = [
        f"# BẢN TIN 24H — {now.strftime('%d/%m/%Y %H:%M')}",
        "",
        "> Nguồn sự thật gốc. Chỉ dùng số liệu và sự kiện trong tài liệu này; mục ghi CHƯA LẤY ĐƯỢC nghĩa là không có số.",
        "",
        "## Chỉ số thị trường",
    ]
    for m in data["indices"]:
        if not m["ok"]:
            lines.append(f"- **{m['label']}**: CHƯA LẤY ĐƯỢC ({m['source']})")
            continue
        diff, pct = change_of(m)
        chg = f" | thay đổi {diff:+,.{m['decimals']}f} ({pct:+.2f}%)" if diff is not None else ""
        sub = f" | {m['sub']}" if m["sub"] else ""
        lines.append(f"- **{m['label']}**: {fmt_num(m['value'], m['decimals'])} {m['unit']}{chg}{sub} — {m['source']} {m['as_of']}".rstrip())

    news = data["structured_news"]
    for key, title in [("watchlist", "Đáng chú ý cho ngành ĐTDĐ")] + NEWS_SECTIONS:
        lines += ["", f"## {title}"]
        items = news.get(key, [])
        if not items:
            lines.append("- (không có tin)")
        for it in items:
            tags = f" [{', '.join(it['tags'])}]" if it["tags"] else ""
            label = (it.get("reliability") or {}).get("label", "")
            lines.append(f"- **{it['title']}**{tags} — {it['summary']} ({it['source']} {it['time']}; {label}) {it['link']}")

    camps = data["competitors"].get("all_campaigns", [])
    lines += ["", "## Khuyến mãi đối thủ (30 ngày)"]
    lines += [f"- [{c['brand']}] {c['title']} ({c.get('pub_date', '')}) {c['url']}" for c in camps] or ["- (không có)"]

    trends = data["trends"].get("vn_trends", [])
    lines += ["", "## Google Trends Việt Nam"]
    lines += [f"- {t['keyword']} ({t['traffic']})" for t in trends] or ["- (chưa lấy được)"]
    return "\n".join(lines) + "\n"


def run_pipeline():
    now = datetime.now()
    print("🚀 BẮT ĐẦU PIPELINE BẢN TIN 24H")
    sources_cfg = load_yaml_config(PROJECT_ROOT / "config" / "sources.yaml")

    print("\n[A] Thu thập dữ liệu")
    indices = collect_all_indices()
    apply_history(indices, today=now.date().isoformat())
    for m in indices:
        print(f"  {'✓' if m['ok'] else '✕'} {m['label']}: {m['value']} {m['unit']} — {m['source']} {m['error'][:100]}")

    competitors = collect_competitor_campaigns()
    print(f"  -> Khuyến mãi đối thủ: {competitors['total_campaigns']} bài ({competitors['new_campaigns_count']} mới)")
    raw_news = collect_news(sources_cfg)
    trends = collect_all_trends()
    print(f"  -> Google Trends VN: {len(trends['vn_trends'])} từ khóa")

    print("\n[B] Xử lý tin")
    processed_news = {}
    for cat in SECTION_LIMITS:
        items = raw_news.get(cat, [])
        ranked = rank_items(verify_and_tag_items(deduplicate_items(items)))
        processed_news[cat] = translate_news_batch(ranked[:10]) + ranked[10:]
        print(f"  -> {cat}: {len(items)} tin thô -> {len(ranked)} tin sau khử trùng")
    structured_news = process_and_structure_all_news(processed_news)
    print(f"  -> Đáng chú ý ngành ĐTDĐ: {len(structured_news['watchlist'])} tin")

    master_data = {
        "indices": indices,
        "competitors": competitors,
        "structured_news": structured_news,
        "trends": trends,
        "marketshare": get_latest_marketshare_data(),
    }

    source_dir = PROJECT_ROOT / "output" / now.strftime("%Y/%m/%d") / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_md_path = source_dir / "daily_source.md"
    source_md_path.write_text(format_daily_source_md(master_data, now), encoding="utf-8")
    print(f"\n[C] File nguồn: {source_md_path}")

    index_path = build_daily_portal(master_data, PROJECT_ROOT / "docs", now)
    print(f"[D] Trang bản tin: {index_path}")

    qc = perform_pre_publish_qc(source_md_path, index_path, master_data)
    print(f"\n[QC] {'✓ ĐẠT' if qc['passed'] else '✕ CÓ LỖI'}")
    for w in qc["warnings"]:
        print(f"  [CẢNH BÁO] {w}")
    for e in qc["errors"]:
        print(f"  [LỖI] {e}")


if __name__ == "__main__":
    run_pipeline()
