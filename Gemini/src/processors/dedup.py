"""
Khử trùng lặp tin tức (Deduplication):
- So khớp độ tương đồng tiêu đề giữa các bài báo
- Gom các bài viết cùng sự kiện lại thành 1 cụm
- Chọn bài có trọng số nguồn cao nhất làm bài đại diện
- Giữ lại các link còn lại vào danh sách corroborating_sources để phục vụ xác minh chéo
"""

import re
from typing import List, Dict, Any

def tokenize(text: str) -> set:
    """Tách từ đơn giản và loại bỏ từ vô nghĩa"""
    clean = re.sub(r'[^\w\s]', '', text.lower())
    words = set(clean.split())
    # Loại bỏ stopwords phổ biến
    stopwords = {"là", "và", "của", "các", "có", "được", "trong", "đã", "cho", "với", "tại", "về", "the", "a", "to", "in", "of", "and"}
    return words - stopwords

def calculate_similarity(text1: str, text2: str) -> float:
    """Đo độ tương đồng Jaccard giữa hai chuỗi từ khóa"""
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)

def deduplicate_items(items: List[Dict[str, Any]], threshold: float = 0.45) -> List[Dict[str, Any]]:
    """Gom cụm và khử trùng lặp danh sách tin tức"""
    clustered = []
    visited = set()
    
    for i, item_a in enumerate(items):
        if i in visited:
            continue
            
        cluster = [item_a]
        visited.add(i)
        
        for j, item_b in enumerate(items):
            if j in visited:
                continue
            sim = calculate_similarity(item_a.get("title", ""), item_b.get("title", ""))
            if sim >= threshold:
                cluster.append(item_b)
                visited.add(j)
                
        # Chọn bài có weight cao nhất làm đại diện
        cluster.sort(key=lambda x: x.get("weight", 0), reverse=True)
        primary_item = cluster[0].copy()
        
        # Gom các nguồn phụ
        corroborating = []
        for other in cluster[1:]:
            corroborating.append({
                "source_name": other.get("source_name"),
                "link": other.get("link")
            })
        primary_item["corroborating_sources"] = corroborating
        primary_item["source_count"] = len(cluster)
        
        clustered.append(primary_item)
        
    return clustered

if __name__ == "__main__":
    sample = [
        {"title": "Giá vàng SJC hôm nay tăng mạnh vượt 90 triệu đồng", "weight": 28, "source_name": "VnExpress", "link": "url1"},
        {"title": "SJC tăng mạnh vượt mốc 90 triệu đồng mỗi lượng", "weight": 24, "source_name": "Thanh Niên", "link": "url2"},
        {"title": "Vivo chuẩn bị ra mắt dòng điện thoại V40 mới tại Việt Nam", "weight": 30, "source_name": "Tinhte", "link": "url3"}
    ]
    res = deduplicate_items(sample)
    print(f"Từ {len(sample)} bài gom thành {len(res)} cụm sự kiện.")
    print("Bài 1 có số nguồn xác thực:", res[0]["source_count"])
