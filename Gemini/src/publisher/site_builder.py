"""
Sinh trang bản tin di động (docs/index.html), bản lưu theo ngày (docs/archive/YYYY-MM-DD.html)
và trang kho lưu trữ (docs/archive.html).

Trang chỉ hiển thị dữ liệu thật đã thu thập. Thiếu dữ liệu thì ghi rõ "chưa lấy được".
"""

import html
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from src.processors.history import change_of
from src.processors.news_analyzer import format_pub_time

WEEKDAYS = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

RELIABILITY_SHORT = {
    "VERIFIED": ("Nhiều nguồn", "ok"),
    "SINGLE_SOURCE": ("1 nguồn", ""),
    "RUMOR": ("Tin đồn", "warn"),
    "OPINION": ("Nhận định", ""),
}

NEWS_SECTIONS = [
    ("domestic_economy", "Thời sự & kinh tế trong nước"),
    ("domestic_tech", "Công nghệ trong nước"),
    ("international_macro", "Kinh tế & địa chính trị quốc tế"),
    ("international_tech", "Công nghệ & di động quốc tế"),
]

esc = html.escape


def fmt_num(v: float, decimals: int) -> str:
    """Định dạng kiểu Việt Nam: 26.370 ; 1.689,84"""
    s = f"{v:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def sparkline(series: List[float], w: int = 96, h: int = 26) -> str:
    if len(series) < 2:
        return ""
    lo, hi = min(series), max(series)
    span = (hi - lo) or 1
    step = w / (len(series) - 1)
    pts = " ".join(f"{i * step:.1f},{h - 2 - (v - lo) / span * (h - 4):.1f}" for i, v in enumerate(series))
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<polyline points="{pts}" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linejoin="round" stroke-linecap="round"/></svg>')


def render_metric(m: Dict[str, Any]) -> str:
    if not m["ok"]:
        return f"""<div class="kpi kpi-missing">
  <div class="kpi-label">{esc(m['label'])}</div>
  <div class="kpi-value">—</div>
  <div class="kpi-sub">Chưa lấy được số liệu</div>
  <div class="kpi-foot">{esc(m['source'])}</div>
</div>"""

    diff, pct = change_of(m)
    if diff is None:
        delta = '<span class="delta flat">chưa có kỳ trước</span>'
    else:
        cls = "up" if diff > 0 else "down" if diff < 0 else "flat"
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "■"
        sign = "+" if pct > 0 else "−" if pct < 0 else ""
        delta = f'<span class="delta {cls}">{arrow} {fmt_num(abs(diff), m["decimals"])} ({sign}{fmt_num(abs(pct), 2)}%)</span>'
    foot = esc(m["source"]) + (f" · {esc(m['as_of'])}" if m["as_of"] else "")
    return f"""<div class="kpi">
  <div class="kpi-head"><span class="kpi-label">{esc(m['label'])}</span>{sparkline(m['series'])}</div>
  <div class="kpi-value">{fmt_num(m['value'], m['decimals'])} <span class="kpi-unit">{esc(m['unit'])}</span></div>
  <div class="kpi-delta">{delta}</div>
  {f'<div class="kpi-sub">{esc(m["sub"])}</div>' if m["sub"] else ''}
  <div class="kpi-foot"><a href="{esc(m['source_url'])}" target="_blank" rel="noopener">{foot}</a></div>
</div>"""


def render_news_item(it: Dict[str, Any], show_tags: bool = False) -> str:
    rel_code = (it.get("reliability") or {}).get("code", "")
    rel_text, rel_cls = RELIABILITY_SHORT.get(rel_code, ("", ""))
    meta = [esc(it["source"])]
    if it.get("time"):
        meta.append(esc(it["time"]))
    if rel_text:
        meta.append(f'<span class="rel {rel_cls}">{rel_text}</span>')
    tags = ""
    if show_tags and it.get("tags"):
        tags = '<div class="tags">' + "".join(f'<span class="tag">{esc(t)}</span>' for t in it["tags"]) + "</div>"
    summary = it.get("summary", "")
    if len(summary) > 260:
        summary = summary[:257].rsplit(" ", 1)[0] + "…"
    return f"""<li class="news">
  <a class="news-title" href="{esc(it['link'])}" target="_blank" rel="noopener">{esc(it['title'])}</a>
  {f'<p class="news-sum">{esc(summary)}</p>' if summary else ''}
  {tags}
  <div class="news-meta">{' · '.join(meta)}</div>
</li>"""


