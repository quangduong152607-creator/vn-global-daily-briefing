"""
Chấm điểm và xếp hạng độ quan trọng của tin tức:
- Độ uy tín nguồn (0-30)
- Số nguồn cùng đưa tin (0-25)
- Độ liên quan tới ngành ĐTDĐ / bán lẻ / mua hàng (0-25) — Ưu tiên cao: Vivo, Realme, Samsung, Xiaomi
- Độ mới (0-10)
- Mức độ thảo luận (0-10)
"""

import re
from typing import List, Dict, Any

# Từ khóa liên quan trực tiếp đến công việc Mua hàng ngành ĐTDĐ của Ryan
HIGH_PRIORITY_KEYWORDS = {
    "vivo": 25,
    "realme": 25,
    "điện thoại": 20,
    "smartphone": 20,
    "samsung": 18,
    "xiaomi": 18,
    "oppo": 18,
    "giá bán": 15,
    "ra mắt": 15,
    "mở bán": 15,
    "mua hàng": 20,
    "chiết khấu": 20,
    "đại lý": 18,
    "bán lẻ": 18,
    "chuỗi cung ứng": 15,
    "nhập khẩu": 15,
    "chip": 12,
    "snapdragon": 12,
    "dimensity": 12
}

def calculate_importance_score(item: Dict[str, Any]) -> float:
    # 1. Điểm uy tín nguồn (0 - 30)
    source_weight = min(float(item.get("weight", 20)), 30.0)
    
    # 2. Số nguồn cùng đưa tin (0 - 25)
    source_count = item.get("source_count", 1)
    corroboration_score = min(float(source_count - 1) * 12.5, 25.0)
    
    # 3. Độ liên quan ngành hàng ĐTDĐ / Mua hàng (0 - 25)
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    combined = f"{title} {summary}"
    
    relevance_score = 0.0
    for kw, score in HIGH_PRIORITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', combined):
            relevance_score = max(relevance_score, score)
    relevance_score = min(relevance_score, 25.0)
    
    # 4. Độ mới (0 - 10)
    recency_score = 10.0 # Mặc định trong vòng 24h
    
    # 5. Mức độ thảo luận / lan truyền (0 - 10)
    discussion_score = 5.0
    if item.get("reliability", {}).get("code") == "VERIFIED":
        discussion_score += 3.0
        
    total_score = source_weight + corroboration_score + relevance_score + recency_score + discussion_score
    return round(total_score, 1)

def rank_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Tính điểm và xếp hạng từ cao xuống thấp"""
    ranked = []
    for it in items:
        it_copy = it.copy()
        it_copy["importance_score"] = calculate_importance_score(it)
        ranked.append(it_copy)
        
    ranked.sort(key=lambda x: x["importance_score"], reverse=True)
    return ranked

if __name__ == "__main__":
    t1 = {"title": "Thời tiết hôm nay tại Hà Nội mưa to", "weight": 20, "source_count": 1}
    t2 = {"title": "Vivo chính thức mở bán V40 5G tại Việt Nam với giá từ 9.99 triệu", "weight": 28, "source_count": 2}
    print("Điểm tin thời tiết:", calculate_importance_score(t1))
    print("Điểm tin Vivo mở bán:", calculate_importance_score(t2))
