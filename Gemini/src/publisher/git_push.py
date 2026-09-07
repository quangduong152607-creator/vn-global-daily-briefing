"""
Tự động xuất bản lên GitHub Pages (Spec Section 7 & 7.5):
- Sao chép docs/index.html ra thư mục gốc repo
- Git commit và git push origin main để cập nhật link:
  https://quangduong152607-creator.github.io/vn-global-daily-briefing/
"""

import shutil
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = PROJECT_ROOT.parent

def deploy_to_github_pages(date_str: str = None) -> bool:
    if not date_str:
        date_str = datetime.now().strftime('%d/%m/%Y')
        
    src_index = PROJECT_ROOT / 'docs' / 'index.html'
    dest_index = REPO_ROOT / 'index.html'
    
    if not src_index.exists():
        print(f'✕ Không tìm thấy file {src_index}')
        return False
        
    # 1. Copy file sang thư mục gốc phục vụ GitHub Pages
    shutil.copy2(src_index, dest_index)
    print(f'✓ Đã cập nhật {dest_index}')
    
    # 2. Thực hiện git commit và push
    try:
        # git add
        subprocess.run(['git', 'add', 'index.html'], cwd=REPO_ROOT, check=True)
        
        # git commit
        commit_msg = f'Bản tin 24h — {date_str}'
        res = subprocess.run(['git', 'commit', '-m', commit_msg], cwd=REPO_ROOT, capture_output=True, text=True)
        if 'nothing to commit' in res.stdout:
            print('ℹ Không có thay đổi mới cần commit.')
        else:
            print(f'✓ Đã commit: "{commit_msg}"')
            
        # git push
        print('🚀 Đang đẩy lên GitHub Pages (origin main)...')
        push_res = subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        print('✓ Đã push thành công lên GitHub!')
        print('🌐 Link xem trên điện thoại: https://quangduong152607-creator.github.io/vn-global-daily-briefing/')
        return True
    except subprocess.CalledProcessError as e:
        print(f'✕ Lỗi khi đẩy git: {e}')
        if hasattr(e, 'stderr') and e.stderr:
            print(f'Chi tiết: {e.stderr}')
        return False

if __name__ == '__main__':
    deploy_to_github_pages()