def render_news_list(items: List[Dict[str, Any]], visible: int = 4, show_tags: bool = False) -> str:
    if not items:
        return '<p class="empty">Chưa lấy được tin cho mục này.</p>'
    head = "".join(render_news_item(it, show_tags) for it in items[:visible])
    rest = items[visible:]
    more = ""
    if rest:
        more = (f'<details class="more"><summary>Xem thêm {len(rest)} tin</summary><ul class="news-list">'
                + "".join(render_news_item(it, show_tags) for it in rest) + "</ul></details>")
    return f'<ul class="news-list">{head}</ul>{more}'


def render_campaigns(comp: Dict[str, Any]) -> str:
    items = comp.get("all_campaigns", [])
    if not items:
        return '<p class="empty">Không tìm thấy bài khuyến mãi mới của CellphoneS / FPT Shop trong 30 ngày (hoặc nguồn lỗi).</p>'
    rows = []
    for c in items[:8]:
        badges = f'<span class="tag">{esc(c["brand"])}</span>'
        if c.get("is_new"):
            badges += '<span class="tag new">Mới</span>'
        if c.get("discount_highlight"):
            badges += f'<span class="tag deal">{esc(c["discount_highlight"])}</span>'
        rows.append(f"""<li class="news">
  <div class="tags">{badges}</div>
  <a class="news-title" href="{esc(c['url'])}" target="_blank" rel="noopener">{esc(c['title'])}</a>
  <div class="news-meta">Đăng {esc(format_pub_time(c.get('pub_date', '')))}</div>
</li>""")
    return f'<ul class="news-list">{"".join(rows)}</ul>'


def render_trends(trends: Dict[str, Any]) -> str:
    vn = trends.get("vn_trends", [])
    if not vn:
        return '<p class="empty">Chưa lấy được Google Trends hôm nay.</p>'
    chips = "".join(
        f'<span class="chip{" ict" if t.get("is_ict") else ""}">{esc(t["keyword"])} <small>{esc(t.get("traffic", ""))}</small></span>'
        for t in vn[:10])
    return f'<div class="chips">{chips}</div><p class="note">Viền đậm: từ khóa liên quan ICT / điện thoại.</p>'


def render_marketshare(ms: Dict[str, Any]) -> str:
    gfk = {b["brand"]: b for b in ms.get("market_gfk_vietnam", [])}
    cp = {b["brand"]: b for b in ms.get("market_vietnam", [])}
    if not gfk:
        return '<p class="empty">Chưa có số liệu thị phần.</p>'
    rows = "".join(
        f"<tr><td>{esc(b)}</td><td class='num'>{gfk[b]['share']:.1f}%</td>"
        f"<td class='num'>{cp[b]['share']:.1f}%</td></tr>" if b in cp else
        f"<tr><td>{esc(b)}</td><td class='num'>{gfk[b]['share']:.1f}%</td><td class='num'>—</td></tr>"
        for b in gfk if b != "Khác")
    return f"""<table class="share">
<thead><tr><th>Hãng</th><th class="num">Bán lẻ (GfK)</th><th class="num">Xuất xưởng (Counterpoint)</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="note">{esc(ms.get('report_period', ''))}. ⚠ {esc(ms.get('manual_note', ''))}.</p>"""


def render_status(data: Dict[str, Any]) -> str:
    rows = []
    for m in data["indices"]:
        state = "ok" if m["ok"] else "fail"
        detail = esc(m["source"]) if m["ok"] else esc(m["error"][:140] or "lỗi")
        rows.append(f'<li class="{state}"><b>{esc(m["label"])}</b> — {detail}</li>')
    news = data["structured_news"]
    for key, title in NEWS_SECTIONS:
        items = news.get(key, [])
        cached = " (bộ nhớ đệm — nguồn lỗi)" if any(it.get("from_cache") for it in items) else ""
        rows.append(f'<li class="{"ok" if items and not cached else "fail"}"><b>{title}</b> — {len(items)} tin{cached}</li>')
    rows.append(f'<li class="{"ok" if data["trends"].get("vn_trends") else "fail"}"><b>Google Trends</b> — {len(data["trends"].get("vn_trends", []))} từ khóa</li>')
    rows.append(f'<li class="ok"><b>Khuyến mãi đối thủ</b> — {data["competitors"].get("total_campaigns", 0)} bài trong 30 ngày</li>')
    return "<ul class='status'>" + "".join(rows) + "</ul>"


def build_plain_text(data: Dict[str, Any], date_str: str) -> str:
    """Bản text gọn để dán Zalo/Telegram."""
    lines = [f"BẢN TIN 24H — {date_str}", "", "CHỈ SỐ"]
    for m in data["indices"]:
        if not m["ok"]:
            continue
        diff, pct = change_of(m)
        chg = f" ({'+' if pct >= 0 else '−'}{fmt_num(abs(pct), 2)}%)" if pct is not None else ""
        lines.append(f"- {m['label']}: {fmt_num(m['value'], m['decimals'])} {m['unit']}{chg}")
    watch = data["structured_news"].get("watchlist", [])
    if watch:
        lines += ["", "ĐÁNG CHÚ Ý NGÀNH ĐTDĐ"]
        lines += [f"- {it['title']} ({it['source']}) {it['link']}" for it in watch]
    return "\n".join(lines)


