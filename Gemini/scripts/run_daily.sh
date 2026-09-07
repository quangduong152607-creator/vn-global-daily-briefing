#!/bin/zsh
export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
cd "/Users/ryan/Documents/Github_AI/Nhịp Đập Thị Trường/Gemini" || exit 1
mkdir -p logs
echo "[$(date "+%Y-%m-%d %H:%M:%S")] Bắt đầu chạy bản tin tự động..." >> logs/scheduler.log
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 main.py >> logs/scheduler.log 2>&1
echo "[$(date "+%Y-%m-%d %H:%M:%S")] Hoàn tất bản tin tự động." >> logs/scheduler.log
