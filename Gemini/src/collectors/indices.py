"""
Bộ thu thập chỉ số thị trường: Tỷ giá, Vàng, Chứng khoán, Hàng hóa, Xăng dầu.

Nguyên tắc: KHÔNG BAO GIỜ trả về số mặc định/ước đoán.
Nguồn lỗi -> value = None, ok = False, kèm lý do. Trang bản tin sẽ hiển thị "chưa lấy được".
Mỗi chỉ số là một dict cùng khuôn (xem make_metric).
"""

import json
import re
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"


def get_ssl_context():
    return ssl._create_unverified_context()


def http_get(url: str, timeout: int = 10) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=get_ssl_context()) as r:
        return r.read()


def now_str() -> str:
    return datetime.now().strftime("%H:%M %d/%m/%Y")


def make_metric(key: str, label: str, group: str, unit: str, decimals: int,
                source: str, source_url: str) -> Dict[str, Any]:
    """Khuôn chung cho 1 chỉ số. value/prev/series do collector điền khi lấy được số thật."""
    return {
        "key": key,
        "label": label,
        "group": group,
        "unit": unit,
        "decimals": decimals,
        "value": None,
        "prev": None,          # giá trị kỳ trước do NGUỒN cung cấp (nếu có)
        "series": [],          # chuỗi lịch sử do NGUỒN cung cấp (nếu có)
        "sub": "",             # dòng phụ, ví dụ "Mua 26.020 · Bán 26.370"
        "as_of": "",           # mốc thời gian của số liệu theo nguồn
        "source": source,
        "source_url": source_url,
        "fetched_at": now_str(),
        "ok": False,
        "error": "",
    }


def parse_number(text: str) -> Optional[float]:
    """'26,370.00' -> 26370.0 ; '-' hoặc rỗng -> None"""
    t = (text or "").strip().replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def vn_int(n: float) -> str:
    return f"{n:,.0f}".replace(",", ".")


# ---------------------------------------------------------------- Tỷ giá

VCB_URL = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"
ER_API_URL = "https://open.er-api.com/v6/latest/USD"


def fetch_forex() -> List[Dict[str, Any]]:
    """USD, CNY, KRW so với VND. Ưu tiên bảng giá Vietcombank; dự phòng tỷ giá tham chiếu quốc tế."""
    spec = [("usd_vnd", "USD/VND", "USD", 0), ("cny_vnd", "CNY/VND", "CNY", 0), ("krw_vnd", "KRW/VND", "KRW", 2)]
    metrics = {k: make_metric(k, label, "fx", "đ", dec, "Vietcombank", VCB_URL) for k, label, _, dec in spec}

    try:
        root = ET.fromstring(http_get(VCB_URL))
        as_of = (root.findtext("DateTime") or "").strip()
        try:  # VCB trả dạng Mỹ "10/20/2026 8:00:00 AM"
            as_of = datetime.strptime(as_of, "%m/%d/%Y %I:%M:%S %p").strftime("%H:%M %d/%m/%Y")
        except ValueError:
            pass
        rates = {e.get("CurrencyCode"): e for e in root.iter("Exrate")}
        for key, _, code, _ in spec:
            e = rates.get(code)
            if e is None:
                continue
            buy, transfer, sell = (parse_number(e.get(a)) for a in ("Buy", "Transfer", "Sell"))
            if sell is None:
                continue
            m = metrics[key]
            m["value"] = sell
            fmt = (lambda v: f"{v:.2f}".replace(".", ",")) if code == "KRW" else vn_int
            parts = []
            if buy is not None:
                parts.append(f"Mua TM {fmt(buy)}")
            if transfer is not None:
                parts.append(f"CK {fmt(transfer)}")
            m["sub"] = " · ".join(parts) + " · giá bán ra"
            m["as_of"] = as_of
            m["ok"] = True
    except Exception as e:
        for m in metrics.values():
            m["error"] = f"Vietcombank: {e}"

    missing = [m for m in metrics.values() if not m["ok"]]
    if missing:
        try:
            data = json.loads(http_get(ER_API_URL))
            rates = data.get("rates", {})
            usd_vnd = rates.get("VND")
            for key, _, code, _ in spec:
                m = metrics[key]
                if m["ok"] or not usd_vnd:
                    continue
                per_usd = 1.0 if code == "USD" else rates.get(code)
                if not per_usd:
                    continue
                m.update({
                    "value": usd_vnd / per_usd,
                    "sub": "Tỷ giá tham chiếu quốc tế (không phải giá ngân hàng)",
                    "as_of": data.get("time_last_update_utc", ""),
                    "source": "open.er-api.com",
                    "source_url": ER_API_URL,
                    "ok": True,
                    "error": "",
                })
        except Exception as e:
            for m in missing:
                m["error"] = (m["error"] + f" | er-api: {e}").strip(" |")

    return [metrics[k] for k, *_ in spec]


# ---------------------------------------------------------------- Yahoo Finance (chuỗi giá đóng cửa)

