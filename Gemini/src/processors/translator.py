"""
Bộ xử lý dịch thuật & hỗ trợ song ngữ (English -> Vietnamese) tốc độ cao:
- Sử dụng ThreadPoolExecutor để dịch song song nhiều bài viết chỉ trong 1-2 giây.
- Tự động nhận diện tin tiếng Anh từ các nguồn quốc tế (Reuters, BBC, Android Authority, The Verge).
- Dịch mượt mà sang Tiếng Việt cho tiêu đề và phần tóm tắt.
- Giữ lại tiêu đề và tóm tắt gốc tiếng Anh để hỗ trợ hiển thị song ngữ trực quan (Bilingual UI).
"""

import re
import ssl
import urllib.request
import urllib.parse
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

# Bộ nhớ tạm (cache) tránh gọi trùng lặp
TRANSLATION_CACHE: Dict[str, str] = {}

def get_ssl_context():
    return ssl._create_unverified_context()

VIETNAMESE_ACCENT_PATTERN = re.compile(
    r'[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]',
    re.IGNORECASE
)

def is_english_text(text: str) -> bool:
    """Kiểm tra văn bản có phải là tiếng Anh (không có dấu tiếng Việt)"""
    if not text or len(text.strip()) < 4:
        return False
    if VIETNAMESE_ACCENT_PATTERN.search(text):
        return False
        
    common_en_words = {"the", "and", "is", "in", "to", "of", "for", "with", "on", "at", "from", "by", "that", "this", "are", "be", "has", "have", "not", "why", "how", "what", "we", "wont", "gets", "shows"}
    words = set(re.sub(r'[^\w\s]', '', text.lower()).split())
    if len(words.intersection(common_en_words)) >= 1:
        return True
        
    return False

def translate_en_to_vi(text: str, timeout: int = 3) -> str:
    """Dịch từ Tiếng Anh sang Tiếng Việt qua MyMemory API với timeout ngắn và fallback an toàn"""
    clean_text = text.strip()
    if not clean_text:
        return ""
        
    if clean_text in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[clean_text]
        
    encoded_query = urllib.parse.quote(clean_text[:350])
    url = f"https://api.mymemory.translated.net/get?q={encoded_query}&langpair=en|vi"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=get_ssl_context()) as r:
            if r.status == 200:
                data = json.loads(r.read())
                trans = data.get("responseData", {}).get("translatedText", "").strip()
                if trans and "MYMEMORY WARNING" not in trans.upper() and trans != clean_text:
                    TRANSLATION_CACHE[clean_text] = trans
                    return trans
    except Exception:
        pass
        
    return clean_text

def translate_item_bilingual(item: Dict[str, Any]) -> Dict[str, Any]:
    """Chuyển đổi bài viết sang định dạng dịch tiếng Việt kèm metadata song ngữ"""
    item_copy = item.copy()
    
    title = item.get("title", "")
    summary = item.get("summary", "")
    
    is_title_en = is_english_text(title)
    is_summary_en = is_english_text(summary)
    
    if is_title_en or is_summary_en:
        item_copy["is_bilingual"] = True
        item_copy["title_en"] = title
        item_copy["summary_en"] = summary
        
        # Dịch đồng thời title và summary
        if is_title_en:
            item_copy["title_vi"] = translate_en_to_vi(title)
            item_copy["title"] = item_copy["title_vi"]
        else:
            item_copy["title_vi"] = title
            
        if is_summary_en:
            item_copy["summary_vi"] = translate_en_to_vi(summary)
            item_copy["summary"] = item_copy["summary_vi"]
        else:
            item_copy["summary_vi"] = summary
    else:
        item_copy["is_bilingual"] = False
        item_copy["title_vi"] = title
        item_copy["summary_vi"] = summary
        
    return item_copy

def translate_news_batch(items: List[Dict[str, Any]], max_workers: int = 5) -> List[Dict[str, Any]]:
    """Dịch song song danh sách bài viết bằng ThreadPoolExecutor"""
    if not items:
        return []
        
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(translate_item_bilingual, items))
    return results

if __name__ == "__main__":
    items = [
        {"title": "Motorola and Google foldables are quietly beating Samsung where it counts", "summary": "Samsung forgot the foldable features that truly matter."},
        {"title": "I want better Samsung phones, but these new sales numbers show why we won’t get them", "summary": "Samsung doesn't have much incentive to push its hardware innovation."}
    ]
    res = translate_news_batch(items)
    for r in res:
        print("VI:", r["title"])
        print("EN:", r["title_en"])
