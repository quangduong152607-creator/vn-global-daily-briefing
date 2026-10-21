"""
Tìm tin qua Google News RSS: tin từng hãng điện thoại tại Việt Nam và tin chuỗi cung ứng / linh kiện.
Trả về cùng khuôn với news_rss.fetch_single_feed để đi chung luồng xử lý (khử trùng, gắn nhãn, xếp hạng).
"""

import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

# (tên hiển thị, truy vấn). "when:Nd" giới hạn N ngày gần nhất.
BRAND_QUERIES_VN = [
    ("Samsung", '"Samsung" (Galaxy OR điện thoại) Việt Nam when:3d'),
    ("Apple", '(iPhone OR Apple) Việt Nam when:3d'),
    ("OPPO", '"OPPO" điện thoại when:3d'),
    ("Xiaomi", '(Xiaomi OR Redmi) điện thoại when:3d'),
    ("vivo", '"vivo" điện thoại when:3d'),
    ("realme", '"realme" when:3d'),
    ("Honor", '"Honor" điện thoại when:3d'),
]

SUPPLY_CHAIN_QUERIES = [
    ("Bộ nhớ DRAM/NAND", '(DRAM OR NAND) (price OR prices) (TrendForce OR smartphone) when:7d'),
    ("Thị trường smartphone", '(Counterpoint OR Canalys OR IDC OR Omdia) smartphone shipments when:7d'),
    ("Chip di động", '(Qualcomm OR MediaTek OR TSMC) smartphone chip when:7d'),
]


def fetch_google_news(query: str, lang: str = "vi", max_items: int = 3) -> List[Dict[str, Any]]:
    if lang == "vi":
        params = {"q": query, "hl": "vi", "gl": "VN", "ceid": "VN:vi"}
    else:
        params = {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=10, context=ssl._create_unverified_context()) as r:
        root = ET.fromstring(r.read())

    items = []
    for it in root.findall(".//item")[:max_items]:
        title = (it.findtext("title") or "").strip()
        source = (it.findtext("source") or "").strip()
        # Google News gắn " - Tên báo" vào cuối tiêu đề
        if source and title.endswith(f" - {source}"):
            title = title[: -len(source) - 3]
        if not title:
            continue
        items.append({
            "title": title,
            "link": (it.findtext("link") or "").strip(),
            "summary": "",
            "pub_date": (it.findtext("pubDate") or "").strip(),
            "source_name": source or "Google News",
            "weight": 22,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    return items


def collect_query_group(queries, lang: str, max_items: int) -> List[Dict[str, Any]]:
    out = []
    for label, q in queries:
        try:
            for it in fetch_google_news(q, lang, max_items):
                it["topic"] = label
                out.append(it)
        except Exception as e:
            print(f"     ✕ Google News '{label}': {e}")
    return out


def collect_brand_and_supply_news() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "brand_vn": collect_query_group(BRAND_QUERIES_VN, "vi", 2),
        "supply_chain": collect_query_group(SUPPLY_CHAIN_QUERIES, "en", 3),
    }
