"""
Bộ thu thập tin tức 24h qua chuẩn RSS từ các đầu báo lớn:
- VnExpress, Tuổi Trẻ, Thanh Niên, Báo Chính Phủ, CafeF, Vietstock
- GSMarena, The Verge, Android Authority, Tinhte, GenK
- BBC/Reuters, CNBC
"""

import ssl
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def get_ssl_context():
    return ssl._create_unverified_context()

def clean_html(raw_html: str) -> str:
    """Lọc sạch thẻ HTML và trích xuất text thuần"""
    if not raw_html:
        return ""
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)
    return ' '.join(clean_text.split()).strip()

def fetch_single_feed(source_info: Dict[str, Any], timeout: int = 8, max_items: int = 10) -> List[Dict[str, Any]]:
    """Đọc và trích xuất tin từ 1 kênh RSS với cơ chế retry an toàn"""
    url = source_info.get("url")
    name = source_info.get("name", "Nguồn")
    category = source_info.get("category", "general")
    weight = source_info.get("weight", 20)
    
    items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=get_ssl_context()) as response:
                if response.status == 200:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    
                    # Hỗ trợ cả RSS 2.0 (channel/item) và Atom (feed/entry)
                    rss_items = root.findall(".//item")
                    if not rss_items:
                        rss_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                        
                    for item in rss_items[:max_items]:
                        title_el = item.find("title") if item.find("title") is not None else item.find("{http://www.w3.org/2005/Atom}title")
                        link_el = item.find("link") if item.find("link") is not None else item.find("{http://www.w3.org/2005/Atom}link")
                        desc_el = item.find("description") if item.find("description") is not None else item.find("{http://www.w3.org/2005/Atom}summary")
                        pubdate_el = item.find("pubDate") if item.find("pubDate") is not None else item.find("{http://www.w3.org/2005/Atom}updated")
                        
                        title = clean_html(title_el.text) if (title_el is not None and title_el.text) else ""
                        
                        link = ""
                        if link_el is not None:
                            link = link_el.text if link_el.text else link_el.get("href", "")
                            
                        desc = clean_html(desc_el.text) if (desc_el is not None and desc_el.text) else ""
                        pubdate = pubdate_el.text if (pubdate_el is not None and pubdate_el.text) else datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # Bộ lọc tin thể thao, bóng đá, án mạng rác
                        low_text = (title + " " + desc).lower()
                        base_junk = [
                            "champions league", "premier league", "la liga", "serie a", "v-league",
                            "arsenal", "chelsea", "manchester", "barca", "real madrid", "hansi flick",
                            "grand slam", "tennis", "tsitsipas", "djokovic", "alcaraz", "bóng đá",
                            "tử vong do đuối nước", "vụ án mạng", "bắt giữ đối tượng cướp"
                        ]
                        if any(k in low_text for k in base_junk):
                            continue
                            
                        # Với tin kinh tế/công nghệ thì lọc thêm showbiz
                        if category not in ["showbiz", "entertainment", "viral_social"]:
                            showbiz_junk = ["showbiz", "người mẫu", "hoa hậu", "diễn viên", "ca sĩ", "ly hôn", "hẹn hò"]
                            if any(k in low_text for k in showbiz_junk):
                                continue

                        if title and link:
                            items.append({
                                "title": title,
                                "link": link.strip(),
                                "summary": desc[:280] + "..." if len(desc) > 280 else desc,
                                "pub_date": pubdate.strip(),
                                "source_name": name,
                                "category": category,
                                "weight": weight,
                                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                    break
        except Exception:
            continue
            
    return items

def collect_news(sources_config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Thu thập toàn bộ các nhóm tin theo 3 Tab: Trong nước (Kinh tế & Tech), Quốc tế (Địa chính trị & Tech), Social"""
    results = {
        "domestic_economy": [],
        "domestic_tech": [],
        "international_macro": [],
        "international_tech": [],
        "social": [],
        # Backward compatibility aliases
        "domestic": [],
        "international": [],
        "technology": []
    }
    
    # 1. Tin kinh tế & thị trường trong nước
    dom_econ_srcs = sources_config.get("news_domestic_economy", []) or sources_config.get("news_domestic", [])
    for src in dom_econ_srcs:
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["domestic_economy"].extend(feed_items)

    # 2. Tin công nghệ trong nước (Tinhte.vn, GenK, VnExpress Số Hóa)
    dom_tech_srcs = sources_config.get("news_domestic_tech", [])
    for src in dom_tech_srcs:
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["domestic_tech"].extend(feed_items)

    # 3. Tin kinh tế & địa chính trị quốc tế (Reuters, BBC, CNBC)
    intl_macro_srcs = sources_config.get("news_international_macro", []) or sources_config.get("news_international", [])
    for src in intl_macro_srcs:
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["international_macro"].extend(feed_items)

    # 4. Tin công nghệ & thiết bị di động quốc tế (GSMArena, The Verge)
    intl_tech_srcs = sources_config.get("news_international_tech", []) or sources_config.get("technology", [])
    for src in intl_tech_srcs:
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["international_tech"].extend(feed_items)

    # 5. Tin Social & Showbiz giải trí (bắt trend văn hóa/mạng xã hội)
    for src in sources_config.get("social_entertainment", []):
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["social"].extend(feed_items)

    # Điền backward compatibility
    results["domestic"] = results["domestic_economy"] + results["domestic_tech"]
    results["international"] = results["international_macro"]
    results["technology"] = results["international_tech"]

    cache_path = Path(__file__).parent.parent.parent / "data" / "raw" / "news_cache.json"
    
    total_fetched = (len(results["domestic_economy"]) + len(results["domestic_tech"]) + 
                     len(results["international_macro"]) + len(results["international_tech"]) + 
                     len(results["social"]))
    
    # Nếu cào thành công thì cập nhật cache
    if total_fetched > 0:
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    # Nếu không lấy được do offline hoặc lỗi mạng, tự động nạp từ cache
    elif cache_path.exists():
        try:
            import json
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
                if isinstance(cached, dict):
                    for k in ["domestic_economy", "domestic_tech", "international_macro", "international_tech", "social", "domestic", "international", "technology"]:
                        if k in cached and cached[k]:
                            results[k] = cached[k]
                    # Nếu cache cũ chưa phân rã, hỗ trợ migrate
                    if not results["domestic_economy"] and results.get("domestic"):
                        results["domestic_economy"] = results["domestic"]
                    if not results["international_macro"] and results.get("international"):
                        results["international_macro"] = results["international"]
                    if not results["international_tech"] and results.get("technology"):
                        results["international_tech"] = results["technology"]
                    if not results["domestic"] and (results["domestic_economy"] or results["domestic_tech"]):
                        results["domestic"] = results["domestic_economy"] + results["domestic_tech"]
        except Exception:
            pass
            
    return results

if __name__ == "__main__":
    sample_cfg = {
        "news_domestic": [
            {"name": "VnExpress", "url": "https://vnexpress.net/rss/tin-moi-nhat.rss", "weight": 28, "category": "general", "enabled": True}
        ],
        "technology": [
            {"name": "GSMArena", "url": "https://www.gsmarena.com/rss-news-reviews.php3", "weight": 30, "category": "mobile", "enabled": True}
        ]
    }
    news = collect_news(sample_cfg)
    print(f"Thu thập thành công: {len(news['domestic'])} tin trong nước, {len(news['technology'])} tin công nghệ.")
