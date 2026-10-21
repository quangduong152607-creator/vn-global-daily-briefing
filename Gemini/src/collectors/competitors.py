"""
Bộ thu thập & theo dõi chiến dịch quảng cáo, tin khuyến mãi của đối thủ:
- CellphoneS (Sforum & Tin khuyến mãi)
- FPT Shop (Tin tức khuyến mãi & Deal công nghệ)
Theo dõi cửa sổ 30 ngày (1 tháng), tự động phát hiện bài khuyến mãi mới.
"""

import os
import ssl
import json
import re
import urllib.parse
import urllib.request
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CACHE_FILE = PROJECT_ROOT / "data" / "raw" / "competitor_campaigns.json"
WINDOW_DAYS = 30

# (tên hiển thị, cách gọi trong truy vấn Google News)
RETAILERS = [
    ("Thế Giới Di Động", '("Thế Giới Di Động" OR TGDĐ OR TopZone)'),
    ("FPT Shop", '"FPT Shop"'),
    ("CellphoneS", 'CellphoneS'),
    ("Di Động Việt", '"Di Động Việt"'),
    ("Hoàng Hà Mobile", '"Hoàng Hà Mobile"'),
    ("Viettel Store", '"Viettel Store"'),
]

PROMO_KEYWORDS = [
    "khuyến mãi", "ưu đãi", "giảm giá", "sale", "hot sale", "thu cũ",
    "đổi mới", "trả góp", "quà tặng", "voucher", "back to school",
    "tựu trường", "ngày đôi", "deal", "mở bán", "đặt trước", "pre-order", "smember"
]

def get_ssl_context():
    return ssl._create_unverified_context()

def load_cached_campaigns() -> Dict[str, Any]:
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_updated": "", "campaigns": {}}

def save_cached_campaigns(cache_data: Dict[str, Any]):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def fetch_rss_campaigns(brand: str, feed_url: str) -> List[Dict[str, Any]]:
    campaigns = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    
    try:
        req = urllib.request.Request(feed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=get_ssl_context()) as r:
            xml_data = r.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall(".//item"):
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                desc_el = item.find("description")
                
                title = title_el.text.strip() if (title_el is not None and title_el.text) else ""
                link = link_el.text.strip() if (link_el is not None and link_el.text) else ""
                pub_date = pub_el.text.strip() if (pub_el is not None and pub_el.text) else ""
                desc = desc_el.text.strip() if (desc_el is not None and desc_el.text) else ""
                desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
                
                if not title or not link:
                    continue
                    
                # Kiểm tra xem có chứa từ khóa khuyến mãi không
                text_lower = f"{title} {desc_clean}".lower()
                is_promo = any(kw in text_lower for kw in PROMO_KEYWORDS)
                
                if is_promo:
                    # Trích xuất điểm nhấn giảm giá nếu có
                    discount_match = re.search(r'(giảm\s+(?:đến|tới|sâu)?\s*[0-9]+%|giảm\s+[0-9]+(?:\.[0-9]+)?\s*(?:triệu|tr|đ)|voucher\s+[0-9]+(?:\.[0-9]+)?\s*(?:triệu|tr|đ))', text_lower)
                    discount_highlight = discount_match.group(1).capitalize() if discount_match else ""
                    
                    campaigns.append({
                        "brand": brand,
                        "title": title,
                        "summary": desc_clean[:220] + "..." if len(desc_clean) > 220 else desc_clean,
                        "url": link,
                        "pub_date": pub_date,
                        "discount_highlight": discount_highlight
                    })
    except Exception:
        pass
        
    return campaigns

def is_recent(pub_date: str, days: int = WINDOW_DAYS) -> bool:
    """Bài đăng trong cửa sổ theo dõi. Không đọc được ngày -> loại (tránh hiện tin cũ như tin mới)."""
    try:
        dt = parsedate_to_datetime(pub_date)
    except (TypeError, ValueError):
        return False
    return datetime.now(dt.tzinfo) - dt <= timedelta(days=days)

def fetch_google_news_campaigns(brand: str, query: str) -> List[Dict[str, Any]]:
    encoded_q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl=vi&gl=VN&ceid=VN:vi"
    return fetch_rss_campaigns(brand, url)

def collect_competitor_campaigns() -> Dict[str, Any]:
    """
    Thu thập, đối soát và gắn nhãn các chiến dịch khuyến mãi của các chuỗi bán lẻ ĐTDĐ trong 30 ngày.
    Tự động đánh dấu is_new khi phát hiện bài khuyến mãi mới.
    """
    cached_db = load_cached_campaigns()
    cached_items = cached_db.get("campaigns", {})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Thử quét online qua Google News RSS và Sforum
    raw_campaigns = []
    
    promo = '("khuyến mãi" OR "ưu đãi" OR "giảm giá" OR "sale" OR "thu cũ" OR "trả góp")'
    for brand, name_q in RETAILERS:
        items = fetch_google_news_campaigns(brand, f"{name_q} {promo}")
        raw_campaigns.extend([c for c in items if is_recent(c.get("pub_date", ""))][:3])

    processed_campaigns = []
    seen_titles = set()
    
    # Xử lý các tin online tìm được
    for item in raw_campaigns:
        title = item["title"]
        if title in seen_titles:
            continue
        seen_titles.add(title)
        
        # Kiểm tra cache để xem là bài mới hay bài cũ
        item_id = f"{item['brand']}_{re.sub(r'[^a-zA-Z0-9]', '', title)[:30]}"
        if item_id not in cached_items:
            # Bài mới phát hiện!
            cached_items[item_id] = {
                "first_seen": now_str,
                "title": title
            }
            item["is_new"] = True
        else:
            # Bài đã có trong cache
            item["is_new"] = False
            
        processed_campaigns.append(item)

    # Lưu lại cache
    cached_db["last_updated"] = now_str
    cached_db["campaigns"] = cached_items
    save_cached_campaigns(cached_db)
    
    return {
        "all_campaigns": processed_campaigns,
        "total_campaigns": len(processed_campaigns),
        "new_campaigns_count": sum(1 for c in processed_campaigns if c.get("is_new")),
        "time_window": "30 ngày qua",
    }

if __name__ == "__main__":
    res = collect_competitor_campaigns()
    print(f"Tổng hợp: {res['total_campaigns']} bài ({res['new_campaigns_count']} mới)")
    for c in res["all_campaigns"]:
        print(f"  * [{c['brand']}]{' [MỚI]' if c.get('is_new') else ''} {c['title']}")
