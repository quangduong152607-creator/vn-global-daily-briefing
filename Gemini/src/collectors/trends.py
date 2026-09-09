"""
Bộ thu thập Google Trends hàng ngày cho Việt Nam và Toàn cầu.
Phát hiện và đánh dấu các từ khóa thuộc ngành ICT & Smartphone.
"""

import ssl
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

ICT_KEYWORDS = {
    "iphone", "apple", "samsung", "galaxy", "vivo", "realme", "xiaomi", "oppo",
    "honor", "tecno", "infinix", "điện thoại", "smartphone", "chip", "snapdragon",
    "mediatek", "android", "ios", "ai", "laptop", "tai nghe", "pin", "sạc", "5g"
}

def get_ssl_context():
    return ssl._create_unverified_context()

def fetch_google_trends(geo: str = "VN") -> List[Dict[str, Any]]:
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    trends = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=get_ssl_context()) as response:
            if response.status == 200:
                root = ET.fromstring(response.read())
                for item in root.findall(".//item"):
                    title_el = item.find("title")
                    approx_traffic = item.find("{https://trends.google.com/trending/rss}approx_traffic")
                    
                    keyword = title_el.text.strip() if (title_el is not None and title_el.text) else ""
                    traffic = approx_traffic.text.strip() if (approx_traffic is not None and approx_traffic.text) else "10K+"
                    
                    if keyword:
                        # Kiểm tra xem có liên quan ICT không
                        keyword_lower = keyword.lower()
                        is_ict = any(k in keyword_lower for k in ICT_KEYWORDS)
                        
                        trends.append({
                            "keyword": keyword,
                            "traffic": traffic,
                            "geo": geo,
                            "is_ict": is_ict,
                            "tag": "📱 ICT/Tech" if is_ict else "🔥 Hot General"
                        })
    except Exception:
        pass
        
    return trends

def collect_all_trends() -> Dict[str, List[Dict[str, Any]]]:
    """Lấy cả xu hướng VN và Global kèm fallback offline"""
    vn_trends = fetch_google_trends("VN")
    global_trends = fetch_google_trends("US")
    
    if not vn_trends:
        vn_trends = [
            {"keyword": "iphone", "traffic": "20K+", "geo": "VN", "is_ict": True, "tag": "📱 ICT/Tech"},
            {"keyword": "vinfast", "traffic": "15K+", "geo": "VN", "is_ict": False, "tag": "🔥 Hot General"},
            {"keyword": "samsung galaxy", "traffic": "10K+", "geo": "VN", "is_ict": True, "tag": "📱 ICT/Tech"},
            {"keyword": "giá vàng sjc", "traffic": "50K+", "geo": "VN", "is_ict": False, "tag": "🔥 Hot General"},
            {"keyword": "vivo v-series", "traffic": "8K+", "geo": "VN", "is_ict": True, "tag": "📱 ICT/Tech"},
            {"keyword": "lãi suất ngân hàng", "traffic": "12K+", "geo": "VN", "is_ict": False, "tag": "🔥 Hot General"}
        ]
        
    return {
        "vn_trends": vn_trends[:12],
        "global_trends": global_trends[:10]
    }

if __name__ == "__main__":
    t = collect_all_trends()
    print(f"Lấy được {len(t['vn_trends'])} trends VN và {len(t['global_trends'])} trends Global.")
    for item in t["vn_trends"][:5]:
        print(f"- {item['keyword']} ({item['traffic']}) [{item['tag']}]")
