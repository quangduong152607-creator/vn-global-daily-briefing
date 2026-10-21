"""
Bộ thu thập Google Trends hàng ngày cho Việt Nam và Toàn cầu.
Phát hiện và đánh dấu các từ khóa thuộc ngành ICT & Smartphone.
"""

import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

ICT_KEYWORDS = {
    "iphone", "apple", "samsung", "galaxy", "vivo", "realme", "xiaomi", "oppo",
    "honor", "tecno", "infinix", "điện thoại", "smartphone", "chip", "snapdragon",
    "mediatek", "dimensity", "android", "ios", "ai", "laptop", "tai nghe", "pin", "sạc", "5g",
    "macbook", "ipad", "airpods", "apple intelligence", "deepseek", "chatgpt", "gemini",
    "fold", "flip", "z fold", "z flip", "find x", "x200", "iqoo", "redmi", "poco"
}

def get_ssl_context():
    return ssl._create_unverified_context()

def fetch_google_trends(geo: str = "VN") -> List[Dict[str, Any]]:
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    trends = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
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
                        # Kiểm tra xem có liên quan ICT không (sử dụng word boundary để tránh nhận nhầm chữ 'ai', 'pin', 'sạc' trong các từ khác)
                        keyword_lower = keyword.lower()
                        is_ict = any(re.search(r'(?:\b|^)' + re.escape(k) + r'(?:\b|$)', keyword_lower) for k in ICT_KEYWORDS)
                        
                        trends.append({
                            "rank": len(trends) + 1,
                            "keyword": keyword,
                            "traffic": traffic,
                            "geo": geo,
                            "is_ict": is_ict,
                            "tag": "📱 ICT / Công nghệ" if is_ict else "🔥 Thịnh hành"
                        })
    except Exception:
        pass
        
    return trends

def collect_all_trends() -> Dict[str, List[Dict[str, Any]]]:
    """Lấy xu hướng tìm kiếm VN và Mỹ từ Google Trends RSS."""
    vn_trends = fetch_google_trends("VN")
    global_trends = fetch_google_trends("US")
    
    # Lỗi mạng thì trả danh sách rỗng; trang bản tin báo "chưa lấy được" (không dùng danh sách mẫu)
    return {
        "vn_trends": vn_trends[:10],
        "global_trends": global_trends[:10]
    }

if __name__ == "__main__":
    t = collect_all_trends()
    print(f"Lấy được {len(t['vn_trends'])} trends VN và {len(t['global_trends'])} trends Global.")
    for item in t["vn_trends"][:10]:
        print(f"#{item['rank']} - {item['keyword']} ({item['traffic']}) [{item['tag']}]")
