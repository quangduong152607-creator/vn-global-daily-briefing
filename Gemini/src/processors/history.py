"""
Lưu lịch sử chỉ số theo ngày (data/history.json) để tính thay đổi so với kỳ trước
và vẽ sparkline cho các chỉ số mà nguồn không cung cấp chuỗi lịch sử (tỷ giá VCB, vàng SJC, xăng).
Chỉ lưu số thật đã lấy được; ngày lỗi thì không ghi.
"""

import json
from datetime import date
from pathlib import Path
from typing import Dict, Any, List

HISTORY_FILE = Path(__file__).parent.parent.parent / "data" / "history.json"
MAX_DAYS = 120
SERIES_LEN = 15


def load_history(path: Path = HISTORY_FILE) -> Dict[str, Dict[str, float]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def apply_history(metrics: List[Dict[str, Any]], today: str = None, path: Path = HISTORY_FILE) -> None:
    """Ghi số hôm nay vào lịch sử, rồi bổ sung prev/series cho chỉ số còn thiếu. Sửa metrics tại chỗ."""
    today = today or date.today().isoformat()
    history = load_history(path)

    # Gộp (không ghi đè) để lần chạy lại trong ngày bị lỗi nguồn không xóa số đã lấy được
    values = {m["key"]: m["value"] for m in metrics if m["ok"] and m["value"] is not None}
    if values:
        history.setdefault(today, {}).update(values)
    for d in sorted(history)[:-MAX_DAYS]:
        del history[d]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    days = sorted(history)
    for m in metrics:
        if not m["ok"]:
            continue
        if m["prev"] is None:
            earlier = [history[d][m["key"]] for d in days if d < today and m["key"] in history[d]]
            m["prev"] = earlier[-1] if earlier else None
        if not m["series"]:
            m["series"] = [history[d][m["key"]] for d in days if m["key"] in history[d]][-SERIES_LEN:]


def change_of(metric: Dict[str, Any]):
    """(chênh lệch tuyệt đối, %) so với kỳ trước, hoặc (None, None)."""
    v, p = metric.get("value"), metric.get("prev")
    if v is None or p in (None, 0):
        return None, None
    return v - p, (v - p) / p * 100