CSS = """
:root{--bg:#f5f4f0;--surface:#fff;--ink:#1b1b1b;--muted:#6a6a6a;--line:#e5e2da;--accent:#b4410f;
--up:#13803b;--down:#c0262d;--chip:#f0ede6;--warn:#a15c00}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#111;--surface:#1b1b1b;--ink:#ececec;
--muted:#9b9b9b;--line:#2d2d2d;--accent:#f08a4b;--up:#4ade80;--down:#f87171;--chip:#262626;--warn:#fbbf24}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:inherit}
.wrap{max-width:780px;margin:0 auto;padding:16px 16px 48px}
header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:8px 0 16px;border-bottom:2px solid var(--ink)}
h1{font-size:24px;line-height:1.15;margin:0;letter-spacing:-.01em}
.kicker{font-size:13px;font-weight:600;color:var(--accent);margin-top:2px}
.date{color:var(--muted);font-size:13px;margin-top:4px}
.top-actions{display:flex;gap:8px;flex-shrink:0}
.btn{border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:8px;padding:6px 10px;font-size:13px;cursor:pointer;text-decoration:none;white-space:nowrap}
.health{display:inline-block;margin-top:8px;font-size:12px;padding:2px 8px;border-radius:99px;background:var(--chip);color:var(--muted)}
section{margin-top:28px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 10px;font-weight:700}
.kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
@media (min-width:640px){.kpis{grid-template-columns:repeat(4,minmax(0,1fr))}}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 12px;min-width:0;overflow:hidden}
.kpi-head{display:flex;justify-content:space-between;align-items:center;gap:6px;min-height:20px}
.kpi-label{font-size:12px;color:var(--muted);font-weight:600}
.kpi-value{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi-unit{font-size:11px;font-weight:500;color:var(--muted)}
.kpi-delta{margin-top:2px}
.delta{font-size:12px;font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.delta.up{color:var(--up)}.delta.down{color:var(--down)}.delta.flat{color:var(--muted);font-weight:500}
.spark{width:52px;height:18px;color:var(--muted);flex-shrink:0}
.kpi-sub{font-size:11px;color:var(--muted);margin-top:2px}
.kpi-foot{font-size:10.5px;color:var(--muted);margin-top:6px;border-top:1px dashed var(--line);padding-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.kpi-foot a{text-decoration:none}
.kpi-missing .kpi-value{color:var(--muted)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:4px 14px}
.watch{border-left:3px solid var(--accent)}
.news-list{list-style:none;margin:0;padding:0}
.news{padding:12px 0;border-bottom:1px solid var(--line)}
.news-list>.news:last-child{border-bottom:0}
.news-title{font-weight:650;font-size:15.5px;line-height:1.35;text-decoration:none;display:block}
.news-title:hover{text-decoration:underline}
.news-sum{margin:4px 0 0;color:var(--muted);font-size:14px}
.news-meta{font-size:12px;color:var(--muted);margin-top:6px}
.rel{font-weight:600}.rel.ok{color:var(--up)}.rel.warn{color:var(--warn)}
.tags{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0 0}
.tag{font-size:11px;font-weight:600;padding:1px 7px;border-radius:99px;background:var(--chip);color:var(--ink)}
.tag.new{background:var(--accent);color:#fff}.tag.deal{color:var(--accent)}
details.more{border-top:1px solid var(--line)}
details.more>summary{cursor:pointer;padding:10px 0;font-size:13px;font-weight:600;color:var(--accent);list-style:none}
details.more>summary::-webkit-details-marker{display:none}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{background:var(--surface);border:1px solid var(--line);border-radius:99px;padding:4px 10px;font-size:13px}
.chip small{color:var(--muted)}
.chip.ict{border:2px solid var(--accent)}
table.share{width:100%;border-collapse:collapse;font-size:14px;background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.share th,.share td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left}
.share th{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.num{text-align:right!important;font-variant-numeric:tabular-nums}
.note,.empty{font-size:12.5px;color:var(--muted);margin:8px 0 0}
.empty{padding:12px 0}
.status{list-style:none;padding:0;margin:8px 0 0;font-size:12.5px;color:var(--muted)}
.status li{padding:3px 0}.status li::before{content:"● ";}
.status li.ok::before{color:var(--up)}.status li.fail::before{color:var(--down)}
footer{margin-top:32px;font-size:12px;color:var(--muted)}
footer details>summary{cursor:pointer;font-weight:600}
#toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:var(--ink);color:var(--bg);padding:8px 14px;border-radius:8px;font-size:13px;opacity:0;pointer-events:none;transition:opacity .2s}
#toast.show{opacity:1}
"""

