#!/usr/bin/env python3
"""
Chuẩn hóa dữ liệu thô (raw notes, text, json) thành tài liệu Markdown chuẩn hóa
để nạp vào Google NotebookLM. NotebookLM xử lý tốt nhất khi tài liệu có
tiêu đề phân cấp, bảng số liệu định lượng, và tóm tắt theo từng chuyên mục.
"""

import os
import sys
import json
import argparse
from datetime import datetime

def format_text_to_notebooklm_source(raw_content: str, title: str = "Báo Cáo Nghiên Cứu Thị Trường") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    header = f"""# {title}
*Thời gian tổng hợp: {timestamp}*
*Nguồn gốc dữ liệu: Bộ phận phân tích thị trường Antigravity*

---

## 1. Tóm Tắt Tổng Quan (Executive Summary)
Tài liệu này được định dạng tối ưu để Google NotebookLM phân tích chuyên sâu, trích xuất dữ liệu đa chiều và xây dựng dàn ý Infographic thị trường.

---

## 2. Nội Dung Phân Tích Chi Tiết & Số Liệu Nguồn
{raw_content}

---

## 3. Chỉ Dẫn Trích Xuất Cho AI
- Nhận diện các con số tuyệt đối, phần trăm tăng trưởng, tỉ trọng thị phần.
- Kết nối các mắt xích nhân quả giữa động lực thị trường và rủi ro.
- Chuẩn bị dữ liệu đầu vào cho các biểu đồ (Bar, Donut, Timeline, Funnel).
"""
    return header

def main():
    parser = argparse.ArgumentParser(description="Chuẩn hóa dữ liệu thị trường cho NotebookLM")
    parser.add_argument("--input", "-i", help="Đường dẫn file thô đầu vào (.txt, .json, .md)")
    parser.add_argument("--output", "-o", help="Đường dẫn file markdown xuất ra cho NotebookLM")
    parser.add_argument("--title", "-t", default="Báo Cáo Nghiên Cứu Thị Trường", help="Tiêu đề báo cáo")
    
    args = parser.parse_args()
    
    if not args.input or not args.output:
        print("Sử dụng: python3 scripts/prepare_notebooklm_source.py --input <file_vao> --output <file_ra>")
        sys.exit(1)
        
    if not os.path.exists(args.input):
        print(f"Lỗi: Không tìm thấy file {args.input}")
        sys.exit(1)
        
    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Xử lý nếu là JSON
    if args.input.endswith(".json"):
        try:
            data = json.loads(content)
            content = "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
        except Exception:
            pass
            
    formatted = format_text_to_notebooklm_source(content, title=args.title)
    
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(formatted)
        
    print(f"✓ Đã xuất tài liệu nguồn chuẩn hóa cho NotebookLM tại: {args.output}")

if __name__ == "__main__":
    main()