def fetch_yahoo(key: str, label: str, group: str, symbol: str, unit: str, decimals: int) -> Dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?interval=1d&range=1mo"
    m = make_metric(key, label, group, unit, decimals, "Yahoo Finance", f"https://finance.yahoo.com/quote/{symbol}")
    try:
        res = json.loads(http_get(url))["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0].get("close", []) if c is not None]
        price = res["meta"].get("regularMarketPrice") or (closes[-1] if closes else None)
        if price is None:
            raise ValueError("không có giá")
        # Yahoo có thể chưa ghi phiên hôm nay vào closes -> so với close cuối nếu nó khác giá hiện tại
        if closes and abs(closes[-1] - price) < 1e-9:
            prev = closes[-2] if len(closes) >= 2 else None
            series = closes[-15:]
        else:
            prev = closes[-1] if closes else None
            series = (closes + [price])[-15:]
        ts = res["meta"].get("regularMarketTime")
        m.update({
            "value": float(price),
            "prev": prev,
            "series": series,
            "as_of": datetime.fromtimestamp(ts).strftime("%H:%M %d/%m/%Y") if ts else "",
            "ok": True,
        })
    except Exception as e:
        m["error"] = str(e)
    return m


# ---------------------------------------------------------------- Vàng SJC

GOLD_URL = "https://24h.com.vn/gia-vang-hom-nay-c425.html"


def fetch_gold_sjc() -> Dict[str, Any]:
    m = make_metric("gold_sjc", "Vàng SJC", "gold", "tr.đ/lượng", 2, "24h.com.vn (bảng giá SJC)", GOLD_URL)
    try:
        html = http_get(GOLD_URL).decode("utf-8", errors="ignore")
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL):
            if "SJC" not in tr:
                continue
            nums = re.findall(r"([0-9]{2,3},[0-9]{3})", tr)
            if len(nums) >= 2:
                buy = float(nums[0].replace(",", "")) / 1000.0
                sell = float(nums[1].replace(",", "")) / 1000.0
                m.update({"value": sell, "sub": f"Mua {buy:.2f}".replace(".", ",") + " · bán ra", "ok": True})
                break
        if not m["ok"]:
            m["error"] = "Không tìm thấy dòng SJC trong bảng giá"
    except Exception as e:
        m["error"] = str(e)
    return m


# ---------------------------------------------------------------- Xăng dầu

FUEL_URL = "https://webgia.com/gia-xang-dau/petrolimex/"


def fetch_fuel() -> Dict[str, Any]:
    """Giá RON 95-III vùng 1 theo bảng niêm yết Petrolimex. Không có số dự phòng."""
    m = make_metric("ron95", "Xăng RON 95", "fuel", "đ/lít", 0, "Petrolimex (qua webgia.com)", FUEL_URL)
    try:
        html = http_get(FUEL_URL).decode("utf-8", errors="ignore")
        period = re.search(r"áp dụng từ\s*([0-9]{1,2}h[0-9]{0,2}\s*ngày\s*[0-9]{1,2}/[0-9]{1,2}/[0-9]{4})", html, re.I)
        found = {}
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL):
            row = re.sub(r"<[^>]+>", " ", tr)
            nums = re.findall(r"\b([1-3]\d[.,]\d{3})\b", row)
            if not nums:
                continue
            price = float(nums[0].replace(".", "").replace(",", ""))
            if "RON 95-III" in row and "ron95" not in found:
                found["ron95"] = price
            elif "RON 95" in row and "RON 95-V" not in row and "ron95" not in found:
                found["ron95"] = price
            elif "E5" in row and "e5" not in found:
                found["e5"] = price
            elif ("DO 0" in row or "Dầu DO" in row) and "do" not in found:
                found["do"] = price
        if "ron95" in found:
            sub = []
            if "e5" in found:
                sub.append(f"E5 {vn_int(found['e5'])}")
            if "do" in found:
                sub.append(f"DO {vn_int(found['do'])}")
            m.update({
                "value": found["ron95"],
                "sub": " · ".join(sub),
                "as_of": f"Kỳ điều hành {period.group(1)}" if period else "",
                "ok": True,
            })
        else:
            m["error"] = "Không tìm thấy dòng RON 95 trong bảng giá"
    except Exception as e:
        m["error"] = str(e)
    return m


# ---------------------------------------------------------------- Tổng hợp

def collect_all_indices() -> List[Dict[str, Any]]:
    """Trả về danh sách chỉ số theo thứ tự hiển thị."""
    metrics = fetch_forex()
    metrics.append(fetch_gold_sjc())
    metrics.append(fetch_yahoo("gold_world", "Vàng thế giới", "gold", "GC=F", "USD/oz", 1))
    metrics.append(fetch_yahoo("vnindex", "VN-Index", "stock", "^VNINDEX.VN", "điểm", 2))
    metrics.append(fetch_fuel())
    metrics.append(fetch_yahoo("brent", "Dầu Brent", "commodity", "BZ=F", "USD/thùng", 2))
    metrics.append(fetch_yahoo("dxy", "Chỉ số USD (DXY)", "fx", "DX-Y.NYB", "điểm", 2))
    return metrics


if __name__ == "__main__":
    for m in collect_all_indices():
        status = "OK " if m["ok"] else "LỖI"
        print(f"[{status}] {m['label']}: {m['value']} {m['unit']} — {m['source']} {m['error']}")