JS = """
function copyBrief(){
  const t=document.getElementById('plain').value;
  const done=()=>{const el=document.getElementById('toast');el.classList.add('show');setTimeout(()=>el.classList.remove('show'),1800)};
  if(navigator.clipboard){navigator.clipboard.writeText(t).then(done)}else{
    const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();done()}
}
"""


def render_page(data: Dict[str, Any], now: datetime, base: str = "") -> str:
    date_str = f"{WEEKDAYS[now.weekday()]}, {now.strftime('%d/%m/%Y')}"
    metrics = data["indices"]
    ok_count = sum(1 for m in metrics if m["ok"])
    news = data["structured_news"]
    watch = news.get("watchlist", [])
    watch_links = {it["link"] for it in watch}

    news_html = ""
    for key, title in NEWS_SECTIONS:
        items = [it for it in news.get(key, []) if it["link"] not in watch_links]
        news_html += f'<section><h2>{title}</h2><div class="card">{render_news_list(items)}</div></section>'

    watch_html = render_news_list(watch, visible=5, show_tags=True) if watch else \
        '<p class="empty">Hôm nay chưa có tin nào khớp nhóm từ khóa ngành ĐTDĐ (hãng, bán lẻ, chip, thuế, tỷ giá, logistics).</p>'

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bản tin 24h — {now.strftime('%d/%m/%Y')}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top">
  <div>
    <h1>Bản tin 24h</h1>
    <div class="kicker">Thị trường · ngành điện thoại</div>
    <div class="date">{date_str} · cập nhật {now.strftime('%H:%M')}</div>
    <span class="health">{ok_count}/{len(metrics)} chỉ số lấy được</span>
  </div>
  <div class="top-actions">
    <button class="btn" onclick="copyBrief()">Sao chép</button>
    <a class="btn" href="{base}archive.html">Lưu trữ</a>
  </div>
</header>

<section><h2>Chỉ số thị trường</h2>
<div class="kpis">{''.join(render_metric(m) for m in metrics)}</div>
<p class="note">Thay đổi so với phiên/ngày trước. Tỷ giá Vietcombank là giá bán ra.</p>
</section>

<section><h2>Đáng chú ý cho ngành ĐTDĐ</h2><div class="card watch">{watch_html}</div></section>

{news_html}

<section><h2>Khuyến mãi đối thủ · 30 ngày</h2><div class="card">{render_campaigns(data.get('competitors', {}))}</div></section>

<section><h2>Google Trends Việt Nam</h2>{render_trends(data.get('trends', {}))}</section>

<section><h2>Thị phần smartphone Việt Nam</h2>{render_marketshare(data.get('marketshare', {}))}</section>

<footer>
  <details><summary>Trạng thái nguồn dữ liệu</summary>{render_status(data)}</details>
  <p>Tự động tổng hợp từ RSS báo chí và nguồn số liệu công khai. Nhãn "Nhiều nguồn / 1 nguồn" theo số báo cùng đưa tin.</p>
</footer>
</div>
<div id="toast">Đã sao chép bản tin</div>
<textarea id="plain" hidden readonly>{esc(build_plain_text(data, date_str))}</textarea>
<script>{JS}</script>
</body>
</html>"""


def render_archive(dates: List[str]) -> str:
    items = "".join(
        f'<li class="news"><a class="news-title" href="archive/{d}.html">{datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")}</a></li>'
        for d in dates)
    return f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lưu trữ bản tin 24h</title><style>{CSS}</style></head>
<body><div class="wrap">
<header class="top"><div><h1>Lưu trữ bản tin</h1><div class="date">{len(dates)} số</div></div>
<div class="top-actions"><a class="btn" href="index.html">Bản mới nhất</a></div></header>
<section><div class="card"><ul class="news-list">{items or '<li class="empty">Chưa có bản lưu.</li>'}</ul></div></section>
</div></body></html>"""


def build_daily_portal(daily_data: Dict[str, Any], output_dir: Path, now: datetime = None) -> Path:
    """Ghi index.html, archive/YYYY-MM-DD.html và archive.html vào output_dir."""
    now = now or datetime.now()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    index_path = output_dir / "index.html"
    index_path.write_text(render_page(daily_data, now), encoding="utf-8")
    (archive_dir / f"{now.strftime('%Y-%m-%d')}.html").write_text(render_page(daily_data, now, base="../"), encoding="utf-8")

    dates = sorted((p.stem for p in archive_dir.glob("*.html")), reverse=True)
    (output_dir / "archive.html").write_text(render_archive(dates), encoding="utf-8")
    return index_path
