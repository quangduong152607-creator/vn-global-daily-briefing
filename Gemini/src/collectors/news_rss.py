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
                        
                        if title and link:
                            items.append({
                                "title": title,
                                "link": link.strip(),
                                "summary": desc[:250] + "..." if len(desc) > 250 else desc,
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
    """Thu thập toàn bộ các nhóm tin thời sự, tài chính, công nghệ"""
    results = {
        "domestic": [],
        "international": [],
        "technology": []
    }
    
    # Tin trong nước
    for src in sources_config.get("news_domestic", []):
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["domestic"].extend(feed_items)
            
    # Tin quốc tế
    for src in sources_config.get("news_international", []):
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=5)
            results["international"].extend(feed_items)
            
    # Tin công nghệ
    for src in sources_config.get("technology", []):
        if src.get("enabled", True):
            feed_items = fetch_single_feed(src, max_items=6)
            results["technology"].extend(feed_items)
            
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
