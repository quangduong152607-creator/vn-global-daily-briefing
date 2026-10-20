"""
Chuẩn hóa tin tức cho bản tin:
- Dịch tin tiếng Anh sang tiếng Việt (giữ nguyên nếu không dịch được).
- Gắn nhãn chủ đề liên quan ngành ĐTDĐ (hãng, bán lẻ, linh kiện, thuế, tỷ giá, logistics)
  bằng từ khóa có trong chính bài viết.
- KHÔNG tự viết thêm "bối cảnh/tác động": chỉ dùng nội dung do nguồn cung cấp.
"""

import re
import urllib.request
import urllib.parse
import json
import ssl
from email.utils import parsedate_to_datetime
from datetime import datetime
from typing import Dict, Any, List


def get_ssl_context():
    return ssl._create_unverified_context()


VI_ACCENT_REGEX = re.compile(r'[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]', re.IGNORECASE)


def is_english_content(text: str) -> bool:
    if not text or len(text.strip()) < 5:
        return False
    if VI_ACCENT_REGEX.search(text):
        return False
    common_en = {"the", "and", "is", "in", "to", "of", "for", "with", "on", "at", "from", "by", "that", "this", "are", "be", "has", "have", "not", "why", "shows", "gets", "wont", "beating", "scores"}
    words = set(re.sub(r'[^\w\s]', '', text.lower()).split())
    return len(words.intersection(common_en)) >= 1


def robust_translate_to_vietnamese(text: str, timeout: int = 3) -> str:
    """Dịch câu tiếng Anh sang tiếng Việt; không dịch được thì trả nguyên văn."""
    clean_text = text.strip()
    if not clean_text or not is_english_content(clean_text):
        return clean_text

    # Tầng 1: Google Translate public single endpoint
    try:
        encoded = urllib.parse.quote(clean_text[:400])
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t&q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
        with urllib.request.urlopen(req, timeout=timeout, context=get_ssl_context()) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                trans = "".join([segment[0] for segment in data[0] if segment and segment[0]]).strip()
                if trans and not is_english_content(trans):
                    return trans
    except Exception:
        pass

    # Tầng 2: MyMemory API
    try:
        encoded = urllib.parse.quote(clean_text[:300])
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|vi"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=get_ssl_context()) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                trans = data.get("responseData", {}).get("translatedText", "").strip()
                if trans and "MYMEMORY WARNING" not in trans.upper() and not is_english_content(trans):
                    return trans
    except Exception:
        pass

    return clean_text


# Nhãn chủ đề cho người làm mua hàng ĐTDĐ: nhãn -> từ khóa (so khớp theo ranh giới từ, không phân biệt hoa thường)
TOPIC_TAGS = {
    "Apple": ["apple", "iphone", "ipad", "airpods", "macbook"],
    "Samsung": ["samsung", "galaxy"],
    "Xiaomi": ["xiaomi", "redmi", "poco"],
    "OPPO": ["oppo", "oneplus"],
    "vivo": ["vivo", "iqoo"],
    "realme": ["realme"],
    "Honor": ["honor"],
    "Transsion": ["tecno", "infinix", "itel"],
    "Bán lẻ": ["thế giới di động", "tgdđ", "tgdd", "fpt shop", "cellphones", "viettel store", "hoàng hà mobile", "di động việt", "topzone", "điện máy xanh"],
    "Chip & bộ nhớ": ["chip", "bán dẫn", "semiconductor", "snapdragon", "dimensity", "mediatek", "qualcomm", "tsmc", "dram", "nand", "bộ nhớ", "memory"],
    "Smartphone": ["smartphone", "điện thoại", "phone", "foldable", "điện thoại gập"],
    "Thuế & nhập khẩu": ["thuế", "thuế quan", "tariff", "nhập khẩu", "hải quan", "xuất khẩu", "import", "export"],
    "Tỷ giá & lãi suất": ["tỷ giá", "nhân dân tệ", "yuan", "lãi suất", "fed", "nhnn", "ngân hàng nhà nước", "interest rate"],
    "Logistics": ["cước", "vận tải", "logistics", "cảng", "shipping", "freight", "biển đỏ", "red sea"],
}
_TAG_PATTERNS = {tag: re.compile(r"(?<!\w)(" + "|".join(re.escape(k) for k in kws) + r")(?!\w)", re.IGNORECASE)
                 for tag, kws in TOPIC_TAGS.items()}


def topic_tags(text: str) -> List[str]:
    return [tag for tag, pat in _TAG_PATTERNS.items() if pat.search(text)]


def format_pub_time(pub_date: str) -> str:
    """'Tue, 20 Oct 2026 06:00:00 +0700' -> '06:00 20/10' (giờ VN theo TZ máy chạy)."""
    try:
        dt = parsedate_to_datetime(pub_date)
        if dt.tzinfo:
            dt = dt.astimezone()
        return dt.strftime("%H:%M %d/%m")
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(pub_date.replace("Z", "+00:00")).astimezone().strftime("%H:%M %d/%m")
    except (TypeError, ValueError):
        return ""


def structure_item(item: Dict[str, Any]) -> Dict[str, Any]:
    title = robust_translate_to_vietnamese(item.get("title", ""))
    summary = robust_translate_to_vietnamese(item.get("summary", ""))
    return {
        "title": title,
        "summary": summary,
        "source": item.get("source_name", ""),
        "link": item.get("link", ""),
        "time": format_pub_time(item.get("pub_date", "")),
        "reliability": item.get("reliability", {}),
        "score": item.get("importance_score", 0),
        "tags": topic_tags(f"{title} {summary} {item.get('title_en', '')} {item.get('summary_en', '')}"),
        "from_cache": item.get("from_cache", False),
    }


SECTION_LIMITS = {
    "domestic_economy": 8,
    "domestic_tech": 6,
    "international_macro": 8,
    "international_tech": 6,
}


def process_and_structure_all_news(news_by_category: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Chuẩn hóa từng nhóm tin và chọn danh sách 'Đáng chú ý cho ngành ĐTDĐ'."""
    sections = {}
    seen = set()
    for cat, limit in SECTION_LIMITS.items():
        out = []
        for it in news_by_category.get(cat, []):
            link = it.get("link")
            if not link or link in seen:
                continue
            seen.add(link)
            out.append(structure_item(it))
            if len(out) >= limit:
                break
        sections[cat] = out

    # Đáng chú ý: tin có nhãn ngành, ưu tiên nhiều nhãn và điểm cao. Nhãn chỉ có "Tỷ giá"/"Thuế" vẫn được tính.
    all_items = [it for cat in SECTION_LIMITS for it in sections[cat]]
    watch = [it for it in all_items if it["tags"]]
    watch.sort(key=lambda it: (len(it["tags"]), it["score"]), reverse=True)
    sections["watchlist"] = watch[:8]
    return sections
